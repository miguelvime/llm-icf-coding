source("analisis/00_comun.R")

datos <- leer("sinteticas")

for (modelo in names(datos)) {
  d <- datos[[modelo]]
  n <- conteos(d$icf_codes, d$predicted_icf_codes_consensus)

  cat("\n", modelo, "\n", sep = "")
  cat("TP =", sum(n$tp), " FP =", sum(n$fp), " FN =", sum(n$fn), " EMR =", sum(n$exactas), "de", nrow(d), "\n")
  print(round(consenso(d), 4))
  print(f1_codigo(d$icf_codes, d$predicted_icf_codes_consensus), digits = 4, row.names = FALSE)
}

boot <- bootstrap(datos, consenso)

cat("\nIC 95% bootstrap\n")
for (modelo in names(boot)) {
  cat("\n", modelo, "\n", sep = "")
  print(round(apply(boot[[modelo]][, c("micro", "macro", "weighted")], 2, ic95), 3))
}

cat("\nDiferencia de micro-F1\n")
comparar(datos, boot)
