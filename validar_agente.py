"""
validar_agente.py
---------------------------------------------------------------------
Batería de pruebas automáticas para validar el funcionamiento del
agente RAG de Globex Corp. Valida:

  1. Cobertura: que cada documento sea usado como fuente al menos una vez.
  2. Fidelidad: que la respuesta contenga las palabras clave esperadas
     (datos reales extraídos de los PDF).
  3. Rechazo correcto: que ante preguntas fuera de alcance, el agente
     admita que no tiene la información (en vez de inventar una respuesta).

No reemplaza la revisión manual, pero detecta rápidamente regresiones
cada vez que cambies el prompt, el chunk_size, o los documentos fuente.

Uso:
    python validar_agente.py
---------------------------------------------------------------------
"""

import os
import sys
import glob

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

load_dotenv()

# =====================================================================
# 1. Casos de prueba
#    - pregunta: lo que se le pregunta al agente
#    - palabras_clave: al menos UNA debe aparecer en la respuesta (para
#      validar fidelidad frente al contenido real del documento)
#    - documento_esperado: substring del nombre de archivo que debería
#      aparecer entre las fuentes citadas (valida cobertura/retrieval)
#    - debe_rechazar: True si se espera que el agente admita que no sabe
# =====================================================================
CASOS_DE_PRUEBA = [
    {
        "categoria": "RH - Vacaciones",
        "pregunta": "¿Cuántos días de vacaciones corresponden con 6 años de antigüedad?",
        "palabras_clave": ["20", "veinte"],
        "documento_esperado": "Manual_Politicas",
    },
    {
        "categoria": "RH - Viáticos",
        "pregunta": "¿Cuál es el tope diario de alimentación en un viaje internacional?",
        "palabras_clave": ["60"],
        "documento_esperado": "Manual_Politicas",
    },
    {
        "categoria": "RH - Trabajo remoto",
        "pregunta": "¿Qué apoyo de internet da la empresa a quienes trabajan remoto?",
        "palabras_clave": ["25"],
        "documento_esperado": "Manual_Politicas",
    },
    {
        "categoria": "RH - Ética",
        "pregunta": "¿Cómo se llama el canal de denuncias internas de la empresa?",
        "palabras_clave": ["línea ética", "linea etica", "línea ética globex"],
        "documento_esperado": "Manual_Politicas",
    },
    {
        "categoria": "E-commerce - Devoluciones",
        "pregunta": "¿Cuántos días tengo para devolver un producto?",
        "palabras_clave": ["30"],
        "documento_esperado": "Reembolsos",
    },
    {
        "categoria": "E-commerce - Envíos",
        "pregunta": "¿Cuánto cuesta el envío estándar en zona urbana?",
        "palabras_clave": ["4.99", "4,99"],
        "documento_esperado": "Envios",
    },
    {
        "categoria": "E-commerce - Privacidad",
        "pregunta": "¿Comparten mis datos personales con empresas de publicidad externas?",
        "palabras_clave": ["no", "nunca"],
        "documento_esperado": "Privacidad",
    },
    {
        "categoria": "E-commerce - FAQ",
        "pregunta": "¿Tienen tienda física?",
        "palabras_clave": ["no", "online", "exclusivamente"],
        "documento_esperado": "FAQ",
    },
    {
        "categoria": "E-commerce - Términos",
        "pregunta": "¿Quién es responsable de mantener mi contraseña en secreto?",
        "palabras_clave": ["usuario", "responsable", "confidencialidad"],
        "documento_esperado": "Terminos",
    },
    {
        "categoria": "RECHAZO - Fuera de alcance",
        "pregunta": "¿Cuál es la capital de Australia?",
        "palabras_clave": ["no cuento", "no tengo esa información", "no cuenta con esa información", "no dispongo"],
        "documento_esperado": None,
        "debe_rechazar": True,
    },
    {
        "categoria": "RECHAZO - Política inventada",
        "pregunta": "¿Cuál es la política de home office de la empresa TechCorp?",
        "palabras_clave": ["no cuento", "no tengo esa información", "no cuenta con esa información", "no dispongo"],
        "documento_esperado": None,
        "debe_rechazar": True,
    },
]


