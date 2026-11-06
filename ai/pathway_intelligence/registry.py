"""
PROTEA Pathway Intelligence Engine (PaIE) Registry
Central catalog and lifecycle manager for all PaIE modules.
"""

from typing import Dict, Any, Type, Callable, Optional
import logging

logger = logging.getLogger("ai.pathway_intelligence.registry")

class PathwayRegistry:
    """Registry maintaining references to all PaIE algorithms, adapters, and engines."""

    def __init__(self):
        self._community_detectors: Dict[str, Type] = {}
        self._enrichment_engines: Dict[str, Type] = {}
        self._ingestion_adapters: Dict[str, Type] = {}
        self._prediction_models: Dict[str, Type] = {}
        self._causal_engines: Dict[str, Type] = {}
        self._instances: Dict[str, Any] = {}

    def register_community_detector(self, name: str):
        """Decorator to register a community detection algorithm."""
        def decorator(cls):
            self._community_detectors[name.lower()] = cls
            logger.info(f"[PaIE REGISTRY] Registered community detector: {name}")
            return cls
        return decorator

    def register_enrichment_engine(self, name: str):
        """Decorator to register an enrichment calculation engine."""
        def decorator(cls):
            self._enrichment_engines[name.lower()] = cls
            logger.info(f"[PaIE REGISTRY] Registered enrichment engine: {name}")
            return cls
        return decorator

    def register_ingestion_adapter(self, name: str):
        """Decorator to register a pathway database adapter."""
        def decorator(cls):
            self._ingestion_adapters[name.lower()] = cls
            logger.info(f"[PaIE REGISTRY] Registered ingestion adapter: {name}")
            return cls
        return decorator

    def register_causal_engine(self, name: str):
        """Decorator to register a causal reasoning engine."""
        def decorator(cls):
            self._causal_engines[name.lower()] = cls
            logger.info(f"[PaIE REGISTRY] Registered causal engine: {name}")
            return cls
        return decorator

    def register_prediction_model(self, name: str):
        """Decorator to register a pathway prediction model."""
        def decorator(cls):
            self._prediction_models[name.lower()] = cls
            logger.info(f"[PaIE REGISTRY] Registered prediction model: {name}")
            return cls
        return decorator

    def get_community_detector(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._community_detectors:
            raise KeyError(f"Community detector '{name}' not found. Available: {list(self._community_detectors.keys())}")
        return self._community_detectors[name](**kwargs)

    def get_enrichment_engine(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._enrichment_engines:
            raise KeyError(f"Enrichment engine '{name}' not found. Available: {list(self._enrichment_engines.keys())}")
        return self._enrichment_engines[name](**kwargs)

    def get_ingestion_adapter(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._ingestion_adapters:
            raise KeyError(f"Ingestion adapter '{name}' not found. Available: {list(self._ingestion_adapters.keys())}")
        return self._ingestion_adapters[name](**kwargs)

    def get_causal_engine(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._causal_engines:
            raise KeyError(f"Causal engine '{name}' not found. Available: {list(self._causal_engines.keys())}")
        return self._causal_engines[name](**kwargs)

    def get_prediction_model(self, name: str, **kwargs):
        name = name.lower()
        if name not in self._prediction_models:
            raise KeyError(f"Prediction model '{name}' not found. Available: {list(self._prediction_models.keys())}")
        return self._prediction_models[name](**kwargs)

    def list_components(self) -> Dict[str, list]:
        """List all registered components across all PaIE categories."""
        return {
            "community_detectors": list(self._community_detectors.keys()),
            "enrichment_engines": list(self._enrichment_engines.keys()),
            "ingestion_adapters": list(self._ingestion_adapters.keys()),
            "prediction_models": list(self._prediction_models.keys()),
            "causal_engines": list(self._causal_engines.keys()),
        }

# Global PaIE registry singleton
paie_registry = PathwayRegistry()
