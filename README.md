[![Stories in Ready](https://badge.waffle.io/SevereOverfl0w/async-clj-omni.png?label=ready&title=Ready)](https://waffle.io/SevereOverfl0w/async-clj-omni)
# clj-async.nvim

Provides async clojure completion through [deoplete.nvim][] and
[nrepl-python-client][].

Trying to use Fireplace's omnicompletion with auto-complete is painfully
slow at times, making typing blocked. Using this module will be faster as
it does not block, it runs in it's own thread.

## Installation

Follow the install instructions for [deoplete.nvim][]. I'm not going to try
and sync them here. Then just include with your favourite plugin manager,
mine is [vim-plug][]

```vim
Plug 'clojure-vim/async-clj-omni'
```

You also need to include the following lines in your init.vim:

```vim
let g:deoplete#keyword_patterns = {}
let g:deoplete#keyword_patterns.clojure = '[\w!$%&*+/:<=>?@\^_~\-\.]*'
```

As I improve them, they may be PR'd into deoplete.vim, but I'm not yet
comfortable suggesting that change upstream.

## Developing

A few snippets and tidbits for development:

```vimscript
:call deoplete#custom#set('async_clj', 'debug_enabled', 1)
:call deoplete#enable_logging("DEBUG", "/tmp/deopletelog")
```

Then you can this command to watch debug statements:
```bash
$ tail -f /tmp/deopletelog
```

Debug statements can be made in the source via:
```python
self.debug(msg)
```

## FAQ

1. Why do you include [nrepl-python-client][] via submodule.

   I made the decision that it was more complex to have users try and manage a
   version of [nrepl-python-client][], than it was for them to "just" have it
   included. In an ideal world, I'd be able to use virtualenv with the
   Python/Neovim, but this isn't currently a realistic expectation for all
   users to be able to use.


[deoplete.nvim]: https://github.com/Shougo/deoplete.nvim
[nrepl-python-client]: https://github.com/cemerick/nrepl-python-client
[vim-plug]: https://github.com/junegunn/vim-plug