def construir_cadena():
    """Reconstruye el pipeline RAG completo (idéntico a app.py)."""
    rutas_pdf = glob.glob(os.path.join("documentos", "*.pdf"))
    if not rutas_pdf:
        print("❌ No se encontraron PDFs en 'documentos/'. Corre primero los")
        print("   scripts generar_pdf_dummy.py y generar_documentos_ecommerce.py")
        sys.exit(1)

    if not os.getenv("GROQ_API_KEY"):
        print("❌ No se encontró GROQ_API_KEY. Configúrala en tu archivo .env")
        sys.exit(1)

    documentos = []
    for ruta in rutas_pdf:
        documentos.extend(PyPDFLoader(ruta).load())

    splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=300)
    fragmentos = splitter.split_documents(documentos)

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectorstore = FAISS.from_documents(fragmentos, embeddings)

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.2)

    prompt_qa = PromptTemplate(
        input_variables=["context", "question"],
        template=(
            "Eres el asistente virtual de Globex Corp. Responde SIEMPRE en "
            "español, de forma clara y concisa, basándote únicamente en el "
            "siguiente contexto. Si la respuesta no está en el contexto, di "
            "explícitamente que no cuentas con esa información.\n\n"
            "Contexto:\n{context}\n\nPregunta: {question}\nRespuesta:"
        ),
    )

    memoria = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True, output_key="answer"
    )

    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        memory=memoria,
        return_source_documents=True,
        combine_docs_chain_kwargs={"prompt": prompt_qa},
    )


def evaluar_caso(cadena, caso):
    """Ejecuta un caso de prueba y valida fidelidad + cobertura de fuentes."""
    resultado = cadena.invoke({"question": caso["pregunta"]})
    respuesta = resultado["answer"]
    respuesta_normalizada = respuesta.lower()

    fuentes = [
        os.path.basename(doc.metadata.get("source", ""))
        for doc in resultado.get("source_documents", [])
    ]

    contiene_palabra_clave = any(
        palabra.lower() in respuesta_normalizada for palabra in caso["palabras_clave"]
    )

    if caso.get("documento_esperado"):
        documento_correcto = any(
            caso["documento_esperado"].lower() in f.lower() for f in fuentes
        )
    else:
        documento_correcto = True  # No aplica para casos de rechazo

    aprobado = contiene_palabra_clave and documento_correcto

    return {
        "categoria": caso["categoria"],
        "pregunta": caso["pregunta"],
        "respuesta": respuesta,
        "fuentes": fuentes,
        "aprobado": aprobado,
    }


def main():
    print("🔧 Construyendo el pipeline RAG (esto puede tardar un momento)...\n")
    cadena = construir_cadena()

    resultados = []
    for i, caso in enumerate(CASOS_DE_PRUEBA, start=1):
        print(f"[{i}/{len(CASOS_DE_PRUEBA)}] {caso['categoria']}: {caso['pregunta']}")
        resultado = evaluar_caso(cadena, caso)
        resultados.append(resultado)

        estado = "✅ PASÓ" if resultado["aprobado"] else "❌ FALLÓ"
        print(f"    {estado}")
        print(f"    Respuesta: {resultado['respuesta'][:150]}...")
        print(f"    Fuentes:   {resultado['fuentes']}\n")

    # --- Resumen final -----------------------------------------------------
    total = len(resultados)
    aprobados = sum(1 for r in resultados if r["aprobado"])

    print("=" * 70)
    print(f"RESUMEN: {aprobados}/{total} casos aprobados ({aprobados/total*100:.0f}%)")
    print("=" * 70)

    if aprobados < total:
        print("\nCasos que fallaron:")
        for r in resultados:
            if not r["aprobado"]:
                print(f"  - [{r['categoria']}] {r['pregunta']}")

    sys.exit(0 if aprobados == total else 1)


if __name__ == "__main__":
    main()
