
suppressPackageStartupMessages({
  library(flextable)
  library(officer)
  library(magrittr)
})

# Datos completos del checklist TRIPOD-LLM
tripod_data <- data.frame(
  Section_Topic = c(
    # Abstract
    'Abstract / Title',
    'Abstract / Abstract',
    'Abstract / Objectives',
    'Abstract / Methods',
    'Abstract / Methods',
    'Abstract / Methods',
    'Abstract / Methods',
    'Abstract / Methods',
    'Abstract / Methods',
    'Abstract / Results',
    'Abstract / Discussion',
    'Abstract / Other',
    # Introduction
    'Introduction / Background',
    'Introduction / Background',
    'Introduction / Objectives',
    # Methods
    'Methods / Data',
    'Methods / Data',
    'Methods / Data',
    'Methods / Data',
    'Methods / Data',
    'Methods / Analytical Methods',
    'Methods / Analytical Methods',
    'Methods / Analytical Methods',
    'Methods / Analytical Methods',
    'Methods / Analytical Methods',
    'Methods / Analytical Methods',
    'Methods / Analytical Methods',
    'Methods / LLM Output',
    'Methods / LLM Output',
    'Methods / LLM Output',
    'Methods / Annotation',
    'Methods / Annotation',
    'Methods / Annotation',
    'Methods / Prompting',
    'Methods / Prompting',
    'Methods / Summarization',
    'Methods / Instruction Tuning',
    'Methods / Compute',
    'Methods / Ethics Approval',
    'Methods / Open Science',
    'Methods / Open Science',
    'Methods / Open Science',
    'Methods / Open Science',
    'Methods / Open Science',
    'Methods / Open Science',
    'Methods / Public Involvement',
    # Results
    'Results / Participants',
    'Results / Participants',
    'Results / Participants',
    'Results / Participants',
    'Results / Performance',
    'Results / LLM Updating',
    # Discussion
    'Discussion / Interpretation',
    'Discussion / Limitations',
    'Discussion / Usability in context',
    'Discussion / Usability in context',
    'Discussion / Usability in context',
    'Discussion / Usability in context',
    'Discussion / Usability in context'
  ),
  Item_Number = c(
    '2a', '2b', '2c', '2d', '2e', '2f', '2g', '2h', '2i', '2j', '2k', '2l',
    '3a', '3b', '4',
    '5a', '5b', '5c', '5d', '5e',
    '6a', '6b', '6c', '6d', '6e', '6f', '6g',
    '7a', '7b', '7c',
    '8a', '8b', '8c',
    '9a', '9b',
    '10',
    '11',
    '12',
    '13',
    '14a', '14b', '14c', '14d', '14e', '14f',
    '15',
    '16a', '16b', '16c', '16d',
    '17',
    '18',
    '19a', '19b', '19c', '19d', '19e', '19f', '19g'
  ),
  Checklist_Item = c(
    'Identify the study as developing, fine-tuning, and/or evaluating the performance of an LLM, specifying the task, the target population, and the outcome to be predicted.',
    'Provide a brief explanation of the healthcare context, use case and rationale for developing or evaluating the performance of an LLM.',
    'Specify the study objectives, including whether the study describes LLMs development, tuning, and/or evaluation.',
    'Describe the key elements of the study setting.',
    'Detail all data used in the study, specify data splits and any selective use of data.',
    'Specify the name and version of LLM used.',
    'Briefly summarize the LLM-building steps, including any fine-tuning, reward modeling, reinforcement learning with human feedback (RLHF), etc.',
    'Describe the specific tasks performed by the LLMs (e.g., medical QA, summarization, extraction), highlighting key inputs and outputs used in the final LLM.',
    'Specify the evaluation datasets/populations used, including the endpoint evaluated, and detail whether this information was held out during training/tuning where relevant, and what measure(s) were used to evaluate LLM performance.',
    'Give an overall report and interpretation of the main results.',
    'Explicitly state any broader implications or concerns that have arisen in light of these results.',
    'Give the registration number and name of the registry or repository (if relevant).',
    'Explain the healthcare context / use case (e.g., administrative, diagnostic, therapeutic, clinical workflow) and rationale for developing or evaluating the LLM, including references to existing approaches and models.',
    'Describe the target population and the intended use of the LLM in the context of the care pathway, including its intended users in current gold standard practices (e.g., healthcare professionals, patients, public, or administrators).',
    'Specify the study objectives, including whether the study describes the initial development, fine-tuning, or validation of an LLM (or multiple stages).',
    'Describe the sources of data separately for the training, tuning, and/or evaluation datasets and the rationale for using these data (e.g., web corpora, clinical research/trial data, EHR data).',
    'Describe the relevant data points and provide a quantitative and qualitative description of their distribution and other relevant descriptors of the dataset (e.g., source, languages, countries of origin).',
    'Specifically state the date of the oldest and newest item of text used in the development process (training, fine-tuning, reward modeling) and in the evaluation datasets.',
    'Describe any data pre-processing and quality checking, including whether this was similar across text corpora, institutions, and relevant sociodemographic groups.',
    'Describe how missing and imbalanced data were handled and provide reasons for omitting any data.',
    'Report the LLM name, version, and last date of training or use during inference.',
    'Specify the type of LLM architecture, and LLM building steps, including any hyperparameter tuning (e.g., temperature, length limits, penalties), prompt engineering, and any inference settings (e.g., seed, temperature, max token length) as relevant.',
    'Report details of LLM development process from text input to outcome generation, such as training, fine-tuning procedures, and alignment strategy (e.g., reinforcement learning, direct preference optimization, etc.) and alignment goals (e.g., helpfulness, honesty, harmlessness, etc.).',
    'Specify the initial and post-processed output of the LLM (e.g., probabilities, classification, unstructured text).',
    'Provide details and rationale for any classification and how the probabilities were determined and thresholds identified.',
    'Include metrics that capture the quality of generative outputs, such as consistency, relevance, and accuracy, compared to gold standards.',
    'Report the outcome metrics relevance to downstream task at deployment time and correlation of metric to human evaluation of the text for the intended use.',
    'Clearly define the outcome, how the LLM predictions were calculated (e.g., formula, code, object, API), and evaluation metrics.',
    'If outcome assessment requires subjective interpretation, describe the qualifications of the assessors, any instructions provided, relevant information on demographics of the assessors, and inter-assessor agreement.',
    'Specify how performance was compared to other LLMs, humans, and other benchmarks or standards.',
    'If annotation was done, report how text was labeled, including providing specific annotation guidelines with examples.',
    'If annotation was done, report how many annotators labeled the dataset(s), including the proportion of data in each dataset that were annotated by more than 1 annotator.',
    'If annotation was done, provide information on the background and experience of the annotators, and the inter-annotator agreement.',
    'If research involved prompting LLMs, provide details on the processes used during prompt design, curation, and selection.',
    'If research involved prompting LLMs, report what data were used to develop the prompts.',
    'Describe any preprocessing of the data before summarization.',
    'If instruction tuning/alignment strategies were used, what were the instructions and interface used for evaluation, and what were the characteristics of the populations doing evaluation?',
    'Report compute, or proxies thereof (e.g., time on what and how many machines, cost on what and how many machines, inference time, floating-point operations per second (FLOPs)), required to carry out methods.',
    'Name the institutional research board or ethics committee that approved the study and describe the participant-informed consent or the ethics committee waiver of informed consent.',
    'Give the source of funding and the role of the funders for the present study.',
    'Declare any conflicts of interest and financial disclosures for all authors.',
    'Indicate where the study protocol can be accessed or state that a protocol was not prepared.',
    'Provide registration information for the study, including register name and registration number, or state that the study was not registered.',
    'Provide details of the availability of the study data.',
    'Provide details of the availability of the code to reproduce the study results.',
    'Provide details of any patient and public involvement during the design, conduct, reporting, interpretation, or dissemination of the study or state no involvement.',
    'When using patient/EHR data, describe the flow of text/EHR/patient data through the study, including the number of documents/questions/participants with and without the outcome/label and follow-up time.',
    'When using patient/EHR data, report the characteristics overall and, for each data source or setting, and for development/evaluation splits, including the key dates, key predictors, and sample size.',
    'For LLM evaluation, show a comparison of the distribution of important predictors between development and evaluation data.',
    'When using patient/EHR data, specify the number of participants and outcome events in each analysis (e.g., for LLM development, hyperparameter tuning, LLM evaluation).',
    'Report LLM performance according to pre-specified metrics (see item 7a) and/or human evaluation (see item 7d).',
    'If applicable, report the results from any LLM updating, including the updated LLM and subsequent performance.',
    'Give an overall interpretation of the main results, including issues of fairness in the context of the objectives and previous studies.',
    'Discuss any limitations of the study and their effects on any biases, statistical uncertainty, and generalizability.',
    'Describe any known challenges in using data for the specified task and domain context with reference to representation, missingness, harmonization, and bias.',
    'Define the intended use for the implementation under evaluation, including the intended input, end-user, level of autonomy/human oversight.',
    'If applicable, describe how poor quality or unavailable input data should be assessed and handled when implementing the LLM, i.e., what is the usability of the LLM in the context of current clinical care.',
    'If applicable, specify whether users will be required to interact in the handling of the input data or use of the LLM, and what level of expertise is required of users.',
    'Discuss any next steps for future research, with a specific view to applicability and generalizability of the LLM.'
  ),
  Research_Design = c(
    'All', 'E, H', 'All', 'All', 'M, D, E', 'All', 'M, D', 'All', 'All', 'All', 'All', 'H',
    'All', 'E, H', 'All',
    'All', 'All', 'M, D, E, H', 'All', 'M, D, E',
    'All', 'M, D, E', 'M, D', 'All', 'All', 'All', 'E, H',
    'E, H', 'All', 'All',
    'All', 'All', 'All',
    'All', 'All',
    'All',
    'M, D',
    'M, D, E',
    'All',
    'All', 'All', 'H', 'H', 'All', 'All',
    'H',
    'E, H', 'E, H', 'E, H', 'E, H',
    'All',
    'All',
    'All', 'All', 'E, H', 'E, H', 'E, H', 'E, H', 'All'
  ),
  LLM_Task = c(
    'All', 'All', 'All', 'All', 'All', 'All', 'All', 'All', 'All', 'All', 'All', 'All',
    'All', 'All', 'All',
    'All', 'All', 'All', 'All', 'All',
    'All', 'All', 'All', 'All', 'C, OF', 'QA, IR, DG, SS, MT', 'All',
    'All', 'All', 'All',
    'All', 'All', 'All',
    'All', 'All',
    'SS',
    'All',
    'All',
    'All',
    'All', 'All', 'All', 'All', 'All', 'All',
    'All',
    'All', 'All', 'All', 'All',
    'All',
    'All',
    'All', 'All', 'All', 'All', 'All', 'All', 'All'
  ),
  Reported_Page = c(
    '1, 5',        # 2a
    '5',           # 2b
    '5',           # 2c
    '5',           # 2d
    '5',           # 2e
    '5',           # 2f
    '5',           # 2g
    '5',           # 2h
    '5',           # 2i
    '5',           # 2j
    '5',           # 2k
    '5, 46',       # 2l
    '6-7',         # 3a
    '7',           # 3b
    '8-9',         # 4
    '10, 23',      # 5a
    '13-15',       # 5b
    '13, 20',      # 5c
    '11, 16-17',   # 5d
    '13, 17, 23',  # 5e
    '15, 18',      # 6a
    '16, 20',      # 6b
    '12, 20-21',   # 6c
    '16, 18-19',   # 6d
    '17, 22-23',   # 6e
    '20',          # 6f
    '22, 36-37',   # 6g
    '21-23',       # 7a
    '23',          # 7b
    '15, 22',      # 7c
    '13, 23',      # 8a
    '23',          # 8b
    '23',          # 8c
    '12, 20-21',   # 9a
    '21',          # 9b
    'Not Req.',    # 10
    '20-21',       # 11
    '22, 27-28, 35', # 12
    '23',          # 13
    '46',          # 14a
    '46',          # 14b
    '10, 46',      # 14c
    '46',          # 14d
    '46',          # 14e
    '10, 46',      # 14f
    '23',          # 15
    '10, 17, 24, 30', # 16a
    '13, 30',      # 16b
    '14-15, 32, 34',  # 16c
    '25, 30',      # 16d
    '24-36',       # 17
    'Not Req.',    # 18
    '36-37',       # 19a
    '38-39',       # 19b
    '37-38',       # 19c
    '38-39, 41',   # 19d
    '37-38',       # 19e
    '39',          # 19f
    '39, 41'       # 19g
  ),
  stringsAsFactors = FALSE
)

