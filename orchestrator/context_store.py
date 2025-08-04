"""
Context Store Module - Maintains context continuity across all stages
"""
import time
import re
from typing import Dict, List, Any, Optional, Set

class ContextStore:
    def __init__(self):
        self.query_details: Dict[str, Any] = {}
        self.dna_sequences: Dict[str, str] = {}
        self.hypotheses: List[Dict[str, str]] = []
        self.tool_results: List[Dict[str, Any]] = []
        self.findings: List[Dict[str, str]] = []
        self.references: Dict[str, Any] = {}
        self.timestamps: Dict[str, float] = {}
        self.history: List[Dict[str, Any]] = []
        self.stage: str = "initialization"

    def log_query(self, query: str) -> None:
        """Store the initial user query"""
        self.query_details["raw_query"] = query
        self.timestamps["query"] = time.time()
        self.stage = "query"
        self._extract_entities_from_query(query)
        self._log_history("query", {"query": query})

    def _extract_entities_from_query(self, query: str) -> None:
        """Extract important entities from the query"""
        # Extract DNA sequences
        dna_matches = re.findall(r'([ATGC]{10,})', query, re.IGNORECASE)
        for i, seq in enumerate(dna_matches):
            seq_id = f"sequence_{i+1}"
            self.dna_sequences[seq_id] = seq.upper()
            self.query_details[f"dna_sequence_{i+1}"] = seq.upper()
        
        # Extract other potential entities
        if "coding" in query.lower():
            self.query_details["focus_coding"] = True
        if "protein" in query.lower():
            self.query_details["focus_protein"] = True
        if "homolog" in query.lower() or "similar" in query.lower():
            self.query_details["focus_homology"] = True

    def add_clarification(self, question: str, options: List[str]) -> None:
        """Store a clarification question and its options"""
        clarification = {
            "question": question,
            "options": options,
            "timestamp": time.time()
        }
        if "clarifications" not in self.query_details:
            self.query_details["clarifications"] = []
        
        self.query_details["clarifications"].append(clarification)
        self.stage = "clarification"
        self._log_history("clarification", clarification)

    def add_user_response(self, response: str) -> None:
        """Store user response to clarification"""
        if "user_responses" not in self.query_details:
            self.query_details["user_responses"] = []
        
        self.query_details["user_responses"].append({
            "response": response,
            "timestamp": time.time()
        })
        self._log_history("user_response", {"response": response})

    def add_research_brief(self, focus: str, hypotheses: List[str]) -> None:
        """Store research brief information"""
        brief = {
            "focus": focus,
            "hypotheses": hypotheses,
            "timestamp": time.time()
        }
        
        self.hypotheses.extend([{"text": h, "status": "untested"} for h in hypotheses])
        self.stage = "research_brief"
        self._log_history("research_brief", brief)

    def add_tool_result(self, tool_name: str, inputs: Dict[str, Any], 
                       result: Any, interpretation: str) -> None:
        """Store results from research tools"""
        tool_result = {
            "tool": tool_name,
            "inputs": inputs,
            "result": result,
            "interpretation": interpretation,
            "timestamp": time.time()
        }
        
        self.tool_results.append(tool_result)
        self._log_history("tool_result", tool_result)

    def update_hypothesis(self, hypothesis_idx: int, status: str, evidence: str) -> None:
        """Update a hypothesis with new evidence or status"""
        if 0 <= hypothesis_idx < len(self.hypotheses):
            self.hypotheses[hypothesis_idx]["status"] = status
            self.hypotheses[hypothesis_idx]["evidence"] = evidence
            self._log_history("hypothesis_update", {
                "hypothesis": self.hypotheses[hypothesis_idx]["text"],
                "status": status,
                "evidence": evidence
            })

    def add_key_finding(self, finding: str, evidence: str, importance: str = "medium") -> None:
        """Add a key finding with supporting evidence"""
        finding_entry = {
            "text": finding,
            "evidence": evidence,
            "importance": importance,
            "timestamp": time.time()
        }
        
        self.findings.append(finding_entry)
        self._log_history("key_finding", finding_entry)

    def add_summary(self, summary_text: str, key_points: List[str]) -> None:
        """Add a summary of findings"""
        summary = {
            "text": summary_text,
            "key_points": key_points,
            "timestamp": time.time()
        }
        
        self.stage = "summarization"
        self._log_history("summary", summary)

    def add_compressed_finding(self, compressed_text: str) -> None:
        """Add compressed findings"""
        compressed = {
            "text": compressed_text,
            "timestamp": time.time()
        }
        
        self.stage = "compression"
        self._log_history("compressed_finding", compressed)

    def set_final_report(self, conclusion: str, next_steps: List[str]) -> None:
        """Set the final report conclusion and next steps"""
        report = {
            "conclusion": conclusion,
            "next_steps": next_steps,
            "timestamp": time.time()
        }
        
        self.stage = "final_report"
        self._log_history("final_report", report)

    def _log_history(self, event_type: str, data: Dict[str, Any]) -> None:
        """Log an event to the history with timestamp"""
        self.history.append({
            "event_type": event_type,
            "data": data,
            "stage": self.stage,
            "timestamp": time.time()
        })

    def validate_references(self, text: str) -> bool:
        """
        Validate that a response properly references context
        Returns True if valid, False if missing references
        """
        if not text:
            return False
            
        # Check if any DNA sequences are referenced
        for seq_id, sequence in self.dna_sequences.items():
            # Check for full sequence or first 10 characters with ellipsis
            if sequence in text or (len(sequence) > 10 and f"{sequence[:10]}..." in text):
                return True
                
        # Check if hypothesis texts are referenced
        for hypothesis in self.hypotheses:
            if hypothesis["text"] in text:
                return True
                
        # Check if tool results are referenced
        for result in self.tool_results:
            tool_name = result["tool"]
            if tool_name in text:
                return True
                
        # Check if findings are referenced
        for finding in self.findings:
            if finding["text"] in text:
                return True
                
        # If we've reached this point with no references found, it's invalid
        return False

    def get_context_for_stage(self, stage: str) -> Dict[str, Any]:
        """Get relevant context data for a specific stage"""
        context = {
            "query": self.query_details.get("raw_query", ""),
            "stage": stage,
            "dna_sequences": self.dna_sequences,
        }
        
        if stage == "clarification":
            # For clarification, include extracted entities from query
            context["extracted_entities"] = {
                k: v for k, v in self.query_details.items() 
                if k not in ["raw_query", "clarifications", "user_responses"]
            }
            
        elif stage == "research_brief":
            # For research brief, include clarifications and user responses
            context["clarifications"] = self.query_details.get("clarifications", [])
            context["user_responses"] = self.query_details.get("user_responses", [])
            
        elif stage in ["parallel_research", "tool_execution"]:
            # For researchers, include hypotheses
            context["hypotheses"] = self.hypotheses
            context["research_focus"] = self.history[-1]["data"]["focus"] if self.history and self.history[-1]["event_type"] == "research_brief" else ""
            
        elif stage == "summarization":
            # For summarization, include tool results and hypotheses
            context["tool_results"] = self.tool_results
            context["hypotheses"] = self.hypotheses
            
        elif stage == "compression":
            # For compression, include findings and summary
            context["findings"] = self.findings
            latest_summary = next((h["data"] for h in reversed(self.history) if h["event_type"] == "summary"), None)
            context["summary"] = latest_summary if latest_summary else {}
            
        elif stage == "final_report":
            # For final report, include everything
            context["findings"] = self.findings
            context["tool_results"] = self.tool_results
            context["hypotheses"] = self.hypotheses
            compressed = next((h["data"] for h in reversed(self.history) if h["event_type"] == "compressed_finding"), None)
            context["compressed"] = compressed if compressed else {}
            
        return context

