import ast
import functools
import os
import sys
from textwrap import dedent
import unittest

try:
    from unittest import skipIf
except ImportError:
    skipIf = None


from nose.tools import assert_equal

from flake8_print import PrintStatementChecker


SHOULD_ADD_FUTURE_PRINT = os.environ.get('FUTURE_PRINT') == '1'
HAS_PRINT_FN = SHOULD_ADD_FUTURE_PRINT or sys.version_info[0] >= 3

if skipIf:
    run_if_print_function = functools.partial(
            skipIf,
            condition=not HAS_PRINT_FN,
            reason='Skipping py2 w/o __future__: no print function')

    run_if_print_statement = functools.partial(
            skipIf,
            condition=HAS_PRINT_FN,
            reason='Skipping py3 and py2 w/ __future__: no print statement')

else:
    # Python 2.6 does not have skipIf or SkipTest, so
    # completely skip the test which will be reported as success.
    def noop_decorator():
        """Decorator to unconditionally skip test method."""
        def noop(*args, **kwargs):
            pass

        return noop

    run_if_print_function = noop_decorator
    run_if_print_statement = noop_decorator


def check_code_for_print_statements(code):
    if SHOULD_ADD_FUTURE_PRINT:
        code = 'from __future__ import print_function\n' + code
    line_offset = -1 if SHOULD_ADD_FUTURE_PRINT else 0

    checker = PrintStatementChecker(ast.parse(code))
    results = []
    for line_number, offset, msg, instance in checker.run():
        results.append({'line': line_number + line_offset, 'col': offset, 'message': msg})
    return results


class Flake8PrintTestCases(unittest.TestCase):
    pass


T001 = 'T001 print statement found.'
T003 = 'T003 print function found.'
T101 = 'T101 Python 2.x reserved word print used.'


@run_if_print_function()
class TestGenericCasesWithPrintFn(Flake8PrintTestCases):
    def test_catches_multiline_print(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b")
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    def test_catches_empty_print_expression(self):
        result = check_code_for_print_statements('print')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T101}])

    def test_catches_simple_print(self):
        result = check_code_for_print_statements('print(4)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    def test_catches_print_multiline(self):
        result = check_code_for_print_statements('print(0\n)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    def test_catches_empty_print(self):
        result = check_code_for_print_statements('print(\n)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])


@run_if_print_statement()
class TestGenericCasesWithoutPrintFn(Flake8PrintTestCases):
    def test_catches_multiline_print(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b")
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_empty_print_statement(self):
        result = check_code_for_print_statements('print')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_simple_print_python2(self):
        result = check_code_for_print_statements('print 4')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_print_multiline(self):
        result = check_code_for_print_statements('print(0\n)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_empty_print(self):
        result = check_code_for_print_statements('print(\n)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])


class TestComments(Flake8PrintTestCases):
    def test_print_in_inline_comment_is_not_a_false_positive(self):
        result = check_code_for_print_statements('# what should I print ?')
        assert_equal(result, list())

    @run_if_print_function()
    def test_print_fn_same_line_as_comment(self):
        result = check_code_for_print_statements('print(5) # what should I do with 5 ?')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    @run_if_print_statement()
    def test_print_statement_same_line_as_comment(self):
        result = check_code_for_print_statements('print 5 # what should I do with 5 ?')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])


class TestSingleQuotes(Flake8PrintTestCases):
    def test_print_in_one_single_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a(\'print the things\', 25)')
        assert_equal(result, list())

    def test_print_in_three_single_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a(\'\'\'print the things\'\'\', 25)')
        assert_equal(result, list())


class TestDoubleQuotes(Flake8PrintTestCases):
    def test_print_in_one_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a("print the things", 25)')
        assert_equal(result, list())

    def test_print_in_three_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a("""print the things""", 25)')
        assert_equal(result, list())


class TestMultilineFalsePositive(Flake8PrintTestCases):
    def test_print_in_one_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('hello="""there is a \nprint on\n the next line"""')
        assert_equal(result, list())

    def test_print_in_three_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a("""print the things""", 25)')
        assert_equal(result, list())


class TestNameFalsePositive(Flake8PrintTestCases):
    def test_print_in_name(self):
        result = check_code_for_print_statements('def print_foo(): pass')
        assert_equal(result, [])
        result = check_code_for_print_statements('def foo_print(): pass')
        assert_equal(result, [])
        result = check_code_for_print_statements('foo_print = 1')
        assert_equal(result, [])
        result = check_code_for_print_statements('print_foo = 1')
        assert_equal(result, [])


@run_if_print_function()
class TestPython3NameFalsePositive(Flake8PrintTestCases):
    def test_redefine_print_function(self):
        result = check_code_for_print_statements('def print(): pass')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T101}])

    def test_print_method(self):
        result = check_code_for_print_statements(dedent("""
            class Foo:
                def print(self):
                    pass
        """))
        assert_equal(result, [{'col': 4, 'line': 3, 'message': T101}])

    def test_print_arg(self):
        result = check_code_for_print_statements('def foo(print): pass')
        assert_equal(result, [{'col': 8, 'line': 1, 'message': T101}])

    def test_print_assignment(self):
        result = check_code_for_print_statements('print=1')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T101}])

    def test_print_assignment_value(self):
        result = check_code_for_print_statements('x = print')
        assert_equal(result, [{'col': 4, 'line': 1, 'message': T101}])

    def test_print_assignment_value_else(self):
        result = check_code_for_print_statements('x = print if True else 1')
        assert_equal(result, [{'col': 4, 'line': 1, 'message': T101}])
        result = check_code_for_print_statements('x = 1 if True else print')
        assert_equal(result, [{'col': 19, 'line': 1, 'message': T101}])

    def test_print_assignment_value_or(self):
        result = check_code_for_print_statements('x = print or 1')
        assert_equal(result, [{'col': 4, 'line': 1, 'message': T101}])
        result = check_code_for_print_statements('x = 1 or print')
        assert_equal(result, [{'col': 9, 'line': 1, 'message': T101}])

    def test_print_in_lambda(self):
        result = check_code_for_print_statements('x = lambda a: print')
        assert_equal(result, [{'col': 14, 'line': 1, 'message': T101}])