# Definir bordes estilo APA / Booktabs
border_main <- fp_border(color = '#222222', width = 1.5)
border_sub  <- fp_border(color = '#444444', width = 0.8)

cut_rows <- c(12, 15, 46, 52)

# Tabla adaptada a A4 Vertical (Portrait)
# Ancho total disponible en A4 Vertical (21cm con margenes de 2cm) = 17cm ≈ 6.69 pulgadas
# Asignacion de anchos:
# Section_Topic: 1.25 in
# Item_Number:   0.38 in
# Checklist_Item: 3.35 in
# Research_Design: 0.55 in
# LLM_Task:      0.60 in
# Reported_Page: 0.56 in
# Total = 6.69 in (17.0 cm)

tabla_a4_v <- flextable(tripod_data) %>%
  set_header_labels(
    Section_Topic   = 'Section / Topic',
    Item_Number     = 'Item',
    Checklist_Item  = 'Checklist Item',
    Research_Design = 'Design',
    LLM_Task        = 'Task',
    Reported_Page   = 'Page'
  ) %>%
  merge_v(j = 'Section_Topic') %>%
  valign(j = 'Section_Topic', valign = 'top') %>%
  italic(j = 'Section_Topic') %>%
  bold(part = 'header') %>%
  bold(j = 'Item_Number') %>%
  align(j = c('Section_Topic', 'Checklist_Item'), align = 'left', part = 'all') %>%
  align(j = c('Item_Number', 'Research_Design', 'LLM_Task', 'Reported_Page'), align = 'center', part = 'all') %>%
  valign(j = c('Item_Number', 'Research_Design', 'LLM_Task', 'Reported_Page'), valign = 'top', part = 'body') %>%
  border_remove() %>%
  hline_top(part = 'header', border = border_main) %>%
  hline_bottom(part = 'header', border = border_sub) %>%
  hline_bottom(part = 'body', border = border_main) %>%
  hline(i = cut_rows, border = border_sub) %>%
  padding(padding.top = 2.5, padding.bottom = 2.5, padding.left = 3, padding.right = 3, part = 'all') %>%
  fontsize(size = 8, part = 'body') %>%
  fontsize(size = 8.5, part = 'header') %>%
  font(fontname = 'Times New Roman', part = 'all') %>%
  width(j = 'Section_Topic', width = 1.25) %>%
  width(j = 'Item_Number', width = 0.38) %>%
  width(j = 'Checklist_Item', width = 3.35) %>%
  width(j = 'Research_Design', width = 0.55) %>%
  width(j = 'LLM_Task', width = 0.60) %>%
  width(j = 'Reported_Page', width = 0.56)

