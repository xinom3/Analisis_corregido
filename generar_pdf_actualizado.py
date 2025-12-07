#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de PDF - Análisis de Préstamos ACTUALIZADO
Crea un reporte en PDF con el análisis consolidado de préstamos
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

padres_total = padres_consolidado["Monto_limpio"].sum()
mari_total = mari_consolidado["monto_deuda"].sum()

no_id_total = mari_consolidado[mari_consolidado["monto_deuda"].isin(no_coinciden_mari)][
    "monto_deuda"
].sum()
no_id_padres_total = padres_consolidado[
    padres_consolidado["Monto_limpio"].isin(no_coinciden_padres)
]["Monto_limpio"].sum()

# Crear PDF
pdf_path = "/home/xinome/Documentos/Analisis_corregido/Analisis_Prestamos.pdf"
doc = SimpleDocTemplate(
    pdf_path, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
)

# Estilos
styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Heading1"],
    fontSize=24,
    textColor=colors.HexColor("#1a1a1a"),
    spaceAfter=10,
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
)
heading_style = ParagraphStyle(
    "CustomHeading",
    parent=styles["Heading2"],
    fontSize=14,
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

# Contenido del PDF
story = []

# Título
story.append(Paragraph("ANÁLISIS CONSOLIDADO DE PRÉSTAMOS", title_style))
story.append(
    Paragraph(f"Generado: {datetime.now().strftime('%d de %B de %Y')}", body_style)
)
story.append(Spacer(1, 0.2 * inch))

# Sección 1: Resumen Ejecutivo
story.append(Paragraph("1. RESUMEN EJECUTIVO", heading_style))
summary_data = [
    ["Concepto", "Monto"],
    ["Total en libreta de PADRES", f"${padres_total:,.2f}"],
    ["Total en libreta de MARI", f"${mari_total:,.2f}"],
    ["Diferencia entre libretas", f"${abs(padres_total - mari_total):,.2f}"],
]
summary_table = Table(summary_data, colWidths=[3.5 * inch, 2 * inch])
summary_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
        ]
    )
)
story.append(summary_table)
story.append(Spacer(1, 0.2 * inch))

# Sección 2: Préstamos Confirmados
story.append(
    Paragraph("2. PRÉSTAMOS CONFIRMADOS (Aparecen en ambas libretas)", heading_style)
)

confirmados_data = [
    ["Monto", "Padres", "Mari", "Total Prestado", "Abonos", "Saldo Pendiente"],
]

for monto in sorted(coinciden):
    padres_count = (padres_consolidado["Monto_limpio"] == monto).sum()
    mari_count = (mari_consolidado["monto_deuda"] == monto).sum()

    padres_reg = padres_consolidado[padres_consolidado["Monto_limpio"] == monto]

    padres_abonos = padres_reg["Abonos"].sum() if "Abonos" in padres_reg.columns else 0

    total_prestado = monto * padres_count
    saldo = total_prestado - padres_abonos

    confirmados_data.append(
        [
            f"${monto:,.2f}",
            str(padres_count),
            str(mari_count),
            f"${total_prestado:,.2f}",
            f"${padres_abonos:,.2f}",
            f"${saldo:,.2f}",
        ]
    )

total_prestado_confirmado = sum(
    [
        m
        * min(
            (padres_consolidado["Monto_limpio"] == m).sum(),
            (mari_consolidado["monto_deuda"] == m).sum(),
        )
        for m in coinciden
    ]
)
total_abonos_confirmado = sum(
    [
        padres_consolidado[padres_consolidado["Monto_limpio"] == m]["Abonos"].sum()
        for m in coinciden
    ]
)
total_saldo_confirmado = total_prestado_confirmado - total_abonos_confirmado

confirmados_data.append(
    [
        "TOTALES",
        "",
        "",
        f"${total_prestado_confirmado:,.2f}",
        f"${total_abonos_confirmado:,.2f}",
        f"${total_saldo_confirmado:,.2f}",
    ]
)

confirmados_table = Table(
    confirmados_data,
    colWidths=[1.2 * inch, 0.6 * inch, 0.6 * inch, 1.2 * inch, 1 * inch, 1.2 * inch],
)
confirmados_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d4e6f1")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(confirmados_table)
story.append(Spacer(1, 0.15 * inch))

# Sección 3: Montos sin identificar
story.append(
    Paragraph(
        "3. MONTOS NO IDENTIFICADOS EN PADRES (Mari registra, padres NO)", heading_style
    )
)

montos_pequenos = [400, 500, 1000, 1200, 2500, 2640]
montos_grandes = [4000, 4400, 5600, 8600, 12000, 35000]

total_pequenos = sum([m for m in montos_pequenos if m in no_coinciden_mari])
total_grandes_no_id = sum([m for m in montos_grandes if m in no_coinciden_mari])

story.append(Paragraph(f"Total No Identificado: ${no_id_total:,.2f}", body_style))
story.append(Spacer(1, 0.1 * inch))

