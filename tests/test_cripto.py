"""Pruebas de la lógica de cripto.py. Ejecutar con: pytest -q

Nota: pow(a, -1, n), math.gcd y hashlib solo se usan aquí, para verificar
las implementaciones de cripto.py por un camino independiente.
"""

import hashlib
import math

import pytest

import cripto
import ejemplos
from cripto import (
    ALFABETO,
    ALFABETO_26,
    Resultado,
    aee,
    cifrado_afin,
    cifrado_atbash,
    cifrado_cesar,
    cifrado_modulo27,
    cifrado_vernam,
    codificacion_ascii,
    codificacion_base64,
    codificacion_binaria,
    codificacion_hexadecimal,
    diffie_hellman,
    es_primo,
    exp_rapida,
    exponenciacion_rapida,
    generar_salts,
    hash_texto,
    inverso_aditivo,
    inverso_aee,
    inverso_tradicional,
    inverso_xor,
    letra_a_numero,
    mcd,
    mcd_euclides,
    modulo,
    normalizar,
    numero_a_letra,
    numeros_a_texto,
    rsa,
    sustitucion_simple,
    texto_a_numeros,
    transposicion_columnar,
    verificar_clave,
)

# ---------------------------- Alfabeto ----------------------------


def test_alfabeto_tiene_27_letras_con_la_ene():
    assert len(ALFABETO) == 27
    assert ALFABETO[0] == "A"
    assert ALFABETO[14] == "Ñ"
    assert ALFABETO[26] == "Z"


# ---------------------------- normalizar ----------------------------


def test_normalizar_pasa_a_mayusculas():
    assert normalizar("hola") == "HOLA"


def test_normalizar_quita_tildes_y_dieresis():
    assert normalizar("canción") == "CANCION"
    assert normalizar("pingüino") == "PINGUINO"
    assert normalizar("áéíóú ÁÉÍÓÚ") == "AEIOUAEIOU"


def test_normalizar_conserva_la_ene():
    assert normalizar("ñandú") == "ÑANDU"
    assert normalizar("AÑO") == "AÑO"


def test_normalizar_ignora_lo_que_no_es_letra():
    assert normalizar("Hola, mundo 123!") == "HOLAMUNDO"
    assert normalizar("  ") == ""
    assert normalizar("") == ""


# ---------------------------- Conversiones ----------------------------


def test_letra_a_numero_extremos():
    assert letra_a_numero("A") == 0
    assert letra_a_numero("Ñ") == 14
    assert letra_a_numero("Z") == 26


def test_numero_a_letra_es_la_inversa():
    for numero, letra in enumerate(ALFABETO):
        assert numero_a_letra(numero) == letra
        assert letra_a_numero(letra) == numero


def test_letra_invalida_lanza_valueerror():
    with pytest.raises(ValueError):
        letra_a_numero("4")
    with pytest.raises(ValueError):
        letra_a_numero("AB")
    with pytest.raises(ValueError):
        letra_a_numero("")


def test_numero_fuera_de_rango_lanza_valueerror():
    with pytest.raises(ValueError):
        numero_a_letra(27)
    with pytest.raises(ValueError):
        numero_a_letra(-1)


def test_texto_a_numeros_normaliza_primero():
    assert texto_a_numeros("Hola") == [7, 15, 11, 0]


def test_numeros_a_texto_recupera_el_original():
    assert numeros_a_texto(texto_a_numeros("España")) == "ESPAÑA"


# ---------------------------- Resultado ----------------------------


def test_resultado_valores_por_defecto():
    resultado = Resultado(valor="15", pasos=["un paso"])
    assert resultado.tabla is None
    assert resultado.verificacion is None
    assert resultado.datos == {}


# ---------------------- 1.1 · Módulo ----------------------


def test_modulo_27_mod_5():
    assert modulo(27, 5).valor == "2"


def test_modulo_negativo():
    resultado = modulo(-7, 26)
    assert resultado.valor == "19"
    assert resultado.datos["q"] == -1
    assert "-7 = -1 × 26 + 19" in resultado.verificacion


@pytest.mark.parametrize("a,n", [(27, 5), (-7, 26), (0, 9), (100, 7), (-100, 7), (5, 5)])
def test_modulo_cumple_la_identidad(a, n):
    resultado = modulo(a, n)
    b = int(resultado.valor)
    q = resultado.datos["q"]
    assert a == q * n + b
    assert 0 <= b < n


@pytest.mark.parametrize("n", [0, -3])
def test_modulo_rechaza_n_no_positivo(n):
    with pytest.raises(ValueError):
        modulo(7, n)


# ---------------------- 1.2 · Inverso aditivo ----------------------


def test_inverso_aditivo_7_mod_26():
    resultado = inverso_aditivo(7, 26)
    assert resultado.valor == "19"
    assert "≡ 0 (mod 26)" in resultado.verificacion


@pytest.mark.parametrize("a,n", [(7, 26), (0, 26), (-4, 9), (30, 26), (13, 13)])
def test_inverso_aditivo_suma_da_multiplo_de_n(a, n):
    x = int(inverso_aditivo(a, n).valor)
    assert (a + x) % n == 0
    assert 0 <= x < n


def test_inverso_aditivo_rechaza_n_no_positivo():
    with pytest.raises(ValueError):
        inverso_aditivo(7, 0)


# ---------------------- 1.3 · Inverso de XOR ----------------------


def test_inverso_xor_binario():
    resultado = inverso_xor("1100", "0110", "binario")
    assert resultado.valor == "1010"
    assert resultado.datos["a"] == 0b1010


def test_inverso_xor_acepta_base_con_mayusculas():
    assert inverso_xor("1100", "0110", "Binario").valor == "1010"


def test_inverso_xor_hexadecimal():
    resultado = inverso_xor("1F", "0F", "hexadecimal")
    assert resultado.valor == "10"
    assert resultado.datos["a"] == 0x10


def test_inverso_xor_decimal():
    assert inverso_xor("12", "6", "decimal").valor == "10"


