# -*- coding: utf-8 -*-
"""
===============================================================================
GENERACIÓN DE FIGURA: SENSIBILIDAD Y ABLACIÓN DE b280 MULTIMODELO (stats_v4)
CALIDAD DE PUBLICACIÓN CIENTÍFICA (300 DPI, FORMATO APA / EDITORIAL)
Skill: tfl-scientific-figures (Código de colores unificado tri-modelo)
===============================================================================
"""

import json
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[2]
LLM_DIR = BASE_DIR / "results" / "llm_text"
TFL_DIR = BASE_DIR / "results" / "TFL"
CARPETA_FIGURAS = TFL_DIR / "figuras"
RUTA_JSON = LLM_DIR / "resumen_ablacion.json"

os.makedirs(CARPETA_FIGURAS, exist_ok=True)

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 11.5
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['xtick.labelsize'] = 9.5
plt.rcParams['ytick.labelsize'] = 9.5
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['figure.dpi'] = 300

with open(RUTA_JSON, "r", encoding="utf-8") as f:
    datos_abl = json.load(f)

# Paleta tri-modelo estandarizada (tfl-scientific-figures)
COLORES_MODELOS = {
    "gemma_31b": {
        "con": "#E67E22",      # Naranja / Ámbar cálido
        "sin": "#FAD7A0"       # Ámbar suave
    },
    "gemini_flash_37": {
        "con": "#27AE60",      # Verde esmeralda
        "sin": "#A9DFBF"       # Verde menta claro
    },
    "gemini_flash_35": {
        "con": "#2E86C1",      # Azul medio profesional
        "sin": "#AED6F1"       # Azul cielo suave
    }
}

def generar_figura_ablacion_multimodelo():
    """Genera la figura comparativa de ablación de b280 para los 3 modelos sin título integrado."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.6), sharey=True)

    modelos_orden = [
        ("gemma_31b", "Gemma-4-31B-it"),
        ("gemini_flash_37", "Gemini Flash 3.7"),
        ("gemini_flash_35", "Gemini Flash 3.5")
    ]

    metricas = ["Micro-F1", "Macro-F1", "Weighted-F1", "EMR"]

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

        rects1 = ax.bar(x - width/2, val_con, width, label="Completo",
                        color=COLORES_MODELOS[m_id]["con"], edgecolor="black", linewidth=0.7)
        rects2 = ax.bar(x + width/2, val_sin, width, label="Sin b280",
                        color=COLORES_MODELOS[m_id]["sin"], edgecolor="black", linewidth=0.7)

        # Anotación sobre barra completa (máximo 2 decimales)
        for bar in rects1:
            h = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, h + 0.015, f"{h:.2f}",
                    ha="center", va="bottom", fontsize=7.5, color="#333333")

        # Etiquetas de retención porcentual a 1 decimal
        for i, r in enumerate(rects2):
            h = r.get_height()
            ax.text(r.get_x() + r.get_width()/2, h + 0.015, f"{ret[i]:.1f}%",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold", color="#111111")

        ax.set_title(f"{m_nombre}", fontweight="bold", pad=10)
        ax.set_xticks(x)
        ax.set_xticklabels(metricas, fontweight="bold")
        ax.set_ylim(0.70, 1.10)
        ax.grid(axis="y", linestyle=":", alpha=0.6)
        ax.legend(loc="lower left", frameon=True, framealpha=0.9)

        if idx == 0:
            ax.set_ylabel("Puntuación de Rendimiento", fontweight="bold")

    plt.tight_layout()
    out_base = CARPETA_FIGURAS / "06_ablacion_b280_comparativa_modelos"
    plt.savefig(out_base.with_suffix(".png"), dpi=300, bbox_inches="tight")
    plt.savefig(out_base.with_suffix(".pdf"), format="pdf", bbox_inches="tight")
    plt.savefig(out_base.with_suffix(".svg"), format="svg", bbox_inches="tight")
    plt.close()
    print(f"[+] Figura 10 guardada con paleta unificada: {out_base.name}.png / .pdf / .svg")

if __name__ == "__main__":
    generar_figura_ablacion_multimodelo()
