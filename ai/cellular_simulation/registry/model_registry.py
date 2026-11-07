"""Curated biological model registry and versioning repository."""

from typing import Any, Dict, List, Optional
from ai.cellular_simulation.schema import SimulationModel
from ai.cellular_simulation.model_builder.model_factory import ModelFactory


class ModelRegistry:
    """Central repository storing curated and user-defined simulation models."""

    def __init__(self):
        self._models: Dict[str, SimulationModel] = {}
        self._register_default_models()

    def _register_default_models(self) -> None:
        """Register default curated biophysical benchmarks."""
        defaults = [
            ModelFactory.create_goldbeter_koshland_model(),
            ModelFactory.create_mapk_cascade_model(),
            ModelFactory.create_lac_operon_grn_model(),
            ModelFactory.create_central_metabolism_fba_model(),
            ModelFactory.create_hybrid_signaling_grn_model(),
        ]
        for m in defaults:
            self._models[m.model_id] = m

    def register_model(self, model: SimulationModel) -> None:
        """Register or update a model."""
        self._models[model.model_id] = model

    def get_model(self, model_id: str) -> Optional[SimulationModel]:
        """Retrieve model by identifier."""
        return self._models.get(model_id)

    def list_models(self) -> List[Dict[str, Any]]:
        """List summary descriptors for all registered models."""
        return [
            {
                "model_id": m.model_id,
                "name": m.name,
                "model_type": m.model_type,
                "species_count": len(m.species),
                "reactions_count": len(m.reactions),
                "parameters_count": len(m.parameters),
                "metadata": m.metadata,
            }
            for m in self._models.values()
        ]
