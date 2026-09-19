"""
Numa · documento de entrega
---------------------------
Genera entrega.pdf: qué se entrega, los enlaces de la app y de GitHub, qué
hacer si la app en línea está dormida y cómo ejecutarla en el computador.
Reutiliza las fuentes, colores y escala de pdf_ejemplos.py para que las dos
entregas se vean iguales.

Ejecutar:  python pdf_entrega.py        (escribe entrega.pdf en la raíz)
"""

from pathlib import Path

from fpdf.enums import XPos, YPos

from pdf_ejemplos import (
    AUTORA, CURSO, CUERPO, INTERLINEA, LAVANDA, MALVA, MONO, ORQUIDEA, PORTADA_NOMBRE,
    ROTULO, TINTA, TITULO_MODULO, TITULO_SUBMENU, UNIVERSIDAD, PdfNuma, _formula, _linea,
    _parrafo, _pasos, _salto_si_falta, limpiar,
)

RAIZ = Path(__file__).parent
ENLACE_APP = "https://numa-cripto.streamlit.app"
ENLACE_GITHUB = "https://github.com/leydymf/numa"


def _seccion(pdf: PdfNuma, texto: str) -> None:
    """Título de sección del documento, al tamaño de los submenús del PDF de ejemplos."""
    _salto_si_falta(pdf, 45)
    pdf.ln(7)
    _linea(pdf, texto, "Chakra", "", TITULO_SUBMENU, TINTA, alto=8)
    pdf.ln(2)


def _subtitulo(pdf: PdfNuma, texto: str) -> None:
    _salto_si_falta(pdf, 30)
    pdf.ln(3)
    _linea(pdf, texto, "Chakra", "", ROTULO, TINTA, alto=6.5)
    pdf.ln(0.5)


def _vineta(pdf: PdfNuma, texto: str) -> None:
    """Un punto de lista con sangría colgante."""
    _salto_si_falta(pdf, 14)
    pdf.set_font("Rajdhani", "", CUERPO)
    pdf.set_text_color(*ORQUIDEA)
    pdf.cell(6, INTERLINEA, "•", new_x=XPos.RIGHT, new_y=YPos.TOP)
    pdf.set_text_color(*TINTA)
    pdf.multi_cell(0, INTERLINEA, limpiar(texto), markdown=True, align="L",
                   new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1.5)


def _enlace(pdf: PdfNuma, rotulo: str, url: str) -> None:
    """Rótulo en negrita y la dirección en lavanda, con enlace real en el PDF."""
    pdf.set_font("Rajdhani", "B", CUERPO)
    pdf.set_text_color(*TINTA)
    pdf.write(INTERLINEA + 0.6, f"{rotulo}  ")
    pdf.set_font("PlexMono", "", MONO)
    pdf.set_text_color(*LAVANDA)
    pdf.write(INTERLINEA + 0.6, url, link=url)
    pdf.ln(INTERLINEA + 2)


def _cabecera(pdf: PdfNuma) -> None:
    """La marca y el título del documento, como una portada corta."""
    pdf.add_page()
    centro = pdf.w / 2
    pdf.set_draw_color(*ORQUIDEA)
    pdf.set_line_width(0.8)
    pdf.ellipse(centro - 8, 26, 16, 16)
    pdf.polygon([(centro - 3.2, 40.5), (centro + 3.2, 40.5), (centro + 6.5, 55), (centro - 6.5, 55)])
    pdf.set_y(62)
    _linea(pdf, "Numa", "Chakra", "B", PORTADA_NOMBRE, TINTA, alto=15, align="C")
    _linea(pdf, "Calculadora criptográfica", "Rajdhani", "", TITULO_SUBMENU, MALVA, alto=8, align="C")
    pdf.ln(6)
    _linea(pdf, "Documento de entrega", "Chakra", "", TITULO_MODULO, ORQUIDEA, alto=11, align="C")
    pdf.ln(3)
    _linea(pdf, f"Realizado por {AUTORA}", "Rajdhani", "B", CUERPO, TINTA, alto=6.5, align="C")
    _linea(pdf, f"{UNIVERSIDAD}, clase de {CURSO}", "Rajdhani", "", CUERPO, TINTA, alto=6.5, align="C")
    pdf.ln(4)
    pdf.set_draw_color(*ORQUIDEA)
    pdf.set_line_width(0.4)
    pdf.line(pdf.l_margin, pdf.get_y(), pdf.w - pdf.r_margin, pdf.get_y())


