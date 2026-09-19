"""Prueba de humo de la interfaz con streamlit.testing: la app arranca,
se navega al módulo 1 y el submenú 1.6 calcula el ejemplo del catálogo."""

from pathlib import Path

from streamlit.testing.v1 import AppTest

RUTA_APP = str(Path(__file__).parent.parent / "app.py")

# La primera tabla de la sesión carga pyarrow y puede ser lenta en frío,
# por eso el margen de tiempo es generoso.
TIEMPO_MAXIMO = 60


def test_la_portada_arranca_sin_excepciones():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO).run()
    assert not at.exception


def test_el_modulo_1_se_abre_sin_excepciones():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "1"
    at.run()
    assert not at.exception


def test_el_submenu_16_calcula_el_ejemplo():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "1"
    at.session_state["submenu-1"] = "1.6 Euclides extendido"
    at.run()
    assert not at.exception

    # "Cargar ejemplo" escribe a = 7 y n = 26 en los widgets
    at.button(key="ej-1.6").click().run()
    assert at.session_state["1.6_a"] == 7
    assert at.session_state["1.6_n"] == 26

    # "Calcular inverso" guarda el Resultado del submenú en session_state
    at.button(key="calc-1.6").click().run()
    assert not at.exception
    resultado = at.session_state["res_1.6"]
    assert resultado.valor == "15"
    assert resultado.datos["rondas"] == 4


def test_una_entrada_sin_inverso_muestra_error_y_no_rompe():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "1"
    at.session_state["submenu-1"] = "1.6 Euclides extendido"
    at.session_state["1.6_a"] = 12
    at.session_state["1.6_n"] = 18
    at.run()
    at.button(key="calc-1.6").click().run()
    assert not at.exception
    assert "No existe inverso" in at.session_state["err_1.6"]
    assert len(at.error) == 1


def test_el_modulo_2_se_abre_sin_excepciones():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "2"
    at.run()
    assert not at.exception


def test_el_submenu_26_cifra_y_verifica_el_ejemplo():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "2"
    at.session_state["submenu-2"] = "2.6 Afín"
    at.run()
    assert not at.exception

    # "Cargar ejemplo" escribe HOLA, a = 5 y b = 8 en los widgets
    at.button(key="ej-2.6").click().run()
    assert at.session_state["2.6_texto"] == "HOLA"
    assert at.session_state["2.6_a"] == 5
    assert at.session_state["2.6_b"] == 8

    # "Cifrar mensaje" guarda el Resultado con el inverso hallado por AEE
    at.button(key="calc-2.6").click().run()
    assert not at.exception
    resultado = at.session_state["res_2.6"]
    assert resultado.valor == "PCJI"
    assert resultado.datos["a_inverso"] == 11

    # "Verificar" aplica la operación inversa y recupera HOLA
    at.button(key="verif-2.6").click().run()
    assert not at.exception
    estado, mensaje = at.session_state["ver_2.6"]
    assert estado == "ok"
    assert "HOLA" in mensaje
    assert len(at.success) == 1


def test_una_clave_vernam_de_otra_longitud_muestra_error_y_no_rompe():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "2"
    at.session_state["submenu-2"] = "2.3 Vernam"
    at.session_state["2.3_texto"] = "HOLA"
    at.session_state["2.3_clave"] = "ABC"
    at.run()
    at.button(key="calc-2.3").click().run()
    assert not at.exception
    assert "bytes" in at.session_state["err_2.3"]
    assert len(at.error) == 1


def test_el_modulo_3_se_abre_sin_excepciones():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "3"
    at.run()
    assert not at.exception


def test_el_submenu_32_calcula_el_ejemplo_con_metricas():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "3"
    at.session_state["submenu-3"] = "3.2 RSA"
    at.run()
    assert not at.exception

    # "Cargar ejemplo" escribe p = 61, q = 53, e = 17 y m = 65 en los widgets
    at.button(key="ej-3.2").click().run()
    assert at.session_state["3.2_p"] == 61
    assert at.session_state["3.2_q"] == 53
    assert at.session_state["3.2_e"] == 17
    assert at.session_state["3.2_m"] == 65

    # "Cifrar con RSA" guarda el Resultado con d hallado por AEE
    at.button(key="calc-3.2").click().run()
    assert not at.exception
    resultado = at.session_state["res_3.2"]
    assert resultado.valor == "2790"
    assert resultado.datos["d"] == 2753
    # La fila de métricas muestra n, φ(n) y d
    assert len(at.metric) == 3


