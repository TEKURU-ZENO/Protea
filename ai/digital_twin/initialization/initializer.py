"""Digital Twin Initialization Engine assembling baseline state and network snapshots."""

from __future__ import annotations

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ai.digital_twin.initialization.context_builder import ContextBuilder
from ai.digital_twin.initialization.evidence_integrator import EvidenceIntegrator
from ai.digital_twin.schema import (
    BiologicalContext,
    DigitalTwin,
    InteractomeSnapshot,
    MolecularState,
    NetworkEdgeEvidence,
    StateStatus,
    TwinVersion,
)

logger = logging.getLogger(__name__)


# Default canonical reference nodes for human hepatocytes
DEFAULT_HEPATOCYTE_NODES = [
    "ALB", "CYP3A4", "CYP2E1", "HNF4A", "NR1I2", "PPARGC1A", "PPARA",
    "AKT1", "MTOR", "INSR", "IRS1", "GSK3B", "FOXO1",
    "TP53", "MDM2", "CDKN1A", "BAX", "CASP3", "CASP8",
    "METTL3", "METTL14", "WTAP", "FTO", "ALKBH5"
]

DEFAULT_HEPATOCYTE_EDGES = [
    {"source": "HNF4A", "target": "ALB", "edge_type": "TRANSCRIPTIONAL_REGULATION", "directed": True, "sign": 1, "confidence": 0.98, "status": "OBSERVED", "source_db": "BioGRID"},
    {"source": "HNF4A", "target": "CYP3A4", "edge_type": "TRANSCRIPTIONAL_REGULATION", "directed": True, "sign": 1, "confidence": 0.95, "status": "CURATED", "source_db": "Reactome"},
    {"source": "NR1I2", "target": "CYP3A4", "edge_type": "TRANSCRIPTIONAL_REGULATION", "directed": True, "sign": 1, "confidence": 0.94, "status": "CURATED", "source_db": "Reactome"},
    {"source": "INSR", "target": "IRS1", "edge_type": "PHOSPHORYLATION", "directed": True, "sign": 1, "confidence": 0.97, "status": "OBSERVED", "source_db": "IntAct"},
    {"source": "IRS1", "target": "AKT1", "edge_type": "PHYSICAL_INTERACTION", "directed": True, "sign": 1, "confidence": 0.93, "status": "CURATED", "source_db": "BioGRID"},
    {"source": "AKT1", "target": "GSK3B", "edge_type": "PHOSPHORYLATION", "directed": True, "sign": -1, "confidence": 0.96, "status": "CURATED", "source_db": "Reactome"},
    {"source": "AKT1", "target": "FOXO1", "edge_type": "PHOSPHORYLATION", "directed": True, "sign": -1, "confidence": 0.92, "status": "CURATED", "source_db": "Reactome"},
    {"source": "AKT1", "target": "MTOR", "edge_type": "PHYSICAL_INTERACTION", "directed": True, "sign": 1, "confidence": 0.91, "status": "CURATED", "source_db": "IntAct"},
    {"source": "TP53", "target": "MDM2", "edge_type": "TRANSCRIPTIONAL_REGULATION", "directed": True, "sign": 1, "confidence": 0.96, "status": "OBSERVED", "source_db": "IntAct"},
    {"source": "MDM2", "target": "TP53", "edge_type": "PHYSICAL_INTERACTION", "directed": True, "sign": -1, "confidence": 0.98, "status": "OBSERVED", "source_db": "IntAct"},
    {"source": "TP53", "target": "BAX", "edge_type": "TRANSCRIPTIONAL_REGULATION", "directed": True, "sign": 1, "confidence": 0.92, "status": "OBSERVED", "source_db": "Reactome"},
    {"source": "BAX", "target": "CASP3", "edge_type": "PHYSICAL_INTERACTION", "directed": True, "sign": 1, "confidence": 0.89, "status": "CURATED", "source_db": "BioGRID"},
    {"source": "METTL3", "target": "METTL14", "edge_type": "COMPLEX_MEMBER", "directed": False, "sign": 0, "confidence": 0.99, "status": "OBSERVED", "source_db": "IntAct"},
    {"source": "METTL3", "target": "WTAP", "edge_type": "COMPLEX_MEMBER", "directed": False, "sign": 0, "confidence": 0.95, "status": "OBSERVED", "source_db": "IntAct"}
]

