args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) stop("Uso: Rscript analisis/analizar.R archivo.json [nombre]")

archivo <- args[1]
nombre <- if (length(args) > 1) args[2] else basename(archivo)

rmarkdown::render("analisis/informe.Rmd",
                  params = list(archivo = archivo, nombre = nombre),
                  output_file = paste0("informe_", tools::file_path_sans_ext(basename(archivo)), ".html"),
                  output_dir = "results",
                  knit_root_dir = getwd())
