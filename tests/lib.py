import os
import sys
import unittest

from flake8 import checker
from flake8.plugins import manager
from flake8.style_guide import StyleGuide
import mock

from flake8_print import PrintStatementChecker

SHOULD_ADD_FUTURE_PRINT = os.environ.get('FUTURE_PRINT') == '1'
HAS_PRINT_FN = SHOULD_ADD_FUTURE_PRINT or sys.version_info[0] >= 3

T001 = u'T001 print statement found.'
T003 = u'T003 print function found.'
T101 = u'T101 Python 2.x reserved word print used.'


def run_if_print_function(fn):
    return unittest.skipIf(
        not HAS_PRINT_FN,
        'Skipping py2 w/o __future__: no print function')(fn)


def run_if_print_statement(fn):
    return unittest.skipIf(
        HAS_PRINT_FN,
        'Skipping py3 and py2 w/ __future__: no print statement')(fn)


class SimpleFileChecker(checker.FileChecker):
    @staticmethod
    def get_checks():
        # Mock an entry point returning the plugin target
        entry_point = mock.Mock(spec=['require', 'resolve', 'load'])
        entry_point.name = PrintStatementChecker.name
        entry_point.resolve.return_value = PrintStatementChecker

        # Load the checker plugins using the entry point mock
        with mock.patch('pkg_resources.iter_entry_points',
                        return_value=[entry_point]):
            return manager.Checkers()

    def __init__(self, code, line_offset):
        lines = [line + '\n' for line in code.split('\n')]
        with mock.patch('flake8.processor.FileProcessor.read_lines',
                        return_value=lines):
            super(SimpleFileChecker, self).__init__(
                filename='-',
                checks=SimpleFileChecker.get_checks().to_dictionary(),
                options=mock.MagicMock())

        options = mock.MagicMock()
        options.select = ['T']
        options.disable_noqa = False

        self.__guide = StyleGuide(
            options=options,
            listener_trie=mock.MagicMock(),
            formatter=mock.MagicMock())
        self.__simple_results = []
        self.__line_offset = line_offset
        self.__lines = lines

    def report(self, error_code, line_number, column, text, line=None):
        if error_code is None:
            error_code, text = text.split(' ', 1)

        with mock.patch('linecache.getline') as mock_get_line:
            mock_get_line.return_value = self.__lines[line_number - 1]
            was_handled = self.__guide.handle_error(
                code=error_code,
                filename='-',
                line_number=line_number,
                column_number=column,
                text=text,
                physical_line=line)
            mock_get_line.assert_called_once()

        if not was_handled:
            return

        self.__simple_results.append({
            'col': column,
            'line': line_number + self.__line_offset,
            'message': u'{0} {1}'.format(error_code, text),
        })

    def get_simple_results(self):
        return self.__simple_results


def check_code_for_print_statements(code):
    if SHOULD_ADD_FUTURE_PRINT:
        code = 'from __future__ import print_function\n' + code

    line_offset = -1 if SHOULD_ADD_FUTURE_PRINT else 0

    file_checker = SimpleFileChecker(code, line_offset)
    file_checker.run_ast_checks()
    return file_checker.get_simple_results()
