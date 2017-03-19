# -*- coding: utf-8 -*-

from cm import register_source
register_source(name='fireplace',
                abbreviation='🔥',
                scopes=['clojure'],
                word_pattern=r'[\w!$%&*+/:<=>?@\^_~\-\.#]+',
                priority=9)
                # TODO early_cache = 0 OR figure out cm_refresh_patterns

import re

class Source:
    def __init__(self,nvim):
        self._nvim = nvim

    def cm_refresh(self,info,ctx):
        matches = ['foo_bar','foo_baz', 'req$\'uire']
        self._nvim.call('cm#complete', info['name'], ctx, ctx['startcol'], matches, async=True)
