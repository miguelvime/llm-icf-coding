# Repetir el F1 quitando el codigo b280 (dolor), que aparece en casi todas las historias
# Ejecutar desde la carpeta principal del proyecto: python scripts_test/03_ablacion_b280.py

import json
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score

archivos = {
    "Gemma-4-31B-it": "results/llm_text/2026-08-25_gemma_codified.json",
    "Gemini Flash 3.5": "results/llm_text/2026-08-25-flash-3.5-codified.json",
    "Gemini Flash 3.7": "results/llm_text/2026-08-25-3.7-flash-codified.json",
}

codigos = ["b130", "b134", "b147", "b152", "b1602", "b280", "b455", "b730", "b760",
           "d175", "d230", "d240", "d430", "d450", "d640", "d760", "d770", "d850", "d920",
           "e1101", "e310", "e355", "e410", "e570"]


def metricas(historias, lista_codigos):
    mlb = MultiLabelBinarizer(classes=lista_codigos)
    y = mlb.fit_transform([[c for c in h["icf_codes"] if c in lista_codigos] for h in historias])
    p = mlb.fit_transform([[c for c in h["predicted_icf_codes_consensus"] if c in lista_codigos] for h in historias])
    micro = f1_score(y, p, average="micro")
    macro = f1_score(y, p, average="macro", zero_division=0)
    weighted = f1_score(y, p, average="weighted", zero_division=0)
    emr = (y == p).all(axis=1).mean()
    return micro, macro, weighted, emr


sin_b280 = [c for c in codigos if c != "b280"]

for modelo, archivo in archivos.items():
    historias = json.load(open(archivo, encoding="utf-8"))
    con = metricas(historias, codigos)
    sin = metricas(historias, sin_b280)

    print(modelo)
    for nombre, a, b in zip(["Micro-F1", "Macro-F1", "Weighted-F1", "EMR"], con, sin):
        print(f"  {nombre:12} con b280 = {a:.4f}  sin b280 = {b:.4f}  diferencia = {b - a:+.4f}  retencion = {b / a * 100:.2f}%")
