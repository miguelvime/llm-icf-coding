source("analisis/00_comun.R")
library(ggplot2)
library(dplyr)
library(scales)
library(patchwork)

sinteticas <- leer("sinteticas")
reales <- leer("reales")

dir.create("results/figuras", showWarnings = FALSE)

colores <- c("Gemini Flash 3.5" = "#4A90C8", "Gemini Flash 3.7" = "#41B36E", "Gemma-4-31B-it" = "#E88A3A")
principales <- c("micro", "macro", "weighted", "emr")
etiquetas <- c("Micro-F1", "Macro-F1", "Weighted-F1", "EMR")

nombres <- unique(unlist(fromJSON("data/generator_input.json")$icf_name))
names(nombres) <- sub("-.*", "", nombres)

theme_set(theme_classic(base_size = 10) +
            theme(legend.position = "bottom", legend.title = element_blank()))

guardar <- function(figura, archivo, ancho = 18, alto = 10) {
  ggsave(file.path("results/figuras", archivo), figura, width = ancho, height = alto, units = "cm", dpi = 300)
}

tabla_metricas <- function(datos, lista_codigos = codigos) {
  tabla <- data.frame()
  for (modelo in names(datos)) {
    m <- consenso(datos[[modelo]], lista_codigos)
    tabla <- rbind(tabla, data.frame(modelo, metrica = names(m), valor = m))
  }
  tabla
}

figura_frecuencia <- function(tabla, total, titulo) {
  ggplot(tabla, aes(reorder(codigo, -n), n / total, fill = codigo == "b280")) +
    geom_col() +
    geom_text(aes(label = percent(n / total, accuracy = 0.1)), angle = 90, hjust = -0.2, size = 2.5) +
    scale_fill_manual(values = c("#3B82F6", "#9CC3F5"), guide = "none") +
    scale_y_continuous(labels = percent, expand = expansion(mult = c(0, 0.15))) +
    labs(x = "Código CIF", y = titulo) +
    theme(axis.text.x = element_text(angle = 90, vjust = 0.5))
}

figura_global <- function(datos) {
  boot <- bootstrap(datos, consenso)
  tabla <- data.frame()
  for (modelo in names(datos)) {
    m <- consenso(datos[[modelo]])
    ic <- apply(boot[[modelo]], 2, ic95)
    tabla <- rbind(tabla, data.frame(modelo, metrica = names(m), valor = m, inf = ic[1, ], sup = ic[2, ]))
  }
  tabla <- filter(tabla, metrica %in% principales)
  tabla$metrica <- factor(tabla$metrica, levels = principales, labels = etiquetas)

  ggplot(tabla, aes(metrica, valor, fill = modelo)) +
    geom_col(position = "dodge") +
    geom_errorbar(aes(ymin = inf, ymax = sup), position = position_dodge(0.9), width = 0.3) +
    geom_text(aes(y = sup, label = number(valor, accuracy = 0.01)),
              position = position_dodge(0.9), vjust = -0.5, size = 2.5) +
    scale_fill_manual(values = colores) +
    labs(x = NULL, y = "Puntuación")
}

figura_por_codigo <- function(datos) {
  tabla <- data.frame()
  for (modelo in names(datos)) {
    d <- datos[[modelo]]
    tabla <- rbind(tabla, data.frame(modelo, f1_codigo(d$icf_codes, d$predicted_icf_codes_consensus)))
  }
  tabla <- filter(tabla, soporte > 0)
  tabla$etiqueta <- paste0(substr(nombres[tabla$codigo], 1, 50), " (n=", tabla$soporte, ")")
  tabla$etiqueta <- factor(tabla$etiqueta, levels = rev(unique(tabla$etiqueta)))

  ggplot(tabla, aes(f1, etiqueta, fill = modelo)) +
    geom_col(position = "dodge") +
    scale_fill_manual(values = colores) +
    labs(x = "F1", y = NULL)
}

