"""
PROTEA PaIE - Comprehensive Backend Test Suite
Validates all 10 modules of the Pathway Intelligence Engine.
"""

import sys
from pathlib import Path
import networkx as nx

# Resolve imports pathing
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_ingestion():
    from ai.pathway_intelligence.ingestion.reactome import ReactomeAdapter
    from ai.pathway_intelligence.ingestion.kegg import KEGGAdapter, WikiPathwaysAdapter

    reactome = ReactomeAdapter()
    apop = reactome.get_pathway("R-HSA-109581")
    assert apop is not None
    assert apop["name"] == "Apoptosis"
    assert "TP53" in apop["proteins"]
    assert len(apop["reactions"]) > 0

    kegg = KEGGAdapter()
    cc = kegg.get_pathway("hsa04110")
    assert cc is not None
    assert "CDK1" in cc["proteins"]

    # Test GMT parsing
    gmt_sample = "TEST_PATHWAY\tPW_001\tTP53\tBAX\tCASP3\n"
    count = reactome.load_gmt(gmt_sample)
    assert count == 1
    assert reactome.get_pathway("PW_001") is not None

def test_go_and_annotations():
    from ai.pathway_intelligence.annotation.gene_ontology import go_engine
    from ai.pathway_intelligence.annotation.functional_annotation import annotation_manager, localization_mapper

    # Test GO term inheritance
    apop_term = go_engine.get_term("GO:0006915") # apoptotic process
    assert apop_term is not None
    ancestors = go_engine.get_ancestors("GO:0006915")
    assert "GO:0008150" in ancestors # biological_process root

    # Test protein annotation
    terms = annotation_manager.get_terms_for_protein("TP53", propagate=True)
    term_ids = {t["term_id"] for t in terms}
    assert "GO:0006915" in term_ids

    # Test localization
    loc = localization_mapper.get_localization("TP53")
    assert "nucleus" in loc

def test_statistical_enrichment():
    from ai.pathway_intelligence.enrichment.ora import ORAEngine
    from ai.pathway_intelligence.enrichment.statistics import benjamini_hochberg
    from ai.pathway_intelligence.enrichment.gsea import GSEAEngine, GSVAEngine

    # Test Benjamini-Hochberg
    raw_p = [0.01, 0.04, 0.03, 0.005]
    adj_p = benjamini_hochberg(raw_p)
    assert len(adj_p) == 4
    assert all(a >= r for a, r in zip(adj_p, raw_p))

    # Test ORA
    ora = ORAEngine(background_size=20000)
    genes = ["TP53", "BAX", "CASP3", "CASP8", "CASP9", "BCL2", "CYCS"]
    enriched = ora.run_enrichment(genes, p_cutoff=0.05)
    assert len(enriched) > 0
    assert any("Apoptosis" in e["name"] for e in enriched)
    assert enriched[0]["p_value"] < 0.01

    # Test GSEA
    gsea = GSEAEngine(n_permutations=50)
    ranked = [("TP53", 3.5), ("BAX", 2.8), ("CASP3", 2.1), ("EGFR", 0.1), ("MYC", -1.2)]
    pw_genes = ["TP53", "BAX", "CASP3"]
    res = gsea.run_gsea(ranked, pw_genes)
    assert "es" in res
    assert res["es"] > 0.0

def test_community_detection_and_dark_matter():
    from ai.pathway_intelligence.discovery.community_detection import LouvainDetector, MarkovClusterAlgorithm
    from ai.pathway_intelligence.discovery.novel_pathways import DeNovoPathwayDiscoveryEngine
    from ai.pathway_intelligence.evaluation.metrics import calculate_modularity

    g = nx.Graph()
    # Create 2 cliques
    clique1 = ["A1", "A2", "A3", "A4"]
    clique2 = ["B1", "B2", "B3", "B4"]
    for c in [clique1, clique2]:
        for u in c:
            for v in c:
                if u < v:
                    g.add_edge(u, v, weight=0.95)
    g.add_edge("A1", "B1", weight=0.1) # Weak bridge

    louvain = LouvainDetector()
    communities = louvain.detect(g)
    assert len(communities) == 2
    q = calculate_modularity(g, communities)
    assert q > 0.40

    mcl = MarkovClusterAlgorithm()
    mcl_comms = mcl.detect(g)
    assert len(mcl_comms) >= 2

    # Test De Novo Dark Matter
    dark_engine = DeNovoPathwayDiscoveryEngine()
    dark_pws = dark_engine.discover_novel_pathways(g, max_annotation_ratio=0.5)
    assert len(dark_pws) > 0
    assert "dark_matter_score" in dark_pws[0]

