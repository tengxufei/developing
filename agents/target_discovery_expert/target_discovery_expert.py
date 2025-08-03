# Target Discovery Expert Agent - Evaluates genes as potential therapeutic targets.
import os
import sys
import pandas as pd
import json

# Add the orchestrator directory to the Python path to import the Bedrock client
orchestrator_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "orchestrator"))
sys.path.append(orchestrator_dir)

from bedrock_client import get_langchain_bedrock_llm

class TargetDiscoveryExpertAgent:
    def __init__(self):
        self.llm = get_langchain_bedrock_llm()

    def _create_target_evaluation_prompt(self, gene):
        """Creates a detailed prompt for evaluating a single gene target."""
        return f"""
        You are a senior scientist in a pharmaceutical oncology R&D division.
        Your task is to evaluate the potential of a single gene, **{gene}**, as a therapeutic target for cancer, specifically in the context of gliomas like Astroblastoma.

        Please provide a concise but comprehensive evaluation based on the following four criteria. Structure your response as a JSON object with the specified keys.

        1.  **Role in Cancer Pathway (role_in_cancer):**
            - Is this gene a known oncogene, tumor suppressor, or part of a critical cancer-related pathway?
            - Briefly describe its mechanism in gliomas if known.

        2.  **Expression Profile (expression_profile):**
            - Is this gene typically overexpressed in tumor tissue compared to essential normal tissues?
            - A good target should have a high therapeutic window (high expression in tumor, low in healthy tissue).

        3.  **Druggability (druggability):**
            - Does the protein product of this gene belong to a class that is considered 'druggable'? (e.g., kinases, cell surface receptors, enzymes).
            - Are there known binding pockets or allosteric sites?

        4.  **Clinical Precedent (clinical_precedent):**
            - Are there any existing FDA-approved drugs or clinical trials (Phase I, II, or III) targeting this gene or its pathway?
            - Mention specific drug names if possible.

        5.  **Overall Score and Recommendation (recommendation):**
            - Provide a final score from 1 (poor target) to 10 (excellent target).
            - Write a brief, one-sentence summary recommendation.

        **Provide your response as a single, valid JSON object only.**
        Example format:
        {{
            "gene": "{gene}",
            "role_in_cancer": "...",
            "expression_profile": "...",
            "druggability": "...",
            "clinical_precedent": "...",
            "recommendation": {{
                "score": 8,
                "summary": "A promising target due to its critical role and existing clinical validation."
            }}
        }}
        """

    def analyze_targets(self, gene_list, output_dir):
        """
        Analyzes a list of genes and evaluates their potential as therapeutic targets.
        """
        print(f"Target Discovery Expert: Analyzing {len(gene_list)} potential targets.")
        
        all_evaluations = []
        for gene in gene_list:
            print(f"  - Evaluating gene: {gene}")
            prompt = self._create_target_evaluation_prompt(gene)
            
            try:
                response = self.llm.invoke(prompt)
                # Clean the response to ensure it's valid JSON
                clean_response = response.content.strip().replace('`', '')
                if clean_response.startswith("json"):
                    clean_response = clean_response[4:]
                
                evaluation = json.loads(clean_response)
                all_evaluations.append(evaluation)
            except Exception as e:
                print(f"    - ERROR: Failed to evaluate {gene}. Reason: {e}")
                # Add a failed record to the list
                all_evaluations.append({
                    "gene": gene, "error": str(e), 
                    "recommendation": {"score": 0, "summary": "Failed to process."}
                })

        # Sort the evaluations by the recommendation score in descending order
        sorted_evaluations = sorted(all_evaluations, key=lambda x: x.get('recommendation', {}).get('score', 0), reverse=True)

        # --- Generate Markdown Report ---
        report_md = "# Therapeutic Target Discovery Report\n\n"
        report_md += "This report provides an evaluation of potential therapeutic targets based on their role in cancer, expression profile, druggability, and clinical precedent.\n\n"

        for eval_data in sorted_evaluations:
            gene = eval_data.get('gene', 'N/A')
            score = eval_data.get('recommendation', {}).get('score', 0)
            summary = eval_data.get('recommendation', {}).get('summary', 'N/A')
            
            report_md += f"## Target: {gene}\n"
            report_md += f"**Overall Score:** {score}/10\n"
            report_md += f"**Recommendation:** {summary}\n\n"
            report_md += "| Criterion            | Analysis                                      |\n"
            report_md += "|----------------------|-----------------------------------------------|\n"
            report_md += f"| Role in Cancer       | {eval_data.get('role_in_cancer', 'N/A')}      |\n"
            report_md += f"| Expression Profile   | {eval_data.get('expression_profile', 'N/A')}  |\n"
            report_md += f"| Druggability         | {eval_data.get('druggability', 'N/A')}        |\n"
            report_md += f"| Clinical Precedent   | {eval_data.get('clinical_precedent', 'N/A')}  |\n\n"
            report_md += "---\n\n"

        # Save the report
        report_path = os.path.join(output_dir, "target_discovery_report.md")
        with open(report_path, "w") as f:
            f.write(report_md)
            
        print(f"Target Discovery Expert: Analysis complete. Report saved to {report_path}")

if __name__ == '__main__':
    # Example Usage
    # This allows running the agent directly for testing purposes
    
    # Create a dummy output directory if it doesn't exist
    output_directory = "../../output" # Relative path for example
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Example gene list - in a real run, this would come from the marker gene file
    example_genes = ["EGFR", "PTEN", "CDK4", "MDM2", "MYC"]
    
    agent = TargetDiscoveryExpertAgent()
    agent.analyze_targets(gene_list=example_genes, output_dir=output_directory)
