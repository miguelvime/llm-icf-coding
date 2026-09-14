# -*- coding: utf-8 -*-
"""
===============================================================================
ANÁLISIS DE ESTRATEGIAS DE CONSENSO Y ABLACIÓN DE b280 EN HUMANOS (N = 21)
Cálculo de métricas diagnósticas y exportación a JSON y CSV para TFL
===============================================================================
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[2]
GT_PATH = BASE_DIR / "data" / "physio_created_annotated.json"
HUMAN_DIR = BASE_DIR / "results" / "human_text"
TABLAS_DIR = BASE_DIR / "results" / "TFL" / "tablas"

F35_PATH = HUMAN_DIR / "2026-08-25-flash-3.5-human-annotated.json"
F37_PATH = HUMAN_DIR / "2026-08-25-flash-3.7-human-annotated.json"
GEMMA_PATH = HUMAN_DIR / "2026-08-26-gemma_human_annotated.json"

TABLAS_DIR.mkdir(parents=True, exist_ok=True)

# Diccionario Core Set CIF (24 categorías)
DICCIONARIO_CIF = {
    'b130': 'Funciones relacionadas con la energía y los impulsos',
    'b134': 'Funciones del sueño',
    'b147': 'Funciones psicomotoras',
    'b152': 'Funciones emocionales',
    'b1602': 'Contenido del pensamiento',
    'b280': 'Sensación de dolor',
    'b455': 'Tolerancia al ejercicio físico',
    'b730': 'Funciones relacionadas con la fuerza muscular',
    'b760': 'Control de los movimientos voluntarios',
    'd175': 'Resolver problemas',
    'd230': 'Llevar a cabo rutinas diarias',
    'd240': 'Manejo del estrés y demandas psicológicas',
    'd430': 'Levantar y llevar objetos',
    'd450': 'Andar y desplazarse',
    'd640': 'Realizar los quehaceres de la casa',
    'd760': 'Relaciones familiares',
    'd770': 'Relaciones íntimas y sociales',
    'd850': 'Trabajo remunerado',
    'd920': 'Tiempo libre y ocio',
    'e1101': 'Medicamentos',
    'e310': 'Familiares cercanos',
    'e355': 'Profesionales de la salud',
    'e410': 'Actitudes individuales de miembros de la familia cercana',
    'e570': 'Servicios, sistemas y políticas de seguridad social'
}
codigos_cif = sorted(list(DICCIONARIO_CIF.keys()))

with open(GT_PATH, "r", encoding="utf-8") as f: gt_data = json.load(f)
with open(F35_PATH, "r", encoding="utf-8") as f: f35_data = json.load(f)
with open(F37_PATH, "r", encoding="utf-8") as f: f37_data = json.load(f)
with open(GEMMA_PATH, "r", encoding="utf-8") as f: gemma_data = json.load(f)

# -----------------------------------------------------------------------------
# 1. FUNCIONES PARA ESTRATEGIAS DE CONSENSO
# -----------------------------------------------------------------------------
def get_it1(h): return set(h.get('predicted_icf_it1', []))
def get_it2(h): return set(h.get('predicted_icf_it2', []))
def get_it3(h): return set(h.get('predicted_icf_it3', []))

def get_strict_consensus(h):
    return set(h.get('predicted_icf_it1', [])) & set(h.get('predicted_icf_it2', [])) & set(h.get('predicted_icf_it3', []))

def get_majority_voting(h):
    it1 = set(h.get('predicted_icf_it1', []))
    it2 = set(h.get('predicted_icf_it2', []))
    it3 = set(h.get('predicted_icf_it3', []))
    all_codes = it1 | it2 | it3
    return {c for c in all_codes if (c in it1) + (c in it2) + (c in it3) >= 2}

def get_union(h):
    return set(h.get('predicted_icf_it1', [])) | set(h.get('predicted_icf_it2', [])) | set(h.get('predicted_icf_it3', []))

estrategias_consenso = [
    ("Iteración 1", get_it1, "1x (Óptimo)", "Pase Único (1x)"),
    ("Iteración 2", get_it2, "1x", "Pase Único (1x)"),
    ("Iteración 3", get_it3, "1x", "Pase Único (1x)"),
    ("Consenso Estricto (3/3)", get_strict_consensus, "3x", "Consenso Multi-Pase (3x)"),
    ("Voto Mayoritario (≥ 2/3)", get_majority_voting, "3x", "Consenso Multi-Pase (3x)"),
    ("Unión / Sensibilidad (≥ 1/3)", get_union, "3x", "Consenso Multi-Pase (3x)")
]

def evaluar_estrategia(datos, pred_fn):
    total_tp = 0
    total_fp = 0
    total_fn = 0
    exact = 0
    n = len(datos)
    per_class = {c: {'tp': 0, 'fp': 0, 'fn': 0, 'soporte': 0} for c in codigos_cif}

    for item in datos:
        gt = set(item.get('icf_codes', []))
        pred = pred_fn(item)
        if gt == pred:
            exact += 1
        tp = len(gt & pred)
        fp = len(pred - gt)
        fn = len(gt - pred)
        total_tp += tp
        total_fp += fp
        total_fn += fn

        for c in codigos_cif:
            in_gt = c in gt
            in_pred = c in pred
            if in_gt and in_pred: per_class[c]['tp'] += 1
            elif in_pred and not in_gt: per_class[c]['fp'] += 1
            elif in_gt and not in_pred: per_class[c]['fn'] += 1
            if in_gt: per_class[c]['soporte'] += 1

    p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
    emr_pct = exact / n * 100.0

    macro_list, w_list = [], []
    tot_s = sum(v['soporte'] for v in per_class.values())
    for c in codigos_cif:
        tp_c = per_class[c]['tp']
        fp_c = per_class[c]['fp']
        fn_c = per_class[c]['fn']
        s_c = per_class[c]['soporte']
        denom = 2 * tp_c + fp_c + fn_c
        f1_c = (2 * tp_c) / denom if denom > 0 else 0.0
        macro_list.append(f1_c)
        w_list.append(f1_c * s_c)

    macro_f1 = float(np.mean(macro_list))
    weighted_f1 = float(sum(w_list) / tot_s) if tot_s > 0 else 0.0

    return {
        'precision': float(p),
        'recall': float(r),
        'f1': float(f1),
        'macro_f1': float(macro_f1),
        'weighted_f1': float(weighted_f1),
        'emr_pct': float(emr_pct),
        'exact': int(exact),
        'tp': int(total_tp),
        'fp': int(total_fp),
        'fn': int(total_fn),
        'n': int(n)
    }

# -----------------------------------------------------------------------------
# 2. EVALUACIÓN Y EXPORTACIÓN DE ESTRATEGIAS DE CONSENSO
# -----------------------------------------------------------------------------
modelos_map = {
    "gemma": ("Gemma-4-31B-it", gemma_data),
    "flash_35": ("Gemini Flash 3.5", f35_data),
    "flash_37": ("Gemini Flash 3.7", f37_data)
}

resumen_consenso = {}
filas_consenso_csv = []

for est_nombre, est_fn, coste, bloque in estrategias_consenso:
    resumen_consenso[est_nombre] = {
        "bloque": bloque,
        "coste": coste
    }
    fila_csv = {
        "Estrategia inferencia": bloque,
        "Estrategia de Decisión": est_nombre,
        "Coste Relativo": coste
    }

    for m_key, (m_nombre, m_datos) in modelos_map.items():
        met = evaluar_estrategia(m_datos, est_fn)
        resumen_consenso[est_nombre][m_key] = met

        prefijo = "Gemma" if m_key == "gemma" else ("Flash 3.5" if m_key == "flash_35" else "Flash 3.7")
        fila_csv[f"{prefijo} (F1)"] = f"{met['f1']:.4f}"
        fila_csv[f"{prefijo} (EMR)"] = f"{met['emr_pct']:.2f}%"

    filas_consenso_csv.append(fila_csv)

with open(HUMAN_DIR / "resumen_estrategias_consenso_human.json", "w", encoding="utf-8") as f:
    json.dump(resumen_consenso, f, indent=2, ensure_ascii=False)

df_consenso = pd.DataFrame(filas_consenso_csv)
df_consenso.to_csv(TABLAS_DIR / "tabla_estrategias_consenso_human.csv", index=False, encoding="utf-8-sig")
print(" [OK] Estrategias de consenso calculadas y guardadas.")

# -----------------------------------------------------------------------------
# 3. FUNCIONES PARA SENSIBILIDAD Y ABLACIÓN DE b280
# -----------------------------------------------------------------------------
def evaluar_ablacion(datos, exclude_codes=None):
    if exclude_codes is None: exclude_codes = set()
    n = len(datos)
    tp, fp, fn, exact = 0, 0, 0, 0
    total_mentions = 0
    per_class = {c: {'tp': 0, 'fp': 0, 'fn': 0, 'soporte': 0} for c in codigos_cif if c not in exclude_codes}

    for item in datos:
        gt_s = set(c for c in item.get('icf_codes', []) if c not in exclude_codes)
        pred_s = set(c for c in item.get('predicted_icf_codes_consensus', []) if c not in exclude_codes)
        total_mentions += len(gt_s)
        if gt_s == pred_s: exact += 1
        tp += len(gt_s & pred_s)
        fp += len(pred_s - gt_s)
        fn += len(gt_s - pred_s)

        for c in per_class:
            in_gt = c in gt_s
            in_pred = c in pred_s
            if in_gt and in_pred: per_class[c]['tp'] += 1
            elif in_pred and not in_gt: per_class[c]['fp'] += 1
            elif in_gt and not in_pred: per_class[c]['fn'] += 1
            if in_gt: per_class[c]['soporte'] += 1

    p = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    r = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = (2 * p * r) / (p + r) if (p + r) > 0 else 0.0
    emr_pct = exact / n * 100.0

    macro_list, w_list = [], []
    tot_s = sum(v['soporte'] for v in per_class.values())
    for c in per_class:
        tp_c = per_class[c]['tp']
        fp_c = per_class[c]['fp']
        fn_c = per_class[c]['fn']
        s_c = per_class[c]['soporte']
        denom = 2 * tp_c + fp_c + fn_c
        f1_c = (2 * tp_c) / denom if denom > 0 else 0.0
        macro_list.append(f1_c)
        w_list.append(f1_c * s_c)

    macro_f1 = float(np.mean(macro_list))
    weighted_f1 = float(sum(w_list) / tot_s) if tot_s > 0 else 0.0

    return {
        'total_mentions': int(total_mentions),
        'Micro_F1': float(f1),
        'Micro_Precision': float(p),
        'Micro_Recall': float(r),
        'Macro_F1': float(macro_f1),
        'Weighted_F1': float(weighted_f1),
        'EMR': float(exact / n),
        'EMR_pct': float(emr_pct),
        'exact': int(exact),
        'TP': int(tp),
        'FP': int(fp),
        'FN': int(fn)
    }

# -----------------------------------------------------------------------------
# 4. EVALUACIÓN Y EXPORTACIÓN DE ABLACIÓN DE b280
# -----------------------------------------------------------------------------
resumen_ablacion = {}
for m_id, (m_nombre, m_datos) in modelos_map.items():
    completo = evaluar_ablacion(m_datos, exclude_codes=set())
    ablado = evaluar_ablacion(m_datos, exclude_codes={'b280'})

    ret_f1 = (ablado['Micro_F1'] / completo['Micro_F1']) * 100.0
    ret_macro = (ablado['Macro_F1'] / completo['Macro_F1']) * 100.0
    ret_wf1 = (ablado['Weighted_F1'] / completo['Weighted_F1']) * 100.0
    ret_emr = (ablado['EMR'] / completo['EMR']) * 100.0 if completo['EMR'] > 0 else 100.0

    resumen_ablacion[m_id] = {
        "completo": completo,
        "ablado": ablado,
        "delta": {
            "Micro_F1": ablado['Micro_F1'] - completo['Micro_F1'],
            "Macro_F1": ablado['Macro_F1'] - completo['Macro_F1'],
            "Weighted_F1": ablado['Weighted_F1'] - completo['Weighted_F1'],
            "EMR": (ablado['EMR'] - completo['EMR']) * 100.0
        },
        "retencion": {
            "Micro_F1": ret_f1,
            "Macro_F1": ret_macro,
            "Weighted_F1": ret_wf1,
            "EMR": ret_emr
        }
    }

with open(HUMAN_DIR / "resumen_ablacion_human.json", "w", encoding="utf-8") as f:
    json.dump(resumen_ablacion, f, indent=2, ensure_ascii=False)

# Crear tabla CSV idéntica a tabla_sensibilidad_ablacion.csv
filas_ablacion_csv = [
    {"Dimensión": "Parámetros del Espacio", "Métrica / Parámetro": "Número de Categorías CIF evaluadas", "Gemma-4-31B-it": "24 códigos", "Gemini Flash 3.5": "24 códigos", "Gemini Flash 3.7": "24 códigos"},
    {"Dimensión": "Parámetros del Espacio", "Métrica / Parámetro": "Soporte Real Ground Truth (menciones)", "Gemma-4-31B-it": "115", "Gemini Flash 3.5": "115", "Gemini Flash 3.7": "115"},
    {"Dimensión": "Parámetros del Espacio", "Métrica / Parámetro": "Prevalencia de b280 en el Corpus", "Gemma-4-31B-it": "100.0% (21/21)", "Gemini Flash 3.5": "100.0% (21/21)", "Gemini Flash 3.7": "100.0% (21/21)"},

    {"Dimensión": "Espacio Completo (Con b280)", "Métrica / Parámetro": "Micro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['completo']['Micro_F1']:.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['completo']['Micro_F1']:.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['completo']['Micro_F1']:.4f}"},
    {"Dimensión": "Espacio Completo (Con b280)", "Métrica / Parámetro": "Macro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['completo']['Macro_F1']:.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['completo']['Macro_F1']:.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['completo']['Macro_F1']:.4f}"},
    {"Dimensión": "Espacio Completo (Con b280)", "Métrica / Parámetro": "Weighted-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['completo']['Weighted_F1']:.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['completo']['Weighted_F1']:.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['completo']['Weighted_F1']:.4f}"},
    {"Dimensión": "Espacio Completo (Con b280)", "Métrica / Parámetro": "Exact Match Ratio (EMR %)", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['completo']['EMR_pct']:.2f}% (4/21)", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['completo']['EMR_pct']:.2f}% (1/21)", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['completo']['EMR_pct']:.2f}% (2/21)"},
    {"Dimensión": "Espacio Completo (Con b280)", "Métrica / Parámetro": "Matriz de Confusión (TP / FP / FN)", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['completo']['TP']} / {resumen_ablacion['gemma']['completo']['FP']} / {resumen_ablacion['gemma']['completo']['FN']}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['completo']['TP']} / {resumen_ablacion['flash_35']['completo']['FP']} / {resumen_ablacion['flash_35']['completo']['FN']}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['completo']['TP']} / {resumen_ablacion['flash_37']['completo']['FP']} / {resumen_ablacion['flash_37']['completo']['FN']}"},

    {"Dimensión": "Ablación (Sin dolor b280)", "Métrica / Parámetro": "Micro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['ablado']['Micro_F1']:.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['ablado']['Micro_F1']:.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['ablado']['Micro_F1']:.4f}"},
    {"Dimensión": "Ablación (Sin dolor b280)", "Métrica / Parámetro": "Macro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['ablado']['Macro_F1']:.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['ablado']['Macro_F1']:.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['ablado']['Macro_F1']:.4f}"},
    {"Dimensión": "Ablación (Sin dolor b280)", "Métrica / Parámetro": "Weighted-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['ablado']['Weighted_F1']:.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['ablado']['Weighted_F1']:.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['ablado']['Weighted_F1']:.4f}"},
    {"Dimensión": "Ablación (Sin dolor b280)", "Métrica / Parámetro": "Exact Match Ratio (EMR %)", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['ablado']['EMR_pct']:.2f}% (4/21)", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['ablado']['EMR_pct']:.2f}% (1/21)", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['ablado']['EMR_pct']:.2f}% (2/21)"},
    {"Dimensión": "Ablación (Sin dolor b280)", "Métrica / Parámetro": "Matriz de Confusión (TP / FP / FN)", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['ablado']['TP']} / {resumen_ablacion['gemma']['ablado']['FP']} / {resumen_ablacion['gemma']['ablado']['FN']}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['ablado']['TP']} / {resumen_ablacion['flash_35']['ablado']['FP']} / {resumen_ablacion['flash_35']['ablado']['FN']}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['ablado']['TP']} / {resumen_ablacion['flash_37']['ablado']['FP']} / {resumen_ablacion['flash_37']['ablado']['FN']}"},

    {"Dimensión": "Variación Absoluta (Δ = Sin - Con)", "Métrica / Parámetro": "Δ Micro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['delta']['Micro_F1']:+.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['delta']['Micro_F1']:+.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['delta']['Micro_F1']:+.4f}"},
    {"Dimensión": "Variación Absoluta (Δ = Sin - Con)", "Métrica / Parámetro": "Δ Macro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['delta']['Macro_F1']:+.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['delta']['Macro_F1']:+.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['delta']['Macro_F1']:+.4f}"},
    {"Dimensión": "Variación Absoluta (Δ = Sin - Con)", "Métrica / Parámetro": "Δ Weighted-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['delta']['Weighted_F1']:+.4f}", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['delta']['Weighted_F1']:+.4f}", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['delta']['Weighted_F1']:+.4f}"},
    {"Dimensión": "Variación Absoluta (Δ = Sin - Con)", "Métrica / Parámetro": "Δ EMR (%)", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['delta']['EMR']:+.2f}%", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['delta']['EMR']:+.2f}%", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['delta']['EMR']:+.2f}%"},

    {"Dimensión": "Tasa de Retención (%)", "Métrica / Parámetro": "Retención Micro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['retencion']['Micro_F1']:.2f}%", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['retencion']['Micro_F1']:.2f}%", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['retencion']['Micro_F1']:.2f}%"},
    {"Dimensión": "Tasa de Retención (%)", "Métrica / Parámetro": "Retención Macro-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['retencion']['Macro_F1']:.2f}%", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['retencion']['Macro_F1']:.2f}%", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['retencion']['Macro_F1']:.2f}%"},
    {"Dimensión": "Tasa de Retención (%)", "Métrica / Parámetro": "Retención Weighted-F1", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['retencion']['Weighted_F1']:.2f}%", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['retencion']['Weighted_F1']:.2f}%", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['retencion']['Weighted_F1']:.2f}%"},
    {"Dimensión": "Tasa de Retención (%)", "Métrica / Parámetro": "Retención EMR", "Gemma-4-31B-it": f"{resumen_ablacion['gemma']['retencion']['EMR']:.2f}%", "Gemini Flash 3.5": f"{resumen_ablacion['flash_35']['retencion']['EMR']:.2f}%", "Gemini Flash 3.7": f"{resumen_ablacion['flash_37']['retencion']['EMR']:.2f}%"}
]

df_ablacion = pd.DataFrame(filas_ablacion_csv)
df_ablacion.to_csv(TABLAS_DIR / "tabla_sensibilidad_ablacion_human.csv", index=False, encoding="utf-8-sig")
print(" [OK] Análisis de ablación calculado y guardado.")
