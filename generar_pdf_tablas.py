#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de PDF con Tablas Detalladas por Etiqueta
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
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


# Preparar PDF
pdf_path = "/home/xinome/Documentos/Analisis_corregido/Analisis_Tablas_Detalladas.pdf"
doc = SimpleDocTemplate(
    pdf_path, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
)

styles = getSampleStyleSheet()
title_style = ParagraphStyle(
    "CustomTitle",
    parent=styles["Heading1"],
    fontSize=20,
    textColor=colors.HexColor("#1a1a1a"),
    spaceAfter=12,
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
)
heading_style = ParagraphStyle(
    "CustomHeading",
    parent=styles["Heading2"],
    fontSize=12,
    textColor=colors.HexColor("#2c5aa0"),
    spaceAfter=6,
    spaceBefore=6,
    fontName="Helvetica-Bold",
)

story = []

# Página 1: Título y tabla José Luis
story.append(Paragraph("ANÁLISIS DETALLADO DE PRÉSTAMOS POR FUENTE", title_style))
story.append(
    Paragraph(
        f"Generado: {datetime.now().strftime('%d de %B de %Y')}", styles["Normal"]
    )
)
story.append(Spacer(1, 0.15 * inch))

# Tabla 1: José Luis
story.append(
    Paragraph("1. LIBRETA DE JOSÉ LUIS (Registros que él mantiene)", heading_style)
)

jose_luis["Monto_limpio"] = jose_luis["Monto"].apply(limpiar_monto)
jose_luis = jose_luis.dropna(subset=["Monto_limpio"])
jose_luis_copy = jose_luis.copy()
jose_luis_copy["ID"] = range(1, len(jose_luis_copy) + 1)

tabla_jl_data = [["ID", "Monto", "Fecha", "Abonos", "Saldo"]]
for idx, row in jose_luis_copy.iterrows():
    monto = row["Monto_limpio"]
    abono = row["Abonos"] if pd.notna(row["Abonos"]) else 0
    saldo = monto - abono
    tabla_jl_data.append(
        [
            str(int(row["ID"])),
            f"${monto:,.2f}",
            str(row["Fecha de prestamo"])[:20],
            f"${abono:,.2f}",
            f"${saldo:,.2f}",
        ]
    )

# Resumen
total_jl = jose_luis_copy["Monto_limpio"].sum()
abonos_jl = jose_luis_copy["Abonos"].sum()
tabla_jl_data.append(
    [
        "TOTAL",
        f"${total_jl:,.2f}",
        "",
        f"${abonos_jl:,.2f}",
        f"${total_jl - abonos_jl:,.2f}",
    ]
)

tabla_jl = Table(
    tabla_jl_data, colWidths=[0.6 * inch, 1.1 * inch, 1.5 * inch, 0.9 * inch, 1 * inch]
)
tabla_jl.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d4e6f1")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(tabla_jl)
story.append(Spacer(1, 0.15 * inch))

# Página 2: María Elena
story.append(PageBreak())
story.append(
    Paragraph("2. LIBRETA DE MARÍA ELENA (Registros que ella mantiene)", heading_style)
)

maria_elena["Monto_limpio"] = maria_elena["Monto"].apply(limpiar_monto)
maria_elena = maria_elena.dropna(subset=["Monto_limpio"])
maria_elena_copy = maria_elena.copy()
maria_elena_copy["ID"] = range(1, len(maria_elena_copy) + 1)

tabla_me_data = [["ID", "Monto", "Fecha", "Abonos", "Saldo"]]
for idx, row in maria_elena_copy.iterrows():
    monto = row["Monto_limpio"]
    abono = row["Abonos"] if pd.notna(row["Abonos"]) else 0
    saldo = monto - abono
    tabla_me_data.append(
        [
            str(int(row["ID"])),
            f"${monto:,.2f}",
            str(row["Fecha de prestamo"])[:20],
            f"${abono:,.2f}",
            f"${saldo:,.2f}",
        ]
    )

total_me = maria_elena_copy["Monto_limpio"].sum()
abonos_me = maria_elena_copy["Abonos"].sum()
tabla_me_data.append(
    [
        "TOTAL",
        f"${total_me:,.2f}",
        "",
        f"${abonos_me:,.2f}",
        f"${total_me - abonos_me:,.2f}",
    ]
)

