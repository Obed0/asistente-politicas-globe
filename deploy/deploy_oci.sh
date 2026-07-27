#!/usr/bin/env bash
# ---------------------------------------------------------------------
# deploy_oci.sh
#
# Este script se ejecuta DENTRO de la instancia de OCI Compute (VM.Standard.E2.1.Micro
# del Always Free Tier, con Ubuntu 22.04) para instalar dependencias,
# clonar el repositorio y dejar la app corriendo como servicio (systemd),
# accesible públicamente en el puerto 8501.
#
# Uso (una vez conectado por SSH a la instancia):
#   chmod +x deploy_oci.sh
#   ./deploy_oci.sh
# ---------------------------------------------------------------------
set -e

REPO_URL="https://github.com/TU_USUARIO/asistente-politicas-globex.git"
CARPETA_PROYECTO="/home/ubuntu/asistente-politicas-globex"
USUARIO_SERVICIO="ubuntu"

echo "🔄 Actualizando paquetes del sistema..."
sudo apt-get update -y
sudo apt-get upgrade -y

echo "🐍 Instalando Python, pip, venv y git..."
sudo apt-get install -y python3 python3-pip python3-venv git

echo "🔽 Clonando el repositorio del proyecto..."
if [ ! -d "$CARPETA_PROYECTO" ]; then
    git clone "$REPO_URL" "$CARPETA_PROYECTO"
fi
cd "$CARPETA_PROYECTO"

echo "🐍 Creando entorno virtual e instalando dependencias..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

echo "📄 Generando los documentos dummy (RH + e-commerce)..."
python generar_pdf_dummy.py
python generar_documentos_ecommerce.py

echo "🔑 Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Edita el archivo .env dentro de la instancia con tu GROQ_API_KEY real:"
    echo "    nano $CARPETA_PROYECTO/.env"
fi

echo "🧩 Instalando el servicio systemd para mantener la app siempre activa..."
sudo cp deploy/asistente_globex.service /etc/systemd/system/asistente_globex.service
sudo systemctl daemon-reload
sudo systemctl enable asistente_globex
sudo systemctl restart asistente_globex

echo ""
echo "✅ Deploy completado."
echo "   Verifica el estado con:  sudo systemctl status asistente_globex"
echo "   Revisa logs con:         sudo journalctl -u asistente_globex -f"
echo ""
echo "⚠️  IMPORTANTE — Reglas de red en OCI:"
echo "   1) En la 'Security List' o 'Network Security Group' de tu VCN,"
echo "      agrega una regla de ingreso (Ingress Rule):"
echo "        - Source CIDR: 0.0.0.0/0"
echo "        - Protocolo: TCP"
echo "        - Puerto destino: 8501"
echo "   2) En el firewall interno de Ubuntu, abre también el puerto:"
echo "        sudo iptables -I INPUT -p tcp --dport 8501 -j ACCEPT"
echo "        sudo netfilter-persistent save"
echo ""
echo "   Luego accede desde tu navegador a: http://<IP_PUBLICA_DE_TU_INSTANCIA>:8501"
