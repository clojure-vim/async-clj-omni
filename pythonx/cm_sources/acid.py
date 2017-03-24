# -*- coding: utf-8 -*-

from cm import register_source, getLogger, Base
register_source(name='acid',
                abbreviation='acid',
                scopes=['clojure'],
                word_pattern=r'[\w!$%&*+/:<=>?@\^_~\-\.#]+',
                priority=9)

import os
import sys
import re

class Source(Base):
    def __init__(self,nvim):
        super(Source,self).__init__(nvim)
        # TODO Why is this necessary when it isn't in deoplete sources?
        sys.path.append(os.path.join(nvim.eval('globpath(&rtp,"rplugin/python3/acid",1)').split("\n")[0], ".."))
        from async_clj_omni import acid
        self._nvim = nvim
        self._acid_manager = acid.AcidManager(getLogger(__name__), nvim)
        self._acid_manager.on_init()

    def cm_refresh(self,info,ctx):
        getLogger(__name__).debug('Running a refresh…')
        matches = self._acid_manager.gather_candidates(ctx['base'])
        # matches = ['foo', 'foobard', 'bazzer']
        getLogger(__name__).debug('Got matches', matches)
        self._nvim.call('cm#complete', info['name'], ctx, ctx['startcol'], matches, 1, async=True)
