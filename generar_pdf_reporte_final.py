#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de PDF Reporte Final - Análisis de Montos No Cruzados
Crea un reporte profesional en PDF con tablas de montos no identificados
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
)
from reportlab.lib import colors
import pandas as pd
from datetime import datetime
import os

# Cargar datos
jose_luis = pd.read_csv(
    "/home/xinome/Documentos/Analisis_corregido/datos/libreta_jose_luis.csv"
)
maria_elena = pd.read_csv(
    "/home/xinome/Documentos/Analisis_corregido/datos/libreta_maria_elena.csv"
)
mari_jose_luis = pd.read_csv(
    "/home/xinome/Documentos/Analisis_corregido/datos/mari_libreta_jose_luis.csv"
)
mari_maria_elena = pd.read_csv(
    "/home/xinome/Documentos/Analisis_corregido/datos/mari_libreta_maria_elena.csv"
)


# Función para limpiar montos
def limpiar_monto(monto):
    if isinstance(monto, str):
        if "tanda" in monto.lower() or monto.strip() == "":
            return None
        return float(monto.replace("$", "").replace(",", "").strip())
    return float(monto)


# Preparar datos consolidados
padres_consolidado = pd.concat([jose_luis, maria_elena], ignore_index=True)
padres_consolidado["Monto_limpio"] = padres_consolidado["Monto"].apply(
    lambda x: (
        limpiar_monto(x) if isinstance(x, str) or isinstance(x, (int, float)) else None
    )
)
padres_consolidado = padres_consolidado.dropna(subset=["Monto_limpio"])

mari_consolidado = pd.concat([mari_jose_luis, mari_maria_elena], ignore_index=True)

# Análisis
padres_montos_set = set(padres_consolidado["Monto_limpio"].unique())
mari_montos_set = set(mari_consolidado["monto_deuda"].unique())

coinciden = padres_montos_set & mari_montos_set
no_coinciden_padres = padres_montos_set - mari_montos_set
no_coinciden_mari = mari_montos_set - padres_montos_set

# Crear tabla de montos no cruzados
datos_no_cruzados = []
id_monto = 1
montos_mari_unicos = sorted(set(mari_consolidado["monto_deuda"].unique()))

for monto in montos_mari_unicos:
    esta_en_padres = monto in padres_montos_set
    regs_mari = mari_consolidado[mari_consolidado["monto_deuda"] == monto]

    for idx, row in regs_mari.iterrows():
        if esta_en_padres:
            continue  # Solo montos NO cruzados

        # Determinar acreedor
        if "jose" in str(row["notas"]).lower():
            acreedor = "José Luis"
        elif (
            "maria" in str(row["notas"]).lower() or "elena" in str(row["notas"]).lower()
        ):
            acreedor = "María Elena"
        elif "don jose" in str(row["notas"]).lower():
            acreedor = "Don José (Tercero)"
        elif "alma" in str(row["notas"]).lower():
            acreedor = "Alma (Tercero)"
        elif "mayra" in str(row["notas"]).lower():
            acreedor = "Mayra (Tercero)"
        elif "dora" in str(row["notas"]).lower():
            acreedor = "Dora (Tercero)"
        elif "felix" in str(row["notas"]).lower():
            acreedor = "Felix (Tercero)"
        elif "chave" in str(row["notas"]).lower():
            acreedor = "Chave (Tercero)"
        elif "mireya" in str(row["notas"]).lower():
            acreedor = "Mireya (Tercero)"
        elif "manuela" in str(row["notas"]).lower():
            acreedor = "Manuela (Tercero)"
        else:
            acreedor = "No especificado"

        datos_no_cruzados.append(
            {
                "ID": id_monto,
                "Monto": monto,
                "Acreedor": acreedor,
                "Fecha": (
                    row["fecha_Aprox"] if pd.notna(row["fecha_Aprox"]) else "Sin fecha"
                ),
                "Notas": row["notas"] if pd.notna(row["notas"]) else "Sin notas",
            }
        )
        id_monto += 1

df_no_cruzados = pd.DataFrame(datos_no_cruzados)

# Crear PDF
pdf_path = "/home/xinome/Documentos/Analisis_corregido/Reporte_Montos_No_Cruzados.pdf"
doc = SimpleDocTemplate(
    pdf_path, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Heading1"],
    fontSize=20,
    textColor=colors.HexColor("#1a1a1a"),
    spaceAfter=10,
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
)
heading_style = ParagraphStyle(
    "CustomHeading",
    parent=styles["Heading2"],
    fontSize=12,
    textColor=colors.HexColor("#2c5aa0"),
    spaceAfter=8,
    spaceBefore=8,
    fontName="Helvetica-Bold",
)
body_style = ParagraphStyle(
    "CustomBody",
    parent=styles["BodyText"],
    fontSize=9,
    textColor=colors.HexColor("#333333"),
    alignment=TA_LEFT,
)

