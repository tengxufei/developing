# Use an official R base image
FROM rocker/r-ver:4.4.0

# Install system dependencies required for R packages
RUN apt-get update && apt-get install -y     libcurl4-openssl-dev     libssl-dev     libxml2-dev     cargo     libhdf5-dev     libfontconfig1-dev     libudunits2-dev     libfftw3-dev     cmake     libfreetype6-dev     libharfbuzz-dev     libfribidi-dev     libcairo2-dev     libgdal-dev     libgeos-dev     libproj-dev     libglpk-dev     libgmp-dev     libmpfr-dev     libtool     automake     autoconf     perl     libbz2-dev     python3     python3-pip     && rm -rf /var/lib/apt/lists/*

# Install renv and BiocManager
RUN R -e "install.packages(c('renv', 'BiocManager'), repos = 'https://cloud.r-project.org')"

# Force downgrade/reinstallation of packages to match Bioconductor version
RUN R -e "BiocManager::install(version = '3.19', ask = FALSE)"

# Install R packages and create renv.lock within the Dockerfile
RUN R -e "install.packages('Matrix', repos = 'https://cloud.r-project.org')" && \
    R -e "BiocManager::install(c('SeuratObject', 'BPCells', 'DESeq2', 'glmGamPoi', 'limma', 'MAST', 'monocle', 'presto', 'rtracklayer', 'SingleCellExperiment', 'multtest'), version = '3.19')" && \
    R -e "install.packages(c('Seurat', 'optparse', 'ggplot2', 'dplyr', 'readr', 'clusterProfiler', 'ggfun', 'aplot', 'scatterpie', 'ggtree', 'enrichplot', 'TCGAbiolinks'), repos = 'https://cloud.r-project.org')" && \
    R -e "renv::snapshot()"

# Restore project dependencies using the generated renv.lock
RUN R -e "renv::restore()"

# Set the working directory
WORKDIR /app

# Set build arguments for AWS credentials and Anthropic model
ARG AWS_ACCESS_KEY_ID
ARG AWS_SECRET_ACCESS_KEY
ARG AWS_REGION
ARG ANTHROPIC_MODEL

# Set environment variables from build arguments
ENV AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
ENV AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
ENV AWS_REGION=$AWS_REGION
ENV ANTHROPIC_MODEL=$ANTHROPIC_MODEL

# Copy the entire project directory into the container
COPY . /app

# Install Python dependencies
RUN python3 -m pip install --no-cache-dir -r /app/requirements.txt

# Expose port for the Flask app
EXPOSE 6000

# Command to run the Flask application with Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:6000", "app:app"]

