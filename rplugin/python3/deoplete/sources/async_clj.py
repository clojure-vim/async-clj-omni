# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "vim_nrepl_python_client/"))
sys.path.append(os.path.join(basedir, "../../../../pythonx/async_clj_omni"))

from async_clj_omni.cider import cider_gather  # NOQA
from async_clj_omni import fireplace
from .base import Base  # NOQA
import deoplete.logger


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = "async_clj"
        self.mark = "CLJ"
        self.filetypes = ['clojure']
        self.rank = 200
        self.__connmanager = fireplace.ConnManager(deoplete.logger.getLogger('fireplace_conn_manager'))

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

        wc = self.__connmanager.get_conn(conn_string)

        return cider_gather(deoplete.logger.getLogger('fireplace_cider_gather'),
                            fireplace.Fireplace_nrepl(wc),
                            context["complete_str"],
                            connection.get("session"),
                            ns)
