"""
Numa · Calculadora criptográfica
--------------------------------
Interfaz de la calculadora: Navegación, portada y páginas de los 6 módulos.
La lógica de las operaciones vive en cripto.py; este es el único archivo
que importa streamlit.

Ejecutar:  streamlit run app.py
"""

import html
import re
from pathlib import Path

# pandas ya viene con Streamlit; aquí solo sirve para resaltar una fila de tabla
import pandas as pd
import streamlit as st

import cripto
import ejemplos
import pdf_ejemplos

RAIZ = Path(__file__).parent

st.set_page_config(page_title="Numa · Calculadora criptográfica", page_icon="🔐", layout="wide")

# Estilos propios (lo que config.toml no alcanza a personalizar)
st.html(f"<style>{(RAIZ / 'estilos.css').read_text(encoding='utf-8')}</style>")

# ----------------------------------------------------------------------
# Estructura de la app: módulos, submenús y la fase en que se construyen
# ----------------------------------------------------------------------

MODULOS = {
    "1": {
        "titulo": "Matemática modular",
        "descripcion": "Módulo, inversos, MCD y Euclides extendido con tabla",
        "fase": 2,
        "submenus": [
            ("1.1", "Módulo"),
            ("1.2", "Inverso aditivo"),
            ("1.3", "Inverso de XOR"),
            ("1.4", "MCD"),
            ("1.5", "Inverso tradicional"),
            ("1.6", "Euclides extendido"),
        ],
    },
    "2": {
        "titulo": "Criptografía clásica",
        "descripcion": "Módulo 27, César, Vernam, Atbash, columnar, afín y sustitución",
        "fase": 3,
        "submenus": [
            ("2.1", "Módulo 27"),
            ("2.2", "César"),
            ("2.3", "Vernam"),
            ("2.4", "Atbash"),
            ("2.5", "Transposición columnar"),
            ("2.6", "Afín"),
            ("2.7", "Sustitución simple"),
        ],
    },
    "3": {
        "titulo": "Criptografía moderna",
        "descripcion": "Diffie-Hellman, RSA y exponenciación rápida",
        "fase": 4,
        "submenus": [
            ("3.1", "Diffie-Hellman"),
            ("3.2", "RSA"),
            ("3.3", "Exponenciación rápida"),
        ],
    },
    "4": {
        "titulo": "Algoritmos hash",
        "descripcion": "MD5, SHA-256 y SHA-512 con efecto avalancha",
        "fase": 5,
        "submenus": [
            ("4.1", "MD5"),
            ("4.2", "SHA-256"),
            ("4.3", "SHA-512"),
        ],
    },
    "5": {
        "titulo": "Codificación",
        "descripcion": "ASCII, hexadecimal, binario y Base64",
        "fase": 5,
        "submenus": [
            ("5.1", "ASCII"),
            ("5.2", "Hexadecimal"),
            ("5.3", "Binario"),
            ("5.4", "Base64"),
        ],
    },
    "6": {
        "titulo": "Uso de salt",
        "descripcion": "La misma clave con hashes distintos gracias al salt",
        "fase": 5,
        "submenus": [
            ("6.1", "Salt con MD5"),
            ("6.2", "Salt con SHA-256"),
            ("6.3", "Salt con SHA-512"),
        ],
    },
}

# Créditos del proyecto (los define pdf_ejemplos.py para que el PDF diga lo mismo)
AUTORA = pdf_ejemplos.AUTORA
UNIVERSIDAD = pdf_ejemplos.UNIVERSIDAD
CURSO = pdf_ejemplos.CURSO


@st.cache_data(show_spinner="Generando el PDF de ejemplos…")
def pdf_de_ejemplos() -> bytes:
    """El PDF se arma en memoria una sola vez y queda en caché para el
    botón de descarga de la barra lateral."""
    return pdf_ejemplos.generar_pdf()

# ------------------------------- Portada -------------------------------

# Fondo de la cerradura: 15 líneas de texto cifrado, hex, binario y base64
LINEAS_CIFRADAS = [
    "4E554D41 2043414C 43554C41 444F5241",
    "01001000 01101111 01101100 01100001",
    "U2VjcmV0b3MgZGUgbGEgbm9jaGU=",
    "19 08 15 22 04 11 04 25 24 01 07 12",
    "KRÑD PCJI SLOZ AKDM KROD XMCK",
    "486F6C61 20636966 7261646F 206E656F",
    "11010010 00101101 10011100 01100110",
    "bWlyYSBwb3IgbGEgY2VycmFkdXJh",
    "3B AA D7 5A 2E 32 81 10 D2 5F 89 5F",
    "A=8  B=19  K=2  n=3233  d=2753",
    "01010011 01100101 01100011 01110010",
    "TnVtYSBjYWxjdWxhZG9yYQ==",
    "90015098 3CD24FB0 D6963F7D 28E17F72",
    "10 02 0F 0A 1D 00 13 25 0C 09 16 04",
    "01001110 01110101 01101101 01100001",
]

CERRADURA_HTML = f"""
<div aria-hidden="true" style="position:relative;width:340px;height:360px;margin:0 auto">
  <div style="position:absolute;left:20px;top:20px;width:300px;height:340px;
              border-radius:150px 150px 0 0;overflow:hidden;text-align:center;
              font-family:plexmono,Consolas,monospace;font-size:12.5px;
              line-height:1.8;color:#5B3F66;white-space:nowrap">
    {"<br>".join(LINEAS_CIFRADAS)}
  </div>
  <svg width="340" height="360" viewBox="0 0 340 360"
       style="position:absolute;inset:0;overflow:visible;filter:drop-shadow(0 0 7px #FF4FA8)">
    <path d="M20 360 V170 A150 150 0 0 1 320 170 V360" fill="none" stroke="#FF4FA8" stroke-width="2"/>
    <path d="M150 219 A44 44 0 1 1 190 219 L206 300 H134 Z" fill="#120814"
          stroke="#FF4FA8" stroke-width="2" stroke-linejoin="round"/>
  </svg>
  <div style="position:absolute;top:160px;left:0;width:100%;text-align:center;
              font-family:chakrapetch,'Segoe UI',sans-serif;font-weight:700;font-size:28px;letter-spacing:.04em;
              color:#FFB38A;text-shadow:0 0 16px rgba(255,179,138,.45)">Hola</div>
</div>
"""

# ------------------------------ Navegación ------------------------------

if "pagina" not in st.session_state:
    st.session_state.pagina = "inicio"