class ChatboxValidator:
    """Validator class to enforce context references and prevent vague language"""
    
    # List of vague terms that should be avoided
    VAGUE_TERMS = [
        "deep dive", "explore further", "look into", "consider investigating",
        "future analysis", "additional research", "further investigation",
        "might be worth", "could potentially", "might want to consider"
    ]
    
    # Terms that suggest external tabs
    EXTERNAL_TERMS = [
        "log tab", "logs tab", "results tab", "external tab", "see logs",
        "check the log", "view results in", "results panel", "status panel"
    ]
    
    @classmethod
    def validate_message(cls, message: str, context_store: ContextStore) -> Dict[str, Any]:
        """
        Validates a message against several criteria
        Returns a dict with 'valid' status and reasons if invalid
        """
        result = {"valid": True, "reasons": []}
        
        # Check for context references
        if not context_store.validate_references(message):
            result["valid"] = False
            result["reasons"].append("Message does not reference contextual data")
        
        # Check for vague language
        vague_terms_found = [term for term in cls.VAGUE_TERMS if term.lower() in message.lower()]
        if vague_terms_found:
            result["valid"] = False
            result["reasons"].append(f"Message contains vague terms: {', '.join(vague_terms_found)}")
        
        # Check for external tab references
        external_terms_found = [term for term in cls.EXTERNAL_TERMS if term.lower() in message.lower()]
        if external_terms_found:
            result["valid"] = False
            result["reasons"].append(f"Message references external tabs: {', '.join(external_terms_found)}")
        
        return result