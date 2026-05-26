<#
run_all.ps1
Automatiza: crear/activar venv, cargar .env en la sesión, instalar dependencias,
ejecutar el pipeline y levantar la demo Flask.

Uso: abrir PowerShell en la raíz del repo y ejecutar:
    .\run_all.ps1

El script modifica la política de ejecución solo para la sesión actual.
#>

# Permitir ejecución en esta sesión
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned -Force

# Mover al directorio del script
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

# Crear venv si no existe
if (-not (Test-Path ".\venv")) {
    Write-Host "Creando virtualenv..."
    py -3 -m venv venv
}

# Activar venv
Write-Host "Activando virtualenv..."
.\venv\Scripts\Activate.ps1

# Actualizar pip e instalar dependencias
Write-Host "Instalando dependencias..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Cargar .env en variables de entorno de la sesión (si existe)
if (Test-Path ".env") {
    Write-Host "Cargando .env en variables de entorno de la sesión..."
    Get-Content .env | ForEach-Object {
        if ($_ -and -not ($_ -match '^\s*#')) {
            $parts = $_ -split '=', 2
            if ($parts.Length -eq 2) {
                $name = $parts[0].Trim()
                $value = $parts[1].Trim()
                if ($name) { Set-Item -Path env:$name -Value $value }
            }
        }
    }
} else {
    Write-Host ".env no encontrado - se usará configuracion por defecto/fallback."
}

# Ejecutar pipeline
Write-Host "Ejecutando pipeline..."
python -m src.pipeline

# Levantar la demo Flask (bloqueante)
Write-Host "Iniciando demo Flask (Ctrl+C para detener)..."
python app.py