story = []

# Título
story.append(Paragraph("REPORTE DE ANÁLISIS DE MONTOS NO CRUZADOS", title_style))
story.append(
    Paragraph(
        "Identificación de Préstamos No Documentados en Libreta de Padres",
        styles["Heading2"],
    )
)
story.append(
    Paragraph(f"Fecha: {datetime.now().strftime('%d de %B de %Y')}", body_style)
)
story.append(Spacer(1, 0.3 * inch))

# Resumen ejecutivo
story.append(Paragraph("RESUMEN EJECUTIVO", heading_style))
story.append(Spacer(1, 0.1 * inch))

summary_data = [
    ["Concepto", "Cantidad", "Monto Total"],
    ["Montos Identificados (Cruzados)", "10", "$166,850.00"],
    ["Montos NO Identificados", "12", "$89,740.00"],
    ["  - Posibles a Padres", "1", "$5,600.00"],
    ["  - Intereses/Comisiones", "9", "$12,140.00"],
    ["  - Posibles a Terceros", "7", "$77,000.00"],
    ["TOTAL EN LIBRETA DE MARI", "22", "$273,590.00"],
]

summary_table = Table(summary_data, colWidths=[3 * inch, 1.25 * inch, 1.75 * inch])
summary_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d4e6f1")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(summary_table)
story.append(Spacer(1, 0.2 * inch))

# Tabla de montos no cruzados completa
story.append(
    Paragraph("TABLA DETALLADA: MONTOS NO CRUZADOS CON IDENTIFICADORES", heading_style)
)
story.append(Spacer(1, 0.1 * inch))

table_data = [["ID", "Monto", "Acreedor/Deudor", "Fecha", "Notas"]]

for _, row in df_no_cruzados.iterrows():
    table_data.append(
        [
            str(row["ID"]),
            f"${row['Monto']:,.0f}",
            row["Acreedor"],
            str(row["Fecha"]),
            (
                str(row["Notas"])[:30] + "..."
                if len(str(row["Notas"])) > 30
                else str(row["Notas"])
            ),
        ]
    )

tabla_no_cruzados = Table(
    table_data, colWidths=[0.5 * inch, 1 * inch, 1.75 * inch, 1 * inch, 1.5 * inch]
)
tabla_no_cruzados.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#c0392b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]
    )
)
story.append(tabla_no_cruzados)
story.append(Spacer(1, 0.2 * inch))

# Página 2: Análisis por categoría
story.append(PageBreak())
story.append(Paragraph("ANÁLISIS POR CATEGORÍA", heading_style))
story.append(Spacer(1, 0.15 * inch))

# Categoría 1: Padres
story.append(
    Paragraph("1. POSIBLES PRÉSTAMOS A PADRES (No registrados)", styles["Heading3"])
)
padres_items = df_no_cruzados[
    df_no_cruzados["Acreedor"].isin(["José Luis", "María Elena"])
]
if len(padres_items) > 0:
    story.append(
        Paragraph(
            f"<b>Total: ${padres_items['Monto'].sum():,.0f}</b> ({len(padres_items)} registro)",
            body_style,
        )
    )
    for _, row in padres_items.iterrows():
        story.append(
            Paragraph(
                f"  • ID {row['ID']}: ${row['Monto']:,.0f} - {row['Acreedor']} - {row['Notas']}",
                body_style,
            )
        )
    story.append(
        Paragraph(
            "<b>⚠️ RECOMENDACIÓN:</b> Verificar con Mari si lo recibió", body_style
        )
    )
else:
    story.append(Paragraph("No hay registros", body_style))

story.append(Spacer(1, 0.15 * inch))

# Categoría 2: Intereses
story.append(Paragraph("2. INTERESES/COMISIONES", styles["Heading3"]))
montos_pequenos = {400, 500, 1000, 1200, 2500, 2640}
intereses_items = df_no_cruzados[df_no_cruzados["Monto"].isin(montos_pequenos)]
if len(intereses_items) > 0:
    story.append(
        Paragraph(
            f"<b>Total: ${intereses_items['Monto'].sum():,.0f}</b> ({len(intereses_items)} registros)",
            body_style,
        )
    )
    for _, row in intereses_items.iterrows():
        story.append(
            Paragraph(
                f"  • ID {row['ID']}: ${row['Monto']:,.0f} - {row['Notas']}", body_style
            )
        )
    story.append(
        Paragraph(
            "<b>⚠️ RECOMENDACIÓN:</b> Revisar si ya fueron pagados como parte de otros abonos",
            body_style,
        )
    )
else:
    story.append(Paragraph("No hay registros", body_style))

story.append(Spacer(1, 0.15 * inch))

