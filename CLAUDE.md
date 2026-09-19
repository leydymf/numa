# CLAUDE.md · Numa, calculadora criptográfica

Este archivo es el contexto permanente del proyecto. Léelo completo antes de cada tarea.

## 1. Qué es el proyecto

Proyecto universitario de criptografía. Es una calculadora con interfaz gráfica hecha en
Python con Streamlit, con 6 módulos y sus submenús. Se entrega el código `.py`, un PDF con
un ejemplo resuelto por cada submenú, y se sustenta en clase. La app se despliega en
Streamlit Community Cloud y también debe correr en el PC del profesor con
`iniciar_windows.bat`.

Quien sustenta debe poder explicar cada línea, así que el código prioriza la claridad
sobre la astucia.

## 2. Estado actual del repositorio

| Archivo | Estado | Regla |
|---|---|---|
| `.streamlit/config.toml` | Terminado | No cambiar colores ni fuentes sin pedir permiso |
| `estilos.css` | Base terminada | Se puede ampliar; mantener los tokens de `:root` |
| `static/fuentes/` | Terminado | No borrar; licencias OFL incluidas. En uso: Chakra Petch, Rajdhani e IBM Plex Mono. Fraunces y Manrope quedan sin usar |
| `requirements.txt` | Terminado | No agregar dependencias sin pedir permiso |
| `iniciar_windows.bat`, `iniciar_mac_linux.sh`, `environment.yml` | Terminados | No tocar salvo que se rompan |
| `app.py` | App real con los 26 submenús | Los créditos (AUTORA, UNIVERSIDAD, CURSO) se importan de `pdf_ejemplos.py` |
| `README.md` | Actualizado | Mantenerlo al día con el nombre y la estructura |

## 3. Stack y restricciones

- Python 3.10 o superior (probado con 3.12). Streamlit 1.64.0 y fpdf2 2.8.8, fijados.
- Todo lo demás con librería estándar: `hashlib`, `secrets`, `base64`, `math`, `unicodedata`, `dataclasses`, `html`.
  Excepción: `pandas`, que ya trae Streamlit, solo se usa en `app.py` para resaltar una fila en `st.dataframe`.
- `pytest` solo para desarrollo, en `requirements-dev.txt`; nunca en `requirements.txt`.
- MCD, algoritmo extendido de Euclides (AEE) y exponenciación rápida se implementan a mano.
  `pow(a, -1, n)` y `pow(b, e, n)` solo se permiten dentro de las pruebas para verificar.
- Código, comentarios, docstrings, mensajes e interfaz en español.
- Nada de `localStorage`, servicios externos ni llamadas de red.

## 4. Arquitectura

```
app.py              Interfaz: navegación, páginas y componentes visuales. Único archivo que importa streamlit.
cripto.py           Lógica pura de los 6 módulos. No importa streamlit.
ejemplos.py         Catálogo único de ejemplos: lo usan "Cargar ejemplo", el PDF y las pruebas.
pdf_ejemplos.py     Genera ejemplos.pdf con fpdf2 a partir de ejemplos.py y cripto.py.
tests/test_cripto.py  Pruebas con pytest.
```

Reglas:

1. `cripto.py` está organizado en secciones con encabezados comentados, en este orden:
   utilidades de texto, matemática modular, criptografía clásica, criptografía moderna,
   hash, codificación y salt.
2. Cada operación devuelve un `Resultado` y nunca imprime ni pide datos:

```python
@dataclass
class Resultado:
    valor: str                          # resultado final, listo para mostrar
    pasos: list[str]                    # procedimiento; cada paso es "**Título.** explicación"
    tabla: list[dict] | None = None     # filas para st.dataframe (AEE, exp. rápida, salts...)
    verificacion: str | None = None     # comprobación, p. ej. "7 × 15 = 105 ≡ 1 (mod 26)"
    datos: dict = field(default_factory=dict)  # valores extra (n, phi, d, A, B...)
```

