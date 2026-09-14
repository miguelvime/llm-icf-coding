# -*- coding: utf-8 -*-
"""
===============================================================================
GENERACIÓN DE FIGURAS CIENTÍFICAS: CONSENSO Y ABLACIÓN DE b280 EN HUMANOS (N=21)
Formatos: PNG (300 DPI), PDF y SVG | Estilo Editorial Biomédico
Skill: tfl-scientific-figures
===============================================================================
"""

import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[2]
HUMAN_DIR = BASE_DIR / "results" / "human_text"
CARPETA_FIGURAS = BASE_DIR / "results" / "TFL" / "figuras"
CARPETA_FIGURAS.mkdir(parents=True, exist_ok=True)

# Configuración tipográfica y de estilo editorial (tfl-scientific-figures)
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11.5
plt.rcParams['axes.labelsize'] = 10.5
plt.rcParams['xtick.labelsize'] = 10.0
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 9.0
plt.rcParams['figure.dpi'] = 300

# -----------------------------------------------------------------------------
# 1. FIGURA: ESTRATEGIAS DE INFERENCIA Y CONSENSO (HUMANO)
# -----------------------------------------------------------------------------
def generar_figura_consenso_human():
    ruta_json = HUMAN_DIR / "resumen_estrategias_consenso_human.json"
    with open(ruta_json, "r", encoding="utf-8") as f:
        cons_data = json.load(f)

    modelos = ["Gemma-4-31B-it", "Gemini Flash 3.5", "Gemini Flash 3.7"]
    mod_keys = ["gemma", "flash_35", "flash_37"]

    estrategias = [
        "Pase Único (K=1, Coste 1x)",
        "Consenso Estricto (3/3, Coste 3x)",
        "Voto Mayoritario (≥ 2/3, Coste 3x)",
        "Unión / Sensibilidad (≥ 1/3, Coste 3x)"
    ]

    json_est_keys = [
        "Iteración 1",
        "Consenso Estricto (3/3)",
        "Voto Mayoritario (≥ 2/3)",
        "Unión / Sensibilidad (≥ 1/3)"
    ]

    filas_f1 = []
    for ek in json_est_keys:
        item = cons_data.get(ek, {})
        vals = [item.get(mk, {}).get("f1", 0.0) for mk in mod_keys]
        filas_f1.append(vals)

    datos_f1 = np.array(filas_f1)

    # Paleta idéntica a la figura sintética (Figura 9)
    colores_estrategias = [
        "#1F4E79",  # Azul oscuro elegante (Pase Único 1x)
        "#2E86C1",  # Azul medio (Consenso Estricto 3/3 3x)
        "#5DADE2",  # Azul claro (Voto Mayoritario ≥ 2/3 3x)
        "#F39C12"   # Ámbar suave (Unión ≥ 1/3 3x)
    ]

    fig, ax = plt.subplots(figsize=(10.5, 5.5))

    x = np.arange(len(modelos))
    ancho_barra = 0.18
    offsets = [-1.5 * ancho_barra, -0.5 * ancho_barra, 0.5 * ancho_barra, 1.5 * ancho_barra]

    for i in range(len(estrategias)):
        vals = datos_f1[i]
        barras = ax.bar(
            x + offsets[i],
            vals,
            width=ancho_barra,
            label=estrategias[i],
            color=colores_estrategias[i],
            alpha=0.92,
            edgecolor="black",
            linewidth=0.7
        )

        # Anotación numérica estricta con MÁXIMO 2 DECIMALES
        for bar in barras:
            y_pos = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2.,
                y_pos + 0.008,
                f"{y_pos:.2f}",
                ha='center',
                va='bottom',
                fontsize=8.5,
                fontweight='bold',
                rotation=90
            )

    ax.set_ylabel("Micro-F1 Score", fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(modelos, fontweight='bold', fontsize=11)
    ax.set_ylim(0.60, 0.85)
    ax.grid(axis='y', linestyle=':', alpha=0.6)

    # Leyenda profesional sin superposición
    ax.legend(
        frameon=True,
        facecolor='#F8F9F9',
        edgecolor='#BDC3C7',
        loc="lower right"
    )

    plt.tight_layout()

    out_base = CARPETA_FIGURAS / "06_eficiencia_estrategias_consenso_f1_human"
    plt.savefig(out_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.savefig(out_base.with_suffix(".pdf"), format="pdf", bbox_inches="tight")
    plt.savefig(out_base.with_suffix(".svg"), format="svg", bbox_inches="tight")
    plt.close()
    print(f" [OK] Figura de consenso en humanos guardada en:\n      - {out_base.name}.png / .pdf / .svg")

# -----------------------------------------------------------------------------
# 2. FIGURA: SENSIBILIDAD Y ABLACIÓN DE b280 (HUMANO)
# -----------------------------------------------------------------------------
def generar_figura_ablacion_human():
    ruta_json = HUMAN_DIR / "resumen_ablacion_human.json"
    with open(ruta_json, "r", encoding="utf-8") as f:
        datos_abl = json.load(f)

    # Paleta tri-modelo unificada (tfl-scientific-figures)
    COLORES_MODELOS = {
        "gemma": {
            "con": "#E67E22",      # Naranja cálido
            "sin": "#FAD7A0"       # Ámbar claro suave
        },
        "flash_37": {
            "con": "#27AE60",      # Verde esmeralda
            "sin": "#A9DFBF"       # Verde menta claro
        },
        "flash_35": {
            "con": "#2E86C1",      # Azul medio profesional
            "sin": "#AED6F1"       # Azul cielo suave
        }
    }

    modelos_orden = [
        ("gemma", "Gemma-4-31B-it"),
        ("flash_37", "Gemini Flash 3.7"),
        ("flash_35", "Gemini Flash 3.5")
    ]

    metricas = ["Micro-F1", "Macro-F1", "Weighted-F1", "EMR"]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8), sharey=True)

    for idx, (m_id, m_nombre) in enumerate(modelos_orden):
        ax = axes[idx]
        m_data = datos_abl[m_id]

        val_con = [
            m_data["completo"]["Micro_F1"],
            m_data["completo"]["Macro_F1"],
            m_data["completo"]["Weighted_F1"],
            m_data["completo"]["EMR"]
        ]

        val_sin = [
            m_data["ablado"]["Micro_F1"],
            m_data["ablado"]["Macro_F1"],
            m_data["ablado"]["Weighted_F1"],
            m_data["ablado"]["EMR"]
        ]

        ret = [
            m_data["retencion"]["Micro_F1"],
            m_data["retencion"]["Macro_F1"],
            m_data["retencion"]["Weighted_F1"],
            m_data["retencion"]["EMR"]
        ]

        x = np.arange(len(metricas))
        width = 0.35

        rects1 = ax.bar(
            x - width/2, val_con, width, label="Completo",
            color=COLORES_MODELOS[m_id]["con"], edgecolor="black", linewidth=0.7
        )
        rects2 = ax.bar(
            x + width/2, val_sin, width, label="Sin b280",
            color=COLORES_MODELOS[m_id]["sin"], edgecolor="black", linewidth=0.7
        )

        # Etiquetas numéricas de retención porcentual con MÁXIMO 2 DECIMALES (1 decimal estándar para %)
        for i, r in enumerate(rects2):
            h = r.get_height()
            ax.text(
                r.get_x() + r.get_width() / 2, h + 0.018, f"{ret[i]:.1f}%",
                ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#111111"
            )

        # Anotación en las barras completas con valor a 2 decimales
        for bar in rects1:
            h = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2, h + 0.018, f"{h:.2f}",
                ha="center", va="bottom", fontsize=7.5, color="#333333"
            )

        # Título limpio del subplot (sin sufijos entre paréntesis)
        ax.set_title(f"{m_nombre}", fontweight="bold", pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(metricas, fontweight="bold")
        ax.set_ylim(0.0, 0.92)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", frameon=True, framealpha=0.9)

        if idx == 0:
            ax.set_ylabel("Puntuación de Rendimiento", fontweight="bold")

    plt.tight_layout()

    out_base = CARPETA_FIGURAS / "07_ablacion_b280_comparativa_modelos_human"
    plt.savefig(out_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.savefig(out_base.with_suffix(".pdf"), format="pdf", bbox_inches="tight")
    plt.savefig(out_base.with_suffix(".svg"), format="svg", bbox_inches="tight")
    plt.close()
    print(f" [OK] Figura de ablación en humanos guardada en:\n      - {out_base.name}.png / .pdf / .svg")

if __name__ == "__main__":
    generar_figura_consenso_human()
    generar_figura_ablacion_human()
    print(" [EXITO] Todas las figuras de validación clínica humana generadas.")
