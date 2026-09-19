"""
Numa · catálogo único de ejemplos
---------------------------------
Una sola fuente de verdad: El botón "Cargar ejemplo" de la interfaz,
el PDF de ejemplos y las pruebas leen los ejemplos de aquí.

Cada ejemplo es un diccionario con estas claves:
  id        identificador del submenú, p. ej. "1.6"
  titulo    enunciado corto del ejemplo
  entradas  dict con las mismas claves que los widgets de la interfaz
  funcion   nombre de la función de cripto.py que resuelve el ejemplo
  esperado  resultado que debe salir (coincide con la tabla de CLAUDE.md)
  enunciado el problema en una frase, para el PDF
  concepto  la idea del método en tres o cuatro frases, para el PDF
  formula   la fórmula del método, para el PDF
  campos    nombre legible de cada entrada, para la tabla de datos del PDF

Los cuatro últimos vienen de EXPLICACIONES, al final del archivo.
"""

# Nota: las claves de `entradas` coinciden con los campos de la interfaz;
# app.py les agrega el prefijo del submenú al usarlas como key de widget
# (por ejemplo "1.6_a"). `esperado` se compara con Resultado.valor.
EJEMPLOS: list[dict] = [
    # ------------------- Módulo 1 · Matemática modular -------------------
    {
        "id": "1.1",
        "titulo": "Módulo de un número negativo: −7 mod 26",
        "entradas": {"a": -7, "n": 26},
        "funcion": "modulo",
        "esperado": "19",
    },
    {
        "id": "1.2",
        "titulo": "Inverso aditivo de 7 módulo 26",
        "entradas": {"a": 7, "n": 26},
        "funcion": "inverso_aditivo",
        "esperado": "19",
    },
    {
        "id": "1.3",
        "titulo": "Recuperar A a partir de C = 1100 y K = 0110",
        "entradas": {"c": "1100", "k": "0110", "base": "Binario"},
        "funcion": "inverso_xor",
        "esperado": "1010",
    },
    {
        "id": "1.4",
        "titulo": "MCD(7, 26) con el algoritmo de Euclides",
        "entradas": {"a": 7, "b": 26},
        "funcion": "mcd_euclides",
        "esperado": "1",
    },
    {
        "id": "1.5",
        "titulo": "Inverso de 3 módulo 7 probando uno a uno",
        "entradas": {"a": 3, "n": 7},
        "funcion": "inverso_tradicional",
        "esperado": "5",
    },
    {
        "id": "1.6",
        "titulo": "Inverso de 7 módulo 26 con la tabla del AEE",
        "entradas": {"a": 7, "n": 26},
        "funcion": "inverso_aee",
        "esperado": "15",
    },
    # ------------------ Módulo 2 · Criptografía clásica ------------------
    {
        "id": "2.1",
        "titulo": "Cifrar HOLA con k = 3 en módulo 27",
        "entradas": {"texto": "HOLA", "k": 3, "modo": "Cifrar"},
        "funcion": "cifrado_modulo27",
        "esperado": "KRÑD",
    },
    {
        "id": "2.2",
        "titulo": "César de HOLA con k = 3 y alfabeto de 26 letras",
        "entradas": {"texto": "HOLA", "k": 3, "alfabeto": "26 letras", "modo": "Cifrar"},
        "funcion": "cifrado_cesar",
        "esperado": "KROD",
    },
    {
        "id": "2.3",
        "titulo": "Vernam de HOLA con la clave XMCK",
        "entradas": {"texto": "HOLA", "clave": "XMCK", "modo": "Cifrar"},
        "funcion": "cifrado_vernam",
        "esperado": "10020F0A",
    },
    {
        "id": "2.4",
        "titulo": "Atbash de HOLA: Reflejar el alfabeto",
        "entradas": {"texto": "HOLA", "modo": "Cifrar"},
        "funcion": "cifrado_atbash",
        "esperado": "SLOZ",
    },
    {
        "id": "2.5",
        "titulo": "Transposición columnar de HOLAMUNDO con la clave CLAVE",
        "entradas": {"texto": "HOLAMUNDO", "clave": "CLAVE", "modo": "Cifrar"},
        "funcion": "transposicion_columnar",
        "esperado": "LDHUMXONAO",
    },
    {
        "id": "2.6",
        "titulo": "Afín de HOLA con a = 5 y b = 8",
        "entradas": {"texto": "HOLA", "a": 5, "b": 8, "modo": "Cifrar"},
        "funcion": "cifrado_afin",
        "esperado": "PCJI",
    },
    {
        "id": "2.7",
        "titulo": "Sustitución simple de HOLA con la palabra MURCIELAGO",
        "entradas": {"texto": "HOLA", "clave": "MURCIELAGO", "modo": "Cifrar"},
        "funcion": "sustitucion_simple",
        "esperado": "AKDM",
    },
    # ----------------- Módulo 3 · Criptografía moderna -----------------
    {
        "id": "3.1",
        "titulo": "Diffie-Hellman con p = 23, g = 5, a = 6 y b = 15",
        "entradas": {"p": 23, "g": 5, "a": 6, "b": 15},
        "funcion": "diffie_hellman",
        "esperado": "2",
    },
    {
        "id": "3.2",
        "titulo": "RSA con p = 61, q = 53, e = 17 y m = 65",
        "entradas": {"p": 61, "q": 53, "e": 17, "m": 65},
        "funcion": "rsa",
        "esperado": "2790",
    },
    {
        "id": "3.3",
        "titulo": "3¹³ mod 7 con cuadrados sucesivos",
        "entradas": {"base": 3, "exponente": 13, "n": 7},
        "funcion": "exponenciacion_rapida",
        "esperado": "3",
    },
    # ------------------- Módulo 4 · Algoritmos hash -------------------
    {
        "id": "4.1",
        "titulo": "MD5 de «abc» y efecto avalancha frente a «abd»",
        "entradas": {"texto": "abc", "algoritmo": "MD5", "comparar": "abd"},
        "funcion": "hash_texto",
        "esperado": "900150983cd24fb0d6963f7d28e17f72",
    },
    {
        "id": "4.2",
        "titulo": "SHA-256 de «abc»",
        "entradas": {"texto": "abc", "algoritmo": "SHA-256", "comparar": ""},
        "funcion": "hash_texto",
        "esperado": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    },
    {
        "id": "4.3",
        "titulo": "SHA-512 de «abc»",
        "entradas": {"texto": "abc", "algoritmo": "SHA-512", "comparar": ""},
        "funcion": "hash_texto",
        "esperado": (
            "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
            "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f"
        ),
    },
    # --------------------- Módulo 5 · Codificación ---------------------
    {
        "id": "5.1",
        "titulo": "«Hola» en códigos ASCII decimales",
        "entradas": {"texto": "Hola", "modo": "Codificar"},
        "funcion": "codificacion_ascii",
        "esperado": "72 111 108 97",
    },
    {
        "id": "5.2",
        "titulo": "«Hola» en hexadecimal",
        "entradas": {"texto": "Hola", "modo": "Codificar"},
        "funcion": "codificacion_hexadecimal",
        "esperado": "486F6C61",
    },
    {
        "id": "5.3",
        "titulo": "«Hola» en binario de 8 bits por byte",
        "entradas": {"texto": "Hola", "modo": "Codificar"},
        "funcion": "codificacion_binaria",
        "esperado": "01001000 01101111 01101100 01100001",
    },
    {
        "id": "5.4",
        "titulo": "«Hola» en Base64",
        "entradas": {"texto": "Hola", "modo": "Codificar"},
        "funcion": "codificacion_base64",
        "esperado": "SG9sYQ==",
    },
    # ---------------------- Módulo 6 · Uso de salt ----------------------
    # El ejemplo de cada submenú es la sección "Verificar clave", que es
    # determinista: el hash generado con salts aleatorios cambia cada vez.
    {
        "id": "6.1",
        "titulo": "Verificar «Clave123» con el salt a1b2c3d4 y MD5",
        "entradas": {
            "clave": "Clave123",
            "salt": "a1b2c3d4",
            "hash_guardado": "3baad75a2e328110d25f895f12abc632",
            "algoritmo": "MD5",
        },
        "funcion": "verificar_clave",
        "esperado": "3baad75a2e328110d25f895f12abc632",
    },
    {
        "id": "6.2",
        "titulo": "Verificar «Clave123» con el salt a1b2c3d4 y SHA-256",
        "entradas": {
            "clave": "Clave123",
            "salt": "a1b2c3d4",
            "hash_guardado": "e3143dc97e4a38f053866bbd28780a1a90af33199dba6cb08681dced52685236",
            "algoritmo": "SHA-256",
        },
        "funcion": "verificar_clave",
        "esperado": "e3143dc97e4a38f053866bbd28780a1a90af33199dba6cb08681dced52685236",
    },
    {
        "id": "6.3",
        "titulo": "Verificar «Clave123» con el salt a1b2c3d4 y SHA-512",
        "entradas": {
            "clave": "Clave123",
            "salt": "a1b2c3d4",
            "hash_guardado": (
                "42f05bf6608218bfbe7339547035e09ce95ace42b1e850d8e967a2dab75954fa"
                "84da5f396a7412dda064d8ffcb815c5e0678cbe772a1a83a28cf3838d84b7ea8"
            ),
            "algoritmo": "SHA-512",
        },
        "funcion": "verificar_clave",
        "esperado": (
            "42f05bf6608218bfbe7339547035e09ce95ace42b1e850d8e967a2dab75954fa"
            "84da5f396a7412dda064d8ffcb815c5e0678cbe772a1a83a28cf3838d84b7ea8"
        ),
    },
]