figura_estrategias <- function(datos) {
  tabla <- data.frame()
  for (modelo in names(datos)) {
    d <- datos[[modelo]]
    f1 <- sapply(estrategias(d), function(p) metricas(d$icf_codes, p)[["micro"]])
    pase_unico <- f1[c("Iteración 1", "Iteración 2", "Iteración 3")]
    tabla <- rbind(tabla, data.frame(
      modelo,
      estrategia = c("Pase único (media de 3)", "Consenso 3/3", "Mayoría 2/3", "Unión 1/3"),
      valor = c(mean(pase_unico), f1["Consenso 3/3"], f1["Mayoría 2/3"], f1["Unión 1/3"]),
      de = c(sd(pase_unico), NA, NA, NA)))
  }
  tabla$estrategia <- factor(tabla$estrategia, levels = unique(tabla$estrategia))

  ggplot(tabla, aes(modelo, valor, fill = estrategia)) +
    geom_col(position = "dodge") +
    geom_errorbar(aes(ymin = valor - de, ymax = valor + de), position = position_dodge(0.9),
                  width = 0.3, na.rm = TRUE) +
    geom_text(aes(label = number(valor, accuracy = 0.01)), position = position_dodge(0.9), vjust = -0.5, size = 2.5) +
    scale_fill_manual(values = c("#2C4F6E", "#3E8EC4", "#8FC1E6", "#F0A030")) +
    labs(x = NULL, y = "Micro-F1")
}

figura_ablacion <- function(datos) {
  con <- filter(tabla_metricas(datos), metrica %in% principales)
  sin <- filter(tabla_metricas(datos, sin_b280), metrica %in% principales)
  con$version <- "Completo"
  sin$version <- "Sin b280"
  con$etiqueta <- number(con$valor, accuracy = 0.01)
  sin$etiqueta <- ifelse(con$valor > 0, percent(sin$valor / con$valor, accuracy = 0.1), "n/a")
  tabla <- rbind(con, sin)
  tabla$metrica <- factor(tabla$metrica, levels = principales, labels = etiquetas)

  ggplot(tabla, aes(metrica, valor, fill = version)) +
    geom_col(position = "dodge") +
    geom_text(aes(label = etiqueta), position = position_dodge(0.9), vjust = -0.5, size = 2.2) +
    facet_wrap(~ modelo) +
    scale_fill_manual(values = c("#4A90C8", "#B8D4EA")) +
    labs(x = NULL, y = "Puntuación")
}

frecuencias <- count(data.frame(codigo = unlist(sinteticas[[1]]$icf_codes)), codigo)
sin_dolor <- filter(frecuencias, codigo != "b280")

guardar(figura_frecuencia(frecuencias, nrow(sinteticas[[1]]), "Historias con el código"), "figura_03.png")
guardar(figura_frecuencia(frecuencias, sum(frecuencias$n), "Frecuencia relativa"), "figura_04.png")
guardar(figura_frecuencia(sin_dolor, sum(sin_dolor$n), "Frecuencia relativa"), "figura_05.png")

guardar(figura_global(sinteticas), "figura_07.png")
guardar(figura_por_codigo(sinteticas), "figura_08.png", alto = 22)
guardar(figura_estrategias(sinteticas), "figura_09.png")
guardar(figura_ablacion(sinteticas), "figura_10.png", ancho = 24)

guardar(figura_global(reales), "figura_11.png")

desglose <- filter(tabla_metricas(reales), grepl("micro|macro", metrica))
desglose$nivel <- factor(ifelse(grepl("macro", desglose$metrica), "Macro", "Micro"), levels = c("Micro", "Macro"))
desglose$medida <- case_when(grepl("precision", desglose$metrica) ~ "Precisión",
                             grepl("recall", desglose$metrica) ~ "Sensibilidad",
                             TRUE ~ "F1")
