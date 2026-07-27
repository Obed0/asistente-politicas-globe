"""
generar_pdf_dummy.py
---------------------------------------------------------------------
Genera el documento "Manual_Politicas_GlobexCorp.pdf": un manual
corporativo ficticio en español que servirá como base de conocimiento
para el agente RAG (Retrieval Augmented Generation).

Empresa ficticia: Globex Corp
Uso: python generar_pdf_dummy.py
Salida: documentos/Manual_Politicas_GlobexCorp.pdf
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

# ---------------------------------------------------------------------
# 1. Configuración de rutas
# ---------------------------------------------------------------------
CARPETA_SALIDA = "documentos"
NOMBRE_ARCHIVO = "Manual_Politicas_GlobexCorp.pdf"
RUTA_SALIDA = os.path.join(CARPETA_SALIDA, NOMBRE_ARCHIVO)

os.makedirs(CARPETA_SALIDA, exist_ok=True)

# ---------------------------------------------------------------------
# 2. Estilos del documento
# ---------------------------------------------------------------------
estilos = getSampleStyleSheet()

estilo_titulo_portada = ParagraphStyle(
    "TituloPortada",
    parent=estilos["Title"],
    fontSize=26,
    alignment=TA_CENTER,
    spaceAfter=20,
    textColor=colors.HexColor("#0B3D91"),
)

estilo_subtitulo_portada = ParagraphStyle(
    "SubtituloPortada",
    parent=estilos["Normal"],
    fontSize=14,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#555555"),
    spaceAfter=10,
)

estilo_seccion = ParagraphStyle(
    "Seccion",
    parent=estilos["Heading1"],
    fontSize=17,
    textColor=colors.HexColor("#0B3D91"),
    spaceBefore=18,
    spaceAfter=10,
)

estilo_subseccion = ParagraphStyle(
    "Subseccion",
    parent=estilos["Heading2"],
    fontSize=13,
    textColor=colors.HexColor("#1F4E8C"),
    spaceBefore=10,
    spaceAfter=6,
)

estilo_cuerpo = ParagraphStyle(
    "Cuerpo",
    parent=estilos["Normal"],
    fontSize=10.5,
    leading=15,
    alignment=TA_JUSTIFY,
    spaceAfter=8,
)

estilo_item = ParagraphStyle(
    "Item",
    parent=estilo_cuerpo,
    leftIndent=12,
)

# ---------------------------------------------------------------------
# 3. Contenido del documento
# ---------------------------------------------------------------------
contenido = []

# --- Portada -----------------------------------------------------------
contenido.append(Spacer(1, 1.5 * inch))
contenido.append(Paragraph("GLOBEX CORP", estilo_titulo_portada))
contenido.append(Paragraph("Manual de Políticas Internas", estilo_subtitulo_portada))
contenido.append(Paragraph("Recursos Humanos · Administración · Ética Corporativa", estilo_subtitulo_portada))
contenido.append(Spacer(1, 0.4 * inch))
contenido.append(Paragraph("Versión 1.0 — Documento de uso interno y confidencial", estilo_cuerpo))
contenido.append(PageBreak())

# --- Índice simple -------------------------------------------------------
contenido.append(Paragraph("Índice de Contenidos", estilo_seccion))
indice_items = [
    "1. Política de Vacaciones y Licencias",
    "2. Viáticos, Reembolsos y Gastos de Representación",
    "3. Modalidad de Trabajo Remoto / Home Office",
    "4. Código de Ética y Canal de Denuncias Internas",
]
contenido.append(
    ListFlowable(
        [ListItem(Paragraph(i, estilo_cuerpo)) for i in indice_items],
        bulletType="bullet",
    )
)
contenido.append(PageBreak())

# =====================================================================
# SECCIÓN 1 — Vacaciones y Licencias
# =====================================================================
contenido.append(Paragraph("1. Política de Vacaciones y Licencias", estilo_seccion))

contenido.append(Paragraph("1.1 Días de vacaciones según antigüedad", estilo_subseccion))
contenido.append(Paragraph(
    "Globex Corp otorga a todo el personal contratado bajo planilla, tiempo completo, "
    "un número de días de vacaciones pagadas que aumenta de acuerdo con la antigüedad "
    "del colaborador en la empresa, conforme a la siguiente tabla:",
    estilo_cuerpo,
))

tabla_vacaciones = Table(
    [
        ["Antigüedad", "Días hábiles de vacaciones al año"],
        ["Menos de 1 año", "12 días (proporcional a meses trabajados)"],
        ["De 1 a 4 años", "15 días"],
        ["De 5 a 9 años", "20 días"],
        ["De 10 a 14 años", "25 días"],
        ["15 años o más", "30 días"],
    ],
    colWidths=[2.6 * inch, 3.0 * inch],
)
tabla_vacaciones.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9.5),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
contenido.append(tabla_vacaciones)
contenido.append(Spacer(1, 10))

contenido.append(Paragraph("1.2 Proceso de solicitud", estilo_subseccion))
contenido.append(Paragraph(
    "Las solicitudes de vacaciones deben registrarse en el portal interno "
    "\"Globex People\" con un mínimo de 15 días calendario de anticipación. "
    "El jefe directo cuenta con un plazo máximo de 3 días hábiles para aprobar "
    "o rechazar la solicitud, justificando el motivo en caso de rechazo. "
    "No se permite acumular más de 10 días de vacaciones de un período a otro; "
    "el excedente debe ser gozado antes del 31 de marzo del año siguiente o se "
    "pierde el derecho al exceso, salvo autorización expresa de Recursos Humanos.",
    estilo_cuerpo,
))

contenido.append(Paragraph("1.3 Licencias especiales", estilo_subseccion))
contenido.append(Paragraph(
    "Además de las vacaciones, Globex Corp reconoce las siguientes licencias remuneradas:",
    estilo_cuerpo,
))
licencias = [
    "Licencia por maternidad: 98 días calendario, ampliables según normativa local.",
    "Licencia por paternidad: 10 días hábiles a partir del nacimiento o adopción.",
    "Licencia por matrimonio: 3 días hábiles consecutivos.",
    "Licencia por duelo (familiar directo): 5 días hábiles.",
    "Licencia por mudanza: 1 día hábil cada 2 años, sujeto a aprobación.",
]
contenido.append(
    ListFlowable(
        [ListItem(Paragraph(l, estilo_item)) for l in licencias],
        bulletType="bullet",
    )
)
contenido.append(PageBreak())

# =====================================================================
# SECCIÓN 2 — Viáticos, Reembolsos y Gastos de Representación
# =====================================================================
contenido.append(Paragraph("2. Viáticos, Reembolsos y Gastos de Representación", estilo_seccion))

contenido.append(Paragraph("2.1 Topes diarios de viáticos", estilo_subseccion))
contenido.append(Paragraph(
    "Los viáticos cubren alimentación, transporte local y hospedaje durante viajes "
    "de trabajo autorizados. Los montos máximos diarios, en dólares americanos (USD), "
    "son los siguientes:",
    estilo_cuerpo,
))

tabla_viaticos = Table(
    [
        ["Concepto", "Viaje Nacional (USD/día)", "Viaje Internacional (USD/día)"],
        ["Alimentación", "35", "60"],
        ["Transporte local", "20", "40"],
        ["Hospedaje", "80", "150"],
        ["Gastos de representación (gerencia)", "hasta 100", "hasta 200"],
    ],
    colWidths=[2.3 * inch, 1.7 * inch, 1.9 * inch],
)
tabla_viaticos.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0B3D91")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.white]),
    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
contenido.append(tabla_viaticos)
contenido.append(Spacer(1, 10))

contenido.append(Paragraph("2.2 Comprobantes fiscales requeridos", estilo_subseccion))
contenido.append(Paragraph(
    "Todo gasto sujeto a reembolso debe respaldarse con comprobante fiscal válido "
    "(factura o boleta electrónica) a nombre de Globex Corp, indicando fecha, "
    "concepto y monto. Los comprobantes deben cargarse en el sistema \"Globex Expense\" "
    "dentro de los 10 días hábiles posteriores al viaje. Gastos sin comprobante fiscal "
    "válido, o presentados fuera de plazo, no serán reembolsados, salvo excepción "
    "aprobada por la Gerencia de Finanzas.",
    estilo_cuerpo,
))

contenido.append(Paragraph("2.3 Anticipos de viaje", estilo_subseccion))
contenido.append(Paragraph(
    "Se puede solicitar un anticipo de hasta el 70% del presupuesto estimado del "
    "viaje, con un mínimo de 5 días hábiles de anticipación. La liquidación final, "
    "con comprobantes y devolución de saldo no utilizado, debe presentarse dentro "
    "de los 10 días hábiles posteriores al regreso.",
    estilo_cuerpo,
))
contenido.append(PageBreak())

# =====================================================================
# SECCIÓN 3 — Trabajo Remoto / Home Office
# =====================================================================
contenido.append(Paragraph("3. Modalidad de Trabajo Remoto / Home Office", estilo_seccion))

contenido.append(Paragraph("3.1 Requisitos de elegibilidad", estilo_subseccion))
contenido.append(Paragraph(
    "Pueden acogerse a la modalidad de trabajo remoto los colaboradores cuyo puesto "
    "no requiera presencia física obligatoria (por ejemplo, atención de planta, "
    "recepción o soporte in situ), que cuenten con al menos 3 meses de antigüedad "
    "en la empresa y que tengan una evaluación de desempeño igual o superior a "
    "\"Cumple expectativas\" en su última revisión.",
    estilo_cuerpo,
))

contenido.append(Paragraph("3.2 Modalidades disponibles", estilo_subseccion))
modalidades = [
    "Remoto total: hasta 5 días a la semana fuera de oficina, sujeto a aprobación del líder de área.",
    "Híbrido estándar: 3 días remoto y 2 días en oficina, con días de oficina fijados por el equipo.",
    "Remoto ocasional: hasta 2 días al mes, sin necesidad de aprobación previa formal.",
]
contenido.append(
    ListFlowable(
        [ListItem(Paragraph(m, estilo_item)) for m in modalidades],
        bulletType="bullet",
    )
)

contenido.append(Paragraph("3.3 Equipo provisto por la empresa", estilo_subseccion))
contenido.append(Paragraph(
    "Globex Corp entrega en calidad de préstamo, para quienes trabajen bajo "
    "modalidad remota o híbrida, el siguiente equipo estándar: laptop corporativa, "
    "monitor adicional (opcional, sujeto a stock), teclado y mouse inalámbricos, "
    "y silla ergonómica para colaboradores con más de 6 meses en modalidad remota. "
    "El equipo es propiedad de la empresa y debe devolverse en caso de desvinculación "
    "o cambio de modalidad.",
    estilo_cuerpo,
))

contenido.append(Paragraph("3.4 Apoyo de conectividad", estilo_subseccion))
contenido.append(Paragraph(
    "Se otorga un apoyo mensual de USD 25 para internet residencial y USD 10 "
    "para consumo eléctrico adicional, depositado junto con la planilla mensual "
    "a quienes estén formalmente en modalidad remota total o híbrida. Este apoyo "
    "no aplica a la modalidad de remoto ocasional.",
    estilo_cuerpo,
))
contenido.append(PageBreak())

# =====================================================================
# SECCIÓN 4 — Código de Ética y Canal de Denuncias
# =====================================================================
contenido.append(Paragraph("4. Código de Ética y Canal de Denuncias Internas", estilo_seccion))

contenido.append(Paragraph("4.1 Principios generales", estilo_subseccion))
contenido.append(Paragraph(
    "Todo colaborador de Globex Corp debe actuar con integridad, honestidad y "
    "respeto en sus relaciones internas y con clientes, proveedores y la comunidad. "
    "Se prohíbe expresamente cualquier forma de acoso laboral o sexual, discriminación "
    "por género, edad, religión, orientación sexual, nacionalidad o discapacidad, así "
    "como el uso indebido de información confidencial, activos de la empresa o "
    "conflictos de interés no declarados.",
    estilo_cuerpo,
))

contenido.append(Paragraph("4.2 Conflictos de interés", estilo_subseccion))
contenido.append(Paragraph(
    "Todo colaborador debe declarar por escrito, ante el área de Cumplimiento, "
    "cualquier relación personal, familiar o comercial que pudiera representar un "
    "conflicto de interés real o potencial con sus funciones, incluyendo relaciones "
    "de parentesco con proveedores, clientes o subordinados directos.",
    estilo_cuerpo,
))

contenido.append(Paragraph("4.3 Canal de denuncias internas", estilo_subseccion))
contenido.append(Paragraph(
    "Globex Corp cuenta con la \"Línea Ética Globex\", un canal confidencial y "
    "anónimo disponible las 24 horas, los 7 días de la semana, para reportar "
    "conductas contrarias al presente Código de Ética. Las denuncias pueden "
    "presentarse a través del portal web interno, por correo electrónico dedicado "
    "o mediante línea telefónica gratuita. Toda denuncia recibida es investigada "
    "por un comité independiente en un plazo máximo de 30 días hábiles, "
    "garantizando la confidencialidad del denunciante y prohibiendo expresamente "
    "cualquier represalia en su contra.",
    estilo_cuerpo,
))

contenido.append(Paragraph("4.4 Consecuencias del incumplimiento", estilo_subseccion))
contenido.append(Paragraph(
    "El incumplimiento comprobado del Código de Ética puede derivar en medidas "
    "disciplinarias que van desde una amonestación escrita hasta la desvinculación "
    "con causa justificada, sin perjuicio de las acciones legales civiles o penales "
    "que correspondan según la gravedad de la falta.",
    estilo_cuerpo,
))

# ---------------------------------------------------------------------
# 4. Construcción del PDF
# ---------------------------------------------------------------------
doc = SimpleDocTemplate(
    RUTA_SALIDA,
    pagesize=LETTER,
    topMargin=0.9 * inch,
    bottomMargin=0.9 * inch,
    leftMargin=0.9 * inch,
    rightMargin=0.9 * inch,
    title="Manual de Políticas - Globex Corp",
    author="Globex Corp - Recursos Humanos",
)

doc.build(contenido)

print(f"✅ PDF generado correctamente en: {RUTA_SALIDA}")
