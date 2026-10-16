source("analisis/00_comun.R")

datos <- leer("sinteticas")

for (modelo in names(datos)) {
  con <- consenso(datos[[modelo]])[c("micro", "macro", "weighted", "emr")]
  sin <- consenso(datos[[modelo]], sin_b280)[c("micro", "macro", "weighted", "emr")]

  cat(modelo, "\n")
  print(round(data.frame(con_b280 = con, sin_b280 = sin, diferencia = sin - con,
                         retencion_pct = sin / con * 100), 4))
}
