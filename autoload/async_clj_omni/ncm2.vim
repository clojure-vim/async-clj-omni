if exists('g:async_clj_omni_loaded_ncm2')
    finish
endif
let g:async_clj_omni_loaded_ncm2 = 1

function! s:on_complete(c)
  call fireplace#omnicomplete({candidates ->
        \ ncm2#complete(a:c, a:c.startccol, candidates, 1)
        \ },
        \ a:c.base)
endf

function! async_clj_omni#ncm2#init()
  call  ncm2#register_source({
        \ 'name': 'async_clj_omni',
        \ 'mark': 'clj',
        \ 'priority': 9,
        \ 'word_pattern': '[\w!$%&*+/:<=>?@\^_~\-\.#]+',
        \ 'complete_pattern': ['\.', '/'],
        \ 'complete_length': 2,
        \ 'matcher': 'none',
        \ 'scope': ['clojure'],
        \ 'on_complete': function('<SID>on_complete'),
        \ })
endf