def ir_a(pagina: str) -> None:
    """Cambia de página. Se usa como on_click para que el cambio ocurra
    antes de que Streamlit vuelva a dibujar la app."""
    st.session_state.pagina = pagina


# La marca lleva un SVG y va por st.markdown: st.html elimina los <svg>
MARCA_HTML = (
    '<div class="marca">'
    '<svg width="26" height="26" viewBox="0 0 28 28" aria-hidden="true">'
    '<path d="M11 16 A5 5 0 1 1 17 16 L18.5 23 H9.5 Z" fill="none" '
    'stroke="#FF4FA8" stroke-width="1.8" stroke-linejoin="round"/>'
    '</svg><span class="marca-nombre">Numa</span></div>'
    '<div class="marca-lema">Calculadora criptográfica</div>'
)

with st.sidebar:
    st.markdown(MARCA_HTML, unsafe_allow_html=True)

    st.html('<div class="nav-titulo">Módulos</div>')
    # Los ítems del menú van pegados (gap=None) y alineados a la izquierda
    # desde estilos.css; el activo (type="primary") lleva la barra de neón
    with st.container(key="nav", gap=None):
        activa = st.session_state.pagina == "inicio"
        st.button(
            "Inicio",
            key="nav-inicio",
            icon=":material/home:",
            on_click=ir_a,
            args=("inicio",),
            type="primary" if activa else "tertiary",
            width="stretch",
        )
        for numero, modulo in MODULOS.items():
            activa = st.session_state.pagina == numero
            st.button(
                f"**{numero}** · {modulo['titulo']}",
                key=f"nav-{numero}",
                on_click=ir_a,
                args=(numero,),
                type="primary" if activa else "tertiary",
                width="stretch",
            )

    st.html(
        '<div class="creditos">'
        '<div class="creditos-rotulo">Realizado por</div>'
        f'<div class="creditos-nombre">{html.escape(AUTORA)}</div>'
        f'<div class="creditos-detalle">{html.escape(UNIVERSIDAD)} · {html.escape(CURSO)}</div>'
        "</div>"
    )
    st.download_button(
        "Descargar PDF de ejemplos",
        data=pdf_de_ejemplos(),
        file_name="ejemplos.pdf",
        mime="application/pdf",
        key="boton-pdf",
        width="stretch",
        help="Un ejemplo resuelto por cada submenú, calculado con el mismo código de la app.",
    )

# ---------------------- Piezas comunes de los submenús ----------------------
#
# Cada submenú guarda su estado en st.session_state con estas claves:
#   res_<id>   el Resultado de la última operación (persiste entre reruns)
#   err_<id>   el mensaje del último ValueError, si lo hubo
#   ver_<id>   el estado del botón "Verificar": ("ok" | "error", mensaje)
#   <id>_<campo>  el valor de cada widget del formulario, p. ej. "1.6_a"


def cargar_ejemplo(sid: str) -> None:
    """Escribe las entradas del ejemplo del catálogo en los widgets del submenú.
    Se usa como on_click para que corra antes de que los widgets se dibujen."""
    for campo, valor in ejemplos.buscar(sid)["entradas"].items():
        st.session_state[f"{sid}_{campo}"] = valor


def calcular(sid: str, funcion, **entradas) -> None:
    """Ejecuta una operación de cripto.py y guarda el resultado o el error."""
    # La verificación anterior deja de valer en cuanto hay un cálculo nuevo
    st.session_state.pop(f"ver_{sid}", None)
    try:
        st.session_state[f"res_{sid}"] = funcion(**entradas)
        st.session_state.pop(f"err_{sid}", None)
    except ValueError as error:
        st.session_state[f"err_{sid}"] = str(error)
        st.session_state.pop(f"res_{sid}", None)


def botones_accion(sid: str, etiqueta: str) -> bool:
    """Botón primario del submenú y botón "Cargar ejemplo", lado a lado.
    Devuelve True cuando hay que calcular."""
    col_calcular, col_ejemplo = st.columns(2)
    pulsado = col_calcular.button(etiqueta, key=f"calc-{sid}", type="primary", width="stretch")
    col_ejemplo.button(
        "Cargar ejemplo",
        key=f"ej-{sid}",
        on_click=cargar_ejemplo,
        args=(sid,),
        width="stretch",
    )
    return pulsado


def verificar_cifrador(sid: str) -> None:
    """Ejecuta la receta de verificación del último resultado: Aplica la
    operación inversa y comprueba que se recupera el original."""
    resultado = st.session_state.get(f"res_{sid}")
    if resultado is None:
        return
    receta = resultado.datos["verificar"]
    try:
        vuelta = getattr(cripto, receta["funcion"])(**receta["entradas"])
    except ValueError as error:
        st.session_state[f"ver_{sid}"] = ("error", f"La verificación falló: {error}")
        return
    if vuelta.valor == receta["esperado"]:
        st.session_state[f"ver_{sid}"] = (
            "ok",
            f"Verificado: Al {receta['descripcion']} se recupera «{receta['esperado']}».",
        )
    else:
        st.session_state[f"ver_{sid}"] = (
            "error",
            f"La verificación no cuadra: Al {receta['descripcion']} salió "
            f"«{vuelta.valor}» y se esperaba «{receta['esperado']}».",
        )


def botones_cifrador(sid: str, etiqueta: str, funcion, campos: tuple) -> None:
    """Los tres botones de un cifrador: La acción principal, "Cargar ejemplo"
    y "Verificar". La acción principal calcula en un on_click para que el
    resultado exista antes de dibujar la tarjeta y de habilitar Verificar."""

    def ejecutar() -> None:
        entradas = {campo: st.session_state[f"{sid}_{campo}"] for campo in campos}
        calcular(sid, funcion, **entradas)

    col_calcular, col_ejemplo, col_verificar = st.columns(3)
    col_calcular.button(etiqueta, key=f"calc-{sid}", type="primary", on_click=ejecutar, width="stretch")
    col_ejemplo.button(
        "Cargar ejemplo",
        key=f"ej-{sid}",
        on_click=cargar_ejemplo,
        args=(sid,),
        width="stretch",
    )
    col_verificar.button(
        "Verificar",
        key=f"verif-{sid}",
        on_click=verificar_cifrador,
        args=(sid,),
        disabled=f"res_{sid}" not in st.session_state,
        help="Aplica la operación inversa y comprueba que se recupera el original.",
        width="stretch",
    )


def mostrar_error(sid: str) -> None:
    """Muestra el último error del submenú, si lo hay."""
    if mensaje := st.session_state.get(f"err_{sid}"):
        st.error(mensaje)


