# -*- coding: utf-8 -*-

from cm import register_source, getLogger, Base
register_source(name='fireplace',
                abbreviation='🔥',
                scopes=['clojure'],
                word_pattern=r'[\w!$%&*+/:<=>?@\^_~\-\.#]+',
                priority=9)

import sys
import os
basedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.normpath(os.path.join(basedir, "../../rplugin/python3/deoplete/sources/vim_nrepl_python_client")))
from async_clj_omni import fireplace
import re

class Source(Base):
    def __init__(self,nvim):
        super(Source,self).__init__(nvim)
        self._nvim = nvim
        self._cider_completion_manager = fireplace.CiderCompletionManager(getLogger(__name__), nvim)

    def cm_refresh(self,info,ctx):
        getLogger(__name__).debug('Running a refresh…')
        matches = self._cider_completion_manager.gather_candidates(re.search(info['word_pattern'], ctx['typed']).group(0))
        self._nvim.call('cm#complete', info['name'], ctx, ctx['startcol'], matches, 1, async=True)
