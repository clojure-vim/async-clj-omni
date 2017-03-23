import deoplete.logger
# Adds a git submodule to the import path
import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(basedir, "../../acid"))
sys.path.append(os.path.join(basedir, "../../../../pythonx/"))

from async_clj_omni.acid import Acid_nrepl, AcidManager
from .base import Base  # NOQA


class Source(Base):
    def __init__(self, vim):
        Base.__init__(self, vim)
        self.name = "acid"
        self.mark = "[acid]"
        self.filetypes = ['clojure']
        self.rank = 200
        self._vim = vim
        self._AcidManager = AcidManager(deoplete.logger.getLogger('acid_cider_completion_manager'), vim)

    def on_init(self, context):
        self._AcidManager.on_init()

    def gather_candidates(self, context):
        return self._AcidManager.gather_candidates(context["complete_str"])