def generar_pdf() -> bytes:
    pdf = PdfNuma()
    pdf.modulo_actual = "Documento de entrega"
    _cabecera(pdf)

    _seccion(pdf, "Qué se entrega")
    _parrafo(pdf, "El proyecto se entrega de tres formas, y las tres contienen lo mismo:")
    pdf.ln(2)
    _pasos(pdf, [
        "**Una carpeta con el código fuente, llamada numa-codigo.** Lista para ejecutar en "
        "cualquier computador con Python. Dentro va el archivo README.md, que explica en detalle cómo instalar y "
        "ejecutar la aplicación, y el archivo ejemplos.pdf, con un ejemplo resuelto y explicado "
        "de cada uno de los 26 submenús.",
        "**La aplicación publicada en internet.** Para usarla sin instalar nada, desde el "
        "navegador.",
        "**El repositorio en GitHub.** Con el mismo código y las mismas instrucciones.",
    ])
    pdf.ln(1)
    _enlace(pdf, "Aplicación en línea:", ENLACE_APP)
    _enlace(pdf, "Repositorio en GitHub:", ENLACE_GITHUB)

    _seccion(pdf, "Si la aplicación en línea no abre de inmediato")
    _parrafo(
        pdf,
        "La aplicación está alojada en Streamlit Community Cloud, un servicio gratuito que pone "
        "a dormir las aplicaciones cuando llevan varios días sin visitas. Puede pasar una de "
        "dos cosas:",
    )
    pdf.ln(2)
    _vineta(
        pdf,
        "Aparece una pantalla en blanco con un círculo girando. Es normal: La aplicación está "
        "arrancando. Espere entre 20 y 40 segundos.",
    )
    _vineta(
        pdf,
        "Aparece un mensaje que dice «This app has gone to sleep» con un botón azul. Pulse el "
        "botón **«Yes, get this app back up!»** y espere alrededor de un minuto. La aplicación "
        "despierta sola y queda lista para usarse.",
    )
    _parrafo(
        pdf,
        "Si después de eso sigue sin abrir, la aplicación se puede ejecutar en el computador con "
        "la carpeta entregada, como se explica a continuación.",
    )

    _seccion(pdf, "Cómo ejecutar la aplicación en el computador")
    _parrafo(
        pdf,
        "Único requisito: Tener instalado Python, versión 3.10 a 3.13. Se descarga de "
        "https://www.python.org/downloads/ y, en Windows, hay que marcar la casilla "
        "«Add python.exe to PATH» durante la instalación. Con Python instalado hay dos opciones.",
    )
    _subtitulo(pdf, "Opción 1, la más sencilla")
    _vineta(pdf, "En Windows: Haga doble clic en el archivo **iniciar_windows.bat** que está en la carpeta.")
    _vineta(
        pdf,
        "En macOS o Linux: Abra una terminal dentro de la carpeta y escriba "
        "**bash iniciar_mac_linux.sh**.",
    )
    _parrafo(
        pdf,
        "La primera vez el script crea un entorno virtual e instala las dos dependencias del "
        "proyecto (Streamlit y fpdf2). Esto tarda un par de minutos y necesita conexión a "
        "internet. Las siguientes veces la aplicación abre de inmediato. Al terminar, el "
        "navegador se abre solo en la dirección http://localhost:8501. Para cerrar la "
        "aplicación basta con cerrar la ventana de la terminal.",
    )
    _subtitulo(pdf, "Opción 2, paso a paso en una terminal abierta dentro de la carpeta")
    _formula(
        pdf,
        "python -m venv .venv\n"
        ".venv\\Scripts\\activate          (en Windows)\n"
        "source .venv/bin/activate       (en macOS o Linux)\n"
        "pip install -r requirements.txt\n"
        "streamlit run app.py",
    )
    pdf.ln(2)
    _parrafo(
        pdf,
        "Estas mismas instrucciones, con más detalle, están en el archivo README.md de la "
        "carpeta y en la página principal del repositorio de GitHub.",
    )

    _seccion(pdf, "El PDF de ejemplos")
    _parrafo(
        pdf,
        "El archivo ejemplos.pdf trae un ejemplo resuelto por cada submenú, con enunciado, "
        "datos, idea del método, procedimiento paso a paso, tabla y comprobación. Se puede "
        "abrir directamente desde la carpeta o descargar desde el botón «Descargar PDF de "
        "ejemplos» de la barra lateral de la aplicación. Los resultados del PDF no están "
        "escritos a mano: Se calculan con el mismo código que usa la aplicación.",
    )
    return bytes(pdf.output())


if __name__ == "__main__":
    (RAIZ / "entrega.pdf").write_bytes(generar_pdf())
    print("Listo: entrega.pdf")
