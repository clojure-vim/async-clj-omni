# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "nrepl_python_client/"))

from .base import Base
# from nrepl_python_client import nrepl
import nrepl


def debug_msg(vim, msg):
    vim.current.buffer.append("{}".format(msg))


short_types = {
    "function": "f",
    "macro": "m",
    "var": "v",
    "special-form": "s",
    "class": "c",
    "keyword": "k",
    "local": "l",
    "namespace": "n",
    "field": "i",
    "method": "f",
    "static-field": "i",
    "static-method": "f",
    "resource": "r"
}


def candidate(val):
    arglists = val.get("arglists")
    type = val.get("type")
    return {
        "word": val.get("candidate"),
        "kind": short_types.get(type, type),
        "info": val.get("doc", ""),
        "menu": " ".join(arglists) if arglists else ""
    }


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = "async_clj"
        self.mark = "CLJ"
        self.filetypes = ['clojure']
        self.rank = 200

    def gather_candidates(self, context):
        client = False
        try:
            client = self.vim.eval("fireplace#client()")
        except Exception:
            pass

        if client:
            transport = client.get("connection", {}).get("transport")
            ns = ""

            try:
                ns = self.vim.eval("fireplace#ns()")
            except Exception:
                pass

            # FIXME: Connection is not reused?
            self.__conn__ = nrepl.connect("nrepl://{}:{}".format(transport.get("host"), transport.get("port")))
            # TODO: context for context aware completions
            self.__conn__.write({
                "op": "complete",
                "symbol": context["complete_str"],
                "extra-metadata": ["arglists", "doc"],
                "ns": ns
            })
            response = self.__conn__.read()

            return [candidate(x) for x in response.get("completions", [])]

        return []
