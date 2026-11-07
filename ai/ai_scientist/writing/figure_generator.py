"""
PROTEA AI Scientist - Figure & Data Table Generator
Produces publication-grade figure specifications, captions, and structured tables.
"""

from typing import Dict, Any, List


class FigureGenerator:
    """
    Generates structured figure specifications (Mermaid, SVG schemas) and data tables for manuscripts.
    """

    def generate_pathway_mechanism_figure(
        self,
        hypothesis_id: str,
        source_protein: str,
        target_protein: str,
        mediators: List[str],
        interaction_type: str = "Phosphorylation / Transactivation",
    ) -> Dict[str, Any]:
        """
        Generates Mermaid diagram specification for the proposed molecular mechanism.
        """
        nodes = [f"    A[{source_protein}] -->|{interaction_type}| B[{target_protein}]"]
        for idx, med in enumerate(mediators):
            nodes.append(f"    B -->|Translocates/Modulates| M{idx}[{med}]")

        mermaid_code = "graph TD\n" + "\n".join(nodes)

        return {
            "figure_id": f"fig_{hypothesis_id}_mechanism",
            "figure_number": 1,
            "title": f"Proposed Mechanistic Pathway: {source_protein} -> {target_protein}",
            "caption": (
                f"Figure 1. Mechanistic model of {source_protein}-mediated regulation of {target_protein}. "
                f"Computational simulations predict downstream effects mediated via {', '.join(mediators) if mediators else 'direct coupling'}."
            ),
            "format": "mermaid",
            "content": mermaid_code,
        }

    def generate_statistical_comparison_table(
        self,
        experiment_id: str,
        conditions: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generates structured data summary table for statistical comparisons.
        """
        headers = ["Condition", "Mean Outcome", "Std Dev", "N Replicates (Sim)", "Cohen's d", "Adj. p-value"]
        rows = []
        for c in conditions:
            rows.append([
                c.get("condition_name", "Condition"),
                f"{c.get('mean', 0.0):.3f}",
                f"{c.get('std', 0.0):.3f}",
                str(c.get("n", 0)),
                f"{c.get('effect_size', 0.0):.3f}",
                f"{c.get('p_value', 1.0):.2e}",
            ])

        return {
            "table_id": f"tbl_{experiment_id}_stats",
            "table_number": 1,
            "title": "Quantitative In-Silico Perturbation Outcomes & Effect Sizes",
            "caption": (
                "Table 1. Statistical summary of perturbation responses across computational replicates. "
                "Replicates correspond to stochastic numerical solver runs, not independent biological specimens."
            ),
            "headers": headers,
            "rows": rows,
        }
