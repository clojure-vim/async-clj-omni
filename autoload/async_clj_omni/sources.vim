function! s:completor(opt, ctx) abort
  let l:col = a:ctx['col']
  let l:typed = a:ctx['typed']

  let l:kw = matchstr(l:typed, '\v[[:alnum:]!$%&*+/:<=>?@\^_~\-\.#]+$')
  let l:kwlen = len(l:kw)

  let l:startcol = l:col - l:kwlen

  call fireplace#omnicomplete({candidates ->
        \ asyncomplete#complete(a:opt['name'], a:ctx, l:startcol, candidates, 1)},
        \ l:kw)
endfunction

function! async_clj_omni#sources#complete(opt, ctx)
  call s:completor(a:opt, a:ctx)
endfunction
