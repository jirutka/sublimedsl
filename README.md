SublimeDSL
==========
[![Build Status](https://api.travis-ci.org/jirutka/sublimedsl.svg?branch=master)](https://travis-ci.org/jirutka/sublimedsl)
[![Coverage Status](https://coveralls.io/repos/jirutka/sublimedsl/badge.svg?branch=master&service=github)](https://coveralls.io/github/jirutka/sublimedsl?branch=master)
[![Code Climate](https://codeclimate.com/github/jirutka/sublimedsl/badges/gpa.svg)](https://codeclimate.com/github/jirutka/sublimedsl)
[![version](https://img.shields.io/pypi/v/sublimedsl.svg?style=flat)](https://pypi.python.org/pypi/sublimedsl)
[![downloads](https://img.shields.io/pypi/dm/sublimedsl.svg?style=flat)](https://pypi.python.org/pypi/sublimedsl)
[![documentation](https://readthedocs.org/projects/sublimedsl/badge/?version=latest)](http://sublimedsl.readthedocs.org/en/latest/)

The configuration of Sublime Text uses verbose JSON files, XML files, and also horrible PList/XML files (TextMate legacy).
When used in plugins, some of them (e.g. keymaps) may contain even hundreds of lines with huge ratio of duplications.
Sooner or later, it’ll become quite hard to maintain such a mess.

The aim of this module is to provide simple pythonic DSL for generating particular configuration files.
Currently only [Key Bindings](http://docs.sublimetext.info/en/latest/reference/key_bindings.html) are supported, but other configs may come later.

You’re more than welcome to add DSL for other Sublime Text’s configs!


## Usage

### Examples

```python
#!/usr/bin/env python3
from sublimedsl.keymap import *

Keymap(
    bind('backspace')
        .to('run_macro_file', file='res://Packages/Default/Delete Left Right.sublime-macro')
        .when('setting.auto_match_enabled').any().true()
        .also('preceding_text').regex_contains(r'_$')
        .also('following_text').regex_contains(r'^_'),

    bind('super+k', 'super+shift+up')
        .to('new_pane', move=False),

    common_context=[
        context('selector').equal('text.asciidoc')
    ],
    default_match_all=True

).dump()
```

The above code generates:

```json
[
  {
    "keys": [ "backspace" ],
    "command": "run_macro_file",
    "args": { "file": "res://Packages/Default/Delete Left Right.sublime-macro" },
    "context": [
      { "key": "setting.auto_match_enabled", "operator": "equal", "operand": true, "match_all": false },
      { "key": "preceding_text", "operator": "regex_contains", "operand": "_$", "match_all": true },
      { "key": "following_text", "operator": "regex_contains", "operand": "^_", "match_all": true },
      { "key": "selector", "operator": "equal", "operand": "text.asciidoc", "match_all": true }
    ]
  },
  {
    "keys": [ "super+k", "super+shift+up" ],
    "command": "new_pane",
    "args": { "move": false },
    "context": [
      { "key": "selector", "operator": "equal", "operand": "text.asciidoc", "match_all": true }
    ]
  }
]
```

You can also look at real-world example in the [Asciidoctor plugin](https://github.com/asciidoctor/sublimetext-asciidoc/): [Keymap DSL](https://github.com/asciidoctor/sublimetext-asciidoc/blob/master/Keymaps/Default.sublime-keymap.py) and [generated JSON](https://github.com/asciidoctor/sublimetext-asciidoc/blob/master/Keymaps/Default.sublime-keymap).


## Installation

### System-wide

Install from PyPI system-wide:

    sudo pip install sublimedsl

…or manually:

    git clone git@github.com:jirutka/sublimedsl.git
    cd sublimedsl
    sudo ./setup.py install

### Locally

If you don’t have a root access to the system, or just don’t want to install sublimedsl system-wide, then you can tell `pip` or `setup.py` to install it into your home directory (namely `~/.local`):

    pip install --user sublimedsl

…or manually:

    git clone git@github.com:jirutka/sublimedsl.git
    cd sublimedsl
    ./setup.py --user install


## License

This project is licensed under [MIT license](http://opensource.org/licenses/MIT).
