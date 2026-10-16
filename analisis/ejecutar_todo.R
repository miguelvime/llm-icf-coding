scripts <- c("01_fiabilidad.R", "02_f1_score.R", "03_ablacion_b280.R", "04_humanos.R",
             "05_estrategias_consenso.R", "06_figuras.R", "07_tablas.R")

sink("results/resultados.txt", split = TRUE)
for (script in scripts) {
  cat("\n=====", script, "=====\n")
  source(file.path("analisis", script))
}
sink()
