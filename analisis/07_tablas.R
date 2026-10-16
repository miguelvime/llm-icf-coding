source("analisis/00_comun.R")

sinteticas <- leer("sinteticas")
reales <- leer("reales")

con_ic <- function(valor, ic) sprintf("%.3f [%.3f, %.3f]", valor, ic[1], ic[2])

media_de <- function(x) paste(round(mean(x), 2), "±", round(sd(x), 2))

tabla_fiabilidad <- function(datos) {
  boot <- bootstrap(datos, fiabilidad)
  sapply(names(datos), function(modelo) {
    d <- datos[[modelo]]
    f <- fiabilidad(d)
    ic <- apply(boot[[modelo]], 2, ic95)
    c("Historias" = nrow(d),
      "Acuerdo 3/3" = paste0(acuerdo_exacto(d), "/", nrow(d)),
      "PAE (%)" = round(acuerdo_exacto(d) / nrow(d) * 100, 2),
      "Po (%)" = round(f[["Po"]] * 100, 2),
      "AC1 [IC 95%]" = con_ic(f[["AC1"]], ic[, "AC1"]),
      "Alfa [IC 95%]" = con_ic(f[["Alfa"]], ic[, "Alfa"]))
  })
}

tabla_desempeno <- function(datos) {
  boot <- bootstrap(datos, consenso)
  sapply(names(datos), function(modelo) {
    d <- datos[[modelo]]
    n <- conteos(d$icf_codes, d$predicted_icf_codes_consensus)
    m <- consenso(d)
    ic <- apply(boot[[modelo]], 2, ic95)
    c("TP" = sum(n$tp),
      "FP" = sum(n$fp),
      "FN" = sum(n$fn),
      "EMR" = paste0(sum(n$exactas), "/", nrow(d)),
      "EMR (%)" = round(m[["emr"]] * 100, 2),
      "Precisión micro" = round(m[["precision_micro"]], 3),
      "Sensibilidad micro" = round(m[["recall_micro"]], 3),
      "Micro-F1 [IC 95%]" = con_ic(m[["micro"]], ic[, "micro"]),
      "Precisión macro" = round(m[["precision_macro"]], 3),
      "Sensibilidad macro" = round(m[["recall_macro"]], 3),
      "Macro-F1 [IC 95%]" = con_ic(m[["macro"]], ic[, "macro"]),
      "Precisión weighted" = round(m[["precision_weighted"]], 3),
      "Sensibilidad weighted" = round(m[["recall_weighted"]], 3),
      "Weighted-F1 [IC 95%]" = con_ic(m[["weighted"]], ic[, "weighted"]))
  })
}

n_sinteticas <- lengths(sinteticas[[1]]$icf_codes)
tabla_1 <- c("Textos clínicos" = length(n_sinteticas),
             "Códigos CIF extraídos" = sum(n_sinteticas),
             "Códigos CIF únicos" = length(unique(unlist(sinteticas[[1]]$icf_codes))),
             "Códigos por texto (media ± DE)" = media_de(n_sinteticas),
             "Códigos por texto (mediana)" = median(n_sinteticas))

tabla_4 <- sapply(sinteticas, function(d) {
  m <- sapply(estrategias(d), function(p) metricas(d$icf_codes, p))
  paste0(round(m["micro", ], 4), " (", round(m["emr", ] * 100, 2), "%)")
})
rownames(tabla_4) <- names(estrategias(sinteticas[[1]]))

n_reales <- lengths(reales[[1]]$icf_codes)
tabla_5 <- rbind("Menciones CIF de referencia" = sum(n_reales),
                 "Códigos por historia (media ± DE)" = media_de(n_reales),
                 tabla_fiabilidad(reales),
                 tabla_desempeno(reales))

cat("\nTabla 1. Características del corpus sintético\n")
print(data.frame(Valor = tabla_1))

cat("\nTabla 2. Fiabilidad entre iteraciones (corpus sintético)\n")
print(t(tabla_fiabilidad(sinteticas)), quote = FALSE)

cat("\nTabla 3. Desempeño de la codificación (corpus sintético)\n")
print(tabla_desempeno(sinteticas), quote = FALSE)

cat("\nTabla 4. Micro-F1 (EMR) según la estrategia de consenso (corpus sintético)\n")
print(tabla_4, quote = FALSE)

cat("\nTabla 5. Fiabilidad y desempeño en historias de fisioterapeutas\n")
print(tabla_5, quote = FALSE)