3. Cada paso de `pasos` se construye con `_paso(titulo, texto)` en `cripto.py`. La plantilla:
   primer paso "Qué buscamos" o "Qué hacemos" en palabras simples, un paso por operación con
   los números reales y la cuenta completa, cada término explicado la primera vez que aparece,
   todas las letras en los cifrados cuando el texto es corto, y un paso "Comprobación" al final.
   `app.py` los muestra con `html_pasos` y el PDF pone el título en negrita con `markdown=True`.
4. Una entrada inválida lanza `ValueError` con un mensaje en español que explica qué pasó
   y cómo corregirlo, por ejemplo: "No existe inverso: MCD(12, 18) = 6. Elige un número
   coprimo con 18."
5. RSA, Diffie-Hellman y el afín reutilizan `mcd`, `aee` y `exp_rapida`. Esto se va a
   señalar en la sustentación.
6. En `ejemplos.py` cada ejemplo tiene: `id` (p. ej. "1.6"), `titulo`, `entradas` (dict con
   las mismas claves que los widgets), `funcion` y `esperado`, más los textos del PDF que vienen
   de `EXPLICACIONES`: `enunciado`, `concepto`, `formula` y `campos` (nombre legible de cada entrada).

## 5. Especificación funcional

Convenciones generales:

- Alfabeto español de 27 letras: `ABCDEFGHIJKLMNÑOPQRSTUVWXYZ`, con A=0 … Ñ=14 … Z=26.
- Normalización para cifrados clásicos: mayúsculas, quitar tildes y diéresis conservando la Ñ,
  e ignorar lo que no esté en el alfabeto. La interfaz muestra el texto normalizado.
- Todo cifrador tiene modo Cifrar y Descifrar, y un botón "Verificar" que aplica la operación
  inversa y confirma que se recupera el original.

### Módulo 1 · Matemática modular

| Id | Operación | Detalle |
|---|---|---|
| 1.1 | a mod n = b | Acepta negativos. Muestra a = q·n + b con 0 ≤ b < n |
| 1.2 | Inverso aditivo | −a mod n, con verificación a + x ≡ 0 (mod n) |
| 1.3 | Inverso de XOR | Dados C y K obtiene A = C ⊕ K. Entradas en binario, decimal o hex. Muestra bits alineados |
| 1.4 | MCD | Euclides paso a paso (a = q·b + r) e indica si existe inverso multiplicativo |
| 1.5 | Inverso, método tradicional | Prueba x = 1, 2, … hasta a·x mod n = 1, mostrando los intentos. Límite n ≤ 100 000 |
| 1.6 | Inverso con AEE | Tabla con columnas Ronda, Cociente q, Residuo r, s, t. Dos filas "Inicio" (n: s=1, t=0; a: s=0, t=1), luego una fila por división. Rondas = número de divisiones. Inverso = t de la fila con r=1, llevado a mod n |

### Módulo 2 · Criptografía clásica (alfabeto de 27 salvo que se indique)

| Id | Cifrado | Detalle |
|---|---|---|
| 2.1 | Módulo 27 | C = (M + k) mod 27. Tabla letra → número → operación → letra |
| 2.2 | César | Desplazamiento configurable, por defecto 3. Selector de alfabeto: 27 (español, por defecto) o 26 |
| 2.3 | Vernam | XOR byte a byte (UTF-8). La clave debe tener la misma longitud en bytes. Salida en hex y binario; descifrado desde hex |
| 2.4 | Atbash | i → 26 − i. La N (13) queda igual; decirlo en la explicación |
| 2.5 | Transposición columnar simple | Clave palabra. Orden de columnas por orden alfabético de la clave (empates de izquierda a derecha). Relleno con X. Mostrar la matriz con la clave y el número de orden encima |
| 2.6 | Afín | C = (a·M + b) mod 27, M = a⁻¹·(C − b) mod 27. Validar MCD(a, 27) = 1 y mostrar a⁻¹ con AEE |
| 2.7 | Sustitución simple | Clave como palabra (alfabeto = palabra sin letras repetidas + resto en orden) o como permutación completa de 27 letras. Mostrar la tabla de correspondencias en dos filas |

