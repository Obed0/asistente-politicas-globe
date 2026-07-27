"""
app.py
---------------------------------------------------------------------
Asistente RAG (Retrieval Augmented Generation) de Políticas Internas
Empresa ficticia: Globex Corp

Arquitectura:
    PDF (documentos/Manual_Politicas_GlobexCorp.pdf)
        -> PyPDFLoader (carga)
        -> RecursiveCharacterTextSplitter (chunk_size=1200, overlap=300)
        -> Embeddings HuggingFace (all-MiniLM-L6-v2)
        -> Vector Store FAISS (local, en disco)
        -> Retriever (top-k)
        -> ChatGroq (llama-3.1-8b-instant)
        -> Cadena de Conversación con memoria (st.session_state)
        -> Interfaz de chat en Streamlit

Ejecutar con:  streamlit run app.py
---------------------------------------------------------------------
"""

import os
import glob
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate

# =====================================================================
# 1. Configuración inicial de la página y variables de entorno
# =====================================================================
st.set_page_config(
    page_title="Asistente de Políticas · Globex Corp",
    page_icon="🤖",
    layout="centered",
)

load_dotenv()  # Carga variables desde el archivo .env si existe localmente

CARPETA_DOCUMENTOS = "documentos"
CARPETA_INDICE_FAISS = "indice_faiss"
MODELO_EMBEDDINGS = "sentence-transformers/all-MiniLM-L6-v2"
MODELO_LLM = "llama-3.1-8b-instant"
CHUNK_SIZE = 1200
CHUNK_OVERLAP = 300


# =====================================================================
# 2. Barra lateral: gestión de la API Key de Groq
# =====================================================================
def obtener_groq_api_key() -> str:
    """
    Obtiene la GROQ_API_KEY, primero desde variables de entorno (.env)
    y, si no existe, permite ingresarla manualmente desde la barra lateral.
    """
    with st.sidebar:
        st.header("⚙️ Configuración")
        st.markdown("**Globex Corp** — Asistente de Políticas Internas")
        st.divider()

        api_key_env = os.getenv("GROQ_API_KEY", "")
        api_key_input = st.text_input(
            "GROQ_API_KEY",
            value=api_key_env,
            type="password",
            help="Obtén tu clave gratuita en https://console.groq.com/keys",
        )

        if api_key_input:
            st.success("✅ API Key configurada", icon="✅")
        else:
            st.warning("⚠️ Ingresa tu GROQ_API_KEY para poder usar el asistente.")

        st.divider()
        st.caption(
            "Este asistente responde exclusivamente en base al "
            "**Manual de Políticas Internas** de Globex Corp."
        )

        if st.button("🗑️ Reiniciar conversación"):
            st.session_state.pop("historial_chat", None)
            st.session_state.pop("memoria", None)
            st.rerun()

    return api_key_input


# =====================================================================
# 3. Construcción / carga de la base vectorial (FAISS)
# =====================================================================
@st.cache_resource(show_spinner="📚 Procesando documentos y creando índice vectorial...")
def construir_vectorstore():
    """
    Carga todos los PDF de la carpeta 'documentos', los divide en
    fragmentos (chunks) y construye (o recupera desde disco) un índice
    vectorial FAISS usando embeddings de HuggingFace.
    """
    rutas_pdf = glob.glob(os.path.join(CARPETA_DOCUMENTOS, "*.pdf"))

    if not rutas_pdf:
        return None, 0

    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)

    # Si ya existe un índice guardado en disco, lo reutilizamos (más rápido)
    if os.path.isdir(CARPETA_INDICE_FAISS):
        vectorstore = FAISS.load_local(
            CARPETA_INDICE_FAISS,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        # Aun así devolvemos el conteo real de chunks re-procesando en memoria
        # (barato, solo para mostrar la métrica en la interfaz)
        documentos = []
        for ruta in rutas_pdf:
            documentos.extend(PyPDFLoader(ruta).load())
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP
        )
        total_chunks = len(splitter.split_documents(documentos))
        return vectorstore, total_chunks

    # 1) Cargar todos los PDF encontrados
    documentos = []
    for ruta in rutas_pdf:
        loader = PyPDFLoader(ruta)
        documentos.extend(loader.load())

    # 2) Dividir en fragmentos (chunks) con superposición
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    fragmentos = splitter.split_documents(documentos)

    # 3) Crear el índice vectorial FAISS y guardarlo en disco
    vectorstore = FAISS.from_documents(fragmentos, embeddings)
    vectorstore.save_local(CARPETA_INDICE_FAISS)

    return vectorstore, len(fragmentos)


