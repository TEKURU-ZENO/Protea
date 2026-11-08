# scripts/prepare_string_dataset.py
import os
import sys
sys.path.insert(0, os.path.abspath("."))

import json
import time
import urllib.request
import torch
from ai.protein_foundation.registry import registry

def get_unique_proteins():
    with open("data/string/string_human_ppi_raw.json", "r", encoding="utf-8") as f:
        edges = json.load(f)
    proteins = sorted(list(set([e["preferredName_A"] for e in edges] + [e["preferredName_B"] for e in edges])))
    return proteins, edges

def fetch_sequences(proteins):
    seq_file = "data/string/protein_sequences.json"
    if os.path.exists(seq_file):
        with open(seq_file, "r", encoding="utf-8") as f:
            sequences = json.load(f)
    else:
        sequences = {}

    missing = [p for p in proteins if p not in sequences]
    print(f"Total proteins: {len(proteins)}, cached: {len(sequences)}, missing to fetch: {len(missing)}")

    for i, g in enumerate(missing):
        url = f"https://rest.uniprot.org/uniprotkb/search?query=gene_exact:{g}+AND+organism_id:9606+AND+reviewed:true&format=json&size=1"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Protea/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                res = json.loads(resp.read().decode())
                if res.get("results"):
                    entry = res["results"][0]
                    sequences[g] = {
                        "uniprot_id": entry["primaryAccession"],
                        "sequence": entry["sequence"]["value"]
                    }
                    print(f"[{i+1}/{len(missing)}] {g} -> {entry['primaryAccession']} (len {len(entry['sequence']['value'])})")
                else:
                    # Fallback query without gene_exact
                    fallback_url = f"https://rest.uniprot.org/uniprotkb/search?query={g}+AND+organism_id:9606+AND+reviewed:true&format=json&size=1"
                    req2 = urllib.request.Request(fallback_url, headers={"User-Agent": "Protea/1.0"})
                    with urllib.request.urlopen(req2, timeout=10) as resp2:
                        res2 = json.loads(resp2.read().decode())
                        if res2.get("results"):
                            entry = res2["results"][0]
                            sequences[g] = {
                                "uniprot_id": entry["primaryAccession"],
                                "sequence": entry["sequence"]["value"]
                            }
                            print(f"[{i+1}/{len(missing)}] {g} (fuzzy) -> {entry['primaryAccession']} (len {len(entry['sequence']['value'])})")
        except Exception as e:
            print(f"Error fetching {g}: {e}")
        time.sleep(0.05)

    with open(seq_file, "w", encoding="utf-8") as f:
        json.dump(sequences, f, indent=2)
    return sequences

def generate_embeddings(proteins, sequences):
    emb_file = "data/string/esm2_embeddings.pt"
    if os.path.exists(emb_file):
        print("Loading cached ESM-2 embeddings from", emb_file)
        return torch.load(emb_file)

    print("Initializing ESM-2 model from registry...")
    esm = registry.get("esm2")
    
    emb_dict = {}
    for i, p in enumerate(proteins):
        if p in sequences:
            seq = sequences[p]["sequence"]
            seq_trunc = seq[:1022]
            res = esm.embed(seq_trunc)
            emb_dict[p] = torch.tensor(res["pooled"], dtype=torch.float)
            print(f"Embedded {i+1}/{len(proteins)}: {p} (dim {len(res['pooled'])})")
        else:
            emb_dict[p] = torch.zeros(640, dtype=torch.float)

    torch.save(emb_dict, emb_file)
    print("Saved ESM-2 embeddings to", emb_file)
    return emb_dict

def main():
    os.makedirs("data/string", exist_ok=True)
    proteins, raw_edges = get_unique_proteins()
    sequences = fetch_sequences(proteins)
    embeddings = generate_embeddings(proteins, sequences)

    # Build node mapping
    node_to_idx = {p: i for i, p in enumerate(proteins)}
    idx_to_node = {i: p for i, p in enumerate(proteins)}
    
    # Feature matrix X
    feat_dim = len(next(iter(embeddings.values())))
    X = torch.zeros((len(proteins), feat_dim), dtype=torch.float)
    for p, idx in node_to_idx.items():
        if p in embeddings:
            X[idx] = embeddings[p]

    # Deduplicated undirected positive edges
    edge_pairs = set()
    for e in raw_edges:
        u = e["preferredName_A"]
        v = e["preferredName_B"]
        if u != v and u in node_to_idx and v in node_to_idx:
            i, j = node_to_idx[u], node_to_idx[v]
            edge_pairs.add((min(i, j), max(i, j)))

    pos_edges = sorted(list(edge_pairs))
    print(f"Total nodes: {len(proteins)}, Feature shape: {X.shape}")
    print(f"Total unique positive edges: {len(pos_edges)}")

    processed_data = {
        "x": X,
        "pos_edges": pos_edges,
        "proteins": proteins,
        "node_to_idx": node_to_idx,
        "idx_to_node": idx_to_node,
        "sequences": sequences
    }
    torch.save(processed_data, "data/string/processed_string_graph.pt")
    print("Saved processed graph data to data/string/processed_string_graph.pt")

if __name__ == "__main__":
    main()
