# -*- coding: utf-8 -*-
suppressPackageStartupMessages({
  library(dplyr)
  library(flextable)
  library(officer)
  library(magrittr)
  library(readr)
})

base_dir <- "/home/miguelvime/projects/2026-03-11_TFM"
tablas_dir <- file.path(base_dir, "results", "TFL", "tablas")
ruta_csv <- file.path(tablas_dir, "tabla_estrategias_consenso_human.csv")
ruta_docx <- file.path(tablas_dir, "tabla_estrategias_consenso_human_apa.docx")

df_datos <- read_csv(ruta_csv, show_col_types = FALSE)

border_main <- fp_border(color = "#222222", width = 1.5)
border_sub  <- fp_border(color = "#444444", width = 0.8)

ft <- flextable(df_datos) %>%
  set_header_labels(
    `Estrategia inferencia` = "Estrategia inferencia",
    `Estrategia de Decisión` = "Estrategia de Decisión",
    `Coste Relativo` = "Coste Relativo",
    `Gemma (F1)` = "Gemma (F1)",
    `Gemma (EMR)` = "Gemma (EMR)",
    `Flash 3.5 (F1)` = "Flash 3.5 (F1)",
    `Flash 3.5 (EMR)` = "Flash 3.5 (EMR)",
    `Flash 3.7 (F1)` = "Flash 3.7 (F1)",
    `Flash 3.7 (EMR)` = "Flash 3.7 (EMR)"
  ) %>%
  merge_v(j = "Estrategia inferencia") %>%
  valign(j = "Estrategia inferencia", valign = "top") %>%
  italic(j = "Estrategia inferencia") %>%
  bold(part = "header") %>%
  align(j = 1:2, align = "left", part = "all") %>%
  align(j = 3:9, align = "center", part = "all") %>%
  border_remove() %>%
  hline_top(part = "header", border = border_main) %>%
  hline_bottom(part = "header", border = border_sub) %>%
  hline_bottom(part = "body", border = border_main) %>%
  hline(i = 3, border = border_sub) %>%
  padding(padding.top = 4.5, padding.bottom = 4.5, padding.left = 5, padding.right = 5, part = "all") %>%
  fontsize(size = 9.0, part = "body") %>%
  fontsize(size = 9.5, part = "header") %>%
  font(fontname = "Times New Roman", part = "all") %>%
  width(j = 1, width = 1.25) %>%
  width(j = 2, width = 1.70) %>%
  width(j = 3, width = 0.85) %>%
  width(j = 4:9, width = 0.60)

doc <- read_docx() %>%
  body_add_par("Validación Clínica con Fisioterapeutas: Eficiencia Computacional y Estrategias de Inferencia", style = "heading 1") %>%
  body_add_par("Tabla . Análisis de eficiencia computacional y rendimiento diagnóstico según la estrategia de inferencia en el corpus de historias clínicas humanas (N = 21).", style = "Normal") %>%
  body_add_flextable(ft) %>%
  body_add_par("Nota. K: Número de pasadas o ejecuciones independientes por historia clínica. F1: Puntuación Micro-F1 frente al Ground Truth de fisioterapeutas (N = 21, 115 menciones reales). EMR: Exact Match Ratio (% de concordancia exacta perfecta multietiqueta). 1x (Óptimo): Menor latencia temporal y consumo de inferencia.", style = "Normal")

print(doc, target = ruta_docx)
cat(" [OK] Tabla APA de consenso en humanos guardada en:\n      -", ruta_docx, "\n")
