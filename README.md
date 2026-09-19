# Numa · Calculadora criptográfica

Calculadora de criptografía con interfaz gráfica, hecha en Python con Streamlit.
Tiene 6 módulos con 26 submenús: matemática modular, criptografía clásica,
criptografía moderna, algoritmos hash, codificación y uso de salt. Cada operación
muestra el resultado, los datos clave, la tabla del método y el procedimiento
paso a paso, y los cifrados incluyen un botón "Verificar" que aplica la
operación inversa para comprobar que se recupera el original.

**App en línea:** https://numa-cripto.streamlit.app

## Cómo ejecutarla en tu computador

Requisito único: **Python 3.10 a 3.13** (probado con 3.12).
Descárgalo de https://www.python.org/downloads/ y, en Windows, marca la casilla
**"Add python.exe to PATH"** durante la instalación.

### Opción 1: doble clic (recomendada)

| Sistema | Qué hacer |
|---|---|
| Windows | Doble clic en `iniciar_windows.bat` |
| macOS / Linux | En una terminal dentro de la carpeta: `bash iniciar_mac_linux.sh` |

La primera vez crea el entorno virtual `.venv` e instala las dependencias
(un par de minutos, necesita internet). Las siguientes veces abre la app de inmediato.
Se abre sola en el navegador en http://localhost:8501.

### Opción 2: paso a paso en la terminal

```bash
# 1. Crear el entorno virtual
python -m venv .venv

# 2. Activarlo
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar
streamlit run app.py
```

### Opción 3: Anaconda

```bash
conda env create -f environment.yml
conda activate numa
streamlit run app.py
```

## PDF de ejemplos

`ejemplos.pdf` trae un ejemplo resuelto por cada uno de los 26 submenús. Se
descarga desde el botón de la barra lateral de la app, o se regenera con:

```bash
python pdf_ejemplos.py
```

Los resultados del PDF no están escritos a mano: se calculan en vivo con las
mismas funciones de `cripto.py` que usa la app, a partir del catálogo de
`ejemplos.py` (el mismo que alimenta el botón "Cargar ejemplo").

## Estructura

```
├── app.py                  Interfaz: navegación, portada y los 26 submenús
│                           (único archivo que importa streamlit)
├── cripto.py               Lógica pura de los 6 módulos; cada operación
│                           devuelve un Resultado con valor, pasos y tabla
├── ejemplos.py             Catálogo único de ejemplos: lo usan la app,
│                           el PDF y las pruebas
├── pdf_ejemplos.py         Genera ejemplos.pdf con fpdf2
├── ejemplos.pdf            El PDF generado (un ejemplo por submenú)
├── estilos.css             Estilos propios del diseño Numa
├── requirements.txt        Dependencias con versión fija
├── requirements-dev.txt    Lo anterior + pytest (solo para desarrollo)
├── environment.yml         Alternativa para Anaconda
├── iniciar_windows.bat     Arranque con doble clic en Windows
├── iniciar_mac_linux.sh    Arranque en macOS y Linux
├── conftest.py             Hace que pytest encuentre los módulos del proyecto
├── tests/                  Pruebas: lógica, interfaz (AppTest) y PDF
├── .streamlit/config.toml  Tema: colores, fuentes y bordes
└── static/fuentes/         Chakra Petch, Rajdhani e IBM Plex Mono (licencia OFL)
```

MCD, algoritmo extendido de Euclides y exponenciación rápida están implementados
a mano en `cripto.py`, y RSA, Diffie-Hellman y el cifrado afín los reutilizan.
Las fuentes van incluidas en el proyecto, así que la app se ve igual aunque el
computador no tenga internet (una vez instaladas las dependencias).

## Pruebas

```bash
pip install -r requirements-dev.txt
pytest -q
```

Cubren los resultados de los 26 submenús (incluidos los ejemplos del catálogo),
las entradas inválidas, la ida y vuelta de todos los cifrados, la interfaz con
`streamlit.testing` y la generación del PDF.

## Autora

Realizado por Leydy Yohana Macareo Fuentes · UNAB · Ciberseguridad
