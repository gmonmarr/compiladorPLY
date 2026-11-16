# cuadruplos.py
import semantic

# queue (Fila) (FIFO)
cuadruplos = []

# Pilas (LIFO)
pila_operadores = []
pila_operandos = [] # operandos son tuplas (valor, tipo)
# pila_tipo = []

temp_cnt = 0

def limpiar():
    global temp_cnt
    cuadruplos.clear()
    pila_operadores.clear()
    pila_operandos.clear()
    temp_cnt = 0

def nuevo_temp():
    from semantic import directorio_funciones, funcion_actual, tabla_simbolos

    global temp_cnt
    locales = directorio_funciones.get(funcion_actual, {}).get('variables', {})
    while True:
        temp_cnt += 1
        nombre = f"t{temp_cnt}"
        if nombre not in tabla_simbolos and nombre not in locales:
            return nombre

# push de cuádruplo
def push_cuadruplo(operador, operando1, operando2, resultado):
    cuadruplo = (operador, operando1, operando2, resultado)
    cuadruplos.append(cuadruplo)
    return len(cuadruplos)-1 # retornar index

### OPERANDOS
# push operando (poner al final)
def push_operando(operando, tipo):
    pila_operandos.append(operando, tipo)

# pop operando (sacar el último)
def pop_operando():
    if not pila_operandos:
        raise Exception("Error: No hay operandos en la pila")
    return pila_operandos.pop()

# top operando (ver el último)
def top_operando():
    if not pila_operandos:
        raise Exception("Error: No hay operandos en la pila")
    return pila_operandos[-1]

### OPERADORES
# push operador (poner al final)
def push_operador(operador):
    pila_operadores.append(operador)

# pop operador (sacar el último)
def pop_operador():
    if not pila_operadores:
        raise Exception("Error: No hay operadores en la pila")
    return pila_operadores.pop()

# top operador (ver el último)
def top_operador():
    if not pila_operadores:
        raise Exception("Error: No hay operadores en la pila")
    return pila_operadores[-1]

def resolver_expresion(operadores):
    """
    input: operadores (list of str) - lista de operadores a resolver
    output: None - genera un cuádruplo y lo agrega a la lista de cuadruplos
    """
    from semantic import add_temp, oraculo_cubo

    if not pila_operadores or top_operador() not in operadores:
        return

    operador = pop_operador()
    derecho, tipo_der = pop_operando()
    izquierdo, tipo_izq = pop_operando()
    tipo = oraculo_cubo(tipo_izq, tipo_der, operador)
    temporal = nuevo_temp()
    add_temp(temporal, tipo)
    push_cuadruplo(operador, izquierdo, derecho, temporal)
    push_operando(temporal, tipo)


def imprimir_cuadruplos():
    for indice, cuadruplo in enumerate(cuadruplos):
        print(f"{indice}: {cuadruplo}")
