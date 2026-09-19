"""
Numa · lógica criptográfica
---------------------------
Todas las operaciones de la calculadora, sin nada de interfaz: Este módulo
no importa streamlit, no imprime y no pide datos. Cada operación devuelve
un `Resultado` listo para que app.py lo muestre.

Secciones, en este orden:
  1. Utilidades de texto
  2. Matemática modular      (fase 2)
  3. Criptografía clásica    (fase 3)
  4. Criptografía moderna    (fase 4)
  5. Hash                    (fase 5)
  6. Codificación            (fase 5)
  7. Salt                    (fase 5)
"""

import base64
import hashlib
import re
import secrets
import unicodedata
from dataclasses import dataclass, field


@dataclass
class Resultado:
    """Lo que devuelve cada operación de la calculadora.

    app.py muestra `valor` en grande en la tarjeta de resultado, `pasos` en el
    expander de procedimiento, `tabla` con st.dataframe cuando existe,
    `verificacion` en menta con ✓ y `datos` alimenta los chips con valores clave.
    """

    valor: str                          # resultado final, listo para mostrar
    pasos: list[str]                    # procedimiento; cada paso empieza con **Título.**
    tabla: list[dict] | None = None     # filas para st.dataframe (AEE, exp. rápida, salts...)
    verificacion: str | None = None     # comprobación, p. ej. "7 × 15 = 105 ≡ 1 (mod 26)"
    datos: dict = field(default_factory=dict)  # valores extra (n, phi, d, A, B...)

    def __post_init__(self):
        # Estilo de la casa: después de dos puntos va mayúscula (salvo variables)
        self.pasos = [mayuscula_tras_dos_puntos(paso) for paso in self.pasos]
        if self.verificacion:
            self.verificacion = mayuscula_tras_dos_puntos(self.verificacion)
        for clave in ("etiqueta", "nota_tabla", "aviso", "mensaje"):
            if isinstance(self.datos.get(clave), str):
                self.datos[clave] = mayuscula_tras_dos_puntos(self.datos[clave])
        if isinstance(self.datos.get("chips"), list):
            self.datos["chips"] = [mayuscula_tras_dos_puntos(str(chip)) for chip in self.datos["chips"]]
        if isinstance(self.datos.get("tabla_extra"), dict):
            for clave in ("titulo", "nota"):
                if isinstance(self.datos["tabla_extra"].get(clave), str):
                    self.datos["tabla_extra"][clave] = mayuscula_tras_dos_puntos(self.datos["tabla_extra"][clave])


# ======================================================================
# Utilidades de texto
# ======================================================================

# Tras dos puntos, una palabra de dos o más letras que no sea una variable
# (las variables son una letra o van seguidas de un operador o paréntesis)
_TRAS_DOS_PUNTOS = re.compile(
    r"(: |:\n)([a-záéíóúñü][a-záéíóúñü]+)\b(?!\s*[=×+−<>≡⊕(])",
)


def mayuscula_tras_dos_puntos(texto: str) -> str:
    """Pone en mayúscula la primera letra después de dos puntos, como en
    «Resultado: El inverso es 15». Respeta las variables y fórmulas:
    «residuo 1: t = −11» y «guarda hash = MD5(...)» quedan igual."""
    return _TRAS_DOS_PUNTOS.sub(lambda m: m.group(1) + m.group(2)[0].upper() + m.group(2)[1:], str(texto))

# Alfabeto español de 27 letras: A=0, B=1, ..., N=13, Ñ=14, O=15, ..., Z=26
ALFABETO = "ABCDEFGHIJKLMNÑOPQRSTUVWXYZ"


def normalizar(texto: str, alfabeto: str = ALFABETO) -> str:
    """Prepara un texto para los cifrados clásicos.

    Pasa a mayúsculas, quita tildes y diéresis (Á→A, Ü→U) conservando la Ñ,
    e ignora todo lo que no esté en el alfabeto (espacios, signos, dígitos).
    Con el alfabeto de 26 letras (César inglés) la Ñ no existe y pierde su
    virgulilla, igual que una tilde: Ñ→N.
    """
    letras = []
    for caracter in texto.upper():
        if caracter == "Ñ" and "Ñ" in alfabeto:
            letras.append(caracter)
            continue
        # NFD separa la letra base de su tilde; nos quedamos con la base
        descompuesto = unicodedata.normalize("NFD", caracter)
        base = "".join(c for c in descompuesto if not unicodedata.combining(c))
        if len(base) == 1 and base in alfabeto:
            letras.append(base)
    return "".join(letras)


def letra_a_numero(letra: str) -> int:
    """Posición de una letra en el alfabeto de 27 (A=0 … Ñ=14 … Z=26)."""
    if len(letra) != 1 or letra not in ALFABETO:
        raise ValueError(
            f"'{letra}' no está en el alfabeto español de 27 letras. "
            "Usa letras de la A a la Z, incluida la Ñ."
        )
    return ALFABETO.index(letra)


def numero_a_letra(numero: int) -> str:
    """Letra que ocupa una posición del alfabeto de 27."""
    if not 0 <= numero <= 26:
        raise ValueError(
            f"El número {numero} no corresponde a ninguna letra: "
            "Debe estar entre 0 y 26."
        )
    return ALFABETO[numero]


def texto_a_numeros(texto: str) -> list[int]:
    """Normaliza un texto y lo convierte en la lista de posiciones de sus letras."""
    return [letra_a_numero(letra) for letra in normalizar(texto)]


def numeros_a_texto(numeros: list[int]) -> str:
    """Convierte una lista de posiciones (0 a 26) en texto."""
    return "".join(numero_a_letra(numero) for numero in numeros)


# ======================================================================
# Matemática modular (fase 2)
# ======================================================================


def _num(numero: int) -> str:
    """Escribe los negativos con el signo menos tipográfico: −11 en vez de -11."""
    return f"−{abs(numero)}" if numero < 0 else str(numero)


def _con_signo(numero: int) -> str:
    """Escribe un número entre paréntesis cuando es negativo, para que las
    fórmulas de los pasos se lean bien: 0 − 3 × (−3) en vez de 0 − 3 × −3."""
    return f"({_num(numero)})" if numero < 0 else str(numero)


def _plural(cantidad: int, singular: str, plural: str) -> str:
    """«1 vez», «3 veces»: El número con la palabra en singular o plural."""
    return f"{cantidad} {singular if cantidad == 1 else plural}"


def _paso(titulo: str, texto: str) -> str:
    """Un paso del procedimiento: Título corto en negrita y la explicación.
    app.py lo muestra con el número en lavanda y el PDF pone el título en negrita."""
    return f"**{titulo}.** {texto}"


def modulo(a: int, n: int) -> Resultado:
    """1.1 · a mod n = b, con la identidad a = q·n + b y 0 ≤ b < n.

    Acepta a negativo: El residuo siempre queda entre 0 y n − 1.
    """
    if n <= 0:
        raise ValueError(
            f"El módulo n debe ser un entero positivo y llegó n = {n}. "
            "Escribe un número mayor o igual que 1."
        )
    b = a % n
    q = a // n  # cociente hacia abajo, para que el residuo nunca sea negativo
    division = f"{_num(a)} entre {n} cabe {_num(q)} veces (ese es el cociente q)."
    if a < 0:
        division += (
            " Como a es negativo, el cociente se toma hacia abajo para que el "
            "residuo no salga negativo."
        )
    pasos = [
        _paso(
            "Qué buscamos",
            f"El residuo de dividir {_num(a)} entre {n}: Lo que sobra, un número b que "
            f"siempre queda entre 0 y {n - 1}. Eso es lo que significa «{_num(a)} mod {n}».",
        ),
        _paso("Dividimos", f"{division} Entonces q × n = {_num(q)} × {n} = {_num(q * n)}."),
        _paso(
            "Calculamos el residuo",
            f"b = a − q × n = {_num(a)} − {_con_signo(q * n)} = {b}.",
        ),
        _paso(
            "Comprobación",
            f"{_num(q)} × {n} + {b} = {_num(a)}, y {b} está entre 0 y {n - 1}, como debe ser.",
        ),
    ]
    return Resultado(
        valor=str(b),
        pasos=pasos,
        verificacion=f"{a} = {q} × {n} + {b}, con 0 ≤ {b} < {n}",
        datos={
            "etiqueta": f"{a} mod {n}",
            "chips": [f"cociente q = {q}", f"residuo b = {b}"],
            "q": q,
            "b": b,
        },
    )


def inverso_aditivo(a: int, n: int) -> Resultado:
    """1.2 · Inverso aditivo: El x que cumple a + x ≡ 0 (mod n), o sea −a mod n."""
    if n <= 0:
        raise ValueError(
            f"El módulo n debe ser un entero positivo y llegó n = {n}. "
            "Escribe un número mayor o igual que 1."
        )
    x = (-a) % n
    if 0 < a < n:
        calculo = f"Como {a} está entre 1 y {n - 1}, basta restarlo de {n}: {n} − {a} = {x}."
    else:
        calculo = f"Llevamos −{_con_signo(a)} al rango 0 a {n - 1} sumando o restando {n} y queda {x}."
    pasos = [
        _paso(
            "Qué buscamos",
            f"Un número x entre 0 y {n - 1} que sumado a {_num(a)} dé un múltiplo de {n}, "
            f"es decir {_num(a)} + x ≡ 0 (mod {n}). Ese x es el inverso aditivo.",
        ),
        _paso("Calculamos", f"x = −a mod n = −{_con_signo(a)} mod {n}. {calculo}"),
        _paso(
            "Comprobación",
            f"{_num(a)} + {x} = {_num(a + x)}, y {_num(a + x)} mod {n} = {(a + x) % n}: "
            f"La suma es un múltiplo de {n}.",
        ),
    ]
    return Resultado(
        valor=str(x),
        pasos=pasos,
        verificacion=f"{a} + {x} = {a + x} ≡ 0 (mod {n})",
        datos={
            "etiqueta": f"Inverso aditivo de {a} módulo {n}",
            "chips": [f"x = {x}", f"suma = {a + x}, múltiplo de {n}"],
            "x": x,
        },
    )


# Bases que acepta el inverso de XOR, con sus dígitos válidos y un consejo
# para el mensaje de error.
BASES_XOR = {"binario": 2, "decimal": 10, "hexadecimal": 16}
_DIGITOS_XOR = {
    "binario": ("01", "Usa solo los dígitos 0 y 1, por ejemplo 1100."),
    "decimal": ("0123456789", "Usa solo dígitos del 0 al 9, sin signo ni puntos."),
    "hexadecimal": ("0123456789ABCDEF", "Usa dígitos del 0 al 9 y letras de la A a la F."),
}


def _texto_a_entero(texto: str, base: str, campo: str) -> tuple[int, str]:
    """Convierte la entrada de un campo (C o K) a entero según la base.

    Devuelve el número y el texto limpio (sin espacios, en mayúsculas),
    que sirve para saber cuántos dígitos escribió la persona.
    """
    limpio = str(texto).replace(" ", "").strip().upper()
    if limpio == "":
        raise ValueError(f"El campo {campo} está vacío. Escribe un número en {base}.")
    validos, consejo = _DIGITOS_XOR[base]
    if any(digito not in validos for digito in limpio):
        raise ValueError(f"'{texto}' no es un número válido en {base}. {consejo}")
    return int(limpio, BASES_XOR[base]), limpio


def inverso_xor(c: str, k: str, base: str = "binario") -> Resultado:
    """1.3 · Inverso de XOR: Dados C y K recupera A = C ⊕ K.

    XOR es su propio inverso: Si C = A ⊕ K, aplicar ⊕ K otra vez devuelve A.
    Las entradas pueden venir en binario, decimal o hexadecimal.
    """
    nombre_base = str(base).strip().lower() if base else ""
    if nombre_base not in BASES_XOR:
        raise ValueError("Elige la base de las entradas: Binario, decimal o hexadecimal.")
    numero_c, limpio_c = _texto_a_entero(c, nombre_base, "C")
    numero_k, limpio_k = _texto_a_entero(k, nombre_base, "K")
    numero_a = numero_c ^ numero_k

    # Ancho en bits para mostrar los tres valores alineados
    if nombre_base == "binario":
        ancho = max(len(limpio_c), len(limpio_k))
    elif nombre_base == "hexadecimal":
        ancho = 4 * max(len(limpio_c), len(limpio_k))
    else:
        ancho = max(numero_c.bit_length(), numero_k.bit_length(), 1)
    digitos_hex = max(1, (ancho + 3) // 4)

    bin_c, bin_k, bin_a = (f"{v:0{ancho}b}" for v in (numero_c, numero_k, numero_a))
    hex_c, hex_k, hex_a = (f"{v:0{digitos_hex}X}" for v in (numero_c, numero_k, numero_a))
    valor = {"binario": bin_a, "decimal": str(numero_a), "hexadecimal": hex_a}[nombre_base]

    alineado = (
        f"  C  {bin_c}\n"
        f"⊕ K  {bin_k}\n"
        f"     {'─' * ancho}\n"
        f"  A  {bin_a}"
    )
    pasos = [
        _paso(
            "Qué buscamos",
            "El mensaje original A. El cifrado fue C = A ⊕ K (XOR con la clave K), y XOR "
            "se deshace aplicándolo otra vez con la misma clave: A = C ⊕ K.",
        ),
        _paso("Pasamos todo a binario", f"Con {ancho} bits: C = {bin_c} y K = {bin_k}."),
        _paso(
            "Aplicamos XOR bit a bit",
            "Comparamos cada bit de C con el bit de K que está en la misma posición: Si "
            f"son distintos el resultado es 1, si son iguales es 0. El primer bit: "
            f"{bin_c[0]} frente a {bin_k[0]} da {bin_a[0]}.",
        ),
        _paso("Resultado", f"A = C ⊕ K = {bin_a}."),
    ]
    if nombre_base != "binario":
        pasos.append(_paso(f"Escrito en {nombre_base}", f"A = {valor}."))
    pasos.append(
        _paso(
            "Comprobación",
            f"A ⊕ K = {bin_a} ⊕ {bin_k} = {bin_c} = C: Aplicar XOR otra vez devuelve el mensaje cifrado.",
        )
    )
    tabla = [
        {"Valor": "C", "Binario": bin_c, "Decimal": numero_c, "Hexadecimal": hex_c},
        {"Valor": "K", "Binario": bin_k, "Decimal": numero_k, "Hexadecimal": hex_k},
        {"Valor": "A = C ⊕ K", "Binario": bin_a, "Decimal": numero_a, "Hexadecimal": hex_a},
    ]
    return Resultado(
        valor=valor,
        pasos=pasos,
        tabla=tabla,
        verificacion=f"A ⊕ K = C: {bin_a} ⊕ {bin_k} = {bin_c}, se recupera C",
        datos={
            "etiqueta": "A = C ⊕ K",
            "chips": [f"{ancho} bits", f"A = {numero_a} en decimal"],
            "alineado": alineado,
            "nota_tabla": "Cada fila muestra el mismo valor en las tres bases; "
            "el XOR se hace sobre la columna de binario.",
            "c": numero_c,
            "k": numero_k,
            "a": numero_a,
        },
    )


def mcd(a: int, b: int) -> int:
    """MCD con el algoritmo de Euclides, implementado a mano.

    Es la pieza que reutilizan el afín (2.6), Diffie-Hellman y RSA (módulo 3).
    """
    while b != 0:
        a, b = b, a % b
    return a


def mcd_euclides(a: int, b: int) -> Resultado:
    """1.4 · MCD paso a paso: Divisiones a = q·b + r hasta que el residuo es 0.

    Además indica si a tiene inverso multiplicativo módulo b (lo tiene
    exactamente cuando el MCD es 1).
    """
    if a <= 0 or b <= 0:
        raise ValueError(
            f"El MCD se calcula con enteros positivos y llegó ({a}, {b}). "
            "Escribe dos números mayores o iguales que 1."
        )
    pasos = [
        _paso(
            "Qué buscamos",
            f"El máximo común divisor de {a} y {b}: El número más grande que divide a los "
            "dos sin dejar residuo. Euclides lo encuentra con divisiones sucesivas.",
        )
    ]
    mayor, menor = a, b
    if mayor < menor:
        mayor, menor = menor, mayor
        pasos.append(_paso("Ordenamos", f"Como {a} < {b}, empezamos dividiendo {b} entre {a}."))

    tabla = []
    while menor != 0:
        cociente, residuo = divmod(mayor, menor)
        tabla.append(
            {
                "Paso": len(tabla) + 1,
                "a": mayor,
                "b": menor,
                "Cociente q": cociente,
                "Residuo r": residuo,
            }
        )
        explicacion = (
            f"{mayor} entre {menor} cabe {_plural(cociente, 'vez', 'veces')} y sobra {residuo}: "
            f"{mayor} = {cociente} × {menor} + {residuo}."
        )
        if residuo == 0:
            explicacion += " El residuo es 0: Aquí paramos."
        else:
            explicacion += f" Ahora dividimos {menor} entre {residuo}."
        pasos.append(_paso(f"División {len(tabla)}", explicacion))
        mayor, menor = menor, residuo

    resultado_mcd = mayor
    existe_inverso = resultado_mcd == 1
    pasos.append(
        _paso(
            "Resultado",
            f"El último residuo distinto de cero es {resultado_mcd}, así que "
            f"MCD({a}, {b}) = {resultado_mcd}.",
        )
    )
    if existe_inverso:
        pasos.append(
            _paso(
                "Qué significa",
                f"Como el MCD es 1, {a} y {b} no comparten divisores (son coprimos) y "
                f"{a} sí tiene inverso módulo {b}.",
            )
        )
    else:
        pasos.append(
            _paso(
                "Qué significa",
                f"Como el MCD es {resultado_mcd} y no 1, {a} y {b} comparten el divisor "
                f"{resultado_mcd}: {a} no tiene inverso módulo {b}.",
            )
        )
    pasos.append(
        _paso(
            "Comprobación",
            f"{a} = {a // resultado_mcd} × {resultado_mcd} y {b} = {b // resultado_mcd} × "
            f"{resultado_mcd}: {resultado_mcd} divide exacto a los dos.",
        )
    )
    return Resultado(
        valor=str(resultado_mcd),
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"{resultado_mcd} divide a los dos: {a} = {a // resultado_mcd} × {resultado_mcd} "
            f"y {b} = {b // resultado_mcd} × {resultado_mcd}"
        ),
        datos={
            "etiqueta": f"MCD({a}, {b})",
            "chips": [
                f"{len(tabla)} divisiones",
                "existe inverso" if existe_inverso else "no existe inverso",
            ],
            "mcd": resultado_mcd,
            "existe_inverso": existe_inverso,
            "nota_tabla": "En cada fila se divide a entre b y el residuo pasa a ser el "
            "b de la fila siguiente. El MCD es el último residuo distinto de cero.",
        },
    )