# Baseline empirical observation values (log2TPM transcript, LFQ abundance)
DEFAULT_HEPATOCYTE_STATES: Dict[str, Dict[str, Any]] = {
    "ALB": {"expression": 14.8, "abundance": 15.2, "activity": 1.0, "location": "cytosol/secreted", "condition": "healthy"},
    "CYP3A4": {"expression": 10.4, "abundance": 11.1, "activity": 0.85, "location": "endoplasmic_reticulum", "condition": "healthy"},
    "CYP2E1": {"expression": 9.2, "abundance": 9.8, "activity": 0.70, "location": "endoplasmic_reticulum", "condition": "healthy"},
    "HNF4A": {"expression": 7.6, "abundance": 6.9, "activity": 0.90, "location": "nucleus", "condition": "healthy"},
    "INSR": {"expression": 6.8, "abundance": 6.2, "activity": 0.80, "location": "plasma_membrane", "condition": "healthy"},
    "IRS1": {"expression": 5.9, "abundance": 5.8, "activity": 0.75, "location": "cytosol", "condition": "healthy"},
    "AKT1": {"expression": 7.1, "abundance": 7.5, "activity": 0.65, "location": "cytosol/nucleus", "condition": "healthy"},
    "GSK3B": {"expression": 6.4, "abundance": 6.8, "activity": 0.55, "location": "cytosol", "condition": "healthy"},
    "FOXO1": {"expression": 5.5, "abundance": 5.1, "activity": 0.40, "location": "nucleus", "condition": "healthy"},
    "MTOR": {"expression": 5.8, "abundance": 6.0, "activity": 0.60, "location": "cytosol", "condition": "healthy"},
    "TP53": {"expression": 6.2, "abundance": 5.9, "activity": 0.20, "location": "nucleus", "condition": "healthy"},
    "MDM2": {"expression": 5.7, "abundance": 5.4, "activity": 0.80, "location": "nucleus", "condition": "healthy"},
    "BAX": {"expression": 5.1, "abundance": 4.8, "activity": 0.15, "location": "cytosol/mitochondria", "condition": "healthy"},
    "CASP3": {"expression": 6.0, "abundance": 5.8, "activity": 0.10, "location": "cytosol", "condition": "healthy"},
    "METTL3": {"expression": 6.5, "abundance": 6.1, "activity": 0.75, "location": "nucleus", "condition": "healthy"},
    "METTL14": {"expression": 6.1, "abundance": 5.9, "activity": 0.70, "location": "nucleus", "condition": "healthy"},
    "WTAP": {"expression": 5.8, "abundance": 5.6, "activity": 0.65, "location": "nucleus", "condition": "healthy"},
    "FTO": {"expression": 5.2, "abundance": 5.0, "activity": 0.50, "location": "nucleus", "condition": "healthy"},
    "ALKBH5": {"expression": 4.9, "abundance": 4.7, "activity": 0.45, "location": "nucleus", "condition": "healthy"}
}


class DigitalTwinInitializer:
    """Orchestrates initialization of a reproducible context-specific Digital Twin."""

    def __init__(self) -> None:
        self.context_builder = ContextBuilder()
        self.evidence_integrator = EvidenceIntegrator()

    def initialize_twin(
        self,
        name: str = "human_liver_hepatocyte_twin",
        organism: str = "NCBI:9606",
        tissue: str = "liver",
        cell_type: str = "hepatocyte",
        condition: str = "healthy",
        mode: str = "hybrid",
        custom_nodes: Optional[List[str]] = None,
        custom_edges: Optional[List[Dict[str, Any]]] = None,
        custom_states: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> DigitalTwin:
        twin_id = f"DTW-{str(uuid.uuid4())[:8].upper()}"
        version_id = f"VER-1.0-BASE"
        version_tag = "v1.0"

        context = self.context_builder.build_context(
            organism=organism,
            tissue=tissue,
            cell_type=cell_type,
            condition=condition
        )

        # 1. Resolve nodes
        nodes = custom_nodes or DEFAULT_HEPATOCYTE_NODES

        # 2. Assemble edges via evidence integrator
        raw_edges = custom_edges or DEFAULT_HEPATOCYTE_EDGES
        integrated_edges: List[NetworkEdgeEvidence] = []
        for e in raw_edges:
            edge_obj = self.evidence_integrator.harmonize_edge(
                source=e["source"],
                target=e["target"],
                evidence_records=[e],
                context_tissue=tissue
            )
            if edge_obj:
                integrated_edges.append(edge_obj)

        # 3. Create InteractomeSnapshot
        snapshot = InteractomeSnapshot(
            snapshot_id=f"SNAP-{twin_id}-v1.0",
            twin_id=twin_id,
            version_id=version_id,
            nodes=nodes,
            edges=integrated_edges
        )
        snapshot.compute_hash()

        # 4. Construct MolecularStates (keeping unobserved fields None)
        states_pool = custom_states or DEFAULT_HEPATOCYTE_STATES
        molecular_states: Dict[str, MolecularState] = {}
        for node in nodes:
            obs = states_pool.get(node, {})
            molecular_states[node] = MolecularState(
                entity_id=node,
                gene_expression=obs.get("expression"),
                protein_abundance=obs.get("abundance"),
                protein_activity=obs.get("activity"),
                phosphorylation=obs.get("phosphorylation"),
                subcellular_location=obs.get("location"),
                pathway_activity=obs.get("pathway_activity", 0.0),
                interaction_status="active",
                cell_condition=condition,
                status=StateStatus.OBSERVED.value if obs else StateStatus.ESTIMATED.value,
                confidence=1.0 if obs else 0.5
            )

        # 5. Create initial TwinVersion
        version = TwinVersion(
            version_id=version_id,
            version_tag=version_tag,
            twin_id=twin_id,
            parent_version_id=None,
            context=context,
            initialization_mode=mode,
            snapshot=snapshot,
            states=molecular_states,
            created_at=datetime.utcnow().isoformat()
        )
        version.compute_hash()

        # 6. Assemble DigitalTwin
        twin = DigitalTwin(
            twin_id=twin_id,
            name=name,
            organism=context.organism_id,
            primary_tissue=tissue,
            primary_cell_type=cell_type,
            active_version_id=version_id,
            versions={version_id: version},
            description=f"Digital Interactome Twin for {organism} {tissue} ({cell_type}) in {condition} state.",
            tags=["liver", "hepatocyte", "baseline", "interactome", mode]
        )

        logger.info(f"Initialized digital twin: {twin_id} with {len(nodes)} nodes and {len(integrated_edges)} edges.")
        return twin
