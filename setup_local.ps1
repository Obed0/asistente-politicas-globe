# ---------------------------------------------------------------------
# setup_local.ps1
# Clona el repositorio, crea un entorno virtual, instala dependencias,
# genera el PDF dummy y levanta la aplicación Streamlit localmente.
#
# Uso (desde PowerShell):
#   .\setup_local.ps1
# ---------------------------------------------------------------------

$RepoUrl = "https://github.com/TU_USUARIO/asistente-politicas-globex.git"
$Carpeta = "asistente-politicas-globex"

Write-Host "🔽 Clonando el repositorio..." -ForegroundColor Cyan
if (-Not (Test-Path $Carpeta)) {
    git clone $RepoUrl
}
Set-Location $Carpeta

Write-Host "🐍 Creando entorno virtual (venv)..." -ForegroundColor Cyan
python -m venv venv
.\venv\Scripts\Activate.ps1

Write-Host "📦 Instalando dependencias..." -ForegroundColor Cyan
python -m pip install --upgrade pip
pip install -r requirements.txt

Write-Host "📄 Generando el manual de políticas dummy (PDF)..." -ForegroundColor Cyan
python generar_pdf_dummy.py

if (-Not (Test-Path ".env")) {
    Write-Host "⚠️  No se encontró el archivo .env" -ForegroundColor Yellow
    Write-Host "    Copiando .env.example -> .env. Recuerda editarlo con tu GROQ_API_KEY." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
}

Write-Host "🚀 Iniciando la aplicación Streamlit..." -ForegroundColor Cyan
streamlit run app.py