def _preparar_inverso(a: int, n: int) -> tuple[int, list[str]]:
    """Validaciones comunes de 1.5 y 1.6: Módulo válido, a reducido y coprimo."""
    if n < 2:
        raise ValueError(
            f"El módulo n debe ser al menos 2 y llegó n = {n}. "
            "Con n = 1 o menos no tiene sentido hablar de inversos."
        )
    pasos = []
    a_reducido = a % n
    if a_reducido != a:
        pasos.append(
            _paso(
                "Reducimos",
                f"{_num(a)} no está entre 0 y {n - 1}: {_num(a)} mod {n} = {a_reducido}, "
                f"y seguimos con {a_reducido}, que es equivalente.",
            )
        )
    if a_reducido == 0:
        raise ValueError(
            f"No existe inverso: {a} equivale a 0 módulo {n} y el 0 no tiene "
            f"inverso multiplicativo. Elige un número coprimo con {n}."
        )
    divisor_comun = mcd(a_reducido, n)
    if divisor_comun != 1:
        raise ValueError(
            f"No existe inverso: MCD({a_reducido}, {n}) = {divisor_comun}. "
            f"Elige un número coprimo con {n}."
        )
    return a_reducido, pasos


def inverso_tradicional(a: int, n: int) -> Resultado:
    """1.5 · Inverso multiplicativo probando x = 1, 2, 3, … hasta a·x mod n = 1.

    Método de fuerza bruta: Sirve para módulos pequeños (n ≤ 100 000).
    """
    if n > 100_000:
        raise ValueError(
            f"El método tradicional prueba una a una hasta n − 1 opciones y con "
            f"n = {n} sería demasiado lento. Usa n ≤ 100 000 o el submenú 1.6."
        )
    a_reducido, pasos = _preparar_inverso(a, n)
    pasos.append(
        _paso(
            "Qué buscamos",
            f"Un número x entre 1 y {n - 1} tal que {a_reducido} × x deje residuo 1 al "
            f"dividirlo entre {n}. Ese x es el inverso de {a_reducido} módulo {n}.",
        )
    )
    pasos.append(
        _paso(
            "Cómo lo hacemos",
            "A fuerza bruta: Probamos x = 1, 2, 3, … y en cada intento calculamos el "
            "producto y su residuo, hasta dar con residuo 1.",
        )
    )

    tabla = []
    frases_intentos = []
    inverso = None
    for x in range(1, n):
        producto = a_reducido * x
        residuo = producto % n
        tabla.append({"Intento x": x, "a × x": producto, "a × x mod n": residuo})
        cuenta = f"{a_reducido} × {x} = {producto}, y {producto} mod {n} = {residuo}."
        if residuo == 1:
            frases_intentos.append(_paso(f"Probamos x = {x}", cuenta + " El residuo es 1: Encontrado."))
            inverso = x
            break
        frases_intentos.append(_paso(f"Probamos x = {x}", cuenta + " No es 1, seguimos."))

    # Con MCD = 1 el inverso siempre aparece antes de agotar los intentos.
    # Si la lista de intentos es muy larga, en los pasos se resume.
    if len(frases_intentos) > 12:
        frases_intentos = (
            frases_intentos[:10]
            + [
                _paso(
                    "Seguimos probando",
                    f"{len(tabla) - 11} intentos más con residuo distinto de 1; la tabla "
                    "los muestra todos.",
                )
            ]
            + [frases_intentos[-1]]
        )
    pasos.extend(frases_intentos)
    producto_final = a_reducido * inverso
    pasos.append(
        _paso(
            "Resultado",
            f"El inverso de {a_reducido} módulo {n} es {inverso}; hicieron falta {inverso} intentos.",
        )
    )
    pasos.append(
        _paso(
            "Comprobación",
            f"{a_reducido} × {inverso} = {producto_final} = {producto_final // n} × {n} + 1: "
            "El residuo es 1.",
        )
    )
    return Resultado(
        valor=str(inverso),
        pasos=pasos,
        tabla=tabla,
        verificacion=f"{a_reducido} × {inverso} = {a_reducido * inverso} ≡ 1 (mod {n})",
        datos={
            "etiqueta": f"Inverso de {a} en módulo {n}",
            "chips": [f"{inverso} intentos", f"MCD({a_reducido}, {n}) = 1"],
            "intentos": inverso,
            "nota_tabla": f"x = {inverso} es el primer intento cuyo residuo es 1: "
            "Ese es el inverso.",
        },
    )


def aee(a: int, b: int) -> tuple[int, int, int, list[dict]]:
    """Algoritmo extendido de Euclides (AEE), implementado a mano.

    Devuelve (mcd, s, t, tabla) con la identidad s·a + t·b = mcd.
    La tabla trae dos filas "Inicio" (a: s=1, t=0 y b: s=0, t=1) y una fila
    por división, como se muestra en el submenú 1.6. La reutilizan el cifrado
    afín (2.6) y RSA (3.2) para hallar inversos.
    """
    if a < b or b < 1:
        raise ValueError(
            f"El AEE espera a ≥ b ≥ 1 y llegó ({a}, {b}). "
            "Pasa primero el número mayor."
        )
    tabla = [
        {"Ronda": "Inicio", "Cociente q": "—", "Residuo r": a, "s": 1, "t": 0},
        {"Ronda": "Inicio", "Cociente q": "—", "Residuo r": b, "s": 0, "t": 1},
    ]
    # (r0, s0, t0) y (r1, s1, t1) son las dos últimas filas de la tabla
    r0, s0, t0 = a, 1, 0
    r1, s1, t1 = b, 0, 1
    ronda = 0
    while r1 != 0:
        ronda += 1
        cociente = r0 // r1
        r2, s2, t2 = r0 - cociente * r1, s0 - cociente * s1, t0 - cociente * t1
        tabla.append(
            {"Ronda": str(ronda), "Cociente q": str(cociente), "Residuo r": r2, "s": s2, "t": t2}
        )
        r0, s0, t0 = r1, s1, t1
        r1, s1, t1 = r2, s2, t2
    # Al salir, (r0, s0, t0) es la última fila con residuo distinto de cero
    return r0, s0, t0, tabla


def inverso_aee(a: int, n: int) -> Resultado:
    """1.6 · Inverso multiplicativo con la tabla del algoritmo extendido de Euclides.

    El inverso es el t de la fila con residuo r = 1, llevado a módulo n.
    """
    a_reducido, pasos = _preparar_inverso(a, n)
    resultado_mcd, s, t, tabla = aee(n, a_reducido)
    rondas = len(tabla) - 2  # las dos primeras filas son de inicio, no divisiones
    inverso = t % n

    pasos.append(
        _paso(
            "Qué buscamos",
            f"Un número x entre 1 y {n - 1} tal que {a_reducido} × x deje residuo 1 al "
            f"dividirlo entre {n}. Ese x es el inverso de {a_reducido} módulo {n}.",
        )
    )
    pasos.append(
        _paso(
            "Preparamos la tabla",
            f"Dos filas de inicio: La de {n} (s = 1, t = 0) y la de {a_reducido} "
            f"(s = 0, t = 1). En cada fila se cumple s × {n} + t × {a_reducido} = residuo: "
            "s y t llevan la cuenta de cómo se forma cada residuo a partir de los dos números.",
        )
    )
    for indice in range(2, len(tabla)):
        anterior2, anterior1, actual = tabla[indice - 2], tabla[indice - 1], tabla[indice]
        q = actual["Cociente q"]
        r2, r1, r = anterior2["Residuo r"], anterior1["Residuo r"], actual["Residuo r"]
        explicacion = (
            f"Dividimos {r2} entre {r1}: Cabe {_plural(int(q), 'vez', 'veces')} y sobra {r}, así que "
            f"{r2} = {q} × {r1} + {r}. Los nuevos s y t salen de restar {_plural(int(q), 'vez', 'veces')} la fila "
            f"anterior: s = {_con_signo(anterior2['s'])} − {q} × {_con_signo(anterior1['s'])} "
            f"= {_num(actual['s'])} y t = {_con_signo(anterior2['t'])} − {q} × "
            f"{_con_signo(anterior1['t'])} = {_num(actual['t'])}."
        )
        if r == 1:
            explicacion += " Como el residuo es 1, esta es la fila que buscábamos."
        elif r == 0:
            explicacion += (
                f" Al llegar a residuo 0 se acaba la tabla: {rondas} divisiones, {rondas} rondas."
            )
        pasos.append(_paso(f"Ronda {actual['Ronda']}", explicacion))
    pasos.append(
        _paso(
            "Leemos el inverso",
            f"En la fila con residuo 1, t = {_num(t)}. Eso significa que "
            f"{_con_signo(s)} × {n} + {_con_signo(t)} × {a_reducido} = 1, o sea que "
            f"{_num(t)} × {a_reducido} deja residuo 1 al dividirlo entre {n}.",
        )
    )
    if t < 0:
        veces = (inverso - t) // n
        suma = f"{n}" if veces == 1 else f"{veces} × {n} = {veces * n}"
        pasos.append(
            _paso(
                "Lo pasamos a positivo",
                f"{_num(t)} no está entre 0 y {n - 1}, así que le sumamos {suma}: "
                f"{_num(t)} + {veces * n} = {inverso}. Sumar múltiplos de {n} no cambia el residuo.",
            )
        )
    else:
        pasos.append(
            _paso("Ya está en rango", f"t = {t} está entre 0 y {n - 1}, así que no hay que ajustarlo.")
        )
    producto_final = a_reducido * inverso
    pasos.append(_paso("Resultado", f"El inverso de {a_reducido} módulo {n} es {inverso}."))
    pasos.append(
        _paso(
            "Comprobación",
            f"{a_reducido} × {inverso} = {producto_final} y {producto_final} = "
            f"{producto_final // n} × {n} + 1: El residuo es 1.",
        )
    )
    return Resultado(
        valor=str(inverso),
        pasos=pasos,
        tabla=tabla,
        verificacion=f"{a_reducido} × {inverso} = {a_reducido * inverso} ≡ 1 (mod {n})",
        datos={
            "etiqueta": f"Inverso de {a} en módulo {n}",
            "chips": [f"{rondas} rondas", f"MCD({a_reducido}, {n}) = 1", f"t = {t}"],
            "rondas": rondas,
            "t": t,
            "s": s,
            "mcd": resultado_mcd,
            "nota_tabla": f"El inverso es el t de la fila con residuo r = 1: t = {t}, "
            f"y {t} mod {n} = {inverso}.",
        },
    )


# ======================================================================
# Criptografía clásica (fase 3)
# ======================================================================
#
# Todos los cifradores reciben `modo` ("cifrar" o "descifrar") y dejan en
# datos["verificar"] la receta de la operación inversa: función, entradas y
# resultado esperado. El botón "Verificar" de la interfaz ejecuta esa receta
# y confirma que se recupera el original.

# Alfabeto inglés de 26 letras, para el selector del César (2.2)
ALFABETO_26 = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

MODOS = ("cifrar", "descifrar")


def _validar_modo(modo) -> str:
    """Valida el modo de un cifrador y lo devuelve en minúsculas."""
    nombre = str(modo).strip().lower() if modo else ""
    if nombre not in MODOS:
        raise ValueError("Elige el modo de la operación: Cifrar o Descifrar.")
    return nombre


def _normalizar_no_vacio(texto: str, alfabeto: str = ALFABETO) -> str:
    """Normaliza un texto y exige que quede al menos una letra."""
    limpio = normalizar(texto, alfabeto)
    if limpio == "":
        raise ValueError(
            "El texto no tiene ninguna letra del alfabeto. "
            "Escribe al menos una letra de la A a la Z."
        )
    return limpio


def _abreviar(texto: str, limite: int = 18) -> str:
    """Acorta un texto largo para las etiquetas de la tarjeta de resultado."""
    return texto if len(texto) <= limite else texto[: limite - 1] + "…"


def _listado_numeros(tabla: list[dict], limite: int = 12) -> str:
    """«H = 7, O = 15, L = 11, A = 0»; con textos largos, las primeras letras y un aviso."""
    piezas = [f"{fila['Letra']} = {fila['Número']}" for fila in tabla]
    if len(piezas) > limite:
        return ", ".join(piezas[:limite]) + (
            f" … y así con las {len(piezas) - limite} letras restantes (la tabla las muestra todas)"
        )
    return ", ".join(piezas)


def _listado_operaciones(tabla: list[dict], titulo_final: str, limite: int = 12) -> str:
    """«H: (7 + 3) mod 27 = 10 → K. O: …», una operación por letra."""
    piezas = [f"{fila['Letra']}: {fila['Operación']} → {fila[titulo_final]}" for fila in tabla]
    aviso = ""
    if len(piezas) > limite:
        aviso = f" Y así con las {len(piezas) - limite} letras restantes; la tabla las muestra todas."
        piezas = piezas[:limite]
    return ". ".join(piezas) + "." + aviso


def _listado_bytes(octetos: bytes, limite: int = 12) -> str:
    """«H» = 48, «O» = 4F… cada byte en hexadecimal; si no son letras ASCII, solo los bytes."""
    if all(32 <= octeto < 127 for octeto in octetos):
        piezas = [f"«{chr(octeto)}» = {octeto:02X}" for octeto in octetos]
    else:
        piezas = [f"{octeto:02X}" for octeto in octetos]
    if len(piezas) > limite:
        return ", ".join(piezas[:limite]) + (
            f" … y {len(piezas) - limite} bytes más (la tabla los muestra todos)"
        )
    return ", ".join(piezas)


