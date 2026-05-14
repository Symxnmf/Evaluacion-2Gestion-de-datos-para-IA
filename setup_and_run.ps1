<#
setup_and_run.ps1
Script en español para preparar el entorno virtual, instalar dependencias
y ejecutar el pipeline en Windows PowerShell.

Uso: abrir PowerShell en la carpeta del proyecto y ejecutar:
    .\setup_and_run.ps1

#>

$ErrorActionPreference = 'Stop'

Write-Host "== Preparando entorno para Evaluacion_parcial2 ==" -ForegroundColor Cyan

# Buscar lanzador de Python
if (Get-Command py -ErrorAction SilentlyContinue) {
    $python = 'py'
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $python = 'python'
} else {
    Write-Host "Python no se encontró en el sistema. Instala Python 3 y marca 'Add Python to PATH' en el instalador." -ForegroundColor Red
    exit 1
}

Write-Host "Usando: $python" -ForegroundColor Green

# Crear venv si no existe
if (-not (Test-Path .\venv)) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    & $python -3 -m venv venv
} else {
    Write-Host "Entorno virtual ya existe." -ForegroundColor Yellow
}

# Ajustar política de ejecución para el usuario (necesario para activar scripts)
try {
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "Política de ejecución configurada: RemoteSigned" -ForegroundColor Green
} catch {
    Write-Host "No se pudo cambiar la política de ejecución automáticamente. Ejecuta: Set-ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Red
}

# Activar el venv (dot-sourcing para mantener variables en el mismo contexto)
$act = Join-Path $PWD "venv\Scripts\Activate.ps1"
if (Test-Path $act) {
    Write-Host "Activando entorno virtual..." -ForegroundColor Yellow
    . $act
} else {
    Write-Host "No se encontró el script de activación en $act" -ForegroundColor Red
    exit 1
}

Write-Host "Actualizando pip e instalando dependencias..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "Ejecutando pipeline (ingesta → procesamiento → validación → carga)..." -ForegroundColor Cyan
python -m src.pipeline

Write-Host "Pipeline finalizado. Comprueba data/db/titanic.db y /data/processed." -ForegroundColor Green
