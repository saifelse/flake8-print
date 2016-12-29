from textwrap import dedent

from nose.tools import assert_equal

import unittest

from .lib import (
    check_code_for_print_statements, run_if_print_function,
    run_if_print_statement, T001, T003)


@run_if_print_function
class TestNoQAWithPrintFunction(unittest.TestCase):
    def test_skips_noqa(self):
        result = check_code_for_print_statements('print(4) # noqa')
        assert_equal(result, list())

    def test_doesnt_skip_noqa_line_if_multiline_end(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b")  # noqa
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    def test_doesnt_skip_noqa_line_if_multiline_middle(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b"  # noqa
                  "c")
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T003}])

    def test_skips_noqa_line_if_multiline_start(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"  # noqa
                  "b")
        """))
        assert_equal(result, list())

    def test_skips_noqa_line_only(self):
        result = check_code_for_print_statements(dedent("""\
            print(4); # noqa
            print(5)
            # noqa
        """))
        assert_equal(result, [{'col': 0, 'line': 2, 'message': T003}])


@run_if_print_statement
class TestNoQAWithPrintStatement(unittest.TestCase):
    def test_skips_noqa(self):
        result = check_code_for_print_statements('print(4) # noqa')
        assert_equal(result, list())

    def test_doesnt_skip_noqa_line_if_multiline_end(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b")  # noqa
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_doesnt_skip_noqa_line_if_multiline_middle(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"
                  "b"  # noqa
                  "c")
        """))
        assert_equal(result, [{'col': 0, 'line': 1, 'message': T001}])

    def test_skips_noqa_line_if_multiline_start(self):
        result = check_code_for_print_statements(dedent("""\
            print("a"  # noqa
                  "b")
        """))
        assert_equal(result, list())

    def test_skips_noqa_line_only(self):
        result = check_code_for_print_statements(dedent("""\
            print(4); # noqa
            print(5)
            # noqa
        """))
        assert_equal(result, [{'col': 0, 'line': 2, 'message': T001}])
