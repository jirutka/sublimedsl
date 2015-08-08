import json
from sublimedsl.keymap import *

# TODO: write proper unit tests!


# Very provisional test that should be replaced ASAP.
def test_integration():
    actual = Keymap(
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
    ).to_json()  # nopep8

    expected = '''[
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
    ]'''  # nopep8

    assert normalize_json(actual) == normalize_json(expected)


def normalize_json(jsondoc):
    return json.dumps(json.loads(jsondoc), indent=2)
