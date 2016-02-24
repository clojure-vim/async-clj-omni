# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, 'nrepl_python_client/'))

from .base import Base
# from nrepl_python_client import nrepl
import nrepl

def parse_list(l_s):
    """
    Parses a clojure list in the form '("foo" "bar" "baz")' into
    a Python array, like ["foo", "bar", "baz"]. This function is
    very crude.
    """
    return l_s[1:-1].replace('"', '').split(" ")

def debug_msg(vim, msg):
    vim.current.buffer.append("{}".format(msg))

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'async_clj'
        self.mark = 'CLJ'

    def gather_candidates(self, context):
        client = False
        try:
            client = self.vim.eval("fireplace#client()")
        except Exception:
            pass

        r = []
        if client:
            transport = client['connection']['transport']
            ns = self.vim.eval("fireplace#ns()")


            self.__conn__ = nrepl.connect("nrepl://{}:{}".format(transport['host'], transport['port']))
            self.__conn__.write({"op": "complete", "symbol": context['complete_str'], "ns": ns})
            c_result = self.__conn__.read()
            candidates_map = c_result["completions"]

            candidates = [x['candidate'] for x in candidates_map]

            r = [{'word': x} for x in candidates]

        return r
