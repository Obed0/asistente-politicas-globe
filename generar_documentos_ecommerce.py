"""
generar_documentos_ecommerce.py
---------------------------------------------------------------------
Genera 5 documentos PDF independientes para la base de conocimiento
de "Globex Corp", reposicionada como tienda online / e-commerce:

  1. Politica_Privacidad_GlobexCorp.pdf
  2. Politica_Reembolsos_Devoluciones_GlobexCorp.pdf
  3. FAQ_GlobexCorp.pdf
  4. Guia_Envios_Entregas_GlobexCorp.pdf
  5. Terminos_Condiciones_GlobexCorp.pdf

Estos documentos se suman al Manual_Politicas_GlobexCorp.pdf (RH) ya
existente en la carpeta 'documentos/'. El agente RAG (app.py) carga
TODOS los PDF de esa carpeta automáticamente, por lo que no requiere
ningún cambio de código: solo ejecutar este script y volver a correr
la app (o borrar 'indice_faiss/' para forzar la reindexación).

Uso: python generar_documentos_ecommerce.py
---------------------------------------------------------------------
"""

import os
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    ListFlowable,
    ListItem,
    Table,
    TableStyle,
)

CARPETA_SALIDA = "documentos"
os.makedirs(CARPETA_SALIDA, exist_ok=True)

# ---------------------------------------------------------------------
# Estilos compartidos por todos los documentos
# ---------------------------------------------------------------------
estilos = getSampleStyleSheet()

ESTILO_TITULO_PORTADA = ParagraphStyle(
    "TituloPortada", parent=estilos["Title"], fontSize=24,
    alignment=TA_CENTER, spaceAfter=16, textColor=colors.HexColor("#0B3D91"),
)
ESTILO_SUBTITULO_PORTADA = ParagraphStyle(
    "SubtituloPortada", parent=estilos["Normal"], fontSize=13,
    alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=8,
)
ESTILO_SECCION = ParagraphStyle(
    "Seccion", parent=estilos["Heading1"], fontSize=16,
    textColor=colors.HexColor("#0B3D91"), spaceBefore=16, spaceAfter=8,
)
ESTILO_SUBSECCION = ParagraphStyle(
    "Subseccion", parent=estilos["Heading2"], fontSize=12.5,
    textColor=colors.HexColor("#1F4E8C"), spaceBefore=8, spaceAfter=6,
)
ESTILO_CUERPO = ParagraphStyle(
    "Cuerpo", parent=estilos["Normal"], fontSize=10.5, leading=15,
    alignment=TA_JUSTIFY, spaceAfter=8,
)
ESTILO_ITEM = ParagraphStyle("Item", parent=ESTILO_CUERPO, leftIndent=12)


def portada(titulo, subtitulo):
    """Genera el bloque de portada reutilizable para cada documento."""
    return [
        Spacer(1, 1.3 * inch),
        Paragraph("GLOBEX CORP", ESTILO_TITULO_PORTADA),
        Paragraph(titulo, ESTILO_SUBTITULO_PORTADA),
        Paragraph(subtitulo, ESTILO_SUBTITULO_PORTADA),
        Spacer(1, 0.3 * inch),
        Paragraph("Tienda Online — Documento de cara al cliente", ESTILO_CUERPO),
        PageBreak(),
    ]


def tabla_estandar(datos, col_widths):
    tabla = Table(datos, colWidths=col_widths)
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tabla


def lista_bullet(items, estilo=ESTILO_ITEM):
    return ListFlowable(
        [ListItem(Paragraph(i, estilo)) for i in items], bulletType="bullet"
    )


def generar_documento(nombre_archivo, contenido):
    ruta = os.path.join(CARPETA_SALIDA, nombre_archivo)
    doc = SimpleDocTemplate(
        ruta, pagesize=LETTER,
        topMargin=0.9 * inch, bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        title=nombre_archivo, author="Globex Corp",
    )
    doc.build(contenido)
    print(f"✅ Generado: {ruta}")