def test_inverso_xor_es_su_propio_inverso():
    datos = inverso_xor("10110", "01011", "binario").datos
    assert datos["a"] ^ datos["k"] == datos["c"]


def test_inverso_xor_tabla_muestra_las_tres_bases():
    tabla = inverso_xor("1100", "0110", "binario").tabla
    assert [fila["Valor"] for fila in tabla] == ["C", "K", "A = C ⊕ K"]
    assert tabla[2]["Binario"] == "1010"
    assert tabla[2]["Decimal"] == 10
    assert tabla[2]["Hexadecimal"] == "A"


@pytest.mark.parametrize(
    "c,k,base",
    [
        ("102", "011", "binario"),   # dígito fuera de la base
        ("1F", "2G", "hexadecimal"),  # letra inválida
        ("-3", "5", "decimal"),       # signo no permitido
        ("", "0110", "binario"),      # campo vacío
        ("1100", "0110", None),       # base sin elegir
    ],
)
def test_inverso_xor_rechaza_entradas_invalidas(c, k, base):
    with pytest.raises(ValueError):
        inverso_xor(c, k, base)


# ---------------------- 1.4 · MCD ----------------------


def test_mcd_7_26_existe_inverso():
    resultado = mcd_euclides(7, 26)
    assert resultado.valor == "1"
    assert resultado.datos["existe_inverso"] is True


def test_mcd_12_18_no_existe_inverso():
    resultado = mcd_euclides(12, 18)
    assert resultado.valor == "6"
    assert resultado.datos["existe_inverso"] is False


def test_mcd_tabla_termina_en_residuo_cero():
    tabla = mcd_euclides(7, 26).tabla
    assert tabla[-1]["Residuo r"] == 0


@pytest.mark.parametrize("a,b", [(7, 26), (12, 18), (26, 7), (1, 1), (100, 75), (17, 3120)])
def test_mcd_coincide_con_math_gcd(a, b):
    assert mcd(a, b) == math.gcd(a, b)
    assert mcd_euclides(a, b).valor == str(math.gcd(a, b))


def test_mcd_rechaza_no_positivos():
    with pytest.raises(ValueError):
        mcd_euclides(0, 18)
    with pytest.raises(ValueError):
        mcd_euclides(7, -26)


# ---------------------- 1.5 · Inverso tradicional ----------------------


def test_inverso_tradicional_3_mod_7():
    resultado = inverso_tradicional(3, 7)
    assert resultado.valor == "5"
    assert resultado.verificacion == "3 × 5 = 15 ≡ 1 (mod 7)"
    assert resultado.datos["intentos"] == 5
    # La tabla registra los 5 intentos y el último tiene residuo 1
    assert len(resultado.tabla) == 5
    assert resultado.tabla[-1] == {"Intento x": 5, "a × x": 15, "a × x mod n": 1}


@pytest.mark.parametrize("a,n", [(3, 7), (7, 26), (5, 27), (11, 100), (123, 997)])
def test_inverso_tradicional_coincide_con_pow(a, n):
    assert int(inverso_tradicional(a, n).valor) == pow(a, -1, n)


def test_inverso_tradicional_sin_inverso():
    with pytest.raises(ValueError, match="No existe inverso"):
        inverso_tradicional(12, 18)


def test_inverso_tradicional_limite_de_n():
    with pytest.raises(ValueError):
        inverso_tradicional(3, 100_001)


# ---------------------- 1.6 · Euclides extendido ----------------------


def test_aee_devuelve_la_identidad_de_bezout():
    g, s, t, tabla = aee(26, 7)
    assert (g, s, t) == (1, 3, -11)
    assert s * 26 + t * 7 == g
    assert len(tabla) == 6  # 2 filas de inicio + 4 divisiones


def test_inverso_aee_7_mod_26():
    resultado = inverso_aee(7, 26)
    assert resultado.valor == "15"
    assert resultado.datos["rondas"] == 4
    assert resultado.datos["t"] == -11
    assert resultado.verificacion == "7 × 15 = 105 ≡ 1 (mod 26)"


def test_inverso_aee_tabla_exacta_del_ejemplo():
    # La tabla debe coincidir con la especificada: dos filas de inicio
    # (n: s=1, t=0 y a: s=0, t=1) y una fila por división.
    tabla = inverso_aee(7, 26).tabla
    assert tabla == [
        {"Ronda": "Inicio", "Cociente q": "—", "Residuo r": 26, "s": 1, "t": 0},
        {"Ronda": "Inicio", "Cociente q": "—", "Residuo r": 7, "s": 0, "t": 1},
        {"Ronda": "1", "Cociente q": "3", "Residuo r": 5, "s": 1, "t": -3},
        {"Ronda": "2", "Cociente q": "1", "Residuo r": 2, "s": -1, "t": 4},
        {"Ronda": "3", "Cociente q": "2", "Residuo r": 1, "s": 3, "t": -11},
        {"Ronda": "4", "Cociente q": "2", "Residuo r": 0, "s": -7, "t": 26},
    ]


@pytest.mark.parametrize("a,n", [(3, 7), (7, 26), (5, 27), (17, 3120), (7, 40), (123, 997)])
def test_inverso_aee_coincide_con_pow(a, n):
    assert int(inverso_aee(a, n).valor) == pow(a, -1, n)


def test_inverso_aee_reduce_a_mayor_que_n():
    # 33 mod 26 = 7, así que el inverso es el mismo que el de 7
    assert inverso_aee(33, 26).valor == inverso_aee(7, 26).valor


def test_inverso_aee_sin_inverso():
    with pytest.raises(ValueError, match="No existe inverso"):
        inverso_aee(12, 18)
    with pytest.raises(ValueError, match="No existe inverso"):
        inverso_aee(26, 26)  # equivale a 0 módulo 26


def test_inverso_aee_rechaza_modulo_menor_que_2():
    with pytest.raises(ValueError):
        inverso_aee(7, 1)


# ---------------------- Catálogo de ejemplos del módulo 1 ----------------------

EJEMPLOS_MODULO_1 = [e for e in ejemplos.EJEMPLOS if e["id"].startswith("1.")]


