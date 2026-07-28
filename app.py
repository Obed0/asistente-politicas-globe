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

import os, glob, warnings
warnings.filterwarnings("ignore")

import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

st.set_page_config(page_title="Asistente · Globex Corp", page_icon="🤖", layout="centered")

CARPETA_DOCUMENTOS   = "documentos"
CARPETA_INDICE_FAISS = "indice_faiss"
MODELO_EMBEDDINGS    = "sentence-transformers/all-MiniLM-L6-v2"
MODELO_LLM           = "llama-3.1-8b-instant"
CHUNK_SIZE, CHUNK_OVERLAP = 1200, 300

def obtener_groq_api_key():
    with st.sidebar:
        st.header("Configuracion")
        st.markdown("**Globex Corp** - Asistente")
        st.divider()
        api_key = st.text_input("GROQ_API_KEY", value=os.getenv("GROQ_API_KEY",""), type="password")
        st.success("API Key configurada") if api_key else st.warning("Ingresa tu GROQ_API_KEY")
        st.divider()
        if st.button("Reiniciar conversacion"):
            st.session_state.pop("historial_chat", None)
            st.session_state.pop("historial_mensajes", None)
            st.rerun()
    return api_key

@st.cache_resource(show_spinner="Indexando documentos...")
def construir_vectorstore():
    rutas_pdf = glob.glob(os.path.join(CARPETA_DOCUMENTOS, "*.pdf"))
    if not rutas_pdf:
        return None, 0
    embeddings = HuggingFaceEmbeddings(model_name=MODELO_EMBEDDINGS)
    if os.path.isdir(CARPETA_INDICE_FAISS):
        return FAISS.load_local(CARPETA_INDICE_FAISS, embeddings, allow_dangerous_deserialization=True), -1
    docs = []
    for r in rutas_pdf:
        docs.extend(PyPDFLoader(r).load())
    chunks = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP).split_documents(docs)
    vs = FAISS.from_documents(chunks, embeddings)
    vs.save_local(CARPETA_INDICE_FAISS)
    return vs, len(chunks)

def construir_chain(retriever, api_key):
    llm = ChatGroq(api_key=api_key, model=MODELO_LLM, temperature=0.2)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Eres el asistente virtual de Globex Corp, una tienda online. "
         "Respondes preguntas de RH y de clientes sobre la tienda. "
         "Responde SIEMPRE en espanol basandote unicamente en el contexto. "
         "Si no esta en el contexto, dilo explicitamente.\n\nContexto:\n{context}"),
        MessagesPlaceholder(variable_name="historial"),
        ("human", "{question}"),
    ])
    return prompt | llm | StrOutputParser()

def main():
    st.title("Asistente de Globex Corp")
    st.caption("Politicas internas y atencion al cliente - agente RAG")
    groq_api_key = obtener_groq_api_key()

    if not glob.glob(os.path.join(CARPETA_DOCUMENTOS, "*.pdf")):
        st.error("No hay PDFs en documentos/")
        st.stop()
    if not groq_api_key:
        st.info("Ingresa tu GROQ_API_KEY en la barra lateral.")
        st.stop()

    try:
        vectorstore, total_chunks = construir_vectorstore()
    except Exception as e:
        st.error(f"Error al procesar documentos: {e}")
        st.stop()

    if vectorstore is None:
        st.error("No se pudo construir el indice vectorial.")
        st.stop()

    n_pdfs = len(glob.glob(os.path.join(CARPETA_DOCUMENTOS, "*.pdf")))
    st.caption(f"{total_chunks if total_chunks > 0 else 'indice cargado'} | {n_pdfs} documentos.")

    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    chain     = construir_chain(retriever, groq_api_key)

    if "historial_chat" not in st.session_state:
        st.session_state.historial_chat     = []
        st.session_state.historial_mensajes = []
        st.session_state.historial_chat.append({"rol": "assistant", "contenido":
            "Hola! Soy el asistente de Globex Corp. Por ejemplo:\n\n"
            "- Cuantos dias de vacaciones me corresponden con 6 anos?\n"
            "- Cuantos dias tengo para devolver un producto?\n"
            "- Cuanto cuesta el envio estandar?\n"
            "- Comparten mis datos personales con terceros?"
        })

    for msg in st.session_state.historial_chat:
        with st.chat_message(msg["rol"]):
            st.markdown(msg["contenido"])

    pregunta = st.chat_input("Escribe tu pregunta sobre Globex Corp...")

    if pregunta:
        st.session_state.historial_chat.append({"rol": "user", "contenido": pregunta})
        with st.chat_message("user"):
            st.markdown(pregunta)
        with st.chat_message("assistant"):
            with st.spinner("Consultando documentos..."):
                try:
                    docs_relevantes = retriever.invoke(pregunta)
                    contexto  = "\n\n".join(d.page_content for d in docs_relevantes)
                    respuesta = chain.invoke({
                        "context":   contexto,
                        "historial": st.session_state.historial_mensajes,
                        "question":  pregunta,
                    })
                    st.session_state.historial_mensajes.append(HumanMessage(content=pregunta))
                    st.session_state.historial_mensajes.append(AIMessage(content=respuesta))
                    fuentes = sorted({os.path.basename(d.metadata.get("source","")) for d in docs_relevantes})
                    if fuentes:
                        respuesta += f"\n\nFuentes: {', '.join(fuentes)}"
                except Exception as e:
                    respuesta = f"Error: {e}"
            st.markdown(respuesta)
        st.session_state.historial_chat.append({"rol": "assistant", "contenido": respuesta})

if __name__ == "__main__":
    main()
