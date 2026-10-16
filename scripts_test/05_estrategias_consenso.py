# Comparar formas de juntar las 3 iteraciones: cada iteracion sola, consenso 3/3,
# mayoria 2/3 y union 1/3. Se hace con las historias sinteticas y con las reales.
# Ejecutar desde la carpeta principal del proyecto: python scripts_test/05_estrategias_consenso.py

import json

archivos = {
    "Sinteticas": {
        "Gemma-4-31B-it": "results/llm_text/2026-08-25_gemma_codified.json",
        "Gemini Flash 3.5": "results/llm_text/2026-08-25-flash-3.5-codified.json",
        "Gemini Flash 3.7": "results/llm_text/2026-08-25-3.7-flash-codified.json",
    },
    "Reales": {
        "Gemma-4-31B-it": "results/human_text/2026-08-26-gemma_human_annotated.json",
        "Gemini Flash 3.5": "results/human_text/2026-08-25-flash-3.5-human-annotated.json",
        "Gemini Flash 3.7": "results/human_text/2026-08-25-flash-3.7-human-annotated.json",
    },
}

excluidas = ["002_1", "012_1"]  # ejemplos del prompt, solo se quitan de las reales


def prediccion(h, estrategia):
    it1, it2, it3 = set(h["predicted_icf_it1"]), set(h["predicted_icf_it2"]), set(h["predicted_icf_it3"])
    if estrategia == "Iteracion 1":
        return it1
    if estrategia == "Iteracion 2":
        return it2
    if estrategia == "Iteracion 3":
        return it3
    if estrategia == "Consenso 3/3":
        return it1 & it2 & it3
    if estrategia == "Mayoria 2/3":
        return {c for c in it1 | it2 | it3 if (c in it1) + (c in it2) + (c in it3) >= 2}
    if estrategia == "Union 1/3":
        return it1 | it2 | it3


estrategias = ["Iteracion 1", "Iteracion 2", "Iteracion 3", "Consenso 3/3", "Mayoria 2/3", "Union 1/3"]

for corpus, modelos in archivos.items():
    print("=====", corpus, "=====")
    for modelo, archivo in modelos.items():
        historias = json.load(open(archivo, encoding="utf-8"))
        if corpus == "Reales":
            historias = [h for h in historias if h["id_clinical_text"] not in excluidas]
        print(modelo)
        for e in estrategias:
            tp = fp = fn = exactas = 0
            for h in historias:
                real = set(h["icf_codes"])
                pred = prediccion(h, e)
                tp += len(real & pred)
                fp += len(pred - real)
                fn += len(real - pred)
                exactas += real == pred
            precision = tp / (tp + fp)
            recall = tp / (tp + fn)
            f1 = 2 * precision * recall / (precision + recall)
            print(f"  {e:13} P = {precision:.4f}  R = {recall:.4f}  F1 = {f1:.4f}  EMR = {exactas}/{len(historias)}")
