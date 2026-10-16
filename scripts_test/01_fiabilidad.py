# Fiabilidad entre las 3 iteraciones de cada modelo (114 historias x 24 codigos)
# Necesita: pip install irrCAC
# Ejecutar desde la carpeta principal del proyecto: python scripts_test/01_fiabilidad.py

import json
import numpy as np
import pandas as pd
from irrCAC.raw import CAC

archivos = {
    "Gemma-4-31B-it": "results/llm_text/2026-08-25_gemma_codified.json",
    "Gemini Flash 3.5": "results/llm_text/2026-08-25-flash-3.5-codified.json",
    "Gemini Flash 3.7": "results/llm_text/2026-08-25-3.7-flash-codified.json",
}

codigos = ["b130", "b134", "b147", "b152", "b1602", "b280", "b455", "b730", "b760",
           "d175", "d230", "d240", "d430", "d450", "d640", "d760", "d770", "d850", "d920",
           "e1101", "e310", "e355", "e410", "e570"]


def fiabilidad(historias):
    # una fila por (historia, codigo) y una columna por iteracion: 1 si lo pone, 0 si no
    filas = []
    for h in historias:
        for c in codigos:
            filas.append([int(c in h["predicted_icf_it1"]),
                          int(c in h["predicted_icf_it2"]),
                          int(c in h["predicted_icf_it3"])])
    votos = pd.DataFrame(filas, columns=["it1", "it2", "it3"])

    cac = CAC(votos)
    gwet = cac.gwet()["est"]
    kripp = cac.krippendorff()["est"]
    return gwet["pa"], gwet["coefficient_value"], kripp["coefficient_value"]


np.random.seed(2026)

for modelo, archivo in archivos.items():
    historias = json.load(open(archivo, encoding="utf-8"))

    # acuerdo exacto: las 3 iteraciones dan exactamente los mismos codigos
    iguales = 0
    for h in historias:
        if set(h["predicted_icf_it1"]) == set(h["predicted_icf_it2"]) == set(h["predicted_icf_it3"]):
            iguales += 1

    po, ac1, alfa = fiabilidad(historias)

    # bootstrap por combinacion de codigos (2000 veces)
    grupos = {}
    for h in historias:
        grupos.setdefault(h["id_code_combination"], []).append(h)
    ids = list(grupos)

    resultados = []
    for i in range(2000):
        muestra = []
        for g in np.random.choice(ids, len(ids)):
            muestra += grupos[g]
        resultados.append(fiabilidad(muestra))
    ic = np.percentile(resultados, [2.5, 97.5], axis=0)

    print(modelo)
    print("  Acuerdo exacto:", iguales, "/", len(historias), f"({iguales / len(historias) * 100:.2f}%)")
    print(f"  Po    = {po:.4f}  IC95% [{ic[0][0]:.4f}, {ic[1][0]:.4f}]")
    print(f"  AC1   = {ac1:.4f}  IC95% [{ic[0][1]:.4f}, {ic[1][1]:.4f}]")
    print(f"  Alfa  = {alfa:.4f}  IC95% [{ic[0][2]:.4f}, {ic[1][2]:.4f}]")
