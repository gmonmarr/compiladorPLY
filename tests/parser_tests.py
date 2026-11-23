import unittest
from contextlib import redirect_stdout
from io import StringIO

import ply.lex as lex
import cuadruplos as q
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
            try:
                grammar.parser.parse(source, lexer=scanner)
            except SyntaxError:
                pass

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
        source = "program demo; void foo()[] {}; main { foo(); } end"

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

        self.assertEqual(semantic.tabla_temporales, {9000: "int", 9001: "int"})

    def test_emits_arithmetic_quadruples_in_precedence_order(self):
        self.parse_source("program demo; var x: int; main { x = 1 + 2 * 3; } end")

        self.assertEqual(q.cuadruplos, [
            ("GOTO", None, None, 1),
            ("*", 13001, 13002, 9000),
            ("+", 13000, 9000, 9001),
            ("=", 9001, None, 1000),
            ("END", None, None, None),
        ])

    def test_emits_parenthesized_and_left_associative_operations(self):
        self.parse_source("program demo; main { print(8 * (4 + 2) / 3); } end")

        self.assertEqual(q.cuadruplos, [
            ("GOTO", None, None, 1),
            ("+", 13001, 13002, 9000),
            ("*", 13000, 9000, 9001),
            ("/", 9001, 13003, 9002),
            ("PRINT", 9002, None, None),
            ("END", None, None, None),
        ])
        self.assertEqual(q.pila_operadores, [])
        self.assertEqual(q.pila_operandos, [])

    def test_emits_relational_quadruples(self):
        for operador in ("<", ">", "!="):
            with self.subTest(operador=operador):
                self.parse_source(f"program demo; main {{ print(1 {operador} 2); }} end")

                self.assertEqual(q.cuadruplos, [
                    ("GOTO", None, None, 1),
                    (operador, 13000, 13001, 12000),
                    ("PRINT", 12000, None, None),
                    ("END", None, None, None),
                ])
                self.assertEqual(semantic.get_temp_type(12000), "bool")

    def test_emits_linear_statement_quadruples(self):
        self.parse_source(
            'program demo; var x: int; main { read(x); x = 4; print(x, "done"); } end'
        )

        self.assertEqual(q.cuadruplos, [
            ("GOTO", None, None, 1),
            ("READ", 1000, None, None),
            ("=", 13000, None, 1000),
            ("PRINT", 1000, None, None),
            ("PRINT", 15000, None, None),
            ("END", None, None, None),
        ])

    def test_emits_unary_negation_as_multiplication(self):
        self.parse_source("program demo; var x: int; main { x = -3; } end")

        self.assertEqual(q.cuadruplos, [
            ("GOTO", None, None, 1),
            ("*", 13000, 13001, 9000),
            ("=", 9000, None, 1000),
            ("END", None, None, None),
        ])

    def test_resets_quadruples_and_temporaries_between_programs(self):
        self.parse_source("program first; main { print(1 + 2); } end")
        self.parse_source("program second; main { print(3 + 4); } end")

        self.assertEqual(q.cuadruplos, [
            ("GOTO", None, None, 1),
            ("+", 13000, 13001, 9000),
            ("PRINT", 9000, None, None),
            ("END", None, None, None),
        ])
        self.assertEqual(semantic.tabla_temporales, {9000: "int"})

    def test_rejects_incompatible_arithmetic_types(self):
        with self.assertRaisesRegex(Exception, "operación inválida"):
            self.parse_source('program demo; main { print("hello" + 1); } end')

        self.assertEqual(q.cuadruplos, [("GOTO", None, None, 1)])


if __name__ == "__main__":
    unittest.main()
