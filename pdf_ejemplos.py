"""
Numa · generador del PDF de ejemplos
------------------------------------
Crea ejemplos.pdf con un ejemplo resuelto por cada uno de los 26 submenús:
los enunciados, entradas y explicaciones salen de ejemplos.py y cada
resultado se calcula en vivo con las funciones de cripto.py, así el PDF
nunca contradice a la app y ningún resultado se escribe a mano.

Ejecutar:  python pdf_ejemplos.py        (escribe ejemplos.pdf en la raíz)
En la app, el botón de la barra lateral llama a generar_pdf() en memoria.
"""

import re
from pathlib import Path

from fpdf import FPDF
from fpdf.enums import XPos, YPos
from fpdf.fonts import FontFace

import cripto
import ejemplos

RAIZ = Path(__file__).parent
FUENTES = RAIZ / "static" / "fuentes"

# Créditos: los usa también app.py, así la barra lateral y el PDF dicen lo mismo
AUTORA = "Leydy Yohana Macareo Fuentes"
UNIVERSIDAD = "UNAB"
CURSO = "Ciberseguridad"

# Versión clara para imprimir: texto tinta sobre fondo blanco y los dos
# acentos neón del sistema Numa. La menta de pantalla es muy clara sobre
# blanco, así que la comprobación va en un verde de imprenta.
TINTA = (18, 8, 20)        # #120814
ORQUIDEA = (255, 79, 168)  # #FF4FA8
LAVANDA = (192, 140, 255)  # #C08CFF
MALVA = (74, 46, 82)       # #4A2E52, texto secundario
NACAR = (246, 233, 242)    # #F6E9F2, relleno de cajas y encabezados de tabla
BORDE = (233, 220, 238)    # rejilla de las tablas, un malva muy claro
VERDE = (30, 138, 106)     # comprobaciones

# Escala tipográfica, en puntos: pocas medidas y siempre las mismas
PORTADA_NOMBRE = 34
TITULO_MODULO = 20
TITULO_SUBMENU = 14
ROTULO = 11.5      # Enunciado, Datos, Idea del método, Procedimiento, Tabla, Resultado
CUERPO = 10.5
MONO = 9.5
TABLA = 9
PEQUENA = 8.5      # cabecera, pie y notas de tabla
INTERLINEA = 5.6   # alto de renglón del cuerpo, en mm

TITULOS_MODULOS = {
    "1": "Matemática modular",
    "2": "Criptografía clásica",
    "3": "Criptografía moderna",
    "4": "Algoritmos hash",
    "5": "Codificación",
    "6": "Uso de salt",
}

# Un párrafo de presentación por módulo, antes de sus ejemplos
INTRO_MODULOS = {
    "1": "La aritmética modular trabaja con residuos: Dos números son «iguales módulo n» "
    "cuando dejan el mismo residuo al dividirlos entre n. De aquí salen el inverso aditivo, "
    "el inverso multiplicativo, el máximo común divisor y el algoritmo extendido de Euclides, "
    "las herramientas que después usan los cifrados clásicos y RSA.",
    "2": "Los cifrados clásicos transforman letras: Las desplazan (módulo 27 y César), las "
    "reflejan (Atbash), las multiplican (afín), las sustituyen (sustitución simple) o cambian "
    "su orden (transposición). Vernam trabaja con bits. Todos usan el alfabeto español de 27 "
    "letras salvo que se indique lo contrario, y todos se deshacen con la operación inversa.",
    "3": "La criptografía moderna se apoya en problemas matemáticos difíciles: El logaritmo "
    "discreto (Diffie-Hellman) y la factorización de números grandes (RSA). La exponenciación "
    "rápida es la herramienta que hace posibles esas potencias enormes módulo n con pocas "
    "multiplicaciones.",
    "4": "Una función hash resume cualquier texto en una huella de tamaño fijo: Siempre la "
    "misma para el mismo texto, imposible de invertir y muy sensible a cualquier cambio (efecto "
    "avalancha). MD5, SHA-256 y SHA-512 se diferencian en el tamaño de la huella y en su "
    "seguridad.",
    "5": "Codificar no es cifrar: No hay clave ni secreto, solo una forma distinta de escribir "
    "los mismos bytes. ASCII, hexadecimal, binario y Base64 son representaciones que cualquiera "
    "puede deshacer y aparecen por todas partes en informática y en seguridad.",
    "6": "Las claves de los usuarios no se guardan en claro ni con un hash simple: Se les añade "
    "un salt aleatorio y único antes de calcular el hash. Así dos usuarios con la misma clave "
    "tienen hashes distintos y las tablas precalculadas de hashes dejan de servir.",
}

