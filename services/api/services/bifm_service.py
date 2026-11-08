"""
PROTEA Phase 12: Biological Intelligence Foundation Model (BIFM) - Service Layer
Singleton service orchestrating universal representations, multimodal encoders,
cross-modal alignment, multi-task predictions, biological world model,
counterfactual interventions, and autonomous research.
"""

from typing import Dict, Any, List, Optional
from ai.bifm.schema import (
    BiologicalContext,
    BiologicalRepresentation,
    MultiModalProfile,
    InterventionSpec,
    EvidenceLevel
)
from ai.bifm.representations.canonical import UniversalRepresentationRegistry
from ai.bifm.encoders.adapters import (
    SequenceEncoderAdapter,
    StructureEncoderAdapter,
    InteractionEncoderAdapter,
    PathwayEncoderAdapter,
    OmicsEncoderAdapter,
    CellularEncoderAdapter,
    SpatialEncoderAdapter,
    EvolutionEncoderAdapter,
    LiteratureEncoderAdapter
)
from ai.bifm.fusion.cross_modal_fusion import CrossModalFusionEngine
from ai.bifm.knowledge.grounding_engine import BiologicalKnowledgeGroundingEngine
from ai.bifm.prediction.multitask_engine import BiologicalMultiTaskEngine
from ai.bifm.context.conditional_engine import BiologicalContextEngine
from ai.bifm.world_model.state_transition import BiologicalWorldModel
from ai.bifm.counterfactuals.intervention_engine import CounterfactualIntelligenceEngine
from ai.bifm.reasoning.scientific_reasoning import UnifiedBiologicalReasoningEngine
from ai.bifm.research.autonomous_orchestrator import AutonomousResearchInterface
from ai.bifm.continual.adapter_manager import ContinualLearningEngine
from ai.bifm.governance.model_cards import FoundationModelGovernance
from ai.bifm.evaluation.benchmarks import BIFMBenchmarkSuite


