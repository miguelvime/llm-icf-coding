# -*- coding: utf-8 -*-
"""
===============================================================================
SUITE DE PRUEBAS AUTOMATIZADAS DE REPRODUCIBILIDAD Y PIPELINE (TFM)
===============================================================================
Verifica la integridad de los datos, el analizador universal de historias clínicas,
la coherencia de las métricas de rendimiento y la existencia de artefactos TFL.

Uso:
    python -m unittest tests/test_reproducibilidad.py
    o directamente:
    python tests/test_reproducibilidad.py
===============================================================================
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts" / "analysis"
RESULTS_DIR = BASE_DIR / "results"
TFL_DIR = RESULTS_DIR / "TFL"
DATA_DIR = BASE_DIR / "data"

class TestReproducibilidadTFM(unittest.TestCase):

    def test_01_archivos_clave_del_repositorio(self):
        """Verifica que los archivos esenciales del repositorio existen y son accesibles."""
        archivos_esenciales = [
            BASE_DIR / "analizar_dataset.py",
            BASE_DIR / "README.md",
            BASE_DIR / "requirements.txt",
            BASE_DIR / ".gitignore",
            SCRIPTS_DIR / "ejecutar_todo.py",
            DATA_DIR / "test_data" / "test_codifier_output.json"
        ]
        for f in archivos_esenciales:
            self.assertTrue(f.exists(), f"Falta el archivo esencial: {f.relative_to(BASE_DIR)}")

    def test_02_integridad_datasets_json(self):
        """Valida que todos los datasets JSON sintéticos y humanos son sintácticamente válidos."""
        datasets = [
            DATA_DIR / "test_data" / "test_codifier_output.json",
            RESULTS_DIR / "llm_text" / "2026-08-25-3.7-flash-codified.json",
            RESULTS_DIR / "llm_text" / "2026-08-25-flash-3.5-codified.json",
            RESULTS_DIR / "llm_text" / "2026-08-25_gemma_codified.json",
            RESULTS_DIR / "human_text" / "2026-08-25-flash-3.5-human-annotated.json",
            RESULTS_DIR / "human_text" / "2026-08-25-flash-3.7-human-annotated.json",
            RESULTS_DIR / "human_text" / "2026-08-26-gemma_human_annotated.json"
        ]
        for ds in datasets:
            self.assertTrue(ds.exists(), f"Dataset no encontrado: {ds.name}")
            with open(ds, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertIsInstance(data, list, f"El archivo {ds.name} debe contener una lista de historias")
            self.assertGreater(len(data), 0, f"El archivo {ds.name} está vacío")
            
            # Verificar campos mínimos requeridos
            first = data[0]
            has_codes = any(k in first for k in ["predicted_icf_codes_consensus", "icf_codes", "codes"])
            self.assertTrue(has_codes, f"El archivo {ds.name} no contiene códigos CIF reconocibles")

    def test_03_analizar_dataset_cli(self):
        """Verifica que el script CLI universal 'analizar_dataset.py' ejecuta sin errores y genera informe."""
        script_path = BASE_DIR / "analizar_dataset.py"
        test_data_path = DATA_DIR / "test_data" / "test_codifier_output.json"
        
        cmd = [sys.executable, str(script_path), str(test_data_path), "--nombre", "Test Suite Run"]
        res = subprocess.run(cmd, capture_output=True, text=True)
        
        self.assertEqual(res.returncode, 0, f"Error ejecutando analizar_dataset.py:\n{res.stderr}")
        self.assertIn("ANÁLISIS COMPLETADO", res.stdout)
        
        # Verificar que se generó el dashboard y el informe
        dashboard = TFL_DIR / "dashboard_resumen.html"
        informe = TFL_DIR / "informes" / "INFORME_EJECUTIVO_METRICAS.md"
        self.assertTrue(dashboard.exists(), "No se generó el dashboard HTML")
        self.assertTrue(informe.exists(), "No se generó el informe Markdown")
        self.assertGreater(dashboard.stat().st_size, 1000, "El dashboard HTML está sospechosamente vacío")

    def test_04_coherencia_metricas_f1(self):
        """Verifica que las métricas globales calculadas para el TFM son consistentes con la memoria."""
        # 1. Corpus sintético
        syn_resumen = RESULTS_DIR / "llm_text" / "resumen_f1_score.json"
        self.assertTrue(syn_resumen.exists(), "Falta resumen_f1_score.json")
        with open(syn_resumen, "r", encoding="utf-8") as f:
            syn_data = json.load(f)
        
        modelos_sinteticos = {m.get("modelo_id", m.get("modelo")): m for m in syn_data}
        for mod in ["gemma_31b", "gemini_flash_35", "gemini_flash_37"]:
            self.assertIn(mod, modelos_sinteticos, f"Modelo {mod} ausente en métricas sintéticas")
            f1 = modelos_sinteticos[mod]["metricas"]["micro"]["f1"]
            self.assertGreater(f1, 0.95, f"Micro-F1 anómalo en sintético para {mod}: {f1}")

        # 2. Corpus humano
        hum_resumen = RESULTS_DIR / "human_text" / "resumen_human_annotated.json"
        self.assertTrue(hum_resumen.exists(), "Falta resumen_human_annotated.json")
        with open(hum_resumen, "r", encoding="utf-8") as f:
            hum_data = json.load(f)
            
        for mod in ["gemma_31b", "flash_35", "flash_37"]:
            self.assertIn(mod, hum_data, f"Modelo {mod} ausente en métricas humanas")
            f1 = hum_data[mod]["desempeno"]["micro"]["f1"]
            self.assertGreaterEqual(f1, 0.60, f"Micro-F1 humano demasiado bajo para {mod}: {f1}")
            self.assertLessEqual(f1, 0.85, f"Micro-F1 humano fuera de rango para {mod}: {f1}")

    def test_05_integridad_figuras_tfl(self):
        """Verifica que las figuras clave PNG en 300 DPI están generadas y no están corruptas."""
        figuras_esperadas = [
            "01_comparativa_global_f1_modelos.png",
            "01_comparativa_global_f1_human.png",
            "02_precision_recall_f1_pareado.png",
            "02_precision_recall_f1_pareado_human.png",
            "03_auditoria_per_class_24_codigos.png",
            "03_auditoria_per_class_human.png",
            "04_desempeno_por_capitulo_cif.png",
            "04_desempeno_por_componente_cif_human.png",
            "05_comparativa_sintetico_vs_humano.png",
            "05_matriz_confusion_tp_fp_fn.png",
            "06_ablacion_b280_comparativa_modelos.png",
            "06_eficiencia_estrategias_consenso_f1_human.png",
            "07_ablacion_b280_comparativa_modelos_human.png"
        ]
        carpeta_figuras = TFL_DIR / "figuras"
        for fig in figuras_esperadas:
            p = carpeta_figuras / fig
            self.assertTrue(p.exists(), f"Figura PNG ausente: {fig}")
            self.assertGreater(p.stat().st_size, 20_000, f"Figura PNG corrupta o vacía: {fig}")

    def test_06_integridad_tablas_csv(self):
        """Verifica que las tablas canónicas CSV de resultados existen con encabezados válidos."""
        tablas_esperadas = [
            TFL_DIR / "tablas" / "tabla1_fiabilidad_inter_iteraciones.csv",
            TFL_DIR / "tablas" / "tabla2_matriz_decisiones_binarias.csv",
            TFL_DIR / "tablas" / "tabla_sensibilidad_ablacion.csv",
            TFL_DIR / "tablas" / "tabla_estrategias_consenso_human.csv",
            TFL_DIR / "tablas" / "tabla_sensibilidad_ablacion_human.csv"
        ]
        for t in tablas_esperadas:
            self.assertTrue(t.exists(), f"Tabla CSV ausente: {t.name}")
            with open(t, "r", encoding="utf-8") as f:
                lines = f.readlines()
            self.assertGreater(len(lines), 1, f"Tabla CSV vacía o sin datos: {t.name}")

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" 🧪 EJECUTANDO SUITE DE PRUEBAS DE REPRODUCIBILIDAD (TFM CIF & LLMS)")
    print("=" * 80 + "\n")
    unittest.main(verbosity=2)