def mostrar_verificacion(sid: str) -> None:
    """Muestra el resultado del botón "Verificar", si se usó."""
    if estado_mensaje := st.session_state.get(f"ver_{sid}"):
        estado, mensaje = estado_mensaje
        if estado == "ok":
            st.success(mensaje)
        else:
            st.error(mensaje)


def mostrar_aviso(sid: str) -> None:
    """Muestra la advertencia del último resultado, si la trae
    (p. ej. un p que no es primo en Diffie-Hellman)."""
    resultado = st.session_state.get(f"res_{sid}")
    if resultado is not None and (aviso := resultado.datos.get("aviso")):
        st.warning(aviso)


def fila_metricas(sid: str) -> None:
    """Los valores clave del resultado (n, φ(n), d, A, B, K...) en una fila
    de st.metric a lo ancho, entre la tarjeta y las tablas."""
    resultado = st.session_state.get(f"res_{sid}")
    if resultado is None:
        return
    metricas = resultado.datos.get("metricas")
    if not metricas:
        return
    with st.container(key=f"panel-metricas-{sid.replace('.', '-')}"):
        for columna, (nombre, valor) in zip(st.columns(len(metricas)), metricas):
            columna.metric(nombre, valor)


def clase_del_valor(valor: str) -> str:
    """Tamaño del valor según su largo: Grande hasta 8 caracteres, compacto
    hasta 24 y, para hashes, binarios y Base64, en monoespaciada."""
    if len(valor) <= 8:
        return "resultado-valor"
    if len(valor) <= 24:
        return "resultado-valor compacto"
    return "resultado-valor largo"


def tarjeta_resultado(sid: str) -> None:
    """Tarjeta de resultado: Etiqueta, valor grande en durazno, chips y verificación."""
    with st.container(key=f"resultado-{sid.replace('.', '-')}"):
        resultado = st.session_state.get(f"res_{sid}")
        if resultado is None:
            if st.session_state.get(f"err_{sid}"):
                espera = "La entrada no es válida: Corrige lo que indica el formulario y calcula de nuevo."
            else:
                espera = "Completa el formulario y calcula para mirar por la cerradura."
            st.html(
                '<div class="resultado-etiqueta">Resultado</div>'
                f'<div class="resultado-espera">{espera}</div>'
            )
            return
        piezas = [
            f'<div class="resultado-etiqueta">'
            f'{html.escape(str(resultado.datos.get("etiqueta", "Resultado")))}</div>',
            f'<div class="{clase_del_valor(resultado.valor)}">{html.escape(resultado.valor)}</div>',
        ]
        if chips := resultado.datos.get("chips"):
            interior = "".join(f'<span class="chip">{html.escape(str(c))}</span>' for c in chips)
            piezas.append(f'<div class="chips">{interior}</div>')
        if resultado.verificacion:
            piezas.append(f'<div class="verificacion">✓ {html.escape(resultado.verificacion)}</div>')
        st.html("".join(piezas))


# Cada paso de Resultado.pasos empieza con su título en negrita: "**Título.** texto"
PATRON_PASO = re.compile(r"^\*\*(.+?)\*\*\s*(.*)$", re.S)


def html_pasos(pasos: list[str]) -> str:
    """El procedimiento como lista: Número en lavanda, título en negrita y explicación."""
    piezas = []
    for numero, paso in enumerate(pasos, start=1):
        coincidencia = PATRON_PASO.match(paso)
        if coincidencia:
            titulo, texto = coincidencia.groups()
            cuerpo = f"<strong>{html.escape(titulo)}</strong> {html.escape(texto)}"
        else:
            cuerpo = html.escape(paso)
        piezas.append(
            f'<li class="paso"><span class="paso-numero">{numero}</span>'
            f'<div class="paso-texto">{cuerpo}</div></li>'
        )
    return '<ol class="pasos">' + "".join(piezas) + "</ol>"


def anchos_de_columnas(filas: list[dict]) -> dict:
    """Las columnas de valores cortos (rondas, cocientes, bits) van estrechas
    para que en pantallas angostas quepan más columnas a la vista."""
    anchos = {}
    for columna in filas[0]:
        largos = [len(str(fila.get(columna, ""))) for fila in filas]
        if max(len(str(columna)), *largos) <= 9:
            anchos[columna] = st.column_config.Column(width="small")
    return anchos


def tabla_para_mostrar(filas: list[dict]):
    """La tabla como DataFrame. En las tablas del AEE resalta la fila con
    residuo r = 1, que es de donde sale el inverso."""
    tabla = pd.DataFrame(filas)
    if "Residuo r" not in tabla.columns:
        return tabla

    def resaltar(fila):
        if fila["Residuo r"] == 1:
            return ["background-color: #2A1631; color: #FFB38A"] * len(fila)
        return [""] * len(fila)

    return tabla.style.apply(resaltar, axis=1)


def mostrar_tabla(filas: list[dict]) -> None:
    st.dataframe(
        tabla_para_mostrar(filas),
        hide_index=True,
        width="stretch",
        column_config=anchos_de_columnas(filas),
    )


def seccion_detalle(sid: str) -> None:
    """Debajo de las dos columnas: La tabla con su nota, la tabla extra
    (p. ej. el AEE del afín) y el procedimiento."""
    resultado = st.session_state.get(f"res_{sid}")
    if resultado is None:
        return
    if resultado.tabla or resultado.datos.get("alineado") or resultado.datos.get("codigo"):
        with st.container(key=f"panel-detalle-{sid.replace('.', '-')}"):
            if alineado := resultado.datos.get("alineado"):
                # Los bloques alineados (bits uno bajo otro) no se envuelven
                st.code(alineado, language=None)
            if codigo := resultado.datos.get("codigo"):
                # Los hashes largos se envuelven para que se lean completos en el celular
                st.code(codigo, language=None, wrap_lines=True)
            if resultado.tabla:
                mostrar_tabla(resultado.tabla)
            if nota := resultado.datos.get("nota_tabla"):
                st.caption(nota)
    if extra := resultado.datos.get("tabla_extra"):
        with st.container(key=f"panel-extra-{sid.replace('.', '-')}"):
            st.markdown(f"**{extra['titulo']}**")
            mostrar_tabla(extra["filas"])
            if nota := extra.get("nota"):
                st.caption(nota)
    # Abierto de entrada: es la parte que explica el resultado a quien no conoce el tema
    with st.expander(f"Procedimiento paso a paso · {len(resultado.pasos)} pasos", expanded=True):
        st.html(html_pasos(resultado.pasos))


