import threading
# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "../../acid"))
sys.path.append(os.path.join(basedir, "../../async_clj_omni"))

try:
    from acid.nvim import localhost, path_to_ns
    from acid.session import SessionHandler, send
    loaded = True
except:
    loaded = False

from async_clj_omni.cider import cider_gather  # NOQA
from .base import Base  # NOQA


class Acid_nrepl:
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
        self.name = "acid"
        self.mark = "[acid]"
        self.filetypes = ['clojure']
        self.rank = 200
        self.__conns = {}

    def on_init(self, context):
        if loaded:
            self.acid_sessions = SessionHandler()
        else:
            self.debug('echomsg "Acid.nvim not found. Please install it."')
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

        return cider_gather(Acid_nrepl(wc),
                            context["complete_str"],
                            session,
                            ns)
