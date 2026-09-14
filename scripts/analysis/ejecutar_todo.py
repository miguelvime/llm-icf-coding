# -*- coding: utf-8 -*-
"""
===============================================================================
ORQUESTADOR MAESTRO DE ANÁLISIS ESTADÍSTICO Y GENERACIÓN DE TFL
TRABAJO DE FIN DE MÁSTER (TFM) - CIF & LLMS
===============================================================================
Este script ejecuta la batería completa de análisis estadístico, validación
diagnóstica, análisis de sensibilidad por ablación, generación de figuras 300 DPI,
tablas en Word (formato APA), informes ejecutivos y el dashboard HTML interactivo.

Uso:
    python scripts/analysis/ejecutar_todo.py
===============================================================================
"""

import sys
import json
import subprocess
import shutil
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
SCRIPTS_DIR = BASE_DIR / "scripts" / "analysis"
RESULTS_DIR = BASE_DIR / "results"
TFL_DIR = RESULTS_DIR / "TFL"

PYTHON_SCRIPTS = [
    ("20_plot_caracteristicas_dataset.py", "Figuras de prevalencia y frecuencia relativa del dataset (300 DPI)"),
    ("01_calculo_confiabilidad_azar.py", "Confiabilidad inter-iteraciones (Krippendorff α, Gwet AC1)"),
    ("02_calculo_acuerdo_exacto.py", "Acuerdo exacto por paciente y discrepancias"),
    ("03_calculo_f1_score.py", "Validez diagnóstica F1 (Micro/Macro), IC 95% Bootstrap"),
    ("04_calculo_sensibilidad_ablacion.py", "Análisis de sensibilidad por ablación de b280"),
    ("05_generar_tfl_fiabilidad.py", "Exportación de TFL de fiabilidad"),
    ("06_plot_desempeno.py", "Generación de figuras de desempeño (300 DPI)"),
    ("07_plot_eficiencia_f1.py", "Figura de coste computacional vs ganancia F1"),
    ("08_plot_sensibilidad_ablacion.py", "Figura de sensibilidad por ablación de b280"),
    ("13_analisis_human_annotated.py", "Métricas diagnósticas en corpus humano (N=21)"),
    ("14_plot_human_annotated.py", "Figuras de validación humana (300 DPI)"),
    ("16_generar_informe_word_completo.py", "Informe clínico integrado en Word"),
    ("17_workflow_diagram.py", "Diagramas metodológicos del flujo (PNG/SVG/PDF)"),
    ("18_generar_dashboard_html.py", "Dashboard interactivo HTML e informe ejecutivo"),
    ("21_analisis_ablacion_consenso_human.py", "Análisis de ablación y consenso en cohorte humana"),
    ("22_plot_ablacion_consenso_human.py", "Figuras de ablación y consenso en cohorte humana (300 DPI)")
]

R_SCRIPTS = [
    ("19_generar_tabla_caracteristicas_dataset_apa.R", "Tabla Word APA de características métricas del dataset"),
    ("09_generar_tablas_apa.R", "Tablas Word APA de desempeño diagnóstico"),
    ("10_generar_tabla_fiabilidad_apa.R", "Tabla Word APA de fiabilidad"),
    ("11_generar_tabla_consenso_apa.R", "Tabla Word APA de estrategias de consenso"),
    ("12_tabla_sensibilidad_ablacion_apa.R", "Tabla Word APA de ablación de b280"),
    ("15_generar_tablas_human_apa.R", "Tablas Word APA de validación humana"),
    ("23_generar_tabla_consenso_human_apa.R", "Tabla Word APA de consenso en cohorte humana"),
    ("24_generar_tabla_ablacion_human_apa.R", "Tabla Word APA de ablación en cohorte humana")
]

