# -*- coding: utf-8 -*-
"""
===============================================================================
ANÁLISIS ESTADÍSTICO DE DESEMPEÑO Y FIABILIDAD: HISTORIAS CLÍNICAS REALES (N=21)
EVALUACIÓN COMPARATIVA TRI-MODELO: GEMINI FLASH 3.5, GEMINI FLASH 3.7 Y GEMMA-4-31B-IT
===============================================================================
"""

import json
import csv
import random
from pathlib import Path
import numpy as np

BASE_DIR = Path(__file__).resolve().parents[2]
GT_PATH = BASE_DIR / 'data' / 'physio_created_annotated.json'
F35_PATH = BASE_DIR / 'results' / 'human_text' / '2026-08-25-flash-3.5-human-annotated.json'
F37_PATH = BASE_DIR / 'results' / 'human_text' / '2026-08-25-flash-3.7-human-annotated.json'
GEMMA_PATH = BASE_DIR / 'results' / 'human_text' / '2026-08-26-gemma_human_annotated.json'

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

COMPONENTES_CIF = {
    'b': 'Funciones Corporales',
    'd': 'Actividades y Participación',
    'e': 'Factores Ambientales'
}

codigos_cif = sorted(list(DICCIONARIO_CIF.keys()))

# Historias empleadas como ejemplos dentro del prompt codificador: se excluyen
# del análisis para evitar fuga de información (N = 21 -> N = 19).
HISTORIAS_EXCLUIDAS = {'002_1', '012_1'}


