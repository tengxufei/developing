"""
Bedrock Multi-Agent Bioinformatics System
"""

from .core.coordinator import AgentCoordinator
from .agents.bio_agent import BioAgent
from .agents.analysis_agent import AnalysisAgent

__version__ = "0.1.0"
__all__ = ['AgentCoordinator', 'BioAgent', 'AnalysisAgent']
