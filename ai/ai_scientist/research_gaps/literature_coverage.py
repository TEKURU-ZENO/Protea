"""Literature coverage density and knowledge distribution evaluator."""

from typing import Any, Dict, List
from ai.ai_scientist.schema import PublicationRecord, ScientificClaim


class LiteratureCoverageAnalyzer:
    """Analyzes evidence density distribution across biological pathways and targets."""

    @staticmethod
    def calculate_coverage(
        entities: List[str],
        publications: List[PublicationRecord],
        claims: List[ScientificClaim],
    ) -> Dict[str, Any]:
        """Compute citation and claim density for each entity."""
        entity_counts = {e: 0 for e in entities}
        for e in entities:
            e_lower = e.lower()
            for p in publications:
                if e_lower in p.title.lower() or e_lower in p.abstract.lower():
                    entity_counts[e] += 1

        total_pubs = max(1, len(publications))
        coverage_densities = {e: round(count / total_pubs, 3) for e, count in entity_counts.items()}

        understudied_entities = [e for e, dens in coverage_densities.items() if dens < 0.3]

        return {
            "coverage_densities": coverage_densities,
            "understudied_entities": understudied_entities,
            "claims_per_entity": {e: sum(1 for c in claims if c.subject == e or c.object == e) for e in entities},
            "literature_saturation_index": round(sum(coverage_densities.values()) / max(1, len(entities)), 3),
        }