# Símbolos que las fuentes TTF no traen, con su versión imprimible.
# Los superíndices seguidos se agrupan bajo un solo ^: 3¹³ -> 3^13.
SUPERINDICES = {
    "⁰": "0", "¹": "1", "²": "2", "³": "3", "⁴": "4",
    "⁵": "5", "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9",
    "ᵃ": "a", "ᵇ": "b", "ᶜ": "c", "ᵈ": "d", "ᵉ": "e",
    "ᵏ": "k", "ᵐ": "m", "ⁿ": "n", "ᵖ": "p", "ˣ": "x", "⁻": "-",
}
REEMPLAZOS = {
    "φ": "phi",
    "⊕": "XOR",
    "≡": "=",
    "→": "->",
    "↔": "<->",
    "⇒": "=>",
    "₂": " (bin)",
    "−": "-",
    "≤": "<=",
    "≥": ">=",
    "✓": "",
}

# Cada paso de cripto.py empieza con su título en negrita: "**Título.** texto"
PATRON_PASO = re.compile(r"^\*\*(.+?)\*\*\s*(.*)$", re.S)

# Un valor numérico o el guion de las filas de inicio: la columna va a la derecha
PATRON_NUMERO = re.compile(r"^-?\d+$|^—$")


def limpiar(texto: str) -> str:
    """Cambia los símbolos sin glifo en las fuentes por texto plano:
    φ(n) -> phi(n), gᵃ -> g^a, 3¹³ -> 3^13, ⊕ -> XOR."""
    piezas = []
    en_superindice = False
    for caracter in str(texto):
        if caracter in SUPERINDICES:
            if not en_superindice:
                piezas.append("^")
                en_superindice = True
            piezas.append(SUPERINDICES[caracter])
            continue
        en_superindice = False
        piezas.append(REEMPLAZOS.get(caracter, caracter))
    return "".join(piezas)


class PdfNuma(FPDF):
    """Página A4 con las fuentes del proyecto. La portada va sin encabezado
    ni número de página; el resto lleva el nombre del módulo en curso."""

    def __init__(self):
        super().__init__(format="A4")
        self.set_margins(22, 24, 22)
        self.set_auto_page_break(True, margin=20)
        self.modulo_actual = ""
        # Fuentes estáticas (un archivo por grosor), registradas tal cual
        self.add_font("Chakra", "", FUENTES / "ChakraPetch-SemiBold.ttf")
        self.add_font("Chakra", "B", FUENTES / "ChakraPetch-Bold.ttf")
        self.add_font("Rajdhani", "", FUENTES / "Rajdhani-Medium.ttf")
        self.add_font("Rajdhani", "B", FUENTES / "Rajdhani-SemiBold.ttf")
        self.add_font("PlexMono", "", FUENTES / "IBMPlexMono-Regular.ttf")
        self.add_font("PlexMono", "B", FUENTES / "IBMPlexMono-Medium.ttf")

    def header(self):
        if self.page_no() == 1:
            return
        self.set_y(11)
        self.set_font("Chakra", "", PEQUENA)
        self.set_text_color(*MALVA)
        self.cell(0, 6, "Numa, calculadora criptográfica", align="L", new_x=XPos.LMARGIN, new_y=YPos.TOP)
        self.set_font("Rajdhani", "", PEQUENA)
        self.cell(0, 6, self.modulo_actual, align="R")
        self.set_draw_color(*ORQUIDEA)
        self.set_line_width(0.4)
        self.line(self.l_margin, 18.5, self.w - self.r_margin, 18.5)
        self.set_y(self.t_margin)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-14)
        self.set_font("Rajdhani", "", PEQUENA)
        self.set_text_color(*MALVA)
        self.cell(0, 6, f"Página {self.page_no()}", align="C")

    def espacio_libre(self) -> float:
        """Milímetros que quedan hasta el margen inferior."""
        return self.h - self.b_margin - self.get_y()


