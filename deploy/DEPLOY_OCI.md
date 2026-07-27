# ☁️ Guía de Deploy en OCI Compute (Oracle Cloud Infrastructure)

Esta guía documenta cómo desplegar el asistente en una instancia gratuita
(*Always Free Tier*) de OCI Compute para cumplir con el requisito de deploy
en la nube del Challenge Alura Agente.

## 1. Crear la cuenta y la instancia

1. Crea una cuenta gratuita en [cloud.oracle.com](https://www.oracle.com/cloud/free/).
2. En el menú, ve a **Compute → Instances → Create Instance**.
3. Configura:
   - **Name:** `asistente-globex`
   - **Image:** `Canonical Ubuntu 22.04`
   - **Shape:** `VM.Standard.E2.1.Micro` (elegible en el Always Free Tier)
   - **Networking:** deja la VCN por defecto, con IP pública asignada automáticamente.
   - **Add SSH keys:** sube tu clave pública SSH (o genera un par nuevo y descarga la privada).
4. Haz clic en **Create** y espera a que el estado pase a `Running`.
5. Copia la **IP pública** de la instancia (la usarás para conectarte y para acceder a la app).

## 2. Abrir el puerto 8501 en la red de OCI

1. Ve a **Networking → Virtual Cloud Networks → (tu VCN) → Security Lists**.
2. Entra a la Security List asociada a la subred pública.
3. Agrega una **Ingress Rule**:
   - **Source CIDR:** `0.0.0.0/0`
   - **IP Protocol:** TCP
   - **Destination Port Range:** `8501`
4. Guarda los cambios.

> Sin este paso, la aplicación funcionará dentro de la instancia pero
> **no será accesible públicamente**, aunque el servicio esté activo.

## 3. Conectarte por SSH a la instancia

```bash
chmod 400 tu-clave-privada.key
ssh -i tu-clave-privada.key ubuntu@<IP_PUBLICA_DE_TU_INSTANCIA>
```

## 4. Ejecutar el script de deploy

Ya dentro de la instancia:

```bash
git clone https://github.com/TU_USUARIO/asistente-politicas-globex.git
cd asistente-politicas-globex
chmod +x deploy/deploy_oci.sh
./deploy/deploy_oci.sh
```

El script instala Python, clona el proyecto, crea el entorno virtual,
instala dependencias, genera el PDF dummy, y configura la app como
**servicio systemd** (`asistente_globex.service`) para que:

- Se inicie automáticamente si la instancia se reinicia.
- Se reinicie solo si el proceso falla (`Restart=always`).
- Corra en segundo plano sin necesitar una sesión SSH abierta.

## 5. Configurar la GROQ_API_KEY en el servidor

```bash
nano /home/ubuntu/asistente-politicas-globex/.env
# Reemplaza el valor de ejemplo por tu clave real de https://console.groq.com/keys

sudo systemctl restart asistente_globex
```

## 6. Verificar que todo esté funcionando

```bash
sudo systemctl status asistente_globex     # Debe mostrar "active (running)"
sudo journalctl -u asistente_globex -f     # Logs en tiempo real
```

## 7. Acceder a la aplicación desde tu navegador

```
http://<IP_PUBLICA_DE_TU_INSTANCIA>:8501
```

Toma una captura de pantalla de la aplicación funcionando desde esta URL
pública y agrégala al `README.md` principal (sección "Evidencia del Deploy"),
junto con el enlace, para cumplir con el entregable del challenge.

## Comandos útiles de administración

| Acción                          | Comando                                             |
|----------------------------------|------------------------------------------------------|
| Ver estado del servicio          | `sudo systemctl status asistente_globex`             |
| Reiniciar el servicio             | `sudo systemctl restart asistente_globex`            |
| Detener el servicio               | `sudo systemctl stop asistente_globex`               |
| Ver logs en vivo                  | `sudo journalctl -u asistente_globex -f`             |
| Actualizar código (tras un push)  | `cd asistente-politicas-globex && git pull && sudo systemctl restart asistente_globex` |