### Módulo 3 · Criptografía moderna

| Id | Operación | Detalle |
|---|---|---|
| 3.1 | Diffie-Hellman | Entradas p, g, a, b. A = gᵃ mod p, B = gᵇ mod p, y la clave calculada por los dos lados (Bᵃ y Aᵇ) para mostrar que coinciden. Avisar si p no es primo |
| 3.2 | RSA | Entradas p, q, e y mensaje m. n, φ(n), validar 1 < e < φ y MCD(e, φ) = 1, d por AEE con su tabla, c = mᵉ mod n y descifrado. Validar que p y q sean primos y m < n |
| 3.3 | Exponenciación rápida | bᵉ mod n con tabla: bit del exponente, potencia al cuadrado, acumulado. Indicar el número de multiplicaciones |

### Módulo 4 · Algoritmos hash

4.1 MD5, 4.2 SHA-256, 4.3 SHA-512 sobre texto UTF-8. Mostrar el hash en hex y su longitud
en bits. Extra: un segundo campo opcional para comparar dos textos y mostrar cuántos
caracteres del hash cambian (efecto avalancha).

### Módulo 5 · Codificación (codificar y decodificar)

5.1 ASCII (códigos decimales separados por espacio; si hay caracteres no ASCII, mostrar sus
bytes UTF-8 y avisar), 5.2 hexadecimal, 5.3 binario de 8 bits por byte, 5.4 Base64.
Validar la entrada al decodificar.

### Módulo 6 · Uso de salt

6.1 MD5, 6.2 SHA-256, 6.3 SHA-512. Entradas: clave y cantidad de salts (1 a 10). Cada salt
es `secrets.token_hex(8)` y el hash es `hash(salt + clave)`; la fórmula se muestra en
pantalla. Tabla salt | hash. Sección "Verificar clave": clave + salt + hash guardado → correcto
o incorrecto. Explicación breve de por qué el salt evita que dos usuarios con la misma clave
tengan el mismo hash, y nota de que en la vida real se usan bcrypt, Argon2 o PBKDF2.

### Resultados verificados (base de ejemplos y pruebas)

| Id | Entrada | Esperado |
|---|---|---|
| 1.1 | 27 mod 5 / −7 mod 26 | 2 / 19 |
| 1.2 | 7 en mod 26 | 19 |
| 1.3 | C = 1100, K = 0110 | 1010 |
| 1.4 | (7, 26) / (12, 18) | 1, existe inverso / 6, no existe |
| 1.5 | inv(3) mod 7 | 5 |
| 1.6 | inv(7) mod 26 | 15, en 4 rondas; fila con r=1: s=3, t=−11 |
| 2.1 | "HOLA", k = 3 | KRÑD |
| 2.2 | "HOLA", k = 3, alfabeto 26 | KROD |
| 2.3 | "HOLA", clave "XMCK" | 10020F0A |
| 2.4 | "HOLA" | SLOZ |
| 2.5 | "HOLAMUNDO", clave "CLAVE" | LDHUMXONAO |
| 2.6 | "HOLA", a = 5, b = 8 | PCJI (a⁻¹ = 11) |
| 2.7 | "HOLA", palabra "MURCIELAGO" | AKDM |
| 3.1 | p=23, g=5, a=6, b=15 | A=8, B=19, K=2 |
| 3.2 | p=61, q=53, e=17, m=65 | n=3233, φ=3120, d=2753, c=2790 |
| 3.3 | 3¹³ mod 7 | 3 |
| 4.1 | "abc" | 900150983cd24fb0d6963f7d28e17f72 |
| 4.2 | "abc" | ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad |
| 4.3 | "abc" | ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f |
| 5.x | "Hola" | ASCII 72 111 108 97 · hex 486F6C61 · binario 01001000 01101111 01101100 01100001 · Base64 SG9sYQ== |
| 6.1 | salt "a1b2c3d4", clave "Clave123" | 3baad75a2e328110d25f895f12abc632 |
| 6.2 | salt "a1b2c3d4", clave "Clave123" | e3143dc97e4a38f053866bbd28780a1a90af33199dba6cb08681dced52685236 |

