#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis Detallado con Tablas por Etiqueta y CSV Consolidado
Genera reportes estructurados para análisis de préstamos
"""

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


# ========== TABLAS IDENTIFICADAS POR ETIQUETA ==========

# 1. TABLA: Datos de José Luis (lo que él registra)
print("\n" + "=" * 100)
print("1. LIBRETA DE JOSÉ LUIS (Registros que él mantiene)")
print("=" * 100)
jose_luis["Monto_limpio"] = jose_luis["Monto"].apply(limpiar_monto)
jose_luis = jose_luis.dropna(subset=["Monto_limpio"])
jose_luis["ID"] = range(1, len(jose_luis) + 1)

tabla_jl = jose_luis[["ID", "Monto", "Fecha de prestamo", "Abonos", "Notas"]].copy()
tabla_jl.columns = ["ID", "Monto", "Fecha", "Abonos", "Notas"]
print(tabla_jl.to_string(index=False))
print(f"\nTotal registros: {len(jose_luis)}")
print(f"Total prestado: ${jose_luis['Monto_limpio'].sum():,.2f}")
print(f"Total abonado: ${jose_luis['Abonos'].sum():,.2f}")
print(
    f"Saldo pendiente: ${(jose_luis['Monto_limpio'].sum() - jose_luis['Abonos'].sum()):,.2f}"
)

# 2. TABLA: Datos de María Elena (lo que ella registra)
print("\n\n" + "=" * 100)
print("2. LIBRETA DE MARÍA ELENA (Registros que ella mantiene)")
print("=" * 100)
maria_elena["Monto_limpio"] = maria_elena["Monto"].apply(limpiar_monto)
maria_elena = maria_elena.dropna(subset=["Monto_limpio"])
maria_elena["ID"] = range(1, len(maria_elena) + 1)

tabla_me = maria_elena[["ID", "Monto", "Fecha de prestamo", "Abonos", "Notas"]].copy()
tabla_me.columns = ["ID", "Monto", "Fecha", "Abonos", "Notas"]
print(tabla_me.to_string(index=False))
print(f"\nTotal registros: {len(maria_elena)}")
print(f"Total prestado: ${maria_elena['Monto_limpio'].sum():,.2f}")
print(f"Total abonado: ${maria_elena['Abonos'].sum():,.2f}")
print(
    f"Saldo pendiente: ${(maria_elena['Monto_limpio'].sum() - maria_elena['Abonos'].sum()):,.2f}"
)

# 3. TABLA: Datos que Mari registra sobre José Luis
print("\n\n" + "=" * 100)
print("3. LIBRETA DE MARI - REGISTROS SOBRE JOSÉ LUIS")
print("=" * 100)
mari_jose_luis["ID"] = range(1, len(mari_jose_luis) + 1)
tabla_mari_jl = mari_jose_luis[
    ["ID", "monto_deuda", "fecha_Aprox", "Abonos", "notas"]
].copy()
tabla_mari_jl.columns = ["ID", "Monto", "Fecha", "Abonos", "Notas"]
print(tabla_mari_jl.to_string(index=False))
print(f"\nTotal registros: {len(mari_jose_luis)}")
print(f"Total prestado: ${mari_jose_luis['monto_deuda'].sum():,.2f}")
print(f"Total abonado: ${mari_jose_luis['Abonos'].sum():,.2f}")
print(
    f"Saldo pendiente: ${(mari_jose_luis['monto_deuda'].sum() - mari_jose_luis['Abonos'].sum()):,.2f}"
)

# 4. TABLA: Datos que Mari registra sobre María Elena
print("\n\n" + "=" * 100)
print("4. LIBRETA DE MARI - REGISTROS SOBRE MARÍA ELENA")
print("=" * 100)
mari_maria_elena["ID"] = range(1, len(mari_maria_elena) + 1)
tabla_mari_me = mari_maria_elena[
    ["ID", "monto_deuda", "fecha_Aprox", "Abonos", "notas"]
].copy()
tabla_mari_me.columns = ["ID", "Monto", "Fecha", "Abonos", "Notas"]
print(tabla_mari_me.to_string(index=False))
print(f"\nTotal registros: {len(mari_maria_elena)}")
print(f"Total prestado: ${mari_maria_elena['monto_deuda'].sum():,.2f}")
print(f"Total abonado: ${mari_maria_elena['Abonos'].sum():,.2f}")
print(
    f"Saldo pendiente: ${(mari_maria_elena['monto_deuda'].sum() - mari_maria_elena['Abonos'].sum()):,.2f}"
)

# ========== CONSOLIDADO GLOBAL EN CSV ==========
print("\n\n" + "=" * 100)
print("GENERANDO CSV CONSOLIDADO")
print("=" * 100)

# Crear CSV consolidado con todas las fuentes
datos_consolidados = []
id_global = 1

# Agregar datos de José Luis
for idx, row in jose_luis.iterrows():
    datos_consolidados.append(
        {
            "ID_Global": id_global,
            "Fuente": "Libreta José Luis",
            "Persona": "José Luis (Deudor)",
            "Monto": row["Monto_limpio"],
            "Fecha": row["Fecha de prestamo"],
            "Abonos": row["Abonos"] if pd.notna(row["Abonos"]) else 0,
            "Saldo": (
                row["Monto_limpio"] - (row["Abonos"] if pd.notna(row["Abonos"]) else 0)
            ),
            "Notas": row["Notas"] if pd.notna(row["Notas"]) else "Sin notas",
        }
    )
    id_global += 1

# Agregar datos de María Elena
for idx, row in maria_elena.iterrows():
    datos_consolidados.append(
        {
            "ID_Global": id_global,
            "Fuente": "Libreta María Elena",
            "Persona": "María Elena (Deudora)",
            "Monto": row["Monto_limpio"],
            "Fecha": row["Fecha de prestamo"],
            "Abonos": row["Abonos"] if pd.notna(row["Abonos"]) else 0,
            "Saldo": (
                row["Monto_limpio"] - (row["Abonos"] if pd.notna(row["Abonos"]) else 0)
            ),
            "Notas": row["Notas"] if pd.notna(row["Notas"]) else "Sin notas",
        }
    )
    id_global += 1

# Agregar datos de Mari sobre José Luis
for idx, row in mari_jose_luis.iterrows():
    datos_consolidados.append(
        {
            "ID_Global": id_global,
            "Fuente": "Libreta Mari (sobre José Luis)",
            "Persona": "José Luis (según Mari)",
            "Monto": row["monto_deuda"],
            "Fecha": row["fecha_Aprox"],
            "Abonos": row["Abonos"] if pd.notna(row["Abonos"]) else 0,
            "Saldo": (
                row["monto_deuda"] - (row["Abonos"] if pd.notna(row["Abonos"]) else 0)
            ),
            "Notas": row["notas"] if pd.notna(row["notas"]) else "Sin notas",
        }
    )
    id_global += 1

# Agregar datos de Mari sobre María Elena
for idx, row in mari_maria_elena.iterrows():
    datos_consolidados.append(
        {
            "ID_Global": id_global,
            "Fuente": "Libreta Mari (sobre María Elena)",
            "Persona": "María Elena (según Mari)",
            "Monto": row["monto_deuda"],
            "Fecha": row["fecha_Aprox"],
            "Abonos": row["Abonos"] if pd.notna(row["Abonos"]) else 0,
            "Saldo": (
                row["monto_deuda"] - (row["Abonos"] if pd.notna(row["Abonos"]) else 0)
            ),
            "Notas": row["notas"] if pd.notna(row["notas"]) else "Sin notas",
        }
    )
    id_global += 1

# Crear DataFrame consolidado
df_consolidado = pd.DataFrame(datos_consolidados)

# Guardar CSV
csv_path = "/home/xinome/Documentos/Analisis_corregido/Consolidado_Prestamos.csv"
df_consolidado.to_csv(csv_path, index=False)

print(f"✅ CSV consolidado generado: {csv_path}")
print(f"\nPrimeras 10 filas del consolidado:")
print(df_consolidado.head(10).to_string(index=False))

# ========== RESUMEN ESTADÍSTICO ==========
print("\n\n" + "=" * 100)
print("RESUMEN ESTADÍSTICO CONSOLIDADO")
print("=" * 100)

print(f"\nTotal de registros: {len(df_consolidado)}")
print(f"Total prestado consolidado: ${df_consolidado['Monto'].sum():,.2f}")
print(f"Total abonado consolidado: ${df_consolidado['Abonos'].sum():,.2f}")
print(f"Saldo total consolidado: ${df_consolidado['Saldo'].sum():,.2f}")

print("\n📊 Desglose por Fuente:")
for fuente in df_consolidado["Fuente"].unique():
    datos_fuente = df_consolidado[df_consolidado["Fuente"] == fuente]
    print(f"\n  {fuente}:")
    print(f"    • Registros: {len(datos_fuente)}")
    print(f"    • Total prestado: ${datos_fuente['Monto'].sum():,.2f}")
    print(f"    • Total abonado: ${datos_fuente['Abonos'].sum():,.2f}")
    print(f"    • Saldo: ${datos_fuente['Saldo'].sum():,.2f}")

print("\n📊 Desglose por Persona:")
for persona in df_consolidado["Persona"].unique():
    datos_persona = df_consolidado[df_consolidado["Persona"] == persona]
    print(f"\n  {persona}:")
    print(f"    • Registros: {len(datos_persona)}")
    print(f"    • Total prestado: ${datos_persona['Monto'].sum():,.2f}")
    print(f"    • Total abonado: ${datos_persona['Abonos'].sum():,.2f}")
    print(f"    • Saldo: ${datos_persona['Saldo'].sum():,.2f}")

# ========== CRUCE DE DATOS (COINCIDENCIAS Y DISCREPANCIAS) ==========
print("\n\n" + "=" * 100)
print("ANÁLISIS DE COINCIDENCIAS Y DISCREPANCIAS")
print("=" * 100)

# Crear tabla de coincidencias
print("\n✅ MONTOS QUE COINCIDEN (Aparecen en múltiples fuentes):")

# Agrupar por monto
montos_por_fuente = df_consolidado.groupby("Monto")["Fuente"].apply(list)

for monto in sorted(montos_por_fuente.index):
    fuentes = montos_por_fuente[monto]
    if len(set(fuentes)) > 1:  # Si aparece en más de una fuente
        print(f"\n  ${monto:,.2f}:")
        for fuente in set(fuentes):
            count = fuentes.count(fuente)
            print(f"    • {fuente}: {count} registro(s)")

print("\n❌ MONTOS ÚNICOS (Aparecen en solo una fuente):")
for monto in sorted(montos_por_fuente.index):
    fuentes = montos_por_fuente[monto]
    if len(set(fuentes)) == 1:
        print(f"  ${monto:,.2f}: {set(fuentes).pop()}")

print("\n\n✅ Archivos generados:")
print(f"  1. {csv_path}")
print(f"  2. Tamaño: {os.path.getsize(csv_path) / 1024:.1f} KB")