# ---------------------- Módulo 1 · Matemática modular ----------------------


def submenu_1_1() -> None:
    sid = "1.1"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-1-1"):
        st.subheader("Módulo: a mod n = b")
        st.write(
            "Divide a entre n y se queda con el residuo b, de modo que "
            "a = q × n + b con 0 ≤ b < n. Acepta valores negativos de a."
        )
        st.session_state.setdefault(f"{sid}_a", 27)
        st.session_state.setdefault(f"{sid}_n", 5)
        campo_a, campo_n = st.columns(2)
        campo_a.number_input("Número a", key=f"{sid}_a", step=1, format="%d")
        campo_n.number_input("Módulo n", key=f"{sid}_n", min_value=1, step=1, format="%d")
        if botones_accion(sid, "Calcular módulo"):
            calcular(
                sid,
                cripto.modulo,
                a=st.session_state[f"{sid}_a"],
                n=st.session_state[f"{sid}_n"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_1_2() -> None:
    sid = "1.2"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-1-2"):
        st.subheader("Inverso aditivo")
        st.write(
            "El inverso aditivo de a módulo n es x = −a mod n, "
            "el número que cumple a + x ≡ 0 (mod n)."
        )
        st.session_state.setdefault(f"{sid}_a", 5)
        st.session_state.setdefault(f"{sid}_n", 12)
        campo_a, campo_n = st.columns(2)
        campo_a.number_input("Número a", key=f"{sid}_a", step=1, format="%d")
        campo_n.number_input("Módulo n", key=f"{sid}_n", min_value=1, step=1, format="%d")
        if botones_accion(sid, "Calcular inverso aditivo"):
            calcular(
                sid,
                cripto.inverso_aditivo,
                a=st.session_state[f"{sid}_a"],
                n=st.session_state[f"{sid}_n"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_1_3() -> None:
    sid = "1.3"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-1-3"):
        st.subheader("Inverso de XOR")
        st.write(
            "XOR es su propio inverso: Si C = A ⊕ K, entonces A = C ⊕ K. "
            "Con el mensaje cifrado C y la clave K se recupera A."
        )
        st.session_state.setdefault(f"{sid}_base", "Binario")
        st.segmented_control(
            "Base de las entradas",
            ["Binario", "Decimal", "Hexadecimal"],
            key=f"{sid}_base",
        )
        st.session_state.setdefault(f"{sid}_c", "1001")
        st.session_state.setdefault(f"{sid}_k", "0101")
        campo_c, campo_k = st.columns(2)
        campo_c.text_input("Mensaje cifrado C", key=f"{sid}_c")
        campo_k.text_input("Clave K", key=f"{sid}_k")
        if botones_accion(sid, "Recuperar A = C ⊕ K"):
            calcular(
                sid,
                cripto.inverso_xor,
                c=st.session_state[f"{sid}_c"],
                k=st.session_state[f"{sid}_k"],
                base=st.session_state[f"{sid}_base"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_1_4() -> None:
    sid = "1.4"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-1-4"):
        st.subheader("MCD con Euclides")
        st.write(
            "Divide una y otra vez con a = q × b + r: El MCD es el último residuo "
            "distinto de cero. Si MCD(a, b) = 1, a tiene inverso módulo b."
        )
        st.session_state.setdefault(f"{sid}_a", 12)
        st.session_state.setdefault(f"{sid}_b", 18)
        campo_a, campo_b = st.columns(2)
        campo_a.number_input("Número a", key=f"{sid}_a", min_value=1, step=1, format="%d")
        campo_b.number_input("Número b", key=f"{sid}_b", min_value=1, step=1, format="%d")
        if botones_accion(sid, "Calcular MCD"):
            calcular(
                sid,
                cripto.mcd_euclides,
                a=st.session_state[f"{sid}_a"],
                b=st.session_state[f"{sid}_b"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_1_5() -> None:
    sid = "1.5"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-1-5"):
        st.subheader("Inverso multiplicativo, método tradicional")
        st.write(
            "Prueba x = 1, 2, 3, … hasta que a × x mod n = 1. "
            "Por ser fuerza bruta, se limita a n ≤ 100 000."
        )
        st.session_state.setdefault(f"{sid}_a", 5)
        st.session_state.setdefault(f"{sid}_n", 26)
        campo_a, campo_n = st.columns(2)
        campo_a.number_input("Número a", key=f"{sid}_a", step=1, format="%d")
        campo_n.number_input(
            "Módulo n", key=f"{sid}_n", min_value=2, max_value=100_000, step=1, format="%d"
        )
        if botones_accion(sid, "Buscar inverso"):
            calcular(
                sid,
                cripto.inverso_tradicional,
                a=st.session_state[f"{sid}_a"],
                n=st.session_state[f"{sid}_n"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_1_6() -> None:
    sid = "1.6"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-1-6"):
        st.subheader("Inverso con Euclides extendido")
        st.write(
            "La tabla del AEE encuentra s y t con s × n + t × a = 1: "
            "El inverso de a es t llevado a módulo n."
        )
        st.session_state.setdefault(f"{sid}_a", 17)
        st.session_state.setdefault(f"{sid}_n", 40)
        campo_a, campo_n = st.columns(2)
        campo_a.number_input("Número a", key=f"{sid}_a", step=1, format="%d")
        campo_n.number_input("Módulo n", key=f"{sid}_n", min_value=2, step=1, format="%d")
        if botones_accion(sid, "Calcular inverso"):
            calcular(
                sid,
                cripto.inverso_aee,
                a=st.session_state[f"{sid}_a"],
                n=st.session_state[f"{sid}_n"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


# ---------------------- Módulo 2 · Criptografía clásica ----------------------
#
# Todos los cifradores comparten la misma estructura: selector de modo
# (Cifrar/Descifrar), campos, y los botones de botones_cifrador(), que
# incluyen "Verificar" para aplicar la operación inversa.


def submenu_2_1() -> None:
    sid = "2.1"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-2-1"):
        st.subheader("Cifrado en módulo 27")
        st.write(
            "Cada letra se vuelve número (A=0 … Ñ=14 … Z=26) y se desplaza: "
            "C = (M + k) mod 27 para cifrar y M = (C − k) mod 27 para descifrar."
        )
        st.session_state.setdefault(f"{sid}_modo", "Cifrar")
        st.session_state.setdefault(f"{sid}_texto", "HOLA")
        st.session_state.setdefault(f"{sid}_k", 3)
        st.segmented_control("Modo", ["Cifrar", "Descifrar"], key=f"{sid}_modo")
        modo = st.session_state[f"{sid}_modo"]
        st.text_input("Mensaje cifrado" if modo == "Descifrar" else "Mensaje", key=f"{sid}_texto")
        st.number_input("Desplazamiento k", key=f"{sid}_k", step=1, format="%d")
        etiqueta = "Descifrar mensaje" if modo == "Descifrar" else "Cifrar mensaje"
        botones_cifrador(sid, etiqueta, cripto.cifrado_modulo27, ("texto", "k", "modo"))
        mostrar_error(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_2_2() -> None:
    sid = "2.2"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-2-2"):
        st.subheader("César")
        st.write(
            "El desplazamiento clásico de Julio César, con k configurable "
            "(3 por defecto) y alfabeto a elegir: 27 letras con Ñ o 26 sin ella."
        )
        st.session_state.setdefault(f"{sid}_modo", "Cifrar")
        st.session_state.setdefault(f"{sid}_alfabeto", "27 letras (español)")
        st.session_state.setdefault(f"{sid}_texto", "HOLA")
        st.session_state.setdefault(f"{sid}_k", 3)
        st.segmented_control("Modo", ["Cifrar", "Descifrar"], key=f"{sid}_modo")
        st.segmented_control(
            "Alfabeto", ["27 letras (español)", "26 letras"], key=f"{sid}_alfabeto"
        )
        modo = st.session_state[f"{sid}_modo"]
        st.text_input("Mensaje cifrado" if modo == "Descifrar" else "Mensaje", key=f"{sid}_texto")
        st.number_input("Desplazamiento k", key=f"{sid}_k", step=1, format="%d")
        etiqueta = "Descifrar mensaje" if modo == "Descifrar" else "Cifrar mensaje"
        botones_cifrador(sid, etiqueta, cripto.cifrado_cesar, ("texto", "k", "alfabeto", "modo"))
        mostrar_error(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_2_3() -> None:
    sid = "2.3"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-2-3"):
        st.subheader("Vernam")
        st.write(
            "XOR byte a byte entre el mensaje y la clave, los dos en UTF-8. "
            "La clave debe medir lo mismo que el mensaje en bytes; la ñ y las "
            "tildes ocupan 2."
        )
        st.session_state.setdefault(f"{sid}_modo", "Cifrar")
        st.session_state.setdefault(f"{sid}_texto", "HOLA")
        st.session_state.setdefault(f"{sid}_clave", "XMCK")
        st.segmented_control("Modo", ["Cifrar", "Descifrar"], key=f"{sid}_modo")
        modo = st.session_state[f"{sid}_modo"]
        st.text_input(
            "Mensaje cifrado en hexadecimal" if modo == "Descifrar" else "Mensaje",
            key=f"{sid}_texto",
        )
        st.text_input("Clave", key=f"{sid}_clave")
        etiqueta = "Descifrar mensaje" if modo == "Descifrar" else "Cifrar mensaje"
        botones_cifrador(sid, etiqueta, cripto.cifrado_vernam, ("texto", "clave", "modo"))
        mostrar_error(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_2_4() -> None:
    sid = "2.4"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-2-4"):
        st.subheader("Atbash")
        st.write(
            "Refleja el alfabeto: Cada letra i se cambia por 26 − i, así que "
            "A↔Z y B↔Y. La N está en el centro y queda igual. Es su propio inverso."
        )
        st.session_state.setdefault(f"{sid}_modo", "Cifrar")
        st.session_state.setdefault(f"{sid}_texto", "HOLA")
        st.segmented_control("Modo", ["Cifrar", "Descifrar"], key=f"{sid}_modo")
        modo = st.session_state[f"{sid}_modo"]
        st.text_input("Mensaje cifrado" if modo == "Descifrar" else "Mensaje", key=f"{sid}_texto")
        etiqueta = "Descifrar mensaje" if modo == "Descifrar" else "Cifrar mensaje"
        botones_cifrador(sid, etiqueta, cripto.cifrado_atbash, ("texto", "modo"))
        mostrar_error(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_2_5() -> None:
    sid = "2.5"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-2-5"):
        st.subheader("Transposición columnar simple")
        st.write(
            "El mensaje se escribe en filas bajo la clave, se rellena con X y "
            "las columnas se leen en el orden alfabético de las letras de la clave."
        )
        st.session_state.setdefault(f"{sid}_modo", "Cifrar")
        st.session_state.setdefault(f"{sid}_texto", "HOLAMUNDO")
        st.session_state.setdefault(f"{sid}_clave", "CLAVE")
        st.segmented_control("Modo", ["Cifrar", "Descifrar"], key=f"{sid}_modo")
        modo = st.session_state[f"{sid}_modo"]
        st.text_input("Mensaje cifrado" if modo == "Descifrar" else "Mensaje", key=f"{sid}_texto")
        st.text_input("Clave (palabra)", key=f"{sid}_clave")
        etiqueta = "Descifrar mensaje" if modo == "Descifrar" else "Cifrar mensaje"
        botones_cifrador(sid, etiqueta, cripto.transposicion_columnar, ("texto", "clave", "modo"))
        mostrar_error(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_2_6() -> None:
    sid = "2.6"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-2-6"):
        st.subheader("Afín")
        st.write(
            "C = (a × M + b) mod 27 y M = a⁻¹ × (C − b) mod 27. Necesita "
            "MCD(a, 27) = 1; el inverso a⁻¹ sale del Euclides extendido del 1.6."
        )
        st.session_state.setdefault(f"{sid}_modo", "Cifrar")
        st.session_state.setdefault(f"{sid}_texto", "HOLA")
        st.session_state.setdefault(f"{sid}_a", 5)
        st.session_state.setdefault(f"{sid}_b", 8)
        st.segmented_control("Modo", ["Cifrar", "Descifrar"], key=f"{sid}_modo")
        modo = st.session_state[f"{sid}_modo"]
        st.text_input("Mensaje cifrado" if modo == "Descifrar" else "Mensaje", key=f"{sid}_texto")
        campo_a, campo_b = st.columns(2)
        campo_a.number_input("Llave a", key=f"{sid}_a", min_value=1, step=1, format="%d")
        campo_b.number_input("Llave b", key=f"{sid}_b", min_value=0, step=1, format="%d")
        etiqueta = "Descifrar mensaje" if modo == "Descifrar" else "Cifrar mensaje"
        botones_cifrador(sid, etiqueta, cripto.cifrado_afin, ("texto", "a", "b", "modo"))
        mostrar_error(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_2_7() -> None:
    sid = "2.7"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-2-7"):
        st.subheader("Sustitución simple")
        st.write(
            "Cada letra se cambia por la de un alfabeto desordenado. La clave "
            "puede ser una palabra (sus letras sin repetir y luego el resto del "
            "alfabeto) o una permutación completa de las 27 letras."
        )
        st.session_state.setdefault(f"{sid}_modo", "Cifrar")
        st.session_state.setdefault(f"{sid}_texto", "HOLA")
        st.session_state.setdefault(f"{sid}_clave", "MURCIELAGO")
        st.segmented_control("Modo", ["Cifrar", "Descifrar"], key=f"{sid}_modo")
        modo = st.session_state[f"{sid}_modo"]
        st.text_input("Mensaje cifrado" if modo == "Descifrar" else "Mensaje", key=f"{sid}_texto")
        st.text_input(
            "Clave (palabra o permutación de 27 letras)",
            key=f"{sid}_clave",
            help="Con una palabra, el alfabeto cifrado empieza con sus letras sin "
            "repetir; con 27 letras distintas, se usa tal cual.",
        )
        etiqueta = "Descifrar mensaje" if modo == "Descifrar" else "Cifrar mensaje"
        botones_cifrador(sid, etiqueta, cripto.sustitucion_simple, ("texto", "clave", "modo"))
        mostrar_error(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


# ---------------------- Módulo 3 · Criptografía moderna ----------------------


def submenu_3_1() -> None:
    sid = "3.1"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-3-1"):
        st.subheader("Diffie-Hellman")
        st.write(
            "Con p y g públicos, cada lado publica su clave: A = gᵃ mod p y "
            "B = gᵇ mod p. La clave compartida K = Bᵃ mod p = Aᵇ mod p se "
            "calcula sin que a ni b viajen por el canal."
        )
        st.session_state.setdefault(f"{sid}_p", 23)
        st.session_state.setdefault(f"{sid}_g", 5)
        st.session_state.setdefault(f"{sid}_a", 6)
        st.session_state.setdefault(f"{sid}_b", 15)
        campo_p, campo_g = st.columns(2)
        campo_p.number_input(
            "Primo p (público)", key=f"{sid}_p", min_value=3, max_value=1_000_000, step=1, format="%d"
        )
        campo_g.number_input("Generador g (público)", key=f"{sid}_g", min_value=2, step=1, format="%d")
        campo_a, campo_b = st.columns(2)
        campo_a.number_input("Clave privada de Alicia, a", key=f"{sid}_a", min_value=1, step=1, format="%d")
        campo_b.number_input("Clave privada de Bob, b", key=f"{sid}_b", min_value=1, step=1, format="%d")
        if botones_accion(sid, "Calcular clave compartida"):
            calcular(
                sid,
                cripto.diffie_hellman,
                p=st.session_state[f"{sid}_p"],
                g=st.session_state[f"{sid}_g"],
                a=st.session_state[f"{sid}_a"],
                b=st.session_state[f"{sid}_b"],
            )
        mostrar_error(sid)
        mostrar_aviso(sid)
    with derecha:
        tarjeta_resultado(sid)
    fila_metricas(sid)
    seccion_detalle(sid)


def submenu_3_2() -> None:
    sid = "3.2"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-3-2"):
        st.subheader("RSA")
        st.write(
            "Con dos primos p y q: n = p × q y φ(n) = (p − 1)(q − 1). La clave "
            "pública es (n, e) con MCD(e, φ) = 1, la privada es d = e⁻¹ mod φ(n) "
            "— hallada con el AEE del 1.6 — y el cifrado es c = mᵉ mod n."
        )
        st.session_state.setdefault(f"{sid}_p", 61)
        st.session_state.setdefault(f"{sid}_q", 53)
        st.session_state.setdefault(f"{sid}_e", 17)
        st.session_state.setdefault(f"{sid}_m", 65)
        campo_p, campo_q = st.columns(2)
        campo_p.number_input("Primo p", key=f"{sid}_p", min_value=2, max_value=1_000_000, step=1, format="%d")
        campo_q.number_input("Primo q", key=f"{sid}_q", min_value=2, max_value=1_000_000, step=1, format="%d")
        campo_e, campo_m = st.columns(2)
        campo_e.number_input("Exponente e", key=f"{sid}_e", min_value=2, step=1, format="%d")
        campo_m.number_input("Mensaje m (número)", key=f"{sid}_m", min_value=0, step=1, format="%d")
        if botones_accion(sid, "Cifrar con RSA"):
            calcular(
                sid,
                cripto.rsa,
                p=st.session_state[f"{sid}_p"],
                q=st.session_state[f"{sid}_q"],
                e=st.session_state[f"{sid}_e"],
                m=st.session_state[f"{sid}_m"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    fila_metricas(sid)
    seccion_detalle(sid)


def submenu_3_3() -> None:
    sid = "3.3"
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key="panel-3-3"):
        st.subheader("Exponenciación rápida")
        st.write(
            "Calcula bᵉ mod n escribiendo el exponente en binario: La base se "
            "eleva al cuadrado una y otra vez y solo se multiplican las "
            "potencias de los bits en 1."
        )
        st.session_state.setdefault(f"{sid}_base", 3)
        st.session_state.setdefault(f"{sid}_exponente", 13)
        st.session_state.setdefault(f"{sid}_n", 7)
        campo_b, campo_e, campo_n = st.columns(3)
        campo_b.number_input("Base b", key=f"{sid}_base", step=1, format="%d")
        campo_e.number_input(
            "Exponente e", key=f"{sid}_exponente", min_value=1, max_value=10**12, step=1, format="%d"
        )
        campo_n.number_input(
            "Módulo n", key=f"{sid}_n", min_value=2, max_value=10**12, step=1, format="%d"
        )
        if botones_accion(sid, "Calcular potencia"):
            calcular(
                sid,
                cripto.exponenciacion_rapida,
                base=st.session_state[f"{sid}_base"],
                exponente=st.session_state[f"{sid}_exponente"],
                n=st.session_state[f"{sid}_n"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


# ---------------------- Módulo 4 · Algoritmos hash ----------------------
#
# Los tres submenús comparten el constructor _submenu_hash: solo cambia el
# algoritmo. El segundo campo es opcional y activa el efecto avalancha.

DESCRIPCIONES_HASH = {
    "MD5": "Resume cualquier texto en una huella fija de 128 bits (32 dígitos "
    "hexadecimales). Hoy se considera roto para seguridad, pero es ideal para "
    "estudiar cómo funciona un hash.",
    "SHA-256": "La función más usada de la familia SHA-2: Huella de 256 bits "
    "(64 dígitos hexadecimales), presente en certificados, firmas y blockchain.",
    "SHA-512": "La hermana grande de SHA-256: Huella de 512 bits (128 dígitos "
    "hexadecimales), calculada con palabras de 64 bits.",
}


def _submenu_hash(sid: str, algoritmo: str) -> None:
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key=f"panel-{sid.replace('.', '-')}"):
        st.subheader(algoritmo)
        st.write(DESCRIPCIONES_HASH[algoritmo])
        st.session_state.setdefault(f"{sid}_texto", "abc")
        st.session_state.setdefault(f"{sid}_comparar", "")
        st.text_input("Texto", key=f"{sid}_texto")
        st.text_input(
            "Texto para comparar (opcional)",
            key=f"{sid}_comparar",
            help="Se calculan los dos hashes y se cuenta cuántos caracteres "
            "cambian entre ellos: El efecto avalancha.",
        )
        if botones_accion(sid, f"Calcular {algoritmo}"):
            calcular(
                sid,
                cripto.hash_texto,
                texto=st.session_state[f"{sid}_texto"],
                algoritmo=algoritmo,
                comparar=st.session_state[f"{sid}_comparar"],
            )
        mostrar_error(sid)
        mostrar_aviso(sid)
    with derecha:
        tarjeta_resultado(sid)
    fila_metricas(sid)
    seccion_detalle(sid)


def submenu_4_1() -> None:
    _submenu_hash("4.1", "MD5")


def submenu_4_2() -> None:
    _submenu_hash("4.2", "SHA-256")


def submenu_4_3() -> None:
    _submenu_hash("4.3", "SHA-512")


# ---------------------- Módulo 5 · Codificación ----------------------
#
# Los cuatro submenús comparten el constructor _submenu_codificacion:
# modo Codificar/Decodificar, un campo de texto y los botones de
# botones_cifrador(), cuyo "Verificar" aplica la operación inversa.


def _submenu_codificacion(sid: str, titulo: str, explicacion: str, funcion) -> None:
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key=f"panel-{sid.replace('.', '-')}"):
        st.subheader(titulo)
        st.write(explicacion)
        st.session_state.setdefault(f"{sid}_modo", "Codificar")
        st.session_state.setdefault(f"{sid}_texto", "Hola")
        st.segmented_control("Modo", ["Codificar", "Decodificar"], key=f"{sid}_modo")
        modo = st.session_state[f"{sid}_modo"]
        st.text_input(
            "Texto codificado" if modo == "Decodificar" else "Texto",
            key=f"{sid}_texto",
        )
        etiqueta = "Decodificar texto" if modo == "Decodificar" else "Codificar texto"
        botones_cifrador(sid, etiqueta, funcion, ("texto", "modo"))
        mostrar_error(sid)
        mostrar_aviso(sid)
        mostrar_verificacion(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)


def submenu_5_1() -> None:
    _submenu_codificacion(
        "5.1",
        "ASCII",
        "Cada carácter se cambia por su código decimal de la tabla ASCII (0 a "
        "127), separado por espacio. Lo que queda fuera de ASCII, como la ñ y "
        "las tildes, se representa con sus bytes UTF-8 y se avisa.",
        cripto.codificacion_ascii,
    )


def submenu_5_2() -> None:
    _submenu_codificacion(
        "5.2",
        "Hexadecimal",
        "Cada byte UTF-8 del texto se escribe con dos dígitos hexadecimales, "
        "de 00 a FF.",
        cripto.codificacion_hexadecimal,
    )


def submenu_5_3() -> None:
    _submenu_codificacion(
        "5.3",
        "Binario",
        "Cada byte UTF-8 del texto se escribe con sus 8 bits: El texto queda "
        "como grupos de ocho ceros y unos.",
        cripto.codificacion_binaria,
    )


def submenu_5_4() -> None:
    _submenu_codificacion(
        "5.4",
        "Base64",
        "Los bits del texto se leen en grupos de 6 y cada grupo elige un "
        "carácter de un alfabeto de 64; el relleno con = completa bloques de "
        "4 caracteres.",
        cripto.codificacion_base64,
    )


# ---------------------- Módulo 6 · Uso de salt ----------------------
#
# Cada submenú tiene dos partes: generar salts (aleatorios, con la tabla
# salt | hash) y "Verificar clave", que repite la fórmula con un salt y un
# hash guardados. El estado de la verificación usa el sufijo "v".


def cargar_ejemplo_salt(sid: str) -> None:
    """El ejemplo del módulo 6 llena las dos secciones: La clave con que se
    generan los salts y la terna clave + salt + hash de "Verificar clave"."""
    entradas = ejemplos.buscar(sid)["entradas"]
    st.session_state[f"{sid}_clave"] = entradas["clave"]
    st.session_state[f"{sid}_clave_v"] = entradas["clave"]
    st.session_state[f"{sid}_salt"] = entradas["salt"]
    st.session_state[f"{sid}_hash_guardado"] = entradas["hash_guardado"]


def _submenu_salt(sid: str, algoritmo: str) -> None:
    ejemplo = ejemplos.buscar(sid)["entradas"]
    izquierda, derecha = st.columns([3, 2], gap="large")
    with izquierda, st.container(key=f"panel-{sid.replace('.', '-')}"):
        st.subheader(f"Salt con {algoritmo}")
        st.write(
            f"A cada usuario se le genera un salt aleatorio y se guarda "
            f"hash = {algoritmo}(salt + clave). Así dos usuarios con la misma "
            "clave quedan con hashes distintos y las tablas de hashes "
            "precalculados dejan de servir."
        )
        st.session_state.setdefault(f"{sid}_clave", ejemplo["clave"])
        st.session_state.setdefault(f"{sid}_cantidad", 3)
        st.text_input("Clave", key=f"{sid}_clave")
        st.number_input(
            "Cantidad de salts", key=f"{sid}_cantidad", min_value=1, max_value=10, step=1, format="%d"
        )
        col_generar, col_ejemplo = st.columns(2)
        generar = col_generar.button(
            "Generar salts", key=f"calc-{sid}", type="primary", width="stretch"
        )
        col_ejemplo.button(
            "Cargar ejemplo",
            key=f"ej-{sid}",
            on_click=cargar_ejemplo_salt,
            args=(sid,),
            width="stretch",
        )
        if generar:
            calcular(
                sid,
                cripto.generar_salts,
                clave=st.session_state[f"{sid}_clave"],
                algoritmo=algoritmo,
                cantidad=st.session_state[f"{sid}_cantidad"],
            )
        mostrar_error(sid)
    with derecha:
        tarjeta_resultado(sid)
    seccion_detalle(sid)

    with st.container(key=f"panel-verificar-{sid.replace('.', '-')}"):
        st.subheader("Verificar clave")
        st.write(
            "El servidor no guarda la clave: Guarda el salt y el hash. Para "
            f"comprobar una clave se repite {algoritmo}(salt + clave) y se "
            "compara el resultado con el hash guardado."
        )
        st.session_state.setdefault(f"{sid}_clave_v", ejemplo["clave"])
        st.session_state.setdefault(f"{sid}_salt", ejemplo["salt"])
        st.session_state.setdefault(f"{sid}_hash_guardado", ejemplo["hash_guardado"])
        campo_clave, campo_salt = st.columns(2)
        campo_clave.text_input("Clave a comprobar", key=f"{sid}_clave_v")
        campo_salt.text_input("Salt guardado", key=f"{sid}_salt")
        st.text_input("Hash guardado", key=f"{sid}_hash_guardado")

        def comprobar() -> None:
            calcular(
                f"{sid}v",
                cripto.verificar_clave,
                clave=st.session_state[f"{sid}_clave_v"],
                salt=st.session_state[f"{sid}_salt"],
                hash_guardado=st.session_state[f"{sid}_hash_guardado"],
                algoritmo=algoritmo,
            )

        st.button(
            "Verificar clave", key=f"verif-{sid}", type="primary", on_click=comprobar, width="stretch"
        )
        mostrar_error(f"{sid}v")
        comprobacion = st.session_state.get(f"res_{sid}v")
        if comprobacion is not None:
            if comprobacion.datos["correcta"]:
                st.success(comprobacion.datos["mensaje"])
            else:
                st.error(comprobacion.datos["mensaje"])
            st.code(comprobacion.datos["alineado"], language=None)
    st.caption(
        "En la vida real las claves no se protegen con un hash rápido: Se usan "
        "bcrypt, Argon2 o PBKDF2, que aplican salt y además son lentos a "
        "propósito para frenar la fuerza bruta."
    )


def submenu_6_1() -> None:
    _submenu_salt("6.1", "MD5")


def submenu_6_2() -> None:
    _submenu_salt("6.2", "SHA-256")


def submenu_6_3() -> None:
    _submenu_salt("6.3", "SHA-512")


# Los 26 submenús de la calculadora
SUBMENUS = {
    "1.1": submenu_1_1,
    "1.2": submenu_1_2,
    "1.3": submenu_1_3,
    "1.4": submenu_1_4,
    "1.5": submenu_1_5,
    "1.6": submenu_1_6,
    "2.1": submenu_2_1,
    "2.2": submenu_2_2,
    "2.3": submenu_2_3,
    "2.4": submenu_2_4,
    "2.5": submenu_2_5,
    "2.6": submenu_2_6,
    "2.7": submenu_2_7,
    "3.1": submenu_3_1,
    "3.2": submenu_3_2,
    "3.3": submenu_3_3,
    "4.1": submenu_4_1,
    "4.2": submenu_4_2,
    "4.3": submenu_4_3,
    "5.1": submenu_5_1,
    "5.2": submenu_5_2,
    "5.3": submenu_5_3,
    "5.4": submenu_5_4,
    "6.1": submenu_6_1,
    "6.2": submenu_6_2,
    "6.3": submenu_6_3,
}

# -------------------------------- Páginas --------------------------------


def portada() -> None:
    """Portada: Título, cerradura de neón y las 6 tarjetas de módulo."""
    izquierda, derecha = st.columns([3, 2], gap="large", vertical_alignment="center")
    with izquierda:
        st.title("Mira a través de la cerradura.")
        st.write(
            "Una calculadora para cifrar, descifrar y entender cada paso: "
            "Aritmética modular, cifrados clásicos y modernos, hashes, "
            "codificación y salt."
        )
        st.caption(f"Proyecto de {AUTORA} para la clase de {CURSO}, {UNIVERSIDAD}.")
    with derecha:
        # La cerradura lleva un SVG y va por st.markdown: st.html elimina los <svg>
        st.markdown(CERRADURA_HTML, unsafe_allow_html=True)

    # Las tarjetas van por filas de tres: así en el celular se apilan en orden 1 a 6
    modulos = list(MODULOS.items())
    for fila in (modulos[:3], modulos[3:]):
        for columna, (numero, modulo) in zip(st.columns(3, gap="medium"), fila):
            with columna, st.container(key=f"modulo-{numero}"):
                st.html(
                    f'<div class="modulo-numero">{numero}</div>'
                    f'<div class="modulo-titulo">{modulo["titulo"]}</div>'
                    f'<div class="modulo-texto">{modulo["descripcion"]}</div>'
                )
                st.button(
                    "Abrir módulo",
                    key=f"abrir-{numero}",
                    on_click=ir_a,
                    args=(numero,),
                    width="stretch",
                )


def pagina_modulo(numero: str) -> None:
    """Página de un módulo: Título, submenús y el submenú seleccionado."""
    modulo = MODULOS[numero]
    st.html(
        f'<h1 class="titulo-modulo"><span class="numero">{numero}</span> · '
        f'{html.escape(modulo["titulo"])}</h1>'
    )

    # El valor de cada píldora sigue siendo "1.6 Euclides extendido"; solo se
    # muestra con el número en negrita (format_func no cambia el valor)
    etiquetas = [f"{sub_id} {nombre}" for sub_id, nombre in modulo["submenus"]]
    seleccion = st.pills(
        "Submenú",
        etiquetas,
        default=etiquetas[0],
        format_func=lambda etiqueta: "**{}** {}".format(*etiqueta.split(maxsplit=1)),
        key=f"submenu-{numero}",
        label_visibility="collapsed",
    )
    if seleccion is None:
        # st.pills permite quitar la selección; volvemos al primer submenú
        seleccion = etiquetas[0]

    sid = seleccion.split()[0]
    dibujar_submenu = SUBMENUS.get(sid)
    if dibujar_submenu is not None:
        dibujar_submenu()
        return

    with st.container(key="panel"):
        st.subheader(seleccion)
        st.write(
            f"Este submenú se construye en la fase {modulo['fase']}. "
            "Aquí irán el formulario, la tarjeta de resultado en arco, "
            "la tabla y el procedimiento paso a paso."
        )


if st.session_state.pagina == "inicio":
    portada()
else:
    pagina_modulo(st.session_state.pagina)
