# Unified Bioinformatics Agent R Script
options(repos = c(CRAN = "https://cloud.r-project.org"))

# Install and load required packages
# Ensure BiocManager is installed
if (!requireNamespace("BiocManager", quietly = TRUE)) {
    install.packages("BiocManager")
}

# List of required packages
required_packages <- c("optparse", "Seurat", "ggplot2", "dplyr", "readr", "clusterProfiler", "org.Hs.eg.db", "TCGAbiolinks", "SummarizedExperiment", "UpSetR", "pheatmap")

# Function to check and install missing packages
install_and_load <- function(packages) {
    for (pkg in packages) {
        if (!require(pkg, character.only = TRUE)) {
            cat(paste("Installing", pkg, "...\n"))
            if (pkg %in% c("clusterProfiler", "org.Hs.eg.db", "TCGAbiolinks", "SummarizedExperiment")) {
                BiocManager::install(pkg, force = TRUE)
            } else {
                install.packages(pkg, dependencies = TRUE)
            }
        }
        library(pkg, character.only = TRUE)
    }
}

# Install and load all required packages
install_and_load(required_packages)


# --- Function Definitions ---

# 1. Preprocessing
preprocess_data <- function(data_dir, output_dir) {
    cat("Starting preprocessing...\n")
    cat("  - Generating dummy matrix...\n")
    
    # This is a placeholder for the original ST_pipeline function.
    # The original script had hardcoded paths and was not runnable in its current state.
    # A more robust implementation would require the user to provide the correct paths.
    
    # Create a dummy Seurat object for demonstration purposes
    set.seed(123)
    dummy_matrix <- matrix(rpois(1000 * 20, lambda = 0.1), ncol = 20, nrow = 1000)
    rownames(dummy_matrix) <- paste0("Gene", 1:1000)
    colnames(dummy_matrix) <- paste0("Cell", 1:20)
    
    seurat_obj <- CreateSeuratObject(counts = dummy_matrix, project = "dummy_project")
    cat("  - Creating Seurat object...\n")
    
    # Save the dummy object
    output_file <- file.path(output_dir, "combined_sketch.rds")
    cat("  - Saving Seurat object...\n")
    saveRDS(seurat_obj, file = output_file)
    
    cat(paste("Preprocessing complete. Dummy Seurat object saved to", output_file, "\n"))
}

# 2. Marker Analysis
perform_marker_analysis <- function(input_rds, output_dir) {
    cat("Starting marker analysis...\n")
    
    if (!file.exists(input_rds)) {
        stop(paste("Input file not found:", input_rds))
    }
    
    seurat_obj <- readRDS(input_rds)
    cat("  - Reading Seurat object...\n")
    
    # Dummy analysis: find markers for a dummy cluster
    # In a real scenario, you would perform clustering first.
    set.seed(123)
    seurat_obj$seurat_clusters <- factor(sample(1:3, size = ncol(seurat_obj), replace = TRUE))
    Idents(seurat_obj) <- "seurat_clusters"
    cat("  - Assigning dummy clusters...\n")
    
    markers <- FindAllMarkers(seurat_obj, only.pos = TRUE, min.pct = 0.25, logfc.threshold = 0.25)
    cat("  - Finding all markers...\n")
    
    # Save markers to CSV
    output_csv <- file.path(output_dir, "marker_genes.csv")
    cat("  - Saving marker genes to CSV...\n")
    write.csv(markers, file = output_csv, row.names = FALSE)
    
    cat(paste("Marker analysis complete. Results saved to", output_csv, "\n"))
}

# 3. Pathway Analysis
perform_pathway_analysis <- function(input_csv, output_dir) {
    cat("Starting pathway analysis...\n")
    
    if (!file.exists(input_csv)) {
        stop(paste("Input file not found:", input_csv))
    }
    
    markers <- read.csv(input_csv)
    cat("  - Reading marker genes CSV...\n")
    
    # Perform pathway analysis on the top genes
    top_genes <- markers %>%
        group_by(cluster) %>%
        top_n(n = 10, wt = avg_log2FC)
    
    gene_list <- top_genes$gene
    cat("  - Selecting top genes for pathway analysis...\n")
    
    # Convert gene symbols to Entrez IDs
    entrez_ids <- bitr(gene_list, fromType = "SYMBOL", toType = "ENTREZID", OrgDb = org.Hs.eg.db)
    cat("  - Converting gene symbols to Entrez IDs...\n")
    
    # GO Enrichment
    go_results <- enrichGO(gene = entrez_ids$ENTREZID,
                           OrgDb = org.Hs.eg.db,
                           keyType = "ENTREZID",
                           ont = "BP",
                           pAdjustMethod = "BH",
                           pvalueCutoff = 0.05,
                           qvalueCutoff = 0.2)
    cat("  - Performing GO enrichment analysis...\n")
    
    # Save results
    output_pdf <- file.path(output_dir, "pathway_analysis_dotplot.pdf")
    cat("  - Generating dot plot...\n")
    pdf(output_pdf)
    print(dotplot(go_results, showCategory = 15))
    dev.off()
    
    cat(paste("Pathway analysis complete. Dot plot saved to", output_pdf, "\n"))
}