story.append(
    Paragraph(
        f"<b>a) Posibles Intereses/Comisiones:</b> ${total_pequenos:,.2f}",
        body_style,
    )
)
pequenos_text = ", ".join(
    [f"${m:,}" for m in sorted([m for m in montos_pequenos if m in no_coinciden_mari])]
)
story.append(Paragraph(f"Montos: {pequenos_text}", body_style))
story.append(Spacer(1, 0.1 * inch))

story.append(
    Paragraph(
        f"<b>b) Montos Grandes Sin Identificar:</b> ${total_grandes_no_id:,.2f}",
        body_style,
    )
)
grandes_text = ", ".join(
    [f"${m:,}" for m in sorted([m for m in montos_grandes if m in no_coinciden_mari])]
)
story.append(Paragraph(f"Montos: {grandes_text}", body_style))
story.append(
    Paragraph(
        "<b>⚠️ Recomendación:</b> Verificar si son préstamos a terceros o errores de registro",
        body_style,
    )
)
story.append(Spacer(1, 0.15 * inch))

# Sección 4: Montos en padres no en Mari
story.append(Paragraph("4. MONTOS EN PADRES QUE NO ESTÁN EN MARI", heading_style))
story.append(Paragraph(f"Total: ${no_id_padres_total:,.2f}", body_style))
story.append(
    Paragraph(
        "$15,000 (María Elena) - Nota: 'Mayra tiene el control de este préstamo que se realizó a Jorge'",
        body_style,
    )
)
story.append(
    Paragraph(
        "<b>🎯 CONCLUSIÓN: NO DEBERÍAN PAGAR ESTO A MARI (no está en su libreta)</b>",
        body_style,
    )
)
story.append(Spacer(1, 0.15 * inch))

# Página 2
story.append(PageBreak())

# Sección 5: Conclusiones
story.append(Paragraph("5. CONCLUSIONES Y RECOMENDACIONES", heading_style))

story.append(Paragraph("<b>✅ DEBEN PAGAR A MARI (Confirmado):</b>", body_style))
story.append(
    Paragraph(
        f"Mínimo: ${total_saldo_confirmado:,.2f} (saldo después de abonos registrados)",
        body_style,
    )
)
story.append(
    Paragraph(
        f"Máximo: ${total_prestado_confirmado:,.2f} (si no han pagado nada)", body_style
    )
)
story.append(Spacer(1, 0.1 * inch))

story.append(Paragraph("<b>❌ NO DEBEN PAGAR:</b>", body_style))
story.append(Paragraph("$15,000 - No está en libreta de Mari", body_style))
story.append(Spacer(1, 0.1 * inch))

story.append(Paragraph("<b>⚠️ DEBEN VERIFICAR CON MARI ANTES DE PAGAR:</b>", body_style))
story.append(
    Paragraph(
        f"${no_id_total:,.2f} - Préstamos no documentados por ustedes:", body_style
    )
)
story.append(
    Paragraph(f"  • Posiblemente a terceros (Don Jose, Mayra, etc.)", body_style)
)
story.append(
    Paragraph(f"  • Intereses/comisiones no incluidas en sus libretas", body_style)
)
story.append(Paragraph(f"  • Errores de transcripción", body_style))
story.append(Spacer(1, 0.15 * inch))

story.append(Paragraph("<b>📋 PRÓXIMOS PASOS:</b>", body_style))
story.append(
    Paragraph("1. Sentarse con Mari y revisar cada monto que no coincide", body_style)
)
story.append(
    Paragraph(
        f"2. Obtener fechas y contexto para los ${total_grandes_no_id:,.2f} en montos grandes",
        body_style,
    )
)
story.append(
    Paragraph(
        f"3. Clarificar cuáles de los ${total_pequenos:,.2f} son intereses ya pagados",
        body_style,
    )
)
story.append(
    Paragraph(
        "4. Crear un documento final firmado con los montos definitivos a pagar",
        body_style,
    )
)
story.append(Spacer(1, 0.2 * inch))

# Tabla de resumen final
story.append(Paragraph("6. TABLA RESUMEN", heading_style))
resumen_final = [
    ["Concepto", "Monto"],
    ["Total Prestado (Confirmado)", f"${total_prestado_confirmado:,.2f}"],
    ["Total Abonado", f"${total_abonos_confirmado:,.2f}"],
    ["SALDO PENDIENTE", f"${total_saldo_confirmado:,.2f}"],
    ["Montos No Identificados", f"${no_id_total:,.2f}"],
    ["NO Debe Pagar", f"${no_id_padres_total:,.2f}"],
]
final_table = Table(resumen_final, colWidths=[3.5 * inch, 2 * inch])
final_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ("FONTSIZE", (0, 1), (-1, -1), 9),
            ("BACKGROUND", (0, 3), (-1, 3), colors.HexColor("#f5b7b1")),
            ("FONTNAME", (0, 3), (-1, 3), "Helvetica-Bold"),
        ]
    )
)
story.append(final_table)

# Pie de página
story.append(Spacer(1, 0.3 * inch))
story.append(
    Paragraph(
        f"<i>Documento generado automáticamente el {datetime.now().strftime('%d de %B de %Y a las %H:%M')}</i>",
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
print(f"✅ PDF generado exitosamente: {pdf_path}")
