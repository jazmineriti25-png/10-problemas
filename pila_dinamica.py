"""
Pila dinámica y evaluación de expresiones aritméticas.

- PilaDinamica: pila implementada con nodos enlazados (memoria dinámica).
- infija_a_posfija: algoritmo de patio de maniobras (Shunting-Yard) con la pila.
- evaluar_posfija: evaluación de la expresión posfija con la pila.
- insercion / busqueda_binaria: ordenamiento y búsqueda sobre los resultados.
"""

import re


# ---------------------------------------------------------------------------
# 1. Estructura de datos: pila dinámica (lista enlazada simple)
# ---------------------------------------------------------------------------
class Nodo:
    def __init__(self, dato, siguiente=None):
        self.dato = dato
        self.siguiente = siguiente


class PilaDinamica:
    """Pila LIFO. Todas las operaciones principales son O(1)."""

    def __init__(self):
        self._cima = None
        self._tamano = 0

    def esta_vacia(self):
        return self._cima is None

    def push(self, dato):
        self._cima = Nodo(dato, self._cima)
        self._tamano += 1

    def pop(self):
        if self.esta_vacia():
            raise IndexError("Pila vacía: no se puede hacer pop")
        dato = self._cima.dato
        self._cima = self._cima.siguiente
        self._tamano -= 1
        return dato

    def peek(self):
        if self.esta_vacia():
            raise IndexError("Pila vacía: no hay cima")
        return self._cima.dato

    def tamano(self):
        return self._tamano


# ---------------------------------------------------------------------------
# 2. Conversión de infija a posfija
# ---------------------------------------------------------------------------
PRECEDENCIA = {"+": 1, "-": 1, "*": 2, "/": 2, "u": 3, "^": 4}  # 'u' = menos unario
ASOC_DERECHA = {"^", "u"}
TOKEN_RE = re.compile(r"\s*(\d+\.?\d*|[+\-*/^()])")


def tokenizar(expresion):
    tokens, pos = [], 0
    expresion = expresion.strip()
    while pos < len(expresion):
        while pos < len(expresion) and expresion[pos].isspace():
            pos += 1
        if pos >= len(expresion):
            break
        m = TOKEN_RE.match(expresion, pos)
        if not m:
            raise ValueError(f"Carácter inválido en la posición {pos}: '{expresion[pos]}'")
        tokens.append(m.group(1))
        pos = m.end()
    return tokens


def infija_a_posfija(expresion):
    salida = []
    pila = PilaDinamica()
    anterior = None  # token previo, para detectar el menos unario

    for tok in tokenizar(expresion):
        if re.fullmatch(r"\d+\.?\d*", tok):
            salida.append(tok)
        elif tok == "(":
            pila.push(tok)
        elif tok == ")":
            while not pila.esta_vacia() and pila.peek() != "(":
                salida.append(pila.pop())
            if pila.esta_vacia():
                raise ValueError("Paréntesis de cierre sin apertura")
            pila.pop()  # descarta '('
        else:
            if tok == "-" and (anterior is None or anterior in "+-*/^("):
                tok = "u"  # menos unario: operador prefijo, no desapila nada
                pila.push(tok)
            else:
                while (not pila.esta_vacia() and pila.peek() != "("
                       and (PRECEDENCIA[pila.peek()] > PRECEDENCIA[tok]
                            or (PRECEDENCIA[pila.peek()] == PRECEDENCIA[tok]
                                and tok not in ASOC_DERECHA))):
                    salida.append(pila.pop())
                pila.push(tok)
        anterior = tok if tok != "u" else "-"

    while not pila.esta_vacia():
        op = pila.pop()
        if op == "(":
            raise ValueError("Paréntesis de apertura sin cierre")
        salida.append(op)
    return salida


# ---------------------------------------------------------------------------
# 3. Evaluación de la expresión posfija
# ---------------------------------------------------------------------------
def evaluar_posfija(tokens):
    pila = PilaDinamica()
    for tok in tokens:
        if tok == "u":
            pila.push(-pila.pop())
        elif tok in "+-*/^":
            if pila.tamano() < 2:
                raise ValueError("Expresión mal formada")
            b, a = pila.pop(), pila.pop()
            if tok == "+":
                pila.push(a + b)
            elif tok == "-":
                pila.push(a - b)
            elif tok == "*":
                pila.push(a * b)
            elif tok == "/":
                if b == 0:
                    raise ZeroDivisionError("División entre cero")
                pila.push(a / b)
            else:
                pila.push(a ** b)
        else:
            pila.push(float(tok))
    if pila.tamano() != 1:
        raise ValueError("Expresión mal formada")
    return pila.pop()


def evaluar(expresion):
    return evaluar_posfija(infija_a_posfija(expresion))


# ---------------------------------------------------------------------------
# 4. Ordenamiento y búsqueda sobre los resultados
# ---------------------------------------------------------------------------
def insercion(lista):
    """Ordenamiento por inserción: O(n^2) peor caso, O(n) mejor caso."""
    a = list(lista)
    for i in range(1, len(a)):
        clave, j = a[i], i - 1
        while j >= 0 and a[j] > clave:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = clave
    return a


def busqueda_binaria(lista_ordenada, objetivo):
    """Búsqueda binaria: O(log n). Devuelve el índice o -1."""
    bajo, alto = 0, len(lista_ordenada) - 1
    while bajo <= alto:
        medio = (bajo + alto) // 2
        if lista_ordenada[medio] == objetivo:
            return medio
        if lista_ordenada[medio] < objetivo:
            bajo = medio + 1
        else:
            alto = medio - 1
    return -1


def fmt(x):
    return str(int(x)) if x == int(x) else str(round(x, 4))


# ---------------------------------------------------------------------------
# 5. Los 10 problemas y casos de error
# ---------------------------------------------------------------------------
PROBLEMAS = [
    "3 + 4 * 2",
    "(3 + 4) * 2",
    "10 / 4 - 1",
    "2 ^ 3 ^ 2",
    "(8 - 3) * (2 + 6) / 4",
    "15 / (7 - (1 + 1)) * 3 - 2",
    "-3 + 5 * -2",
    "2 * (3 + 4) ^ 2 - 10",
    "100 / 5 / 2 + 3 * 4",
    "((2 + 3) * (4 - 1)) ^ 2 / 5",
]

CASOS_ERROR = ["(3 + 4", "3 + 4)", "8 / (4 - 4)", "3 + * 4", "2 $ 3"]


def main():
    print("=== 10 problemas de evaluación de expresiones ===")
    resultados = []
    for i, expr in enumerate(PROBLEMAS, 1):
        posfija = infija_a_posfija(expr)
        valor = evaluar_posfija(posfija)
        resultados.append(valor)
        print(f"{i:>2}. {expr:<30} posfija: {' '.join(posfija):<28} = {fmt(valor)}")

    print("\n=== Casos de error ===")
    for expr in CASOS_ERROR:
        try:
            evaluar(expr)
            print(f"{expr!r}: sin error (inesperado)")
        except (ValueError, ZeroDivisionError, IndexError) as e:
            print(f"{expr!r:<16} -> {type(e).__name__}: {e}")

    print("\n=== Ordenamiento y búsqueda de resultados ===")
    ordenados = insercion(resultados)
    print("Resultados ordenados:", [fmt(x) for x in ordenados])
    for objetivo in (45, 7, 99):
        idx = busqueda_binaria(ordenados, objetivo)
        print(f"Buscar {objetivo}: {'índice ' + str(idx) if idx >= 0 else 'no encontrado'}")


if __name__ == "__main__":
    main()