def test_causal_reasoning_and_propagation():
    from ai.pathway_intelligence.causal.regulatory_reasoning import RegulatoryReasoningEngine
    from ai.pathway_intelligence.causal.propagation import NetworkPropagationEngine, SignalingCascadeTracer

    dg = nx.DiGraph()
    dg.add_edge("EGFR", "GRB2", type="activates", weight=0.9)
    dg.add_edge("GRB2", "SOS1", type="activates", weight=0.9)
    dg.add_edge("SOS1", "KRAS", type="activates", weight=0.9)
    dg.add_edge("KRAS", "BRAF", type="activates", weight=0.9)

    regulatory = RegulatoryReasoningEngine()
    cascade = regulatory.evaluate_cascade_causality(["EGFR", "GRB2", "SOS1", "KRAS", "BRAF"], dg)
    assert cascade["net_sign"] == 1
    assert cascade["net_effect"] == "Activation"

    # Perturbation simulation
    impacts = regulatory.infer_perturbation_impact("EGFR", "overexpression", dg)
    assert len(impacts) == 4

    # Network propagation (RWR)
    g = dg.to_undirected()
    rwr = NetworkPropagationEngine(restart_prob=0.3)
    probs = rwr.propagate(["EGFR"], g)
    assert "EGFR" in probs
    assert probs["EGFR"] > probs["BRAF"] # Signal decays with distance

    # Yen's K-shortest paths
    tracer = SignalingCascadeTracer()
    k_paths = tracer.find_k_shortest_paths("EGFR", "BRAF", g, k=2)
    assert len(k_paths) >= 1
    assert k_paths[0]["path"][0] == "EGFR"
    assert k_paths[0]["path"][-1] == "BRAF"

def test_evolution_and_explainability():
    from ai.pathway_intelligence.evolution.ortholog_mapping import CrossSpeciesOrthologMapper, PathwayEvolutionAnalyzer
    from ai.pathway_intelligence.explainability.evidence import EvidenceAggregator, ScientificExplanationGenerator

    mapper = CrossSpeciesOrthologMapper()
    res = mapper.map_protein("TP53", "mouse")
    assert res is not None
    assert res["ortholog_symbol"] == "Trp53"

    evo = PathwayEvolutionAnalyzer(mapper)
    comp = evo.compare_pathway_across_species("PW_TEST", "Test Pathway", ["TP53", "AKT1", "EGFR"])
    assert "species_comparison" in comp
    assert "mouse" in comp["species_comparison"]

    # Explainability
    evidence = EvidenceAggregator()
    explainer = ScientificExplanationGenerator(evidence)
    explanation = explainer.generate_pathway_explanation("Apoptosis", ["TP53", "BAX", "CASP3"], "Activation", 1)
    assert "summary" in explanation
    assert len(explanation["citations"]) > 0

def test_api_service_and_benchmarks():
    from services.api.services.pathway_service import pathway_service
    from benchmarks.pathways.benchmark_suite import benchmark_suite

    # Test service statistics
    stats = pathway_service.get_statistics()
    assert stats["curated_pathways_count"] > 0
    assert stats["interactome_nodes"] > 0

    # Run Benchmark Suite
    bench_results = benchmark_suite.run_all_benchmarks()
    assert bench_results["status"] == "PASS"

if __name__ == "__main__":
    print("Executing Phase 5 PaIE backend test suite...")
    test_ingestion()
    test_go_and_annotations()
    test_statistical_enrichment()
    test_community_detection_and_dark_matter()
    test_causal_reasoning_and_propagation()
    test_evolution_and_explainability()
    test_api_service_and_benchmarks()
    print("All Phase 5 PaIE backend tests passed successfully!")
