from textwrap import dedent
import unittest

from nose.tools import assert_equal

from .lib import (
    check_code_for_print_statements, run_if_print_function,
    run_if_print_statement, T101)


class TestMultilineFalsePositive(unittest.TestCase):
    def test_print_in_one_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('hello="""there is a \nprint on\n the next line"""')
        assert_equal(result, list())

    def test_print_in_three_double_quote_single_line_string_not_false_positive(self):
        result = check_code_for_print_statements('a("""print the things""", 25)')
        assert_equal(result, list())


class TestNameFalsePositive(unittest.TestCase):
    def test_print_in_name(self):
        result = check_code_for_print_statements('def print_foo(): pass')
        assert_equal(result, [])
        result = check_code_for_print_statements('def foo_print(): pass')
        assert_equal(result, [])
        result = check_code_for_print_statements('foo_print = 1')
        assert_equal(result, [])
        result = check_code_for_print_statements('print_foo = 1')
        assert_equal(result, [])


@run_if_print_function
class TestPython3NameFalsePositive(unittest.TestCase):
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