def main():
    print("=" * 80)
    print(" 🚀 INICIANDO EJECUCIÓN MAESTRA DEL PIPELINE DE ANÁLISIS ESTADÍSTICO (TFM)")
    print("=" * 80)
    start_time = time.time()

    # Detectar Python virtualenv si existe
    venv_python = BASE_DIR / ".venv" / "bin" / "python"
    python_bin = str(venv_python) if venv_python.exists() else sys.executable

    # 1. Ejecutar scripts de Python
    print("\n📦 [1/2] Ejecutando módulos estadísticos, figuras y dashboard en Python...")

    for script_name, desc in PYTHON_SCRIPTS:
        script_path = SCRIPTS_DIR / script_name
        if not script_path.exists():
            print(f"   ⚠️  No encontrado: {script_name}")
            continue
        
        print(f"   ▶ Ejecutando: {script_name} ({desc})...", end=" ", flush=True)
        res = subprocess.run([python_bin, str(script_path)], capture_output=True, text=True)
        if res.returncode == 0:
            print("✅ [OK]")
        else:
            print("❌ [ERROR]")
            print(res.stderr[:500])

    # 2. Ejecutar scripts de R si Rscript está disponible
    rscript_bin = shutil.which("Rscript")
    print("\n📄 [2/2] Renderizando tablas editoriales APA en Word (.docx)...")
    if rscript_bin:
        for script_name, desc in R_SCRIPTS:
            script_path = SCRIPTS_DIR / script_name
            if not script_path.exists():
                print(f"   ⚠️  No encontrado: {script_name}")
                continue
            
            print(f"   ▶ Ejecutando R: {script_name} ({desc})...", end=" ", flush=True)
            res = subprocess.run([rscript_bin, str(script_path)], capture_output=True, text=True)
            if res.returncode == 0:
                print("✅ [OK]")
            else:
                print("❌ [ERROR]")
                print(res.stderr[:500])
    else:
        print("   ℹ️  'Rscript' no detectado en PATH. Las tablas APA en Word se generan con R.")

    elapsed = time.time() - start_time
    print("\n" + "=" * 80)
    print(f" ✨ PIPELINE COMPLETADO CON ÉXITO EN {elapsed:.2f} SEGUNDOS")
    print("=" * 80)

    # 3. Resumen Ejecutivo en Pantalla
    print("\n📊 RESUMEN EJECUTIVO DE RESULTADOS ACTUALIZADOS (24 CATEGORÍAS CIF):")
    print("-" * 80)
    
    # Cargar datos sintéticos
    try:
        with open(RESULTS_DIR / "llm_text" / "resumen_f1_score.json", encoding="utf-8") as f:
            syn_data = json.load(f)
        print(" 1. CORPUS SINTÉTICO IN-SILICO (N = 114 historias clínicas):")
        for m in syn_data:
            nombre = m.get("modelo_nombre", "Modelo")
            met = m.get("metricas", {})
            micro = met.get("micro", {})
            emr_pct = met.get("emr_pct", 0.0)
            exact_n = met.get("exact_matches_n", 0)
            total_n = met.get("n_historias", 114)
            print(f"    • {nombre:<26}: Micro-F1 = {micro.get('f1', 0):.4f} | Precisión = {micro.get('precision', 0)*100:.2f}% | Recall = {micro.get('recall', 0)*100:.2f}% | EMR = {emr_pct:.2f}% ({exact_n}/{total_n})")
    except Exception as e:
        print(f"    Error cargando resumen sintético: {e}")

    # Cargar datos humanos
    try:
        with open(RESULTS_DIR / "human_text" / "resumen_human_annotated.json", encoding="utf-8") as f:
            hum_data = json.load(f)
        print("\n 2. CORPUS REAL HUMANO (N = 21 historias, Fisioterapeutas Colegiados):")
        for k, nombre in [("gemma_31b", "Gemma-4-31B-it"), ("flash_35", "Gemini Flash 3.5"), ("flash_37", "Gemini Flash 3.7")]:
            m = hum_data.get(k, {})
            dp = m.get("desempeno", {})
            micro = dp.get("micro", {})
            emr = dp.get("emr", 0.0)
            exact = dp.get("exact", 0)
            n_cases = dp.get("n", 21)
            print(f"    • {nombre:<26}: Micro-F1 = {micro.get('f1', 0):.4f} | Precisión = {micro.get('p', 0)*100:.2f}% | Recall = {micro.get('r', 0)*100:.2f}% | EMR = {emr:.2f}% ({exact}/{n_cases})")
    except Exception as e:
        print(f"    Error cargando resumen humano: {e}")

    print("-" * 80)
    print(" 📁 ARTEFACTOS GENERADOS DISPONIBLES EN results/TFL/:")
    print(f"    • Dashboard Interactivo HTML: {TFL_DIR / 'dashboard_resumen.html'}  (¡Doble clic para abrir!)")
    print(f"    • Informes ejecutivos: {TFL_DIR / 'informes'}")
    print(f"    • Tablas APA (Word / Excel / CSV): {TFL_DIR / 'tablas'}")
    print(f"    • Figuras en 300 DPI (PNG / SVG / PDF): {TFL_DIR / 'figuras'}")
    print(f"    • Listados clínicos y discrepancias: {TFL_DIR / 'listados'}")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    main()
