# Main Orchestrator - Simulates a real-time, reasoning-based multi-agent scientific team
from dotenv import load_dotenv
import os
import sys
import json
import queue
import threading
import time
import re
from typing import Any, Dict, List, Tuple

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
        self.conversation_history = [] # Stores {'agent': ..., 'message': ..., 'entities': ...}
        self.last_prompt_details = {}

    def _extract_entities(self, message: str) -> Dict[str, Any]:
        entities = {}
        dna_match = re.search(r'([ATGC]{10,})', message, re.IGNORECASE)
        if dna_match: entities['dna_sequence'] = dna_match.group(1).upper()
        # Add more entity extraction logic here as needed
        return entities

    def _log(self, agent: str, message: str):
        """Helper function to send a structured, timestamped log message to the frontend and store context."""
        if self.q:
            timestamp = time.strftime("[%H:%M:%S]")
            log_entry = f"{timestamp} **{agent}:** {message}"
            self.q.put(json.dumps({"type": "log", "content": log_entry}))
            self.conversation_history.append({'agent': agent, 'message': message, 'entities': self._extract_entities(message)})
            time.sleep(1.6 + (len(message) / 100.0) * 0.7) # Slower, more pensive pace

    def _send_final_report(self, report_content: str):
        """This function is no longer used as all information lives in the chatbox."""
        pass

    def _send_chat_message(self, message: str):
        """Sends a conversational message to the user in the chat window."""
        if self.q:
            self.q.put(json.dumps({"type": "chat_message", "content": message}))
            
    def _send_report(self, content: str):
        """Sends detailed results to the Results tab."""
        if self.q:
            self.q.put(json.dumps({"type": "report", "content": content}))

    def _update_status(self, stage: str, status: str, message: str):
        """Updates the high-level status in the UI's Status tab."""
        if self.q:
            self.q.put(json.dumps({"type": "status", "stage": stage, "status": status, "message": message}))

    def _get_context_prefix(self, current_agent: str, current_prompt_entities: Dict[str, Any], is_initial_query: bool) -> str:
        """Generates a context-referencing prefix for an agent's message, enforcing context chains."""
        if is_initial_query: return ""
        if not self.conversation_history: return ""

        # Try to find a direct reference to the current prompt's main entity (A2 referencing A1's entity)
        if 'dna_sequence' in current_prompt_entities:
            seq = current_prompt_entities['dna_sequence']
            for entry in reversed(self.conversation_history):
                if 'dna_sequence' in entry['entities'] and entry['entities']['dna_sequence'] == seq:
                    return f"Referring to the {len(seq)}-nt sequence '{seq[:10]}...' from our previous conversation, "

        # Fallback to general recent context
        for i in range(len(self.conversation_history) - 1, -1, -1):
            entry = self.conversation_history[i]
            if entry['agent'] != current_agent: # Avoid self-referencing immediately
                # Check if the message is substantial enough to reference
                if len(entry['message']) > 20:
                    return f"Following up on {entry['agent']}'s point about '{entry['message'][:30]}...', "
                else: # If message is too short, try to find a more substantial one
                    continue
        
        return ""

    def _reasoning_engine(self, prompt: str):
        """A dynamic, real-time reasoning engine that thinks aloud to solve a user's query."""
        is_follow_up = bool(self.conversation_history)
        current_prompt_entities = self._extract_entities(prompt)

        if not is_follow_up:
            self.conversation_history = []
            self._update_status("Deconstruction", "processing", "Agents are deconstructing the query...")
        else:
            self._update_status("Contextualizing", "processing", "Agents are contextualizing the follow-up query...")
            a1_main_entity_str = ""
            for entry in reversed(self.conversation_history):
                if 'dna_sequence' in entry['entities']:
                    seq = entry['entities']['dna_sequence']
                    a1_main_entity_str = f"the DNA sequence '{seq[:10]}...'"
                    break
            self._log("PI Agent", f"Contextualizing follow-up query: '{prompt}'. Connecting to previous analysis of {a1_main_entity_str}.")

        central_topic = ""
        implied_detail = ""
        domain = ""
        specialist_role = ""
        prompt_lower = prompt.lower()
        dna_match = re.search(r'([ATGC]{10,})', prompt, re.IGNORECASE)

        if "pcr failing" in prompt_lower:
            central_topic = "PCR troubleshooting"
            implied_detail = "technical/protocol-specific"
            domain = "molecular biology"
            specialist_role = "PCR Troubleshooting Specialist"
        elif dna_match:
            central_topic = "DNA sequence analysis"
            implied_detail = "structural/functional characterization"
            domain = "bioinformatics"
            specialist_role = "Sequence Analysis Expert"
        elif "protein folding" in prompt_lower:
            central_topic = "protein folding mechanisms"
            implied_detail = "conceptual/biophysical"
            domain = "structural biology"
            specialist_role = "Protein Folding Expert"
        elif "nitrogen fixation" in prompt_lower:
            central_topic = "biological nitrogen fixation"
            implied_detail = "conceptual/mechanistic"
            domain = "plant physiology/microbiology"
            specialist_role = "Nitrogen Cycle Biologist"
        elif "coding element" in prompt_lower and is_follow_up and 'dna_sequence' in current_prompt_entities:
            central_topic = f"coding element properties of {current_prompt_entities['dna_sequence']}"
            implied_detail = "functional characterization"
            domain = "molecular biology/genetics"
            specialist_role = "Geneticist"
        else:
            central_topic = prompt
            implied_detail = "general conceptual"
            domain = "general biology"
            specialist_role = "General Biological Scientist"

        self.last_prompt_details = {
            'central_topic': central_topic,
            'implied_detail': implied_detail,
            'domain': domain,
            'specialist_role': specialist_role,
            'entities': current_prompt_entities
        }

        if not is_follow_up:
            initial_chat_message_prefix = f"For your query about '{prompt}', "
        else:
            a1_main_entity_str = ""
            for entry in reversed(self.conversation_history):
                if 'dna_sequence' in entry['entities']:
                    seq = entry['entities']['dna_sequence']
                    a1_main_entity_str = f"the DNA sequence '{seq[:10]}...'"
                    break
            if a1_main_entity_str:
                initial_chat_message_prefix = f"You asked earlier about analyzing {a1_main_entity_str}, and now want to know about '{prompt}'. Let's connect this to what we already know about the sequence. "
            else:
                initial_chat_message_prefix = f"Regarding your question about '{prompt}', "

        self._log("PI Agent", f"Deconstructing query: '{prompt}'. Central topic: {central_topic}. Implied detail: {implied_detail}. Domain: {domain}. Activating {specialist_role}.")
        self._send_chat_message(initial_chat_message_prefix + f"I'd say the central topic is: {central_topic}. The implied level of detail seems to be {implied_detail}, and it falls within the domain of {domain}. I'm activating our {specialist_role}.")
        self._update_status("Generating Execution Steps", "processing", "Agents are defining actionable steps...")
        
        execution_steps = []
        if central_topic == "PCR troubleshooting":
            self._log(specialist_role, "For PCR troubleshooting, my first thought is to verify the master mix and thermocycler. This rules out general issues before we dive into primer specifics.")
            execution_steps.append({'action': 'Verify PCR master mix and thermocycler functionality', 'justification': 'Before troubleshooting primer/template issues, it\'s crucial to rule out general PCR component or equipment failure.', 'success_metric': 'Successful amplification of a known positive control template.', 'details': 'Run a PCR with a well-characterized positive control template and primers.'})
            self._log("Scientific Critic", "And if that works, then we need to consider the template and primers. For a short template, primer-dimer formation is a common culprit.")
            execution_steps.append({'action': 'Redesign primers for short template', 'justification': 'For a 17-nt template, standard 18-22 nt primers are likely too long, leading to primer-dimer formation or poor annealing.', 'success_metric': 'New primers (e.g., 15 nt) designed with optimal Tm and minimal self-complementarity.', 'details': 'Design primers of ~15 nt, ensuring Tm is around 50-55°C. Use an oligo analysis tool to check for secondary structures.'})
        elif central_topic == "DNA sequence analysis":
            sequence = current_prompt_entities.get('dna_sequence', '')
            seq_len = len(sequence)
            self._log(specialist_role, f"For the {seq_len}-nt DNA sequence, the first step is always characterization. I\'ll calculate the precise GC content.")
            execution_steps.append({'action': 'Calculate precise GC content', 'justification': f'GC content impacts DNA stability and can provide clues about the sequence\'s origin (e.g., high GC for some bacteria). For the {seq_len}-nt sequence, this is a fundamental characterization step.', 'success_metric': 'Accurate percentage of G and C bases in the sequence.', 'details': f'Count G and C bases in {sequence} and divide by {seq_len}.'})
            self._log("Scientific Critic", "And while doing that, let\'s also scan for functional motifs. An ATG start codon or restriction sites would be highly informative for this specific sequence.")
            execution_steps.append({'action': 'Perform six-frame translation and ORF scan', 'justification': f'To assess potential coding regions, all six reading frames must be examined. The {seq_len}-nt length suggests a partial ORF if coding.', 'success_metric': 'Identification of any Open Reading Frames (ORFs) and their characteristics (start/stop codons, length).', 'details': 'Use a bioinformatics tool or script to translate the sequence in all six frames. Note presence of ATG start codons.'})
            self._log(specialist_role, f"Given the {seq_len}-nt length, a standard BLAST search will be too noisy. We need to use `blastn-short`.")
            execution_steps.append({'action': 'Execute specialized BLAST search', 'justification': f'For a short {seq_len}-nt sequence, a standard BLAST search is prone to high noise. A specialized search is needed to find meaningful homologs.', 'success_metric': 'Identification of homologous sequences with high confidence (e.g., bitscore > 40, e-value < 1e-3) using appropriate parameters.', 'details': 'Run `blastn-short` against the NCBI nt database. Set `word_size=7` and adjust e-value/bitscore thresholds.'})
        elif central_topic == "coding element properties of " + current_prompt_entities.get('dna_sequence', ''):
            sequence = current_prompt_entities.get('dna_sequence', '')
            seq_len = len(sequence)
            self._log(specialist_role, f"For the {seq_len}-nt sequence, we need to confirm the ATG context. Is it a true start codon or just a random ATG?")
            execution_steps.append({'action': 'Confirm ATG start codon context', 'justification': f'While the {seq_len}-nt sequence has an ATG, its position and surrounding nucleotides need to be checked for a strong Kozak consensus (in eukaryotes) or Shine-Dalgarno sequence (in prokaryotes) to confirm true coding potential.', 'success_metric': 'Identification of ribosomal binding sites or consensus sequences adjacent to the ATG.', 'details': f'Analyze the {seq_len}-nt sequence around the ATG at position {sequence.find("ATG") + 1} for known ribosomal binding motifs.'})
            self._log("Scientific Critic", f"And given its {seq_len}-nt length, it\'s likely a partial coding element. We should search for the full gene.")
            execution_steps.append({'action': 'Search for homologous full-length genes', 'justification': f'Given the {seq_len}-nt sequence is likely a partial coding element, searching for longer homologs can reveal the full gene it belongs to.', 'success_metric': 'Identification of a larger gene containing the {seq_len}-nt sequence with high sequence identity.', 'details': f'Use BLAST (standard blastn) with the {seq_len}-nt sequence as query against genomic or mRNA databases.'})
        elif central_topic == "biological nitrogen fixation":
            self._log(specialist_role, "To understand nitrogen fixation, we should first identify the key organisms involved. Not all prokaryotes can do it.")
            execution_steps.append({'action': 'Identify key nitrogen-fixing organisms', 'justification': 'Nitrogen fixation is performed by specific prokaryotes. Identifying them is crucial for understanding the process.', 'success_metric': 'List of prominent free-living and symbiotic nitrogen-fixing bacteria/archaea.', 'details': 'Research common genera like *Rhizobium*, *Azotobacter*, *Frankia*, and their associated plant hosts.'})
            self._log("Scientific Critic", "And then, we must understand the central enzyme: nitrogenase. Its oxygen sensitivity is a critical aspect.")
            execution_steps.append({'action': 'Describe the nitrogenase enzyme complex', 'justification': 'Nitrogenase is the central enzyme for nitrogen fixation. Understanding its structure and function is key.', 'success_metric': 'Explanation of nitrogenase components (Fe-protein, MoFe-protein) and its oxygen sensitivity.', 'details': 'Detail the two main components and how oxygen exclusion is achieved (e.g., leghemoglobin in legumes).'})
        else:
            self._log(specialist_role, f"For a broad query like {central_topic}, we need to break it down into actionable sub-questions.")
            execution_steps.append({'action': f'Deconstruct \'{central_topic}\' into sub-questions', 'justification': 'For broad queries, breaking them into smaller, actionable questions allows for systematic analysis.', 'success_metric': 'A list of 2-3 specific, answerable sub-questions related to the query.', 'details': 'Identify key terms and concepts in the query and formulate questions around them.'})
            self._log("Scientific Critic", "And we need to know where to find the information. Identifying relevant databases is crucial.")
            execution_steps.append({'action': f'Identify relevant biological databases or resources for \'{central_topic}\'', 'justification': 'Knowing where to find information is the first step in any biological inquiry.', 'success_metric': 'A list of 2-3 appropriate databases, tools, or literature sources.', 'details': 'Suggest resources like NCBI, UniProt, PDB, specific review articles, or textbooks.'})

        escaped_prompt = prompt.replace("'", "\\'")
        # Create a shorter, more concise chat response
        final_chat_response = f"Analysis of '{escaped_prompt}':\n\n"
        final_chat_response += f"• **Topic:** {central_topic}\n"
        final_chat_response += f"• **Specialist:** {specialist_role}\n\n"
        
        final_chat_response += "**Key Steps:**\n"
        for i, step in enumerate(execution_steps):
            final_chat_response += f"{i+1}. {step['action']}\n"
            
        # Create more detailed content for the results tab
        results_content = f"# Analysis Report for: '{escaped_prompt}'\n\n"
        results_content += f"**Central Topic:** {central_topic}\n"
        results_content += f"**Implied Detail:** {implied_detail}\n"
        results_content += f"**Domain:** {domain}\n"
        results_content += f"**Specialist Activated:** {specialist_role}\n\n"
        
        results_content += "## Proposed Execution Steps\n"
        for i, step in enumerate(execution_steps):
            results_content += f"\n### {i+1}. {step['action']}\n"
            results_content += f"**Justification:** {step['justification']}\n"
            results_content += f"**Success Metric:** {step['success_metric']}\n"
            if step.get('details'):
                results_content += f"**Details:** {step['details']}\n"

        self._update_status("Dialogue Complete", "completed", "Initial analysis complete. Awaiting further input.")
        self._send_chat_message(final_chat_response)
        self._send_report(results_content)

    def stream_bioinformatics_task(self, prompt: str):
        """
        Runs the agent simulation in a separate thread and streams the dialogue to the client.
        """
        self.q = queue.Queue()

        def run_simulation_thread():
            try:
                self._reasoning_engine(prompt)
            except Exception as e:
                import traceback
                tb_str = traceback.format_exc()
                error_message = f"An error occurred during the simulation: {e}\n{tb_str}"
                self._log("Orchestrator", error_message)
                self._update_status("Error", "error", str(e))
            finally:
                self.q.put(json.dumps({"type": "close", "message": "Stream finished"}))
                self.q.put(None)

        thread = threading.Thread(target=run_simulation_thread)
        thread.start()

        while True:
            item = self.q.get()
            if item is None:
                break
            yield item