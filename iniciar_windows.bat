@echo off
chcp 65001 >nul
title Numa - Calculadora criptografica
cd /d "%~dp0"

echo.
echo   Numa - Calculadora criptografica
echo   --------------------------------
echo.

rem 1. Buscar Python
set "PY="
where py >nul 2>&1 && set "PY=py -3"
if not defined PY (
  where python >nul 2>&1 && set "PY=python"
)
if not defined PY (
  echo   No se encontro Python en este equipo.
  echo   Instalalo desde https://www.python.org/downloads/
  echo   y marca la casilla "Add python.exe to PATH".
  pause
  exit /b 1
)

rem 2. Crear el entorno virtual la primera vez
if not exist ".venv\Scripts\python.exe" (
  echo   Creando entorno virtual .venv ...
  %PY% -m venv .venv
  if errorlevel 1 (
    echo   No se pudo crear el entorno virtual.
    pause
    exit /b 1
  )
)

rem 3. Instalar dependencias la primera vez (o si cambio requirements.txt)
fc /b requirements.txt ".venv\requirements.instalado" >nul 2>&1
if errorlevel 1 (
  echo   Instalando dependencias, esto tarda un par de minutos la primera vez ...
  ".venv\Scripts\python.exe" -m pip install --upgrade pip
  ".venv\Scripts\python.exe" -m pip install -r requirements.txt
  if errorlevel 1 (
    echo   Fallo la instalacion. Revisa la conexion a internet.
    pause
    exit /b 1
  )
  copy /y requirements.txt ".venv\requirements.instalado" >nul
)

rem 4. Abrir la aplicacion en el navegador
echo   Abriendo la aplicacion en http://localhost:8501
echo   Para cerrarla, cierra esta ventana.
".venv\Scripts\python.exe" -m streamlit run app.py
pause
