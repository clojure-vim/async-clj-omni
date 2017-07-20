import threading
from async_clj_omni.cider import cider_gather  # NOQA
try:
    from acid.nvim import localhost, get_acid_ns
    from acid.session import SessionHandler, send
    loaded = True
except:
    loaded = False


class Acid_nrepl:
    def __init__(self, wc):
        self.wc = wc

    def send(self, msg):
        self.wc.send(msg)

    def watch(self, name, q, callback):
        self.wc.watch(name, q, callback)

    def unwatch(self, name):
        self.wc.unwatch(name)


class AcidManager:
    def __init__(self, logger, vim):
        self._vim = vim
        self._logger = logger
        self.__conns = {}

    def on_init(self):
        if loaded:
            self.acid_sessions = SessionHandler()
        else:
            self._logger.debug('Acid.nvim not found. Please install it.')
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

    def gather_candidates(self, keyword):
        if not loaded:
            return []

        address = localhost(self._vim)
        if address is None:
            return []
        url = "nrepl://{}:{}".format(*address)
        wc = self.get_wc(url)
        session = self.get_session(url, wc)
        ns = get_acid_ns(self._vim)

        def global_watch(cmsg, cwc, ckey):
            self._logger.debug("Received message for {}".format(url))
            self._logger.debug(cmsg)

        wc.watch('global_watch', {}, global_watch)

        return cider_gather(self._logger,
                            Acid_nrepl(wc),
                            keyword,
                            session,
                            ns)
