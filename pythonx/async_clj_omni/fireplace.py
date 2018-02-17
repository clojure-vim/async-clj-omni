import nrepl
from async_clj_omni.cider import cider_gather
from neovim.api.nvim import NvimError

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

def gather_conn_info(vim):
    try:
        client = vim.eval("fireplace#client()")
    # If Fireplace complains that there is no REPL connection, silently fail
    # instead of throwing an error in the user's face.
    except NvimError as e:
        if str(e) == "b'Fireplace: :Connect to a REPL or install classpath.vim'":
            client = None
        else:
            raise Error(str(e))
    except Exception as e:
        raise Error(str(e))

    if client:
        connection = client.get("connection", {})
        transport = connection.get("transport")

        if not transport:
            raise Error

    ns = ""
    try:
        ns = vim.eval("fireplace#ns()")
    except Exception:
        pass

    return [client, connection, transport, ns]

class ConnManager:
    def __init__(self, logger):
        self.__conns = {}
        self.logger = logger

    def get_conn(self, conn_string):
        if conn_string not in self.__conns:
            conn = nrepl.connect(conn_string)

            def global_watch(cmsg, cwc, ckey):
                self.logger.debug("Received message for {}".format(conn_string))
                self.logger.debug(cmsg)

            wc = nrepl.WatchableConnection(conn)
            self.__conns[conn_string] = wc
            wc.watch("global_watch", {}, global_watch)

        return self.__conns.get(conn_string)

    def remove_conn(self, conn_string):
        self.logger.debug(
            ("Connection to {} died. "
             "Removing the connection.").format(conn_string)
        )
        self.__conns.pop(conn_string, None)

class Fireplace_nrepl:
    def __init__(self, wc):
        self.wc = wc

    def send(self, msg):
        self.wc.send(msg)

    def watch(self, name, q, callback):
        self.wc.watch(name, q, callback)

    def unwatch(self, name):
        self.wc.unwatch(name)

class CiderCompletionManager:
    def __init__(self, logger, vim):
        self.__connmanager = ConnManager(logger)
        self.__logger = logger
        self.__vim = vim

    def gather_candidates(self, complete_str):
        self.__logger.debug("Gathering candidates")

        try:
            client, connection, transport, ns = gather_conn_info(self.__vim)
        except Error as e:
            self.__logger.exception("Unable to get connection info: " + str(e))
            return []

        host = transport.get("host")
        port = transport.get("port")

        conn_string = "nrepl://{}:{}".format(host, port)

        wc = self.__connmanager.get_conn(conn_string)

        def on_error(e):
            self.__connmanager.remove_conn(conn_string)

        return cider_gather(self.__logger,
                            Fireplace_nrepl(wc),
                            complete_str,
                            connection.get("session"),
                            ns,
                            on_error)
