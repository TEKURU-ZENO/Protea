"""
PROTEA AI Scientist - Multi-Agent System Module
Specialized agents for literature, knowledge, gaps, hypotheses, experiments, analysis, criticism, and writing.
"""

from ai.ai_scientist.agents.literature_agent import LiteratureAgent
from ai.ai_scientist.agents.knowledge_agent import KnowledgeAgent
from ai.ai_scientist.agents.gap_agent import GapAgent
from ai.ai_scientist.agents.hypothesis_agent import HypothesisAgent
from ai.ai_scientist.agents.experiment_agent import ExperimentAgent
from ai.ai_scientist.agents.execution_agent import ExecutionAgent
from ai.ai_scientist.agents.analysis_agent import AnalysisAgent
from ai.ai_scientist.agents.critic_agent import CriticAgent
from ai.ai_scientist.agents.writer_agent import WriterAgent
from ai.ai_scientist.agents.orchestrator import PrincipalResearchOrchestrator

__all__ = [
    "LiteratureAgent",
    "KnowledgeAgent",
    "GapAgent",
    "HypothesisAgent",
    "ExperimentAgent",
    "ExecutionAgent",
    "AnalysisAgent",
    "CriticAgent",
    "WriterAgent",
    "PrincipalResearchOrchestrator",
]
