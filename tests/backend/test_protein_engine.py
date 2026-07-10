import sys
from pathlib import Path

# Resolve workspace imports
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def test_fasta_parsing():
    from pipelines.preprocessing.fasta_parser import FastaParser
    parser = FastaParser()
    
    fasta_data = """
    >sp|P01308|INS_HUMAN Insulin OS=Homo sapiens GN=INS PE=1 SV=1
    MALWMRLLPLLALLALWGPDPAAAFVNQHLCGSHLVEALYLVCGERGFFYTPKTR
    REAEDLQVGQVELGGGPGAGSLQPLALEGSLQKRGIVEQCCTSICSLYQLENYCN
    """
    entries = parser.parse_string(fasta_data)
    assert len(entries) == 1
    entry = entries[0]
    assert entry["id"] == "P01308"
    assert entry["name"] == "INS_HUMAN"
    assert entry["organism"] == "Homo sapiens"
    assert entry["gene"] == "INS"
    assert "MALWMR" in entry["sequence"]

def test_tokenizer():
    from ai.protein_foundation.protein_tokenizer import ProteinTokenizer
    tokenizer = ProteinTokenizer(max_length=50)
    
    seq = "MNGTEGPNFY"
    assert tokenizer.validate_sequence(seq)[0] is True
    
    tokens = tokenizer.tokenize(seq, add_special_tokens=False)
    # Validate character map conversion
    assert len(tokens) == len(seq)
    assert tokens[0] == tokenizer.char_to_id["M"]

def test_model_registry():
    from ai.protein_foundation.registry import registry
    
    # Verify adapters are registered
    esm = registry.get("esm2")
    protbert = registry.get("protbert")
    assert esm is not None
    assert protbert is not None
    
    # Run mock/actual embed forward pass
    seq = "MALWMRLLPLLAL"
    res = esm.embed(seq)
    assert "pooled" in res
    assert "per_residue" in res
    assert res["pooled"].shape[0] in [640, 1280]

def test_cross_fusion():
    from ai.protein_foundation.registry import registry
    from ai.protein_foundation.fusion import fusion_registry
    from pipelines.preprocessing.structure_ingestion import PdbParser
    
    # Parse mock PDB content
    pdb_parser = PdbParser()
    struct_feats = pdb_parser.parse_string("") # loads mock fallback
    
    esm = registry.get("esm2")
    seq = "A" * struct_feats["num_residues"]
    seq_emb = esm.embed(seq)["per_residue"]
    
    # Get cross-attention fusion strategy
    strategy = fusion_registry.get("cross_attention")
    fused = strategy.fuse(seq_emb, struct_feats)
    
    assert fused.shape == (struct_feats["num_residues"], 1024)

if __name__ == "__main__":
    print("Running Phase 2 backend engine tests...")
    test_fasta_parsing()
    test_tokenizer()
    test_model_registry()
    test_cross_fusion()
    print("All Phase 2 tests passed successfully!")
