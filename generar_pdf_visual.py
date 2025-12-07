#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de PDF con Visualizaciones - Análisis de Préstamos
Crea un reporte en PDF con gráficos y análisis consolidado
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
    Image,
)
from reportlab.lib import colors
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("Agg")  # Usar backend sin GUI
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

# Calcular totales confirmados
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

# Crear directorio para gráficos
temp_dir = "/tmp/graficos_pdf"
os.makedirs(temp_dir, exist_ok=True)

# ============ GRÁFICO 1: Comparación Totales ============
fig, ax = plt.subplots(figsize=(8, 5))
categorias = ["Padres", "Mari"]
montos = [padres_total, mari_total]
colores_bar = ["#3498db", "#e74c3c"]
barras = ax.bar(
    categorias, montos, color=colores_bar, alpha=0.7, edgecolor="black", linewidth=2
)

# Añadir valores en las barras
for barra, monto in zip(barras, montos):
    altura = barra.get_height()
    ax.text(
        barra.get_x() + barra.get_width() / 2.0,
        altura,
        f"${monto:,.0f}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

ax.set_ylabel("Monto ($)", fontsize=12, fontweight="bold")
ax.set_title(
    "Comparación de Totales: Padres vs Mari", fontsize=14, fontweight="bold", pad=20
)
ax.set_ylim(0, max(montos) * 1.15)
ax.grid(axis="y", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig(f"{temp_dir}/grafico1_comparacion.png", dpi=150, bbox_inches="tight")
plt.close()

# ============ GRÁFICO 2: Distribución de Préstamos Confirmados ============
montos_confirmados = sorted(coinciden)
cantidades = []
for m in montos_confirmados:
    cant = (padres_consolidado["Monto_limpio"] == m).sum()
    cantidades.append(cant)

fig, ax = plt.subplots(figsize=(10, 6))
x_pos = range(len(montos_confirmados))
barras = ax.bar(
    x_pos, cantidades, color="#27ae60", alpha=0.7, edgecolor="black", linewidth=1.5
)

# Añadir valores en barras
for barra, cant in zip(barras, cantidades):
    altura = barra.get_height()
    ax.text(
        barra.get_x() + barra.get_width() / 2.0,
        altura,
        f"{int(cant)}",
        ha="center",
        va="bottom",
        fontsize=10,
        fontweight="bold",
    )

ax.set_xticks(x_pos)
ax.set_xticklabels(
    [f"${int(m):,}" for m in montos_confirmados], rotation=45, ha="right"
)
ax.set_ylabel("Cantidad de Registros", fontsize=11, fontweight="bold")
ax.set_title(
    "Distribución de Préstamos Confirmados por Monto",
    fontsize=13,
    fontweight="bold",
    pad=15,
)
ax.grid(axis="y", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig(f"{temp_dir}/grafico2_distribucion.png", dpi=150, bbox_inches="tight")
plt.close()

# ============ GRÁFICO 3: Resumen de Situación Financiera ============
fig, ax = plt.subplots(figsize=(9, 6))
conceptos = ["Total\nPrestado", "Total\nAbonado", "Saldo\nPendiente"]
valores = [total_prestado_confirmado, total_abonos_confirmado, total_saldo_confirmado]
colores_res = ["#3498db", "#2ecc71", "#e74c3c"]
barras = ax.bar(
    conceptos, valores, color=colores_res, alpha=0.8, edgecolor="black", linewidth=2
)

# Añadir valores en las barras
for barra, valor in zip(barras, valores):
    altura = barra.get_height()
    ax.text(
        barra.get_x() + barra.get_width() / 2.0,
        altura,
        f"${valor:,.0f}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

ax.set_ylabel("Monto ($)", fontsize=12, fontweight="bold")
ax.set_title(
    "Resumen Financiero: Préstamos Confirmados", fontsize=14, fontweight="bold", pad=20
)
ax.set_ylim(0, max(valores) * 1.2)
ax.grid(axis="y", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig(f"{temp_dir}/grafico3_resumen_financiero.png", dpi=150, bbox_inches="tight")
plt.close()

# ============ GRÁFICO 4: Pie Chart - Desglose de Montos ============
fig, ax = plt.subplots(figsize=(9, 6))
montos_para_pie = []
etiquetas_pie = []

for m in sorted(coinciden, reverse=True):
    total = m * (padres_consolidado["Monto_limpio"] == m).sum()
    montos_para_pie.append(total)
    etiquetas_pie.append(f"${int(m):,}")

colores_pie = plt.cm.Set3(range(len(montos_para_pie)))
wedges, texts, autotexts = ax.pie(
    montos_para_pie,
    labels=etiquetas_pie,
    autopct="%1.1f%%",
    colors=colores_pie,
    startangle=90,
    textprops={"fontsize": 10},
)

for autotext in autotexts:
    autotext.set_color("white")
    autotext.set_fontweight("bold")

ax.set_title(
    "Distribución de Montos Totales Confirmados", fontsize=13, fontweight="bold", pad=20
)
plt.tight_layout()
plt.savefig(f"{temp_dir}/grafico4_pie_montos.png", dpi=150, bbox_inches="tight")
plt.close()

# ============ GRÁFICO 5: Estado de Discrepancias ============
fig, ax = plt.subplots(figsize=(10, 6))
estados = ["Confirmados\n(Ambos)", "No Identificados\nen Padres", "No Deben\nPagar"]
montos_estados = [total_prestado_confirmado, no_id_total, 15000]
colores_estados = ["#27ae60", "#f39c12", "#c0392b"]
barras = ax.bar(
    estados,
    montos_estados,
    color=colores_estados,
    alpha=0.8,
    edgecolor="black",
    linewidth=2,
)

# Añadir valores
for barra, valor in zip(barras, montos_estados):
    altura = barra.get_height()
    ax.text(
        barra.get_x() + barra.get_width() / 2.0,
        altura,
        f"${valor:,.0f}",
        ha="center",
        va="bottom",
        fontsize=12,
        fontweight="bold",
    )

ax.set_ylabel("Monto ($)", fontsize=12, fontweight="bold")
ax.set_title(
    "Estado de Discrepancias: Clasificación de Montos",
    fontsize=14,
    fontweight="bold",
    pad=20,
)
ax.set_ylim(0, max(montos_estados) * 1.2)
ax.grid(axis="y", alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig(f"{temp_dir}/grafico5_discrepancias.png", dpi=150, bbox_inches="tight")
plt.close()

# ============ Crear PDF ============
pdf_path = "/home/xinome/Documentos/Analisis_corregido/Analisis_Prestamos_Visual.pdf"
doc = SimpleDocTemplate(
    pdf_path, pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch
)

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

story = []

# Página 1: Título y Gráficos
story.append(Paragraph("ANÁLISIS CONSOLIDADO DE PRÉSTAMOS", title_style))
story.append(Paragraph("Con Visualizaciones Gráficas", styles["Heading2"]))
story.append(
    Paragraph(
        f"Generado: {datetime.now().strftime('%d de %B de %Y')}", styles["Normal"]
    )
)
story.append(Spacer(1, 0.2 * inch))

# Gráfico 1
story.append(Paragraph("1. Comparación de Totales: Padres vs Mari", heading_style))
story.append(
    Image(f"{temp_dir}/grafico1_comparacion.png", width=6 * inch, height=3.75 * inch)
)
story.append(Spacer(1, 0.15 * inch))

# Gráfico 2
story.append(PageBreak())
story.append(Paragraph("2. Distribución de Préstamos Confirmados", heading_style))
story.append(
    Image(f"{temp_dir}/grafico2_distribucion.png", width=6.5 * inch, height=3.9 * inch)
)
story.append(Spacer(1, 0.15 * inch))

# Gráfico 3
story.append(PageBreak())
story.append(Paragraph("3. Resumen Financiero: Préstamos Confirmados", heading_style))
story.append(
    Image(
        f"{temp_dir}/grafico3_resumen_financiero.png",
        width=6 * inch,
        height=3.75 * inch,
    )
)
story.append(Spacer(1, 0.2 * inch))

# Tabla resumida
summary_data = [
    ["Concepto", "Monto"],
    ["Total Prestado (Confirmado)", f"${total_prestado_confirmado:,.2f}"],
    ["Total Abonado", f"${total_abonos_confirmado:,.2f}"],
    ["SALDO PENDIENTE", f"${total_saldo_confirmado:,.2f}"],
]
summary_table = Table(summary_data, colWidths=[3.5 * inch, 2 * inch])
summary_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5aa0")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
            ("BACKGROUND", (0, 1), (-1, -1), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )
)
story.append(summary_table)

# Página 2: Gráficos adicionales
story.append(PageBreak())
story.append(Paragraph("4. Distribución de Montos Totales", heading_style))
story.append(
    Image(f"{temp_dir}/grafico4_pie_montos.png", width=5.5 * inch, height=4.125 * inch)
)
story.append(Spacer(1, 0.2 * inch))

story.append(Paragraph("5. Clasificación de Discrepancias", heading_style))
story.append(
    Image(f"{temp_dir}/grafico5_discrepancias.png", width=6.5 * inch, height=3.9 * inch)
)

# Página 3: Conclusiones
story.append(PageBreak())
story.append(Paragraph("CONCLUSIONES FINALES", heading_style))

conclusions = f"""
<b>✅ DEBEN PAGAR A MARI (Confirmado):</b><br/>
${total_saldo_confirmado:,.2f} (saldo después de abonos registrados)<br/>
<br/>

<b>❌ NO DEBEN PAGAR:</b><br/>
$15,000.00 - No está en libreta de Mari<br/>
<br/>

<b>⚠️ DEBEN VERIFICAR CON MARI ANTES DE PAGAR:</b><br/>
${no_id_total:,.2f} - Préstamos no documentados<br/>
<br/>

<b>📊 RESUMEN DE MONTOS:</b><br/>
• Total en libreta de PADRES: ${padres_total:,.2f}<br/>
• Total en libreta de MARI: ${mari_total:,.2f}<br/>
• Diferencia: ${abs(padres_total - mari_total):,.2f}<br/>
• Montos confirmados (ambos): 10<br/>
<br/>

<b>📋 PRÓXIMOS PASOS:</b><br/>
1. Reunirse con Mari para verificar los ${no_id_total:,.2f}<br/>
2. Confirmar el saldo pendiente de ${total_saldo_confirmado:,.2f}<br/>
3. Firmar un documento con los montos definitivos<br/>
4. Establecer un plan de pagos<br/>
"""

story.append(Paragraph(conclusions, styles["BodyText"]))

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
print(f"✅ PDF con visualizaciones generado exitosamente: {pdf_path}")
print(f"   Tamaño: {os.path.getsize(pdf_path) / 1024:.1f} KB")