def buscar(id_ejemplo: str) -> dict:
    """Devuelve el ejemplo de un submenú por su id, p. ej. buscar("1.6")."""
    for ejemplo in EJEMPLOS:
        if ejemplo["id"] == id_ejemplo:
            return ejemplo
    raise KeyError(f"No hay ejemplo con id '{id_ejemplo}' en el catálogo.")


# ----------------------------------------------------------------------
# Textos que acompañan a cada ejemplo en el PDF: el enunciado del
# problema, la idea del método con su fórmula y el nombre de cada campo.
# Se anexan a cada ejemplo de EJEMPLOS al final de este archivo.
# ----------------------------------------------------------------------

EXPLICACIONES: dict[str, dict] = {
    "1.1": {
        "enunciado": "Calcular −7 mod 26, es decir, el residuo de dividir −7 entre 26, y escribir "
        "la identidad a = q × n + b con 0 ≤ b < n.",
        "concepto": "«a mod n» es el residuo que queda al dividir a entre n. Siempre está entre 0 "
        "y n − 1, también cuando a es negativo: Por eso el cociente se toma hacia abajo (−1 en "
        "vez de 0). La identidad a = q × n + b conecta el cociente q, el módulo n y el residuo b.",
        "formula": "a = q × n + b, con 0 ≤ b < n",
        "campos": {"a": "Número a", "n": "Módulo n"},
    },
    "1.2": {
        "enunciado": "Hallar el inverso aditivo de 7 en módulo 26 y comprobar que la suma es un "
        "múltiplo de 26.",
        "concepto": "El inverso aditivo de a es el número x que, sumado a a, da 0 en módulo n: "
        "a + x ≡ 0 (mod n). Se calcula como −a mod n, que para 0 < a < n equivale a n − a. Es la "
        "versión modular del opuesto de un número.",
        "formula": "x = −a mod n, de modo que a + x ≡ 0 (mod n)",
        "campos": {"a": "Número a", "n": "Módulo n"},
    },
    "1.3": {
        "enunciado": "Dados el mensaje cifrado C = 1100 y la clave K = 0110, en binario, recuperar "
        "el mensaje original A.",
        "concepto": "XOR (⊕) compara dos bits y da 1 cuando son distintos y 0 cuando son iguales. "
        "Su propiedad clave es que se deshace a sí mismo: (A ⊕ K) ⊕ K = A. Por eso, si el "
        "cifrado fue C = A ⊕ K, basta aplicar de nuevo la clave para recuperar A. Es la base "
        "del cifrado Vernam (2.3).",
        "formula": "A = C ⊕ K",
        "campos": {"c": "Mensaje cifrado C", "k": "Clave K", "base": "Base de las entradas"},
    },
    "1.4": {
        "enunciado": "Calcular MCD(7, 26) con el algoritmo de Euclides y decidir si 7 tiene "
        "inverso multiplicativo módulo 26.",
        "concepto": "El algoritmo de Euclides encuentra el máximo común divisor dividiendo una y "
        "otra vez: El divisor de cada paso pasa a ser el dividendo del siguiente y el residuo, "
        "el nuevo divisor, hasta que el residuo es 0. El último residuo distinto de cero es el "
        "MCD. Dos números con MCD 1 se llaman coprimos, y un número tiene inverso módulo n "
        "exactamente cuando es coprimo con n.",
        "formula": "a = q × b + r, repetido hasta que r = 0",
        "campos": {"a": "Número a", "b": "Número b"},
    },
    "1.5": {
        "enunciado": "Hallar el inverso multiplicativo de 3 en módulo 7 probando x = 1, 2, 3, … "
        "hasta que 3 × x deje residuo 1.",
        "concepto": "El inverso multiplicativo de a módulo n es el x que cumple a × x ≡ 1 (mod n). "
        "El método tradicional lo busca por fuerza bruta: Prueba cada x desde 1 hasta dar con el "
        "residuo 1. Sirve con módulos pequeños; para módulos grandes se usa el algoritmo "
        "extendido de Euclides (1.6).",
        "formula": "a × x ≡ 1 (mod n)",
        "campos": {"a": "Número a", "n": "Módulo n"},
    },
    "1.6": {
        "enunciado": "Hallar el inverso multiplicativo de 7 en módulo 26 con la tabla del algoritmo "
        "extendido de Euclides (AEE) y comprobar el resultado.",
        "concepto": "El AEE hace las mismas divisiones de Euclides, pero además lleva dos columnas "
        "s y t que en cada fila cumplen s × n + t × a = r. Cuando el residuo r llega a 1, la "
        "identidad dice s × n + t × a = 1, y como s × n es múltiplo de n, queda t × a ≡ 1 (mod n): t es "
        "el inverso de a. Si t sale negativo se le suma n. RSA (3.2) y el cifrado afín (2.6) "
        "usan esta misma tabla.",
        "formula": "s × n + t × a = 1  ⇒  a⁻¹ = t mod n",
        "campos": {"a": "Número a", "n": "Módulo n"},
    },
    "2.1": {
        "enunciado": "Cifrar el mensaje HOLA con desplazamiento k = 3 en el alfabeto español de "
        "27 letras.",
        "concepto": "El cifrado en módulo 27 convierte cada letra en su posición (A = 0 … Ñ = 14 … "
        "Z = 26), le suma el desplazamiento k y toma el residuo módulo 27 para no salirse del "
        "alfabeto. Descifrar es restar k. Es el cifrado de César adaptado al alfabeto con Ñ.",
        "formula": "C = (M + k) mod 27\nM = (C − k) mod 27",
        "campos": {"texto": "Mensaje", "k": "Desplazamiento k", "modo": "Modo"},
    },
    "2.2": {
        "enunciado": "Cifrar HOLA con el cifrado de César, k = 3, usando el alfabeto inglés de 26 "
        "letras (sin Ñ).",
        "concepto": "El cifrado de César desplaza cada letra k posiciones. Con 26 letras el módulo "
        "es 26 y la Ñ no existe (se escribe como N). Solo hay 25 desplazamientos posibles, así "
        "que se rompe probándolos todos: Por eso hoy es solo didáctico.",
        "formula": "C = (M + k) mod 26\nM = (C − k) mod 26",
        "campos": {"texto": "Mensaje", "k": "Desplazamiento k", "alfabeto": "Alfabeto", "modo": "Modo"},
    },
    "2.3": {
        "enunciado": "Cifrar HOLA con Vernam usando la clave XMCK y mostrar el resultado en "
        "hexadecimal y en binario.",
        "concepto": "Vernam aplica XOR entre cada byte del mensaje y el byte de la clave que está "
        "en la misma posición; la clave debe medir lo mismo que el mensaje. Como XOR se deshace "
        "a sí mismo, descifrar es repetir la misma operación con la misma clave. Con una clave "
        "aleatoria, secreta y de un solo uso es el «cuaderno de un solo uso», el único cifrado "
        "matemáticamente irrompible.",
        "formula": "C = M ⊕ K\nM = C ⊕ K",
        "campos": {"texto": "Mensaje", "clave": "Clave", "modo": "Modo"},
    },
    "2.4": {
        "enunciado": "Cifrar HOLA con Atbash, el cifrado que refleja el alfabeto.",
        "concepto": "Atbash cambia la primera letra por la última, la segunda por la penúltima y "
        "así sucesivamente: La letra de la posición i pasa a la 26 − i. Reflejar dos veces "
        "devuelve el original, así que cifrar y descifrar son la misma operación. En el alfabeto "
        "de 27 letras la N (posición 13) es el centro y no cambia.",
        "formula": "C = 26 − M",
        "campos": {"texto": "Mensaje", "modo": "Modo"},
    },
    "2.5": {
        "enunciado": "Cifrar HOLAMUNDO por transposición columnar simple con la clave CLAVE.",
        "concepto": "La transposición no cambia las letras, cambia su orden. El mensaje se escribe "
        "en filas bajo la clave, se rellena con X hasta completar la última fila y se leen las "
        "columnas en el orden alfabético de las letras de la clave. Para descifrar se reparte el "
        "texto en columnas con ese mismo orden y se lee por filas.",
        "formula": "las columnas se leen en el orden alfabético de la clave",
        "campos": {"texto": "Mensaje", "clave": "Clave (palabra)", "modo": "Modo"},
    },
    "2.6": {
        "enunciado": "Cifrar HOLA con el cifrado afín de llaves a = 5 y b = 8 en el alfabeto de "
        "27 letras.",
        "concepto": "El afín combina una multiplicación y una suma: C = (a × M + b) mod 27. Para "
        "descifrar hay que deshacer la suma y luego la multiplicación, y eso exige el inverso "
        "a⁻¹ de a módulo 27, que existe solo si MCD(a, 27) = 1. El inverso se obtiene con la "
        "tabla del AEE (1.6).",
        "formula": "C = (a × M + b) mod 27\nM = a⁻¹ × (C − b) mod 27",
        "campos": {"texto": "Mensaje", "a": "Llave a", "b": "Llave b", "modo": "Modo"},
    },
    "2.7": {
        "enunciado": "Cifrar HOLA por sustitución simple con la palabra clave MURCIELAGO.",
        "concepto": "En la sustitución simple cada letra del alfabeto se reemplaza siempre por la "
        "misma letra de un alfabeto desordenado. Con una palabra clave, el alfabeto cifrado "
        "empieza con sus letras (sin repetir) y sigue con las que faltan, en orden. Hay 27! "
        "alfabetos posibles, pero el cifrado se rompe por análisis de frecuencias porque cada "
        "letra conserva su frecuencia.",
        "formula": "alfabeto cifrado = letras de la clave sin repetir + letras restantes en orden",
        "campos": {"texto": "Mensaje", "clave": "Clave (palabra)", "modo": "Modo"},
    },
    "3.1": {
        "enunciado": "Con p = 23 y g = 5 públicos, y las claves privadas a = 6 (Alicia) y b = 15 "
        "(Bob), calcular las claves públicas A y B y la clave compartida K.",
        "concepto": "Diffie-Hellman permite que dos personas acuerden un secreto por un canal "
        "público. Cada una publica una potencia de g con su exponente secreto y eleva la "
        "potencia recibida al suyo; las dos llegan al mismo K porque (gᵇ)ᵃ = (gᵃ)ᵇ. Quien "
        "escucha ve p, g, A y B, pero recuperar a o b es el problema del logaritmo discreto, "
        "intratable con primos grandes. Todas las potencias se calculan con la exponenciación "
        "rápida (3.3).",
        "formula": "A = gᵃ mod p\nB = gᵇ mod p\nK = Bᵃ mod p = Aᵇ mod p",
        "campos": {
            "p": "Primo p (público)",
            "g": "Generador g (público)",
            "a": "Clave privada de Alicia, a",
            "b": "Clave privada de Bob, b",
        },
    },
    "3.2": {
        "enunciado": "Generar las claves RSA con p = 61, q = 53 y e = 17, cifrar el mensaje m = 65 "
        "y comprobar que la clave privada lo recupera.",
        "concepto": "RSA usa dos primos secretos p y q. Su producto n es público, pero "
        "φ(n) = (p − 1)(q − 1) solo se conoce si se conocen p y q, y de φ(n) sale la clave "
        "privada d = e⁻¹ mod φ(n), con la tabla del AEE (1.6). Cifrar es elevar a e módulo n y "
        "descifrar es elevar a d; funciona porque e × d ≡ 1 (mod φ(n)). La seguridad descansa en "
        "que factorizar n es muy difícil cuando los primos son grandes.",
        "formula": "n = p × q\nφ(n) = (p − 1)(q − 1)\ne × d ≡ 1 (mod φ(n))\n"
        "c = mᵉ mod n\nm = cᵈ mod n",
        "campos": {"p": "Primo p", "q": "Primo q", "e": "Exponente e", "m": "Mensaje m"},
    },
    "3.3": {
        "enunciado": "Calcular 3¹³ mod 7 con el método de cuadrados sucesivos e indicar cuántas "
        "multiplicaciones se hacen.",
        "concepto": "La exponenciación rápida escribe el exponente en binario y eleva la base al "
        "cuadrado una y otra vez (b, b², b⁴, b⁸ …), reduciendo módulo n en cada paso para que "
        "los números no crezcan. Solo se multiplican al acumulado las potencias cuyo bit vale 1. "
        "Así se hacen unas pocas multiplicaciones en vez de e − 1; es la pieza que usan "
        "Diffie-Hellman y RSA.",
        "formula": "bᵉ mod n: e en binario, cuadrados sucesivos y producto de los bits en 1",
        "campos": {"base": "Base b", "exponente": "Exponente e", "n": "Módulo n"},
    },
    "4.1": {
        "enunciado": "Calcular el MD5 del texto «abc» y compararlo con el de «abd» para observar "
        "el efecto avalancha.",
        "concepto": "Una función hash convierte cualquier texto en una huella de tamaño fijo. Tres "
        "propiedades la definen: El mismo texto da siempre la misma huella, no se puede volver "
        "de la huella al texto y cualquier cambio en el texto cambia la huella por completo "
        "(efecto avalancha). MD5 produce 128 bits (32 dígitos hexadecimales); hoy se considera "
        "roto para seguridad, pero es ideal para estudiar cómo funciona un hash.",
        "formula": "MD5(texto) → 128 bits = 32 dígitos hexadecimales",
        "campos": {"texto": "Texto", "algoritmo": "Algoritmo", "comparar": "Texto para comparar"},
    },
    "4.2": {
        "enunciado": "Calcular el SHA-256 del texto «abc».",
        "concepto": "SHA-256 pertenece a la familia SHA-2 y produce huellas de 256 bits (64 dígitos "
        "hexadecimales). Es el hash más usado hoy: Aparece en los certificados TLS, en las firmas "
        "digitales y en la cadena de bloques de Bitcoin. Sus propiedades son las de toda función "
        "hash: Determinista, irreversible y con efecto avalancha.",
        "formula": "SHA-256(texto) → 256 bits = 64 dígitos hexadecimales",
        "campos": {"texto": "Texto", "algoritmo": "Algoritmo", "comparar": "Texto para comparar"},
    },
    "4.3": {
        "enunciado": "Calcular el SHA-512 del texto «abc».",
        "concepto": "SHA-512 es la variante grande de SHA-2: Trabaja con palabras de 64 bits, mezcla "
        "los bytes en bloques de 1024 bits y produce huellas de 512 bits (128 dígitos "
        "hexadecimales). Ofrece más margen de seguridad que SHA-256 y en procesadores de 64 bits "
        "suele ser igual de rápido.",
        "formula": "SHA-512(texto) → 512 bits = 128 dígitos hexadecimales",
        "campos": {"texto": "Texto", "algoritmo": "Algoritmo", "comparar": "Texto para comparar"},
    },
    "5.1": {
        "enunciado": "Codificar el texto «Hola» como códigos ASCII decimales separados por espacio.",
        "concepto": "ASCII asigna a cada carácter un número del 0 al 127: Las mayúsculas van de 65 "
        "a 90, las minúsculas de 97 a 122 y el espacio es 32. Codificar es escribir ese número "
        "por cada carácter. Los caracteres que no están en ASCII, como la ñ o las tildes, se "
        "representan con sus bytes UTF-8 (dos por carácter).",
        "formula": "carácter → código decimal de 0 a 127",
        "campos": {"texto": "Texto", "modo": "Modo"},
    },
    "5.2": {
        "enunciado": "Codificar el texto «Hola» en hexadecimal.",
        "concepto": "Hexadecimal es la base 16: Usa los dígitos 0 a 9 y las letras A a F (10 a 15). "
        "Un byte vale de 0 a 255 y, como 16 × 16 = 256, cada byte cabe exactamente en dos dígitos "
        "hexadecimales: El primero es el cociente de dividir entre 16 y el segundo, el residuo. "
        "Es la forma habitual de escribir bytes, hashes y direcciones de memoria.",
        "formula": "byte = d1 × 16 + d0  →  dos dígitos hexadecimales d1 d0",
        "campos": {"texto": "Texto", "modo": "Modo"},
    },
    "5.3": {
        "enunciado": "Codificar el texto «Hola» en binario, con 8 bits por byte.",
        "concepto": "El computador guarda cada byte como 8 bits, y cada bit es un 0 o un 1. Los "
        "bits valen 128, 64, 32, 16, 8, 4, 2 y 1 de izquierda a derecha: El byte es la suma de "
        "los valores de los bits en 1. Codificar en binario es escribir esos 8 bits por cada byte "
        "del texto en UTF-8.",
        "formula": "byte = b7 × 128 + b6 × 64 + b5 × 32 + b4 × 16 + b3 × 8 + b2 × 4 + b1 × 2 + b0 × 1",
        "campos": {"texto": "Texto", "modo": "Modo"},
    },
    "5.4": {
        "enunciado": "Codificar el texto «Hola» en Base64.",
        "concepto": "Base64 sirve para escribir bytes cualesquiera usando solo 64 caracteres seguros "
        "(A–Z, a–z, 0–9, + y /), por ejemplo para adjuntar archivos en un correo o incrustar "
        "imágenes en HTML. Toma los bits de 6 en 6 (2⁶ = 64) y cada grupo elige un carácter; el "
        "resultado va en bloques de 4 caracteres y el relleno «=» completa el último. Ocupa un "
        "tercio más que los bytes originales.",
        "formula": "3 bytes = 24 bits → 4 grupos de 6 bits → 4 caracteres",
        "campos": {"texto": "Texto", "modo": "Modo"},
    },
    "6.1": {
        "enunciado": "Comprobar si la clave «Clave123» es correcta a partir del salt a1b2c3d4 y el "
        "hash MD5 guardado.",
        "concepto": "Un sistema no debe guardar las claves de sus usuarios: Guarda un salt (un valor "
        "aleatorio único por usuario) y el hash de salt + clave. Para verificar una clave repite "
        "la fórmula con el salt guardado y compara el resultado con el hash guardado. El salt "
        "hace que dos usuarios con la misma clave tengan hashes distintos y que las tablas de "
        "hashes precalculados no sirvan. En la práctica se usan funciones lentas como bcrypt, "
        "Argon2 o PBKDF2.",
        "formula": "hash = MD5(salt + clave)",
        "campos": {
            "clave": "Clave a comprobar",
            "salt": "Salt guardado",
            "hash_guardado": "Hash guardado",
            "algoritmo": "Algoritmo",
        },
    },
    "6.2": {
        "enunciado": "Comprobar si la clave «Clave123» es correcta a partir del salt a1b2c3d4 y el "
        "hash SHA-256 guardado.",
        "concepto": "Igual que con MD5, el sistema guarda el salt y el hash de salt + clave, nunca "
        "la clave. Con SHA-256 la huella mide 256 bits (64 dígitos hexadecimales), lo que hace "
        "inviable adivinarla por fuerza bruta. El salt, único por usuario, evita que dos claves "
        "iguales produzcan el mismo hash y anula las tablas precalculadas.",
        "formula": "hash = SHA-256(salt + clave)",
        "campos": {
            "clave": "Clave a comprobar",
            "salt": "Salt guardado",
            "hash_guardado": "Hash guardado",
            "algoritmo": "Algoritmo",
        },
    },
    "6.3": {
        "enunciado": "Comprobar si la clave «Clave123» es correcta a partir del salt a1b2c3d4 y el "
        "hash SHA-512 guardado.",
        "concepto": "Con SHA-512 la huella mide 512 bits (128 dígitos hexadecimales). El "
        "procedimiento es el mismo: Pegar el salt delante de la clave, calcular el hash y "
        "comparar con el guardado. Si coinciden, la clave es correcta; si no, la clave o el salt "
        "no son los originales.",
        "formula": "hash = SHA-512(salt + clave)",
        "campos": {
            "clave": "Clave a comprobar",
            "salt": "Salt guardado",
            "hash_guardado": "Hash guardado",
            "algoritmo": "Algoritmo",
        },
    },
}

# Cada ejemplo lleva sus textos: enunciado, concepto, formula y campos
for _ejemplo in EJEMPLOS:
    _ejemplo.update(EXPLICACIONES[_ejemplo["id"]])
assert set(EXPLICACIONES) == {e["id"] for e in EJEMPLOS}, "cada ejemplo necesita su explicación"