def _pasos_desplazamiento(limpio: str, k: int, alfabeto: str, modo: str, tabla: list[dict],
                          titulo_final: str, salida: str, inversa: str) -> list[str]:
    """Los pasos comunes de 2.1 y 2.2: Qué se hace, letras a números, la
    operación letra por letra, el resultado y la comprobación."""
    n = len(alfabeto)
    ultima = alfabeto[-1]
    numeracion = "A = 0, B = 1 … Ñ = 14 … Z = 26" if n == 27 else "A = 0, B = 1 … Z = 25"
    if modo == "cifrar":
        que = (
            f"Cada letra se cambia por la que está {k} puestos más adelante en el alfabeto "
            f"de {n} letras. Si nos pasamos de la {ultima} seguimos por la A: Eso es «mod {n}»."
        )
        accion = f"Sumamos {k} y tomamos mod {n}"
        vuelta = "resta"
    else:
        que = (
            f"Cada letra se cambia por la que está {k} puestos más atrás en el alfabeto "
            f"de {n} letras. Si nos pasamos de la A seguimos por la {ultima}: Eso es «mod {n}»."
        )
        accion = f"Restamos {k} y tomamos mod {n}"
        vuelta = "suma"
    primera = tabla[0]
    return [
        _paso("Qué hacemos", que),
        _paso("Letras a números", f"{numeracion}. «{limpio}» queda {_listado_numeros(tabla)}."),
        _paso(accion, _listado_operaciones(tabla, titulo_final)),
        _paso("Resultado", f"«{limpio}» se convierte en «{salida}»."),
        _paso(
            "Comprobación",
            f"Para deshacerlo se {vuelta} {k} a cada número: {primera[titulo_final]} = "
            f"{alfabeto.index(primera[titulo_final])} → {inversa} = {primera['Número']} → "
            f"{primera['Letra']}, y así se recupera «{limpio}».",
        ),
    ]


def _desplazar(limpio: str, k: int, alfabeto: str, modo: str, titulo_final: str) -> tuple[str, list[dict]]:
    """Aplica C = (M + k) mod N letra a letra (o M = (C − k) mod N al descifrar).

    Es el corazón de 2.1 (módulo 27) y 2.2 (César): Solo cambia el alfabeto.
    Devuelve el texto resultante y la tabla letra → número → operación → letra.
    """
    n = len(alfabeto)
    tabla = []
    salida = []
    for letra in limpio:
        m = alfabeto.index(letra)
        if modo == "cifrar":
            c = (m + k) % n
            operacion = f"({m} + {k}) mod {n} = {c}"
        else:
            c = (m - k) % n
            operacion = f"({m} − {k}) mod {n} = {c}"
        salida.append(alfabeto[c])
        tabla.append(
            {"Letra": letra, "Número": m, "Operación": operacion, titulo_final: alfabeto[c]}
        )
    return "".join(salida), tabla


def cifrado_modulo27(texto: str, k: int, modo: str = "cifrar") -> Resultado:
    """2.1 · Cifrado en módulo 27: C = (M + k) mod 27, M = (C − k) mod 27.

    Cada letra se convierte en su número del alfabeto español (A=0 … Ñ=14 …
    Z=26), se desplaza k posiciones y se vuelve letra.
    """
    nombre_modo = _validar_modo(modo)
    k = int(k)
    pasos = []
    limpio = _normalizar_no_vacio(texto)
    if limpio != str(texto):
        pasos.append(_paso("Preparamos el texto", f"Mayúsculas, sin tildes y solo letras: «{texto}» → «{limpio}»."))
    k_reducido = k % 27
    if k_reducido != k:
        pasos.append(
            _paso("Reducimos k", f"{k} es más de una vuelta al alfabeto: {k} mod 27 = {k_reducido}, que desplaza igual.")
        )

    titulo_final = "Letra cifrada" if nombre_modo == "cifrar" else "Letra descifrada"
    salida, tabla = _desplazar(limpio, k_reducido, ALFABETO, nombre_modo, titulo_final)

    primera = tabla[0]
    contrario = "descifrar" if nombre_modo == "cifrar" else "cifrar"
    participio = "cifrado" if nombre_modo == "cifrar" else "descifrado"
    indice_final = ALFABETO.index(primera[titulo_final])
    inversa = (
        f"({indice_final} − {k_reducido}) mod 27"
        if nombre_modo == "cifrar"
        else f"({indice_final} + {k_reducido}) mod 27"
    )
    pasos.extend(
        _pasos_desplazamiento(limpio, k_reducido, ALFABETO, nombre_modo, tabla, titulo_final, salida, inversa)
    )
    return Resultado(
        valor=salida,
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"{inversa} = {primera['Número']} = {primera['Letra']}: "
            "La operación inversa recupera la primera letra"
        ),
        datos={
            "etiqueta": f"«{_abreviar(limpio)}» {participio} con k = {k_reducido}",
            "chips": [f"k = {k_reducido}", f"{len(limpio)} letras", "alfabeto de 27"],
            "normalizado": limpio,
            "nota_tabla": "Cada fila convierte la letra en número, aplica la fórmula "
            "y vuelve a letra.",
            "verificar": {
                "funcion": "cifrado_modulo27",
                "entradas": {"texto": salida, "k": k_reducido, "modo": contrario},
                "esperado": limpio,
                "descripcion": f"{contrario} «{salida}» con k = {k_reducido}",
            },
        },
    )


def cifrado_cesar(texto: str, k: int = 3, alfabeto="27", modo: str = "cifrar") -> Resultado:
    """2.2 · César: Igual que el módulo 27 pero con alfabeto a elegir.

    Con 27 letras es el alfabeto español (con Ñ); con 26 es el inglés,
    donde la Ñ pierde la virgulilla y se escribe N. Por defecto k = 3,
    el desplazamiento del César histórico.
    """
    nombre_modo = _validar_modo(modo)
    k = int(k)
    codigo = str(alfabeto).strip()[:2]
    if codigo not in ("27", "26"):
        raise ValueError("Elige el alfabeto del César: 27 letras (español) o 26 letras.")
    letras_alfabeto = ALFABETO if codigo == "27" else ALFABETO_26
    n = len(letras_alfabeto)

    pasos = []
    limpio = _normalizar_no_vacio(texto, letras_alfabeto)
    if limpio != str(texto):
        pasos.append(_paso("Preparamos el texto", f"Mayúsculas, sin tildes y solo letras: «{texto}» → «{limpio}»."))
    if codigo == "26" and "Ñ" in str(texto).upper():
        pasos.append(_paso("Sin Ñ", "El alfabeto de 26 letras no tiene Ñ: La Ñ pierde la virgulilla y queda como N."))
    k_reducido = k % n
    if k_reducido != k:
        pasos.append(
            _paso("Reducimos k", f"{k} es más de una vuelta al alfabeto: {k} mod {n} = {k_reducido}, que desplaza igual.")
        )

    titulo_final = "Letra cifrada" if nombre_modo == "cifrar" else "Letra descifrada"
    salida, tabla = _desplazar(limpio, k_reducido, letras_alfabeto, nombre_modo, titulo_final)

    primera = tabla[0]
    contrario = "descifrar" if nombre_modo == "cifrar" else "cifrar"
    participio = "cifrado" if nombre_modo == "cifrar" else "descifrado"
    indice_final = letras_alfabeto.index(primera[titulo_final])
    inversa = (
        f"({indice_final} − {k_reducido}) mod {n}"
        if nombre_modo == "cifrar"
        else f"({indice_final} + {k_reducido}) mod {n}"
    )
    pasos.extend(
        _pasos_desplazamiento(
            limpio, k_reducido, letras_alfabeto, nombre_modo, tabla, titulo_final, salida, inversa
        )
    )
    return Resultado(
        valor=salida,
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"{inversa} = {primera['Número']} = {primera['Letra']}: "
            "La operación inversa recupera la primera letra"
        ),
        datos={
            "etiqueta": f"«{_abreviar(limpio)}» {participio} con César, k = {k_reducido}",
            "chips": [f"k = {k_reducido}", f"alfabeto de {n}", f"{len(limpio)} letras"],
            "normalizado": limpio,
            "nota_tabla": "Cada fila convierte la letra en número, aplica la fórmula "
            "y vuelve a letra.",
            "verificar": {
                "funcion": "cifrado_cesar",
                "entradas": {"texto": salida, "k": k_reducido, "alfabeto": codigo, "modo": contrario},
                "esperado": limpio,
                "descripcion": f"{contrario} «{salida}» con k = {k_reducido} y alfabeto de {n}",
            },
        },
    )


_HEX = "0123456789ABCDEF"


def cifrado_vernam(texto: str, clave: str, modo: str = "cifrar") -> Resultado:
    """2.3 · Vernam: XOR byte a byte entre el mensaje y la clave, en UTF-8.

    Al cifrar, mensaje y clave son texto y la salida va en hexadecimal y
    binario. Al descifrar, el mensaje llega en hexadecimal y se recupera el
    texto. La clave debe medir lo mismo que el mensaje en bytes; ojo: En
    UTF-8 la ñ, las tildes y la ü ocupan 2 bytes.
    """
    nombre_modo = _validar_modo(modo)
    if str(clave) == "":
        raise ValueError("La clave está vacía. Escribe una clave con la misma longitud en bytes que el mensaje.")
    bytes_clave = str(clave).encode("utf-8")
    if nombre_modo == "cifrar":
        que = (
            "Vernam mezcla el mensaje con una clave del mismo tamaño usando XOR bit a bit. "
            "Cada carácter se convierte en un byte (8 bits, en UTF-8) y se combina con el "
            "byte de la clave que está en la misma posición."
        )
    else:
        que = (
            "Para descifrar Vernam se aplica el mismo XOR con la misma clave: XOR se deshace "
            "a sí mismo, así que del cifrado sale otra vez el mensaje."
        )
    pasos = [_paso("Qué hacemos", que)]

    if nombre_modo == "cifrar":
        if str(texto) == "":
            raise ValueError("El mensaje está vacío. Escribe el texto que quieres cifrar.")
        bytes_mensaje = str(texto).encode("utf-8")
        pasos.append(
            _paso(
                "El mensaje en bytes",
                f"En UTF-8, «{texto}» ocupa {len(bytes_mensaje)} bytes (en hexadecimal): "
                f"{_listado_bytes(bytes_mensaje)}.",
            )
        )
    else:
        limpio_hex = str(texto).replace(" ", "").strip().upper()
        if limpio_hex == "":
            raise ValueError("El mensaje cifrado está vacío. Pega el resultado en hexadecimal.")
        if any(digito not in _HEX for digito in limpio_hex):
            raise ValueError(
                f"«{texto}» no es hexadecimal válido. Usa dígitos del 0 al 9 y letras de la A a la F."
            )
        if len(limpio_hex) % 2 != 0:
            raise ValueError(
                f"El mensaje cifrado tiene {len(limpio_hex)} dígitos hexadecimales y deben ser "
                "pares: Cada byte son dos dígitos."
            )
        bytes_mensaje = bytes.fromhex(limpio_hex)
        pasos.append(
            _paso(
                "Leemos el hexadecimal",
                f"Cada pareja de dígitos es un byte: {len(bytes_mensaje)} bytes: "
                f"{_listado_bytes(bytes_mensaje)}.",
            )
        )

    if len(bytes_mensaje) != len(bytes_clave):
        raise ValueError(
            f"La clave debe medir lo mismo que el mensaje: El mensaje ocupa "
            f"{len(bytes_mensaje)} bytes y la clave «{clave}» ocupa {len(bytes_clave)}. "
            "Recuerda que en UTF-8 la ñ, las tildes y la ü ocupan 2 bytes."
        )

    bytes_salida = bytes(m ^ c for m, c in zip(bytes_mensaje, bytes_clave))
    tabla = [
        {
            "Byte": posicion + 1,
            "Mensaje (bin)": f"{m:08b}",
            "Clave (bin)": f"{c:08b}",
            "Resultado (bin)": f"{r:08b}",
            "Resultado (hex)": f"{r:02X}",
        }
        for posicion, (m, c, r) in enumerate(zip(bytes_mensaje, bytes_clave, bytes_salida))
    ]
    hexadecimal = bytes_salida.hex().upper()
    binario = " ".join(f"{b:08b}" for b in bytes_salida)
    m0, c0, r0 = bytes_mensaje[0], bytes_clave[0], bytes_salida[0]
    pasos.extend(
        [
            _paso(
                "La clave en bytes",
                f"«{clave}» ocupa {len(bytes_clave)} bytes, igual que el mensaje: "
                f"{_listado_bytes(bytes_clave)}.",
            ),
            _paso(
                "XOR byte a byte",
                "Comparamos bit a bit cada byte del mensaje con el byte de la clave que está en "
                "la misma posición: 1 si los bits son distintos, 0 si son iguales. El primer "
                f"byte: {m0:02X} ⊕ {c0:02X} = {m0:08b} ⊕ {c0:08b} = {r0:08b}, que en "
                f"hexadecimal es {r0:02X}. La tabla muestra los {len(bytes_salida)} bytes.",
            ),
        ]
    )

    if nombre_modo == "cifrar":
        pasos.append(_paso("Resultado", f"Juntamos los bytes en hexadecimal: {hexadecimal}. En binario: {binario}."))
        pasos.append(
            _paso(
                "Comprobación",
                f"Aplicar XOR con la misma clave deshace el cifrado: {r0:02X} ⊕ {c0:02X} = "
                f"{m0:02X}, el primer byte del mensaje.",
            )
        )
        valor = hexadecimal
        codigo_copiable = f"Hexadecimal: {hexadecimal}\nBinario:     {binario}"
        receta = {
            "funcion": "cifrado_vernam",
            "entradas": {"texto": hexadecimal, "clave": str(clave), "modo": "descifrar"},
            "esperado": str(texto),
            "descripcion": f"descifrar «{hexadecimal}» con la clave «{clave}»",
        }
        etiqueta = f"«{_abreviar(str(texto))}» cifrado con Vernam"
    else:
        try:
            valor = bytes_salida.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                "El resultado del XOR no es texto UTF-8 válido. Revisa que el mensaje "
                "en hexadecimal y la clave sean los que se usaron al cifrar."
            ) from None
        pasos.append(_paso("Resultado", f"Interpretamos los bytes resultantes como texto UTF-8: «{valor}»."))
        pasos.append(
            _paso(
                "Comprobación",
                f"Cifrar «{valor}» con la misma clave devuelve {bytes_mensaje.hex().upper()}.",
            )
        )
        codigo_copiable = f"Texto recuperado: {valor}\nBinario:          {binario}"
        limpio_hex = bytes_mensaje.hex().upper()
        receta = {
            "funcion": "cifrado_vernam",
            "entradas": {"texto": valor, "clave": str(clave), "modo": "cifrar"},
            "esperado": limpio_hex,
            "descripcion": f"cifrar «{valor}» con la clave «{clave}»",
        }
        etiqueta = "Mensaje descifrado con Vernam"

    return Resultado(
        valor=valor,
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"{r0:02X} ⊕ {c0:02X} = {m0:02X}: Aplicar XOR con la clave otra vez "
            "recupera el primer byte"
        ),
        datos={
            "etiqueta": etiqueta,
            "chips": [f"{len(bytes_mensaje)} bytes", "XOR byte a byte", "clave de un solo uso"],
            "codigo": codigo_copiable,
            "hexadecimal": hexadecimal,
            "binario": binario,
            "nota_tabla": "Cada fila muestra un byte del mensaje, el byte de la clave "
            "en la misma posición y su XOR: 1 si los bits son distintos, 0 si son iguales.",
            "verificar": receta,
        },
    )


