import unittest

import ply.lex as lex
import lexer
import parser as grammar
import cuadruplos as q
import memoria
import semantic as s


class ControlAndFunctionTests(unittest.TestCase):
    def compilar(self, fuente):
        grammar.parser.parse(fuente, lexer=lex.lex(module=lexer))
        self.assertEqual(q.pila_operadores, [])
        self.assertEqual(q.pila_operandos, [])
        self.assertEqual(q.pila_saltos, [])
        self.assertEqual(q.pila_llamadas, [])
        return q.cuadruplos

    def test_if_patches_false_branch_to_next_quadruple(self):
        resultado = self.compilar(
            "program p; main { if (1 < 2) print(3);; print(4); } end"
        )
        self.assertEqual(resultado, [
            ('GOTO', None, None, 1),
            ('<', 13000, 13001, 12000),
            ('GotoF', 12000, None, 4),
            ('PRINT', 13002, None, None),
            ('PRINT', 13003, None, None),
            ('END', None, None, None),
        ])

    def test_if_else_patches_both_branches(self):
        resultado = self.compilar(
            "program p; main { if (1 < 2) print(3); else print(4);; print(5); } end"
        )
        self.assertEqual(resultado[2], ('GotoF', 12000, None, 5))
        self.assertEqual(resultado[4], ('GOTO', None, None, 6))
        self.assertEqual(resultado[5], ('PRINT', 13003, None, None))
        self.assertEqual(resultado[6], ('PRINT', 13004, None, None))

    def test_while_returns_to_condition_and_patches_exit(self):
        resultado = self.compilar(
            "program p; var x: int; main { x = 0; "
            "while (x < 3) do [x = x + 1;]; print(x); } end"
        )
        self.assertEqual(resultado, [
            ('GOTO', None, None, 1),
            ('=', 13000, None, 1000),
            ('<', 1000, 13001, 12000),
            ('GotoF', 12000, None, 7),
            ('+', 1000, 13002, 9000),
            ('=', 9000, None, 1000),
            ('GOTO', None, None, 2),
            ('PRINT', 1000, None, None),
            ('END', None, None, None),
        ])

    def test_nested_if_inside_loop_keeps_correct_jump_targets(self):
        resultado = self.compilar(
            "program p; var x: int; main { x = 0; while (x < 3) do ["
            "if (x < 1) print(x); else print(2);; x = x + 1;]; } end"
        )
        self.assertEqual(resultado[3], ('GotoF', 12000, None, 12))
        self.assertEqual(resultado[5], ('GotoF', 12001, None, 8))
        self.assertEqual(resultado[7], ('GOTO', None, None, 9))
        self.assertEqual(resultado[11], ('GOTO', None, None, 2))

    def test_conditions_require_bool(self):
        for estatuto in ('if (1) print(2);;', 'while (1) do print(2);;'):
            with self.subTest(estatuto=estatuto):
                with self.assertRaisesRegex(Exception, 'condición debe ser bool'):
                    self.compilar(f"program p; main {{ {estatuto} }} end")

    def test_void_function_parameters_workspace_and_call(self):
        resultado = self.compilar(
            "program p; void show(value: int)[var copy: int;] "
            "{ copy = value + 1; print(copy); }; main { show(7); } end"
        )
        funcion = s.directorio_funciones['show']
        self.assertEqual(funcion['inicio'], 1)
        self.assertEqual(funcion['num_parametros'], 1)
        self.assertEqual(funcion['num_locales'], 1)
        self.assertEqual(funcion['num_temporales'], 1)
        self.assertEqual(funcion['direcciones'], {'value': 5000, 'copy': 5001})
        self.assertEqual(resultado[0], ('GOTO', None, None, 5))
        self.assertEqual(resultado[4], ('ENDFUNC', None, None, None))
        self.assertEqual(resultado[5], ('ERA', 'show', None, funcion['espacio']))
        self.assertEqual(resultado[6], ('PARAMETER', 13001, None, 1))
        self.assertEqual(resultado[7], ('GOSUB', 'show', None, 1))
        self.assertEqual(funcion['espacio']['locales']['int'], 2)

    def test_nested_typed_calls_preserve_outer_arguments(self):
        resultado = self.compilar(
            "program p; int inc(x: int)[] { return x + 1; }; "
            "int sum(a: int, b: int)[] { return a + b; }; "
            "main { print(sum(inc(2), inc(3))); } end"
        )
        self.assertEqual([q[1] for q in resultado if q[0] == 'ERA'], ['sum', 'inc', 'inc'])
        self.assertEqual([q[1] for q in resultado if q[0] == 'GOSUB'], ['inc', 'inc', 'sum'])
        self.assertEqual(
            [q[3] for q in resultado if q[0] == 'PARAMETER'], [1, 1, 1, 2]
        )
        self.assertEqual(resultado[-2], ('PRINT', 9002, None, None))

    def test_recursive_era_is_completed_after_function_body(self):
        resultado = self.compilar(
            "program p; int fact(n: int)[] { "
            "if (n < 2) return 1; else return n * fact(n - 1);; "
            "}; main { print(fact(4)); } end"
        )
        funcion = s.directorio_funciones['fact']
        self.assertEqual(funcion['num_temporales'], 4)
        for operador, nombre, _, espacio in resultado:
            if operador == 'ERA':
                self.assertEqual(nombre, 'fact')
                self.assertEqual(espacio, funcion['espacio'])
        retornos = [q for q in resultado if q[0] == 'RETURN']
        self.assertEqual(len(retornos), 2)
        self.assertTrue(all(q[3] == funcion['retorno'] for q in retornos))

    def test_rejects_invalid_calls(self):
        casos = [
            ("missing();", "no declarada"),
            ("f();", "número de argumentos"),
            ("f(1, 2);", "número de argumentos"),
            ("f(1.5);", "tipo de argumento"),
            ("print(f(1));", "void no produce"),
        ]
        for llamada, mensaje in casos:
            with self.subTest(llamada=llamada):
                with self.assertRaisesRegex(Exception, mensaje):
                    self.compilar(
                        f"program p; void f(x: int)[] {{}}; main {{ {llamada} }} end"
                    )

    def test_scope_addresses_reuse_local_space_without_hiding_globals(self):
        resultado = self.compilar(
            "program p; var x: int; void f(x: int)[] { print(x); }; "
            "void g(y: int)[] { print(x, y); }; main { x = 3; f(x); } end"
        )
        self.assertEqual(s.direcciones_globales['x'], 1000)
        self.assertEqual(s.directorio_funciones['f']['direcciones']['x'], 5000)
        self.assertEqual(s.directorio_funciones['g']['direcciones']['y'], 5000)
        self.assertEqual(resultado[1:5], [
            ('PRINT', 5000, None, None),
            ('ENDFUNC', None, None, None),
            ('PRINT', 1000, None, None),
            ('PRINT', 5000, None, None),
        ])

    def test_constants_are_deduplicated_and_separated_by_type(self):
        self.compilar('program p; main { print(1, 1, 1.0, "1"); } end')
        self.assertEqual(memoria.constantes, {
            ('int', 1): 13000, ('float', 1.0): 14000, ('string', '"1"'): 15000,
        })

    def test_virtual_address_overflow(self):
        memoria.limpiar()
        self.addCleanup(memoria.limpiar)
        for _ in range(memoria.BLOQUE):
            memoria.reservar('local', 'int')
        with self.assertRaisesRegex(Exception, 'Memoria virtual agotada'):
            memoria.reservar('local', 'int')


if __name__ == '__main__':
    unittest.main()
