library(jsonlite)
library(irrCAC)

archivos <- list(
  sinteticas = c(
    "Gemini Flash 3.5" = "results/llm_text/2026-08-25-flash-3.5-codified.json",
    "Gemini Flash 3.7" = "results/llm_text/2026-08-25-3.7-flash-codified.json",
    "Gemma-4-31B-it"   = "results/llm_text/2026-08-25_gemma_codified.json"
  ),
  reales = c(
    "Gemini Flash 3.5" = "results/human_text/2026-08-25-flash-3.5-human-annotated.json",
    "Gemini Flash 3.7" = "results/human_text/2026-08-25-flash-3.7-human-annotated.json",
    "Gemma-4-31B-it"   = "results/human_text/2026-08-26-gemma_human_annotated.json"
  )
)

excluidas <- c("002_1", "012_1")

codigos <- c("b130", "b134", "b147", "b152", "b1602", "b280", "b455", "b730", "b760",
             "d175", "d230", "d240", "d430", "d450", "d640", "d760", "d770", "d850", "d920",
             "e1101", "e310", "e355", "e410", "e570")

sin_b280 <- setdiff(codigos, "b280")

leer <- function(corpus) {
  lapply(archivos[[corpus]], function(archivo) {
    d <- fromJSON(archivo)
    if (corpus == "reales") d <- d[!d$id_clinical_text %in% excluidas, ]
    d
  })
}

binarizar <- function(listas, lista_codigos = codigos) {
  m <- t(sapply(listas, function(x) as.integer(lista_codigos %in% x)))
  colnames(m) <- lista_codigos
  m
}

conteos <- function(reales, predichos, lista_codigos = codigos) {
  y <- binarizar(reales, lista_codigos)
  p <- binarizar(predichos, lista_codigos)
  list(soporte = colSums(y),
       tp = colSums(y * p),
       fp = colSums((1 - y) * p),
       fn = colSums(y * (1 - p)),
       exactas = rowSums(y != p) == 0)
}

dividir <- function(a, b) ifelse(b > 0, a / b, 0)

metricas <- function(reales, predichos, lista_codigos = codigos) {
  n <- conteos(reales, predichos, lista_codigos)
  precision <- dividir(n$tp, n$tp + n$fp)
  recall <- dividir(n$tp, n$tp + n$fn)
  f1 <- dividir(2 * n$tp, 2 * n$tp + n$fp + n$fn)
  hay <- n$soporte > 0
  c(precision_micro = sum(n$tp) / sum(n$tp + n$fp),
    recall_micro = sum(n$tp) / sum(n$tp + n$fn),
    micro = 2 * sum(n$tp) / sum(2 * n$tp + n$fp + n$fn),
    precision_macro = mean(precision[hay]),
    recall_macro = mean(recall[hay]),
    macro = mean(f1[hay]),
    precision_weighted = sum(precision * n$soporte) / sum(n$soporte),
    recall_weighted = sum(recall * n$soporte) / sum(n$soporte),
    weighted = sum(f1 * n$soporte) / sum(n$soporte),
    emr = mean(n$exactas))
}

f1_codigo <- function(reales, predichos) {
  n <- conteos(reales, predichos)
  data.frame(codigo = codigos, soporte = n$soporte, tp = n$tp, fp = n$fp, fn = n$fn,
             f1 = dividir(2 * n$tp, 2 * n$tp + n$fp + n$fn))
}

consenso <- function(d, lista_codigos = codigos) {
  metricas(d$icf_codes, d$predicted_icf_codes_consensus, lista_codigos)
}

votar <- function(d, minimo) {
  mapply(function(a, b, c) {
    votos <- table(c(a, b, c))
    names(votos)[votos >= minimo]
  }, d$predicted_icf_it1, d$predicted_icf_it2, d$predicted_icf_it3, SIMPLIFY = FALSE)
}

estrategias <- function(d) {
  list("Iteración 1" = d$predicted_icf_it1,
       "Iteración 2" = d$predicted_icf_it2,
       "Iteración 3" = d$predicted_icf_it3,
       "Consenso 3/3" = votar(d, 3),
       "Mayoría 2/3" = votar(d, 2),
       "Unión 1/3" = votar(d, 1))
}

acuerdo_exacto <- function(d) {
  sum(mapply(function(a, b, c) setequal(a, b) && setequal(b, c),
             d$predicted_icf_it1, d$predicted_icf_it2, d$predicted_icf_it3))
}

fiabilidad <- function(d) {
  votos <- cbind(as.vector(binarizar(d$predicted_icf_it1)),
                 as.vector(binarizar(d$predicted_icf_it2)),
                 as.vector(binarizar(d$predicted_icf_it3)))
  gwet <- gwet.ac1.raw(votos)$est
  kripp <- krippen.alpha.raw(votos)$est
  c(Po = gwet$pa, AC1 = gwet$coeff.val, Alfa = kripp$coeff.val)
}

bootstrap <- function(datos, estadistico, n = 2000) {
  set.seed(2026)
  ids <- unique(datos[[1]]$id_code_combination)
  resultados <- list()
  for (b in 1:n) {
    elegidos <- sample(ids, replace = TRUE)
    for (modelo in names(datos)) {
      d <- datos[[modelo]]
      filas <- unlist(lapply(elegidos, function(g) which(d$id_code_combination == g)))
      resultados[[modelo]] <- rbind(resultados[[modelo]], estadistico(d[filas, ]))
    }
  }
  resultados
}

ic95 <- function(x) quantile(x, c(0.025, 0.975))

comparar <- function(datos, boot) {
  pares <- list(c("Gemma-4-31B-it", "Gemini Flash 3.7"),
                c("Gemma-4-31B-it", "Gemini Flash 3.5"),
                c("Gemini Flash 3.7", "Gemini Flash 3.5"))
  for (par in pares) {
    diferencia <- consenso(datos[[par[1]]])[["micro"]] - consenso(datos[[par[2]]])[["micro"]]
    ic <- ic95(boot[[par[1]]][, "micro"] - boot[[par[2]]][, "micro"])
    cat(par[1], "-", par[2], "=", round(diferencia, 4), " IC 95%:", round(ic, 4),
        ifelse(ic[1] > 0 | ic[2] < 0, " (excluye el 0)", " (incluye el 0)"), "\n")
  }
}
