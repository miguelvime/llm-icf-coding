source("analisis/00_comun.R")

datos <- leer("sinteticas")
boot <- bootstrap(datos, fiabilidad)

for (modelo in names(datos)) {
  d <- datos[[modelo]]
  cat("\n", modelo, "\n", sep = "")
  cat("Acuerdo exacto:", acuerdo_exacto(d), "de", nrow(d), "historias\n")
  print(round(rbind(estimacion = fiabilidad(d), apply(boot[[modelo]], 2, ic95)), 4))
}
