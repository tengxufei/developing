options(repos = c(CRAN = "https://cloud.r-project.org", BiocManager = "https://bioconductor.org/packages/release/bioc"))

# Function to install and load a package
install_and_load <- function(pkg, version = NULL, url = NULL, bioc = FALSE, github_repo = NULL) {
    if (!require(pkg, character.only = TRUE)) {
        message(paste("Installing", pkg, "..."))
        if (bioc) {
            if (!require("BiocManager", quietly = TRUE)) {
                install.packages("BiocManager")
            }
            BiocManager::install(pkg)
        } else if (!is.null(github_repo)) {
            if (!require("remotes", quietly = TRUE)) {
                install.packages("remotes")
            }
            remotes::install_github(github_repo)
        } else if (!is.null(url)) {
            install.packages(url, repos = NULL, type = "source")
        } else if (!is.null(version)) {
            remotes::install_version(pkg, version = version)
        } else {
            install.packages(pkg, dependencies = TRUE)
        }
        
        if (require(pkg, character.only = TRUE)) {
            message(paste(pkg, "installed and loaded successfully."))
        } else {
            stop(paste("Failed to install or load", pkg))
        }
    } else {
        message(paste(pkg, "is already installed and loaded."))
    }
}

# Install dependencies
install_and_load("remotes")
install_and_load("optparse")
install_and_load("Matrix", version = "1.6-5")
install_and_load("MASS", url = "https://cran.r-project.org/src/contrib/Archive/MASS/MASS_7.3-60.0.1.tar.gz")
install_and_load("Rcpp")
install_and_load("magrittr")
install_and_load("vctrs")