Además: cifrar y luego descifrar devuelve el original en todos los cifrados clásicos, con
textos de prueba que incluyan Ñ, tildes y espacios.

## 6. Sistema de diseño Numa

Concepto: descifrar es mirar por la cerradura. Estética neón de ciberseguridad con aire gamer:
fondo ciruela, superficies oscuras, acentos neón y **esquinas cortadas** (chaflán) en tarjetas,
botones, píldoras y campos. **Nada va en cursiva.** La cerradura de neón queda como marca en la
portada y en la barra lateral. La app se llama **Numa**.

### Tokens

| Token | Hex | Uso |
|---|---|---|
| Ciruela noche | `#120814` | Fondo |
| Terciopelo | `#1D0F22` | Barra lateral y tarjetas |
| Berenjena | `#2A1631` | Campos, chips, píldoras, ítem activo del menú, fila destacada |
| Malva humo | `#4A2E52` | Bordes |
| Nácar | `#F6E9F2` | Texto principal |
| Lila niebla | `#B9A3C2` | Texto secundario |
| Orquídea neón | `#FF4FA8` | Acción principal, selección, cerradura |
| Lavanda eléctrica | `#C08CFF` | Números de módulo y enlaces |
| Durazno neón | `#FFB38A` | Resultado final |
| Menta hielo | `#7FF5D0` | Verificación correcta |
| Coral | `#FF6B7A` | Errores |

Proporción 60/30/10: fondos, superficies y texto, neón. Sobre los neones el texto va en
`#120814`, nunca en blanco.

Tipografía (todas locales en `static/fuentes/`, registradas en `config.toml`):

- **Chakra Petch** para títulos, marca, números de módulo y valores de resultado.
- **Rajdhani** para texto, formularios y botones. Es condensada, por eso el tema usa
  `baseFontSize = 17` y `baseFontWeight = 500`.
- **IBM Plex Mono** solo para hashes, binarios, tablas, chips y rótulos pequeños.

Formas: `corner-shape: bevel` sobre el `border-radius` (Chromium 139 o superior; en otros
navegadores quedan esquinas redondeadas, que es un degradado aceptable). Tarjetas 18 px,
tarjeta de resultado 22 px, botones y píldoras 0.5 rem. El brillo neón solo en la cerradura,
la tarjeta de resultado y la píldora activa.

### Pantallas de referencia

