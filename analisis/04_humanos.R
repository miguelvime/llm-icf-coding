source("analisis/00_comun.R")

datos <- leer("reales")
cat("Historias analizadas:", nrow(datos[[1]]), "\n")

for (modelo in names(datos)) {
  d <- datos[[modelo]]
  cat("\n", modelo, "\n", sep = "")
  cat("Acuerdo exacto:", acuerdo_exacto(d), "de", nrow(d), "historias\n")
  print(round(fiabilidad(d), 4))
  print(round(data.frame(con_b280 = consenso(d), sin_b280 = consenso(d, sin_b280)), 4))
}

boot <- bootstrap(datos, consenso)

cat("\nIC 95% bootstrap\n")
for (modelo in names(boot)) {
  cat("\n", modelo, "\n", sep = "")
  print(round(apply(boot[[modelo]][, c("micro", "macro", "weighted")], 2, ic95), 3))
}

cat("\nDiferencia de micro-F1\n")
comparar(datos, boot)