def cifrado_atbash(texto: str, modo: str = "cifrar") -> Resultado:
    """2.4 · Atbash: Cada letra se refleja en el alfabeto, i → 26 − i.

    A↔Z, B↔Y… La N ocupa la posición 13, el centro exacto del alfabeto de
    27, así que 26 − 13 = 13 y la N queda igual. Reflejar dos veces devuelve
    el original: Cifrar y descifrar son la misma operación.
    """
    nombre_modo = _validar_modo(modo)
    pasos = []
    limpio = _normalizar_no_vacio(texto)
    if limpio != str(texto):
        pasos.append(_paso("Preparamos el texto", f"Mayúsculas, sin tildes y solo letras: «{texto}» → «{limpio}»."))

    titulo_final = "Letra cifrada" if nombre_modo == "cifrar" else "Letra descifrada"
    tabla = []
    salida = []
    for letra in limpio:
        i = letra_a_numero(letra)
        reflejo = 26 - i
        salida.append(numero_a_letra(reflejo))
        tabla.append(
            {"Letra": letra, "Número": i, "Operación": f"26 − {i} = {reflejo}", titulo_final: numero_a_letra(reflejo)}
        )
    resultado_texto = "".join(salida)

    primera = tabla[0]
    pasos.extend(
        [
            _paso(
                "Qué hacemos",
                "Atbash refleja el alfabeto: La primera letra se cambia por la última, la "
                "segunda por la penúltima, y así. Con los números del alfabeto de 27, la letra "
                "i se cambia por 26 − i. Cifrar y descifrar son la misma operación.",
            ),
            _paso("Letras a números", f"A = 0, B = 1 … Ñ = 14 … Z = 26. «{limpio}» queda {_listado_numeros(tabla)}."),
            _paso("Reflejamos cada letra", _listado_operaciones(tabla, titulo_final)),
            _paso("La N no cambia", "Está en la posición 13, justo en el centro del alfabeto: 26 − 13 = 13."),
            _paso("Resultado", f"«{limpio}» se convierte en «{resultado_texto}»."),
            _paso(
                "Comprobación",
                f"Reflejar otra vez devuelve el original: {primera[titulo_final]} = "
                f"{26 - primera['Número']} → 26 − {26 - primera['Número']} = {primera['Número']} → "
                f"{primera['Letra']}, y así se recupera «{limpio}».",
            ),
        ]
    )
    contrario = "descifrar" if nombre_modo == "cifrar" else "cifrar"
    participio = "cifrado" if nombre_modo == "cifrar" else "descifrado"
    return Resultado(
        valor=resultado_texto,
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"26 − {26 - primera['Número']} = {primera['Número']} = {primera['Letra']}: "
            "Reflejar otra vez recupera la primera letra"
        ),
        datos={
            "etiqueta": f"«{_abreviar(limpio)}» {participio} con Atbash",
            "chips": ["i → 26 − i", "la N queda igual", f"{len(limpio)} letras"],
            "normalizado": limpio,
            "nota_tabla": "Atbash refleja el alfabeto: A↔Z, B↔Y… y la N, en el centro, "
            "se queda en su sitio.",
            "verificar": {
                "funcion": "cifrado_atbash",
                "entradas": {"texto": resultado_texto, "modo": contrario},
                "esperado": limpio,
                "descripcion": f"{contrario} «{resultado_texto}» con Atbash",
            },
        },
    )


def transposicion_columnar(texto: str, clave: str, modo: str = "cifrar") -> Resultado:
    """2.5 · Transposición columnar simple con clave de palabra.

    Al cifrar, el mensaje se escribe en filas bajo la clave, se rellena con X
    y se leen las columnas en el orden alfabético de las letras de la clave
    (los empates se numeran de izquierda a derecha). Al descifrar se reparte
    el mensaje en columnas siguiendo ese orden y se lee por filas.
    """
    nombre_modo = _validar_modo(modo)
    clave_limpia = normalizar(clave)
    if len(clave_limpia) < 2:
        raise ValueError(
            f"La clave necesita al menos 2 letras para formar columnas y «{clave}» "
            f"queda en «{clave_limpia}». Escribe una palabra, por ejemplo CLAVE."
        )
    if nombre_modo == "cifrar":
        que = (
            f"Escribimos el mensaje en filas debajo de la clave «{clave_limpia}», una letra "
            "por columna, y luego leemos las columnas en el orden alfabético de las letras "
            "de la clave."
        )
    else:
        que = (
            "Hacemos el camino inverso: Repartimos el mensaje cifrado en columnas siguiendo "
            f"el orden alfabético de las letras de la clave «{clave_limpia}» y leemos la "
            "matriz por filas."
        )
    pasos = [_paso("Qué hacemos", que)]
    limpio = _normalizar_no_vacio(texto)
    if limpio != str(texto):
        pasos.append(_paso("Preparamos el texto", f"Mayúsculas, sin tildes y solo letras: «{texto}» → «{limpio}»."))
    if clave_limpia != str(clave):
        pasos.append(_paso("Preparamos la clave", f"Mayúsculas, sin tildes y solo letras: «{clave}» → «{clave_limpia}»."))

    columnas_total = len(clave_limpia)
    # Orden de lectura: índices de columna ordenados por la letra de la clave;
    # en empate gana la columna de más a la izquierda
    orden_lectura = sorted(range(columnas_total), key=lambda i: (letra_a_numero(clave_limpia[i]), i))
    numero_de_orden = [0] * columnas_total
    for rango, indice in enumerate(orden_lectura, start=1):
        numero_de_orden[indice] = rango
    numeracion = ", ".join(
        f"{clave_limpia[i]}={numero_de_orden[i]}" for i in orden_lectura
    )
    pasos.append(
        _paso(
            "Numeramos las columnas",
            f"Por orden alfabético de las letras de la clave: {numeracion}. Si una letra se "
            "repite, va primero la de más a la izquierda.",
        )
    )

    if nombre_modo == "cifrar":
        filas_total = (len(limpio) + columnas_total - 1) // columnas_total  # división hacia arriba
        relleno = filas_total * columnas_total - len(limpio)
        con_relleno = limpio + "X" * relleno
        filas = [con_relleno[i * columnas_total:(i + 1) * columnas_total] for i in range(filas_total)]
        matriz = (
            f"El mensaje tiene {len(limpio)} letras y la clave {columnas_total}, así que "
            f"salen {filas_total} filas de {columnas_total} letras"
        )
        if relleno:
            matriz += (
                f"; {'falta' if relleno == 1 else 'faltan'} {_plural(relleno, 'casilla', 'casillas')} "
                f"y la{'' if relleno == 1 else 's'} rellenamos con X: «{con_relleno}»"
            )
        pasos.append(_paso("Llenamos la matriz", f"{matriz}. Filas: {' / '.join(filas)}."))
        trozos = ["".join(fila[indice] for fila in filas) for indice in orden_lectura]
        salida = "".join(trozos)
        lectura = ", ".join(
            f"{clave_limpia[indice]}({numero_de_orden[indice]}) → {trozo}"
            for indice, trozo in zip(orden_lectura, trozos)
        )
        pasos.append(_paso("Leemos las columnas en orden", f"Columna por columna, de arriba abajo: {lectura}."))
        pasos.append(_paso("Resultado", f"Uniendo los trozos en ese orden queda «{salida}»."))
        pasos.append(
            _paso(
                "Comprobación",
                f"La matriz conserva las {len(con_relleno)} letras: Leída por filas devuelve "
                f"«{con_relleno}», el mensaje con su relleno.",
            )
        )
        receta = {
            "funcion": "transposicion_columnar",
            "entradas": {"texto": salida, "clave": clave_limpia, "modo": "descifrar"},
            "esperado": con_relleno,
            "descripcion": f"descifrar «{salida}» con la clave «{clave_limpia}»",
        }
        etiqueta = f"«{_abreviar(limpio)}» cifrado por columnas"
        verificacion = (
            f"La matriz conserva las {len(con_relleno)} letras: Leerla por filas "
            f"devuelve «{con_relleno}»"
        )
        chips = [
            f"{columnas_total} columnas",
            f"{filas_total} filas",
            f"relleno: {relleno} X" if relleno else "sin relleno",
        ]
    else:
        if len(limpio) % columnas_total != 0:
            raise ValueError(
                f"El mensaje cifrado tiene {len(limpio)} letras y no se reparte exacto "
                f"en {columnas_total} columnas. Revisa el texto o la clave: Al cifrar "
                "se rellenó con X hasta completar la matriz."
            )
        filas_total = len(limpio) // columnas_total
        pasos.append(
            _paso(
                "Medimos la matriz",
                f"El mensaje cifrado tiene {len(limpio)} letras y la clave {columnas_total}, así "
                f"que la matriz tiene {filas_total} filas: Cada columna recibe {filas_total} letras.",
            )
        )
        columnas = [""] * columnas_total
        posicion = 0
        trozos = []
        for indice in orden_lectura:
            columnas[indice] = limpio[posicion:posicion + filas_total]
            trozos.append(f"{clave_limpia[indice]}({numero_de_orden[indice]}) ← {columnas[indice]}")
            posicion += filas_total
        pasos.append(
            _paso(
                "Repartimos en columnas",
                f"Cortamos el cifrado en trozos de {filas_total} letras y los colocamos "
                f"siguiendo la numeración: {', '.join(trozos)}.",
            )
        )
        filas = [
            "".join(columnas[c][f] for c in range(columnas_total)) for f in range(filas_total)
        ]
        salida = "".join(filas)
        con_relleno = salida
        pasos.append(_paso("Resultado", f"Leemos la matriz por filas, de izquierda a derecha: «{salida}»."))
        if salida.endswith("X"):
            pasos.append(_paso("Ojo con las X", "Las X del final pueden ser el relleno que se agregó al cifrar."))
        pasos.append(
            _paso("Comprobación", f"Cifrar «{salida}» con la clave «{clave_limpia}» devuelve «{limpio}».")
        )
        receta = {
            "funcion": "transposicion_columnar",
            "entradas": {"texto": salida, "clave": clave_limpia, "modo": "cifrar"},
            "esperado": limpio,
            "descripcion": f"cifrar «{salida}» con la clave «{clave_limpia}»",
        }
        etiqueta = "Mensaje descifrado por columnas"
        verificacion = (
            f"La matriz conserva las {len(limpio)} letras: Leer las columnas en orden "
            f"devuelve «{limpio}»"
        )
        chips = [f"{columnas_total} columnas", f"{filas_total} filas"]

    # Matriz para st.dataframe: cada columna se titula con su letra de la
    # clave y el número de orden encima de las letras del mensaje
    encabezados = [
        f"{clave_limpia[i]} ({numero_de_orden[i]})" for i in range(columnas_total)
    ]
    tabla = [dict(zip(encabezados, fila)) for fila in filas]

    return Resultado(
        valor=salida,
        pasos=pasos,
        tabla=tabla,
        verificacion=verificacion,
        datos={
            "etiqueta": etiqueta,
            "chips": chips,
            "normalizado": limpio,
            "clave": clave_limpia,
            "orden": numero_de_orden,
            "nota_tabla": "La matriz con la clave y su número de orden encima: Al cifrar "
            "se leen las columnas siguiendo esa numeración; al descifrar se leen las filas.",
            "verificar": receta,
        },
    )


def cifrado_afin(texto: str, a: int, b: int, modo: str = "cifrar") -> Resultado:
    """2.6 · Afín: C = (a·M + b) mod 27 y M = a⁻¹·(C − b) mod 27.

    Solo funciona si MCD(a, 27) = 1, porque descifrar necesita el inverso
    a⁻¹. Ese inverso se calcula con el algoritmo extendido de Euclides del
    submenú 1.6, reutilizando mcd() y aee().
    """
    nombre_modo = _validar_modo(modo)
    a, b = int(a), int(b)
    pasos = []
    a_reducido = a % 27
    b_reducido = b % 27
    if a_reducido != a or b_reducido != b:
        pasos.append(
            _paso(
                "Reducimos las llaves",
                f"Las llaves se toman módulo 27: a = {a} mod 27 = {a_reducido} y b = {b} mod 27 = {b_reducido}.",
            )
        )
    divisor = mcd(a_reducido, 27) if a_reducido else 27
    if divisor != 1:
        raise ValueError(
            f"No sirve a = {a}: MCD({a_reducido}, 27) = {divisor} y debe ser 1 para que "
            "exista a⁻¹ y se pueda descifrar. Elige un a que no sea múltiplo de 3."
        )
    limpio = _normalizar_no_vacio(texto)
    if limpio != str(texto):
        pasos.insert(0, _paso("Preparamos el texto", f"Mayúsculas, sin tildes y solo letras: «{texto}» → «{limpio}»."))
    if nombre_modo == "cifrar":
        que = (
            f"El afín multiplica y suma: C = (a × M + b) mod 27, con a = {a_reducido} y "
            f"b = {b_reducido}. Para poder descifrar después hace falta a⁻¹, el inverso de a "
            "módulo 27, y por eso a debe ser coprimo con 27."
        )
    else:
        que = (
            "Para descifrar el afín se deshace la suma y la multiplicación: "
            f"M = a⁻¹ × (C − b) mod 27, con a = {a_reducido} y b = {b_reducido}. "
            "a⁻¹ es el inverso de a módulo 27, y existe porque a es coprimo con 27."
        )
    pasos.insert(0, _paso("Qué hacemos", que))

    # a⁻¹ con el algoritmo extendido de Euclides del módulo 1
    _, _, t, tabla_aee = aee(27, a_reducido)
    a_inverso = t % 27
    rondas = len(tabla_aee) - 2
    pasos.append(
        _paso("Comprobamos a", f"MCD({a_reducido}, 27) = 1: a no comparte divisores con 27, así que tiene inverso.")
    )
    pasos.append(
        _paso(
            "Hallamos a⁻¹",
            f"Con la tabla del Euclides extendido del submenú 1.6 ({rondas} rondas): "
            f"t = {_num(t)} y a⁻¹ = {_num(t)} mod 27 = {a_inverso}. Comprobación: "
            f"{a_reducido} × {a_inverso} = {a_reducido * a_inverso} y "
            f"{a_reducido * a_inverso} mod 27 = 1.",
        )
    )

    titulo_final = "Letra cifrada" if nombre_modo == "cifrar" else "Letra descifrada"
    tabla = []
    salida = []
    for letra in limpio:
        numero = letra_a_numero(letra)
        if nombre_modo == "cifrar":
            resultado_numero = (a_reducido * numero + b_reducido) % 27
            operacion = f"({a_reducido} × {numero} + {b_reducido}) mod 27 = {resultado_numero}"
        else:
            resultado_numero = (a_inverso * (numero - b_reducido)) % 27
            operacion = f"{a_inverso} × ({numero} − {b_reducido}) mod 27 = {resultado_numero}"
        salida.append(numero_a_letra(resultado_numero))
        tabla.append(
            {"Letra": letra, "Número": numero, "Operación": operacion, titulo_final: numero_a_letra(resultado_numero)}
        )
    resultado_texto = "".join(salida)

    formula = "C = (a × M + b) mod 27" if nombre_modo == "cifrar" else "M = a⁻¹ × (C − b) mod 27"
    primera = tabla[0]
    contrario = "descifrar" if nombre_modo == "cifrar" else "cifrar"
    participio = "cifrado" if nombre_modo == "cifrar" else "descifrado"
    indice_final = letra_a_numero(primera[titulo_final])
    if nombre_modo == "cifrar":
        inversa = f"{a_inverso} × ({indice_final} − {b_reducido}) mod 27"
    else:
        inversa = f"({a_reducido} × {indice_final} + {b_reducido}) mod 27"
    pasos.extend(
        [
            _paso("Letras a números", f"A = 0, B = 1 … Ñ = 14 … Z = 26. «{limpio}» queda {_listado_numeros(tabla)}."),
            _paso(f"Aplicamos {formula}", _listado_operaciones(tabla, titulo_final)),
            _paso("Resultado", f"«{limpio}» se convierte en «{resultado_texto}»."),
            _paso(
                "Comprobación",
                f"Para {contrario}: {primera[titulo_final]} = {indice_final} → {inversa} = "
                f"{primera['Número']} → {primera['Letra']}, y así se recupera «{limpio}».",
            ),
        ]
    )
    return Resultado(
        valor=resultado_texto,
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"{inversa} = {primera['Número']} = {primera['Letra']}: "
            "La operación inversa recupera la primera letra"
        ),
        datos={
            "etiqueta": f"«{_abreviar(limpio)}» {participio} con afín, a = {a_reducido}, b = {b_reducido}",
            "chips": [f"a⁻¹ = {a_inverso}", f"MCD({a_reducido}, 27) = 1", f"{rondas} rondas del AEE"],
            "normalizado": limpio,
            "a_inverso": a_inverso,
            "nota_tabla": "Cada fila convierte la letra en número, aplica la fórmula afín "
            "y vuelve a letra.",
            "tabla_extra": {
                "titulo": f"Tabla del AEE para a⁻¹ = {a_inverso}",
                "filas": tabla_aee,
                "nota": f"La misma tabla del submenú 1.6 con n = 27 y a = {a_reducido}: "
                f"El inverso es el t de la fila con residuo r = 1, y {t} mod 27 = {a_inverso}.",
            },
            "verificar": {
                "funcion": "cifrado_afin",
                "entradas": {"texto": resultado_texto, "a": a_reducido, "b": b_reducido, "modo": contrario},
                "esperado": limpio,
                "descripcion": f"{contrario} «{resultado_texto}» con a = {a_reducido} y b = {b_reducido}",
            },
        },
    )


