# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "vim_nrepl_python_client/"))
sys.path.append(os.path.join(basedir, "../../../../pythonx/async_clj_omni"))

from async_clj_omni.cider import cider_gather  # NOQA
from async_clj_omni import fireplace
from .base import Base  # NOQA
import nrepl  # NOQA


class Fireplace_nrepl:
    def __init__(self, wc):
        self.wc = wc

    def send(self, msg):
        self.wc.send(msg)

    def watch(self, name, q, callback):
        self.wc.watch(name, q, callback)

    def unwatch(self, name):
        self.wc.unwatch(name)


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = "async_clj"
        self.mark = "CLJ"
        self.filetypes = ['clojure']
        self.rank = 200
        self.__conns = {}

    def gather_candidates(self, context):
        self.debug("Gathering candidates")

        try:
            client, connection, transport, ns = fireplace.gather_conn_info(self.vim)
        except fireplace.Error:
            self.exception("Unable to get connection info")
            return []

        host = transport.get("host")
        port = transport.get("port")

        conn_string = "nrepl://{}:{}".format(host, port)

        if conn_string not in self.__conns:
            conn = nrepl.connect(conn_string)

            def global_watch(cmsg, cwc, ckey):
                self.debug("Received message for {}".format(conn_string))
                self.debug(cmsg)

            wc = nrepl.WatchableConnection(conn)
            self.__conns[conn_string] = wc
            wc.watch("global_watch", {}, global_watch)

        wc = self.__conns.get(conn_string)
        self.debug(self.__conns)

        return cider_gather(Fireplace_nrepl(wc),
                            context["complete_str"],
                            connection.get("session"),
                            ns)
