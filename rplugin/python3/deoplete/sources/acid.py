import uuid
import threading
# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "vim_nrepl_python_client/"))
sys.path.append(os.path.join(basedir, "../../acid"))

try:
    from acid.nvim import localhost, path_to_ns
    from acid.session import SessionHandler, send
    loaded = True
except:
    loaded = False

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
        self.name = "acid"
        self.mark = "[acid]"
        self.filetypes = ['clojure']
        self.rank = 200
        self.__conns = {}

    def on_init(self, context):
        if loaded:
            self.acid_sessions = SessionHandler()
        else:
            self.vim.command('echomsg "Acid.nvim not found. Please install it."')
        self.sessions = {}

    def get_wc(self, url):
        return self.acid_sessions.get_or_create(url)

    def get_session(self, url, wc):
        if url in self.sessions:
            return self.sessions[url]

        session_event = threading.Event()

        def clone_handler(msg, wc, key):
            wc.unwatch(key)
            self.sessions[url] = msg['new-session']
            session_event.set()

        wc.watch('dyn-session', {'new-session': None}, clone_handler)
        wc.send({'op': 'clone'})
        session_event.wait(0.5)

        return self.sessions[url]

    def gather_candidates(self, context):
        if not loaded:
            return []

        address = localhost(self.vim)
        if address is None:
            return []
        url = "nrepl://{}:{}".format(*address)
        wc = self.get_wc(url)
        session = self.get_session(url, wc)
        ns = path_to_ns(self.vim)

        def global_watch(cmsg, cwc, ckey):
            self.debug("Received message for {}".format(url))
            self.debug(cmsg)

        wc.watch('global_watch', {}, global_watch)

        # Should be unique for EVERY message
        msgid = uuid.uuid4().hex

        # Perform completion
        completion_event = threading.Event()
        response = None

        def completion_callback(cmsg, cwc, ckey):
            nonlocal response
            response = cmsg
            self.debug("Got response {}".format(str(cmsg)))
            completion_event.set()

        self.debug("Adding completion watch")
        watcher_key = "{}-completion".format(msgid),
        wc.watch(watcher_key, {"id": msgid}, completion_callback)

        # TODO: context for context aware completions
        self.debug("Sending completion op")
        try:
            payload = {"id": msgid,
                       "op": "complete",
                       "symbol": context["complete_str"],
                       "session": session,
                       "extra-metadata": ["arglists", "doc"],
                       "ns": ns}
            self.debug('Sending payload {}'.format(str(payload)))
            wc.send(payload)
        except BrokenPipeError:
            self.debug("Connection died. Removing the connection.")
            wc.close() # Try and cancel the hanging connection
            del self.acid_sessions.sessions[url]

        self.debug("Waiting for completion")
        completion_event.wait(0.5)
        self.debug("Completion event is done!")
        wc.unwatch(watcher_key)
        # Bencode read can return None, e.g. when and empty byte is read
        # from connection.
        if response:
            return [candidate(x) for x in response.get("completions", [])]

        self.debug('No answer.')
        return []