def sustitucion_simple(texto: str, clave: str, modo: str = "cifrar") -> Resultado:
    """2.7 · Sustitución simple con alfabeto desordenado.

    La clave puede ser una palabra (el alfabeto cifrado empieza con sus
    letras sin repetir y sigue con el resto del alfabeto en orden) o una
    permutación completa de las 27 letras, que se usa tal cual.
    """
    nombre_modo = _validar_modo(modo)
    clave_limpia = normalizar(clave)
    if clave_limpia == "":
        raise ValueError(
            f"La clave «{clave}» no tiene letras del alfabeto. Escribe una palabra "
            "(por ejemplo MURCIELAGO) o una permutación completa de las 27 letras."
        )
    if nombre_modo == "cifrar":
        que = (
            "Cada letra se cambia por la que ocupa su misma posición en un alfabeto "
            "desordenado, que se construye a partir de la clave."
        )
    else:
        que = (
            "Cada letra del cifrado se busca en el alfabeto desordenado (construido con la "
            "clave) y se cambia por la letra normal que ocupa esa misma posición."
        )
    pasos = [_paso("Qué hacemos", que)]
    if clave_limpia != str(clave):
        pasos.append(_paso("Preparamos la clave", f"Mayúsculas, sin tildes y solo letras: «{clave}» → «{clave_limpia}»."))

    if len(clave_limpia) == 27 and set(clave_limpia) == set(ALFABETO):
        alfabeto_cifrado = clave_limpia
        tipo_clave = "permutación completa"
        pasos.append(
            _paso("Alfabeto cifrado", "La clave ya es una permutación de las 27 letras: Se usa tal cual como alfabeto cifrado.")
        )
    else:
        # dict.fromkeys conserva el orden y quita las letras repetidas
        sin_repetidas = "".join(dict.fromkeys(clave_limpia))
        resto = "".join(letra for letra in ALFABETO if letra not in sin_repetidas)
        alfabeto_cifrado = sin_repetidas + resto
        tipo_clave = "palabra clave"
        if sin_repetidas != clave_limpia:
            pasos.append(
                _paso("Quitamos repetidas", f"Cada letra de la clave se usa una sola vez: «{clave_limpia}» → «{sin_repetidas}».")
            )
        pasos.append(
            _paso(
                "Construimos el alfabeto cifrado",
                f"Empieza con las letras de la clave («{sin_repetidas}») y sigue con las "
                f"{27 - len(sin_repetidas)} letras que faltan, en orden alfabético: «{alfabeto_cifrado}».",
            )
        )

    limpio = _normalizar_no_vacio(texto)
    if limpio != str(texto):
        pasos.insert(1, _paso("Preparamos el texto", f"Mayúsculas, sin tildes y solo letras: «{texto}» → «{limpio}»."))

    salida = []
    correspondencias = []
    for letra in limpio:
        if nombre_modo == "cifrar":
            nueva = alfabeto_cifrado[letra_a_numero(letra)]
        else:
            nueva = numero_a_letra(alfabeto_cifrado.index(letra))
        salida.append(nueva)
        correspondencias.append(f"{letra} → {nueva}")
    resultado_texto = "".join(salida)

    sentido = (
        "buscamos cada letra en la fila de arriba y la cambiamos por la de abajo"
        if nombre_modo == "cifrar"
        else "buscamos cada letra en la fila de abajo y subimos a la de arriba"
    )
    if len(correspondencias) > 20:
        correspondencias = correspondencias[:20] + ["…"]
    pasos.append(
        _paso(
            "Tabla de correspondencias",
            "Arriba va el alfabeto normal (A, B, C…) y abajo el cifrado, letra bajo letra. "
            "Cifrar es bajar de fila; descifrar, subir.",
        )
    )
    pasos.append(_paso("Cambiamos cada letra", f"{sentido[0].upper() + sentido[1:]}: {', '.join(correspondencias)}."))
    pasos.append(_paso("Resultado", f"«{limpio}» se convierte en «{resultado_texto}»."))
    pasos.append(
        _paso(
            "Comprobación",
            f"Leyendo la tabla en sentido contrario, {resultado_texto[0]} → {limpio[0]}, "
            f"y así se recupera «{limpio}».",
        )
    )

    # Tabla de correspondencias en dos filas: el alfabeto original arriba
    # (encabezados) y el alfabeto cifrado abajo
    tabla = [dict(zip(ALFABETO, alfabeto_cifrado))]

    contrario = "descifrar" if nombre_modo == "cifrar" else "cifrar"
    participio = "cifrado" if nombre_modo == "cifrar" else "descifrado"
    primera_original = limpio[0]
    primera_nueva = resultado_texto[0]
    return Resultado(
        valor=resultado_texto,
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"{primera_nueva} → {primera_original} leyendo la tabla al revés: "
            "La sustitución inversa recupera la primera letra"
        ),
        datos={
            "etiqueta": f"«{_abreviar(limpio)}» {participio} por sustitución",
            "chips": [tipo_clave, f"clave «{_abreviar(clave_limpia, 14)}»", f"{len(limpio)} letras"],
            "normalizado": limpio,
            "alfabeto_cifrado": alfabeto_cifrado,
            "tipo_clave": tipo_clave,
            "nota_tabla": "Tabla de correspondencias en dos filas: Arriba el alfabeto "
            "original y abajo el cifrado. Cifrar baja de fila; descifrar sube.",
            "verificar": {
                "funcion": "sustitucion_simple",
                "entradas": {"texto": resultado_texto, "clave": clave_limpia, "modo": contrario},
                "esperado": limpio,
                "descripcion": f"{contrario} «{resultado_texto}» con la clave «{clave_limpia}»",
            },
        },
    )


# ======================================================================
# Criptografía moderna (fase 4)
# ======================================================================
#
# Los tres submenús comparten piezas hechas a mano: es_primo valida los
# primos con divisiones de prueba y exp_rapida calcula todas las potencias
# modulares. RSA además reutiliza mcd (1.4) y aee (1.6) para d = e⁻¹ mod φ.

# Dígitos en superíndice para escribir potencias como 5⁶ o 3¹³
_SUPERINDICES = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")

# Tope para los primos de 3.1 y 3.2: la prueba de primalidad divide una a
# una hasta la raíz cuadrada y con números más grandes se vuelve lenta
LIMITE_PRIMO = 1_000_000


def _potencia_txt(base: int, exponente: int) -> str:
    """Escribe bᵉ con el exponente en superíndice, por ejemplo 3¹³."""
    return f"{base}{str(exponente).translate(_SUPERINDICES)}"


def _primer_divisor(n: int) -> int | None:
    """El divisor más pequeño de n entre 2 y √n, o None si n ≥ 2 es primo."""
    if n % 2 == 0 and n > 2:
        return 2
    divisor = 3
    while divisor * divisor <= n:
        if n % divisor == 0:
            return divisor
        divisor += 2
    return None


def es_primo(n: int) -> bool:
    """Primalidad por divisiones de prueba hasta la raíz cuadrada, a mano."""
    return n >= 2 and _primer_divisor(n) is None


def exp_rapida(base: int, exponente: int, n: int) -> tuple[int, list[dict], int]:
    """Exponenciación rápida (cuadrados sucesivos), implementada a mano.

    Calcula base^exponente mod n recorriendo los bits del exponente del
    menos al más significativo: En cada fila la potencia se eleva al
    cuadrado y, cuando el bit es 1, se multiplica al acumulado. Devuelve
    (resultado, tabla, multiplicaciones). Es la pieza que reutilizan
    Diffie-Hellman (3.1) y RSA (3.2) para todas sus potencias.
    """
    if n < 2:
        raise ValueError(
            f"El módulo n debe ser al menos 2 y llegó n = {n}. "
            "Con n = 1 todos los residuos valen 0."
        )
    if exponente < 1:
        raise ValueError(
            f"El exponente debe ser al menos 1 y llegó {exponente}. "
            "Escribe un entero positivo."
        )
    # Bits del exponente del menos al más significativo, dividiendo entre 2
    bits = []
    resto = exponente
    while resto > 0:
        bits.append(resto % 2)
        resto //= 2

    potencia = base % n
    acumulado = 1
    multiplicaciones = 0
    tabla = []
    for i, bit in enumerate(bits):
        if i > 0:
            potencia = potencia * potencia % n
            multiplicaciones += 1
        if bit == 1:
            acumulado = acumulado * potencia % n
            multiplicaciones += 1
        tabla.append(
            {
                "Bit i": i,
                "Bit del exponente": bit,
                "Potencia al cuadrado": potencia,
                "Acumulado": acumulado,
            }
        )
    return acumulado, tabla, multiplicaciones


def diffie_hellman(p: int, g: int, a: int, b: int) -> Resultado:
    """3.1 · Intercambio de claves Diffie-Hellman.

    Con p y g públicos, Alicia publica A = gᵃ mod p y Bob publica
    B = gᵇ mod p. Cada uno eleva lo que recibe a su clave privada y los
    dos llegan a la misma K porque (gᵇ)ᵃ = (gᵃ)ᵇ = g^(a × b) (mod p).
    Todas las potencias se calculan con exp_rapida (3.3). Si p no es
    primo el cálculo sale igual, pero se deja un aviso en datos["aviso"].
    """
    p, g, a, b = int(p), int(g), int(a), int(b)
    if p < 3:
        raise ValueError(
            f"El módulo p debe ser al menos 3 y llegó p = {p}. Usa un primo, como 23."
        )
    if p > LIMITE_PRIMO:
        raise ValueError(
            f"Para comprobar si p es primo se divide una a una hasta su raíz y con "
            f"p = {p} sería lento. Usa p ≤ 1 000 000."
        )
    if not 2 <= g <= p - 1:
        raise ValueError(
            f"El generador g debe estar entre 2 y p − 1 = {p - 1} y llegó g = {g}."
        )
    if a < 1 or b < 1:
        raise ValueError(
            f"Las claves privadas deben ser enteros positivos y llegaron "
            f"a = {a} y b = {b}."
        )

    pasos = [
        _paso(
            "Qué buscamos",
            "Que Alicia y Bob acuerden una clave secreta K hablando por un canal que "
            "cualquiera puede escuchar. Cada uno guarda un número privado y publica solo "
            "una potencia de g.",
        ),
        _paso(
            "Datos",
            f"Públicos: p = {p} (el módulo) y g = {g} (la base). Privados: a = {a} de "
            f"Alicia y b = {b} de Bob.",
        ),
    ]
    aviso = None
    if es_primo(p):
        pasos.append(
            _paso(
                "Comprobamos p",
                f"Probamos dividir {p} entre 2, 3, 5, … hasta su raíz cuadrada y ninguno lo "
                f"divide exacto: {p} es primo, como pide el método.",
            )
        )
    else:
        divisor = _primer_divisor(p)
        aviso = (
            f"p = {p} no es primo: {p} = {divisor} × {p // divisor}. El cálculo sale "
            "igual, pero Diffie-Hellman solo es seguro con un p primo (y en la "
            "práctica, enorme)."
        )
        pasos.append(
            _paso(
                "Comprobamos p",
                f"{p} = {divisor} × {p // divisor}: No es primo. El cálculo sale igual, "
                "pero el intercambio pierde su seguridad.",
            )
        )

    a_publica, _, mult_a = exp_rapida(g, a, p)
    b_publica, _, mult_b = exp_rapida(g, b, p)
    k_alicia, tabla_k, _ = exp_rapida(b_publica, a, p)
    k_bob, _, _ = exp_rapida(a_publica, b, p)

    pasos.extend(
        [
            _paso(
                "Alicia publica A",
                f"Eleva g a su número privado: A = gᵃ mod p = {_potencia_txt(g, a)} mod {p} "
                f"= {a_publica}. Lo calcula con la exponenciación rápida del 3.3 "
                f"({mult_a} multiplicaciones).",
            ),
            _paso(
                "Bob publica B",
                f"Hace lo mismo con el suyo: B = gᵇ mod p = {_potencia_txt(g, b)} mod {p} "
                f"= {b_publica} ({mult_b} multiplicaciones).",
            ),
            _paso(
                "Intercambio",
                "A y B viajan por el canal público y cualquiera puede verlos; a y b nunca "
                "salen de cada lado.",
            ),
            _paso(
                "Alicia calcula K",
                f"Eleva lo que recibió de Bob a su número privado: K = Bᵃ mod p = "
                f"{_potencia_txt(b_publica, a)} mod {p} = {k_alicia}.",
            ),
            _paso(
                "Bob calcula K",
                f"Eleva lo que recibió de Alicia al suyo: K = Aᵇ mod p = "
                f"{_potencia_txt(a_publica, b)} mod {p} = {k_bob}.",
            ),
            _paso(
                "Comprobación",
                f"Los dos obtienen K = {k_alicia} porque Bᵃ = (gᵇ)ᵃ = g^(a × b) = (gᵃ)ᵇ = Aᵇ "
                "(mod p): Da igual el orden en que se aplican los exponentes. Quien escucha "
                "el canal solo ve p, g, A y B; sacar a o b de ahí es el problema del "
                "logaritmo discreto, muy difícil con números grandes.",
            ),
        ]
    )

    tabla = [
        {
            "Quién": "Alicia",
            "Calcula": "A = gᵃ mod p",
            "Operación": f"{_potencia_txt(g, a)} mod {p}",
            "Resultado": a_publica,
            "Viaja por el canal": "sí: A es pública",
        },
        {
            "Quién": "Bob",
            "Calcula": "B = gᵇ mod p",
            "Operación": f"{_potencia_txt(g, b)} mod {p}",
            "Resultado": b_publica,
            "Viaja por el canal": "sí: B es pública",
        },
        {
            "Quién": "Alicia",
            "Calcula": "K = Bᵃ mod p",
            "Operación": f"{_potencia_txt(b_publica, a)} mod {p}",
            "Resultado": k_alicia,
            "Viaja por el canal": "no: K queda en secreto",
        },
        {
            "Quién": "Bob",
            "Calcula": "K = Aᵇ mod p",
            "Operación": f"{_potencia_txt(a_publica, b)} mod {p}",
            "Resultado": k_bob,
            "Viaja por el canal": "no: K queda en secreto",
        },
    ]

    datos = {
        "etiqueta": f"Clave compartida con p = {p} y g = {g}",
        "chips": [
            "p primo" if aviso is None else "p no primo",
            "4 potencias con la exp. rápida de 3.3",
            f"Bᵃ ≡ Aᵇ ≡ {k_alicia} (mod {p})",
        ],
        "metricas": [
            ("A = gᵃ mod p", a_publica),
            ("B = gᵇ mod p", b_publica),
            ("K compartida", k_alicia),
        ],
        "A": a_publica,
        "B": b_publica,
        "K": k_alicia,
        "nota_tabla": "A y B viajan por el canal público; a, b y K nunca. Los dos "
        "caminos llegan a la misma K porque (gᵇ)ᵃ = (gᵃ)ᵇ = g^(a × b) (mod p).",
        "tabla_extra": {
            "titulo": f"Exponenciación rápida (3.3) para K = Bᵃ mod p = "
            f"{_potencia_txt(b_publica, a)} mod {p}",
            "filas": tabla_k,
            "nota": "La misma tabla del submenú 3.3: La potencia se eleva al "
            "cuadrado en cada fila y el acumulado multiplica las potencias de "
            f"los bits en 1 del exponente a = {a}.",
        },
    }
    if aviso is not None:
        datos["aviso"] = aviso

    return Resultado(
        valor=str(k_alicia),
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"Los dos caminos coinciden: Bᵃ = {_potencia_txt(b_publica, a)} ≡ "
            f"{k_alicia} y Aᵇ = {_potencia_txt(a_publica, b)} ≡ {k_bob} (mod {p})"
        ),
        datos=datos,
    )