def test_un_primo_invalido_en_rsa_muestra_error_y_no_rompe():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "3"
    at.session_state["submenu-3"] = "3.2 RSA"
    at.session_state["3.2_p"] = 10
    at.run()
    at.button(key="calc-3.2").click().run()
    assert not at.exception
    assert "primo" in at.session_state["err_3.2"]
    assert len(at.error) == 1


def test_un_p_no_primo_en_diffie_hellman_avisa_pero_calcula():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "3"
    at.session_state["submenu-3"] = "3.1 Diffie-Hellman"
    at.session_state["3.1_p"] = 15
    at.session_state["3.1_g"] = 2
    at.run()
    at.button(key="calc-3.1").click().run()
    assert not at.exception
    assert "res_3.1" in at.session_state
    assert len(at.warning) == 1


def test_el_modulo_4_se_abre_sin_excepciones():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "4"
    at.run()
    assert not at.exception


def test_el_submenu_41_calcula_el_ejemplo_con_avalancha():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "4"
    at.session_state["submenu-4"] = "4.1 MD5"
    at.run()
    assert not at.exception

    # "Cargar ejemplo" escribe "abc" y el texto de comparación "abd"
    at.button(key="ej-4.1").click().run()
    assert at.session_state["4.1_texto"] == "abc"
    assert at.session_state["4.1_comparar"] == "abd"

    # "Calcular MD5" guarda el hash y las métricas del efecto avalancha
    at.button(key="calc-4.1").click().run()
    assert not at.exception
    resultado = at.session_state["res_4.1"]
    assert resultado.valor == "900150983cd24fb0d6963f7d28e17f72"
    assert resultado.datos["cambios"] > 0
    assert len(at.metric) == 3


def test_el_modulo_5_se_abre_sin_excepciones():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "5"
    at.run()
    assert not at.exception


def test_el_submenu_54_codifica_y_verifica_el_ejemplo():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "5"
    at.session_state["submenu-5"] = "5.4 Base64"
    at.run()
    assert not at.exception

    # "Cargar ejemplo" escribe "Hola" en modo Codificar
    at.button(key="ej-5.4").click().run()
    assert at.session_state["5.4_texto"] == "Hola"

    # "Codificar texto" guarda el Base64 con su tabla de grupos de 6 bits
    at.button(key="calc-5.4").click().run()
    assert not at.exception
    resultado = at.session_state["res_5.4"]
    assert resultado.valor == "SG9sYQ=="

    # "Verificar" decodifica el resultado y recupera "Hola"
    at.button(key="verif-5.4").click().run()
    assert not at.exception
    estado, mensaje = at.session_state["ver_5.4"]
    assert estado == "ok"
    assert "Hola" in mensaje


def test_un_hexadecimal_invalido_en_52_muestra_error_y_no_rompe():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "5"
    at.session_state["submenu-5"] = "5.2 Hexadecimal"
    at.session_state["5.2_modo"] = "Decodificar"
    at.session_state["5.2_texto"] = "XYZ"
    at.run()
    at.button(key="calc-5.2").click().run()
    assert not at.exception
    assert "hexadecimal" in at.session_state["err_5.2"]
    assert len(at.error) == 1


def test_el_modulo_6_se_abre_sin_excepciones():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "6"
    at.run()
    assert not at.exception


def test_el_submenu_61_genera_salts_y_verifica_la_clave():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "6"
    at.session_state["submenu-6"] = "6.1 Salt con MD5"
    at.run()
    assert not at.exception

    # "Generar salts" produce tantas filas como pide la cantidad (3 por defecto)
    at.button(key="calc-6.1").click().run()
    assert not at.exception
    resultado = at.session_state["res_6.1"]
    assert len(resultado.tabla) == 3

    # "Verificar clave" con los valores del ejemplo, precargados por defecto
    at.button(key="verif-6.1").click().run()
    assert not at.exception
    comprobacion = at.session_state["res_6.1v"]
    assert comprobacion.datos["correcta"] is True
    assert len(at.success) == 1


def test_una_clave_incorrecta_en_61_se_reporta_sin_romper():
    at = AppTest.from_file(RUTA_APP, default_timeout=TIEMPO_MAXIMO)
    at.session_state["pagina"] = "6"
    at.session_state["submenu-6"] = "6.1 Salt con MD5"
    at.session_state["6.1_clave_v"] = "OtraClave"
    at.run()
    at.button(key="verif-6.1").click().run()
    assert not at.exception
    comprobacion = at.session_state["res_6.1v"]
    assert comprobacion.datos["correcta"] is False
    assert len(at.error) == 1
