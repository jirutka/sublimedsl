from sublimedsl.keymap import Context, context
from pytest import fixture


@fixture
def subject():
    return Context('foo', object())


def describe_init():

    def sets_attr_key(subject):
        assert subject.key == 'foo'


def describe_operators():

    @fixture(params=[
        'equal', 'not_equal', 'regex_match', 'not_regex_match',
        'regex_contains', 'not_regex_contains'])
    def operator(request):
        return request.param

    def sets_attr_operator(operator, subject):
        getattr(subject, operator)(42)
        assert subject.operator == operator

    def sets_attr_operand(operator, subject):
        getattr(subject, operator)(42)
        assert subject.operand == 42

    def returns_parent_when_parent_is_set(operator):
        parent = object()
        subject = Context('foo', parent)
        result = getattr(subject, operator)(42)
        assert result == parent

    def returns_self_when_parent_is_not_set(operator):
        subject = Context('foo')
        result = getattr(subject, operator)(42)
        assert result == subject


def describe_all():

    def sets_attr_match_all_to_true(subject):
        subject.all()
        assert subject.match_all is True

    def returns_self(subject):
        assert subject.all() == subject


def describe_any():

    def sets_attr_match_all_to_false(subject):
        subject.any()
        assert subject.match_all is False

    def returns_self(subject):
        assert subject.all() == subject


def describe_eq():

    def returns_true_when_public_attrs_are_equal():
        first = Context('foo', object())
        second = Context('foo', object())
        assert first == second

        first.all().equal(42)
        second.all().equal(42)
        assert first == second

    def returns_false_when_given_different_type():
        assert Context('foo') != 'foo'

    def returns_false_when_public_attrs_are_not_equal():
        assert Context('foo') != Context('bar')
        assert Context('foo').all() != Context('bar').any()
        assert Context('foo').equal(42) != Context('foo').not_equal(42)
        assert Context('foo').equal(42) != Context('foo').equal(55)


def test_context_is_alias_for_Context():
    assert context is Context
