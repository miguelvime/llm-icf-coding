source("analisis/00_comun.R")

for (corpus in names(archivos)) {
  cat("=====", corpus, "=====\n")
  datos <- leer(corpus)
  for (modelo in names(datos)) {
    d <- datos[[modelo]]
    resultado <- t(sapply(estrategias(d), function(p) metricas(d$icf_codes, p)))

    cat(modelo, "\n")
    print(round(resultado[, c("precision_micro", "recall_micro", "micro", "emr")], 4))
  }
}