# ------------------------------ Piezas de texto ------------------------------


def _salto_si_falta(pdf: PdfNuma, minimo: float) -> None:
    """Pasa de página si no queda sitio para un bloque de `minimo` mm, así
    un rótulo o una caja no quedan huérfanos al final de la página."""
    if pdf.espacio_libre() < minimo:
        pdf.add_page()


def _linea(pdf: PdfNuma, texto: str, fuente: str, estilo: str, tamano: float,
           color: tuple, alto: float = INTERLINEA, align: str = "L",
           markdown: bool = False) -> None:
    """Un párrafo que baja el cursor al renglón siguiente. Con markdown=True,
    lo que va entre ** ** sale en negrita (los títulos de los pasos)."""
    pdf.set_font(fuente, estilo, tamano)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, alto, limpiar(texto), align=align, markdown=markdown,
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _parrafo(pdf: PdfNuma, texto: str, color: tuple = TINTA) -> None:
    _linea(pdf, texto, "Rajdhani", "", CUERPO, color)


def _rotulo(pdf: PdfNuma, texto: str) -> None:
    """Rótulo de cada parte de la sección: Enunciado, Datos, Idea del método…
    Va por encima del cuerpo en tamaño, para que la jerarquía se lea de un vistazo."""
    _salto_si_falta(pdf, 28)
    pdf.ln(4.5)
    _linea(pdf, texto, "Chakra", "", ROTULO, TINTA, alto=6.5)
    pdf.ln(0.5)


def _titulo_modulo(pdf: PdfNuma, numero: str, titulo: str) -> None:
    pdf.set_font("Chakra", "B", TITULO_MODULO)
    pdf.set_text_color(*LAVANDA)
    pdf.write(11, f"{numero}  ")
    pdf.set_text_color(*TINTA)
    pdf.write(11, titulo)
    pdf.ln(14)
    _parrafo(pdf, INTRO_MODULOS[numero], MALVA)
    pdf.ln(7)


def _titulo_submenu(pdf: PdfNuma, id_ejemplo: str, titulo: str) -> None:
    pdf.set_font("Chakra", "", TITULO_SUBMENU)
    pdf.set_text_color(*ORQUIDEA)
    pdf.write(8, f"{id_ejemplo}  ")
    pdf.set_text_color(*TINTA)
    pdf.write(8, limpiar(titulo))
    pdf.ln(10)


