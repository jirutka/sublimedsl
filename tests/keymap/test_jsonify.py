from sublimedsl.keymap import Binding, Context, jsonify
from textwrap import dedent


def context_given_Context():

    def dumps_attrs_in_defined_order():
        context = Context('text').any().equal('meh')
        assert jsonify(context) == dedent('''\
            {
              "key": "text",
              "operator": "equal",
              "operand": "meh",
              "match_all": false
            }''')

    def omits_None_values():
        context = Context('text')
        assert '"operand"' not in jsonify(context)


def context_given_Binding():

    def dumps_attrs_in_defined_order():
        binding = Binding('x', 'y').to('new_pane', move=False)
        binding.when('foo')
        assert jsonify(binding) == dedent('''\
            {
              "keys": [
                "x",
                "y"
              ],
              "command": "new_pane",
              "args": {
                "move": false
              },
              "context": [
                {
                  "key": "foo"
                }
              ]
            }''')

    def sorts_dict_values():
        binding = Binding('x').to('foo', z=1, o=2, a=3, c=4)
        assert jsonify(binding) == dedent('''\
            {
              "keys": [
                "x"
              ],
              "command": "foo",
              "args": {
                "a": 3,
                "c": 4,
                "o": 2,
                "z": 1
              }
            }''')

    def omits_None_values():
        binding = Binding('x')
        assert '"command"' not in jsonify(binding)

    def omits_empty_dicts():
        binding = Binding('x').to('new_pane')
        assert '"args"' not in jsonify(binding)

    def omits_empty_lists():
        binding = Binding('x').to('new_pane')
        assert '"context"' not in jsonify(binding)
