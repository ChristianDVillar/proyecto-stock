# Arrancar backend en desarrollo (PowerShell)
# Uso: .\scripts\run_backend.ps1
# Ejecutar desde la raíz del proyecto: proyecto-stock

$ErrorActionPreference = "Stop"
# Raíz del proyecto (carpeta que contiene src/ y requirements.txt)
$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $root "src"))) {
    $root = (Get-Location).Path
}
Set-Location $root

$env:PYTHONPATH = "src"
$env:FLASK_APP = "src/run.py"
$env:FLASK_ENV = "development"

Write-Host "Instalando dependencias (desarrollo con SQLite, sin psycopg2)..." -ForegroundColor Cyan
pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Intentando con requirements.txt completo (por si usas PostgreSQL)..." -ForegroundColor Yellow
    pip install -r requirements.txt
}
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Aplicando migraciones..." -ForegroundColor Cyan
flask db upgrade
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Iniciando servidor Flask..." -ForegroundColor Green
python src/run.py
