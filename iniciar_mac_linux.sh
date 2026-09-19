#!/usr/bin/env bash
# Numa · Calculadora criptográfica
# Uso: bash iniciar_mac_linux.sh
set -e
cd "$(dirname "$0")"

if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v python >/dev/null 2>&1; then PY=python
else
  echo "No se encontró Python. Instálalo desde https://www.python.org/downloads/"
  exit 1
fi

if [ ! -x ".venv/bin/python" ]; then
  echo "Creando entorno virtual .venv ..."
  "$PY" -m venv .venv
fi

if ! cmp -s requirements.txt .venv/requirements.instalado; then
  echo "Instalando dependencias ..."
  .venv/bin/python -m pip install --upgrade pip
  .venv/bin/python -m pip install -r requirements.txt
  cp requirements.txt .venv/requirements.instalado
fi

echo "Abriendo la aplicación en http://localhost:8501 (Ctrl+C para cerrar)"
.venv/bin/python -m streamlit run app.py
