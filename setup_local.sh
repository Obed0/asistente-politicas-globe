#!/usr/bin/env bash
# ---------------------------------------------------------------------
# setup_local.sh
# Clona el repositorio, crea un entorno virtual, instala dependencias,
# genera el PDF dummy y levanta la aplicación Streamlit localmente.
#
# Uso:
#   chmod +x setup_local.sh
#   ./setup_local.sh
# ---------------------------------------------------------------------
set -e  # Detener el script si algún comando falla

REPO_URL="https://github.com/TU_USUARIO/asistente-politicas-globex.git"
CARPETA_PROYECTO="asistente-politicas-globex"

echo "🔽 Clonando el repositorio..."
if [ ! -d "$CARPETA_PROYECTO" ]; then
    git clone "$REPO_URL"
fi
cd "$CARPETA_PROYECTO"

echo "🐍 Creando entorno virtual (venv)..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt

echo "📄 Generando los documentos dummy (RH + e-commerce)..."
python generar_pdf_dummy.py
python generar_documentos_ecommerce.py

if [ ! -f ".env" ]; then
    echo "⚠️  No se encontró el archivo .env"
    echo "    Copiando .env.example -> .env. Recuerda editarlo con tu GROQ_API_KEY."
    cp .env.example .env
fi

echo "🚀 Iniciando la aplicación Streamlit..."
streamlit run app.py