def rsa(p: int, q: int, e: int, m: int) -> Resultado:
    """3.2 · RSA completo: Claves, cifrado y descifrado de comprobación.

    n = p·q y φ(n) = (p−1)(q−1). El exponente e debe cumplir 1 < e < φ(n)
    y MCD(e, φ) = 1 (con el mcd de 1.4); d = e⁻¹ mod φ(n) sale de la tabla
    del AEE de 1.6, y las potencias c = mᵉ mod n y m = cᵈ mod n se
    calculan con la exponenciación rápida de 3.3.
    """
    p, q, e, m = int(p), int(q), int(e), int(m)
    for nombre, candidato in (("p", p), ("q", q)):
        if candidato > LIMITE_PRIMO:
            raise ValueError(
                f"Para comprobar si {nombre} es primo se divide una a una hasta su "
                f"raíz y con {nombre} = {candidato} sería lento. Usa primos de "
                "hasta 1 000 000."
            )
        if not es_primo(candidato):
            if candidato >= 4:
                divisor = _primer_divisor(candidato)
                detalle = f"{candidato} = {divisor} × {candidato // divisor}"
            else:
                detalle = f"llegó {nombre} = {candidato}"
            raise ValueError(
                f"RSA necesita que {nombre} sea primo y {detalle}. "
                "Prueba con primos como 61 y 53."
            )
    if p == q:
        raise ValueError(
            f"p y q deben ser primos distintos y llegó p = q = {p}: "
            "Con p = q la fórmula φ(n) = (p − 1)(q − 1) deja de valer."
        )
    n = p * q
    phi = (p - 1) * (q - 1)
    if not 1 < e < phi:
        raise ValueError(
            f"El exponente e debe cumplir 1 < e < φ(n) = {phi} y llegó e = {e}. "
            "Prueba con e = 17."
        )
    divisor_comun = mcd(e, phi)
    if divisor_comun != 1:
        raise ValueError(
            f"No sirve e = {e}: MCD({e}, {phi}) = {divisor_comun} y debe ser 1 "
            f"para que exista d = e⁻¹ mod φ(n). Elige un e coprimo con {phi}."
        )
    if not 0 <= m < n:
        raise ValueError(
            f"El mensaje debe cumplir 0 ≤ m < n = {n} y llegó m = {m}. "
            "Escribe el mensaje como un número menor que n."
        )

    # d = e⁻¹ mod φ(n) con el algoritmo extendido de Euclides del 1.6
    _, _, t, tabla_aee = aee(phi, e)
    d = t % phi
    rondas = len(tabla_aee) - 2

    # Cifrado y descifrado de comprobación con la exponenciación rápida del 3.3
    c, tabla_exp, mult_c = exp_rapida(m, e, n)
    descifrado, _, _ = exp_rapida(c, d, n)
    binario_e = "".join(str(fila["Bit del exponente"]) for fila in reversed(tabla_exp))

    pasos = [
        _paso(
            "Qué buscamos",
            f"Crear las claves RSA a partir de los primos p y q, cifrar el mensaje m = {m} "
            "con la clave pública y comprobar que la clave privada lo recupera.",
        ),
        _paso(
            "Comprobamos los primos",
            f"Probamos dividir {p} y {q} entre 2, 3, 5, … hasta su raíz cuadrada y ninguno "
            "los divide exacto: Los dos son primos, y son distintos.",
        ),
        _paso(
            "Calculamos n",
            f"n = p × q = {p} × {q} = {n}. Es el módulo de todas las cuentas y forma parte "
            "de la clave pública.",
        ),
        _paso(
            "Calculamos φ(n)",
            f"φ(n) = (p − 1) × (q − 1) = {p - 1} × {q - 1} = {phi}. Es el número que "
            "permite hallar la clave privada, y solo se conoce si se conocen p y q.",
        ),
        _paso(
            "Validamos e",
            f"e = {e} cumple 1 < {e} < {phi} y, con el Euclides del 1.4, MCD({e}, {phi}) = 1: "
            f"e no comparte divisores con φ(n). La clave pública es (n, e) = ({n}, {e}).",
        ),
        _paso(
            "Hallamos d",
            f"d es el inverso de e módulo φ(n). La tabla del Euclides extendido del 1.6 "
            f"({rondas} rondas) da t = {_num(t)}, y d = {_num(t)} mod {phi} = {d}. "
            f"La clave privada es d = {d}.",
        ),
        _paso(
            "Comprobamos d",
            f"{e} × {d} = {e * d} = {(e * d) // phi} × {phi} + 1: El residuo es 1, "
            "como debe ser.",
        ),
        _paso(
            "Ciframos",
            f"c = mᵉ mod n = {_potencia_txt(m, e)} mod {n} = {c}, calculado con la "
            f"exponenciación rápida del 3.3 ({mult_c} multiplicaciones).",
        ),
        _paso(
            "Comprobación",
            f"Desciframos con la clave privada: cᵈ mod n = {_potencia_txt(c, d)} mod {n} "
            f"= {descifrado}, y recuperamos m = {m}.",
        ),
    ]

    return Resultado(
        valor=str(c),
        pasos=pasos,
        tabla=tabla_exp,
        verificacion=(
            f"{_potencia_txt(c, d)} mod {n} = {descifrado}: "
            f"El descifrado recupera el mensaje m = {m}"
        ),
        datos={
            "etiqueta": f"Cifrado RSA de m = {m}",
            "chips": [
                f"{e} × {d} ≡ 1 (mod {phi})",
                f"d en {rondas} rondas del AEE",
                f"descifrado: {descifrado} = m",
            ],
            "metricas": [
                ("n = p × q", n),
                ("φ(n)", phi),
                ("d = e⁻¹ mod φ(n)", d),
            ],
            "n": n,
            "phi": phi,
            "d": d,
            "c": c,
            "descifrado": descifrado,
            "t": t,
            "rondas": rondas,
            "nota_tabla": f"La tabla de la exponenciación rápida (3.3) para el "
            f"cifrado c = {_potencia_txt(m, e)} mod {n}: El exponente e = {e} en "
            f"binario es {binario_e} y solo se multiplican las potencias de sus "
            "bits en 1.",
            "tabla_extra": {
                "titulo": f"Tabla del AEE (1.6) para d = e⁻¹ mod φ(n) = {d}",
                "filas": tabla_aee,
                "nota": f"La misma tabla del submenú 1.6 con n = φ(n) = {phi} y "
                f"a = e = {e}: El inverso es el t de la fila con residuo r = 1, "
                f"t = {t}, y {t} mod {phi} = {d}.",
            },
        },
    )


def exponenciacion_rapida(base: int, exponente: int, n: int) -> Resultado:
    """3.3 · bᵉ mod n con la tabla de cuadrados sucesivos.

    El exponente se escribe en binario y solo se multiplican las potencias
    de los bits en 1: En vez de las e − 1 multiplicaciones del método
    directo se hacen unas pocas.
    """
    base, exponente, n = int(base), int(exponente), int(n)
    resultado, tabla, multiplicaciones = exp_rapida(base, exponente, n)

    base_reducida = base % n
    binario = "".join(str(fila["Bit del exponente"]) for fila in reversed(tabla))
    cuadrados = len(tabla) - 1
    productos = multiplicaciones - cuadrados
    potencia_txt = _potencia_txt(base_reducida, exponente)
    pasos = [
        _paso(
            "Qué buscamos",
            f"{_potencia_txt(base, exponente)} mod {n}: El residuo de esa potencia al "
            f"dividirla entre {n}, sin multiplicar {base} por sí mismo {exponente - 1} veces.",
        )
    ]
    if base_reducida != base:
        pasos.append(
            _paso(
                "Reducimos la base",
                f"{base} mod {n} = {base_reducida}: Trabajar con {base_reducida} da el mismo "
                "residuo y números más pequeños.",
            )
        )
    pasos.extend(
        [
            _paso(
                "El exponente en binario",
                f"{exponente} = {binario}₂, con {len(tabla)} bits. Lo leemos de derecha a "
                "izquierda (i = 0, 1, 2, …): Cada bit dice si hay que usar la potencia de esa fila.",
            ),
            _paso(
                "Cómo funciona",
                f"Empezamos con la potencia {base_reducida}. En cada fila la elevamos al "
                f"cuadrado y tomamos mod {n}: Así conseguimos {base_reducida}¹, "
                f"{base_reducida}², {base_reducida}⁴, {base_reducida}⁸… Cuando el bit vale 1, "
                "multiplicamos esa potencia al acumulado (que empieza en 1); cuando vale 0, "
                "el acumulado no cambia.",
            ),
        ]
    )
    frases = []
    for i, fila in enumerate(tabla):
        bit = fila["Bit del exponente"]
        potencia_fila = fila["Potencia al cuadrado"]
        if i == 0:
            frase = f"La potencia empieza en {base_reducida}."
        else:
            anterior = tabla[i - 1]["Potencia al cuadrado"]
            cuadrado = anterior * anterior
            frase = f"Potencia = {anterior}² = {cuadrado}, y {cuadrado} mod {n} = {potencia_fila}."
        if bit == 1:
            previo = 1 if i == 0 else tabla[i - 1]["Acumulado"]
            producto = previo * potencia_fila
            frase += (
                f" El bit es 1: acumulado = {previo} × {potencia_fila} = {producto}, "
                f"y {producto} mod {n} = {fila['Acumulado']}."
            )
        else:
            frase += f" El bit es 0: El acumulado sigue en {fila['Acumulado']}."
        frases.append(_paso(f"Bit i = {i}, vale {bit}", frase))
    if len(frases) > 12:
        frases = (
            frases[:10]
            + [_paso("Seguimos igual", f"Con los {len(tabla) - 11} bits restantes; la tabla los muestra todos.")]
            + [frases[-1]]
        )
    pasos.extend(frases)
    pasos.append(
        _paso("Resultado", f"El acumulado final es la respuesta: {potencia_txt} mod {n} = {resultado}.")
    )
    pasos.append(
        _paso(
            "Cuántas cuentas",
            f"{multiplicaciones} multiplicaciones ({cuadrados} al cuadrado y {productos} por "
            f"bits en 1); el método directo haría {exponente - 1}.",
        )
    )

    # Comprobación por un camino distinto: multiplicar la base una y otra vez,
    # reduciendo módulo n en cada paso (solo si el exponente lo permite)
    if exponente <= 100_000:
        directo = 1
        for _ in range(exponente):
            directo = directo * base_reducida % n
        if exponente <= 64 and len(str(base_reducida)) * exponente <= 18:
            completa = base_reducida**exponente
            verificacion = (
                f"Método directo: {potencia_txt} = {completa} y "
                f"{completa} mod {n} = {directo}"
            )
        else:
            verificacion = (
                f"Método directo: Multiplicar {base_reducida} por sí mismo "
                f"{exponente} veces, reduciendo módulo {n}, también da {directo}"
            )
    else:
        verificacion = (
            f"El resultado multiplica módulo {n} las potencias de los bits en 1 "
            f"del exponente {binario}₂"
        )

    return Resultado(
        valor=str(resultado),
        pasos=pasos,
        tabla=tabla,
        verificacion=verificacion,
        datos={
            "etiqueta": f"{potencia_txt} mod {n}",
            "chips": [
                f"e = {binario}₂",
                f"{multiplicaciones} multiplicaciones",
                f"método directo: {exponente - 1}",
            ],
            "resultado": resultado,
            "binario": binario,
            "multiplicaciones": multiplicaciones,
            "nota_tabla": f"El exponente en binario es {binario}: La tabla lo "
            "recorre al revés, del bit i = 0 (el de la derecha) al de la "
            "izquierda. La potencia se eleva al cuadrado en cada fila y el "
            "acumulado solo cambia cuando el bit es 1.",
        },
    )


# ======================================================================
# Hash (fase 5)
# ======================================================================

# Los tres submenús del módulo 4 son la misma operación con distinto
# algoritmo, y el módulo 6 reutiliza estos algoritmos para el salt.
_ALGORITMOS_HASH = {"MD5": hashlib.md5, "SHA-256": hashlib.sha256, "SHA-512": hashlib.sha512}

# Tamaño del bloque interno que procesa cada algoritmo, para el paso a paso
_BITS_BLOQUE = {"MD5": 512, "SHA-256": 512, "SHA-512": 1024}

# Cuántos dígitos hexadecimales tiene el hash de cada algoritmo
_DIGITOS_HASH = {"MD5": 32, "SHA-256": 64, "SHA-512": 128}


def _validar_algoritmo(algoritmo) -> str:
    """Devuelve el nombre estándar del algoritmo: MD5, SHA-256 o SHA-512."""
    nombre = str(algoritmo).strip().upper().replace("SHA256", "SHA-256").replace("SHA512", "SHA-512")
    if nombre not in _ALGORITMOS_HASH:
        raise ValueError(
            f"El algoritmo '{algoritmo}' no está en la calculadora. "
            "Usa MD5, SHA-256 o SHA-512."
        )
    return nombre


def _hash_hex(texto: str, nombre: str) -> str:
    """Hash de un texto en UTF-8, escrito en hexadecimal en minúsculas."""
    return _ALGORITMOS_HASH[nombre](str(texto).encode("utf-8")).hexdigest()


def hash_texto(texto: str, algoritmo: str, comparar: str = "") -> Resultado:
    """4.1, 4.2 y 4.3 · Hash de un texto en UTF-8 con MD5, SHA-256 o SHA-512.

    Muestra el hash en hexadecimal y su longitud en bits. Si llega un
    segundo texto en `comparar`, calcula los dos hashes y cuenta cuántos
    caracteres cambian entre ellos: Es el efecto avalancha, por el que un
    cambio mínimo en la entrada transforma el hash por completo.
    """
    nombre = _validar_algoritmo(algoritmo)
    if str(texto) == "":
        raise ValueError("El texto está vacío. Escribe el texto al que quieres calcular el hash.")
    octetos = str(texto).encode("utf-8")
    resumen = _hash_hex(texto, nombre)
    bits = len(resumen) * 4

    pasos = [
        _paso(
            "Qué hacemos",
            f"Calcular la huella {nombre} del texto: Un resumen de tamaño fijo que cambia "
            "por completo si el texto cambia en algo, y desde el que no se puede volver "
            "al texto.",
        ),
        _paso(
            "El texto en bytes",
            f"En UTF-8, «{texto}» ocupa {len(octetos)} bytes (en hexadecimal): "
            f"{_listado_bytes(octetos)}.",
        ),
        _paso(
            "El algoritmo mezcla los bytes",
            f"{nombre} completa los bytes hasta un bloque de {_BITS_BLOQUE[nombre]} bits y "
            "los pasa por muchas rondas de sumas, rotaciones y operaciones lógicas; el "
            "estado final de esa mezcla es la huella.",
        ),
        _paso(
            "La huella",
            f"Mide {bits} bits y se escribe con {len(resumen)} dígitos hexadecimales "
            f"(cada dígito son 4 bits): {nombre}(«{_abreviar(str(texto))}») = {resumen}.",
        ),
    ]
    chips = [nombre, f"{bits} bits", f"{len(resumen)} dígitos hex"]
    verificacion = f"Mismo texto, mismo hash: {nombre} de «{_abreviar(str(texto))}» siempre da esta huella"
    datos = {
        "etiqueta": f"{nombre} de «{_abreviar(str(texto))}»",
        "chips": chips,
        "codigo": resumen,
        "bits": bits,
    }

    if str(comparar) != "":
        resumen_2 = _hash_hex(comparar, nombre)
        cambios = sum(1 for x, y in zip(resumen, resumen_2) if x != y)
        porcentaje = round(100 * cambios / len(resumen))
        marcas = "".join("^" if x != y else " " for x, y in zip(resumen, resumen_2))
        pasos.append(
            _paso("Segundo texto", f"Calculamos también {nombre}(«{_abreviar(str(comparar))}») = {resumen_2}.")
        )
        if str(comparar) == str(texto):
            pasos.append(
                _paso("Comparamos", "Los dos textos son idénticos, así que los hashes coinciden carácter a carácter.")
            )
            verificacion = "Los dos textos son iguales y sus hashes coinciden carácter a carácter"
            datos["aviso"] = (
                "Los dos textos son iguales, así que los hashes coinciden. Cambia "
                "una sola letra del segundo texto para ver el efecto avalancha."
            )
        else:
            pasos.append(
                _paso(
                    "Efecto avalancha",
                    f"Comparamos los dos hashes posición por posición: Cambian {cambios} de "
                    f"{len(resumen)} caracteres ({porcentaje} %). Un cambio mínimo en el texto "
                    "cambia casi toda la huella.",
                )
            )
            verificacion = (
                f"Efecto avalancha: Con dos textos distintos cambian "
                f"{cambios} de {len(resumen)} caracteres del hash"
            )
        chips.append(f"cambian {cambios} de {len(resumen)}")
        datos["cambios"] = cambios
        datos["alineado"] = f"Texto 1: {resumen}\nTexto 2: {resumen_2}\n         {marcas}"
        datos["nota_tabla"] = (
            "Cada ^ marca una posición donde los dos hashes difieren: Aunque los "
            "textos se parezcan, los hashes no se parecen en nada."
        )
        datos["metricas"] = [
            ("Caracteres que cambian", f"{cambios} de {len(resumen)}"),
            ("Porcentaje del hash", f"{porcentaje} %"),
            ("Longitud del hash", f"{bits} bits"),
        ]

    pasos.append(
        _paso(
            "Comprobación",
            f"Calcular {nombre} de «{_abreviar(str(texto))}» otra vez da exactamente la misma "
            "huella: El hash no tiene nada de azar.",
        )
    )
    return Resultado(valor=resumen, pasos=pasos, verificacion=verificacion, datos=datos)


