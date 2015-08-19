from sublimedsl.keymap import Binding, Context, bind
from pytest import fixture


@fixture
def subject():
    return Binding('x')


def describe_init():

    def sets_attr_keys():
        subject = Binding('x', 'y')
        assert subject.keys == ('x', 'y')


def describe_to():

    def sets_attr_command(subject):
        subject.to('fire')
        assert subject.command == 'fire'

    def stores_kwargs_in_attr_args(subject):
        subject.to('fire', a=1, b=2)
        assert subject.args == {'a': 1, 'b': 2}

    def returns_self(subject):
        assert subject.to('fire') is subject


def describe_when():

    def returns_Context_with_key_and_parent(subject):
        result = subject.when('foo')
        assert isinstance(result, Context)
        assert result.key == 'foo'
        assert result._parent is subject

    def adds_Context_to_attr_context(subject):
        result = subject.when('foo')
        assert subject.context == [result]


def describe_also():

    def is_alias_for_when():
        assert Binding.when is Binding.also


def describe_and_():

    def is_alias_for_when():
        assert Binding.when is Binding.and_


def describe_eq():

    def returns_true_when_attrs_are_equal():
        first = Binding('x', 'y').to('fire', a=42)
        second = Binding('x', 'y').to('fire', a=42)
        assert first == second

        first.when('foo')
        second.when('foo')
        assert first == second

    def returns_false_when_given_different_type():
        assert Binding('x') != 'x'

    def returns_false_when_attrs_are_not_equal():
        assert Binding('x', 'y') != Binding('x')
        assert Binding('x').to('fire') != Binding('x').to('water')
        assert Binding('x').to('fire', a=42) != Binding('x').to('water', a=24)

        first = Binding('x').to('fire').when('a').true()
        second = Binding('x').to('fire').when('a').false()
        assert first != second


def test_bind_is_alias_for_Binding():
    assert bind is Binding