tabla_me = Table(
    tabla_me_data, colWidths=[0.6 * inch, 1.1 * inch, 1.5 * inch, 0.9 * inch, 1 * inch]
)
tabla_me.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#27ae60")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#d5f4e6")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(tabla_me)
story.append(Spacer(1, 0.15 * inch))

# Página 3: Mari sobre José Luis
story.append(PageBreak())
story.append(Paragraph("3. LIBRETA DE MARI - REGISTROS SOBRE JOSÉ LUIS", heading_style))

mari_jl_copy = mari_jose_luis.copy()
mari_jl_copy["ID"] = range(1, len(mari_jl_copy) + 1)

tabla_mari_jl_data = [["ID", "Monto", "Fecha", "Abonos", "Saldo"]]
for idx, row in mari_jl_copy.iterrows():
    monto = row["monto_deuda"]
    abono = row["Abonos"] if pd.notna(row["Abonos"]) else 0
    saldo = monto - abono
    tabla_mari_jl_data.append(
        [
            str(int(row["ID"])),
            f"${monto:,.2f}",
            str(row["fecha_Aprox"])[:15],
            f"${abono:,.2f}",
            f"${saldo:,.2f}",
        ]
    )

total_mari_jl = mari_jl_copy["monto_deuda"].sum()
abonos_mari_jl = mari_jl_copy["Abonos"].sum()
tabla_mari_jl_data.append(
    [
        "TOTAL",
        f"${total_mari_jl:,.2f}",
        "",
        f"${abonos_mari_jl:,.2f}",
        f"${total_mari_jl - abonos_mari_jl:,.2f}",
    ]
)

tabla_mari_jl = Table(
    tabla_mari_jl_data,
    colWidths=[0.6 * inch, 1.1 * inch, 1.5 * inch, 0.9 * inch, 1 * inch],
)
tabla_mari_jl.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e74c3c")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fadbd8")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(tabla_mari_jl)
story.append(Spacer(1, 0.15 * inch))

# Página 4: Mari sobre María Elena
story.append(PageBreak())
story.append(
    Paragraph("4. LIBRETA DE MARI - REGISTROS SOBRE MARÍA ELENA", heading_style)
)

mari_me_copy = mari_maria_elena.copy()
mari_me_copy["ID"] = range(1, len(mari_me_copy) + 1)

tabla_mari_me_data = [["ID", "Monto", "Fecha", "Abonos", "Saldo"]]
for idx, row in mari_me_copy.iterrows():
    monto = row["monto_deuda"]
    abono = row["Abonos"] if pd.notna(row["Abonos"]) else 0
    saldo = monto - abono
    tabla_mari_me_data.append(
        [
            str(int(row["ID"])),
            f"${monto:,.2f}",
            str(row["fecha_Aprox"])[:15],
            f"${abono:,.2f}",
            f"${saldo:,.2f}",
        ]
    )

total_mari_me = mari_me_copy["monto_deuda"].sum()
abonos_mari_me = mari_me_copy["Abonos"].sum()
tabla_mari_me_data.append(
    [
        "TOTAL",
        f"${total_mari_me:,.2f}",
        "",
        f"${abonos_mari_me:,.2f}",
        f"${total_mari_me - abonos_mari_me:,.2f}",
    ]
)

tabla_mari_me = Table(
    tabla_mari_me_data,
    colWidths=[0.6 * inch, 1.1 * inch, 1.5 * inch, 0.9 * inch, 1 * inch],
)
tabla_mari_me.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f39c12")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7.5),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, -1), (-1, -1), colors.HexColor("#fdebd0")),
            ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(tabla_mari_me)

# Pie de página
story.append(Spacer(1, 0.2 * inch))
story.append(
    Paragraph(
        f"<i>Documento generado: {datetime.now().strftime('%d de %B de %Y a las %H:%M')}</i>",
        ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            fontSize=7,
            textColor=colors.grey,
            alignment=TA_CENTER,
        ),
    )
)

# Construir PDF
doc.build(story)
print(f"✅ PDF de tablas detalladas generado: {pdf_path}")
print(f"   Tamaño: {os.path.getsize(pdf_path) / 1024:.1f} KB")

import os
