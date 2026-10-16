# Analisis de las historias reales escritas por fisioterapeutas (21 historias, quitamos 2 -> 19)
# Fiabilidad, F1 con IC 95%, comparacion pareada y ablacion de b280
# Necesita: pip install irrCAC
# Ejecutar desde la carpeta principal del proyecto: python scripts_test/04_humanos.py

import json
import numpy as np
import pandas as pd
from irrCAC.raw import CAC
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.metrics import f1_score

archivos = {
    "Gemma-4-31B-it": "results/human_text/2026-08-26-gemma_human_annotated.json",
    "Gemini Flash 3.5": "results/human_text/2026-08-25-flash-3.5-human-annotated.json",
    "Gemini Flash 3.7": "results/human_text/2026-08-25-flash-3.7-human-annotated.json",
}

codigos = ["b130", "b134", "b147", "b152", "b1602", "b280", "b455", "b730", "b760",
           "d175", "d230", "d240", "d430", "d450", "d640", "d760", "d770", "d850", "d920",
           "e1101", "e310", "e355", "e410", "e570"]

# estas dos historias se usaron como ejemplo en el prompt, asi que no se cuentan
excluidas = ["002_1", "012_1"]


def f1s(historias, lista_codigos=codigos):
    mlb = MultiLabelBinarizer(classes=lista_codigos)
    y = mlb.fit_transform([[c for c in h["icf_codes"] if c in lista_codigos] for h in historias])
    p = mlb.fit_transform([[c for c in h["predicted_icf_codes_consensus"] if c in lista_codigos] for h in historias])
    micro = f1_score(y, p, average="micro")
    # el macro solo se calcula con los codigos que aparecen en la referencia
    con_soporte = y.sum(axis=0) > 0
    macro = f1_score(y[:, con_soporte], p[:, con_soporte], average="macro", zero_division=0)
    weighted = f1_score(y, p, average="weighted", zero_division=0)
    emr = (y == p).all(axis=1).mean()
    return micro, macro, weighted, emr


datos = {}
for modelo, archivo in archivos.items():
    todas = json.load(open(archivo, encoding="utf-8"))
    datos[modelo] = [h for h in todas if h["id_clinical_text"] not in excluidas]

print("Historias analizadas:", len(datos["Gemma-4-31B-it"]))

# ---- fiabilidad y F1 ----
for modelo, historias in datos.items():
    filas = []
    for h in historias:
        for c in codigos:
            filas.append([int(c in h["predicted_icf_it1"]),
                          int(c in h["predicted_icf_it2"]),
                          int(c in h["predicted_icf_it3"])])
    cac = CAC(pd.DataFrame(filas, columns=["it1", "it2", "it3"]))
    gwet = cac.gwet()["est"]
    alfa = cac.krippendorff()["est"]["coefficient_value"]

    iguales = sum(set(h["predicted_icf_it1"]) == set(h["predicted_icf_it2"]) == set(h["predicted_icf_it3"])
                  for h in historias)

    micro, macro, weighted, emr = f1s(historias)
    s_micro, s_macro, s_weighted, s_emr = f1s(historias, [c for c in codigos if c != "b280"])

    print(modelo)
    print(f"  Acuerdo exacto iteraciones = {iguales}/{len(historias)}  Po = {gwet['pa']:.4f}  "
          f"AC1 = {gwet['coefficient_value']:.4f}  Alfa = {alfa:.4f}")
    print(f"  Micro-F1 = {micro:.4f}  Macro-F1 = {macro:.4f}  Weighted-F1 = {weighted:.4f}  EMR = {emr * 100:.2f}%")
    print(f"  Sin b280: Micro-F1 = {s_micro:.4f}  Macro-F1 = {s_macro:.4f}  Weighted-F1 = {s_weighted:.4f}  EMR = {s_emr * 100:.2f}%")

# ---- bootstrap por combinacion de codigos ----
np.random.seed(2026)
ids = sorted(set(h["id_code_combination"] for h in datos["Gemma-4-31B-it"]))

boot = {modelo: [] for modelo in datos}
for i in range(2000):
    elegidos = np.random.choice(ids, len(ids))
    for modelo, historias in datos.items():
        muestra = [h for g in elegidos for h in historias if h["id_code_combination"] == g]
        boot[modelo].append(f1s(muestra)[:3])

print("\nIC 95% bootstrap (micro, macro, weighted)")
for modelo in datos:
    print(modelo, np.round(np.percentile(boot[modelo], [2.5, 97.5], axis=0), 3).tolist())

print("\nDiferencia de micro-F1 (A - B)")
pares = [("Gemma-4-31B-it", "Gemini Flash 3.7"),
         ("Gemma-4-31B-it", "Gemini Flash 3.5"),
         ("Gemini Flash 3.7", "Gemini Flash 3.5")]
for a, b in pares:
    diferencia = f1s(datos[a])[0] - f1s(datos[b])[0]
    ic = np.percentile(np.array(boot[a])[:, 0] - np.array(boot[b])[:, 0], [2.5, 97.5])
    print(f"  {a} - {b}: {diferencia:+.4f}  IC95% [{ic[0]:+.4f}, {ic[1]:+.4f}]",
          "-> excluye el 0" if ic[0] > 0 or ic[1] < 0 else "-> incluye el 0")
