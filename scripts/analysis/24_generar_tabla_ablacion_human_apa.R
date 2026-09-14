# -*- coding: utf-8 -*-
suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(flextable)
  library(officer)
  library(magrittr)
})

base_dir <- "/home/miguelvime/projects/2026-03-11_TFM"
tablas_dir <- file.path(base_dir, "results", "TFL", "tablas")
ruta_csv <- file.path(tablas_dir, "tabla_sensibilidad_ablacion_human.csv")
ruta_docx <- file.path(tablas_dir, "tabla_sensibilidad_ablacion_human_apa.docx")

df_datos <- read_csv(ruta_csv, show_col_types = FALSE)

border_main <- fp_border(color = "#222222", width = 1.5)
border_sub  <- fp_border(color = "#444444", width = 0.8)

ft <- flextable(df_datos) %>%
  set_header_labels(
    `Dimensión` = "Dimensión",
    `Métrica / Parámetro` = "Métrica / Parámetro",
    `Gemma-4-31B-it` = "Gemma-4-31B-it",
    `Gemini Flash 3.5` = "Gemini Flash 3.5",
    `Gemini Flash 3.7` = "Gemini Flash 3.7"
  ) %>%
  merge_v(j = 1) %>%
  valign(j = 1, valign = "top") %>%
  italic(j = 1) %>%
  bold(part = "header") %>%
  align(j = 1:2, align = "left", part = "all") %>%
  align(j = 3:5, align = "center", part = "all") %>%
  border_remove() %>%
  hline_top(part = "header", border = border_main) %>%
  hline_bottom(part = "header", border = border_sub) %>%
  hline_bottom(part = "body", border = border_main) %>%
  hline(i = c(3, 8, 13, 17), border = border_sub) %>%
  padding(padding.top = 4, padding.bottom = 4, padding.left = 6, padding.right = 6, part = "all") %>%
  fontsize(size = 9.0, part = "all") %>%
  fontsize(size = 9.5, part = "header") %>%
  font(fontname = "Times New Roman", part = "all") %>%
  autofit()

doc <- read_docx() %>%
  body_add_par("Validación Clínica con Fisioterapeutas: Análisis de Sensibilidad y Ablación de la Categoría Dominante (b280)", style = "heading 2") %>%
  body_add_par("Evaluación comparativa del rendimiento diagnóstico en historias clínicas de fisioterapeutas (N = 21) antes y después de excluir el código de dolor (b280).", style = "Normal") %>%
  body_add_flextable(ft) %>%
  body_add_par("Nota. N = 21 historias clínicas narradas libremente por fisioterapeutas colegiados. La tasa de retención se define como [Métrica (Sin b280) / Métrica (Con b280)] × 100.", style = "Normal")

print(doc, target = ruta_docx)
cat(" [OK] Tabla APA de ablación en humanos guardada en:\n      -", ruta_docx, "\n")
