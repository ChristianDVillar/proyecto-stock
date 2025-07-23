@echo off
echo Configurando el entorno...

REM Crear entorno virtual si no existe
if not exist "venv" (
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
pip install flask flask-sqlalchemy flask-jwt-extended flask-login werkzeug

REM Ejecutar script de inicialización
python init_db.py

echo Configuración completada.
pause 