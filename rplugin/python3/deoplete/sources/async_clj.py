# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "vim_nrepl_python_client/"))
sys.path.append(os.path.join(basedir, "../../../../pythonx/async_clj_omni"))

# from async_clj_omni.cider import cider_gather  # NOQA
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
        self.__cider_completion_manager = fireplace.CiderCompletionManager(deoplete.logger.getLogger('fireplace_cider_completion_manager'), vim)

    def gather_candidates(self, context):
        return self.__cider_completion_manager.gather_candidates(context["complete_str"])
