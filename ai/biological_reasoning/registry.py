"""
PROTEA Biological Reasoning Engine (BRE) Registry
Central catalog for reasoning modules, retrieval adapters, and specialized agents.
"""

from typing import Dict, Any, Type, Optional
import logging

logger = logging.getLogger("ai.biological_reasoning.registry")

class BiologicalReasoningRegistry:
    """Registry maintaining references to all BRE components and agents."""

    def __init__(self):
        self._retrievers: Dict[str, Type] = {}
        self._reasoners: Dict[str, Type] = {}
        self._agents: Dict[str, Type] = {}
        self._validators: Dict[str, Type] = {}

    def register_retriever(self, name: str):
        def decorator(cls):
            self._retrievers[name.lower()] = cls
            logger.info(f"[BRE REGISTRY] Registered retriever: {name}")
            return cls
        return decorator

    def register_reasoner(self, name: str):
        def decorator(cls):
            self._reasoners[name.lower()] = cls
            logger.info(f"[BRE REGISTRY] Registered reasoner: {name}")
            return cls
        return decorator

    def register_agent(self, name: str):
        def decorator(cls):
            self._agents[name.lower()] = cls
            logger.info(f"[BRE REGISTRY] Registered agent: {name}")
            return cls
        return decorator

    def register_validator(self, name: str):
        def decorator(cls):
            self._validators[name.lower()] = cls
            logger.info(f"[BRE REGISTRY] Registered validator: {name}")
            return cls
        return decorator

    def get_retriever(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._retrievers:
            raise KeyError(f"Retriever '{name}' not found. Available: {list(self._retrievers.keys())}")
        return self._retrievers[name](**kwargs)

    def get_reasoner(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._reasoners:
            raise KeyError(f"Reasoner '{name}' not found. Available: {list(self._reasoners.keys())}")
        return self._reasoners[name](**kwargs)

    def get_agent(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' not found. Available: {list(self._agents.keys())}")
        return self._agents[name](**kwargs)

    def get_validator(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._validators:
            raise KeyError(f"Validator '{name}' not found. Available: {list(self._validators.keys())}")
        return self._validators[name](**kwargs)

    def list_components(self) -> Dict[str, list]:
        return {
            "retrievers": list(self._retrievers.keys()),
            "reasoners": list(self._reasoners.keys()),
            "agents": list(self._agents.keys()),
            "validators": list(self._validators.keys())
        }

bre_registry = BiologicalReasoningRegistry()
