# Scientific Critic Agent - Validates the analysis results
import os
import sys
import pandas as pd
from langchain_core.tools import tool

# Add the orchestrator directory to the Python path to import the Bedrock client
orchestrator_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "orchestrator"))
sys.path.append(orchestrator_dir)

from bedrock_client import get_langchain_bedrock_llm
from langchain_core.output_parsers import StrOutputParser

class ScientificCriticAgent:
    def __init__(self):
        self.llm = get_langchain_bedrock_llm()

    def review_results(self, results_dir):
        """
        Reviews the Seurat analysis results using AWS Bedrock.
        """
        print(f"Scientific Critic Agent: Reviewing results from {results_dir}")
        
        # 1. Read the marker genes file
        marker_genes_path = os.path.join(results_dir, "marker_genes.csv")
        if not os.path.exists(marker_genes_path):
            print("ERROR: Marker genes file not found.")
            return
        
        try:
            marker_df = pd.read_csv(marker_genes_path)
            # Get the top 5 markers for the first 3 clusters for the prompt
            top_markers_summary = marker_df.groupby('cluster').head(5).groupby('cluster')['gene'].apply(list).head(3).to_dict()
        except Exception as e:
            print(f"ERROR: Could not read or process marker genes file: {e}")
            return

        # 2. Formulate a prompt for the critic model
        prompt = f"""
        You are a senior computational biologist acting as a scientific critic.
        An automated Seurat analysis was performed on a spatial transcriptomics dataset from an Astroblastoma sample.
        The analysis produced a list of marker genes for different cell clusters.
        
        Here is a summary of the top marker genes for the first few clusters:
        {top_markers_summary}

        Based on this information, please provide a critical review of the analysis.
        Focus on the following points:
        1.  **Potential Pitfalls:** What are common issues or biases that could arise from an automated Seurat workflow (e.g., normalization, clustering resolution, batch effects)?
        2.  **Statistical Soundness:** Are the provided markers statistically significant? What further statistical tests would you recommend? (Assume standard Seurat defaults were used).
        3.  **Next Steps:** What are the essential next steps to validate these findings and ensure the quality of the analysis before biological interpretation?
        
        Provide a concise, critical review.
        """

        # 3. Invoke the Bedrock model
        chain = self.llm | StrOutputParser()
        critique = chain.invoke(prompt)
        
        # 4. Save the critique to a file
        critique_path = os.path.join(results_dir, "scientific_critique.txt")
        with open(critique_path, "w") as f:
            f.write(critique)
            
        print(f"Scientific Critic Agent: Critique saved to {critique_path}") # Keep this for file tracking
        return critique

if __name__ == "__main__":
    # Example usage requires output from the bioinformatician agent
    # This assumes the script is run from the project root
    output_directory = "output" 
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        # Create a dummy marker file for testing
        dummy_data = {'cluster': [0, 0, 1, 1], 'gene': ['GENE_A', 'GENE_B', 'GENE_C', 'GENE_D']}
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_csv(os.path.join(output_directory, "marker_genes.csv"), index=False)

    critic_agent = ScientificCriticAgent()
    generated_critique = critic_agent.review_results(output_directory)
    if generated_critique:
        print("--- Generated Critique ---")
        print(generated_critique)
        print("--------------------------")