# =====================================================================
# 1. POLÍTICA DE PRIVACIDAD
# =====================================================================
def generar_politica_privacidad():
    c = portada(
        "Política de Privacidad",
        "Protección y tratamiento de datos personales de clientes",
    )

    c.append(Paragraph("1. Datos que recopilamos", ESTILO_SECCION))
    c.append(Paragraph(
        "Al comprar en GlobexCorp.com recopilamos: nombre completo, correo "
        "electrónico, número de teléfono, dirección de envío y facturación, "
        "historial de pedidos, y datos de pago procesados de forma segura por "
        "nuestra pasarela de pagos certificada PCI-DSS (no almacenamos números "
        "completos de tarjeta en nuestros propios servidores).",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("2. Finalidad del tratamiento", ESTILO_SECCION))
    c.append(lista_bullet([
        "Procesar y dar seguimiento a tus pedidos y envíos.",
        "Enviar notificaciones transaccionales (confirmación de compra, estado de envío).",
        "Enviar comunicaciones de marketing, solo si aceptaste recibirlas explícitamente.",
        "Prevenir fraude y cumplir obligaciones legales y fiscales.",
        "Mejorar la experiencia de compra mediante análisis agregado y anónimo de navegación.",
    ]))

    c.append(Paragraph("3. Conservación de los datos", ESTILO_SECCION))
    c.append(Paragraph(
        "Conservamos los datos de tu cuenta mientras esta permanezca activa. "
        "Los datos asociados a facturación se conservan por 5 años, conforme a "
        "obligaciones contables y fiscales. Puedes solicitar la eliminación de "
        "tu cuenta en cualquier momento desde \"Mi Cuenta > Privacidad\", sin "
        "perjuicio de la información que debamos conservar por ley.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("4. Derechos del titular (ARCO)", ESTILO_SECCION))
    c.append(Paragraph(
        "Como cliente, tienes derecho a Acceder, Rectificar, Cancelar y Oponerte "
        "(derechos ARCO) al tratamiento de tus datos personales. Puedes ejercer "
        "estos derechos escribiendo a privacidad@globexcorp.com, adjuntando una "
        "identificación oficial. Responderemos en un plazo máximo de 15 días hábiles.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("5. Comparticion con terceros", ESTILO_SECCION))
    c.append(Paragraph(
        "Compartimos datos estrictamente necesarios con: empresas de mensajería "
        "(nombre, dirección y teléfono, para la entrega), la pasarela de pagos "
        "(para procesar el cobro) y proveedores de email marketing (solo correo, "
        "y solo si diste tu consentimiento). Nunca vendemos tus datos personales "
        "a terceros con fines publicitarios ajenos a Globex Corp.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("6. Cookies", ESTILO_SECCION))
    c.append(Paragraph(
        "Utilizamos cookies propias y de terceros para recordar tu carrito de "
        "compras, mantener tu sesión iniciada y medir el rendimiento del sitio. "
        "Puedes gestionar tus preferencias de cookies desde el banner de "
        "consentimiento que aparece en tu primera visita.",
        ESTILO_CUERPO,
    ))

    generar_documento("Politica_Privacidad_GlobexCorp.pdf", c)


# =====================================================================
# 2. POLÍTICA DE REEMBOLSOS Y DEVOLUCIONES
# =====================================================================
def generar_politica_reembolsos():
    c = portada(
        "Política de Reembolsos y Devoluciones",
        "Condiciones para devolver un producto y solicitar tu reembolso",
    )

    c.append(Paragraph("1. Plazo para devoluciones", ESTILO_SECCION))
    c.append(Paragraph(
        "Cuentas con 30 días calendario, contados desde la fecha de entrega, "
        "para solicitar la devolución de un producto sin necesidad de justificar "
        "el motivo (derecho de retracto). Productos defectuosos o dañados en "
        "tránsito pueden reportarse hasta 60 días después de la entrega.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("2. Condiciones del producto a devolver", ESTILO_SECCION))
    c.append(lista_bullet([
        "El producto debe estar en su empaque original, sin señales de uso.",
        "Debe incluir todos los accesorios, manuales y regalos promocionales recibidos.",
        "Productos de higiene personal, ropa interior y alimentos no son elegibles para devolución, salvo defecto de fábrica.",
        "Productos electrónicos deben conservar los sellos de garantía intactos.",
    ]))

    c.append(Paragraph("3. Tiempos de reembolso según método de pago", ESTILO_SUBSECCION))
    tabla = tabla_estandar(
        [
            ["Método de pago", "Tiempo estimado de reembolso"],
            ["Tarjeta de crédito", "5 a 10 días hábiles"],
            ["Tarjeta de débito", "3 a 7 días hábiles"],
            ["Billetera digital (ej. PayPal)", "1 a 3 días hábiles"],
            ["Transferencia bancaria", "3 a 5 días hábiles"],
        ],
        [2.8 * inch, 2.8 * inch],
    )
    c.append(tabla)
    c.append(Spacer(1, 10))

    c.append(Paragraph("4. Costos de devolución", ESTILO_SECCION))
    c.append(Paragraph(
        "Si la devolución se debe a un error de Globex Corp (producto "
        "equivocado, defectuoso o dañado), la etiqueta de envío de devolución "
        "es gratuita. Si la devolución es por cambio de opinión del cliente, "
        "se descuenta del reembolso un costo fijo de envío de retorno de USD 5.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("5. Cómo iniciar una devolución", ESTILO_SECCION))
    c.append(Paragraph(
        "Ingresa a \"Mi Cuenta > Mis Pedidos\", selecciona el pedido y haz clic "
        "en \"Solicitar devolución\". Recibirás una etiqueta de envío prepagada "
        "(cuando aplique) por correo electrónico dentro de las 24 horas. Una vez "
        "que el producto sea recibido e inspeccionado en nuestro centro de "
        "devoluciones, procesaremos el reembolso según los tiempos indicados arriba.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("6. Cambios de producto", ESTILO_SECCION))
    c.append(Paragraph(
        "En lugar de un reembolso, puedes solicitar el cambio por otra talla, "
        "color o modelo de igual o menor valor, sujeto a disponibilidad de "
        "inventario. Si el nuevo producto tiene mayor valor, deberás pagar la "
        "diferencia.",
        ESTILO_CUERPO,
    ))

    generar_documento("Politica_Reembolsos_Devoluciones_GlobexCorp.pdf", c)


# =====================================================================
# 3. PREGUNTAS FRECUENTES (FAQ)
# =====================================================================
def generar_faq():
    c = portada(
        "Preguntas Frecuentes (FAQ)",
        "Respuestas rápidas sobre compras, pagos, cuenta y más",
    )

    preguntas = [
        ("¿Qué métodos de pago aceptan?",
         "Aceptamos tarjetas de crédito y débito Visa, Mastercard y American "
         "Express, PayPal, y transferencia bancaria (SPEI en México). No "
         "aceptamos pagos contra entrega en efectivo."),
        ("¿Puedo cambiar la dirección de envío después de comprar?",
         "Sí, siempre que el pedido no haya sido despachado. Ve a "
         "\"Mi Cuenta > Mis Pedidos\" y haz clic en \"Editar dirección\" dentro "
         "de la primera hora tras la compra. Pasado ese tiempo, contacta a "
         "soporte@globexcorp.com lo antes posible."),
        ("¿Tienen tienda física?",
         "No, Globex Corp opera exclusivamente como tienda online (e-commerce), "
         "sin puntos de venta físicos."),
        ("¿Cómo creo una cuenta?",
         "Haz clic en \"Registrarme\" en la esquina superior derecha del sitio, "
         "ingresa tu correo electrónico y crea una contraseña. También puedes "
         "registrarte usando tu cuenta de Google."),
        ("¿Puedo comprar sin crear una cuenta?",
         "Sí, ofrecemos la opción de \"Compra como invitado\", aunque recomendamos "
         "crear una cuenta para dar seguimiento más fácil a tus pedidos."),
        ("¿Los precios incluyen impuestos?",
         "Sí, todos los precios mostrados en el sitio ya incluyen los impuestos "
         "aplicables (IVA) para envíos dentro del país de origen de la tienda."),
        ("¿Qué hago si recibí un producto dañado?",
         "Repórtalo dentro de las 48 horas siguientes a la entrega desde "
         "\"Mi Cuenta > Mis Pedidos > Reportar problema\", adjuntando fotos del "
         "producto y el empaque. Se procesará reemplazo o reembolso sin costo."),
        ("¿Puedo cancelar un pedido ya realizado?",
         "Puedes cancelar sin costo mientras el pedido tenga estado "
         "\"En preparación\". Una vez que cambia a \"Enviado\", deberás esperar "
         "la entrega y luego solicitar una devolución."),
        ("¿Cómo contacto a servicio al cliente?",
         "Por chat en vivo (disponible de 8:00 a 20:00 hora local), correo "
         "electrónico a soporte@globexcorp.com, o línea telefónica gratuita "
         "1-800-GLOBEX-1."),
    ]

    for pregunta, respuesta in preguntas:
        c.append(Paragraph(f"P: {pregunta}", ESTILO_SUBSECCION))
        c.append(Paragraph(f"R: {respuesta}", ESTILO_CUERPO))

    generar_documento("FAQ_GlobexCorp.pdf", c)


# =====================================================================
# 4. GUÍA DE ENVÍOS Y ENTREGAS
# =====================================================================
def generar_guia_envios():
    c = portada(
        "Guía de Envíos y Entregas",
        "Tiempos, costos y cobertura de nuestros envíos",
    )

    c.append(Paragraph("1. Tiempos de entrega estimados", ESTILO_SECCION))
    tabla = tabla_estandar(
        [
            ["Tipo de envío", "Tiempo estimado", "Costo"],
            ["Estándar (zona urbana)", "3 a 5 días hábiles", "USD 4.99"],
            ["Estándar (zona rural/foránea)", "5 a 8 días hábiles", "USD 7.99"],
            ["Express (zona urbana)", "1 a 2 días hábiles", "USD 12.99"],
            ["Envío gratis", "3 a 5 días hábiles", "Gratis en compras mayores a USD 60"],
        ],
        [2.1 * inch, 2.1 * inch, 1.8 * inch],
    )
    c.append(tabla)
    c.append(Spacer(1, 10))

    c.append(Paragraph("2. Cobertura geográfica", ESTILO_SECCION))
    c.append(Paragraph(
        "Actualmente realizamos envíos a todo el territorio nacional, "
        "incluyendo zonas rurales, con posibles días adicionales para "
        "localidades de difícil acceso. Los envíos internacionales están "
        "disponibles solo para México, Colombia, Chile, Perú y Argentina, con "
        "tiempos de 8 a 15 días hábiles.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("3. Rastreo de pedidos", ESTILO_SECCION))
    c.append(Paragraph(
        "Una vez despachado tu pedido, recibirás un correo electrónico con el "
        "número de guía y un enlace de rastreo en tiempo real. También puedes "
        "consultar el estado desde \"Mi Cuenta > Mis Pedidos > Rastrear envío\".",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("4. Empaque y sustentabilidad", ESTILO_SECCION))
    c.append(Paragraph(
        "Utilizamos empaques de cartón reciclado y cinta biodegradable siempre "
        "que el producto lo permite. Para productos frágiles, se añade material "
        "de protección adicional certificado.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("5. Pedidos perdidos o retrasados", ESTILO_SECCION))
    c.append(Paragraph(
        "Si tu pedido no ha llegado dentro del plazo estimado más 3 días "
        "hábiles de margen, contáctanos para abrir una investigación con la "
        "paquetería. Si se confirma la pérdida del paquete, se reenvía el "
        "producto sin costo adicional o se reembolsa el importe completo, "
        "según tu preferencia.",
        ESTILO_CUERPO,
    ))

    generar_documento("Guia_Envios_Entregas_GlobexCorp.pdf", c)


# =====================================================================
# 5. TÉRMINOS Y CONDICIONES
# =====================================================================
def generar_terminos_condiciones():
    c = portada(
        "Términos y Condiciones de Uso",
        "Condiciones generales de compra en GlobexCorp.com",
    )

    c.append(Paragraph("1. Aceptación de los términos", ESTILO_SECCION))
    c.append(Paragraph(
        "Al crear una cuenta o realizar una compra en GlobexCorp.com, aceptas "
        "íntegramente los presentes Términos y Condiciones, así como nuestra "
        "Política de Privacidad. Si no estás de acuerdo, te pedimos abstenerte "
        "de usar el sitio.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("2. Disponibilidad de productos y precios", ESTILO_SECCION))
    c.append(Paragraph(
        "Los precios y la disponibilidad de los productos pueden cambiar sin "
        "previo aviso hasta el momento de la confirmación del pago. En caso de "
        "un error evidente de precio (por ejemplo, un cero de menos), Globex "
        "Corp se reserva el derecho de cancelar el pedido y reembolsar el "
        "importe pagado en su totalidad.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("3. Cuenta de usuario", ESTILO_SECCION))
    c.append(Paragraph(
        "Eres responsable de mantener la confidencialidad de tu contraseña y de "
        "toda actividad realizada bajo tu cuenta. Debes notificarnos de "
        "inmediato ante cualquier uso no autorizado a soporte@globexcorp.com.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("4. Propiedad intelectual", ESTILO_SECCION))
    c.append(Paragraph(
        "Todo el contenido del sitio (textos, imágenes, logotipos, diseño) es "
        "propiedad de Globex Corp o de sus licenciantes, y está protegido por "
        "leyes de propiedad intelectual. Queda prohibida su reproducción total "
        "o parcial sin autorización previa por escrito.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("5. Limitación de responsabilidad", ESTILO_SECCION))
    c.append(Paragraph(
        "Globex Corp no será responsable por retrasos o incumplimientos "
        "derivados de causas de fuerza mayor (desastres naturales, huelgas, "
        "fallas de proveedores logísticos externos, entre otros) ajenas a su "
        "control razonable.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("6. Resolución de disputas", ESTILO_SECCION))
    c.append(Paragraph(
        "Cualquier controversia derivada del uso del sitio o de una compra se "
        "intentará resolver primero mediante contacto directo con nuestro "
        "equipo de atención al cliente. De no llegar a un acuerdo, la disputa "
        "se someterá a los tribunales competentes de la jurisdicción donde "
        "Globex Corp tiene su domicilio fiscal.",
        ESTILO_CUERPO,
    ))

    c.append(Paragraph("7. Modificaciones", ESTILO_SECCION))
    c.append(Paragraph(
        "Globex Corp puede actualizar estos Términos y Condiciones en cualquier "
        "momento. La versión vigente siempre estará publicada en el sitio web, "
        "con la fecha de última actualización indicada al pie del documento.",
        ESTILO_CUERPO,
    ))

    generar_documento("Terminos_Condiciones_GlobexCorp.pdf", c)


# =====================================================================
# Ejecución principal: genera los 5 documentos
# =====================================================================
if __name__ == "__main__":
    generar_politica_privacidad()
    generar_politica_reembolsos()
    generar_faq()
    generar_guia_envios()
    generar_terminos_condiciones()
    print("\n🎉 Los 5 documentos de e-commerce se generaron en la carpeta 'documentos/'.")
