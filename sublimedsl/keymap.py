"""
DSL for SublimeText's  Key Bindings.

Example:

..  code-block:: python

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

    ).dump()  # nopep8


The above code generates:

..  code-block:: json

    [{
      "keys": [ "backspace" ],
      "command": "run_macro_file",
      "args": { "file": "res://Packages/Default/Delete Left Right.sublime-macro" },
      "context": [
        { "key": "setting.auto_match_enabled", "operator": "equal", "operand": true, "match_all": false },
        { "key": "preceding_text", "operator": "regex_contains", "operand": "_$", "match_all": true },
        { "key": "following_text", "operator": "regex_contains", "operand": "^_", "match_all": true },
        { "key": "selector", "operator": "equal", "operand": "text.asciidoc", "match_all": true }
      ]
    }, {
      "keys": [ "super+k", "super+shift+up" ],
      "command": "new_pane",
      "args": { "move": false },
      "context": [
        { "key": "selector", "operator": "equal", "operand": "text.asciidoc", "match_all": true }
      ]
    }]

See `Key Bindings <http://docs.sublimetext.info/en/latest/reference/key_bindings.html>`_
in the SublimeText documentation.
"""  # nopep8

import json
import sys
from collections import OrderedDict
from copy import deepcopy
from funcy import all_fn, any_fn, complement, iffy, isa, isnone, partial
from funcy import rcompose as pipe
from funcy import first, flatten, lflatten, map, pluck_attr, select_values, walk_values

__all__ = ['Context', 'Binding', 'Keymap', 'bind', 'context']

FILE_HEADER = '''\
// This file is generated, do not edit it by hand!
'''


class Keymap():

    """ Basically a container for key bindings. """

    def __init__(self, *bindings, default_match_all=None, common_context=[]):
        """
        Arguments:
            *bindings (Binding): The key bindings to be added to this keymap.
            default_match_all (Optional[bool]): The default value of ``match_all`` to be
                set when context doesn't specify it. See :meth:`Context.any`
                and :meth:`Context.all`.
            common_context (List[Context]): The context that should be added to all bindings.
        """
        self._default_match_all = default_match_all
        self._common_context = common_context
        self._bindings = self._preprocess(bindings)

    def to_json(self, **kwargs):
        """
        Arguments:
            **kwargs: Options to be passed into :func:`json.dumps`.
        Returns:
            str: A JSON representing this keymap.
        """
        return jsonify(self._bindings, **kwargs)

    def dump(self, fp=sys.stdout, **kwargs):
        """ Serialize this keymap as a JSON formatted stream to the *fp*.

        Arguments:
            fp: A ``.write()``-supporting file-like object to write the
                generated JSON to (default is ``sys.stdout``).
            **kwargs: Options to be passed into :func:`json.dumps`.
        """
        fp.write(FILE_HEADER)
        fp.write(self.to_json(**kwargs))
        fp.write('\n')

    def extend(self, *bindings):
        """ Append the given bindings to this keymap.

        Arguments:
            *bindings (Binding): Bindings to be added.
        """
        self._bindings.extend(self._preprocess(bindings))

    def _preprocess(self, bindings):
        return pipe(
            deepcopy,
            partial(lflatten, follow=isa(list, tuple, Keymap)),
            self._apply_common_context,
            self._apply_default_match_all
        )(bindings)

    def _apply_common_context(self, bindings):
        for binding in bindings:
            binding.context.extend(self._common_context)
        return bindings

    def _apply_default_match_all(self, bindings):
        for context in flatten(pluck_attr('context', bindings)):
            if context.match_all is None:
                context.match_all = self._default_match_all
        return bindings

    def __iter__(self):
        return iter(self._bindings)

    def __lshift__(self, binding):
        self.extend([binding])

    def __len__(self):
        return len(self._bindings)

    def __str__(self):
        return self.jsonify()


