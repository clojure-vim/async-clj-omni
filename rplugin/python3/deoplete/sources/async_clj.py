import uuid
import threading
# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "nrepl_python_client/"))

from .base import Base  # NOQA
import nrepl  # NOQA


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


def completion_callback(event):
    def handlecompletion(msg, wc, key):
        pass
    return handlecompletion


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = "async_clj"
        self.mark = "CLJ"
        self.filetypes = ['clojure']
        self.rank = 200
        self.__conns = {}

    def gather_candidates(self, context):
        client = False
        try:
            client = self.vim.eval("fireplace#client()")
        except Exception:
            pass

        if client:
            connection = client.get("connection", {})
            transport = connection.get("transport")
            if not transport:
                return []

            ns = ""
            try:
                ns = self.vim.eval("fireplace#ns()")
            except Exception:
                pass

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

            # Should be unique for EVERY message
            msgid = uuid.uuid4().hex

            # Perform completion
            completion_event = threading.Event()
            response = None

            def completion_callback(cmsg, cwc, ckey):
                nonlocal response
                response = cmsg
                completion_event.set()

            self.debug("Adding completion watch")
            watcher_key = "{}-completion".format(msgid),
            wc.watch(watcher_key,
                     {"id": msgid},
                     completion_callback)

            # TODO: context for context aware completions
            self.debug("Sending completion op")
            wc.send({
                "id": msgid,
                "op": "complete",
                "session": connection.get('session'),
                "symbol": context["complete_str"],
                "extra-metadata": ["arglists", "doc"],
                "ns": ns
            })

            self.debug("Waiting for completion")
            completion_event.wait(timeout=0.5)
            self.debug("Completion event is done!")
            wc.unwatch(watcher_key)
            # Bencode read can return None, e.g. when and empty byte is read
            # from connection.
            if response:
                return [candidate(x) for x in response.get("completions", [])]

        return []
