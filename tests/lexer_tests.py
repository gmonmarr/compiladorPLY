import unittest
from contextlib import redirect_stdout
from io import StringIO

import ply.lex as lex
import lexer as lexer_rules


class LexerTests(unittest.TestCase):
    def tokenize(self, source):
        # Build a fresh scanner for each test.
        scanner = lex.lex(module=lexer_rules)
        scanner.lineno = 1
        scanner.input(source)

        # Keep both the token type and value so tests check the result precisely.
        return [(token.type, token.value) for token in scanner]

    def test_identifiers(self):
        actual = self.tokenize("alpha beta_2")

        self.assertEqual(
            actual,
            [
                ("ID", "alpha"),
                ("ID", "beta_2"),
            ],
        )

    def test_reserved_words(self):
        actual = self.tokenize("while if int float return")

        self.assertEqual(
            actual,
            [
                ("WHILE", "while"),
                ("IF", "if"),
                ("INT", "int"),
                ("FLOAT", "float"),
                ("RETURN", "return"),
            ],
        )

    def test_integer_and_float_constants(self):
        actual = self.tokenize("12 3.5")

        self.assertEqual(
            actual,
            [
                ("CTE_INT", 12),
                ("CTE_FLOAT", 3.5),
            ],
        )

    def test_string_constant(self):
        actual = self.tokenize('"hello"')

        # The current lexer keeps the quote marks in the token value.
        self.assertEqual(actual, [("CTE_STRING", '"hello"')])

    def test_inequality_and_single_character_literals(self):
        actual = self.tokenize("!= - , ; : ( ) { } [ ] * / + = < >")

        # Literal characters are returned using the character as both type and value.
        self.assertEqual(
            actual,
            [
                ("NEQ", "!="),
            ] + [(char, char) for char in "-,;:(){}[]*/+=<>"]
        )

    def test_newline_updates_token_line_number(self):
        scanner = lex.lex(module=lexer_rules)
        scanner.lineno = 1
        scanner.input("first\nsecond\n\nth_ird\n_fourth")

        output = StringIO()
        actual = []

        with redirect_stdout(output):
            for token in scanner:
                actual.append((token.type, token.value, token.lineno))

        self.assertEqual(
            actual,
            [
                ("ID", "first", 1),
                ("ID", "second", 2),
                ("ID", "th_ird", 4),
                ("ID", "fourth", 5),
            ],
        )
        self.assertIn(
            "Caracter no reconocido: '_' en la línea 5",
            output.getvalue(),
        )

    def test_invalid_character_is_reported_and_skipped(self):
        output = StringIO()

        with redirect_stdout(output):
            actual = self.tokenize("left @ right")

        self.assertEqual(
            actual,
            [
                ("ID", "left"),
                ("ID", "right"),
            ],
        )
        self.assertIn("Caracter no reconocido", output.getvalue())


if __name__ == "__main__":
    unittest.main()