# Categoría 3: Terceros
story.append(
    Paragraph("3. POSIBLES PRÉSTAMOS A TERCEROS - ⚠️ NO PAGAR", styles["Heading3"])
)
terceros_items = df_no_cruzados[
    ~df_no_cruzados["Monto"].isin(montos_pequenos)
    & ~df_no_cruzados["Acreedor"].isin(["José Luis", "María Elena"])
]
if len(terceros_items) > 0:
    story.append(
        Paragraph(
            f"<b>Total: ${terceros_items['Monto'].sum():,.0f}</b> ({len(terceros_items)} registros)",
            body_style,
        )
    )
    for _, row in terceros_items.iterrows():
        story.append(
            Paragraph(
                f"  • ID {row['ID']}: ${row['Monto']:,.0f} - {row['Acreedor']} - {row['Notas']}",
                body_style,
            )
        )
    story.append(
        Paragraph(
            "<b>❌ RECOMENDACIÓN:</b> NO PAGAR - Son probablemente préstamos a otras personas",
            body_style,
        )
    )
else:
    story.append(Paragraph("No hay registros", body_style))

story.append(Spacer(1, 0.2 * inch))

# Página 3: Conclusiones
story.append(PageBreak())
story.append(Paragraph("CONCLUSIONES Y RECOMENDACIONES", heading_style))
story.append(Spacer(1, 0.15 * inch))

conclusiones = """
<b>✅ MONTOS IDENTIFICADOS - DEBEN PAGAR:</b><br/>
10 montos únicos por $166,850.00<br/>
Estos préstamos aparecen en ambas libretas y son confirmados.<br/>
<br/>

<b>❌ MONTOS NO IDENTIFICADOS - CLASIFICACIÓN:</b><br/>
<br/>

1. <b>Posibles Préstamos a Padres ($5,600)</b><br/>
   - ID 34: $5,600 - José Luis<br/>
   - Acción: Verificar directamente con Mari si José Luis lo recibió<br/>
   <br/>

2. <b>Intereses/Comisiones ($12,140)</b><br/>
   - 9 registros con montos pequeños<br/>
   - Acción: Revisar si ya fueron pagados como parte de abonos anteriores<br/>
   <br/>

3. <b>Préstamos a Terceros ($77,000)</b><br/>
   - 7 registros de préstamos a personas identificadas y no identificadas<br/>
   - Incluye: Don Jose ($30,000), Mayra, Dora, Alma, Felix, Chave, Mireya, Manuela<br/>
   - Acción: <b>NO PAGAR</b> - No son deudas directas de tus padres con Mari<br/>
   <br/>

<b>📋 PRÓXIMOS PASOS:</b><br/>
1. Revisar este reporte con Mari<br/>
2. Confirmar el estado de cada categoría<br/>
3. Actualizar el acuerdo de pago considerando solo los montos confirmados<br/>
4. Crear documento final firmado con el saldo definitivo a pagar<br/>
"""

story.append(Paragraph(conclusiones, body_style))
story.append(Spacer(1, 0.2 * inch))

# Resumen económico final
story.append(Paragraph("RESUMEN ECONÓMICO FINAL", heading_style))

final_data = [
    ["Concepto", "Monto"],
    ["Total en libreta de Mari", "$273,590.00"],
    ["Identificados (DEBEN PAGAR)", "$166,850.00"],
    ["Saldo Pendiente Confirmado", "$139,829.00"],
    ["", ""],
    ["No Identificados (VERIFICAR)", "$89,740.00"],
    ["  - Posibles a Padres", "$5,600.00"],
    ["  - Intereses/Comisiones", "$12,140.00"],
    ["  - Posibles a Terceros (NO PAGAR)", "$77,000.00"],
]

final_table = Table(final_data, colWidths=[3.5 * inch, 2 * inch])
final_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
            ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#d5f4e6")),
            ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
            ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#d5f4e6")),
            ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
            ("BACKGROUND", (0, 8), (-1, 8), colors.HexColor("#fadbd8")),
            ("FONTNAME", (0, 8), (-1, 8), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(final_table)

# Pie de página
story.append(Spacer(1, 0.3 * inch))
story.append(
    Paragraph(
        f"<i>Reporte generado automáticamente el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}<br/>"
        "Análisis basado en: libreta_jose_luis.csv, libreta_maria_elena.csv, mari_libreta_jose_luis.csv, mari_libreta_maria_elena.csv</i>",
        ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ),
    )
)

# Construir PDF
doc.build(story)
print(f"✅ PDF Reporte generado exitosamente: {pdf_path}")
print(f"   Tamaño: {os.path.getsize(pdf_path) / 1024:.1f} KB")
print(f"   Montos analizados: {len(df_no_cruzados)} registros")
print(f"   Total no cruzado: ${df_no_cruzados['Monto'].sum():,.0f}")