def test_el_catalogo_tiene_los_6_submenus_del_modulo_1():
    assert [e["id"] for e in EJEMPLOS_MODULO_1] == ["1.1", "1.2", "1.3", "1.4", "1.5", "1.6"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_1, ids=lambda e: e["id"])
def test_ejemplos_del_modulo_1_dan_el_resultado_esperado(ejemplo):
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    assert resultado.valor == ejemplo["esperado"]


# ======================================================================
# Módulo 2 · Criptografía clásica
# ======================================================================

# Textos con Ñ, tildes y espacios para las pruebas de ida y vuelta
TEXTOS_CON_ENIE = [
    "El niño juega",
    "Añoranza y corazón",
    "La cigüeña añeja",
    "mañana será otro día",
]


# ---------------------- 2.1 · Módulo 27 ----------------------


def test_modulo27_cifra_hola_con_k_3():
    resultado = cifrado_modulo27("HOLA", 3, "cifrar")
    assert resultado.valor == "KRÑD"
    assert resultado.tabla[0] == {
        "Letra": "H",
        "Número": 7,
        "Operación": "(7 + 3) mod 27 = 10",
        "Letra cifrada": "K",
    }


def test_modulo27_descifra_krnd():
    assert cifrado_modulo27("KRÑD", 3, "descifrar").valor == "HOLA"


def test_modulo27_reduce_k_grande():
    # k = 30 equivale a k = 3
    assert cifrado_modulo27("HOLA", 30, "cifrar").valor == "KRÑD"


@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
def test_modulo27_ida_y_vuelta(texto):
    cifrado = cifrado_modulo27(texto, 11, "cifrar").valor
    assert cifrado_modulo27(cifrado, 11, "descifrar").valor == normalizar(texto)


def test_modulo27_rechaza_texto_sin_letras():
    with pytest.raises(ValueError):
        cifrado_modulo27("123 !!", 3, "cifrar")


def test_modulo27_rechaza_modo_invalido():
    with pytest.raises(ValueError, match="Cifrar o Descifrar"):
        cifrado_modulo27("HOLA", 3, "codificar")


# ---------------------- 2.2 · César ----------------------


def test_cesar_hola_con_alfabeto_26():
    resultado = cifrado_cesar("HOLA", 3, "26 letras", "cifrar")
    assert resultado.valor == "KROD"


def test_cesar_con_alfabeto_27_coincide_con_modulo27():
    assert cifrado_cesar("HOLA", 3, "27 letras (español)", "cifrar").valor == "KRÑD"


def test_cesar_desplazamiento_por_defecto_es_3():
    assert cifrado_cesar("HOLA").valor == "KRÑD"


def test_cesar_26_convierte_la_ene_en_n():
    # En el alfabeto de 26 la Ñ pierde la virgulilla, como una tilde
    resultado = cifrado_cesar("AÑO", 0, "26 letras", "cifrar")
    assert resultado.datos["normalizado"] == "ANO"


@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
@pytest.mark.parametrize("alfabeto", ["27 letras (español)", "26 letras"])
def test_cesar_ida_y_vuelta(texto, alfabeto):
    letras = ALFABETO if alfabeto.startswith("27") else ALFABETO_26
    cifrado = cifrado_cesar(texto, 7, alfabeto, "cifrar").valor
    assert cifrado_cesar(cifrado, 7, alfabeto, "descifrar").valor == normalizar(texto, letras)


def test_cesar_rechaza_alfabeto_invalido():
    with pytest.raises(ValueError, match="27 letras"):
        cifrado_cesar("HOLA", 3, "25", "cifrar")


# ---------------------- 2.3 · Vernam ----------------------


def test_vernam_cifra_hola_con_xmck():
    resultado = cifrado_vernam("HOLA", "XMCK", "cifrar")
    assert resultado.valor == "10020F0A"
    assert resultado.datos["binario"] == "00010000 00000010 00001111 00001010"


def test_vernam_descifra_desde_hex():
    assert cifrado_vernam("10020F0A", "XMCK", "descifrar").valor == "HOLA"


def test_vernam_descifra_hex_con_espacios_y_minusculas():
    assert cifrado_vernam("10 02 0f 0a", "XMCK", "descifrar").valor == "HOLA"


@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
def test_vernam_ida_y_vuelta_conserva_tildes_y_espacios(texto):
    # Vernam trabaja con bytes UTF-8: no normaliza, el original vuelve intacto
    clave = "K" * len(texto.encode("utf-8"))
    cifrado = cifrado_vernam(texto, clave, "cifrar").valor
    assert cifrado_vernam(cifrado, clave, "descifrar").valor == texto


def test_vernam_rechaza_clave_de_otra_longitud():
    # "mañana" ocupa 7 bytes (la ñ ocupa 2) y "abcdef" solo 6
    with pytest.raises(ValueError, match="bytes"):
        cifrado_vernam("mañana", "abcdef", "cifrar")


@pytest.mark.parametrize(
    "texto_hex",
    ["10020F0G", "10020F0"],  # dígito inválido / cantidad impar de dígitos
)
def test_vernam_rechaza_hexadecimal_invalido(texto_hex):
    with pytest.raises(ValueError):
        cifrado_vernam(texto_hex, "XMCK", "descifrar")


def test_vernam_rechaza_entradas_vacias():
    with pytest.raises(ValueError):
        cifrado_vernam("", "XMCK", "cifrar")
    with pytest.raises(ValueError):
        cifrado_vernam("HOLA", "", "cifrar")


# ---------------------- 2.4 · Atbash ----------------------


def test_atbash_cifra_hola():
    assert cifrado_atbash("HOLA", "cifrar").valor == "SLOZ"


def test_atbash_la_n_queda_igual():
    # La N ocupa la posición 13, el centro del alfabeto: 26 − 13 = 13
    assert cifrado_atbash("N", "cifrar").valor == "N"


def test_atbash_es_su_propio_inverso():
    assert cifrado_atbash("SLOZ", "descifrar").valor == "HOLA"
    assert cifrado_atbash(cifrado_atbash("ÑANDU", "cifrar").valor, "cifrar").valor == "ÑANDU"


