from textwrap import dedent

from nose.tools import assert_equal

import unittest

from .lib import (
    check_code_for_print_statements, run_if_print_function,
    run_if_print_statement, T001, T003, T101)


@run_if_print_function
class TestGenericCasesWithPrintFn(unittest.TestCase):
    def test_catches_multiline_print(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b")
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    def test_catches_empty_print_expression(self):
        # TODO: This depends on __future__.print_function
        # as it can be either a print statement or unused function reference.
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


@run_if_print_statement
class TestGenericCasesWithoutPrintFn(unittest.TestCase):
    def test_catches_multiline_print(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b")
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_simple_print_python2(self):
        result = check_code_for_print_statements('print 4')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_empty_print_statement(self):
        result = check_code_for_print_statements('print')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_print_multiline(self):
        result = check_code_for_print_statements('print(0\n)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_catches_empty_print(self):
        result = check_code_for_print_statements('print(\n)')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])