**Inicio.** Barra lateral: marca (icono de cerradura + "Numa" en Chakra Petch + "Calculadora
criptográfica"), rótulo "Módulos" y el menú con "Inicio" y los 6 módulos dentro de
`st.container(key="nav", gap=None)`: ítems alineados a la izquierda, número en lavanda en una
columna fija (`**1** · Título`; "Inicio" lleva el icono `:material/home:` en esa columna), el activo con fondo berenjena y barra de neón a la izquierda. Al
pie, los créditos "Realizado por Leydy Yohana Macareo Fuentes · UNAB · Ciberseguridad" y el
botón "Descargar PDF de ejemplos". En el contenido, a la izquierda el título "Mira a través de
la cerradura.", un párrafo corto y una línea de créditos; a la derecha la cerradura de neón.
Debajo, 6 tarjetas en dos filas de tres (se crean fila por fila para que en el celular se
apilen en orden 1 a 6) con número, título, descripción y el botón "Abrir módulo".

Cerradura de la portada (340 × 360 px). Lleva un `<svg>`, así que se inserta con
`st.markdown(..., unsafe_allow_html=True)`: `st.html` sanitiza el HTML y elimina los SVG.

```html
<div aria-hidden="true" style="position:relative;width:340px;height:360px">
  <!-- Fondo: 15 líneas de texto cifrado, hex, binario y base64 en IBM Plex Mono 12.5px,
       color #5B3F66, dentro de un div absoluto left:20px top:20px 300×340
       con border-radius:150px 150px 0 0 y overflow:hidden -->
  <svg width="340" height="360" viewBox="0 0 340 360"
       style="position:absolute;inset:0;overflow:visible;filter:drop-shadow(0 0 7px #FF4FA8)">
    <path d="M20 360 V170 A150 150 0 0 1 320 170 V360" fill="none" stroke="#FF4FA8" stroke-width="2"/>
    <path d="M150 219 A44 44 0 1 1 190 219 L206 300 H134 Z" fill="#120814"
          stroke="#FF4FA8" stroke-width="2" stroke-linejoin="round"/>
  </svg>
  <!-- "Hola" centrado en top:160px, Chakra Petch 700 28px, #FFB38A,
       text-shadow 0 0 16px rgba(255,179,138,.45) -->
</div>
```

**Pantalla de módulo** (referencia: 1.6). Título por `st.html` con la clase `titulo-modulo` y el
número en lavanda. Debajo, los submenús con `st.pills` (key `submenu-N`; el valor de cada
opción es "1.6 Euclides extendido" y `format_func` solo muestra el número en negrita): píldoras
grandes con fondo berenjena y borde malva, la activa rellena en orquídea con texto ciruela y
brillo. Luego dos columnas:

- Izquierda, panel de formulario (`st.container(key="panel-1-6")`): título del submenú,
  explicación de una o dos frases con la fórmula, campos, botón primario con verbo concreto
  ("Calcular inverso", "Cifrar mensaje") y botón secundario "Cargar ejemplo".
- Derecha, tarjeta de resultado (`st.container(key="resultado-1-6")`): etiqueta ("Inverso de 7
  en módulo 26"), valor en durazno con tres tamaños según el largo (Chakra Petch 5 rem hasta 8
  caracteres, 2.4 rem hasta 24, Plex Mono 1.05 rem para hashes, binarios y Base64), chips con
  datos clave ("4 rondas", "MCD(7, 26) = 1") y verificación en menta con ✓. Si hubo error, la
  tarjeta lo dice en vez de "Completa el formulario".

Debajo, a todo el ancho, el panel con la tabla (`st.dataframe`: las columnas de valores cortos
van con `width="small"` y en las tablas del AEE se resalta la fila con r = 1) y una nota que
interpreta la tabla. Al final, el procedimiento abierto de entrada:
`st.expander("Procedimiento paso a paso · N pasos", expanded=True)` con cada paso numerado en
lavanda y su título en negrita (`html_pasos` en `app.py`).

### Reglas de interfaz

- Clases CSS: `st.container(key="x")` produce `.st-key-x` sobre el propio `stVerticalBlock`.
  Los widgets con `key` también reciben `.st-key-<key>` en su contenedor. Los estilos nuevos
  van en `estilos.css` usando las variables de `:root`.
- HTML propio por `st.html`, salvo cuando lleva `<svg>`: entonces `st.markdown(...,
  unsafe_allow_html=True)`, porque `st.html` elimina los SVG.
- Resultados largos (hashes, Base64, binario): `st.code` para tener botón de copiar; los hashes
  con `wrap_lines=True` para que se lean completos en el celular. Los bloques alineados
  (bits uno bajo otro) no se envuelven.
- Estados: `st.success` para verificación correcta y `st.error` para errores, con mensajes que dicen cómo corregir.
- Sin cursiva, sin emojis en la interfaz (salvo el favicon), sin etiquetas en MAYÚSCULAS, sin degradados, sin sombras grises genéricas.
- Texto en español, en frase normal, voz activa y sin relleno.
- Después de dos puntos va mayúscula («Resultado: El inverso es 15»), salvo cuando sigue una
  variable o fórmula («residuo 1: t = −11»). `cripto.mayuscula_tras_dos_puntos` lo aplica a todo
  `Resultado`; los textos fijos ya vienen escritos así.
- La multiplicación en los textos se escribe con × (a × x), nunca con el punto medio.
- Los resultados persisten en `st.session_state`. "Cargar ejemplo" usa un `on_click` que escribe los valores en las `key` de los widgets antes de que se dibujen.
- Todo texto del usuario que se inserte en `st.html` pasa por `html.escape`.
- La navegación debe funcionar con teclado y tener foco visible.
- Celular: `estilos.css` tiene un `@media (max-width: 640px)` que reduce el espacio superior
  y los cuerpos grandes. Chrome no baja de 500 px de ventana; para revisar a 390 px se fija
  `document.querySelector('[data-testid="stApp"]').style.width = '390px'`.

## 7. PDF de ejemplos

- `python pdf_ejemplos.py` genera `ejemplos.pdf`. En la app, el botón de la barra lateral lo genera en memoria con `st.download_button`.
- Usa las mismas funciones de `cripto.py` y los datos de `ejemplos.py`; ningún resultado se escribe a mano.
- Versión clara para imprimir: fondo blanco, texto `#120814`, títulos en Chakra Petch, texto en Rajdhani (Rajdhani-Medium como regular) y acentos en `#FF4FA8` y `#C08CFF`. Registrar las TTF de `static/fuentes/` con `add_font` para tener tildes y Ñ. Si un símbolo no existe en la fuente (p. ej. φ), escribir "phi(n)".
- Escala tipográfica única: 34 (nombre en portada), 20 (módulos e índice), 14 (submenús), 10.5 (cuerpo),
  9.5 (monoespaciada) y 8.5 (rótulos, tablas, pie). Interlineado 5.2 mm. Texto alineado a la izquierda.
- Estructura: portada (título, "Realizado por" + autora, universidad y curso), índice, una página de inicio por módulo con su párrafo de `INTRO_MODULOS`, y una
  sección por submenú con: Enunciado, Datos (tabla campo/valor), Idea del método con la fórmula en
  monoespaciada, Procedimiento (los pasos de `cripto.py`, título en negrita, número en orquídea),
  Detalle (bloques monoespaciados), Tabla completa con su nota, y la caja de Resultado con la
  comprobación en verde de imprenta. La cabecera lleva el módulo en curso.

## 8. Forma de trabajar

1. Trabajar por fases (sección 9). Antes de escribir código en cada fase, presentar un plan corto.
2. Al terminar cada fase:
   - `pytest -q` sin fallos.
   - Prueba de humo: `streamlit.testing.v1.AppTest.from_file("app.py").run()` sin excepciones, navegando al menos a una página del módulo trabajado.
   - Resumen de lo hecho y qué falta.
   - Commit con mensaje en español si el repositorio tiene git.
3. No cambiar tokens de diseño, dependencias ni scripts de arranque sin preguntar.
4. Si algo de la especificación es ambiguo, preguntar en lugar de suponer.

## 9. Fases

| Fase | Contenido |
|---|---|
| 1 | Estructura de archivos, `Resultado`, utilidades de texto, navegación completa, portada con cerradura, páginas vacías de los 6 módulos con sus submenús |
| 2 | Módulo 1 completo (lógica, interfaz, ejemplos y pruebas) |
| 3 | Módulo 2 completo |
| 4 | Módulo 3 completo |
| 5 | Módulos 4, 5 y 6 completos |
| 6 | PDF de ejemplos y botón de descarga |
| 7 | Revisión final: validaciones, textos, accesibilidad, README y lista de verificación |

## 10. Definición de terminado

- Los 26 submenús funcionan, con "Cargar ejemplo" y resultados iguales a la tabla de la sección 5.
- Ninguna entrada inválida rompe la app.
- `pytest -q` pasa y la prueba de humo con AppTest no lanza excepciones.
- `ejemplos.pdf` se genera con todos los ejemplos.
- La app arranca con `iniciar_windows.bat` en un PC limpio y en Streamlit Community Cloud.
- El diseño coincide con la sección 6.
