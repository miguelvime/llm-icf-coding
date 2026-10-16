# F1 de cada modelo (consenso 3/3) frente a los codigos reales, con IC 95% bootstrap
# y comparacion pareada entre modelos
# Ejecutar desde la carpeta principal del proyecto: python scripts_test/02_f1_score.py

import json
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score, precision_score, recall_score

archivos = {
    "Gemma-4-31B-it": "results/llm_text/2026-08-25_gemma_codified.json",
    "Gemini Flash 3.5": "results/llm_text/2026-08-25-flash-3.5-codified.json",
    "Gemini Flash 3.7": "results/llm_text/2026-08-25-3.7-flash-codified.json",
}

codigos = ["b130", "b134", "b147", "b152", "b1602", "b280", "b455", "b730", "b760",
           "d175", "d230", "d240", "d430", "d450", "d640", "d760", "d770", "d850", "d920",
           "e1101", "e310", "e355", "e410", "e570"]

mlb = MultiLabelBinarizer(classes=codigos)


def binarizar(historias):
    y = mlb.fit_transform([h["icf_codes"] for h in historias])
    p = mlb.fit_transform([h["predicted_icf_codes_consensus"] for h in historias])
    return y, p


datos = {}
for modelo, archivo in archivos.items():
    datos[modelo] = json.load(open(archivo, encoding="utf-8"))

# ---- metricas de cada modelo ----
for modelo, historias in datos.items():
    y, p = binarizar(historias)
    print(modelo)
    print("  TP =", (y * p).sum(), " FP =", ((1 - y) * p).sum(), " FN =", (y * (1 - p)).sum())
    print("  EMR =", (y == p).all(axis=1).sum(), "/", len(y))
    print(f"  Precision micro = {precision_score(y, p, average='micro'):.4f}")
    print(f"  Recall micro    = {recall_score(y, p, average='micro'):.4f}")
    for tipo in ["micro", "macro", "weighted"]:
        print(f"  F1 {tipo} = {f1_score(y, p, average=tipo, zero_division=0):.4f}")
    print("  F1 por codigo:")
    f1_codigos = f1_score(y, p, average=None, zero_division=0)
    for c, f in zip(codigos, f1_codigos):
        print(f"    {c}: {f:.4f}  (soporte {y[:, codigos.index(c)].sum()})")

# ---- bootstrap por combinacion de codigos (mismas muestras para los 3 modelos) ----
np.random.seed(2026)
ids = sorted(set(h["id_code_combination"] for h in datos["Gemma-4-31B-it"]))

boot = {modelo: [] for modelo in datos}
for i in range(2000):
    elegidos = np.random.choice(ids, len(ids))
    for modelo, historias in datos.items():
        muestra = [h for g in elegidos for h in historias if h["id_code_combination"] == g]
        y, p = binarizar(muestra)
        boot[modelo].append([f1_score(y, p, average=t, zero_division=0) for t in ["micro", "macro", "weighted"]])

print("\nIC 95% bootstrap (micro, macro, weighted)")
for modelo in datos:
    ic = np.percentile(boot[modelo], [2.5, 97.5], axis=0)
    print(modelo, np.round(ic, 3).tolist())

# ---- comparacion pareada de micro-F1 ----
print("\nDiferencia de micro-F1 (A - B)")
pares = [("Gemma-4-31B-it", "Gemini Flash 3.7"),
         ("Gemma-4-31B-it", "Gemini Flash 3.5"),
         ("Gemini Flash 3.7", "Gemini Flash 3.5")]
for a, b in pares:
    ya, pa = binarizar(datos[a])
    yb, pb = binarizar(datos[b])
    diferencia = f1_score(ya, pa, average="micro") - f1_score(yb, pb, average="micro")
    difs = np.array(boot[a])[:, 0] - np.array(boot[b])[:, 0]
    ic = np.percentile(difs, [2.5, 97.5])
    print(f"  {a} - {b}: {diferencia:+.4f}  IC95% [{ic[0]:+.4f}, {ic[1]:+.4f}]",
          "-> excluye el 0" if ic[0] > 0 or ic[1] < 0 else "-> incluye el 0")
