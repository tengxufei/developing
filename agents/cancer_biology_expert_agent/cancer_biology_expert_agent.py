# Cancer Biology Expert Agent - Provides biological interpretation
import os
import sys
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Add the orchestrator directory to the Python path to import the Bedrock client
orchestrator_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "orchestrator"))
sys.path.append(orchestrator_dir)

from bedrock_client import get_langchain_bedrock_llm

class CancerBiologyExpertAgent:
    def __init__(self):
        self.llm = get_langchain_bedrock_llm()

    def provide_interpretation(self, results_dir):
        """
        Provides a biological interpretation of the results using AWS Bedrock.
        """
        print(f"Cancer Biology Expert Agent: Providing interpretation for results from {results_dir}")

        # 1. Read all relevant data files
        # Read marker genes
        marker_genes_path = os.path.join(results_dir, "marker_genes.csv")
        if not os.path.exists(marker_genes_path):
            print("ERROR: Marker genes file not found.")
            return
        try:
            marker_df = pd.read_csv(marker_genes_path)
            top_markers_summary = marker_df.groupby('cluster').head(3).groupby('cluster')['gene'].apply(list).to_dict()
        except Exception as e:
            print(f"ERROR: Could not read or process marker genes file: {e}")
            return

        # Read scientific critique
        critique_path = os.path.join(results_dir, "scientific_critique.txt")
        critique_text = "No critique was provided."
        if os.path.exists(critique_path):
            with open(critique_path, "r") as f:
                critique_text = f.read()

        # Read pathway analysis results
        pathway_path = os.path.join(results_dir, "pathway_analysis_results.csv")
        pathway_text = "No pathway analysis results were found."
        if os.path.exists(pathway_path):
            try:
                pathway_df = pd.read_csv(pathway_path)
                # Summarize top 3 pathways per cluster
                top_pathways_summary = pathway_df.groupby('cluster').head(3).groupby('cluster')['Description'].apply(list).to_dict()
                pathway_text = str(top_pathways_summary)
            except Exception as e:
                pathway_text = f"Could not process pathway file: {e}"


        # 3. Formulate a detailed, structured prompt for the expert model using Langchain
        prompt_template = ChatPromptTemplate.from_messages(
            [
                (
                    "human",
                    """
        You are a world-class Cancer Biologist and Bioinformatician with deep expertise in Astroblastoma and spatial transcriptomics.
        An automated analysis has been performed on a spatial transcriptomics dataset from an Astroblastoma tumor sample.
        Your task is to first, reason through the data step-by-step (Chain of Thought), and then second, synthesize all available data into a comprehensive, publication-quality interpretation for a research team.

        **INPUT DATA:**
        ---
        **1. Top Marker Genes per Cluster:**
        {top_markers_summary}

        **2. Top Enriched Biological Pathways (Gene Ontology) per Cluster:**
        {pathway_text}

        **3. Scientific Critique of the Analysis Pipeline:**
        {critique_text}
        ---

        **INSTRUCTIONS:**
        First, provide a step-by-step reasoning process to analyze the data. Then, based on your reasoning, generate the final detailed report.

        **--- START OF RESPONSE ---**

        **CHAIN OF THOUGHT:**
        1.  **Initial Data Scan:** Briefly review the marker genes, pathways, and critique. Note any immediate standouts or potential issues mentioned in the critique.
        2.  **Cluster-by-Cluster Analysis:** For each cluster, systematically:
            a.  List the marker genes.
            b.  List the enriched pathways.
            c.  Synthesize: How do the genes relate to the pathways? What is the likely cell type or state? (e.g., "Cluster X has markers A, B, C. Pathways are related to 'cell division' and 'metabolism'. This suggests these are highly proliferative tumor cells.")
        3.  **TME Integration:** How do the inferred cluster functions relate to each other? Formulate initial ideas about their interactions. (e.g., "Cluster Y looks like immune cells, and their pathways suggest activation. This might be a response to the proliferative tumor cells in Cluster X.")
        4.  **Hypothesis Formulation:** Based on the synthesis, what are the most interesting, testable questions that arise?
        5.  **Report Structuring:** Plan the structure of the final report based on the insights gathered.

        **--- START OF REPORT ---**

        **1. EXECUTIVE SUMMARY:**
        Provide a high-level summary of the key findings. What is the overall cellular landscape and functional state of this tumor?

        **2. DETAILED CELL TYPE AND FUNCTIONAL ANNOTATION:**
        For each cluster, provide a detailed annotation in a markdown table.
        - Cluster ID
        - Top Marker Genes
        - Top Pathways
        - Inferred Cell Type / State
        - Functional Interpretation (Explain what the cells in this cluster are *doing* by linking their marker genes to their enriched pathways, based on your chain of thought).

        **3. TUMOR MICROENVIRONMENT (TME) ANALYSIS:**
        Describe the TME's composition and functional state.
        - Discuss the interplay between different cell types based on their inferred functions (e.g., "The angiogenic pathways in Cluster 2 (Endothelial cells) are likely activated in response to signals from Cluster 1 (Tumor cells), which show high expression of VEGFA.").
        - Propose which cellular neighborhoods are of highest interest for follow-up spatial analysis.

        **4. ACTIONABLE, TESTABLE HYPOTHESES:**
        Propose 2-3 specific, testable hypotheses that arise from the integrated analysis. These should be concrete ideas for follow-up experiments.
        - Example: "Hypothesis 1: The 'inflammatory response' pathway in Cluster 5 (Macrophages) is driven by the marker gene IL1B. This can be validated by performing co-immunofluorescence for CD68 (a macrophage marker) and IL1B on the tissue slides."

        **5. POTENTIAL CLINICAL AND THERAPEUTIC RELEVANCE:**
        Discuss the potential clinical implications of your findings, focusing on how the functional states of the cell clusters might influence tumor progression, prognosis, or response to therapy.

        **--- END OF REPORT ---**
        """
                ),
            ]
        )

        # 4. Invoke the Bedrock model using Langchain chain
        chain = prompt_template | self.llm | StrOutputParser()
        interpretation = chain.invoke(
            {
                "top_markers_summary": top_markers_summary,
                "pathway_text": pathway_text,
                "critique_text": critique_text,
            }
        )

        # 5. Save the interpretation to a file
        interpretation_path = os.path.join(results_dir, "biological_interpretation_report.md")
        with open(interpretation_path, "w") as f:
            f.write(interpretation)

        print(f"Cancer Biology Expert Agent: Detailed report saved to {interpretation_path}") # Keep this for file tracking
        return interpretation

if __name__ == "__main__":
    # Example usage requires output from the bioinformatician and critic agents
    output_directory = "output"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
        # Create dummy files for testing
        dummy_data = {'cluster': [0, 0, 1, 1], 'gene': ['GFAP', 'OLIG2', 'PTPRC', 'CD19']}
        dummy_df = pd.DataFrame(dummy_data)
        dummy_df.to_csv(os.path.join(output_directory, "marker_genes.csv"), index=False)
        with open(os.path.join(output_directory, "scientific_critique.txt"), "w") as f:
            f.write("The analysis appears sound, but spatial context is needed.")

    expert_agent = CancerBiologyExpertAgent()
    generated_interpretation = expert_agent.provide_interpretation(output_directory)
    if generated_interpretation:
        print("\n--- GENERATED BIOLOGICAL INTERPRETATION REPORT (Preview) ---")
        # Print the first 10 lines of the report
        print("\n".join(generated_interpretation.splitlines()[:10]))
        print("...")
        print("------------------------------------------------------------")

