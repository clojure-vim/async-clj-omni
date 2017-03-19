import nrepl  # NOQA

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

def gather_conn_info(vim):
    try:
        client = vim.eval("fireplace#client()")
    except Exception:
        raise Error

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
    def __init__(self):
        self.__conns = {}

    def get_conn(self, conn_string):
        if conn_string not in self.__conns:
            conn = nrepl.connect(conn_string)

            # def global_watch(cmsg, cwc, ckey):
            #     self.debug("Received message for {}".format(conn_string))
            #     self.debug(cmsg)

            wc = nrepl.WatchableConnection(conn)
            self.__conns[conn_string] = wc
            # wc.watch("global_watch", {}, global_watch)

        return self.__conns.get(conn_string)
