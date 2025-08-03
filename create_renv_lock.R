# Install renv and BiocManager
if (!requireNamespace("renv", quietly = TRUE)) {
  install.packages("renv", repos = "https://cloud.r-project.org")
}
if (!requireNamespace("BiocManager", quietly = TRUE)) {
  install.packages("BiocManager", repos = "https://cloud.r-project.org")
}

# Install Bioconductor version 3.18
BiocManager::install(version = "3.18", ask = FALSE)

# Install packages
install.packages('Matrix', repos = 'https://cloud.r-project.org')
BiocManager::install(c('SeuratObject', 'BPCells', 'DESeq2', 'glmGamPoi', 'limma', 'MAST', 'monocle', 'presto', 'rtracklayer', 'SingleCellExperiment', 'multtest'), version = '3.18')
install.packages(c('Seurat', 'optparse', 'ggplot2', 'dplyr', 'readr', 'clusterProfiler', 'ggfun', 'aplot', 'scatterpie', 'ggtree', 'enrichplot', 'TCGAbiolinks'), repos = 'https://cloud.r-project.org')

# Create renv.lock
renv::snapshot()
