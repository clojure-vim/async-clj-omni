augroup async_clj_omni_plugins
  autocmd!
  autocmd User cmp#ready call async_clj_omni#cmp#register()
augroup END
