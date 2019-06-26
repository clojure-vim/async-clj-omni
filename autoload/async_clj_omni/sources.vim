let s:short_types = {
      \ 'function': 'f',
      \ 'macro': 'm',
      \ 'var': 'v',
      \ 'special-form': 's',
      \ 'class': 'c',
      \ 'keyword': 'k',
      \ 'local': 'l',
      \ 'namespace': 'n',
      \ 'field': 'i',
      \ 'method': 'f',
      \ 'static-field': 'i',
      \ 'static-method': 'f',
      \ 'resource': 'r'
      \ }

function! s:candidate(val) abort
  let type = get(a:val, 'type', '')
  let arglists = get(a:val, 'arglists', [])
  return {
        \ 'word': get(a:val, 'candidate'),
        \ 'kind': get(s:short_types, type, type),
        \ 'info': get(a:val, 'doc', ''),
        \ 'menu': empty(arglists) ? '' : '(' . join(arglists, ' ') . ')'
        \ }
endfunction

function! s:completor(opt, ctx)
  let l:col = a:ctx['col']
  let l:typed = a:ctx['typed']

  let l:kw = matchstr(l:typed, '\v[[:alnum:]!$%&*+/:<=>?@\^_~\-\.#]+$')
  let l:kwlen = len(l:kw)

  let l:startcol = l:col - l:kwlen

  call fireplace#message({'op': 'complete', 'symbol': l:kw, 'ns': fireplace#ns()},
			  \ { msg -> has_key(msg, 'completions')
			  \ && 
			  \ asyncomplete#complete(a:opt['name'], a:ctx, l:startcol, map(msg['completions'], { _, val -> s:candidate(val) }), 1)})
endfunction

function! async_clj_omni#sources#complete(opt, ctx)
  call s:completor(a:opt, a:ctx)
endfunction
