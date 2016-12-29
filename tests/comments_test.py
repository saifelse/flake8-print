from nose.tools import assert_equal

import unittest

from .lib import (
    check_code_for_print_statements, run_if_print_function, run_if_print_statement, T001, T003)


class TestComments(unittest.TestCase):
    def test_print_in_inline_comment_is_not_a_false_positive(self):
        result = check_code_for_print_statements('# what should I print ?')
        assert_equal(result, list())

    @run_if_print_function
    def test_print_fn_same_line_as_comment(self):
        result = check_code_for_print_statements('print(5) # what should I do with 5 ?')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    @run_if_print_statement
    def test_print_statement_same_line_as_comment(self):
        result = check_code_for_print_statements('print 5 # what should I do with 5 ?')
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])