class Binding():

    """ Represents a single key binding.

    See `Structure of a Key Binding
    <http://docs.sublimetext.info/en/latest/reference/key_bindings.html#structure-of-a-key-binding>`_
    in the SublimeText documentation.
    """

    def __init__(self, *keys):
        """
        Arguments:
            *keys (str): One or more case-sensitive keys. Modifiers can be
                specified with the ``+`` sign.
        """
        self.keys = keys
        self.command = None
        self.args = []
        self.context = []

    def to(self, command, **args):
        """ Bind the keys to the specified *command* with some *args*.

        Arguments:
            command (str): Name of the ST command (e.g. ``insert_snippet``).
            **args: Arguments for the command.
        Returns:
            Binding: self
        """
        self.command = command
        self.args = args
        return self

    def when(self, key):
        """ Specify context, i.e. condition that must be met.

        Arguments:
            key (str): Name of the context whose value you want to query.
        Returns:
            Context:
        """
        ctx = Context(key, self)
        self.context.append(ctx)
        return ctx

    # aliases
    also = when
    and_ = when

    def __str__(self):
        return jsonify(self)

# alias
bind = Binding


class Context():

    """ Represents a context's condition for a key binding.

    Examples::
        >>> context('preceding_text').regex_match('^[*_-]+')
        '{"key": "preceding_text", "operator": "regex_match", "operand": "^[*_-]+"}'

        >>> context('selector').all().equal('text.asciidoc')
        '{"key": "selector", "operator": "equal", "operand": "text.asciidoc", "match_all": true}'

        >>> context('selection_empty').true()
        '{"key": "selection_empty", "operator": "equal", "operand": true}'

    See `Structure of a Context
    <http://docs.sublimetext.info/en/latest/reference/key_bindings.html#structure-of-a-context>`_
    in the SublimeText documentation.

    All operator methods returns the parent :class:`Binding`, or self if
    parent is ``None``.

    Methods:
        equal(value)
            Specify that the context's value must be equal to the specified value.

        not_equal(value)
            Specify that the context's value must *not* be equal to the specified value.

        regex_match(pattern)
            Specify that the context's value must match the pattern (full match).

        not_regex_match(pattern)
            Specify that the context's value must *not* match the pattern (full match).

        regex_contains(pattern)
            Specify that the context's value must contain the pattern (partial match).

        not_regex_contains(pattern)
            Specify that the context's value must *not* contain the pattern
            (partial match).
    """

    _OPERATORS = [
        'equal', 'not_equal', 'regex_match', 'not_regex_match',
        'regex_contains', 'not_regex_contains'
    ]

    def __init__(self, key, parent=None):
        """
        Arguments:
            key (str): Name of the context whose value you want to query.
            parent: An object that should be returned by the operator methods.
        """
        self.key = key
        self.operator = None
        self.operand = None
        self.match_all = None
        self._parent = parent

    def all(self):
        """ Require the test to succeed for all selections.

        This method sets attribute ``match_all`` to ``True``.

        Returns:
            Context: self (for chaining)
        """
        self.match_all = True
        return self

    def any(self):
        """ Require the test to succeed for at least one selection.

        This method sets attribute ``match_all`` to ``False``.

        Returns:
            Context: self (for chaining)
        """
        self.match_all = False
        return self

    def true(self):
        """ Specify that the context's value must be ``True``.

        This is shortcut for ``equal(True)``.
        """
        return self._operator('equal', True)

    def false(self):
        """ Specify that the context's value must be ``False``.

        This is shortcut for ``equal(False)``.
        """
        return self._operator('equal', False)

    def _operator(self, operator, operand):
        self.operator = operator
        self.operand = operand
        return self._parent or self

    def __getattr__(self, name):
        if name in self._OPERATORS:
            return partial(self._operator, name)
        raise AttributeError

    def __str__(self):
        return jsonify(self, indent=None)

# alias
context = Context


class KeymapJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        ordered_attrs = pipe(
            partial(map, lambda attr: (attr, getattr(obj, attr))),
            partial(remove_values, isnone),
            partial(remove_values, all_fn(isa(list, dict), isempty)),
            partial(walk_values, iffy(isa(dict), sort_dict)),
            OrderedDict)

        if isinstance(obj, Context):
            return ordered_attrs(['key', 'operator', 'operand', 'match_all'])
        elif isinstance(obj, Binding):
            return ordered_attrs(['keys', 'command', 'args', 'context'])
        else:
            return super().default(obj)


def isempty(obj):
    return len(obj) == 0


def remove_values(pred, col):
    return select_values(complement(pred), col)


def sort_dict(dic, key=lambda t: first(t)):
    return OrderedDict(sorted(dic.items(), key=key))


def jsonify(self, indent=2, **kwargs):
    return json.dumps(self, cls=KeymapJSONEncoder, indent=indent, **kwargs)
