import unittest
from contextlib import redirect_stdout
from io import StringIO

import ply.lex as lex
import lexer as lexer_rules
import parser as grammar
import semantic


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

    def parse_source(self, source):
        scanner = lex.lex(module=lexer_rules)
        scanner.lineno = 1
        return grammar.parser.parse(source, lexer=scanner)

    def test_accepts_minimal_program(self):
        source = "program demo; main {} end"

        messages = self.parse_and_capture_messages(source)

        self.assertNotIn("Error de sintaxis", messages)

    def test_accepts_assignment(self):
        source = "program demo; var x: int; main { x = 1; } end"

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

    def test_records_global_variables(self):
        self.parse_source("program demo; var x, y: int; z: float; main {} end")

        self.assertEqual(semantic.tabla_simbolos, {"x": "int", "y": "int", "z": "float"})

    def test_rejects_duplicate_global_variable(self):
        with self.assertRaisesRegex(Exception, "ya declarada"):
            self.parse_source("program demo; var x: int; x: float; main {} end")

    def test_rejects_undeclared_variable_use(self):
        with self.assertRaisesRegex(Exception, "no declarada"):
            self.parse_source("program demo; main { x = 1; } end")

    def test_rejects_incompatible_assignment(self):
        with self.assertRaisesRegex(Exception, "no se puede asignar"):
            self.parse_source("program demo; var x: int; main { x = 1.5; } end")

    def test_accepts_numeric_promotion_in_assignment(self):
        self.parse_source("program demo; var x: float; main { x = 1; } end")

    def test_accepts_string_variable_assignment_and_print(self):
        source = 'program demo; var message: string; main { message = "hello"; print(message); } end'
        self.parse_source(source)

        self.assertEqual(semantic.get_var_type("message"), "string")

    def test_registers_function_parameters_and_local_variables(self):
        source = (
            "program demo; var shared: int; "
            "float calc(amount: float)[var local: int;] "
            "{ local = shared; return amount; }; main {} end"
        )
        self.parse_source(source)

        self.assertEqual(semantic.get_function_return_type("calc"), "float")
        self.assertEqual(semantic.get_function_parameters("calc"), [("amount", "float")])
        self.assertEqual(
            semantic.directorio_funciones["calc"]["variables"],
            {"amount": "float", "local": "int"},
        )

    def test_rejects_duplicate_parameter_and_local_name(self):
        source = (
            "program demo; int calc(value: int)[var value: float;] "
            "{ return value; }; main {} end"
        )
        with self.assertRaisesRegex(Exception, "ya declarada"):
            self.parse_source(source)

    def test_rejects_return_type_mismatch(self):
        source = "program demo; float calc()[var value: int;] { return value; }; main {} end"
        with self.assertRaisesRegex(Exception, "debe retornar float"):
            self.parse_source(source)

    def test_tracks_temporary_types_for_arithmetic(self):
        self.parse_source("program demo; var x: int; main { x = 1 + 2 * 3; } end")

        self.assertEqual(semantic.tabla_temporales, {"t1": "int", "t2": "int"})


if __name__ == "__main__":
    unittest.main()
