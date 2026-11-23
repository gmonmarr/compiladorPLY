"""Asignación de direcciones virtuales por segmento y tipo."""

TIPOS = ('int', 'float', 'string', 'bool') # tipos de datos permitidos
BASES = {'global': 1000, 'local': 5000, 'temporal': 9000, 'constante': 13000} # 
BLOQUE = 1000 # se reservan 1000 direcciones por TIPO y por SEGMENTO
contadores = {}
constantes = {}  # (tipo, valor) -> dirección


def limpiar():
    contadores.clear()
    constantes.clear()


def reservar(segmento, tipo):
    indice = TIPOS.index(tipo)
    llave = (segmento, tipo)
    usados = contadores.get(llave, 0)
    if usados == BLOQUE:
        raise Exception(f"Memoria virtual agotada para {segmento} {tipo}")
    direccion = BASES[segmento] + indice * BLOQUE + usados
    contadores[llave] = usados + 1
    return direccion


def constante(valor, tipo):
    llave = (tipo, valor)
    if llave not in constantes:
        constantes[llave] = reservar('constante', tipo)
    return constantes[llave]


def iniciar_memoria():
    # Cada activación usa los mismos rangos locales y temporales.
    for segmento in ('local', 'temporal'):
        for tipo in TIPOS:
            contadores[(segmento, tipo)] = 0


def espacio(segmento):
    return {tipo: contadores.get((segmento, tipo), 0) for tipo in TIPOS}
