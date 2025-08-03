from typing import Dict, List, Any, Optional
import boto3
from ..agents.bio_agent import BioAgent
from ..agents.analysis_agent import AnalysisAgent

class AgentCoordinator:
    """
    Coordinates multiple AI agents for bioinformatics analysis using AWS Bedrock
    """
    
    def __init__(self, 
                region_name: str = "us-east-1",
                profile_name: Optional[str] = None):
        # Initialize AWS session
        session = boto3.Session(
            profile_name=profile_name,
            region_name=region_name
        )
        self.bedrock = session.client('bedrock-runtime')
        
        # Initialize agents
        self.bio_agent = BioAgent(self.bedrock)
        self.analysis_agent = AnalysisAgent(self.bedrock)
        
    async def process_query(self, query: str) -> Dict[str, Any]:
        """
        Process a bioinformatics query using multiple agents
        """
        try:
            # Initial query processing by bio agent
            bio_response = await self.bio_agent.process_query(query)
            
            # If analysis needed, use analysis agent
            if bio_response.get("needs_analysis"):
                analysis_response = await self.analysis_agent.analyze(
                    bio_response["data"]
                )
                return self._combine_responses(bio_response, analysis_response)
            
            return bio_response
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def analyze_dataset(self, 
                            data_path: str,
                            analysis_type: str) -> Dict[str, Any]:
        """
        Analyze a biological dataset
        """
        try:
            # Initial data processing
            analysis_result = await self.analysis_agent.process_data(
                data_path,
                analysis_type
            )
            
            # Get biological interpretation
            interpretation = await self.bio_agent.interpret_results(
                analysis_result
            )
            
            return {
                "analysis": analysis_result,
                "interpretation": interpretation
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def _combine_responses(self,
                         bio_response: Dict[str, Any],
                         analysis_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine responses from multiple agents
        """
        return {
            "biological_context": bio_response.get("context"),
            "analysis_results": analysis_response.get("results"),
            "interpretation": bio_response.get("interpretation"),
            "suggestions": bio_response.get("suggestions"),
            "confidence": min(
                bio_response.get("confidence", 0),
                analysis_response.get("confidence", 0)
            )
        }