# ======================================================================
# Codificación (fase 5)
# ======================================================================

# Los cuatro submenús del módulo 5 se comportan como los cifradores del
# módulo 2: reciben `modo` ("codificar" o "decodificar") y dejan en
# datos["verificar"] la receta de la operación inversa para el botón
# "Verificar". Todos trabajan sobre los bytes UTF-8 del texto.

# Alfabeto estándar de Base64: 64 caracteres, cada uno vale 6 bits
_ALFABETO_B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def _validar_modo_codificacion(modo) -> str:
    """Normaliza el modo de los codificadores a 'codificar' o 'decodificar'."""
    nombre = str(modo).strip().lower()
    if nombre not in ("codificar", "decodificar"):
        raise ValueError(
            f"El modo '{modo}' no existe en los codificadores. "
            "Usa 'codificar' o 'decodificar'."
        )
    return nombre


def _mostrar_caracter(caracter: str) -> str:
    """El espacio se escribe como palabra para que se vea en las tablas."""
    return "(espacio)" if caracter == " " else caracter


def _tabla_bytes(texto: str) -> list[dict]:
    """Una fila por byte UTF-8: Carácter, decimal, hexadecimal y binario.
    La ñ, las tildes y la ü ocupan 2 bytes y por eso llenan 2 filas."""
    filas = []
    for caracter in str(texto):
        octetos = caracter.encode("utf-8")
        for posicion, octeto in enumerate(octetos, start=1):
            visible = _mostrar_caracter(caracter)
            if len(octetos) > 1:
                visible = f"{visible} (byte {posicion} de {len(octetos)})"
            filas.append(
                {
                    "Carácter": visible,
                    "Decimal": octeto,
                    "Hexadecimal": f"{octeto:02X}",
                    "Binario": f"{octeto:08b}",
                }
            )
    return filas


def _receta_codificacion(funcion: str, nombre_modo: str, texto_plano: str, codificado: str) -> dict:
    """Receta del botón "Verificar": Aplicar la operación inversa debe
    devolver exactamente lo que se tenía antes."""
    if nombre_modo == "codificar":
        return {
            "funcion": funcion,
            "entradas": {"texto": codificado, "modo": "decodificar"},
            "esperado": texto_plano,
            "descripcion": f"decodificar «{_abreviar(codificado, 24)}»",
        }
    return {
        "funcion": funcion,
        "entradas": {"texto": texto_plano, "modo": "codificar"},
        "esperado": codificado,
        "descripcion": f"codificar «{_abreviar(texto_plano, 24)}»",
    }


def _aviso_no_ascii(texto_plano: str) -> str | None:
    """Arma el aviso del submenú 5.1 cuando el texto sale de la tabla ASCII."""
    fuera, vistos = [], set()
    for caracter in texto_plano:
        if ord(caracter) > 127 and caracter not in vistos:
            vistos.add(caracter)
            octetos = " ".join(str(octeto) for octeto in caracter.encode("utf-8"))
            fuera.append(f"«{caracter}» (bytes UTF-8: {octetos})")
    if not fuera:
        return None
    return (
        "La tabla ASCII solo llega al código 127 y el texto trae "
        + ", ".join(fuera)
        + ". Esos caracteres se representan con sus bytes UTF-8."
    )


def codificacion_ascii(texto: str, modo: str = "codificar") -> Resultado:
    """5.1 · ASCII: Cada carácter se cambia por su código decimal (0 a 127).

    Los códigos van separados por espacio. Si el texto trae caracteres
    fuera de ASCII (ñ, tildes, ü), se muestran sus bytes UTF-8 y se avisa.
    Al decodificar se validan los números y que los bytes formen texto.
    """
    nombre_modo = _validar_modo_codificacion(modo)

    if nombre_modo == "codificar":
        if str(texto) == "":
            raise ValueError("El texto está vacío. Escribe el texto que quieres codificar.")
        texto_plano = str(texto)
        octetos = texto_plano.encode("utf-8")
    else:
        partes = str(texto).split()
        if not partes:
            raise ValueError(
                "La entrada está vacía. Pega los códigos decimales separados "
                "por espacio, por ejemplo: 72 111 108 97."
            )
        valores = []
        for parte in partes:
            try:
                numero = int(parte)
            except ValueError:
                raise ValueError(
                    f"«{parte}» no es un número entero. Escribe códigos decimales "
                    "separados por espacio, por ejemplo: 72 111 108 97."
                ) from None
            if not 0 <= numero <= 255:
                raise ValueError(
                    f"El código {numero} está fuera de rango: Cada byte va de 0 a 255 "
                    "(y el ASCII estricto, de 0 a 127)."
                )
            valores.append(numero)
        octetos = bytes(valores)
        try:
            texto_plano = octetos.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                "Esos códigos no forman texto UTF-8 válido. Revisa que sean "
                "exactamente los que salieron al codificar."
            ) from None

    codificado = " ".join(str(octeto) for octeto in octetos)
    primer = texto_plano[0]
    bytes_primer = " ".join(str(octeto) for octeto in primer.encode("utf-8"))
    caracteres = list(texto_plano)
    muestras = ", ".join(
        f"«{_mostrar_caracter(c)}» = {' '.join(str(o) for o in c.encode('utf-8'))}"
        for c in caracteres[:12]
    )
    if len(caracteres) > 12:
        muestras += (
            f" … y así con los {len(caracteres) - 12} caracteres restantes "
            "(la tabla los muestra todos)"
        )

    if nombre_modo == "codificar":
        pasos = [
            _paso(
                "Qué hacemos",
                "Cada carácter tiene un número en la tabla ASCII (del 0 al 127): La A es 65, "
                "la a es 97, el espacio es 32. Escribimos ese número en decimal.",
            ),
            _paso("Buscamos cada carácter en la tabla", f"{muestras}."),
            _paso("Resultado", f"Los códigos separados por un espacio: {codificado}."),
            _paso(
                "Comprobación",
                f"Cada código vuelve a su carácter ({bytes_primer} → «{_mostrar_caracter(primer)}» …) "
                f"y se recupera «{texto_plano}».",
            ),
        ]
        valor, etiqueta = codificado, f"«{_abreviar(texto_plano)}» en ASCII decimal"
    else:
        pasos = [
            _paso(
                "Qué hacemos",
                "Cada número es el código ASCII de un carácter: Buscamos en la tabla a qué "
                "carácter corresponde y los juntamos.",
            ),
            _paso("Leemos los números", f"Separados por espacio hay {len(octetos)} códigos: {codificado}."),
            _paso("Cada código vuelve a ser su carácter", f"{muestras}."),
            _paso("Resultado", f"Juntamos los caracteres: «{texto_plano}»."),
            _paso("Comprobación", f"Codificar «{texto_plano}» devuelve {codificado}."),
        ]
        valor, etiqueta = texto_plano, "Texto decodificado de ASCII"

    datos = {
        "etiqueta": etiqueta,
        "chips": [f"{len(texto_plano)} caracteres", f"{len(octetos)} bytes", "ASCII 0–127"],
        "nota_tabla": (
            "La columna Decimal es el código de cada byte. Hasta 127 es ASCII "
            "puro; de 128 en adelante son bytes UTF-8 de caracteres como la ñ."
        ),
        "verificar": _receta_codificacion("codificacion_ascii", nombre_modo, texto_plano, codificado),
    }
    if nombre_modo == "codificar":
        datos["codigo"] = codificado
    if aviso := _aviso_no_ascii(texto_plano):
        datos["aviso"] = aviso
        pasos.insert(2, _paso("Fuera de ASCII", aviso))

    return Resultado(
        valor=valor,
        pasos=pasos,
        tabla=_tabla_bytes(texto_plano),
        verificacion=f"«{_mostrar_caracter(primer)}» ↔ {bytes_primer}: La ida y la vuelta coinciden",
        datos=datos,
    )


def codificacion_hexadecimal(texto: str, modo: str = "codificar") -> Resultado:
    """5.2 · Hexadecimal: Cada byte UTF-8 se escribe con dos dígitos (00 a FF)."""
    nombre_modo = _validar_modo_codificacion(modo)

    if nombre_modo == "codificar":
        if str(texto) == "":
            raise ValueError("El texto está vacío. Escribe el texto que quieres codificar.")
        texto_plano = str(texto)
        octetos = texto_plano.encode("utf-8")
    else:
        limpio = str(texto).replace(" ", "").strip().upper()
        if limpio == "":
            raise ValueError(
                "La entrada está vacía. Pega el texto en hexadecimal, por ejemplo: 486F6C61."
            )
        if any(digito not in _HEX for digito in limpio):
            raise ValueError(
                f"«{texto}» no es hexadecimal válido. Usa dígitos del 0 al 9 "
                "y letras de la A a la F."
            )
        if len(limpio) % 2 != 0:
            raise ValueError(
                f"La entrada tiene {len(limpio)} dígitos hexadecimales y deben "
                "ser pares: Cada byte son dos dígitos."
            )
        octetos = bytes.fromhex(limpio)
        try:
            texto_plano = octetos.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                "Esos bytes no forman texto UTF-8 válido. Revisa que sea el "
                "hexadecimal que salió al codificar."
            ) from None

    codificado = octetos.hex().upper()
    primer = texto_plano[0]
    hex_primer = primer.encode("utf-8").hex().upper()

    primero = octetos[0]
    conversion = (
        f"{primero} = {primero // 16} × 16 + {primero % 16}, y esos dos números escritos "
        f"como dígitos hexadecimales son {primero // 16:X} y {primero % 16:X}: {primero:02X}"
    )
    listado = _listado_bytes(octetos)
    if nombre_modo == "codificar":
        pasos = [
            _paso(
                "Qué hacemos",
                "Hexadecimal es contar en base 16, con los dígitos 0 a 9 y las letras A a F "
                "(A vale 10, F vale 15). Cada byte del texto, un número de 0 a 255, se "
                "escribe con exactamente dos dígitos hexadecimales, de 00 a FF.",
            ),
            _paso(
                "El texto en bytes",
                f"En UTF-8, «{texto_plano}» ocupa {len(octetos)} bytes; en decimal: "
                f"{' '.join(str(octeto) for octeto in octetos)}.",
            ),
            _paso(
                "Cada byte a dos dígitos",
                f"Por ejemplo «{_mostrar_caracter(primer)}»: {conversion}. Todos: {listado}.",
            ),
            _paso("Resultado", f"Juntamos las parejas de dígitos: {codificado}."),
            _paso(
                "Comprobación",
                f"Leyendo las parejas al revés ({codificado[:2]} → {primero} → "
                f"«{_mostrar_caracter(primer)}» …) se recupera «{texto_plano}».",
            ),
        ]
        valor, etiqueta = codificado, f"«{_abreviar(texto_plano)}» en hexadecimal"
    else:
        pasos = [
            _paso(
                "Qué hacemos",
                "Cada pareja de dígitos hexadecimales es un byte, un número de 0 a 255 "
                "(los dígitos van del 0 al 9 y de A = 10 a F = 15). Convertimos las parejas "
                "y leemos los bytes como texto UTF-8.",
            ),
            _paso("Partimos en parejas", f"{len(octetos)} bytes: {listado}."),
            _paso(
                "Cada pareja a decimal",
                f"Por ejemplo {codificado[:2]}: {primero // 16} × 16 + {primero % 16} = {primero}, "
                f"que es «{_mostrar_caracter(primer)}».",
            ),
            _paso("Resultado", f"Interpretamos los bytes como texto UTF-8: «{texto_plano}»."),
            _paso("Comprobación", f"Codificar «{texto_plano}» devuelve {codificado}."),
        ]
        valor, etiqueta = texto_plano, "Texto decodificado de hexadecimal"

    datos = {
        "etiqueta": etiqueta,
        "chips": [f"{len(octetos)} bytes", "1 byte = 2 dígitos hex", f"{len(codificado)} dígitos"],
        "nota_tabla": (
            "Cada fila es un byte del texto en UTF-8: El mismo valor escrito "
            "en decimal, en hexadecimal y en binario."
        ),
        "verificar": _receta_codificacion(
            "codificacion_hexadecimal", nombre_modo, texto_plano, codificado
        ),
    }
    if nombre_modo == "codificar":
        datos["codigo"] = codificado

    return Resultado(
        valor=valor,
        pasos=pasos,
        tabla=_tabla_bytes(texto_plano),
        verificacion=f"«{_mostrar_caracter(primer)}» ↔ {hex_primer}: La ida y la vuelta coinciden",
        datos=datos,
    )


def codificacion_binaria(texto: str, modo: str = "codificar") -> Resultado:
    """5.3 · Binario: Cada byte UTF-8 se escribe con sus 8 bits."""
    nombre_modo = _validar_modo_codificacion(modo)

    if nombre_modo == "codificar":
        if str(texto) == "":
            raise ValueError("El texto está vacío. Escribe el texto que quieres codificar.")
        texto_plano = str(texto)
        octetos = texto_plano.encode("utf-8")
    else:
        limpio = str(texto).replace(" ", "").strip()
        if limpio == "":
            raise ValueError(
                "La entrada está vacía. Pega el texto en binario, por ejemplo: 01001000 01101111."
            )
        if any(bit not in "01" for bit in limpio):
            raise ValueError(
                f"«{_abreviar(str(texto), 24)}» no es binario válido: Usa solo ceros y unos "
                "(los espacios entre bytes sí se permiten)."
            )
        if len(limpio) % 8 != 0:
            raise ValueError(
                f"La entrada tiene {len(limpio)} bits y deben ser múltiplo de 8: "
                "Cada byte son exactamente 8 bits."
            )
        octetos = bytes(int(limpio[i : i + 8], 2) for i in range(0, len(limpio), 8))
        try:
            texto_plano = octetos.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                "Esos bits no forman texto UTF-8 válido. Revisa que sea el "
                "binario que salió al codificar."
            ) from None

    codificado = " ".join(f"{octeto:08b}" for octeto in octetos)
    primer = texto_plano[0]

    primero = octetos[0]
    bits_primero = f"{primero:08b}"
    suma = " + ".join(
        str(valor_bit)
        for valor_bit, bit in zip((128, 64, 32, 16, 8, 4, 2, 1), bits_primero)
        if bit == "1"
    ) or "0"
    filas_bytes = _tabla_bytes(texto_plano)
    listado = ", ".join(f"«{fila['Carácter']}» = {fila['Binario']}" for fila in filas_bytes[:12])
    if len(filas_bytes) > 12:
        listado += f" … y {len(filas_bytes) - 12} bytes más (la tabla los muestra todos)"
    if nombre_modo == "codificar":
        pasos = [
            _paso(
                "Qué hacemos",
                "El computador guarda cada carácter como un byte: 8 bits, y cada bit es un "
                "0 o un 1. Escribimos los 8 bits de cada byte del texto.",
            ),
            _paso(
                "El texto en bytes",
                f"En UTF-8, «{texto_plano}» ocupa {len(octetos)} bytes; en decimal: "
                f"{' '.join(str(octeto) for octeto in octetos)}.",
            ),
            _paso(
                "Cada byte a 8 bits",
                "Los bits valen 128, 64, 32, 16, 8, 4, 2 y 1, de izquierda a derecha, y se "
                f"pone un 1 en cada valor que hace falta sumar. Por ejemplo {primero} = {suma}, "
                f"que se escribe {bits_primero}. Todos: {listado}.",
            ),
            _paso("Resultado", f"Los bytes separados por un espacio para poder leerlos: {codificado}."),
            _paso(
                "Comprobación",
                f"Sumando los valores de los bits en 1 de cada grupo se recuperan los bytes "
                f"({bits_primero} → {primero} → «{_mostrar_caracter(primer)}» …) y el texto «{texto_plano}».",
            ),
        ]
        valor, etiqueta = codificado, f"«{_abreviar(texto_plano)}» en binario"
    else:
        pasos = [
            _paso(
                "Qué hacemos",
                "Cada grupo de 8 bits es un byte. Sumamos los valores de los bits en 1 "
                "(128, 64, 32, 16, 8, 4, 2 y 1, de izquierda a derecha) y leemos los bytes "
                "como texto UTF-8.",
            ),
            _paso(
                "Partimos en grupos de 8",
                f"Sin los espacios quedan {8 * len(octetos)} bits, es decir {len(octetos)} bytes.",
            ),
            _paso(
                "Cada grupo a decimal",
                f"Por ejemplo {bits_primero} = {suma} = {primero}, que es "
                f"«{_mostrar_caracter(primer)}». Todos: {listado}.",
            ),
            _paso("Resultado", f"Interpretamos los bytes como texto UTF-8: «{texto_plano}»."),
            _paso("Comprobación", f"Codificar «{texto_plano}» devuelve {codificado}."),
        ]
        valor, etiqueta = texto_plano, "Texto decodificado de binario"

    datos = {
        "etiqueta": etiqueta,
        "chips": [f"{len(octetos)} bytes", "8 bits por byte", f"{8 * len(octetos)} bits"],
        "nota_tabla": (
            "Cada fila es un byte del texto en UTF-8: El mismo valor escrito "
            "en decimal, en hexadecimal y en binario."
        ),
        "verificar": _receta_codificacion(
            "codificacion_binaria", nombre_modo, texto_plano, codificado
        ),
    }
    if nombre_modo == "codificar":
        datos["codigo"] = codificado

    return Resultado(
        valor=valor,
        pasos=pasos,
        tabla=_tabla_bytes(texto_plano),
        verificacion=f"«{_mostrar_caracter(primer)}» ↔ {octetos[0]:08b}: La ida y la vuelta coinciden",
        datos=datos,
    )