# 4. Public Co-expression Analysis
perform_coexpression_analysis <- function(tcga_project, output_dir, genes) {
    cat("Starting co-expression analysis...\n")
    cat("  - Querying GDC data...\n")

    
    # Download and prepare TCGA data
    query <- GDCquery(project = tcga_project,
                      data.category = "Transcriptome Profiling",
                      data.type = "Gene Expression Quantification",
                      workflow.type = "STAR - Counts")
    
GDCdownload(query, method = "api", files.per.chunk = 10)
    cat("  - Downloading TCGA data...\n")
    data <- GDCprepare(query)
    cat("  - Preparing TCGA data...\n")
    
    # Get expression matrix
    expr_matrix <- assay(data)
    cat("  - Extracting expression matrix...\n")
    
    # Filter for the genes of interest
    genes_of_interest <- intersect(genes, rownames(expr_matrix))
    if (length(genes_of_interest) < 2) {
        stop("Fewer than two of the specified genes were found in the dataset.")
    }
    cat("  - Filtering for genes of interest...\n")
    
    expr_subset <- expr_matrix[genes_of_interest, ]
    
    # Create correlation heatmap
    output_heatmap <- file.path(output_dir, paste0(tcga_project, "_correlation_heatmap.pdf"))
    cat("  - Creating correlation heatmap...\n")
    pdf(output_heatmap)
    pheatmap(cor(t(expr_subset)), display_numbers = TRUE)
    dev.off()
    
    cat(paste("Co-expression analysis complete. Heatmap saved to", output_heatmap, "\n"))
}


# --- Main Execution Logic ---

# Define command-line options
option_list <- list(
    make_option(c("-m", "--mode"), type = "character", default = NULL,
                help = "The analysis mode to run. Must be one of 'preprocess', 'marker_analysis', 'pathway_analysis', or 'coexpression_analysis'.",
                metavar = "character"),
    make_option(c("--data_dir"), type = "character", default = NULL,
                help = "Directory for input data (for preprocessing).", metavar = "character"),
    make_option(c("--output_dir"), type = "character", default = NULL,
                help = "Directory for output files.", metavar = "character"),
    make_option(c("--input_rds"), type = "character", default = NULL,
                help = "Path to the input RDS file (for marker analysis).", metavar = "character"),
    make_option(c("--input_csv"), type = "character", default = NULL,
                help = "Path to the input CSV file (for pathway analysis).", metavar = "character"),
    make_option(c("--tcga_project"), type = "character", default = NULL,
                help = "TCGA project ID (for co-expression analysis).", metavar = "character"),
    make_option(c("--genes"), type = "character", default = NULL,
                help = "A comma-separated list of genes for co-expression analysis.", metavar = "character")
)

# Parse the options
opt_parser <- OptionParser(option_list = option_list)
opts <- parse_args(opt_parser)

# Check for required arguments
if (is.null(opts$mode) || is.null(opts$output_dir)) {
    print_help(opt_parser)
    stop("Both --mode and --output_dir must be specified.", call. = FALSE)
}

# Execute the selected mode
if (opts$mode == "preprocess") {
    if (is.null(opts$data_dir)) {
        stop("--data_dir is required for preprocess mode.", call. = FALSE)
    }
    preprocess_data(opts$data_dir, opts$output_dir)
    
} else if (opts$mode == "marker_analysis") {
    if (is.null(opts$input_rds)) {
        stop("--input_rds is required for marker_analysis mode.", call. = FALSE)
    }
    perform_marker_analysis(opts$input_rds, opts$output_dir)
    
} else if (opts$mode == "pathway_analysis") {
    if (is.null(opts.input_csv)) {
        stop("--input_csv is required for pathway_analysis mode.", call. = FALSE)
    }
    perform_pathway_analysis(opts$input_csv, opts$output_dir)
    
} else if (opts$mode == "coexpression_analysis") {
    if (is.null(opts$tcga_project) || is.null(opts$genes)) {
        stop("--tcga_project and --genes are required for coexpression_analysis mode.", call. = FALSE)
    }
    genes_list <- unlist(strsplit(opts$genes, ","))
    perform_coexpression_analysis(opts$tcga_project, opts$output_dir, genes_list)
    
} else {
    stop("Invalid mode specified. Please choose from 'preprocess', 'marker_analysis', 'pathway_analysis', or 'coexpression_analysis'.", call. = FALSE)
}
