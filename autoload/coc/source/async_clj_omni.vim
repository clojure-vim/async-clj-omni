function! coc#source#async_clj_omni#init() abort
  return {
        \'shortcut': 'clj',
        \'priority': 1,
        \'filetypes': ['clojure'],
        \'firstMatch': 0,
        \'triggerCharacters': ['.', '/', ':'],
        \}
endfunction

function! coc#source#async_clj_omni#complete(opt, cb) abort
  call fireplace#omnicomplete({candidates ->
        \ a:cb(candidates)
        \ },
        \ a:opt.input)
endfunction
