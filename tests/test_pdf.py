"""Pruebas del generador del PDF de ejemplos (pdf_ejemplos.py)."""

import ejemplos
import pdf_ejemplos


def test_el_pdf_se_genera_y_es_un_pdf_valido():
    datos = pdf_ejemplos.generar_pdf()
    assert datos[:5] == b"%PDF-"
    # Portada, índice y 26 secciones con las fuentes incrustadas
    assert len(datos) > 50_000


def test_el_pdf_recorre_todos_los_ejemplos_del_catalogo():
    # Los títulos de los módulos del PDF cubren los 6 módulos del catálogo
    modulos_del_catalogo = {e["id"].split(".")[0] for e in ejemplos.EJEMPLOS}
    assert modulos_del_catalogo == set(pdf_ejemplos.TITULOS_MODULOS)


def test_limpiar_cambia_los_simbolos_sin_glifo():
    assert pdf_ejemplos.limpiar("φ(n)") == "phi(n)"
    assert pdf_ejemplos.limpiar("gᵃ mod p") == "g^a mod p"
    assert pdf_ejemplos.limpiar("3¹³") == "3^13"
    assert pdf_ejemplos.limpiar("a⁻¹") == "a^-1"
    assert pdf_ejemplos.limpiar("C ⊕ K") == "C XOR K"
    assert pdf_ejemplos.limpiar("a + x ≡ 0") == "a + x = 0"


def test_limpiar_no_toca_el_texto_normal():
    texto = "El ñandú corrió al río: MCD(7, 26) = 1"
    assert pdf_ejemplos.limpiar(texto) == texto
