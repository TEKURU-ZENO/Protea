import sys
from pathlib import Path

# Resolve imports pathing
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_mappers():
    from graph.entity_resolution.protein_mapper import protein_mapper
    from graph.entity_resolution.gene_mapper import gene_mapper
    
    # Test Entrez/Ensembl mapping resolution to UniProt ID
    uniprot = protein_mapper.resolve("3643")
    assert uniprot == "P01308"
    
    symbol = gene_mapper.resolve("HGNC:6081")
    assert symbol == "INS"

def test_adapters():
    from graph.etl.ingestion.string_adapter import StringAdapter
    from graph.etl.ingestion.biogrid_adapter import BiogridAdapter
    from graph.etl.ingestion.intact_adapter import IntactAdapter
    
    # Verify STRING parser normalize
    string_adapter = StringAdapter()
    line_string = "ENSP00000272298 ENSP00000272298 0 0 0 0 0 0 0 960"
    item_string = string_adapter.parse_line(line_string)
    assert item_string is not None
    assert item_string.combined_score == 0.96
    
    # Verify BioGRID parser normalize
    biogrid_adapter = BiogridAdapter()
    line_biogrid = "1\t3643\t3643\t\t\t\t\t\t\t\t\tphysical\tTwo-hybrid\t\t123456"
    item_biogrid = biogrid_adapter.parse_line(line_biogrid)
    assert item_biogrid is not None
    assert "BioGRID" in item_biogrid.source_databases
    assert item_biogrid.publications == ["123456"]

def test_bayesian_combiner():
    from graph.etl.loaders.knowledge_graph_builder import KnowledgeGraphBuilder
    builder = KnowledgeGraphBuilder()
    
    # 1 - (1 - 0.8) * (1 - 0.5) = 1 - 0.2 * 0.5 = 1 - 0.1 = 0.9
    combined = builder.combine_confidence(0.8, 0.5)
    assert abs(combined - 0.9) < 1e-5
    print(f"[TEST] Bayesian combination test: 0.8 + 0.5 = {combined}")

def test_merger_deduplicate():
    from graph.etl.loaders.knowledge_graph_builder import KnowledgeGraphBuilder
    from graph.etl.ingestion.canonical_schema import CanonicalInteraction
    builder = KnowledgeGraphBuilder()
    
    # Build duplicate list: A-B and B-A
    i1 = CanonicalInteraction("P01308", "Q15345", combined_score=0.8, source_databases=["STRING"])
    i2 = CanonicalInteraction("Q15345", "P01308", combined_score=0.5, source_databases=["BioGRID"])
    
    merged = builder.merge_interactions([i1, i2])
    assert len(merged) == 1
    assert abs(merged[0].combined_score - 0.9) < 1e-5
    assert set(merged[0].source_databases) == {"STRING", "BioGRID"}

if __name__ == "__main__":
    print("Running Phase 3 UIG backend tests...")
    test_mappers()
    test_adapters()
    test_bayesian_combiner()
    test_merger_deduplicate()
    print("All Phase 3 UIG tests passed successfully!")
