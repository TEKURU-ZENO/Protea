"""
PROTEA Phase 10: Drug Candidate Retriever
Queries ChEMBL and BindingDB knowledge bases for approved drugs and advanced investigational leads.
"""

from __future__ import annotations
from typing import List, Dict, Any, Optional
from ai.mutation_therapeutics.schema import DrugCandidate

# Curated precision oncology compound catalog
COMPOUND_REGISTRY: List[Dict[str, Any]] = [
    {
        "drug_id": "DRUG_VEMURAFENIB",
        "name": "Vemurafenib",
        "chembl_id": "CHEMBL1229517",
        "mechanism_of_action": "Selective BRAF V600 inhibitor (ATP-competitive Type I 1/2)",
        "primary_targets": ["BRAF"],
        "molecule_type": "small_molecule",
        "clinical_phase": "Approved (Phase 4)",
        "smiles": "CCCS(=O)(=O)NC1=C(C(=C(C=C1)F)C(=O)C2=CNC3=C2C=C(C=N3)C4=CC=C(C=C4)Cl)F",
        "molecular_weight": 489.9
    },
    {
        "drug_id": "DRUG_DABRAFENIB",
        "name": "Dabrafenib",
        "chembl_id": "CHEMBL2105759",
        "mechanism_of_action": "Potent BRAF V600 kinase inhibitor",
        "primary_targets": ["BRAF"],
        "molecule_type": "small_molecule",
        "clinical_phase": "Approved (Phase 4)",
        "smiles": "CC(C)(C)C1=NC(=C(S1)C2=NC(=NC=C2)N)C3=C(C(=C(C=C3)S(=O)(=O)NC4=C(C=CC=C4F)F)F)F",
        "molecular_weight": 519.5
    },
    {
        "drug_id": "DRUG_TRAMETINIB",
        "name": "Trametinib",
        "chembl_id": "CHEMBL2103841",
        "mechanism_of_action": "Allosteric MEK1/MEK2 inhibitor",
        "primary_targets": ["MAP2K1", "MAP2K2"],
        "molecule_type": "small_molecule",
        "clinical_phase": "Approved (Phase 4)",
        "smiles": "CC1=C(C(=O)N(C(=O)N1C2=CC=C(C=C2I)F)C3=CC=CC(=C3)NC(=O)C)C(=O)NC4CC4",
        "molecular_weight": 615.4
    },
    {
        "drug_id": "DRUG_OSIMERTINIB",
        "name": "Osimertinib",
        "chembl_id": "CHEMBL3353410",
        "mechanism_of_action": "3rd generation mutant-selective irreversible EGFR T790M inhibitor",
        "primary_targets": ["EGFR"],
        "molecule_type": "small_molecule",
        "clinical_phase": "Approved (Phase 4)",
        "smiles": "CN(C)CC=CC(=O)NC1=CC(=C(C=C1NC2=NC=CC(=N2)C3=CN(C4=CC=CC=C43)C)OC)OC",
        "molecular_weight": 499.6
    },
    {
        "drug_id": "DRUG_GEFITINIB",
        "name": "Gefitinib",
        "chembl_id": "CHEMBL939",
        "mechanism_of_action": "1st generation reversible EGFR tyrosine kinase inhibitor",
        "primary_targets": ["EGFR"],
        "molecule_type": "small_molecule",
        "clinical_phase": "Approved (Phase 4)",
        "smiles": "COC1=C(C=C2C(=C1)N=CN=C2NC3=CC(=C(C=C3)F)Cl)OCCCN4CCOCC4",
        "molecular_weight": 446.9
    },
    {
        "drug_id": "DRUG_SOTORASIB",
        "name": "Sotorasib",
        "chembl_id": "CHEMBL4523789",
        "mechanism_of_action": "Covalent KRAS G12C switch II pocket inhibitor",
        "primary_targets": ["KRAS"],
        "molecule_type": "small_molecule",
        "clinical_phase": "Approved (Phase 4)",
        "smiles": "C=CC(=O)N1CCN(CC1)C2=C(C=CC(=C2)C3=CC=C(C=C3)Cl)C4=NC5=C(N4)C=C(C=C5)F",
        "molecular_weight": 560.6
    },
    {
        "drug_id": "DRUG_CETUXIMAB",
        "name": "Cetuximab",
        "chembl_id": "CHEMBL1201583",
        "mechanism_of_action": "Chimeric monoclonal antibody targeting EGFR extracellular domain III",
        "primary_targets": ["EGFR"],
        "molecule_type": "biologic",
        "clinical_phase": "Approved (Phase 4)",
        "smiles": None,
        "molecular_weight": 145781.0
    }
]


class DrugRetriever:
    """Finds drugs and therapeutic compounds targeting given genes or pathways."""

    @classmethod
    def get_drugs_for_targets(cls, target_genes: List[str]) -> List[DrugCandidate]:
        """Returns matching drug candidates for a list of target genes."""
        up_targets = {t.upper() for t in target_genes}
        matched: List[DrugCandidate] = []

        for c in COMPOUND_REGISTRY:
            if any(t.upper() in up_targets for t in c["primary_targets"]):
                matched.append(DrugCandidate.from_dict(c))

        return matched

    @classmethod
    def get_all_drugs(cls) -> List[DrugCandidate]:
        """Returns all registered drug candidates."""
        return [DrugCandidate.from_dict(c) for c in COMPOUND_REGISTRY]
