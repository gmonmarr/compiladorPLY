import unittest

import cuadruplos as q


class QuadrupleStructureTests(unittest.TestCase):
    def setUp(self):
        q.limpiar()
        self.addCleanup(q.limpiar)

    def test_operand_stack_keeps_types_in_lifo_order(self):
        q.push_operando("left", "int")
        q.push_operando(2.5, "float")

        self.assertEqual(q.top_operando(), 2.5)
        self.assertEqual(q.pop_operando(), (2.5, "float"))
        self.assertEqual(q.pop_operando(), ("left", "int"))
        self.assertEqual(q.pila_tipo, [])

    def test_pop_from_empty_stack_fails(self):
        with self.assertRaisesRegex(Exception, "No hay operandos"):
            q.pop_operando()
        with self.assertRaisesRegex(Exception, "No hay operadores"):
            q.pop_operador()

    def test_quadruple_list_preserves_insertion_order(self):
        self.assertEqual(q.push_cuadruplo("+", 1, 2, "t1"), 0)
        self.assertEqual(q.push_cuadruplo("=", "t1", None, "x"), 1)
        self.assertEqual(q.cuadruplos, [("+", 1, 2, "t1"), ("=", "t1", None, "x")])


if __name__ == "__main__":
    unittest.main()
