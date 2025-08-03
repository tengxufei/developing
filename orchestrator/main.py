# Main Orchestrator - Simulates a multi-agent scientific collaboration
from dotenv import load_dotenv
import os
import sys
import json
import queue
import threading
import time
import re
from typing import Any, Dict, List

# Add the project root to the Python path for module discovery
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

load_dotenv()

class Orchestrator:
    def __init__(self, base_dir):
        self.base_dir = base_dir
        self.output_dir = os.path.join(base_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)
        self.q = None

    def _log(self, agent: str, message: str):
        """Helper function to send a structured, timestamped log message to the frontend."""
        if self.q:
            timestamp = time.strftime("[%H:%M:%S]")
            log_entry = f"{timestamp} **{agent}:** {message}"
            self.q.put(json.dumps({"type": "log", "content": log_entry}))
            # Simulate the natural pause of a conversation
            time.sleep(1.5 + (len(message) / 100.0) * 0.5) # Scale delay by message length

    def _send_final_report(self, report_content: str):
        """Sends the final, polished report to the UI's Results tab."""
        if self.q:
            self.q.put(json.dumps({"type": "report", "content": report_content}))

    def _send_chat_message(self, message: str):
        """Sends a conversational message to the user in the chat window."""
        if self.q:
            self.q.put(json.dumps({"type": "chat_message", "content": message}))

    def _update_status(self, stage: str, status: str, message: str):
        """Updates the high-level status in the UI's Status tab."""
        if self.q:
            self.q.put(json.dumps({"type": "status", "stage": stage, "status": status, "message": message}))

    def _simulate_qpcr_dialogue(self, gene_name):
        """Generates a simulated dialogue specifically for qPCR primer design."""
        self._update_status("Task Framing", "processing", "Orchestrator is defining the task...")
        self._log("Orchestrator", f"Team, the task is to design a robust set of qPCR primers for the gene '{gene_name}'. This is a critical first step, so let's be thorough. MolecularBiologist, what are your initial thoughts on the parameters?")
        
        self._update_status("Methodology Debate", "processing", "Agents are discussing the approach...")
        self._log("MolecularBiologist", f"Standard parameters apply: length of 18-22 bp, Tm around 60-64°C, and a GC content of 40-60%. But for {gene_name}, we need to be extra careful about splice variants. We must target a constitutive exon.")
        
        self._log("Bioinformatician", f"I agree. I can pull the transcript data for {gene_name} from Ensembl and RefSeq. I'll align them to identify exons present in all major isoforms. That should be our target region.")

        self._log("ScientificCritic", "Before we do that, let's consider the source. Is RefSeq sufficient, or should we also check the UCSC Genome Browser for more comprehensive annotations? Sometimes one database misses a rare but functionally important isoform. Let's not introduce a blind spot at step one.")

        self._log("Bioinformatician", "Good point. Cross-referencing is better. It will take a few more minutes, but it's worth it. I'll pull from all three and create a consensus exon map.")

        self._update_status("Action Plan", "processing", "Agents are defining concrete steps...")
        self._log("MolecularBiologist", "Once we have that consensus exon, I'll need to check for SNPs. We don't want a polymorphism in our primer binding site, as that would kill our amplification efficiency for certain alleles. I'll run the target sequence through dbSNP.")

        self._log("ScientificCritic", "And what about off-target binding? A BLAST search against the human transcriptome is non-negotiable. The primers must be unique to {gene_name}.")

        self._log("Orchestrator", "Excellent. We have a clear, rigorous plan. To summarize the next steps: 1) Bioinformatician will create a consensus exon map for {gene_name} from RefSeq, Ensembl, and UCSC. 2) MolecularBiologist will then scan that region for SNPs. 3) Finally, we will design primers within a clean, constitutive region and validate their specificity via BLAST. Let's start with the exon mapping.")

        # The final report is a summary of the *plan*, not results.
        final_report_content = f"### Plan for Designing qPCR Primers for {gene_name}\n\n**Objective:** To design a highly specific and efficient set of qPCR primers for the gene {gene_name}.\n\n**Methodology Outline:**\n1.  **Identify Constitutive Exons:** Align transcript data from RefSeq, Ensembl, and the UCSC Genome Browser to identify exons common to all major isoforms of {gene_name}.\n2.  **SNP Avoidance:** The selected exon region will be checked against dbSNP to ensure primer binding sites do not overlap with known single nucleotide polymorphisms.\n3.  **Primer Design:** Primers will be designed with standard parameters (18-22 bp length, 60-64°C Tm, 40-60% GC content) within the validated exon region.\n4.  **Specificity Validation:** The final primer candidates will be subjected to a BLAST search against the human transcriptome to ensure they do not have significant off-target binding sites."

        self._send_final_report(final_report_content)
        self._send_chat_message(f"We have formulated a detailed plan for designing the {gene_name} primers. The proposed methodology is now available in the 'Results' tab. Shall we proceed with the first step?")

    def _simulate_generic_dialogue(self, task_prompt):
        """Generates a generic but query-relevant dialogue for any other biological task."""
        self._update_status("Task Framing", "processing", "Orchestrator is defining the task...")
        self._log("Orchestrator", f"Okay team, we have a new request: '{task_prompt}'. This is complex, so let's break it down methodically. ExpertAgent, what's your initial interpretation of this query? What are the core scientific questions we need to address?")

        self._update_status("Methodology Debate", "processing", "Agents are discussing the approach...")
        self._log("ExpertAgent", "My interpretation is that the user wants to understand the fundamental process for tackling this problem. The first step is always to define the scope. What are the knowns and unknowns? For instance, what data sources are available and what are their limitations?")

        self._log("CriticAgent", "I agree. Before we propose a single step, we must question the premise. Is the user's query based on a sound assumption? Are there alternative interpretations we should consider? For example, if the query is about analyzing data, we must first discuss data quality control, normalization, and potential batch effects. Rushing to analysis is how we get misleading results.")

        self._update_status("Action Plan", "processing", "Agents are defining concrete steps...")
        self._log("Orchestrator", "Excellent points. So, our first phase is purely about planning and risk assessment. Let's outline the initial steps for how we would *approach* this, not solve it. Step 1: Clearly define the biological question. Step 2: Identify and validate the necessary input data. Step 3: Debate and select the most appropriate analytical methods, considering the points raised by the Critic. Let's begin by formalizing the biological question.")

        final_report_content = f"### Methodological Approach for: {task_prompt}\n\n**Objective:** To outline a rigorous and transparent scientific process to address the user's query.\n\n**Phase 1: Scoping and Planning**\n1.  **Question Definition:** Collaboratively refine the user's query into a precise, testable scientific question.\n2.  **Data Vetting:** Identify the required data types and sources. Establish a protocol for quality control and validation before any analysis is performed.\n3.  **Methodological Debate:** Discuss the pros and cons of various analytical tools and approaches relevant to the query. The Scientific Critic will lead a pre-mortem analysis to identify potential pitfalls and biases in each proposed method."

        self._send_final_report(final_report_content)
        self._send_chat_message("We have outlined a high-level strategic plan for how to approach your query. The focus is on ensuring a rigorous and well-planned scientific process. The plan is now in the 'Results' tab.")

    def stream_bioinformatics_task(self, prompt: str):
        """
        Runs the agent simulation in a separate thread and streams the dialogue to the client.
        """
        self.q = queue.Queue()

        def run_simulation_thread():
            try:
                # Check for specific keywords to trigger a specialized dialogue
                if "qpcr" in prompt.lower() and "primer" in prompt.lower():
                    gene_match = re.search(r"for (\w+)", prompt, re.IGNORECASE)
                    gene_name = gene_match.group(1) if gene_match else "a target gene"
                    self._simulate_qpcr_dialogue(gene_name)
                else:
                    self._simulate_generic_dialogue(prompt)

            except Exception as e:
                error_message = f"An error occurred during the simulation: {e}"
                self._log("Orchestrator", error_message)
                self._update_status("Error", "error", str(e))
            finally:
                # Signal completion to the frontend
                self._update_status("Processing Complete", "completed", "Workflow finished.")
                self.q.put(json.dumps({"type": "close", "message": "Stream finished"}))
                self.q.put(None) # Sentinel to close the stream

        thread = threading.Thread(target=run_simulation_thread)
        thread.start()

        # Yield messages from the queue as they become available
        while True:
            item = self.q.get()
            if item is None:
                break
            yield item
