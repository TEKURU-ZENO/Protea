// ============================================================================
// PROTEA Knowledge Graph Schema Definition
// Phase 1 - Constraints & Indexes ONLY (No data seeded)
// Aligning with OptimusKG and Biolink standards.
// ============================================================================

// --- PROTEIN CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT protein_id_unique IF NOT EXISTS
FOR (p:Protein) REQUIRE p.id IS UNIQUE;

CREATE INDEX protein_uniprot_idx IF NOT EXISTS
FOR (p:Protein) ON (p.uniprotId);

CREATE INDEX protein_name_idx IF NOT EXISTS
FOR (p:Protein) ON (p.name);

// --- GENE CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT gene_id_unique IF NOT EXISTS
FOR (g:Gene) REQUIRE g.id IS UNIQUE;

CREATE INDEX gene_symbol_idx IF NOT EXISTS
FOR (g:Gene) ON (g.symbol);

// --- PATHWAY CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT pathway_id_unique IF NOT EXISTS
FOR (pw:Pathway) REQUIRE pw.id IS UNIQUE;

CREATE INDEX pathway_name_idx IF NOT EXISTS
FOR (pw:Pathway) ON (pw.name);

// --- DISEASE CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT disease_id_unique IF NOT EXISTS
FOR (d:Disease) REQUIRE d.id IS UNIQUE;

CREATE INDEX disease_name_idx IF NOT EXISTS
FOR (d:Disease) ON (d.name);

// --- DRUG CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT drug_id_unique IF NOT EXISTS
FOR (dr:Drug) REQUIRE dr.id IS UNIQUE;

CREATE INDEX drug_name_idx IF NOT EXISTS
FOR (dr:Drug) ON (dr.name);

// --- ORGANISM CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT organism_id_unique IF NOT EXISTS
FOR (o:Organism) REQUIRE o.id IS UNIQUE;

// --- TISSUE CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT tissue_id_unique IF NOT EXISTS
FOR (t:Tissue) REQUIRE t.id IS UNIQUE;

// --- PUBLICATION CONSTRAINTS & INDEXES ---
CREATE CONSTRAINT publication_id_unique IF NOT EXISTS
FOR (pub:Publication) REQUIRE pub.id IS UNIQUE;