class BIFMService:
    """Singleton service facade for the Biological Intelligence Foundation Model."""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BIFMService, cls).__new__(cls, *args, **kwargs)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if getattr(self, "_initialized", False):
            return

        self.registry = UniversalRepresentationRegistry()
        self.encoders = {
            "sequence": SequenceEncoderAdapter(),
            "structure": StructureEncoderAdapter(),
            "interaction": InteractionEncoderAdapter(),
            "pathway": PathwayEncoderAdapter(),
            "omics": OmicsEncoderAdapter(),
            "cellular": CellularEncoderAdapter(),
            "spatial": SpatialEncoderAdapter(),
            "evolution": EvolutionEncoderAdapter(),
            "literature": LiteratureEncoderAdapter()
        }
        self.fusion = CrossModalFusionEngine(unified_dim=256, shared_dim=64, private_dim=32)
        self.grounding = BiologicalKnowledgeGroundingEngine()
        self.multitask = BiologicalMultiTaskEngine()
        self.context_engine = BiologicalContextEngine(context_dim=64)
        self.world_model = BiologicalWorldModel(state_dim=128)
        self.counterfactuals = CounterfactualIntelligenceEngine(self.world_model)
        self.reasoning = UnifiedBiologicalReasoningEngine(self.grounding)
        self.research = AutonomousResearchInterface(self.reasoning, self.counterfactuals)
        self.continual = ContinualLearningEngine()
        self.governance = FoundationModelGovernance()
        self.benchmarks = BIFMBenchmarkSuite()

        self._seed_reference_entities()
        self._initialized = True

    def _seed_reference_entities(self):
        """Pre-registers reference representations for canonical oncogenes."""
        genes = ["BRAF", "EGFR", "KRAS", "TP53", "POLR2A"]
        for g in genes:
            seq_v = self.encoders["sequence"].encode(f"SEQUENCE_FOR_{g}_HOMO_SAPIENS")
            struct_v = self.encoders["structure"].encode(f"PDB_{g}_STRUCTURE")
            omics_v = self.encoders["omics"].encode([2.5, 4.1, 1.2, 5.0])

            self.registry.register_representation(g, "protein", "sequence", seq_v, "esm2")
            self.registry.register_representation(g, "protein", "structure", struct_v, "egnn")
            self.registry.register_representation(g, "protein", "omics", omics_v, "scvi")

            prof = self.registry.get_multimodal_profile(g)
            if prof:
                self.fusion.fuse_multimodal_profile(prof)

    # 1. Universal Representations
    def encode_entity(
        self,
        entity_id: str,
        entity_type: str,
        modality: str,
        raw_input: Any,
        context: Optional[Dict[str, Any]] = None,
        organism_id: str = "9606"
    ) -> Dict[str, Any]:
        encoder = self.encoders.get(modality.lower(), self.encoders["sequence"])
        emb = encoder.encode(raw_input, context)
        rep = self.registry.register_representation(
            entity_id=entity_id,
            entity_type=entity_type,
            modality=modality,
            embedding=emb,
            model_name=encoder.get_metadata().get("model", "bifm_encoder"),
            organism_id=organism_id,
            biological_context=context
        )
        return rep.to_dict()

    def get_representation(self, entity_id: str, modality: str) -> Optional[Dict[str, Any]]:
        rep = self.registry.get_representation(entity_id, modality)
        return rep.to_dict() if rep else None

    def get_multimodal_profile(self, entity_id: str) -> Optional[Dict[str, Any]]:
        prof = self.registry.get_multimodal_profile(entity_id)
        return prof.to_dict() if prof else None

    # 2. Alignment & Fusion
    def align_entity_modalities(self, entity_id: str) -> Dict[str, Any]:
        prof = self.registry.get_multimodal_profile(entity_id)
        if not prof:
            # Create dynamic profile
            self.encode_entity(entity_id, "protein", "sequence", f"SEQ_{entity_id}")
            prof = self.registry.get_multimodal_profile(entity_id)

        fused = self.fusion.fuse_multimodal_profile(prof)
        return fused

    def impute_missing_modality(self, entity_id: str, target_modality: str) -> Dict[str, Any]:
        prof = self.registry.get_multimodal_profile(entity_id)
        if not prof or not prof.shared_factors:
            align_res = self.align_entity_modalities(entity_id)
            shared = align_res["shared_factors"]
        else:
            shared = prof.shared_factors
        return self.fusion.impute_missing_modality(shared, target_modality)

    # 3. Contextualization
    def contextualize(self, entity_id: str, context_dict: Dict[str, Any]) -> Dict[str, Any]:
        rep = self.registry.get_representation(entity_id, "sequence")
        if not rep:
            self.encode_entity(entity_id, "protein", "sequence", f"SEQ_{entity_id}")
            rep = self.registry.get_representation(entity_id, "sequence")

        ctx = BiologicalContext.from_dict(context_dict)
        contextualized = self.context_engine.contextualize_representation(rep, ctx)
        return contextualized.to_dict()

    # 4. Multi-Task Predictions
    def predict(
        self,
        task_name: str,
        entity_id: str,
        partner_id: Optional[str] = None,
        mutation: Optional[str] = None,
        target_taxid: int = 10090
    ) -> Dict[str, Any]:
        prof = self.registry.get_multimodal_profile(entity_id)
        latent = prof.unified_embedding if prof and prof.unified_embedding else [0.2] * 256

        if task_name == "protein_function":
            pred = self.multitask.predict_protein_function(entity_id, latent)
        elif task_name == "protein_interaction":
            latent_b = [0.25] * 256
            if partner_id:
                prof_b = self.registry.get_multimodal_profile(partner_id)
                if prof_b and prof_b.unified_embedding:
                    latent_b = prof_b.unified_embedding
            pred = self.multitask.predict_protein_interaction(entity_id, partner_id or "PARTNER", latent, latent_b)
        elif task_name == "evolution_transfer":
            pred = self.multitask.predict_evolution_transfer(entity_id, 9606, target_taxid)
        elif task_name == "mutation_effect":
            pred = self.multitask.predict_mutation_effect(entity_id, mutation or "V600E", latent)
        elif task_name == "therapeutic_prioritization":
            pred = self.multitask.predict_therapeutic_prioritization(entity_id, latent)
        else:
            pred = self.multitask.predict_protein_function(entity_id, latent)

        return self.governance.verify_safety_disclaimers(pred.to_dict())

    # 5. World Model & Counterfactuals
    def forecast_world_model(
        self,
        system_id: str,
        target_entity: str,
        intervention_type: str = "small_molecule_inhibition",
        magnitude: float = 0.10,
        steps: int = 3
    ) -> List[Dict[str, Any]]:
        init_state = self.world_model.initialize_state(system_id)
        spec = InterventionSpec(target_entity=target_entity, intervention_type=intervention_type, magnitude=magnitude)
        trajectory = self.world_model.forecast_trajectory(init_state, spec, total_steps=steps)
        return [s.to_dict() for s in trajectory]

    def evaluate_counterfactual(
        self,
        target_entity: str,
        intervention_type: str = "gene_knockout",
        magnitude: float = 0.0
    ) -> Dict[str, Any]:
        spec = InterventionSpec(target_entity=target_entity, intervention_type=intervention_type, magnitude=magnitude)
        res = self.counterfactuals.evaluate_counterfactual(spec)
        return self.governance.verify_safety_disclaimers(res.to_dict())

    # 6. Scientific Reasoning
    def reason(
        self,
        question: str,
        focal_gene: str,
        partner_gene: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        ctx = BiologicalContext.from_dict(context) if context else None
        explanation = self.reasoning.generate_explanation(question, focal_gene, partner_gene, ctx)
        return self.governance.verify_safety_disclaimers(explanation.to_dict())

    # 7. Autonomous Research
    def launch_investigation(
        self,
        research_question: str,
        focal_gene: str,
        partner_gene: Optional[str] = None
    ) -> Dict[str, Any]:
        res = self.research.launch_investigation(research_question, focal_gene, partner_gene)
        return self.governance.verify_safety_disclaimers(res)

    # 8. Continual Learning & Governance
    def register_adapter(self, domain: str, task: str, datasets: List[str]) -> Dict[str, Any]:
        return self.continual.register_adapter(domain, task, datasets)

    def audit_adapter(self, adapter_id: str, benchmark_pass_rate: float) -> Dict[str, Any]:
        return self.continual.audit_regression_gate(adapter_id, benchmark_pass_rate)

    def get_model_card(self) -> Dict[str, Any]:
        card = self.governance.generate_bifm_model_card()
        return card.to_dict()

    def run_benchmarks(self) -> Dict[str, Any]:
        return self.benchmarks.run_all_benchmarks()
