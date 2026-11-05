import unittest
from contextlib import redirect_stdout
from io import StringIO

import ply.lex as lex
import lexer as lexer_rules
import parser as grammar


class ParserTests(unittest.TestCase):
    def parse_and_capture_messages(self, source):
        # parser.py doesn't create a lexer object for imported use,
        # so build one here and pass it to parse().
        scanner = lex.lex(module=lexer_rules)
        scanner.lineno = 1

        output = StringIO()
        with redirect_stdout(output):
            grammar.parser.parse(source, lexer=scanner)

        return output.getvalue()

    def test_accepts_minimal_program(self):
        source = "program demo; main {} end"

        messages = self.parse_and_capture_messages(source)

        self.assertNotIn("Error de sintaxis", messages)

    def test_accepts_assignment(self):
        source = "program demo; main { x = 1; } end"

        messages = self.parse_and_capture_messages(source)

        self.assertNotIn("Error de sintaxis", messages)

    def test_accepts_print_statement(self):
        source = 'program demo; main { print("hello"); } end'

        messages = self.parse_and_capture_messages(source)

        self.assertNotIn("Error de sintaxis", messages)

    def test_accepts_zero_argument_function_call_statement(self):
        source = "program demo; main { foo(); } end"

        messages = self.parse_and_capture_messages(source)

        self.assertNotIn("Error de sintaxis", messages)

    def test_reports_missing_assignment_semicolon(self):
        source = "program demo; main { x = 1 } end"

        messages = self.parse_and_capture_messages(source)

        self.assertIn("Error de sintaxis", messages)

    def test_reports_missing_program_end(self):
        source = "program demo; main {}"

        messages = self.parse_and_capture_messages(source)

        self.assertIn("Error de sintaxis", messages)


if __name__ == "__main__":
    unittest.main()