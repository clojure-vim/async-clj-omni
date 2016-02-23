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

class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = 'async_clj'
        self.mark = 'CLJ'

    def gather_candidates(self, context):
        self.__conn__ = nrepl.connect("nrepl://localhost:39663")
        self.__conn__.write({"op": "eval", "code": "(map (comp name first) (ns-publics 'clojure.core))"})
        sys.stdout.write('fooooo')
        candidates_str = self.__conn__.read()['value']

        candidates = parse_list(candidates_str)

        return [{'word': x} for x in candidates]