desglose$medida <- factor(desglose$medida, levels = c("Precisión", "Sensibilidad", "F1"))

figura_12 <- ggplot(desglose, aes(medida, valor, fill = modelo)) +
  geom_col(position = "dodge") +
  geom_text(aes(label = number(valor, accuracy = 0.01)), position = position_dodge(0.9), vjust = -0.5, size = 2.5) +
  facet_wrap(~ nivel) +
  scale_fill_manual(values = colores) +
  labs(x = NULL, y = "Puntuación")
guardar(figura_12, "figura_12.png", ancho = 22)

guardar(figura_por_codigo(reales), "figura_13.png", alto = 20)

componentes <- data.frame()
for (letra in c("b", "d", "e")) {
  micro <- filter(tabla_metricas(reales, codigos[startsWith(codigos, letra)]), metrica == "micro")
  componentes <- rbind(componentes, data.frame(micro, componente = letra))
}
componentes$componente <- factor(componentes$componente, levels = c("b", "d", "e"),
                                 labels = c("Funciones corporales (b)", "Actividades y participación (d)",
                                            "Factores ambientales (e)"))

figura_14 <- ggplot(componentes, aes(componente, valor, fill = modelo)) +
  geom_col(position = "dodge") +
  geom_text(aes(label = number(valor, accuracy = 0.01)), position = position_dodge(0.9), vjust = -0.5, size = 2.5) +
  scale_fill_manual(values = colores) +
  labs(x = NULL, y = "Micro-F1")
guardar(figura_14, "figura_14.png")

generalizacion <- data.frame()
for (modelo in names(sinteticas)) {
  s <- c(consenso(sinteticas[[modelo]]), fiabilidad(sinteticas[[modelo]]))
  r <- c(consenso(reales[[modelo]]), fiabilidad(reales[[modelo]]))
  generalizacion <- rbind(generalizacion, data.frame(modelo, metrica = names(s), sinteticas = s, reales = r))
}

micro <- filter(generalizacion, metrica == "micro")
corpus <- rbind(data.frame(modelo = micro$modelo, corpus = "Sintéticas (N = 114)", valor = micro$sinteticas),
                data.frame(modelo = micro$modelo, corpus = "Fisioterapeutas (N = 19)", valor = micro$reales))
corpus$corpus <- factor(corpus$corpus, levels = c("Sintéticas (N = 114)", "Fisioterapeutas (N = 19)"))

retencion <- filter(generalizacion, metrica %in% c("precision_micro", "recall_micro", "micro", "emr", "AC1"))
retencion$valor <- retencion$reales / retencion$sinteticas
retencion$metrica <- factor(retencion$metrica, levels = c("precision_micro", "recall_micro", "micro", "emr", "AC1"),
                            labels = c("Precisión", "Sensibilidad", "Micro-F1", "EMR", "AC1"))

figura_15a <- ggplot(corpus, aes(modelo, valor, fill = corpus)) +
  geom_col(position = "dodge") +
  geom_text(aes(label = number(valor, accuracy = 0.01)), position = position_dodge(0.9), vjust = -0.5, size = 2.5) +
  scale_fill_manual(values = c("#4A90C8", "#B8D4EA")) +
  labs(x = NULL, y = "Micro-F1")

figura_15b <- ggplot(retencion, aes(metrica, valor, fill = modelo)) +
  geom_col(position = "dodge") +
  geom_text(aes(label = percent(valor, accuracy = 1)), position = position_dodge(0.9), vjust = -0.5, size = 2.5) +
  scale_fill_manual(values = colores) +
  scale_y_continuous(labels = percent) +
  labs(x = NULL, y = "Retención")

guardar(figura_15a + figura_15b + plot_annotation(tag_levels = "A"), "figura_15.png", ancho = 26, alto = 11)

guardar(figura_estrategias(reales), "figura_16.png")
guardar(figura_ablacion(reales), "figura_17.png", ancho = 24)
