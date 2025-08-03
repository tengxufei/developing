import sys
sys.path.append('orchestrator')
from bedrock_client import BedrockClient

def generate_critique():
    """
    Generates a scientific critique of the TCGA co-expression analysis.
    """
    bedrock_client = BedrockClient()

    prompt = f"""
    You are a senior computational biologist acting as a scientific critic.
    An automated analysis was performed to assess the co-expression of the genes CD276, DLL3, and SEZ6 in the TCGA-GBM dataset.

    The analysis produced the following summary:
    ---
    TCGA Project: TCGA-GBM
    Genes Analyzed: CD276, DLL3, SEZ6
    Expression Threshold: TPM > 1

    Summary Statistics:
              Combination Num_Expressing Total_Samples Percentage
    1               CD276            372           372        100
    2                DLL3            372           372        100
    3                SEZ6            372           372        100
    4        CD276 + DLL3            372           372        100
    5        CD276 + SEZ6            372           372        100
    6         DLL3 + SEZ6            372           372        100
    7 CD276 + DLL3 + SEZ6            372           372        100
    ---

    Based on this information, please provide a critical review of the analysis.
    Focus on the following points:
    1.  **Methodology:** Is querying TCGA bulk RNA-seq data a valid approach for assessing co-expression? What are the inherent strengths and weaknesses of this method?
    2.  **Interpretation of Results:** The results show 100% co-expression for all combinations. How should this be interpreted? What are the potential artifacts or biological reasons for this observation?
    3.  **Limitations and Next Steps:** What are the major limitations of this analysis? What are the essential next steps to validate these findings and gain a deeper biological understanding? Suggest specific experiments.

    Provide a concise, critical review in a markdown format.
    """

    critique = bedrock_client.invoke_model(prompt)

    with open("output/TCGA_coexpression_critique.md", "w") as f:
        f.write(critique)

    print("Critique generated and saved to output/TCGA_coexpression_critique.md")
    print(critique)

if __name__ == "__main__":
    generate_critique()