@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
def test_atbash_ida_y_vuelta(texto):
    cifrado = cifrado_atbash(texto, "cifrar").valor
    assert cifrado_atbash(cifrado, "descifrar").valor == normalizar(texto)


# ---------------------- 2.5 · Transposición columnar ----------------------


def test_columnar_cifra_holamundo_con_clave():
    resultado = transposicion_columnar("HOLAMUNDO", "CLAVE", "cifrar")
    assert resultado.valor == "LDHUMXONAO"
    # Orden de las columnas de CLAVE: C=2, L=4, A=1, V=5, E=3
    assert resultado.datos["orden"] == [2, 4, 1, 5, 3]
    # La matriz lleva la clave y el número de orden como encabezados
    assert resultado.tabla == [
        {"C (2)": "H", "L (4)": "O", "A (1)": "L", "V (5)": "A", "E (3)": "M"},
        {"C (2)": "U", "L (4)": "N", "A (1)": "D", "V (5)": "O", "E (3)": "X"},
    ]


def test_columnar_descifra_con_relleno():
    assert transposicion_columnar("LDHUMXONAO", "CLAVE", "descifrar").valor == "HOLAMUNDOX"


def test_columnar_empates_de_la_clave_van_de_izquierda_a_derecha():
    # En SALSA, la S y la A repetidas se numeran de izquierda a derecha:
    # S=4, A=1, L=3, S=5, A=2
    resultado = transposicion_columnar("HOLAMUNDO", "SALSA", "cifrar")
    assert resultado.datos["orden"] == [4, 1, 3, 5, 2]


@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
def test_columnar_ida_y_vuelta_salvo_el_relleno(texto):
    cifrado = transposicion_columnar(texto, "NOCHE", "cifrar").valor
    recuperado = transposicion_columnar(cifrado, "NOCHE", "descifrar").valor
    limpio = normalizar(texto)
    # Lo recuperado es el original más las X de relleno
    assert recuperado.startswith(limpio)
    assert set(recuperado[len(limpio):]) <= {"X"}


def test_columnar_rechaza_clave_corta():
    with pytest.raises(ValueError, match="2 letras"):
        transposicion_columnar("HOLA", "A", "cifrar")


def test_columnar_rechaza_descifrado_que_no_llena_la_matriz():
    # 9 letras no se reparten exacto en 5 columnas
    with pytest.raises(ValueError, match="columnas"):
        transposicion_columnar("HOLAMUNDO", "CLAVE", "descifrar")


# ---------------------- 2.6 · Afín ----------------------


def test_afin_cifra_hola_con_a5_b8():
    resultado = cifrado_afin("HOLA", 5, 8, "cifrar")
    assert resultado.valor == "PCJI"
    assert resultado.datos["a_inverso"] == 11


def test_afin_descifra_pcji():
    assert cifrado_afin("PCJI", 5, 8, "descifrar").valor == "HOLA"


def test_afin_reutiliza_la_tabla_del_aee():
    # La tabla extra del afín es exactamente la del AEE del submenú 1.6
    resultado = cifrado_afin("HOLA", 5, 8, "cifrar")
    assert resultado.datos["tabla_extra"]["filas"] == aee(27, 5)[3]


@pytest.mark.parametrize("a", [1, 2, 4, 5, 7, 8, 10, 25, 26])
def test_afin_calcula_el_inverso_correcto(a):
    assert cifrado_afin("A", a, 0, "cifrar").datos["a_inverso"] == pow(a, -1, 27)


@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
def test_afin_ida_y_vuelta(texto):
    cifrado = cifrado_afin(texto, 7, 11, "cifrar").valor
    assert cifrado_afin(cifrado, 7, 11, "descifrar").valor == normalizar(texto)


@pytest.mark.parametrize("a", [3, 6, 9, 27])
def test_afin_rechaza_a_sin_inverso(a):
    with pytest.raises(ValueError, match="MCD"):
        cifrado_afin("HOLA", a, 8, "cifrar")


# ---------------------- 2.7 · Sustitución simple ----------------------


def test_sustitucion_cifra_hola_con_murcielago():
    resultado = sustitucion_simple("HOLA", "MURCIELAGO", "cifrar")
    assert resultado.valor == "AKDM"
    assert resultado.datos["tipo_clave"] == "palabra clave"
    assert resultado.datos["alfabeto_cifrado"] == "MURCIELAGOBDFHJKNÑPQSTVWXYZ"


def test_sustitucion_descifra_akdm():
    assert sustitucion_simple("AKDM", "MURCIELAGO", "descifrar").valor == "HOLA"


def test_sustitucion_tabla_en_dos_filas():
    # Una fila de datos con el alfabeto original como encabezados
    tabla = sustitucion_simple("HOLA", "MURCIELAGO", "cifrar").tabla
    assert len(tabla) == 1
    assert list(tabla[0].keys()) == list(ALFABETO)
    assert "".join(tabla[0].values()) == "MURCIELAGOBDFHJKNÑPQSTVWXYZ"


def test_sustitucion_quita_letras_repetidas_de_la_clave():
    # PAPAYA queda en PAY y el resto del alfabeto sigue en orden
    resultado = sustitucion_simple("HOLA", "PAPAYA", "cifrar")
    assert resultado.datos["alfabeto_cifrado"].startswith("PAY")
    assert len(set(resultado.datos["alfabeto_cifrado"])) == 27


def test_sustitucion_acepta_permutacion_completa():
    # El alfabeto invertido es una permutación válida y equivale a Atbash
    resultado = sustitucion_simple("HOLA", ALFABETO[::-1], "cifrar")
    assert resultado.valor == "SLOZ"
    assert resultado.datos["tipo_clave"] == "permutación completa"


@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
@pytest.mark.parametrize("clave", ["MURCIELAGO", "año señal"])
def test_sustitucion_ida_y_vuelta(texto, clave):
    cifrado = sustitucion_simple(texto, clave, "cifrar").valor
    assert sustitucion_simple(cifrado, clave, "descifrar").valor == normalizar(texto)


