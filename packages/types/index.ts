export interface Protein {
  id: string;
  uniprotId: string;
  name: string;
  organism: string;
  sequence: string;
  length: number;
  structureFileUrl?: string; // e.g. MinIO PDB link
  molecularWeight?: number;
  subcellularLocation?: string;
  molecularFunction?: string[];
}

export interface Interaction {
  sourceProteinId: string;
  targetProteinId: string;
  confidenceScore: number;
  interactionType: 'phosphorylation' | 'ubiquitination' | 'binding' | 'regulatory' | 'unknown';
  tissueSpecificity?: string[];
  evidenceCodes: string[]; // e.g. ECO codes
  uncertaintyVariance?: number; // Bayesian uncertainty metric
}

export interface Mutation {
  proteinId: string;
  position: number;
  wildType: string;
  mutant: string;
  deltaDeltaG?: number; // stability impact
  pathogenicity?: 'benign' | 'likely_benign' | 'uncertain' | 'likely_pathogenic' | 'pathogenic';
  clinicalContexts?: string[];
}

export interface Pathway {
  id: string;
  name: string;
  nodes: string[]; // Protein IDs
  edges: { source: string; target: string; weight?: number; type?: string }[];
  organism: string;
  description?: string;
  confidenceScore?: number;
}

export interface SimulationState {
  time: number;
  abundances: Record<string, number>; // Protein ID -> relative abundance
}

export interface SystemStatus {
  status: 'healthy' | 'unstable' | 'degraded';
  databases: {
    postgres: boolean;
    neo4j: boolean;
    redis: boolean;
    qdrant: boolean;
    minio: boolean;
  };
  uptimeSeconds: number;
  version: string;
}