# =====================================================================
# 4. Construcción de la cadena conversacional RAG
# =====================================================================
def construir_cadena_rag(vectorstore, groq_api_key: str):
    """
    Arma la cadena ConversationalRetrievalChain: LLM (Groq) + Retriever
    (FAISS) + Memoria de conversación (para mantener contexto entre turnos).
    """
    llm = ChatGroq(
        api_key=groq_api_key,
        model=MODELO_LLM,
        temperature=0.2,
    )

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    memoria = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )

    prompt_qa = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "Eres el asistente virtual de Globex Corp, una tienda online. "
            "Respondes tanto preguntas internas de RH (vacaciones, viáticos, "
            "trabajo remoto, ética) como preguntas de clientes sobre la tienda "
            "(privacidad, reembolsos, envíos, términos y condiciones, FAQ). "
            "Responde SIEMPRE en español, de forma clara y concisa, basándote "
            "únicamente en el siguiente contexto extraído de los documentos "
            "oficiales de Globex Corp. Si la respuesta no se encuentra en el "
            "contexto, indica explícitamente que no cuentas con esa "
            "información y sugiere contactar a RH (temas internos) o a "
            "soporte@globexcorp.com (temas de clientes), según corresponda.\n\n"
            "Contexto:\n{context}\n\n"
            "Pregunta: {question}\n"
            "Respuesta:"
        ),
    )

    cadena = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memoria,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt_qa},
        verbose=False,
    )

    return cadena


# =====================================================================
# 5. Interfaz principal de la aplicación
# =====================================================================
def main():
    st.title("🤖 Asistente de Políticas Internas")
    st.caption("Globex Corp · Agente RAG basado en el Manual de Políticas Internas")

    groq_api_key = obtener_groq_api_key()

    # --- Validación: sin PDF no hay nada que hacer -----------------------
    if not glob.glob(os.path.join(CARPETA_DOCUMENTOS, "*.pdf")):
        st.error(
            "❌ No se encontró ningún PDF en la carpeta `documentos/`.\n\n"
            "Ejecuta primero: `python generar_pdf_dummy.py` para generar el "
            "manual de ejemplo, o coloca allí tu propio documento PDF."
        )
        st.stop()

    # --- Validación: sin API Key no se puede llamar al LLM ---------------
    if not groq_api_key:
        st.info(
            "👈 Ingresa tu **GROQ_API_KEY** en la barra lateral para comenzar "
            "a chatear con el asistente.\n\n"
            "Puedes obtener una clave gratuita en "
            "[console.groq.com/keys](https://console.groq.com/keys)."
        )
        st.stop()

    # --- Construcción del índice vectorial (una sola vez, cacheado) ------
    try:
        vectorstore, total_chunks = construir_vectorstore()
    except Exception as error:
        st.error(f"❌ Error al procesar los documentos: {error}")
        st.stop()

    if vectorstore is None:
        st.error("❌ No fue posible construir el índice vectorial.")
        st.stop()

    st.caption(f"📄 Base de conocimiento indexada: {total_chunks} fragmentos de texto.")

    # --- Construcción de la cadena RAG (depende de la API key) -----------
    try:
        cadena_rag = construir_cadena_rag(vectorstore, groq_api_key)
    except Exception as error:
        st.error(
            "❌ No fue posible inicializar el modelo de lenguaje. "
            f"Verifica tu GROQ_API_KEY. Detalle técnico: {error}"
        )
        st.stop()

    # --- Historial de conversación en session_state -----------------------
    if "historial_chat" not in st.session_state:
        st.session_state.historial_chat = [
            {
                "rol": "assistant",
                "contenido": (
                    "¡Hola! 👋 Soy el asistente de Globex Corp. Puedo responder "
                    "preguntas de RH y también de tienda online. Por ejemplo:\n\n"
                    "- ¿Cuántos días de vacaciones me corresponden con 6 años "
                    "de antigüedad?\n"
                    "- ¿Cuántos días tengo para devolver un producto?\n"
                    "- ¿Cuánto cuesta el envío estándar a una zona urbana?\n"
                    "- ¿Qué hago si recibo un producto dañado?\n"
                    "- ¿Comparten mis datos personales con terceros?"
                ),
            }
        ]

    # --- Renderizado del historial ----------------------------------------
    for mensaje in st.session_state.historial_chat:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    # --- Entrada de chat -----------------------------------------------------
    pregunta_usuario = st.chat_input("Escribe tu pregunta sobre las políticas de Globex Corp...")

    if pregunta_usuario:
        st.session_state.historial_chat.append(
            {"rol": "user", "contenido": pregunta_usuario}
        )
        with st.chat_message("user"):
            st.markdown(pregunta_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Consultando el manual de políticas..."):
                try:
                    resultado = cadena_rag.invoke({"question": pregunta_usuario})
                    respuesta = resultado["answer"]

                    fuentes = resultado.get("source_documents", [])
                    paginas = sorted(
                        {doc.metadata.get("page", "?") + 1 for doc in fuentes}
                    ) if fuentes else []

                    if paginas:
                        respuesta += (
                            f"\n\n*📎 Fuente: páginas {', '.join(map(str, paginas))} "
                            "del Manual de Políticas.*"
                        )

                except Exception as error:
                    respuesta = (
                        "⚠️ Ocurrió un error al generar la respuesta. "
                        f"Detalle: {error}"
                    )

            st.markdown(respuesta)

        st.session_state.historial_chat.append(
            {"rol": "assistant", "contenido": respuesta}
        )


if __name__ == "__main__":
    main()