def codificacion_base64(texto: str, modo: str = "codificar") -> Resultado:
    """5.4 · Base64: Los bits del texto se leen en grupos de 6 y cada grupo
    elige un carácter de un alfabeto de 64.

    Como 6 bits dan valores de 0 a 63, cada carácter Base64 guarda 6 bits.
    El relleno con «=» completa el último bloque de 4 caracteres; por eso
    un Base64 válido siempre mide un múltiplo de 4.
    """
    nombre_modo = _validar_modo_codificacion(modo)

    if nombre_modo == "codificar":
        if str(texto) == "":
            raise ValueError("El texto está vacío. Escribe el texto que quieres codificar.")
        texto_plano = str(texto)
        octetos = texto_plano.encode("utf-8")
    else:
        limpio = str(texto).replace(" ", "").strip()
        if limpio == "":
            raise ValueError(
                "La entrada está vacía. Pega el texto en Base64, por ejemplo: SG9sYQ==."
            )
        cuerpo = limpio.rstrip("=")
        if any(caracter not in _ALFABETO_B64 for caracter in cuerpo):
            invalido = next(c for c in cuerpo if c not in _ALFABETO_B64)
            raise ValueError(
                f"El carácter «{invalido}» no pertenece al alfabeto Base64 "
                "(A–Z, a–z, 0–9, + y /, con = solo como relleno final)."
            )
        if len(limpio) - len(cuerpo) > 2:
            raise ValueError("El relleno con «=» puede ser de máximo 2 caracteres, al final.")
        if len(limpio) % 4 != 0:
            raise ValueError(
                f"Un Base64 válido mide un múltiplo de 4 caracteres y este mide "
                f"{len(limpio)}. ¿Faltan los «=» de relleno?"
            )
        try:
            octetos = base64.b64decode(limpio, validate=True)
        except ValueError:
            raise ValueError(
                f"«{_abreviar(limpio, 24)}» no es Base64 válido. Revisa que sea "
                "el texto que salió al codificar."
            ) from None
        try:
            texto_plano = octetos.decode("utf-8")
        except UnicodeDecodeError:
            raise ValueError(
                "Esos bytes no forman texto UTF-8 válido. Revisa que sea el "
                "Base64 que salió al codificar."
            ) from None

    codificado = base64.b64encode(octetos).decode("ascii")

    # La tabla reconstruye el Base64 a mano: bits seguidos, grupos de 6 y
    # el carácter del alfabeto que corresponde a cada grupo
    bits = "".join(f"{octeto:08b}" for octeto in octetos)
    sobran = (6 - len(bits) % 6) % 6
    bits_completos = bits + "0" * sobran
    grupos = [bits_completos[i : i + 6] for i in range(0, len(bits_completos), 6)]
    relleno = codificado.count("=")
    # La columna Decimal va como texto porque las filas de relleno llevan "—"
    # y st.dataframe necesita columnas de un solo tipo
    tabla = [
        {"Grupo de 6 bits": grupo, "Decimal": str(int(grupo, 2)), "Carácter Base64": _ALFABETO_B64[int(grupo, 2)]}
        for grupo in grupos
    ]
    tabla.extend({"Grupo de 6 bits": "(relleno)", "Decimal": "—", "Carácter Base64": "="} for _ in range(relleno))

    bits_por_byte = " ".join(f"{octeto:08b}" for octeto in octetos[:12]) + (" …" if len(octetos) > 12 else "")
    grupos_txt = " ".join(grupos[:16]) + (" …" if len(grupos) > 16 else "")
    eleccion = ", ".join(
        f"{grupo} = {int(grupo, 2)} → «{_ALFABETO_B64[int(grupo, 2)]}»" for grupo in grupos[:12]
    )
    if len(grupos) > 12:
        eleccion += f" … y así con los {len(grupos) - 12} grupos restantes (la tabla los muestra todos)"
    codificando = nombre_modo == "codificar"
    pasos = [
        _paso(
            "Qué hacemos",
            "Base64 escribe cualquier secuencia de bytes usando solo 64 caracteres (A–Z, "
            "a–z, 0–9, + y /). Toma los bits de 6 en 6 y cada grupo de 6 bits, leído como un "
            "número de 0 a 63, elige un carácter."
            + ("" if codificando else " Al decodificar se hace ese camino al revés."),
        ),
        _paso(
            "El texto en bits",
            f"En UTF-8, «{texto_plano}» ocupa {len(octetos)} bytes, es decir {len(bits)} bits: "
            f"{bits_por_byte}.",
        ),
        _paso(
            "Partimos en grupos de 6",
            f"Escribimos los bits seguidos y los cortamos de 6 en 6: {grupos_txt} "
            f"({len(grupos)} grupos"
            + (f"; los últimos {sobran} bits se completan con ceros)." if sobran else ")."),
        ),
        _paso("Cada grupo elige un carácter", f"{eleccion}."),
        _paso(
            "Relleno",
            f"Los caracteres van en bloques de 4; faltan {relleno} y se completan con «=»."
            if relleno
            else "Los grupos completan bloques exactos de 4 caracteres, así que no hace falta relleno con «=».",
        ),
        _paso(
            "Resultado",
            f"{codificado}." if codificando else f"Deshaciendo el camino, los bytes vuelven a ser «{texto_plano}».",
        ),
        _paso(
            "Comprobación",
            f"Decodificar {codificado} devuelve «{texto_plano}»."
            if codificando
            else f"Codificar «{texto_plano}» devuelve {codificado}.",
        ),
    ]

    if nombre_modo == "codificar":
        valor, etiqueta = codificado, f"«{_abreviar(texto_plano)}» en Base64"
    else:
        valor, etiqueta = texto_plano, "Texto decodificado de Base64"

    datos = {
        "etiqueta": etiqueta,
        "chips": [
            f"{len(octetos)} bytes → {len(grupos)} grupos de 6 bits",
            f"relleno: {'=' * relleno if relleno else 'ninguno'}",
            "alfabeto de 64",
        ],
        "nota_tabla": (
            "Cada carácter Base64 guarda 6 bits. Las filas de relleno «=» no "
            "llevan bits: Solo completan el bloque de 4 caracteres."
        ),
        "tabla_extra": {
            "titulo": "Los bytes del texto, bit a bit",
            "filas": _tabla_bytes(texto_plano),
            "nota": "De aquí salen los bits que arriba se agrupan de 6 en 6.",
        },
        "verificar": _receta_codificacion(
            "codificacion_base64", nombre_modo, texto_plano, codificado
        ),
    }
    if nombre_modo == "codificar":
        datos["codigo"] = codificado

    return Resultado(
        valor=valor,
        pasos=pasos,
        tabla=tabla,
        verificacion=(
            f"{grupos[0]} = {int(grupos[0], 2)} = «{_ALFABETO_B64[int(grupos[0], 2)]}»: "
            "Cada carácter Base64 guarda exactamente 6 bits"
        ),
        datos=datos,
    )


# ======================================================================
# Salt (fase 5)
# ======================================================================

# El módulo 6 reutiliza los algoritmos del módulo 4 con la fórmula
# hash = algoritmo(salt + clave): el salt se pega delante de la clave.


def _hash_con_salt(clave: str, salt: str, nombre: str) -> str:
    """La fórmula del módulo 6: Hash hexadecimal de salt + clave."""
    return _hash_hex(str(salt) + str(clave), nombre)


def generar_salts(clave: str, algoritmo: str, cantidad: int) -> Resultado:
    """6.1, 6.2 y 6.3 · Genera salts aleatorios y el hash de salt + clave.

    Cada salt sale de secrets.token_hex(8): 8 bytes aleatorios seguros,
    escritos como 16 dígitos hexadecimales. Aunque la clave es la misma en
    todas las filas, cada hash es completamente distinto: Eso impide saber
    si dos usuarios comparten clave y anula las tablas de hashes
    precalculados.
    """
    nombre = _validar_algoritmo(algoritmo)
    if str(clave) == "":
        raise ValueError("La clave está vacía. Escribe la clave que quieres proteger con salt.")
    cantidad = int(cantidad)
    if not 1 <= cantidad <= 10:
        raise ValueError(f"La cantidad de salts debe estar entre 1 y 10, y pediste {cantidad}.")

    salts = [secrets.token_hex(8) for _ in range(cantidad)]
    hashes = [_hash_con_salt(clave, salt, nombre) for salt in salts]
    distintos = len(set(hashes)) == cantidad
    tabla = [
        {"N.º": posicion, "Salt": salt, f"Hash {nombre}(salt + clave)": hash_hex}
        for posicion, (salt, hash_hex) in enumerate(zip(salts, hashes), start=1)
    ]

    pasos = [
        _paso(
            "Qué hacemos",
            f"Guardar la clave «{clave}» sin guardar la clave: Se guarda "
            f"hash = {nombre}(salt + clave), donde el salt es un valor aleatorio distinto "
            "para cada usuario y el hash es una huella de la que no se puede volver atrás.",
        ),
        _paso(
            "Generamos los salts",
            f"{_plural(cantidad, 'salt', 'salts')} con secrets.token_hex(8): 8 bytes aleatorios seguros, "
            f"escritos como 16 dígitos hexadecimales. Salt 1: {salts[0]}.",
        ),
        _paso("Pegamos salt y clave", f"«{salts[0]}» + «{clave}» = «{salts[0] + str(clave)}»."),
        _paso("Calculamos el hash", f"{nombre}(«{salts[0] + str(clave)}») = {hashes[0]}."),
    ]
    if cantidad > 1:
        pasos.append(
            _paso(
                "Repetimos con cada salt",
                "La clave no cambia, pero como el salt es distinto el hash sale totalmente "
                f"distinto en las {cantidad} filas.",
            )
        )
    pasos.append(
        _paso(
            "Qué se guarda",
            "El salt y el hash, nunca la clave. El salt no es secreto: Solo tiene que ser único.",
        )
    )
    pasos.append(
        _paso(
            "Por qué sirve",
            "Dos usuarios con la misma clave quedan con hashes distintos, y una tabla de "
            "hashes precalculados deja de servir porque habría que calcularla de nuevo "
            "para cada salt.",
        )
    )
    pasos.append(
        _paso(
            "En la vida real",
            "Se usan bcrypt, Argon2 o PBKDF2: Aplican salt y además son lentos a propósito "
            "para frenar la fuerza bruta.",
        )
    )

    if not distintos:
        verificacion = None
    elif cantidad == 1:
        verificacion = (
            "Vuelve a generar: Saldrá otro salt y, con la misma clave, un hash "
            "totalmente distinto"
        )
    else:
        verificacion = (
            f"Los {cantidad} salts son distintos y los {cantidad} hashes también, "
            f"con la misma clave «{_abreviar(str(clave))}»"
        )

    return Resultado(
        valor="1 hash con salt" if cantidad == 1 else f"{cantidad} hashes distintos",
        pasos=pasos,
        tabla=tabla,
        verificacion=verificacion,
        datos={
            "etiqueta": f"Salt con {nombre} para «{_abreviar(str(clave))}»",
            "chips": [
                f"hash = {nombre}(salt + clave)",
                "salt = secrets.token_hex(8)",
                f"{_DIGITOS_HASH[nombre]} dígitos hex",
            ],
            "formula": f"hash = {nombre}(salt + clave)",
            "salts": salts,
            "hashes": hashes,
            "nota_tabla": (
                "La clave es la misma en todas las filas: Solo cambia el salt y el "
                "hash completo cambia con él. El salt se guarda junto al hash; no "
                "es secreto, solo único."
            ),
        },
    )


def verificar_clave(clave: str, salt: str, hash_guardado: str, algoritmo: str) -> Resultado:
    """6.1, 6.2 y 6.3 · Comprueba una clave contra un salt y un hash guardados.

    El servidor no guarda la clave: Guarda el salt y el hash. Para verificar
    repite hash = algoritmo(salt + clave) y compara el resultado con el
    hash guardado; si coinciden, la clave es correcta.
    """
    nombre = _validar_algoritmo(algoritmo)
    if str(clave) == "":
        raise ValueError("La clave está vacía. Escribe la clave que quieres comprobar.")
    salt_limpio = str(salt).strip()
    if salt_limpio == "":
        raise ValueError("El salt está vacío. Copia el salt que se guardó junto al hash.")
    guardado = str(hash_guardado).strip().lower()
    if guardado == "":
        raise ValueError("El hash guardado está vacío. Copia el hash de la tabla para comparar.")
    if any(digito not in "0123456789abcdef" for digito in guardado):
        raise ValueError(
            "El hash guardado no es hexadecimal válido. Cópialo tal como salió "
            "en la tabla, sin espacios ni otros caracteres."
        )
    if len(guardado) != _DIGITOS_HASH[nombre]:
        raise ValueError(
            f"Un hash {nombre} tiene {_DIGITOS_HASH[nombre]} dígitos hexadecimales "
            f"y el guardado tiene {len(guardado)}. Revisa que copiaste el hash "
            "completo y que el algoritmo sea el mismo."
        )

    calculado = _hash_con_salt(clave, salt_limpio, nombre)
    correcta = calculado == guardado
    marcas = "".join(" " if x == y else "^" for x, y in zip(calculado, guardado))
    alineado = f"Guardado:  {guardado}\nCalculado: {calculado}"
    if not correcta:
        alineado += f"\n           {marcas}"

    pasos = [
        _paso(
            "Qué hacemos",
            "Comprobar la clave sin tenerla guardada: Repetimos la fórmula "
            f"hash = {nombre}(salt + clave) con el salt guardado y comparamos el resultado "
            "con el hash guardado.",
        ),
        _paso("Pegamos salt y clave", f"«{salt_limpio}» + «{clave}» = «{salt_limpio + str(clave)}»."),
        _paso("Calculamos el hash", f"{nombre}(«{salt_limpio + str(clave)}») = {calculado}."),
        _paso(
            "Comparamos",
            "Coincide con el hash guardado carácter a carácter: La clave es correcta."
            if correcta
            else f"No coincide con el guardado ({guardado}): La clave o el salt no son los "
            "que se usaron al generar el hash. Las ^ marcan las diferencias.",
        ),
    ]

    return Resultado(
        valor=calculado,
        pasos=pasos,
        verificacion=(
            f"{nombre}(salt + clave) reproduce el hash guardado: La clave es correcta"
            if correcta
            else None
        ),
        datos={
            "etiqueta": f"Hash calculado con {nombre}",
            "chips": [
                f"hash = {nombre}(salt + clave)",
                "coincide" if correcta else "no coincide",
            ],
            "correcta": correcta,
            "mensaje": (
                "Clave correcta: El hash calculado coincide con el guardado."
                if correcta
                else "Clave incorrecta: El hash calculado no coincide con el "
                "guardado. Revisa la clave y que el salt sea el de la misma fila."
            ),
            "alineado": alineado,
        },
    )
