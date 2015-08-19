from io import StringIO
from sublimedsl import keymap
from sublimedsl.keymap import Keymap, bind, context
from pytest import fixture


@fixture
def subject():
    return Keymap()

@fixture
def bindings():
    return [bind('x'), bind('y'), bind('z')]

@fixture
def binding1():
    return (bind('x').to('fire')
            .when('foo').any().true()
            .also('bar').true()
            .also('baz').all().false())


def describe_preprocess():

    def creates_deepcopy(subject, bindings):
        result = subject._preprocess(bindings)
        assert all([new == orig for new, orig in zip(result, bindings)])
        assert all([new is not orig for new, orig in zip(result, bindings)])

    def flattens_nested_lists(subject, bindings):
        nested = [bind('x'), [bind('y'), [bind('z')]]]
        assert subject._preprocess(nested) == bindings

    def flattens_nested_tuples(subject, bindings):
        nested = (bind('x'), (bind('y'), (bind('z'),)))
        assert subject._preprocess(nested) == bindings

    def flattens_nested_keymaps(subject, bindings):
        nested = [Keymap(bind('x'), Keymap(bind('y'))), bind('z')]
        assert subject._preprocess(nested) == bindings

    def injects_common_context_to_bindings(binding1):
        bindings = [binding1, bind('x')]
        contexts = [context('abc').equal(42), context('def').any().equal(55)]

        result = Keymap(common_context=contexts)._preprocess(bindings)

        assert result[0].context == binding1.context + contexts
        assert result[1].context == contexts

    def context_default_match_all_is_None():

        def does_not_change_anything(binding1):
            result = Keymap(default_match_all=None)._preprocess([binding1])
            assert result[0] == binding1

    def context_default_match_all_is_True():

        def change_match_all_None_to_True_in_bindings_contexts(binding1):
            result = Keymap(default_match_all=True)._preprocess([binding1])
            assert [cxt.match_all for cxt in result[0].context] == [False, True, True]

    def context_default_match_all_is_False():

        def change_match_all_None_to_False_in_bindings_contexts(binding1):
            result = Keymap(default_match_all=False)._preprocess([binding1])
            assert [cxt.match_all for cxt in result[0].context] == [False, False, True]


def describe_init():

    def preprocesses_given_bindings(bindings, mocker):
        processed = [bind('a'), bind('b')]
        mocker.patch.object(Keymap, '_preprocess', return_value=processed)

        subject = Keymap(*bindings)

        Keymap._preprocess.assert_called_with(tuple(bindings))
        assert list(iter(subject)) == processed


def describe_extend():

    def preprocesses_given_bindings_and_adds_them(subject, bindings, mocker):
        processed = [bind('a'), bind('b')]
        mocker.patch.object(Keymap, '_preprocess', return_value=processed)

        subject.extend(*bindings)

        Keymap._preprocess.assert_called_with(tuple(bindings))
        assert list(iter(subject)) == processed

    def returns_self(subject, bindings):
        assert subject.extend(*bindings) is subject


def describe_to_json():

    def returns_jsonified_bidings(bindings, mocker):
        mocker.patch('sublimedsl.keymap.jsonify', return_value='--json--')
        subject = Keymap(bindings)

        assert subject.to_json(indent=4) == '--json--'
        keymap.jsonify.assert_called_with(bindings, indent=4)


def describe_dump():

    def writes_file_header_and_jsonified_bindings_to_given_fp(subject, mocker):
        fp = StringIO()
        mocker.patch.object(Keymap, 'to_json', return_value='--json--')

        subject.dump(fp=fp)

        assert fp.getvalue() == keymap.FILE_HEADER + '--json--' + '\n'


def describe_iter():

    def iterates_over_bindings(bindings):
        subject = Keymap(*bindings)
        assert list(iter(subject)) == bindings


def describe_lshift():

    def wraps_value_and_calls_extend(subject, binding1, mocker):
        mocker.patch.object(Keymap, 'extend')

        subject << binding1

        Keymap.extend.assert_called_with([binding1])


def describe_len():

    def returns_number_of_bindings(bindings):
        subject = Keymap(*bindings)
        assert len(subject) == len(bindings)


def describe_str():

    def delegates_to_to_json(subject, mocker):
        mocker.patch.object(Keymap, 'to_json', return_value='--json--')
        assert str(subject) == '--json--'