def _formula(pdf: PdfNuma, texto: str) -> None:
    """La fórmula del método en monoespaciada, con un filo de nácar."""
    pdf.set_fill_color(*NACAR)
    pdf.set_font("PlexMono", "", MONO)
    pdf.set_text_color(*TINTA)
    pdf.multi_cell(0, INTERLINEA, limpiar(texto), fill=True, padding=(3, 4, 3, 4), align="L",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def _pasos(pdf: PdfNuma, pasos: list[str]) -> None:
    """Procedimiento numerado: El número en orquídea y el texto con sangría
    colgante, para que las líneas largas no tapen la numeración."""
    ancho_numero = 8
    for numero, paso in enumerate(pasos, start=1):
        _salto_si_falta(pdf, 14)
        pdf.set_font("Chakra", "B", CUERPO)
        pdf.set_text_color(*ORQUIDEA)
        pdf.cell(ancho_numero, INTERLINEA, f"{numero}.", new_x=XPos.RIGHT, new_y=YPos.TOP)
        pdf.set_font("Rajdhani", "", CUERPO)
        pdf.set_text_color(*TINTA)
        pdf.multi_cell(0, INTERLINEA, limpiar(paso), markdown=True, align="L",
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(2.2)


def _bloque_mono(pdf: PdfNuma, texto: str, color: tuple = TINTA) -> None:
    """Texto monoespaciado sobre nácar (bits alineados, hashes). Reduce el
    cuerpo hasta que la línea más larga quepa completa."""
    texto = limpiar(texto)
    ancho_util = pdf.w - pdf.l_margin - pdf.r_margin - 6
    mas_larga = max(len(linea) for linea in texto.split("\n"))
    # Ancho aproximado de un carácter monoespaciado: 0.63 · tamaño en puntos.
    # Por debajo de 8 puntos ya no se lee: entonces la línea se parte en vez de encoger
    ajustado = ancho_util / (mas_larga * 0.63 * 0.3528)
    tamano = max(min(MONO, ajustado), 8)
    modo = "WORD" if ajustado >= 8 else "CHAR"
    pdf.set_fill_color(*NACAR)
    pdf.set_font("PlexMono", "", tamano)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, tamano * 0.55, texto, fill=True, padding=(2.5, 3, 2.5, 3), align="L",
                   wrapmode=modo, new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ------------------------------ Tablas ------------------------------


def _tabla_datos(pdf: PdfNuma, entradas: dict, campos: dict) -> None:
    """Las entradas del ejemplo en dos columnas: Nombre del campo y valor."""
    filas = [(campos.get(campo, campo), valor) for campo, valor in entradas.items() if valor != ""]
    pdf.set_fill_color(255, 255, 255)  # las filas van en blanco (fpdf2 usa el relleno vigente)
    pdf.set_font("Rajdhani", "", CUERPO)
    pdf.set_text_color(*TINTA)
    pdf.set_draw_color(*BORDE)
    pdf.set_line_width(0.2)
    estilo_campo = FontFace(family="Rajdhani", emphasis="BOLD", size_pt=CUERPO, color=TINTA)
    estilo_valor = FontFace(family="PlexMono", size_pt=MONO, color=TINTA)
    with pdf.table(
        col_widths=(2, 5),
        first_row_as_headings=False,
        line_height=6.4,
        padding=(1.2, 2.5),
        borders_layout="HORIZONTAL_LINES",
    ) as tabla:
        for nombre, valor in filas:
            fila = tabla.row()
            fila.cell(limpiar(nombre), style=estilo_campo)
            fila.cell(limpiar(str(valor)), style=estilo_valor)


def _tabla(pdf: PdfNuma, filas: list[dict], nota: str | None = None) -> None:
    """Tabla del resultado: Encabezado en nácar, números a la derecha y
    todas las filas (si no caben en la página, sigue en la siguiente)."""
    encabezados = list(filas[0].keys())

    def largo(valor) -> int:
        return len(limpiar(str(valor)))

    # Columnas proporcionales al contenido más largo, con tope para que un
    # hash no aplaste al resto
    anchos = tuple(
        min(max(6, largo(encabezado), *(largo(fila.get(encabezado, "")) for fila in filas)), 40)
        for encabezado in encabezados
    )
    alineacion = tuple(
        "RIGHT" if all(PATRON_NUMERO.match(limpiar(str(fila.get(encabezado, "")))) for fila in filas) else "LEFT"
        for encabezado in encabezados
    )
    pdf.set_fill_color(255, 255, 255)  # las filas van en blanco (fpdf2 usa el relleno vigente)
    # Con muchas columnas (la tabla de correspondencias de 2.7 tiene 27) el
    # cuerpo baja y el relleno se estrecha para que quepan en el ancho de página
    muchas_columnas = len(encabezados) > 12
    tamano = 7.5 if muchas_columnas else TABLA
    relleno = (1, 0.6) if muchas_columnas else (1.2, 2)
    pdf.set_font("PlexMono", "", tamano)
    pdf.set_text_color(*TINTA)
    pdf.set_draw_color(*BORDE)
    pdf.set_line_width(0.2)
    estilo_encabezado = FontFace(
        family="Rajdhani", emphasis="BOLD", size_pt=tamano, color=TINTA, fill_color=NACAR
    )
    with pdf.table(
        col_widths=anchos,
        text_align=alineacion,
        line_height=5.8,
        headings_style=estilo_encabezado,
        padding=relleno,
        borders_layout="HORIZONTAL_LINES",
    ) as tabla:
        fila_titulos = tabla.row()
        for encabezado in encabezados:
            fila_titulos.cell(limpiar(encabezado))
        for fila in filas:
            celdas = tabla.row()
            for encabezado in encabezados:
                celdas.cell(limpiar(str(fila.get(encabezado, ""))))
    if nota:
        pdf.ln(2)
        _linea(pdf, nota, "Rajdhani", "", PEQUENA, MALVA, alto=4.6)


# ------------------------------ Caja de resultado ------------------------------


def _caja_resultado(pdf: PdfNuma, valor: str, verificacion: str | None) -> None:
    """El resultado final sobre nácar con una barra de orquídea a la
    izquierda; debajo, la comprobación en verde."""
    _salto_si_falta(pdf, 40)
    pdf.ln(5)
    y_inicio = pdf.get_y()
    pdf.set_fill_color(*NACAR)
    pdf.set_font("Chakra", "", ROTULO)
    pdf.set_text_color(*TINTA)
    pdf.multi_cell(0, 6.5, "Resultado", fill=True, padding=(3, 4, 0.5, 6),
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    texto = limpiar(valor)
    if len(texto) > 24 or "\n" in texto:
        pdf.set_font("PlexMono", "B", MONO)
        alto = 5.2
    else:
        pdf.set_font("Chakra", "B", TITULO_SUBMENU)
        alto = 8
    pdf.set_text_color(*ORQUIDEA)
    pdf.multi_cell(0, alto, texto, fill=True, padding=(0.5, 4, 2, 6), wrapmode="CHAR",
                   align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    if verificacion:
        pdf.set_font("Rajdhani", "", CUERPO)
        pdf.set_text_color(*VERDE)
        pdf.multi_cell(0, INTERLINEA, "Comprobación: " + limpiar(verificacion), fill=True,
                       padding=(0, 4, 3, 6), align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    else:
        pdf.multi_cell(0, 1, "", fill=True, padding=(0, 0, 1.5, 0),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_fill_color(*ORQUIDEA)
    pdf.rect(pdf.l_margin, y_inicio, 1.4, pdf.get_y() - y_inicio, style="F")


# ------------------------------ Portada e índice ------------------------------


def _portada(pdf: PdfNuma) -> None:
    pdf.add_page()

    # La cerradura de la marca, dibujada con las primitivas de fpdf2
    centro = pdf.w / 2
    pdf.set_draw_color(*ORQUIDEA)
    pdf.set_line_width(0.9)
    pdf.ellipse(centro - 11, 44, 22, 22)
    pdf.polygon([(centro - 4.5, 64), (centro + 4.5, 64), (centro + 9, 84), (centro - 9, 84)])

    pdf.set_y(96)
    _linea(pdf, "Numa", "Chakra", "B", PORTADA_NOMBRE, TINTA, alto=16, align="C")
    _linea(pdf, "Calculadora criptográfica", "Rajdhani", "", TITULO_SUBMENU, MALVA, alto=8, align="C")
    pdf.ln(12)
    _linea(pdf, "Ejemplos resueltos", "Chakra", "", TITULO_MODULO, ORQUIDEA, alto=11, align="C")
    _linea(
        pdf,
        "Un ejemplo explicado por cada uno de los 26 submenús de la calculadora: "
        "Enunciado, datos, idea del método, procedimiento paso a paso, tabla y comprobación. "
        "Todos los resultados se calculan con el mismo código que usa la app.",
        "Rajdhani", "", CUERPO, TINTA, align="C",
    )
    pdf.ln(18)
    _linea(pdf, f"Realizado por {AUTORA}", "Rajdhani", "B", CUERPO, TINTA, alto=6.5, align="C")
    _linea(pdf, f"{UNIVERSIDAD}, clase de {CURSO}", "Rajdhani", "", CUERPO, TINTA, alto=6.5, align="C")


def _indice(pdf: PdfNuma, outline) -> None:
    """Dibuja el índice en la página reservada por insert_toc_placeholder."""
    # El cursor llega con la x del pie de la última página; se reinicia
    pdf.set_x(pdf.l_margin)
    _linea(pdf, "Índice", "Chakra", "B", TITULO_MODULO, TINTA, alto=12)
    pdf.ln(1)
    _linea(
        pdf,
        "Cada ejemplo tiene seis partes: Enunciado, Datos, Idea del método, Procedimiento, "
        "Tabla y Resultado con su comprobación. Los resultados no están escritos a mano: se "
        "calculan con el mismo código de la calculadora.",
        "Rajdhani", "", CUERPO, MALVA,
    )
    pdf.ln(6)
    for seccion in outline:
        if seccion.level == 0:
            pdf.ln(2)
            pdf.set_font("Rajdhani", "B", CUERPO)
            pdf.set_text_color(*TINTA)
            alto = 6.5
            sangria = 0.0
        else:
            pdf.set_font("Rajdhani", "", CUERPO)
            pdf.set_text_color(*MALVA)
            alto = 5.6
            sangria = 8.0
        if sangria:
            pdf.cell(sangria, alto, "")
        pdf.cell(150 - sangria, alto, limpiar(seccion.name))
        pdf.cell(0, alto, str(seccion.page_number), align="R",
                 new_x=XPos.LMARGIN, new_y=YPos.NEXT)


# ------------------------------ Una sección por ejemplo ------------------------------


def _seccion_ejemplo(pdf: PdfNuma, ejemplo: dict) -> None:
    """Enunciado, datos, idea y fórmula, procedimiento, tablas y resultado
    con su comprobación. Todo sale de cripto.py en vivo."""
    resultado = getattr(cripto, ejemplo["funcion"])(**ejemplo["entradas"])

    # Si no queda sitio ni para el título y el enunciado, página nueva
    _salto_si_falta(pdf, 70)
    pdf.start_section(f"{ejemplo['id']}  {ejemplo['titulo']}", level=1)
    _titulo_submenu(pdf, ejemplo["id"], ejemplo["titulo"])

    _rotulo(pdf, "Enunciado")
    _parrafo(pdf, ejemplo["enunciado"])

    _rotulo(pdf, "Datos")
    _tabla_datos(pdf, ejemplo["entradas"], ejemplo["campos"])

    _rotulo(pdf, "Idea del método")
    _parrafo(pdf, ejemplo["concepto"])
    pdf.ln(1.5)
    _formula(pdf, ejemplo["formula"])

    _rotulo(pdf, "Procedimiento")
    _pasos(pdf, resultado.pasos)

    if alineado := resultado.datos.get("alineado"):
        _rotulo(pdf, "Detalle")
        _bloque_mono(pdf, alineado)
    if codigo := resultado.datos.get("codigo"):
        if codigo != resultado.valor:
            _rotulo(pdf, "Detalle")
            _bloque_mono(pdf, codigo)

    if resultado.tabla:
        _rotulo(pdf, "Tabla")
        _tabla(pdf, resultado.tabla, resultado.datos.get("nota_tabla"))
    if extra := resultado.datos.get("tabla_extra"):
        _rotulo(pdf, extra["titulo"])
        _tabla(pdf, extra["filas"], extra.get("nota"))

    _caja_resultado(pdf, resultado.valor, resultado.verificacion)
    pdf.ln(12)


def generar_pdf() -> bytes:
    """Arma el PDF completo y lo devuelve como bytes, listo para guardar
    en disco o para el st.download_button de la app."""
    pdf = PdfNuma()
    _portada(pdf)

    pdf.modulo_actual = "Índice"
    pdf.add_page()
    # El marcador del índice crea también la página siguiente, la del módulo 1,
    # y la cabecera se dibuja al crearla: el nombre del módulo va antes
    primer_numero, primer_titulo = next(iter(TITULOS_MODULOS.items()))
    pdf.modulo_actual = f"Módulo {primer_numero}: {primer_titulo}"
    pdf.insert_toc_placeholder(_indice, pages=1, allow_extra_pages=True)

    for posicion, (numero, titulo) in enumerate(TITULOS_MODULOS.items()):
        pdf.modulo_actual = f"Módulo {numero}: {titulo}"
        # insert_toc_placeholder ya dejó lista la página del primer módulo
        if posicion:
            pdf.add_page()
        pdf.start_section(f"Módulo {numero}: {titulo}", level=0)
        _titulo_modulo(pdf, numero, titulo)
        for ejemplo in (e for e in ejemplos.EJEMPLOS if e["id"].startswith(f"{numero}.")):
            _seccion_ejemplo(pdf, ejemplo)

    return bytes(pdf.output())


if __name__ == "__main__":
    (RAIZ / "ejemplos.pdf").write_bytes(generar_pdf())
    print("Listo: ejemplos.pdf")
