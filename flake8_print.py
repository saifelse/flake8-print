"""Extension for flake8 that finds usage of print."""

import ast
import sys

__version__ = '2.1.0'

MAJ_VERSION = sys.version_info[0]
PY2 = MAJ_VERSION == 2
PY3 = MAJ_VERSION == 3


class PrintStatementChecker(object):
    version = __version__
    name = 'flake8-print'

    _PRINT_FN_NAME = 'print'

    _ERRORS = {
        'T001': 'print statement found.',
        'T003': 'print function found.',
        'T101': 'Python 2.x reserved word print used.',
    }

    def __init__(self, tree):
        self.tree = tree

    def _generate_error(self, node, code):
        msg = u'{0} {1}'.format(code, self._ERRORS[code])
        return node.lineno, node.col_offset, msg, type(self)

    def _is_print_name_node(self, node):
        return isinstance(node, ast.Name) and node.id == self._PRINT_FN_NAME

    def run(self):
        print_fn_name_nodes = set()
        print_name_nodes = set()

        for node in ast.walk(self.tree):
            # `print foo, bar`
            if PY2 and isinstance(node, ast.Print):
                yield self._generate_error(node, 'T001')

            # `def print(foo, bar):`
            elif isinstance(node, ast.FunctionDef) and node.name == self._PRINT_FN_NAME:
                yield self._generate_error(node, 'T101')

            # foo(print, print, print=3, print=4, *print, **print)
            elif PY3 and isinstance(node, ast.arguments):
                args = node.args + node.kwonlyargs + [node.vararg, node.kwarg]
                for arg_node in args:
                    if arg_node and arg_node.arg == self._PRINT_FN_NAME:
                        yield self._generate_error(arg_node, 'T101')

            # `print(foo, bar)`
            elif isinstance(node, ast.Call) and self._is_print_name_node(node.func):
                print_fn_name_nodes.add(node.func)
                yield self._generate_error(node.func, 'T003')

            # `1 + print` or `print(foo, bar)`: don't yield, just log, so that
            # we can avoid double counting function calls
            elif isinstance(node, ast.Name) and self._is_print_name_node(node):
                print_name_nodes.add(node)

        # Of the `print` ast.Name nodes, we raise an error if it had not been logged for
        # being used in a print function call.
        for node in print_name_nodes - print_fn_name_nodes:
            yield self._generate_error(node, 'T101')