def cargar_filtrado(ruta):
    with open(ruta, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    return [d for d in datos if d.get('id_clinical_text') not in HISTORIAS_EXCLUIDAS]


f35_data = cargar_filtrado(F35_PATH)
f37_data = cargar_filtrado(F37_PATH)
gemma_data = cargar_filtrado(GEMMA_PATH)

def calcular_fiabilidad_iteraciones(dataset):
    n_historias = len(dataset)
    exact_matches_iter = 0
    decisiones = []
    
    for item in dataset:
        it1 = set(item.get('predicted_icf_it1', []))
        it2 = set(item.get('predicted_icf_it2', []))
        it3 = set(item.get('predicted_icf_it3', []))
        
        if it1 == it2 == it3:
            exact_matches_iter += 1
            
        for c in codigos_cif:
            v1 = 1 if c in it1 else 0
            v2 = 1 if c in it2 else 0
            v3 = 1 if c in it3 else 0
            decisiones.append([v1, v2, v3])
            
    pae_pct = (exact_matches_iter / n_historias) * 100.0
    n_units = len(decisiones)
    n_raters = 3
    
    po_sum = 0
    for row in decisiones:
        pairs = (row[0] == row[1]) + (row[0] == row[2]) + (row[1] == row[2])
        po_sum += pairs / 3.0
    Po = po_sum / n_units
    
    total_ratings = n_units * n_raters
    count_1 = sum(sum(r) for r in decisiones)
    count_0 = total_ratings - count_1
    p1 = count_1 / total_ratings
    p0 = count_0 / total_ratings
    
    Pe_gwet = 2 * p1 * p0
    ac1 = (Po - Pe_gwet) / (1 - Pe_gwet) if (1 - Pe_gwet) > 0 else 1.0
    
    De = 2 * p0 * p1
    Do = 1 - Po
    alpha = 1 - (Do / De) if De > 0 else 1.0
    
    return {
        'n_historias': n_historias,
        'exact_iter_n': exact_matches_iter,
        'pae_pct': pae_pct,
        'Po': Po,
        'ac1': ac1,
        'alpha': alpha
    }

def evaluar_desempeno(dataset):
    total_tp = 0
    total_fp = 0
    total_fn = 0
    exact = 0
    
    per_class = {c: {'tp': 0, 'fp': 0, 'fn': 0, 'soporte': 0} for c in codigos_cif}
    
    for item in dataset:
        gt = set(item.get('icf_codes', []))
        pred = set(item.get('predicted_icf_codes_consensus', []))
        
        if gt == pred:
            exact += 1
            
        total_tp += len(gt & pred)
        total_fp += len(pred - gt)
        total_fn += len(gt - pred)
        
        for c in codigos_cif:
            in_gt = c in gt
            in_pred = c in pred
            if in_gt and in_pred:
                per_class[c]['tp'] += 1
            elif in_pred and not in_gt:
                per_class[c]['fp'] += 1
            elif in_gt and not in_pred:
                per_class[c]['fn'] += 1
            if in_gt:
                per_class[c]['soporte'] += 1
                
    micro_p = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    micro_r = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    micro_f1 = (2 * micro_p * micro_r / (micro_p + micro_r)) if (micro_p + micro_r) > 0 else 0.0
    
    macro_p_l, macro_r_l, macro_f1_l = [], [], []
    w_p_l, w_r_l, w_f1_l = [], [], []
    tot_sup = sum(v['soporte'] for v in per_class.values())
    
    # Per component breakdown
    comp_metrics = {comp: {'tp': 0, 'fp': 0, 'fn': 0, 'soporte': 0, 'f1_list': []} for comp in ['b', 'd', 'e']}
    
    for c in codigos_cif:
        tp_c = per_class[c]['tp']
        fp_c = per_class[c]['fp']
        fn_c = per_class[c]['fn']
        sup_c = per_class[c]['soporte']
        
        p_c = tp_c / (tp_c + fp_c) if (tp_c + fp_c) > 0 else 0.0
        r_c = tp_c / (tp_c + fn_c) if (tp_c + fn_c) > 0 else 0.0
        f_c = (2 * p_c * r_c / (p_c + r_c)) if (p_c + r_c) > 0 else 0.0
        
        per_class[c]['precision'] = p_c
        per_class[c]['recall'] = r_c
        per_class[c]['f1'] = f_c
        per_class[c]['nombre'] = DICCIONARIO_CIF[c]
        per_class[c]['componente'] = c[0]
        
        comp = c[0]
        comp_metrics[comp]['tp'] += tp_c
        comp_metrics[comp]['fp'] += fp_c
        comp_metrics[comp]['fn'] += fn_c
        comp_metrics[comp]['soporte'] += sup_c
        comp_metrics[comp]['f1_list'].append(f_c)
        
        # Macro solo sobre las categorías con al menos una mención en la referencia
        if sup_c > 0:
            macro_p_l.append(p_c)
            macro_r_l.append(r_c)
            macro_f1_l.append(f_c)

        w_p_l.append(p_c * sup_c)
        w_r_l.append(r_c * sup_c)
        w_f1_l.append(f_c * sup_c)
        
    for comp in ['b', 'd', 'e']:
        tp_k = comp_metrics[comp]['tp']
        fp_k = comp_metrics[comp]['fp']
        fn_k = comp_metrics[comp]['fn']
        p_k = tp_k / (tp_k + fp_k) if (tp_k + fp_k) > 0 else 0.0
        r_k = tp_k / (tp_k + fn_k) if (tp_k + fn_k) > 0 else 0.0
        f1_k = (2 * p_k * r_k / (p_k + r_k)) if (p_k + r_k) > 0 else 0.0
        comp_metrics[comp]['micro_precision'] = p_k
        comp_metrics[comp]['micro_recall'] = r_k
        comp_metrics[comp]['micro_f1'] = f1_k
        comp_metrics[comp]['macro_f1'] = float(np.mean(comp_metrics[comp]['f1_list']))
        
    return {
        'n': len(dataset),
        'exact': exact,
        'emr': exact / len(dataset) * 100.0,
        'tp': total_tp,
        'fp': total_fp,
        'fn': total_fn,
        'soporte': tot_sup,
        'micro': {'p': micro_p, 'r': micro_r, 'f1': micro_f1},
        'macro': {'p': float(np.mean(macro_p_l)), 'r': float(np.mean(macro_r_l)), 'f1': float(np.mean(macro_f1_l))},
        'weighted': {'p': sum(w_p_l)/tot_sup, 'r': sum(w_r_l)/tot_sup, 'f1': sum(w_f1_l)/tot_sup},
        'per_class': per_class,
        'por_componente': comp_metrics
    }

def agrupar_por_combinacion(dataset):
    """Agrupa las historias por combinación de códigos (conglomerado)."""
    clusters = {}
    for item in dataset:
        clusters.setdefault(item['id_code_combination'], []).append(item)
    return clusters


def micro_f1_rapido(dataset):
    """Micro-F1 sin desglose per class (usado en el remuestreo pareado)."""
    tp = fp = fn = 0
    for item in dataset:
        gt = set(item.get('icf_codes', []))
        pred = set(item.get('predicted_icf_codes_consensus', []))
        tp += len(gt & pred)
        fp += len(pred - gt)
        fn += len(gt - pred)
    if tp == 0:
        return 0.0
    prec = tp / (tp + fp)
    rec = tp / (tp + fn)
    return (2 * prec * rec / (prec + rec)) if (prec + rec) > 0 else 0.0


def bootstrap_ci(dataset, n_iter=2000, seed=2026):
    """
    IC 95% por bootstrap percentil por conglomerados: se remuestrean las
    combinaciones de códigos y no las historias individuales, porque las
    historias de una misma combinación comparten los códigos de referencia.
    """
    rng = random.Random(seed)
    clusters = agrupar_por_combinacion(dataset)
    ids_cluster = sorted(clusters)
    micros, macros, weighteds = [], [], []
    for _ in range(n_iter):
        elegidos = [rng.choice(ids_cluster) for _ in range(len(ids_cluster))]
        sample = [h for c in elegidos for h in clusters[c]]
        res = evaluar_desempeno(sample)
        micros.append(res['micro']['f1'])
        macros.append(res['macro']['f1'])
        weighteds.append(res['weighted']['f1'])
    micros.sort()
    macros.sort()
    weighteds.sort()
    return {
        'micro': (micros[int(0.025 * n_iter)], micros[int(0.975 * n_iter)]),
        'macro': (macros[int(0.025 * n_iter)], macros[int(0.975 * n_iter)]),
        'weighted': (weighteds[int(0.025 * n_iter)], weighteds[int(0.975 * n_iter)])
    }


def diferencias_pareadas(datasets_por_modelo, n_iter=2000, seed=2026):
    """
    Prueba de bootstrap pareado sobre la diferencia de Micro-F1 entre modelos:
    en cada iteración se remuestrea el mismo conjunto de conglomerados para
    ambos modelos, de modo que el IC 95% corresponde a δ = Micro-F1(A) − Micro-F1(B).
    """
    pares = [
        ('gemma_31b', 'flash_37'),
        ('gemma_31b', 'flash_35'),
        ('flash_37', 'flash_35'),
    ]
    nombres = {
        'gemma_31b': 'Gemma-4-31B-it',
        'flash_37': 'Gemini Flash 3.7',
        'flash_35': 'Gemini Flash 3.5',
    }

    por_modelo = {
        mid: {h['id_clinical_text']: h for h in datos}
        for mid, datos in datasets_por_modelo.items()
    }
    clusters = {}
    for h in next(iter(datasets_por_modelo.values())):
        clusters.setdefault(h['id_code_combination'], []).append(h['id_clinical_text'])
    ids_cluster = sorted(clusters)

    rng = random.Random(seed)
    muestras_ids = []
    for _ in range(n_iter):
        elegidos = [rng.choice(ids_cluster) for _ in range(len(ids_cluster))]
        muestras_ids.append([tid for c in elegidos for tid in clusters[c]])

    f1_por_iter = {
        mid: [micro_f1_rapido([mapa[tid] for tid in ids]) for ids in muestras_ids]
        for mid, mapa in por_modelo.items()
    }

    comparaciones = []
    for a, b in pares:
        punto = micro_f1_rapido(datasets_por_modelo[a]) - micro_f1_rapido(datasets_por_modelo[b])
        diffs = sorted(x - y for x, y in zip(f1_por_iter[a], f1_por_iter[b]))
        ic_low, ic_high = diffs[int(0.025 * n_iter)], diffs[int(0.975 * n_iter)]
        comparaciones.append({
            'modelo_a': nombres[a],
            'modelo_b': nombres[b],
            'diferencia_micro_f1': punto,
            'ic_95': (ic_low, ic_high),
            'excluye_cero': ic_low > 0 or ic_high < 0
        })
    return comparaciones

if __name__ == '__main__':
    fiab35 = calcular_fiabilidad_iteraciones(f35_data)
    des35 = evaluar_desempeno(f35_data)
    ci35 = bootstrap_ci(f35_data)

    fiab36 = calcular_fiabilidad_iteraciones(f37_data)
    des36 = evaluar_desempeno(f37_data)
    ci36 = bootstrap_ci(f37_data)

    fiab_gemma = calcular_fiabilidad_iteraciones(gemma_data)
    des_gemma = evaluar_desempeno(gemma_data)
    ci_gemma = bootstrap_ci(gemma_data)

    comparaciones = diferencias_pareadas({
        'flash_35': f35_data,
        'flash_37': f37_data,
        'gemma_31b': gemma_data
    })

    print(f'\n[INFO] N analizado = {len(gemma_data)} '
          f'(excluidas {sorted(HISTORIAS_EXCLUIDAS)} como ejemplos del prompt)')
    print('\n▶ COMPARACIÓN PAREADA ENTRE MODELOS (bootstrap pareado por conglomerados; B = 2000)')
    for c in comparaciones:
        ic = f"[{c['ic_95'][0]:+.4f}, {c['ic_95'][1]:+.4f}]"
        conclusion = 'Excluye el cero' if c['excluye_cero'] else 'Incluye el cero'
        print(f"  {c['modelo_a']} − {c['modelo_b']}: "
              f"Δ = {c['diferencia_micro_f1']:+.4f}  IC 95% {ic}  {conclusion}")

    resumen = {
        'n_analizado': len(gemma_data),
        'historias_excluidas': sorted(HISTORIAS_EXCLUIDAS),
        'flash_35': {'fiabilidad': fiab35, 'desempeno': des35, 'ci_95': ci35},
        'flash_37': {'fiabilidad': fiab36, 'desempeno': des36, 'ci_95': ci36},
        'flash_36': {'fiabilidad': fiab36, 'desempeno': des36, 'ci_95': ci36},
        'gemma_31b': {'fiabilidad': fiab_gemma, 'desempeno': des_gemma, 'ci_95': ci_gemma},
        'comparaciones_pareadas': comparaciones
    }

    out_dir = BASE_DIR / 'results' / 'human_text'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / 'resumen_human_annotated.json'
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    print(f'[OK] Resumen tri-modelo guardado en: {out_json}')

    # Export per-class CSV for R flextable and table generator
    csv_path = out_dir / 'tabla_per_class_human.csv'
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'componente_id', 'componente_nombre', 'codigo', 'nombre_categoria', 'soporte_real',
            'f35_tp', 'f35_fp', 'f35_fn', 'f35_prec', 'f35_rec', 'f35_f1',
            'f37_tp', 'f37_fp', 'f37_fn', 'f37_prec', 'f37_rec', 'f37_f1',
            'gemma_tp', 'gemma_fp', 'gemma_fn', 'gemma_prec', 'gemma_rec', 'gemma_f1'
        ])
        for c in codigos_cif:
            comp_id = c[0]
            comp_nom = COMPONENTES_CIF[comp_id]
            nom = DICCIONARIO_CIF[c]
            c35 = des35['per_class'][c]
            c36 = des36['per_class'][c]
            cg = des_gemma['per_class'][c]
            writer.writerow([
                comp_id, comp_nom, c, nom, c35['soporte'],
                c35['tp'], c35['fp'], c35['fn'], round(c35['precision'], 4), round(c35['recall'], 4), round(c35['f1'], 4),
                c36['tp'], c36['fp'], c36['fn'], round(c36['precision'], 4), round(c36['recall'], 4), round(c36['f1'], 4),
                cg['tp'], cg['fp'], cg['fn'], round(cg['precision'], 4), round(cg['recall'], 4), round(cg['f1'], 4)
            ])
    print(f'[OK] CSV tri-modelo per-class guardado en: {csv_path}')
