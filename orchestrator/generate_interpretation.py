import sys
sys.path.append('orchestrator')
from bedrock_client import BedrockClient

def generate_interpretation():
    """
    Generates a biological interpretation of the TCGA co-expression analysis.
    """
    bedrock_client = BedrockClient()

    prompt = f"""
    You are a world-class Cancer Biologist and Bioinformatician with deep expertise in Glioblastoma (GBM).
    An analysis of the TCGA-GBM dataset revealed that the genes CD276 (B7H3), DLL3, and SEZ6 are co-expressed in 100% of primary tumor samples (using a TPM > 1 threshold).

    **INPUT DATA:**
    - **Genes:** CD276 (B7H3), DLL3, SEZ6
    - **Tumor Type:** Glioblastoma (GBM)
    - **Finding:** 100% of tumors show co-expression of all three genes. The genes are also highly correlated.

    **INSTRUCTIONS:**
    Please provide a detailed biological interpretation of this finding. Structure your report as follows:

    **--- START OF REPORT ---**

    **1. EXECUTIVE SUMMARY:**
    Provide a high-level summary of the potential significance of the universal co-expression of these three genes in GBM.

    **2. GENE-SPECIFIC ROLES IN GLIOBLASTOMA:**
    For each gene (CD276, DLL3, SEZ6), briefly describe its known or hypothesized role in cancer, particularly in GBM if possible.

    **3. HYPOTHESES FOR CO-REGULATION AND FUNCTIONAL INTERPLAY:**
    Based on their individual roles, propose 2-3 hypotheses to explain their consistent co-expression.
    - Could they be part of the same signaling pathway?
    - Might they be transcriptionally co-regulated by a common master transcription factor?
    - Could their functions be synergistic in promoting GBM progression (e.g., one handles immune evasion, another proliferation)?

    **4. POTENTIAL THERAPEUTIC IMPLICATIONS:**
    Discuss the therapeutic potential of targeting these co-expressed genes.
    - Does the high co-expression suggest a vulnerability that could be exploited?
    - Could a multi-target therapy (e.g., a bispecific antibody or combination therapy) be a viable strategy?
    - What are the risks and challenges associated with targeting these genes in GBM?

    **5. PROPOSED VALIDATION EXPERIMENTS:**
    What are the key experiments needed to validate this co-expression pattern at the cellular level and to test your functional hypotheses?
    - Example: "Use multiplex immunofluorescence or spatial transcriptomics on GBM tissue samples to confirm co-expression on the same tumor cells."

    **--- END OF REPORT ---**
    """

    interpretation = bedrock_client.invoke_model(prompt)

    with open("output/TCGA_coexpression_biological_interpretation.md", "w") as f:
        f.write(interpretation)

    print("Biological interpretation report generated and saved to output/TCGA_coexpression_biological_interpretation.md")
    print(interpretation)

if __name__ == "__main__":
    generate_interpretation()
