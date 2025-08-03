```python
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import boto3
from scipy.stats import pearsonr, spearmanr
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.preprocessing import StandardScaler
import os

def main():
    parser = argparse.ArgumentParser(description='Co-expression analysis')
    parser.add_argument('--s3-path', required=True, help='S3 path to input data')
    parser.add_argument('--genes', required=True, help='Comma-separated gene symbols')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    genes = [gene.strip() for gene in args.genes.split(',')]
    
    os.makedirs(args.output_dir, exist_ok=True)
    
    s3_parts = args.s3_path.replace('s3://', '').split('/')
    bucket = s3_parts[0]
    key = '/'.join(s3_parts[1:])
    
    s3_client = boto3.client('s3')
    local_file = os.path.join(args.output_dir, 'input_data.csv.gz')
    s3_client.download_file(bucket, key, local_file)
    
    df = pd.read_csv(local_file, compression='gzip', index_col=0)
    
    available_genes = [gene for gene in genes if gene in df.index]
    if not available_genes:
        print(f"None of the specified genes found in data")
        return
    
    gene_data = df.loc[available_genes].T
    gene_data = gene_data.dropna()
    
    correlation_matrix = gene_data.corr(method='pearson')
    correlation_matrix.to_csv(os.path.join(args.output_dir, 'correlation_matrix.csv'))
    
    plt.figure(figsize=(10, 8))
    mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
    sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdBu_r', center=0,
                square=True, fmt='.3f', cbar_kws={"shrink": .8})
    plt.title('Gene Co-expression Correlation Matrix')
    plt.tight_layout()
    plt.savefig(os.path.join(args.output_dir, 'correlation_heatmap.png'), dpi=300, bbox_inches='tight')
    plt.close()
    
    pairwise_stats = []
    for i, gene1 in enumerate(available_genes):
        for j, gene2 in enumerate(available_genes):
            if i < j:
                x = gene_data[gene1]
                y = gene_data[gene2]
                
                pearson_r, pearson_p = pearsonr(x, y)
                spearman_r, spearman_p = spearmanr(x, y)
                
                pairwise_stats.append({
                    'Gene1': gene1,
                    'Gene2': gene2,
                    'Pearson_r': pearson_r,
                    'Pearson_p': pearson_p,
                    'Spearman_r': spearman_r,
                    'Spearman_p': spearman_p,
                    'N_samples': len(x)
                })
    
    stats_df = pd.DataFrame(pairwise_stats)
    stats_df.to_csv(os.path.join(args.output_dir, 'pairwise_correlations.csv'), index=False)
    
    n_genes = len(available_genes)
    if n_genes > 1:
        fig, axes = plt.subplots(n_genes, n_genes, figsize=(4*n_genes, 4*n_genes))
        if n_genes == 2:
            axes = axes.reshape(2,