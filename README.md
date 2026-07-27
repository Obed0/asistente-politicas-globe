# 🤖 Asistente de Políticas Internas — Globex Corp

Proyecto desarrollado para el **Challenge Alura Agente**: un agente de
Inteligencia Artificial basado en **RAG (Retrieval Augmented Generation)**
capaz de responder preguntas en lenguaje natural sobre el manual de
políticas internas de una empresa ficticia, **Globex Corp**, con deploy
funcional en la nube de **Oracle Cloud Infrastructure (OCI)**.

> Proyecto adaptado a partir de una arquitectura de referencia
> ([asistente-politicas-technova](https://github.com/liza18/asistente-politicas-technova)),
> personalizado con documentación propia, empresa ficticia distinta
> (Globex Corp) y deploy propio en OCI Compute.

---

## 📌 Descripción general

El sistema permite a cualquier colaborador de Globex Corp preguntar, en
lenguaje natural, sobre las políticas de la empresa (vacaciones, viáticos,
trabajo remoto, código de ética, etc.) y recibir una respuesta precisa
generada por un modelo de lenguaje (LLM), fundamentada exclusivamente en
el contenido del manual corporativo real, evitando respuestas inventadas
("alucinaciones") del modelo.

## 🏗️ Arquitectura de la solución

```
┌──────────────────────┐
│  Manual_Politicas_    │
│  GlobexCorp.pdf        │  <- generado por generar_pdf_dummy.py
└──────────┬────────────┘
           │  PyPDFLoader
           ▼
┌──────────────────────┐
│ RecursiveCharacter     │  chunk_size=1200
│ TextSplitter           │  chunk_overlap=300
└──────────┬────────────┘
           │  fragmentos de texto
           ▼
┌──────────────────────┐
│ HuggingFaceEmbeddings  │  all-MiniLM-L6-v2
└──────────┬────────────┘
           │  vectores
           ▼
┌──────────────────────┐
│  Vector Store FAISS    │  índice local (indice_faiss/)
└──────────┬────────────┘
           │  retriever (top-k=4)
           ▼
┌──────────────────────┐      ┌──────────────────────┐
│ ConversationalRetrieval│◄────►│ ConversationBufferMem │
│ Chain (LangChain)      │      │ (historial de chat)    │
└──────────┬────────────┘      └──────────────────────┘
           │
           ▼
┌──────────────────────┐
│ ChatGroq                │  llama-3.1-8b-instant
│ (Groq Cloud API)        │  (gratuito)
└──────────┬────────────┘
           │  respuesta
           ▼
┌──────────────────────┐
│  Interfaz Streamlit     │  chat interactivo + sidebar
└──────────────────────┘
```

**Componentes técnicos:**

| Componente               | Tecnología                                             |
|---------------------------|----------------------------------------------------------|
| Orquestación RAG          | [LangChain](https://www.langchain.com/)                  |
| Vector Database            | [FAISS](https://github.com/facebookresearch/faiss) (local)|
| Embeddings                 | HuggingFace `all-MiniLM-L6-v2` (sentence-transformers)   |
| LLM                        | `llama-3.1-8b-instant` vía [Groq Cloud](https://groq.com/)|
| Interfaz de usuario        | [Streamlit](https://streamlit.io/)                        |
| Procesamiento de PDF        | `PyPDFLoader` + `RecursiveCharacterTextSplitter`          |
| Generación del documento    | `reportlab` (PDF dummy corporativo)                       |
| Deploy                       | OCI Compute (VM.Standard.E2.1.Micro, Always Free Tier)    |

## 📂 Estructura del repositorio

```
asistente-politicas-globex/
├── app.py                       # Aplicación Streamlit con la cadena RAG
├── generar_pdf_dummy.py         # Genera el manual PDF de Globex Corp
├── documentos/                  # Carpeta donde vive el PDF fuente
│   └── Manual_Politicas_GlobexCorp.pdf
├── indice_faiss/                # Índice vectorial (se genera automáticamente)
├── requirements.txt             # Dependencias del proyecto
├── .env.example                 # Plantilla de variables de entorno
├── .gitignore
├── setup_local.sh               # Instalación y ejecución local (Linux/Mac)
├── setup_local.ps1              # Instalación y ejecución local (Windows)
└── deploy/
    ├── deploy_oci.sh            # Script de deploy dentro de la VM de OCI
    ├── asistente_globex.service # Servicio systemd (auto-inicio en OCI)
    └── DEPLOY_OCI.md            # Guía paso a paso del deploy en OCI
```

## 🚀 Instrucciones para ejecutar el proyecto localmente

### Requisitos previos
- Python 3.10 o superior
- Una clave de API gratuita de Groq: [console.groq.com/keys](https://console.groq.com/keys)

### Opción A — Script automático

**Linux / macOS:**
```bash
chmod +x setup_local.sh
./setup_local.sh
```

**Windows (PowerShell):**
```powershell
.\setup_local.ps1
```

### Opción B — Paso a paso manual

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU_USUARIO/asistente-politicas-globex.git
cd asistente-politicas-globex

# 2. Crear y activar entorno virtual
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Generar el documento PDF dummy
python generar_pdf_dummy.py

# 5. Configurar variables de entorno
cp .env.example .env
# Edita el archivo .env y coloca tu GROQ_API_KEY real

# 6. Ejecutar la aplicación
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

> 💡 También puedes prototipar todo el flujo en **Google Colab** antes de
> correrlo localmente: sube `generar_pdf_dummy.py` y `app.py`, instala
> las dependencias de `requirements.txt` con `!pip install`, y prueba la
> lógica de la cadena RAG en celdas antes de pasar a Streamlit.

## 💬 Ejemplos de preguntas y respuestas del agente

| Pregunta                                                              | Respuesta esperada (resumen)                                                                 |
|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------|
| *¿Cuántos días de vacaciones me corresponden con 6 años de antigüedad?* | Con 6 años de antigüedad corresponden **20 días hábiles** de vacaciones al año, según la tabla de la sección 1.1. |
| *¿Cuál es el tope diario de viáticos de alimentación en un viaje internacional?* | El tope diario para alimentación en viaje internacional es de **USD 60**. |
| *¿Qué equipo me da la empresa si trabajo en modalidad remota?*         | La empresa entrega en préstamo **laptop corporativa, monitor adicional (según stock), teclado y mouse inalámbricos**, y silla ergonómica tras 6 meses en remoto. |
| *¿Cómo puedo denunciar una situación de acoso laboral de forma confidencial?* | A través de la **Línea Ética Globex**, un canal anónimo disponible 24/7 vía portal web, correo dedicado o línea telefónica gratuita. |
| *¿Cuál es la política de vacaciones de la empresa X?* (fuera del documento) | El agente indica que **no cuenta con esa información en el manual** y sugiere contactar a Recursos Humanos, en lugar de inventar una respuesta. |

## ☁️ Evidencia del Deploy en OCI

- **URL pública de la aplicación:** `http://<IP_PUBLICA_DE_TU_INSTANCIA>:8501`
  _(reemplazar con la IP real de la instancia una vez desplegada)_
- **Captura de pantalla:** ver `deploy/screenshot-oci.png` _(agregar la captura real de la app corriendo en OCI)_
- **Guía completa del proceso de deploy:** [`deploy/DEPLOY_OCI.md`](deploy/DEPLOY_OCI.md)

## 🧠 Decisiones técnicas y notas

- Se usa **FAISS local** (en lugar de un servicio administrado) para
  mantener el proyecto simple, gratuito y fácil de reproducir en la
  instancia Always Free de OCI.
- El LLM (`llama-3.1-8b-instant` en Groq Cloud) fue elegido por ser
  **gratuito y de baja latencia**, ideal para una demo funcional.
- La memoria de conversación (`ConversationBufferMemory`) permite hacer
  preguntas de seguimiento (ej. *"¿y si tengo 10 años de antigüedad?"*)
  manteniendo el contexto del chat.
- El prompt del sistema obliga al modelo a responder **solo con base en
  el contexto recuperado**, y a admitir cuando no tiene la información,
  reduciendo alucinaciones.

## 📄 Licencia y uso

Proyecto desarrollado con fines educativos para el Challenge Alura Agente
(Alura LATAM / Oracle). Los datos de "Globex Corp" son ficticios.