def test_sustitucion_rechaza_clave_sin_letras():
    with pytest.raises(ValueError, match="clave"):
        sustitucion_simple("HOLA", "123", "cifrar")


# ---------------------- Verificación (operación inversa) ----------------------

EJEMPLOS_MODULO_2 = [e for e in ejemplos.EJEMPLOS if e["id"].startswith("2.")]


def test_el_catalogo_tiene_los_7_submenus_del_modulo_2():
    ids = [e["id"] for e in EJEMPLOS_MODULO_2]
    assert ids == ["2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_2, ids=lambda e: e["id"])
def test_ejemplos_del_modulo_2_dan_el_resultado_esperado(ejemplo):
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    assert resultado.valor == ejemplo["esperado"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_2, ids=lambda e: e["id"])
def test_la_receta_de_verificar_recupera_el_original(ejemplo):
    # Lo mismo que hace el botón "Verificar" de la interfaz: aplicar la
    # operación inversa del resultado y comparar con lo esperado
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    receta = resultado.datos["verificar"]
    vuelta = getattr(cripto, receta["funcion"])(**receta["entradas"])
    assert vuelta.valor == receta["esperado"]


# ======================================================================
# Módulo 3 · Criptografía moderna
# ======================================================================


# ---------------------- es_primo ----------------------


@pytest.mark.parametrize("n", [2, 3, 5, 23, 53, 61, 997, 999_983])
def test_es_primo_reconoce_primos(n):
    assert es_primo(n) is True


@pytest.mark.parametrize("n", [-7, 0, 1, 4, 9, 15, 100, 3233, 999_981])
def test_es_primo_rechaza_no_primos(n):
    assert es_primo(n) is False


# ---------------------- exp_rapida (núcleo reutilizable) ----------------------


def test_exp_rapida_3_13_mod_7_tabla_exacta():
    # 13 = 1101 en binario; la tabla recorre los bits del menos significativo
    # al más significativo: en cada fila la potencia se eleva al cuadrado y
    # el acumulado solo cambia cuando el bit es 1.
    resultado, tabla, multiplicaciones = exp_rapida(3, 13, 7)
    assert resultado == 3
    assert multiplicaciones == 6  # 3 al cuadrado + 3 por bits en 1
    assert tabla == [
        {"Bit i": 0, "Bit del exponente": 1, "Potencia al cuadrado": 3, "Acumulado": 3},
        {"Bit i": 1, "Bit del exponente": 0, "Potencia al cuadrado": 2, "Acumulado": 3},
        {"Bit i": 2, "Bit del exponente": 1, "Potencia al cuadrado": 4, "Acumulado": 5},
        {"Bit i": 3, "Bit del exponente": 1, "Potencia al cuadrado": 2, "Acumulado": 3},
    ]


@pytest.mark.parametrize(
    "base,exponente,n",
    [
        (3, 13, 7),
        (5, 6, 23),
        (5, 15, 23),
        (65, 17, 3233),
        (2790, 2753, 3233),
        (7, 1, 26),
        (2, 10, 1024),
        (-4, 3, 7),
        (123_456, 789_012, 999_983),
    ],
)
def test_exp_rapida_coincide_con_pow(base, exponente, n):
    assert exp_rapida(base, exponente, n)[0] == pow(base, exponente, n)


def test_exp_rapida_una_fila_por_bit_del_exponente():
    _, tabla, _ = exp_rapida(3, 13, 7)
    assert len(tabla) == 4  # 13 = 1101 tiene 4 bits


def test_exp_rapida_rechaza_entradas_invalidas():
    with pytest.raises(ValueError):
        exp_rapida(3, 13, 1)  # módulo menor que 2
    with pytest.raises(ValueError):
        exp_rapida(3, 0, 7)  # exponente menor que 1


# ---------------------- 3.1 · Diffie-Hellman ----------------------


def test_diffie_hellman_ejemplo_de_la_clase():
    resultado = diffie_hellman(23, 5, 6, 15)
    assert resultado.valor == "2"
    assert resultado.datos["A"] == 8
    assert resultado.datos["B"] == 19
    assert resultado.datos["K"] == 2
    # Con p = 23 primo no hay advertencia
    assert "aviso" not in resultado.datos


def test_diffie_hellman_metricas_para_a_b_y_k():
    metricas = diffie_hellman(23, 5, 6, 15).datos["metricas"]
    assert [valor for _, valor in metricas] == [8, 19, 2]


def test_diffie_hellman_reutiliza_la_tabla_de_exp_rapida():
    # La tabla extra es exactamente la del submenú 3.3 para K = Bᵃ mod p
    resultado = diffie_hellman(23, 5, 6, 15)
    assert resultado.datos["tabla_extra"]["filas"] == exp_rapida(19, 6, 23)[1]


@pytest.mark.parametrize("p,g,a,b", [(23, 5, 6, 15), (7, 3, 2, 5), (997, 7, 123, 456)])
def test_diffie_hellman_los_dos_lados_coinciden(p, g, a, b):
    datos = diffie_hellman(p, g, a, b).datos
    assert datos["A"] == pow(g, a, p)
    assert datos["B"] == pow(g, b, p)
    assert datos["K"] == pow(datos["B"], a, p) == pow(datos["A"], b, p)


def test_diffie_hellman_avisa_si_p_no_es_primo():
    resultado = diffie_hellman(15, 2, 3, 5)
    assert "no es primo" in resultado.datos["aviso"]
    # El cálculo sale igual, solo que sin garantía de seguridad
    assert int(resultado.valor) == pow(pow(2, 5, 15), 3, 15)


@pytest.mark.parametrize(
    "p,g,a,b",
    [
        (2, 5, 6, 15),  # p menor que 3
        (1_000_003, 5, 6, 15),  # p por encima del límite
        (23, 1, 6, 15),  # g menor que 2
        (23, 23, 6, 15),  # g fuera de rango (g debe ser menor que p)
        (23, 5, 0, 15),  # clave privada no positiva
        (23, 5, 6, -2),  # clave privada negativa
    ],
)
def test_diffie_hellman_rechaza_entradas_invalidas(p, g, a, b):
    with pytest.raises(ValueError):
        diffie_hellman(p, g, a, b)


# ---------------------- 3.2 · RSA ----------------------


def test_rsa_ejemplo_de_la_clase():
    resultado = rsa(61, 53, 17, 65)
    assert resultado.valor == "2790"
    assert resultado.datos["n"] == 3233
    assert resultado.datos["phi"] == 3120
    assert resultado.datos["d"] == 2753
    assert resultado.datos["descifrado"] == 65
    assert "65" in resultado.verificacion


def test_rsa_metricas_para_n_phi_y_d():
    metricas = rsa(61, 53, 17, 65).datos["metricas"]
    assert [valor for _, valor in metricas] == [3233, 3120, 2753]


def test_rsa_reutiliza_la_tabla_del_aee_para_d():
    # La tabla extra es exactamente la del AEE del 1.6 con (φ(n), e)
    resultado = rsa(61, 53, 17, 65)
    assert resultado.datos["tabla_extra"]["filas"] == aee(3120, 17)[3]


def test_rsa_reutiliza_la_tabla_de_exp_rapida_para_c():
    # La tabla principal es la de la exponenciación rápida del 3.3
    resultado = rsa(61, 53, 17, 65)
    assert resultado.tabla == exp_rapida(65, 17, 3233)[1]


@pytest.mark.parametrize(
    "p,q,e,m",
    [(61, 53, 17, 65), (11, 13, 7, 9), (17, 23, 5, 100), (101, 103, 19, 4242)],
)
def test_rsa_d_coincide_con_pow_y_descifra(p, q, e, m):
    datos = rsa(p, q, e, m).datos
    phi = (p - 1) * (q - 1)
    assert datos["d"] == pow(e, -1, phi)
    assert datos["c"] == pow(m, e, p * q)
    assert datos["descifrado"] == m


@pytest.mark.parametrize(
    "p,q,e,m,texto_error",
    [
        (10, 53, 17, 65, "primo"),  # p no es primo
        (61, 1, 17, 65, "primo"),  # q = 1 no es primo
        (13, 13, 5, 6, "distintos"),  # p = q
        (61, 53, 4, 65, "MCD"),  # MCD(4, 3120) = 4
        (61, 53, 1, 65, "1 < e"),  # e fuera de rango por abajo
        (61, 53, 3120, 65, "1 < e"),  # e fuera de rango por arriba
        (61, 53, 17, 3233, "m < n"),  # mensaje demasiado grande
        (61, 53, 17, -1, "0 ≤ m"),  # mensaje negativo
        (1_000_003, 53, 17, 65, "lento"),  # p por encima del límite
    ],
)
def test_rsa_rechaza_entradas_invalidas(p, q, e, m, texto_error):
    with pytest.raises(ValueError, match=texto_error):
        rsa(p, q, e, m)


# ---------------------- 3.3 · Exponenciación rápida ----------------------


def test_exponenciacion_rapida_3_13_mod_7():
    resultado = exponenciacion_rapida(3, 13, 7)
    assert resultado.valor == "3"
    assert resultado.datos["binario"] == "1101"
    assert resultado.datos["multiplicaciones"] == 6
    # La comprobación directa muestra la potencia completa cuando es corta
    assert "1594323" in resultado.verificacion


def test_exponenciacion_rapida_reduce_la_base():
    # 10 mod 7 = 3, así que 10¹³ y 3¹³ dejan el mismo residuo
    assert exponenciacion_rapida(10, 13, 7).valor == "3"
    assert exponenciacion_rapida(-4, 3, 7).valor == str(pow(-4, 3, 7))


def test_exponenciacion_rapida_con_exponente_grande():
    # Con exponentes enormes no se puede comprobar por el método directo:
    # la verificación cambia de redacción, pero el valor sigue siendo exacto
    resultado = exponenciacion_rapida(7, 10**9, 999_983)
    assert resultado.valor == str(pow(7, 10**9, 999_983))
    assert "bits en 1" in resultado.verificacion


def test_exponenciacion_rapida_rechaza_entradas_invalidas():
    with pytest.raises(ValueError):
        exponenciacion_rapida(3, 13, 1)
    with pytest.raises(ValueError):
        exponenciacion_rapida(3, 0, 7)


# ---------------------- Catálogo de ejemplos del módulo 3 ----------------------

EJEMPLOS_MODULO_3 = [e for e in ejemplos.EJEMPLOS if e["id"].startswith("3.")]


def test_el_catalogo_tiene_los_3_submenus_del_modulo_3():
    assert [e["id"] for e in EJEMPLOS_MODULO_3] == ["3.1", "3.2", "3.3"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_3, ids=lambda e: e["id"])
def test_ejemplos_del_modulo_3_dan_el_resultado_esperado(ejemplo):
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    assert resultado.valor == ejemplo["esperado"]


# ======================================================================
# Módulo 4 · Algoritmos hash
# ======================================================================


def test_md5_de_abc():
    resultado = hash_texto("abc", "MD5")
    assert resultado.valor == "900150983cd24fb0d6963f7d28e17f72"
    assert resultado.datos["bits"] == 128


def test_sha256_de_abc():
    resultado = hash_texto("abc", "SHA-256")
    assert resultado.valor == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert resultado.datos["bits"] == 256


def test_sha512_de_abc():
    resultado = hash_texto("abc", "SHA-512")
    assert resultado.valor == (
        "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
        "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
    )
    assert resultado.datos["bits"] == 512


@pytest.mark.parametrize("algoritmo,funcion_hashlib", [
    ("MD5", hashlib.md5),
    ("SHA-256", hashlib.sha256),
    ("SHA-512", hashlib.sha512),
])
def test_hash_coincide_con_hashlib_con_enie_y_tildes(algoritmo, funcion_hashlib):
    texto = "El ñandú corrió al río"
    resultado = hash_texto(texto, algoritmo)
    assert resultado.valor == funcion_hashlib(texto.encode("utf-8")).hexdigest()


def test_hash_avalancha_cuenta_los_caracteres_que_cambian():
    resultado = hash_texto("abc", "MD5", comparar="abd")
    hash_2 = hashlib.md5(b"abd").hexdigest()
    esperadas = sum(1 for x, y in zip(resultado.valor, hash_2) if x != y)
    assert resultado.datos["cambios"] == esperadas
    assert esperadas > 20  # con textos distintos cambia casi todo el hash
    assert resultado.datos["alineado"].count("^") == esperadas


def test_hash_comparar_textos_iguales_no_cambia_nada_y_avisa():
    resultado = hash_texto("abc", "MD5", comparar="abc")
    assert resultado.datos["cambios"] == 0
    assert "aviso" in resultado.datos


def test_hash_sin_comparar_no_trae_metricas():
    resultado = hash_texto("abc", "MD5")
    assert "metricas" not in resultado.datos
    assert "cambios" not in resultado.datos


def test_hash_texto_vacio_lanza_valueerror():
    with pytest.raises(ValueError, match="vacío"):
        hash_texto("", "MD5")


def test_hash_algoritmo_desconocido_lanza_valueerror():
    with pytest.raises(ValueError, match="SHA-256"):
        hash_texto("abc", "SHA-1")


# ---------------------- Catálogo de ejemplos del módulo 4 ----------------------

EJEMPLOS_MODULO_4 = [e for e in ejemplos.EJEMPLOS if e["id"].startswith("4.")]


def test_el_catalogo_tiene_los_3_submenus_del_modulo_4():
    assert [e["id"] for e in EJEMPLOS_MODULO_4] == ["4.1", "4.2", "4.3"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_4, ids=lambda e: e["id"])
def test_ejemplos_del_modulo_4_dan_el_resultado_esperado(ejemplo):
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    assert resultado.valor == ejemplo["esperado"]


# ======================================================================
# Módulo 5 · Codificación
# ======================================================================

CODIFICADORES = [
    codificacion_ascii,
    codificacion_hexadecimal,
    codificacion_binaria,
    codificacion_base64,
]


def test_ascii_codifica_hola():
    resultado = codificacion_ascii("Hola", "codificar")
    assert resultado.valor == "72 111 108 97"
    assert len(resultado.tabla) == 4


def test_ascii_decodifica_los_codigos():
    assert codificacion_ascii("72 111 108 97", "decodificar").valor == "Hola"


def test_ascii_avisa_con_caracteres_fuera_de_ascii():
    resultado = codificacion_ascii("ñ", "codificar")
    assert resultado.valor == "195 177"
    assert "195 177" in resultado.datos["aviso"]


def test_ascii_sin_enie_no_trae_aviso():
    assert "aviso" not in codificacion_ascii("Hola", "codificar").datos


@pytest.mark.parametrize("entrada", ["72 x 108", "72 300 108", "195"])
def test_ascii_rechaza_decodificar_entradas_invalidas(entrada):
    with pytest.raises(ValueError):
        codificacion_ascii(entrada, "decodificar")


def test_hexadecimal_codifica_hola():
    assert codificacion_hexadecimal("Hola", "codificar").valor == "486F6C61"


def test_hexadecimal_decodifica_con_minusculas_y_espacios():
    assert codificacion_hexadecimal("48 6f 6c 61", "decodificar").valor == "Hola"


@pytest.mark.parametrize("entrada", ["XYZ", "486F6C6", "C3"])
def test_hexadecimal_rechaza_decodificar_entradas_invalidas(entrada):
    with pytest.raises(ValueError):
        codificacion_hexadecimal(entrada, "decodificar")


def test_binario_codifica_hola():
    assert (
        codificacion_binaria("Hola", "codificar").valor
        == "01001000 01101111 01101100 01100001"
    )


def test_binario_decodifica_con_o_sin_espacios():
    assert codificacion_binaria("01001000 01101111 01101100 01100001", "decodificar").valor == "Hola"
    assert codificacion_binaria("01001000011011110110110001100001", "decodificar").valor == "Hola"


@pytest.mark.parametrize("entrada", ["0100100", "01001002", "11000011"])
def test_binario_rechaza_decodificar_entradas_invalidas(entrada):
    with pytest.raises(ValueError):
        codificacion_binaria(entrada, "decodificar")


def test_base64_codifica_hola_con_relleno():
    resultado = codificacion_base64("Hola", "codificar")
    assert resultado.valor == "SG9sYQ=="
    # 4 bytes = 32 bits -> 6 grupos de 6 bits + 2 caracteres de relleno
    assert len(resultado.tabla) == 8


def test_base64_decodifica():
    assert codificacion_base64("SG9sYQ==", "decodificar").valor == "Hola"


def test_base64_coincide_con_el_modulo_base64_con_enie():
    import base64 as base64_estandar

    texto = "año señal"
    esperado = base64_estandar.b64encode(texto.encode("utf-8")).decode("ascii")
    assert codificacion_base64(texto, "codificar").valor == esperado


@pytest.mark.parametrize("entrada", ["SG9sYQ", "SG9sY@==", "====", "=SG9sYQ=="])
def test_base64_rechaza_decodificar_entradas_invalidas(entrada):
    with pytest.raises(ValueError):
        codificacion_base64(entrada, "decodificar")


@pytest.mark.parametrize("funcion", CODIFICADORES, ids=lambda f: f.__name__)
@pytest.mark.parametrize("texto", TEXTOS_CON_ENIE)
def test_codificar_y_decodificar_devuelve_el_original(funcion, texto):
    # A diferencia de los cifrados clásicos, aquí no se normaliza: la ida y
    # vuelta conserva mayúsculas, tildes, espacios y la ñ tal cual.
    codificado = funcion(texto, "codificar").valor
    assert funcion(codificado, "decodificar").valor == texto


@pytest.mark.parametrize("funcion", CODIFICADORES, ids=lambda f: f.__name__)
def test_codificadores_rechazan_texto_vacio(funcion):
    with pytest.raises(ValueError):
        funcion("", "codificar")
    with pytest.raises(ValueError):
        funcion("   ", "decodificar")


@pytest.mark.parametrize("funcion", CODIFICADORES, ids=lambda f: f.__name__)
def test_codificadores_rechazan_modo_invalido(funcion):
    with pytest.raises(ValueError):
        funcion("Hola", "cifrar")


# ---------------------- Catálogo de ejemplos del módulo 5 ----------------------

EJEMPLOS_MODULO_5 = [e for e in ejemplos.EJEMPLOS if e["id"].startswith("5.")]


def test_el_catalogo_tiene_los_4_submenus_del_modulo_5():
    assert [e["id"] for e in EJEMPLOS_MODULO_5] == ["5.1", "5.2", "5.3", "5.4"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_5, ids=lambda e: e["id"])
def test_ejemplos_del_modulo_5_dan_el_resultado_esperado(ejemplo):
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    assert resultado.valor == ejemplo["esperado"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_5, ids=lambda e: e["id"])
def test_ejemplos_del_modulo_5_pasan_su_receta_de_verificacion(ejemplo):
    # La receta de datos["verificar"] es la que ejecuta el botón "Verificar"
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    receta = resultado.datos["verificar"]
    vuelta = getattr(cripto, receta["funcion"])(**receta["entradas"])
    assert vuelta.valor == receta["esperado"]


# ======================================================================
# Módulo 6 · Uso de salt
# ======================================================================

FUNCIONES_HASHLIB = {"MD5": hashlib.md5, "SHA-256": hashlib.sha256, "SHA-512": hashlib.sha512}


@pytest.mark.parametrize("algoritmo", ["MD5", "SHA-256", "SHA-512"])
def test_generar_salts_formato_y_formula(algoritmo):
    resultado = generar_salts("Clave123", algoritmo, 3)
    assert len(resultado.tabla) == 3
    for salt, hash_hex in zip(resultado.datos["salts"], resultado.datos["hashes"]):
        # token_hex(8) son 8 bytes: 16 dígitos hexadecimales
        assert len(salt) == 16
        assert all(digito in "0123456789abcdef" for digito in salt)
        # la fórmula es hash(salt + clave), verificada con hashlib directo
        esperado = FUNCIONES_HASHLIB[algoritmo](f"{salt}Clave123".encode("utf-8")).hexdigest()
        assert hash_hex == esperado


def test_generar_salts_produce_hashes_distintos():
    resultado = generar_salts("Clave123", "SHA-256", 10)
    assert len(set(resultado.datos["hashes"])) == 10
    assert len(set(resultado.datos["salts"])) == 10


@pytest.mark.parametrize("cantidad", [0, 11, -1])
def test_generar_salts_rechaza_cantidad_fuera_de_rango(cantidad):
    with pytest.raises(ValueError, match="entre 1 y 10"):
        generar_salts("Clave123", "MD5", cantidad)


def test_generar_salts_rechaza_clave_vacia():
    with pytest.raises(ValueError, match="vacía"):
        generar_salts("", "MD5", 3)


def test_verificar_clave_correcta():
    resultado = verificar_clave(
        "Clave123", "a1b2c3d4", "3baad75a2e328110d25f895f12abc632", "MD5"
    )
    assert resultado.datos["correcta"] is True
    assert resultado.valor == "3baad75a2e328110d25f895f12abc632"
    assert resultado.verificacion is not None


def test_verificar_clave_incorrecta_es_resultado_no_error():
    resultado = verificar_clave(
        "OtraClave", "a1b2c3d4", "3baad75a2e328110d25f895f12abc632", "MD5"
    )
    assert resultado.datos["correcta"] is False
    assert resultado.verificacion is None
    assert "incorrecta" in resultado.datos["mensaje"]


def test_verificar_clave_acepta_el_hash_en_mayusculas():
    resultado = verificar_clave(
        "Clave123", "a1b2c3d4", "3BAAD75A2E328110D25F895F12ABC632", "MD5"
    )
    assert resultado.datos["correcta"] is True


def test_verificar_clave_rechaza_hash_de_otra_longitud():
    with pytest.raises(ValueError, match="64"):
        verificar_clave("Clave123", "a1b2c3d4", "3baad75a", "SHA-256")


def test_verificar_clave_rechaza_hash_no_hexadecimal():
    with pytest.raises(ValueError, match="hexadecimal"):
        verificar_clave("Clave123", "a1b2c3d4", "z" * 32, "MD5")


def test_verificar_clave_rechaza_campos_vacios():
    with pytest.raises(ValueError):
        verificar_clave("", "a1b2c3d4", "3baad75a2e328110d25f895f12abc632", "MD5")
    with pytest.raises(ValueError):
        verificar_clave("Clave123", "", "3baad75a2e328110d25f895f12abc632", "MD5")
    with pytest.raises(ValueError):
        verificar_clave("Clave123", "a1b2c3d4", "", "MD5")


# ---------------------- Catálogo de ejemplos del módulo 6 ----------------------

EJEMPLOS_MODULO_6 = [e for e in ejemplos.EJEMPLOS if e["id"].startswith("6.")]


def test_el_catalogo_tiene_los_3_submenus_del_modulo_6():
    assert [e["id"] for e in EJEMPLOS_MODULO_6] == ["6.1", "6.2", "6.3"]


@pytest.mark.parametrize("ejemplo", EJEMPLOS_MODULO_6, ids=lambda e: e["id"])
def test_ejemplos_del_modulo_6_dan_el_resultado_esperado(ejemplo):
    funcion = getattr(cripto, ejemplo["funcion"])
    resultado = funcion(**ejemplo["entradas"])
    assert resultado.valor == ejemplo["esperado"]
    assert resultado.datos["correcta"] is True


# ---------------------- Catálogo completo ----------------------


def test_el_catalogo_cubre_los_26_submenus():
    ids = [e["id"] for e in ejemplos.EJEMPLOS]
    assert ids == [
        "1.1", "1.2", "1.3", "1.4", "1.5", "1.6",
        "2.1", "2.2", "2.3", "2.4", "2.5", "2.6", "2.7",
        "3.1", "3.2", "3.3",
        "4.1", "4.2", "4.3",
        "5.1", "5.2", "5.3", "5.4",
        "6.1", "6.2", "6.3",
    ]