tabla_a4_v <- tabla_a4_v %>%
  add_footer_lines(values = c(
    'Note. TRIPOD-LLM checklist for transparent reporting of AI/LLM studies in healthcare.',
    'Design: M = Model development; D = Development with fine-tuning; E = Evaluation; H = Human evaluation; All = All designs.',
    'Task: All = All tasks; C = Classification; OF = Outcome forecasting; QA = Question answering; IR = Information retrieval; DG = Dialogue generation; SS = Summarization; MT = Machine translation.'
  )) %>%
  fontsize(size = 7.5, part = 'footer') %>%
  font(fontname = 'Times New Roman', part = 'footer') %>%
  italic(part = 'footer') %>%
  hline_bottom(part = 'footer', border = border_main)

# Seccion A4 Vertical con margenes estandar (2.0 cm = 0.79 in)
sec_portrait <- prop_section(
  page_size = page_size(orient = 'portrait', width = 8.27, height = 11.69),
  page_margins = page_mar(top = 0.79, bottom = 0.79, left = 0.79, right = 0.79)
)

doc_portrait <- read_docx() %>%
  body_add_par('Anexo: TRIPOD-LLM Checklist', style = 'heading 1') %>%
  body_add_par('Lista de verificación para la comunicación transparente de estudios biomédicos y clínicos con Modelos de Lenguaje Grande (LLMs). Formato adaptado a A4 Vertical (APA / Booktabs).', style = 'Normal') %>%
  body_add_par('') %>%
  body_add_flextable(tabla_a4_v) %>%
  body_set_default_section(sec_portrait)

output_dir <- '/home/miguelvime/projects/2026-03-11_TFM/entregas/entrega_septiembre_inicios'
output_file_v <- file.path(output_dir, 'Anexo_TRIPOD_LLM_Checklist_A4_Vertical.docx')
output_file_v2 <- '/home/miguelvime/projects/2026-03-11_TFM/results/Anexo_TRIPOD_LLM_Checklist_A4_Vertical.docx'

print(doc_portrait, target = output_file_v)
print(doc_portrait, target = output_file_v2)
cat('Generado A4 Vertical en:\n', output_file_v, '\n', output_file_v2, '\n')
