" cmp isn't guaranteed to be loaded before this file runs, which is why we
" leave the option to manually register.
if exists('*cmp#register_source')
  call async_clj_omni#cmp#register()
endif
