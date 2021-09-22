let s:source = {}

function! s:source.new() abort
  return deepcopy(s:source)
endfunction

function! s:source.is_available()
  if fireplace#op_available('complete')
    return v:true
  else
    return v:false
  endif
endfunction

function! s:source.get_keyword_pattern(params)
  " Minimum 2 letters because completion on "y" doesn't resolve any
  " namespaces, but "ya" will resolve on "yada".
  return '\k\k\+'
endfunction

function! s:source.get_trigger_characters(params)
  return ['/', '.', ':']
endfunction

" unfortunately f is for both function & static method.  to workaround, we'll
" need to go to a lower level than fireplace#omnicomplete, which would lose us
" the context of the completion from surrounding lines.
let s:lsp_kinds = luaeval("
\ (function()
\  local cmp = require'cmp'
\  return {f = cmp.lsp.CompletionItemKind.Function,
\          m = cmp.lsp.CompletionItemKind.Function,
\          v = cmp.lsp.CompletionItemKind.Variable,
\          s = cmp.lsp.CompletionItemKind.Keyword,
\          c = cmp.lsp.CompletionItemKind.Class,
\          k = cmp.lsp.CompletionItemKind.Keyword,
\          l = cmp.lsp.CompletionItemKind.Variable,
\          n = cmp.lsp.CompletionItemKind.Module,
\          i = cmp.lsp.CompletionItemKind.Field,
\          r = cmp.lsp.CompletionItemKind.File,}
\ end)()")

function! s:coerce_to_lsp(vc)
  return {'label': a:vc.word,
        \ 'labelDetails': {
        \   'detail': a:vc.menu,
        \   },
        \ 'documentation': a:vc.info,
        \ 'kind': get(s:lsp_kinds, a:vc.kind, 1)
        \ }
endf

function! s:source.complete(params, callback) abort
  let l:kw = a:params.context.cursor_before_line[(a:params.offset-1):]

  call fireplace#omnicomplete({candidates ->
        \ a:callback(map(candidates,
        \  {_, val -> s:coerce_to_lsp(val)}))
        \ },
        \ l:kw)
endfunction

function async_clj_omni#cmp#register()
  call cmp#register_source('async_clj_omni', s:source.new())
endf
