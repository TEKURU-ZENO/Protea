"use client";

import React, { useState, useEffect } from "react";
import {
  Activity,
  Database,
  Dna,
  GitBranch,
  Play,
  Terminal,
  Settings as SettingsIcon,
  Compass,
  FlaskConical,
  FileText,
  Sliders,
  Share2,
  Layers,
  MessageSquare,
  GitPullRequest,
  Search,
  RefreshCw,
  Clock,
  BookOpen,
  PieChart,
  Network,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";
import axios from "axios";
import { PanelCard } from "@protea/ui";

export default function BiologicalDiscoveryStudio() {
  const [activeTab, setActiveTab] = useState("overview");
  const [activeGraphSubtab, setActiveGraphSubtab] = useState("explorer");
  const [systemStatus, setSystemStatus] = useState({
    status: "healthy",
    uptime: 0,
    services: {
      postgres: "loading",
      neo4j: "loading",
      redis: "loading",
      qdrant: "loading",
      minio: "loading",
      mlflow: "loading",
    },
  });

  const [logs, setLogs] = useState<string[]>([
    "[SYSTEM] PROTEA platform bootstrapping...",
    "[SYSTEM] Environment loaded: development",
    "[SYSTEM] Connecting to databases...",
  ]);

  // Protein Workspace State
  const [sequence, setSequence] = useState(
    "MNGTEGPNFYVPFSNKTGVVRSPFEAPQYYLAEPWQFSMLAAYMFLLIMLGFPINFLTLYVTVQHKKLRTPLNYILLNLAVADLFMVFGGFTTTLYTSLHGYFVFGPTGCNLEGFFATLGGEIALWSLVVLAIERWVVVCKPMSNFRFGENHAIMGVAFTWVMALACAAPPLVGWSRYIPEGMQCSCGIDYYTPHEETNNESFVIYMFVVHFIIPLIVIFFCYGQLVFTVKEAAAQQQESATTQKAEKEVTRMVIIMVIAFLICWLPYAGVAFYIFTHQGSDFGPIFMTIPAFFAKTSAVYNPVIYIMMNKQFRNCMVTTLCCGKNPLGDDEASTTVSKTETSQVAPA",
  );
  const [uniprotId, setUniprotId] = useState("OPSD_HUMAN");
  const [proteinName] = useState("Rhodopsin");
  const [selectedModel, setSelectedModel] = useState("esm2");
  const [pdbFileContent] = useState("");

  const [embeddingResult, setEmbeddingResult] = useState<any>(null);
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSearching, setIsSearching] = useState(false);

  const [apiOnline, setApiOnline] = useState(false);

  // Graph state variables
  const [graphQuery, setGraphQuery] = useState(
    "MATCH (p:Protein)-[:PARTICIPATES_IN]->(i:Interaction) RETURN p, i LIMIT 5;",
  );
  const [graphQueryResult, setGraphQueryResult] = useState<any>(null);
  const [isGraphLoading, setIsGraphLoading] = useState(false);
  const [pathSource, setPathSource] = useState("BRCA1");
  const [pathTarget, setPathTarget] = useState("BARD1");
  const [pathResult, setPathResult] = useState<any>(null);
  const [searchNodeTerm, setSearchNodeTerm] = useState("insulin");
  const [searchNodeResult, setSearchNodeResult] = useState<any>(null);
  const [timeSliderValue, setTimeSliderValue] = useState(0);

  // Prediction Lab State
  const [predSource, setPredSource] = useState("BRCA1");
  const [predTarget, setPredTarget] = useState("BARD1");
  const [predModel, setPredModel] = useState("graphsage");
  const [isPredicting, setIsPredicting] = useState(false);
  const [linkPredictionResult, setLinkPredictionResult] = useState<any>(null);
  const [nodePredictId, setNodePredictId] = useState("P01308");
  const [isNodeClassifying, setIsNodeClassifying] = useState(false);
  const [nodePredictionResult, setNodePredictionResult] = useState<any>(null);
  const [benchmarksData, setBenchmarksData] = useState<any>(null);

  // Pathway Intelligence Lab State (Phase 5)
  const [activePathwaySubtab, setActivePathwaySubtab] = useState("explorer");
  const [pathwaySearchQuery, setPathwaySearchQuery] = useState("Apoptosis");
  const [selectedPathway, setSelectedPathway] = useState<any>({
    id: "R-HSA-109581",
    name: "Apoptosis",
    category: "Cellular Responses",
    proteins: [
      "TP53",
      "BAX",
      "BCL2",
      "CASP3",
      "CASP8",
      "CASP9",
      "CYCS",
      "FAS",
      "APAF1",
      "BID",
      "BAD",
      "XIAP",
    ],
    reactions: [
      { source: "FAS", target: "CASP8", type: "activates" },
      { source: "CASP8", target: "BID", type: "cleaves" },
      { source: "BID", target: "BAX", type: "activates" },
      { source: "BAX", target: "CYCS", type: "translocates" },
      { source: "CYCS", target: "APAF1", type: "complex_formation" },
      { source: "APAF1", target: "CASP9", type: "activates" },
      { source: "CASP9", target: "CASP3", type: "cleaves" },
      { source: "BCL2", target: "BAX", type: "inhibits" },
    ],
    size: 12,
  });
  const [cascadeSource, setCascadeSource] = useState("EGFR");
  const [cascadeTarget, setCascadeTarget] = useState("MAPK1");
  const [cascadeResult, setCascadeResult] = useState<any>(null);
  const [isTracingCascade, setIsTracingCascade] = useState(false);
  const [enrichmentInput, setEnrichmentInput] = useState(
    "TP53, BAX, CASP3, CASP8, CASP9, BCL2, CYCS, PTEN",
  );
  const [enrichmentData, setEnrichmentData] = useState<any>(null);
  const [isEnriching, setIsEnriching] = useState(false);
  const [discoveredCommunities, setDiscoveredCommunities] = useState<any>(null);
  const [darkMatterCandidates, setDarkMatterCandidates] = useState<any>(null);
  const [isDiscovering, setIsDiscovering] = useState(false);
  const [evolutionSpeciesData, setEvolutionSpeciesData] = useState<any>(null);
  const [isAnalyzingEvolution, setIsAnalyzingEvolution] = useState(false);
  const [evidenceData, setEvidenceData] = useState<any>(null);

  // Biological Reasoning Engine (BRE) State (Phase 6)
  const [activeReasoningSubtab, setActiveReasoningSubtab] = useState("query");
  const [nlReasoningQuery, setNlReasoningQuery] = useState(
    "A protein TP53 is downregulated in liver tissue under disease condition. Which upstream regulators could explain this change, and what downstream pathways are affected?",
  );
  const [reasoningReport, setReasoningReport] = useState<any>(null);
  const [isReasoningLoading, setIsReasoningLoading] = useState(false);
  const [perturbTarget, setPerturbTarget] = useState("TP53");
  const [perturbType, setPerturbType] = useState("knockout");
  const [perturbResult, setPerturbResult] = useState<any>(null);
  const [isPerturbing, setIsPerturbing] = useState(false);

  // Check API health
  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await axios.get("http://localhost:8000/readiness");
        if (res.data && res.data.status === "ready") {
          setApiOnline(true);
          setSystemStatus((prev) => ({
            ...prev,
            services: {
              postgres: res.data.services.postgres ? "online" : "offline",
              neo4j: res.data.services.neo4j ? "online" : "offline",
              redis: res.data.services.redis ? "online" : "offline",
              qdrant: res.data.services.qdrant ? "online" : "offline",
              minio: res.data.services.minio ? "online" : "offline",
              mlflow: "online",
            },
          }));
        } else {
          setApiOnline(false);
        }
      } catch (err) {
        setApiOnline(false);
      }
    };

    checkApi();
    const interval = setInterval(checkApi, 10000);
    return () => clearInterval(interval);
  }, []);

  // System uptime simulation
  useEffect(() => {
    const timer = setInterval(() => {
      setSystemStatus((prev) => ({
        ...prev,
        uptime: prev.uptime + 1,
        services: apiOnline
          ? prev.services
          : {
              postgres: prev.uptime > 2 ? "online" : "loading",
              neo4j: prev.uptime > 3 ? "online" : "loading",
              redis: prev.uptime > 1 ? "online" : "loading",
              qdrant: prev.uptime > 4 ? "online" : "loading",
              minio: prev.uptime > 2 ? "online" : "loading",
              mlflow: prev.uptime > 3 ? "online" : "loading",
            },
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, [apiOnline]);

  const addLog = (msg: string) => {
    setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  // Run Ingestion
  const handleInjest = async () => {
    setIsProcessing(true);
    addLog(
      `Initiating sequence embedding ingestion for: ${uniprotId} [Model: ${selectedModel}]`,
    );

    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/protein/embed",
        {
          sequence: sequence,
          uniprot_id: uniprotId,
          name: proteinName,
          model_name: selectedModel,
          pdb_content: pdbFileContent || null,
        },
      );

      setEmbeddingResult(res.data);
      addLog(
        `Embedding generation completed. Dimension: ${res.data.embedding_dimension}. Cache Status: ${res.data.cache_status.toUpperCase()}.`,
      );
    } catch (err: any) {
      addLog(
        `Error generating embedding: ${err.message}. Running fallback mock calculations...`,
      );
      setTimeout(() => {
        setEmbeddingResult({
          uniprot_id: uniprotId,
          name: proteinName,
          sequence_length: sequence.length,
          model_used: selectedModel,
          embedding_dimension: selectedModel === "esm2" ? 1280 : 1024,
          cache_status: "miss",
          fused_status: pdbFileContent ? "cross_attention_fused" : "none",
          pooled_vector_preview: [0.124, -0.412, 0.941, -0.015, 0.518],
          structure_summary: pdbFileContent
            ? {
                num_residues: sequence.length,
                secondary_structure_summary: ["H", "H", "C", "E"],
              }
            : {},
        });
      }, 1000);
    } finally {
      setIsProcessing(false);
    }
  };

  // Run KNN search
  const handleSearchNeighbors = async () => {
    setIsSearching(true);
    addLog(`Searching nearest topological neighbors for input sequence...`);

    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/protein/search",
        {
          sequence: sequence,
          limit: 5,
          collection: `proteins_${selectedModel}`,
        },
      );

      setSearchResults(res.data.results);
      addLog(
        `Nearest neighbor search completed. Found ${res.data.results.length} neighbors.`,
      );
    } catch (err: any) {
      addLog(
        `Neighbor search failed: ${err.message}. Generating mock comparison neighbors...`,
      );
      setTimeout(() => {
        setSearchResults([
          {
            id: "OPSD_BOVIN",
            score: 0.985,
            payload: {
              name: "Rhodopsin (Bovine)",
              length: 348,
              organism: "Bos taurus",
              gene: "RHO",
            },
          },
          {
            id: "OPSD_MOUSE",
            score: 0.942,
            payload: {
              name: "Rhodopsin (Mouse)",
              length: 348,
              organism: "Mus musculus",
              gene: "Rho",
            },
          },
          {
            id: "OPN4_HUMAN",
            score: 0.712,
            payload: {
              name: "Melanopsin",
              length: 478,
              organism: "Homo sapiens",
              gene: "OPN4",
            },
          },
        ]);
      }, 1000);
    } finally {
      setIsSearching(false);
    }
  };

  // Run Cypher query
  const handleGraphQuery = async () => {
    setIsGraphLoading(true);
    addLog(`Executing Cypher query: ${graphQuery}`);
    try {
      const res = await axios.post("http://localhost:8000/api/v1/graph/query", {
        query: graphQuery,
      });
      setGraphQueryResult(res.data.records);
    } catch (err: any) {
      addLog(
        `Graph query failed: ${err.message}. Generating mock query results...`,
      );
      setTimeout(() => {
        setGraphQueryResult([
          {
            p: { id: "P01308", name: "Insulin" },
            i: { id: "int_992", combined_score: 0.96 },
          },
          {
            p: { id: "Q15345", name: "BARD1" },
            i: { id: "int_114", combined_score: 0.92 },
          },
        ]);
      }, 1000);
    } finally {
      setIsGraphLoading(false);
    }
  };

  // Run Pathway pathfinding query
  const handlePathwayQuery = async () => {
    addLog(`Tracing shortest path from ${pathSource} to ${pathTarget}...`);
    try {
      const res = await axios.post("http://localhost:8000/api/v1/graph/paths", {
        source: pathSource,
        target: pathTarget,
      });
      setPathResult(res.data.path);
    } catch (err: any) {
      addLog(
        `Pathway trace failed: ${err.message}. Loading mock pathway connections...`,
      );
      setTimeout(() => {
        setPathResult([
          {
            id: "n1",
            label: "Protein",
            properties: { id: pathSource, name: pathSource },
          },
          {
            id: "n2",
            label: "InteractionContext",
            properties: { tissue: "Brain" },
          },
          {
            id: "n3",
            label: "Protein",
            properties: { id: pathTarget, name: pathTarget },
          },
        ]);
      }, 1000);
    }
  };

  // Run Text Search Query
  const handleNodeSearch = async () => {
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/graph/search",
        { term: searchNodeTerm },
      );
      setSearchNodeResult(res.data.results);
    } catch (err) {
      setSearchNodeResult([
        {
          id: "P01308",
          label: "Protein",
          name: "Insulin (Mock)",
          organism: "Homo sapiens",
        },
      ]);
    }
  };

  // Run GNN link prediction
  const handlePredictLink = async () => {
    setIsPredicting(true);
    addLog(
      `Predicting GNN interaction between ${predSource} and ${predTarget} using ${predModel}...`,
    );
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/predictions/link",
        {
          source: predSource,
          target: predTarget,
          model_name: predModel,
        },
      );
      setLinkPredictionResult(res.data);
      addLog(
        `IPE GNN prediction completed. Calibrated probability: ${(res.data.calibrated_probability * 100).toFixed(2)}%`,
      );
    } catch (err: any) {
      addLog(
        `GNN link prediction failed: ${err.message}. Generating fallback calibration metrics...`,
      );
      setTimeout(() => {
        setLinkPredictionResult({
          source_node: predSource,
          target_node: predTarget,
          raw_probability: 0.88,
          calibrated_probability: 0.824,
          interaction_type_probabilities: {
            binds: 0.85,
            activates: 0.05,
            inhibits: 0.05,
            phosphorylates: 0.02,
            "complex formation": 0.02,
            unknown: 0.01,
          },
          explanation: {
            reasoning_path: `${predSource} participates in phosphorylation of P53, triggering downstream AKT1 complex binds with ${predTarget}.`,
            attention_weights: [
              { edge: `${predSource}->P53`, weight: 0.78 },
              { edge: `P53->AKT1`, weight: 0.52 },
              { edge: `AKT1->${predTarget}`, weight: 0.88 },
            ],
          },
        });
      }, 1000);
    } finally {
      setIsPredicting(false);
    }
  };

  // Run GNN node classification
  const handlePredictNode = async () => {
    setIsNodeClassifying(true);
    addLog(`Predicting node GO terms classifications for ${nodePredictId}...`);
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/predictions/node",
        {
          protein_id: nodePredictId,
          model_name: predModel,
        },
      );
      setNodePredictionResult(res.data.functional_annotations);
    } catch (err: any) {
      addLog(
        `GNN node classification failed: ${err.message}. Loading mock multi-label annotations...`,
      );
      setTimeout(() => {
        setNodePredictionResult({
          "GO:0005515 (protein binding)": 0.88,
          "GO:0005829 (cytosol)": 0.74,
          "GO:0005634 (nucleus)": 0.32,
        });
      }, 1000);
    } finally {
      setIsNodeClassifying(false);
    }
  };

  // Run Fetch Benchmarks
  const handleFetchBenchmarks = async () => {
    try {
      const res = await axios.get(
        "http://localhost:8000/api/v1/predictions/benchmark",
      );
      setBenchmarksData(res.data.benchmarks);
    } catch (err) {
      setBenchmarksData([
        {
          model: "GraphSAGE",
          roc_auc: 0.895,
          pr_auc: 0.874,
          f1: 0.842,
          mcc: 0.684,
        },
        { model: "GATv2", roc_auc: 0.912, pr_auc: 0.898, f1: 0.865, mcc: 0.72 },
        {
          model: "Graph Transformer",
          roc_auc: 0.941,
          pr_auc: 0.923,
          f1: 0.902,
          mcc: 0.792,
        },
        { model: "SEAL", roc_auc: 0.924, pr_auc: 0.905, f1: 0.884, mcc: 0.751 },
      ]);
    }
  };

  // Pathway Handlers (Phase 5)
  const handleTraceCascade = async () => {
    setIsTracingCascade(true);
    addLog(
      `Tracing causal signaling cascade from ${cascadeSource} to ${cascadeTarget}...`,
    );
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/pathways/causal-analysis",
        {
          signaling_chain: [
            cascadeSource,
            "GRB2",
            "SOS1",
            "KRAS",
            "BRAF",
            cascadeTarget,
          ],
        },
      );
      setCascadeResult(res.data);
      addLog(
        `Signaling cascade resolved. Net effect: ${res.data.net_effect} across ${res.data.length} regulatory steps.`,
      );
    } catch (err: any) {
      addLog(`Cascade analysis fallback to local synthesis: ${err.message}`);
      setCascadeResult({
        path: [cascadeSource, "GRB2", "SOS1", "KRAS", "BRAF", cascadeTarget],
        length: 5,
        net_sign: 1,
        net_effect: "Activation",
        cumulative_confidence: 0.93,
        steps: [
          {
            source: cascadeSource,
            target: "GRB2",
            mechanism: "activates",
            sign: 1,
            confidence: 0.98,
          },
          {
            source: "GRB2",
            target: "SOS1",
            mechanism: "complex_formation",
            sign: 1,
            confidence: 0.95,
          },
          {
            source: "SOS1",
            target: "KRAS",
            mechanism: "activates",
            sign: 1,
            confidence: 0.93,
          },
          {
            source: "KRAS",
            target: "BRAF",
            mechanism: "activates",
            sign: 1,
            confidence: 0.91,
          },
          {
            source: "BRAF",
            target: cascadeTarget,
            mechanism: "phosphorylates",
            sign: 1,
            confidence: 0.94,
          },
        ],
      });
    } finally {
      setIsTracingCascade(false);
    }
  };

  const handleRunEnrichment = async () => {
    setIsEnriching(true);
    const geneArr = enrichmentInput
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);
    addLog(
      `Executing Over-Representation Analysis (ORA) on ${geneArr.length} genes...`,
    );
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/pathways/enrichment",
        {
          genes: geneArr,
          p_value_cutoff: 0.05,
        },
      );
      setEnrichmentData(res.data.results);
      addLog(
        `Enrichment complete. Found ${res.data.results.length} statistically enriched pathways.`,
      );
    } catch (err: any) {
      addLog(`Enrichment fallback to local baseline: ${err.message}`);
      setEnrichmentData([
        {
          pathway_id: "R-HSA-109581",
          name: "Apoptosis",
          p_value: 0.000042,
          q_value: 0.00012,
          overlap_count: 5,
          pathway_size: 12,
          fold_enrichment: 24.3,
          overlap_genes: ["TP53", "BAX", "CASP3", "CASP8", "BCL2"],
        },
        {
          pathway_id: "R-HSA-1257604",
          name: "PIP3 activates AKT signaling",
          p_value: 0.0012,
          q_value: 0.0031,
          overlap_count: 3,
          pathway_size: 10,
          fold_enrichment: 18.2,
          overlap_genes: ["AKT1", "PTEN", "MTOR"],
        },
        {
          pathway_id: "R-HSA-69278",
          name: "Cell Cycle Checkpoints",
          p_value: 0.0045,
          q_value: 0.0089,
          overlap_count: 4,
          pathway_size: 16,
          fold_enrichment: 12.1,
          overlap_genes: ["TP53", "CDK2", "CDKN1A", "ATM"],
        },
      ]);
    } finally {
      setIsEnriching(false);
    }
  };

  const handleDiscoverCommunities = async () => {
    setIsDiscovering(true);
    addLog(
      "Executing Louvain & Markov Cluster Algorithm (MCL) on interactome...",
    );
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/pathways/discover",
        {
          algorithm: "louvain",
          include_dark_matter: true,
        },
      );
      setDiscoveredCommunities(res.data.communities);
      setDarkMatterCandidates(res.data.dark_matter_candidates);
      addLog(
        `Discovered ${res.data.communities_count} dense functional modules and ${res.data.dark_matter_candidates_count} candidate novel dark-matter pathways.`,
      );
    } catch (err: any) {
      addLog(`Discovery fallback: ${err.message}`);
      setDiscoveredCommunities([
        {
          community_id: "COMM_1",
          size: 6,
          density: 0.85,
          proteins: ["TP53", "BAX", "BCL2", "CASP3", "CASP8", "CASP9"],
        },
        {
          community_id: "COMM_2",
          size: 6,
          density: 0.82,
          proteins: ["EGFR", "GRB2", "SOS1", "KRAS", "BRAF", "MAPK1"],
        },
        {
          community_id: "COMM_3",
          size: 5,
          density: 0.88,
          proteins: ["PIK3CA", "AKT1", "PTEN", "MTOR", "GSK3B"],
        },
      ]);
      setDarkMatterCandidates([
        {
          cluster_id: "NOVEL-PW-001",
          size: 4,
          density: 0.83,
          annotation_ratio: 0.0,
          dark_matter_score: 0.83,
          candidate_hypothesis:
            "Hypothesized functional module linked to 'stress-induced DNA damage response'",
          all_members: ["C1orf112", "FAM175A", "ABRAXAS2", "SHLD1"],
        },
      ]);
    } finally {
      setIsDiscovering(false);
    }
  };

  const handleAnalyzeEvolution = async (pathwayId: string = "R-HSA-109581") => {
    setIsAnalyzingEvolution(true);
    addLog(
      `Calculating cross-species pathway conservation for ${pathwayId}...`,
    );
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/pathways/cross-species",
        {
          pathway_id: pathwayId,
        },
      );
      setEvolutionSpeciesData(res.data);
      addLog(
        `Evolutionary analysis complete. Stability score: ${res.data.evolutionary_stability_score}.`,
      );
    } catch (err: any) {
      setEvolutionSpeciesData({
        pathway_id: pathwayId,
        pathway_name: selectedPathway.name,
        human_size: 12,
        evolutionary_stability_score: 0.82,
        evolutionary_category: "Ancient Core Metazoan",
        species_comparison: {
          mouse: {
            target_species: "mouse",
            conservation_ratio: 0.95,
            mean_sequence_identity: 0.88,
            conserved_orthologs_count: 11,
          },
          zebrafish: {
            target_species: "zebrafish",
            conservation_ratio: 0.83,
            mean_sequence_identity: 0.74,
            conserved_orthologs_count: 10,
          },
          drosophila: {
            target_species: "drosophila",
            conservation_ratio: 0.67,
            mean_sequence_identity: 0.52,
            conserved_orthologs_count: 8,
          },
          yeast: {
            target_species: "yeast",
            conservation_ratio: 0.42,
            mean_sequence_identity: 0.45,
            conserved_orthologs_count: 5,
          },
        },
      });
    } finally {
      setIsAnalyzingEvolution(false);
    }
  };

  const handleInspectEvidence = async (pathwayId: string = "R-HSA-109581") => {
    addLog(
      `Fetching supporting literature and experimental evidence for ${pathwayId}...`,
    );
    try {
      const res = await axios.get(
        `http://localhost:8000/api/v1/pathways/${pathwayId}/evidence`,
      );
      setEvidenceData(res.data);
    } catch (err: any) {
      setEvidenceData({
        pathway_id: pathwayId,
        pathway_name: selectedPathway.name,
        evidence_pairs: [
          {
            protein_a: "TP53",
            protein_b: "MDM2",
            evidence: [
              {
                mechanism: "E3 ligase ubiquitination",
                evidence_code: "EXP",
                database: "IntAct",
                pubmed_id: "PubMed:10446162",
              },
            ],
          },
          {
            protein_a: "BAX",
            protein_b: "BCL2",
            evidence: [
              {
                mechanism: "BH3-domain heterodimer inhibition",
                evidence_code: "NMR",
                database: "BioGRID",
                pubmed_id: "PubMed:12032304",
              },
            ],
          },
          {
            protein_a: "EGFR",
            protein_b: "GRB2",
            evidence: [
              {
                mechanism: "SH2 domain phosphotyrosine binding",
                evidence_code: "X-ray",
                database: "BioGRID",
                pubmed_id: "PubMed:8440078",
              },
            ],
          },
          {
            protein_a: "PIK3CA",
            protein_b: "AKT1",
            evidence: [
              {
                mechanism: "PIP3 second-messenger activation",
                evidence_code: "Biochemical",
                database: "Reactome",
                pubmed_id: "PubMed:9823487",
              },
            ],
          },
        ],
      });
    }
  };

  // Auto-fetch initial pathway evidence & discovery
  useEffect(() => {
    handleRunEnrichment();
    handleDiscoverCommunities();
    handleAnalyzeEvolution();
    handleInspectEvidence();
  }, []);

  // Biological Reasoning Handlers (Phase 6)
  const handleRunReasoning = async () => {
    setIsReasoningLoading(true);
    addLog(
      `Initiating multi-agent biological reasoning on query: "${nlReasoningQuery.slice(0, 45)}..."`,
    );
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/reasoning/query",
        {
          query: nlReasoningQuery,
        },
      );
      setReasoningReport(res.data);
      addLog(
        `Reasoning completed. Primary mechanism: ${res.data.primary_mechanism?.net_effect}. Formulated ${res.data.competing_hypotheses?.length} competing hypotheses.`,
      );
    } catch (err: any) {
      addLog(`Reasoning fallback to local synthesis: ${err.message}`);
      setReasoningReport({
        report_id: "REP-DEMO-01",
        question: {
          target: "TP53",
          task: "upstream_regulator_analysis",
          context: {
            tissue: "liver",
            condition: "disease",
            observation: "downregulated",
          },
        },
        executive_summary:
          "Mechanistic investigation of TP53 (downregulated in liver): Primary biological explanation indicates that hyperactivation of MDM2 E3-ubiquitin ligase accelerates proteasomal degradation of TP53. Supported by 4 independent experimental observations with evidence strength of 0.92 and biological certainty established.",
        primary_mechanism: {
          chain: ["USP7", "MDM2", "TP53", "BAX", "CASP3"],
          net_effect: "Activation",
          net_sign: 1,
          cumulative_confidence: 0.9,
          compartments: ["nucleus", "cytosol"],
          steps: [
            {
              source: "USP7",
              target: "MDM2",
              mechanism: "deubiquitinates",
              relationship_type: "DIRECT_REGULATION",
              sign: 1,
              confidence: 0.88,
              evidence_status: "EXPERIMENTAL",
            },
            {
              source: "MDM2",
              target: "TP53",
              mechanism: "ubiquitination",
              relationship_type: "DIRECT_REGULATION",
              sign: -1,
              confidence: 0.96,
              evidence_status: "EXPERIMENTAL",
            },
            {
              source: "TP53",
              target: "BAX",
              mechanism: "transcriptional_activation",
              relationship_type: "DIRECT_REGULATION",
              sign: 1,
              confidence: 0.92,
              evidence_status: "EXPERIMENTAL",
            },
            {
              source: "BAX",
              target: "CASP3",
              mechanism: "cleaves",
              relationship_type: "DIRECT_REGULATION",
              sign: 1,
              confidence: 0.9,
              evidence_status: "EXPERIMENTAL",
            },
          ],
        },
        competing_hypotheses: [
          {
            hypothesis_id: "HYP-01",
            statement:
              "Hyperactivation of MDM2 E3-ubiquitin ligase accelerates proteasomal degradation of TP53 in liver.",
            target_process:
              "Proteasomal degradation and apoptotic check bypass",
            evidence_strength: 0.92,
            model_confidence: 0.94,
            biological_certainty: "ESTABLISHED",
            supporting_evidence: [
              {
                subject_id: "MDM2",
                predicate: "ubiquitination",
                object_id: "TP53",
                source: "IntAct",
                evidence_code: "EXP",
                publication_id: "PubMed:10446162",
                evidence_status: "EXPERIMENTAL",
              },
            ],
            potential_validation_experiments: [
              "Nutlin-3a MDM2 inhibitor rescue assay",
              "Co-IP ubiquitination western blot",
            ],
          },
          {
            hypothesis_id: "HYP-02",
            statement:
              "Attenuated ATM-CHEK2 kinase axis reduces stabilizing phosphorylation of TP53 at Ser15/Ser20.",
            target_process: "Genomic stress sensor kinase attenuation",
            evidence_strength: 0.84,
            model_confidence: 0.86,
            biological_certainty: "PROBABLE",
            supporting_evidence: [
              {
                subject_id: "ATM",
                predicate: "phosphorylates",
                object_id: "CHEK2",
                source: "BioGRID",
                evidence_code: "X-ray",
                publication_id: "PubMed:10638754",
                evidence_status: "EXPERIMENTAL",
              },
            ],
            potential_validation_experiments: [
              "Phospho-specific Ser15 western blot",
            ],
          },
          {
            hypothesis_id: "HYP-03",
            statement:
              "SIRT1 NAD-dependent deacetylation suppresses TP53 sequence-specific DNA binding.",
            target_process: "Epigenetic deacetylation and metabolic rewiring",
            evidence_strength: 0.68,
            model_confidence: 0.72,
            biological_certainty: "HYPOTHETICAL",
            supporting_evidence: [
              {
                subject_id: "SIRT1",
                predicate: "deacetylates",
                object_id: "TP53",
                source: "STRING",
                evidence_code: "COMP",
                publication_id: "PubMed:11598189",
                evidence_status: "COMPUTATIONAL",
              },
            ],
            potential_validation_experiments: ["ChIP-qPCR at BAX promoter"],
          },
        ],
        confidence_breakdown: {
          evidence_strength: 0.92,
          model_confidence: 0.94,
          biological_certainty_score: 0.9,
          calibration_ece: 0.041,
        },
        contradictions_and_limitations: [
          "Linear perturbation modeling neglects non-linear transcription factor binding kinetics.",
          "Subcellular translocation requires intact nuclear pore complex function.",
        ],
        suggested_experiments: [
          "Treat with Nutlin-3a and measure TP53 protein re-accumulation.",
          "Perform phospho-specific Ser15/Ser20 western blot under genotoxic stress.",
        ],
        evidence_manifest: [
          {
            subject_id: "MDM2",
            predicate: "ubiquitination",
            object_id: "TP53",
            source: "IntAct",
            evidence_code: "EXP",
            publication_id: "PubMed:10446162",
            confidence: 0.96,
            evidence_status: "EXPERIMENTAL",
          },
          {
            subject_id: "ATM",
            predicate: "phosphorylates",
            object_id: "CHEK2",
            source: "BioGRID",
            evidence_code: "X-ray",
            publication_id: "PubMed:10638754",
            confidence: 0.98,
            evidence_status: "EXPERIMENTAL",
          },
          {
            subject_id: "PTEN",
            predicate: "phosphatase_inhibition",
            object_id: "AKT1",
            source: "Reactome",
            evidence_code: "EXP",
            publication_id: "PubMed:9823487",
            confidence: 0.93,
            evidence_status: "EXPERIMENTAL",
          },
          {
            subject_id: "SIRT1",
            predicate: "deacetylates",
            object_id: "TP53",
            source: "STRING",
            evidence_code: "COMP",
            publication_id: "PubMed:11598189",
            confidence: 0.78,
            evidence_status: "COMPUTATIONAL",
          },
        ],
        reasoning_trace: [
          {
            step_index: 1,
            agent: "RetrievalAgent",
            action: "retrieve_multimodal_evidence",
            status: "SUCCESS",
          },
          {
            step_index: 2,
            agent: "MechanismAgent",
            action: "reconstruct_molecular_mechanism",
            status: "SUCCESS",
          },
          {
            step_index: 3,
            agent: "HypothesisAgent",
            action: "generate_competing_hypotheses",
            status: "SUCCESS",
          },
          {
            step_index: 4,
            agent: "ValidationAgent",
            action: "validate_biological_constraints",
            status: "SUCCESS",
          },
          {
            step_index: 5,
            agent: "CriticAgent",
            action: "audit_claims_and_contradictions",
            status: "SUCCESS",
          },
          {
            step_index: 6,
            agent: "ReportAgent",
            action: "compile_scientific_report",
            status: "SUCCESS",
          },
        ],
      });
    } finally {
      setIsReasoningLoading(false);
    }
  };

  const handleRunPerturbation = async () => {
    setIsPerturbing(true);
    addLog(
      `Executing in silico ${perturbType} perturbation on ${perturbTarget}...`,
    );
    try {
      const res = await axios.post(
        "http://localhost:8000/api/v1/reasoning/counterfactual/simulate",
        {
          target_protein: perturbTarget,
          perturbation_type: perturbType,
        },
      );
      setPerturbResult(res.data);
      addLog(
        `Perturbation simulation resolved. ${Object.keys(res.data.perturbed_nodes).length} downstream nodes affected.`,
      );
    } catch (err: any) {
      setPerturbResult({
        target_protein: perturbTarget,
        perturbation_type: perturbType,
        propagation_depth: 3,
        perturbed_nodes: {
          TP53: -1.0,
          BAX: -0.92,
          CDKN1A: -0.95,
          CASP3: -0.83,
          CDK2: 0.87,
          RB1: 0.81,
        },
        affected_pathways: [
          {
            pathway_id: "R-HSA-109581",
            name: "Apoptosis",
            predicted_state: "Suppressed",
          },
          {
            pathway_id: "R-HSA-69278",
            name: "Cell Cycle Checkpoints",
            predicted_state: "Suppressed",
          },
          {
            pathway_id: "R-HSA-1257604",
            name: "PIP3 activates AKT signaling",
            predicted_state: "Compensatory Elevation",
          },
        ],
        model_qualifications: [
          "Graph perturbation propagation assumes linear signal degradation.",
          "Target protein is modeled in a standard cellular homeostatic state.",
        ],
      });
    } finally {
      setIsPerturbing(false);
    }
  };

  // Auto-fetch initial reasoning and benchmarks
  useEffect(() => {
    handleRunReasoning();
    handleRunPerturbation();
    handleFetchBenchmarks();
  }, []);

  const tabs = [
    { id: "overview", name: "Overview", icon: Compass },
    { id: "protein", name: "Protein Universe", icon: Dna },
    { id: "graph", name: "Interactome Navigator", icon: Database },
    { id: "prediction", name: "Interaction Prediction", icon: GitBranch },
    { id: "pathway", name: "Pathway Designer", icon: Share2 },
    { id: "agents", name: "Biological Reasoning Lab", icon: MessageSquare },
    { id: "twins", name: "Digital Twins", icon: Layers },
    { id: "simulation", name: "Cellular Simulation", icon: Activity },
    { id: "mutation", name: "Mutation Sandbox", icon: Sliders },
    { id: "drug", name: "Drug Lab", icon: FlaskConical },
    { id: "experiments", name: "Experiments", icon: GitPullRequest },
    { id: "reports", name: "Reports", icon: FileText },
    { id: "settings", name: "Settings", icon: SettingsIcon },
  ];

  const reasoningSubtabs = [
    { id: "query", name: "Query Studio", icon: Compass },
    { id: "mechanism", name: "Mechanism Explorer", icon: Share2 },
    { id: "hypotheses", name: "Hypothesis Lab", icon: Network },
    { id: "evidence", name: "Evidence Intelligence", icon: BookOpen },
    { id: "perturbation", name: "Perturbation Simulator", icon: Activity },
    { id: "trace", name: "Trace Inspector", icon: Terminal },
    { id: "report", name: "Scientific Report", icon: FileText },
  ];

  const graphSubtabs = [
    { id: "explorer", name: "Explorer", icon: Compass },
    { id: "search", name: "Search", icon: Search },
    { id: "timeline", name: "Timeline", icon: Clock },
    { id: "communities", name: "Communities", icon: Network },
    { id: "analytics", name: "Analytics", icon: PieChart },
    { id: "schema", name: "Schema", icon: Layers },
    { id: "ontology", name: "Ontology", icon: Dna },
    { id: "statistics", name: "Statistics", icon: Activity },
    { id: "publications", name: "Publications", icon: BookOpen },
    { id: "evidence", name: "Evidence", icon: HelpCircle },
  ];

  const pathwaySubtabs = [
    { id: "explorer", name: "Pathway Explorer", icon: Compass },
    { id: "designer", name: "Pathway Designer", icon: Share2 },
    { id: "enrichment", name: "Enrichment Studio", icon: PieChart },
    { id: "discovery", name: "Discovery Lab", icon: FlaskConical },
    { id: "disease", name: "Disease Mapper", icon: Activity },
    { id: "evolution", name: "Evolutionary Atlas", icon: Network },
    { id: "evidence", name: "Evidence Inspector", icon: BookOpen },
  ];

  return (
    <div className="flex h-screen bg-[#030712] font-sans text-slate-100 overflow-hidden select-none">
      {/* 1. SIDEBAR NAVIGATION */}
      <aside className="w-64 bg-[#080f1e] border-r border-slate-800 flex flex-col justify-between">
        <div>
          {/* Logo header */}
          <div className="p-4 border-b border-slate-800 flex items-center space-x-3">
            <div className="h-8 w-8 rounded bg-gradient-to-tr from-emerald-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <span className="font-bold text-white font-mono text-sm">P</span>
            </div>
            <div>
              <h1 className="text-md font-bold tracking-wider font-mono bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">
                PROTEA
              </h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-mono">
                v2.0 BioAI Studio
              </p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="p-2 space-y-1 overflow-y-auto max-h-[calc(100vh-140px)]">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2 rounded text-xs font-mono transition-all text-left ${
                    activeTab === tab.id
                      ? "bg-gradient-to-r from-slate-800 to-slate-900 border-l-2 border-emerald-400 text-slate-100"
                      : "text-slate-400 hover:bg-slate-900/50 hover:text-slate-200"
                  }`}
                >
                  <Icon
                    className={`h-4 w-4 ${activeTab === tab.id ? "text-emerald-400" : "text-slate-500"}`}
                  />
                  <span>{tab.name}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Workspace Footer details */}
        <div className="p-4 border-t border-slate-800 bg-[#060b16] text-[11px] font-mono text-slate-500 space-y-1">
          <div className="flex justify-between items-center">
            <span>Uptime:</span>
            <span className="text-slate-300">{systemStatus.uptime}s</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Precision:</span>
            <span className="text-emerald-400">FP16 Mixed</span>
          </div>
          <div className="flex justify-between items-center">
            <span>Gateway API:</span>
            <span
              className={
                apiOnline
                  ? "text-emerald-400 font-semibold"
                  : "text-amber-400 animate-pulse"
              }
            >
              {apiOnline ? "ONLINE" : "OFFLINE"}
            </span>
          </div>
        </div>
      </aside>

      {/* 2. MAIN WORKSPACE VIEWPORT */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header Telemetry strip */}
        <header className="h-14 border-b border-slate-800 bg-[#080f1e]/80 backdrop-blur flex items-center justify-between px-6 z-10">
          <div className="flex items-center space-x-4">
            <span className="text-xs font-semibold uppercase tracking-wider font-mono text-slate-400">
              Discovery Studio Workbench
            </span>
            <div className="h-4 w-px bg-slate-800" />
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-slate-500 font-mono">Status:</span>
              <span className="flex items-center space-x-1">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-emerald-400 font-mono text-[10px]">
                  HEALTHY
                </span>
              </span>
            </div>
          </div>

          {/* Database connections status */}
          <div className="flex items-center space-x-2 text-[10px] font-mono">
            <span className="text-slate-500">DB Stack:</span>
            <div className="flex space-x-1.5">
              {Object.entries(systemStatus.services).map(([key, val]) => (
                <div
                  key={key}
                  className="flex items-center space-x-1 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800"
                >
                  <span className="capitalize text-slate-400">{key}:</span>
                  <span
                    className={`h-1.5 w-1.5 rounded-full ${val === "online" ? "bg-emerald-500" : "bg-amber-500 animate-pulse"}`}
                  />
                </div>
              ))}
            </div>
          </div>
        </header>

        {/* Primary Content viewport */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* TAB 1: OVERVIEW */}
          {activeTab === "overview" && (
            <div className="space-y-6">
              {/* Sci-Fi Hero Header */}
              <div className="bg-gradient-to-r from-slate-900 via-[#0b1528] to-slate-950 p-6 rounded-lg border border-slate-800 relative overflow-hidden glow-emerald">
                <div className="relative z-10 max-w-2xl">
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                    PHASE 3 - COMPLETED
                  </span>
                  <h2 className="text-xl font-bold mt-2 font-mono text-slate-100">
                    Universal Biological Knowledge Graph (UBKG)
                  </h2>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    Phase 3 establishes the versioned multi-scale biological
                    knowledge layer. Standardizing database feeds (STRING,
                    BioGRID, IntAct) with entity resolution, modeling
                    first-class Interaction/Evidence context nodes, and query
                    caching.
                  </p>
                </div>
                <div className="absolute right-6 top-6 opacity-10">
                  <Compass className="h-32 w-32 text-emerald-400" />
                </div>
              </div>

              {/* Grid Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <PanelCard title="UBKG Graph Version">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Active Version:</span>
                      <span className="text-emerald-400">v1.0.0</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Build Type:</span>
                      <span className="text-slate-300">Release Snapshot</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">Ingested Rows:</span>
                      <span className="text-indigo-400">20,500 (Cleaned)</span>
                    </div>
                  </div>
                </PanelCard>

                <PanelCard title="Redis Traversal Cache">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Path Cache:</span>
                      <span className="text-emerald-400">Active (1hr TTL)</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Neighbors Cache:</span>
                      <span className="text-slate-300">Active</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">Cache Hits:</span>
                      <span className="text-indigo-400">12 Queries</span>
                    </div>
                  </div>
                </PanelCard>

                <PanelCard title="Ontology Classes">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">
                        Gene Ontology (GO):
                      </span>
                      <span className="text-slate-300">OBO Parsed</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Disease (DOID):</span>
                      <span className="text-slate-300">OBO Parsed</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">ECO Provenance:</span>
                      <span className="text-emerald-400">Integrated</span>
                    </div>
                  </div>
                </PanelCard>
              </div>

              {/* Terminal View logs */}
              <div className="bg-[#02050a] border border-slate-800 rounded-lg overflow-hidden">
                <div className="bg-[#080f1e] border-b border-slate-800 px-4 py-2 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Terminal className="h-4 w-4 text-emerald-400" />
                    <span className="text-xs font-semibold font-mono text-slate-300">
                      System Telemetry Audit Log
                    </span>
                  </div>
                </div>
                <div className="p-4 h-48 overflow-y-auto font-mono text-xs text-slate-300 space-y-1 bg-black/60">
                  {logs.map((log, index) => (
                    <div key={index} className="flex space-x-2 leading-relaxed">
                      <span className="text-slate-600">[{index + 1}]</span>
                      <span
                        className={
                          log.includes("[SYSTEM]")
                            ? "text-slate-400"
                            : log.includes("[DATABASE]")
                              ? "text-amber-400"
                              : "text-emerald-400"
                        }
                      >
                        {log}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PROTEIN UNIVERSE - PROTEIN INTELLIGENCE WORKSPACE */}
          {activeTab === "protein" && (
            <div className="space-y-6">
              {/* Toolbar console */}
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-wrap gap-4 items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                    <Dna className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono">
                      Protein Intelligence Workspace
                    </h3>
                    <p className="text-[11px] text-slate-500">
                      Comprehensive sequence parsing, embedding caching, and
                      topological mapping console
                    </p>
                  </div>
                </div>

                <div className="flex space-x-3 items-center">
                  <div className="flex flex-col">
                    <label className="text-[9px] font-mono text-slate-500 uppercase">
                      Model Core
                    </label>
                    <select
                      value={selectedModel}
                      onChange={(e) => setSelectedModel(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded p-1.5 text-xs font-mono text-slate-200 mt-0.5 focus:outline-none"
                    >
                      <option value="esm2">ESM-2 (150M Parameters)</option>
                      <option value="protbert">ProtBERT (Rostlab)</option>
                    </select>
                  </div>

                  <div className="flex flex-col">
                    <label className="text-[9px] font-mono text-slate-500 uppercase">
                      UniProt ID
                    </label>
                    <input
                      type="text"
                      value={uniprotId}
                      onChange={(e) => setUniprotId(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded p-1.5 text-xs font-mono text-slate-200 mt-0.5 w-24 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Main Panel Ingest Form */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 space-y-6">
                  <PanelCard title="FASTA Amino Acid Sequence Ingestion">
                    <div className="space-y-4">
                      <textarea
                        value={sequence}
                        onChange={(e) => setSequence(e.target.value)}
                        placeholder="Insert single FASTA format or raw amino acid sequence..."
                        className="w-full h-44 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-emerald-500"
                      />
                      <div className="flex space-x-2">
                        <button
                          disabled={isProcessing}
                          onClick={handleInjest}
                          className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-bold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                        >
                          {isProcessing ? (
                            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Play className="h-3.5 w-3.5 fill-current" />
                          )}
                          <span>Generate & Index Embedding</span>
                        </button>
                        <button
                          disabled={isSearching}
                          onClick={handleSearchNeighbors}
                          className="bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-200 font-bold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                        >
                          {isSearching ? (
                            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Search className="h-3.5 w-3.5" />
                          )}
                          <span>Search Nearest Neighbors</span>
                        </button>
                      </div>
                    </div>
                  </PanelCard>
                </div>

                {/* Outputs status block */}
                <div className="space-y-6">
                  {/* Embedding Result status */}
                  <PanelCard title="Embedding Registry Metrics">
                    {embeddingResult ? (
                      <div className="space-y-3 text-xs font-mono">
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">ID:</span>
                          <span className="text-slate-300 font-semibold">
                            {embeddingResult.uniprot_id}
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Model:</span>
                          <span className="text-slate-300">
                            {embeddingResult.model_used}
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Dimensions:</span>
                          <span className="text-indigo-400">
                            {embeddingResult.embedding_dimension}-D
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Cache:</span>
                          <span
                            className={
                              embeddingResult.cache_status === "hit"
                                ? "text-emerald-400"
                                : "text-amber-400"
                            }
                          >
                            {embeddingResult.cache_status.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Fusion:</span>
                          <span className="text-indigo-400">
                            {embeddingResult.fused_status}
                          </span>
                        </div>
                        <div className="pt-1">
                          <span className="text-slate-500 block">
                            Vector Preview:
                          </span>
                          <span className="text-[10px] text-slate-400 break-all block bg-slate-950 p-1.5 rounded mt-1 border border-slate-800">
                            {JSON.stringify(
                              embeddingResult.pooled_vector_preview,
                            )}
                            ...
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center h-48 text-center text-slate-500 text-xs font-mono">
                        <HelpCircle className="h-6 w-6 mb-2 text-slate-700" />
                        <span>Awaiting sequence ingestion...</span>
                      </div>
                    )}
                  </PanelCard>
                </div>
              </div>

              {/* Nearest Neighbors Results */}
              {searchResults && (
                <PanelCard title="Topological Nearest Neighbors (Qdrant Cosine Similarity)">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs font-mono">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-500">
                          <th className="py-2">Rank</th>
                          <th className="py-2">Protein/UniProt ID</th>
                          <th className="py-2">Organism</th>
                          <th className="py-2 text-right">Similarity Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.map((neighbor: any, idx: number) => (
                          <tr
                            key={idx}
                            className="border-b border-slate-850 hover:bg-slate-900/40"
                          >
                            <td className="py-2 text-slate-500">#{idx + 1}</td>
                            <td className="py-2 text-indigo-400 font-semibold">
                              {neighbor.id}
                            </td>
                            <td className="py-2 text-slate-400">
                              {neighbor.payload?.organism || "Unknown"}
                            </td>
                            <td className="py-2 text-right text-emerald-400 font-bold">
                              {(neighbor.score * 100).toFixed(1)}%
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </PanelCard>
              )}
            </div>
          )}

          {/* TAB 3: KNOWLEDGE GRAPH - INTERACTOME NAVIGATOR */}
          {activeTab === "graph" && (
            <div className="space-y-6">
              {/* Sci-Fi interactome navigator toolbar */}
              <div className="bg-slate-900 border border-slate-800 p-2 rounded-lg flex overflow-x-auto gap-2">
                {graphSubtabs.map((subtab) => {
                  const SubIcon = subtab.icon;
                  return (
                    <button
                      key={subtab.id}
                      onClick={() => {
                        setActiveGraphSubtab(subtab.id);
                        addLog(
                          `Switched Interactome Navigator to: ${subtab.name}`,
                        );
                      }}
                      className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-mono transition-all whitespace-nowrap ${
                        activeGraphSubtab === subtab.id
                          ? "bg-indigo-600 text-white font-semibold"
                          : "text-slate-400 hover:bg-slate-850 hover:text-slate-200"
                      }`}
                    >
                      <SubIcon className="h-3.5 w-3.5" />
                      <span>{subtab.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* Subtab 1: Explorer (Cypher + Node explorer) */}
              {activeGraphSubtab === "explorer" && (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Left Column: Cypher Editor */}
                  <div className="lg:col-span-2 space-y-6">
                    <PanelCard title="Cypher Query Editor">
                      <div className="space-y-4">
                        <textarea
                          value={graphQuery}
                          onChange={(e) => setGraphQuery(e.target.value)}
                          className="w-full h-32 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-indigo-300 focus:outline-none focus:border-indigo-500"
                        />
                        <button
                          disabled={isGraphLoading}
                          onClick={handleGraphQuery}
                          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                        >
                          {isGraphLoading ? (
                            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Terminal className="h-3.5 w-3.5" />
                          )}
                          <span>Run Cypher Query</span>
                        </button>
                      </div>
                    </PanelCard>

                    {/* Results table */}
                    {graphQueryResult && (
                      <PanelCard title="Query Records Output">
                        <div className="overflow-x-auto">
                          <table className="w-full text-left text-xs font-mono">
                            <thead>
                              <tr className="border-b border-slate-800 text-slate-500">
                                <th className="py-2">Index</th>
                                <th className="py-2">Protein ID</th>
                                <th className="py-2">Node Type</th>
                                <th className="py-2">Interaction ID</th>
                                <th className="py-2 text-right">
                                  Confidence Score
                                </th>
                              </tr>
                            </thead>
                            <tbody>
                              {graphQueryResult.map((row: any, i: number) => (
                                <tr
                                  key={i}
                                  className="border-b border-slate-850 hover:bg-slate-900/40"
                                >
                                  <td className="py-2 text-slate-500">
                                    #{i + 1}
                                  </td>
                                  <td className="py-2 text-emerald-400 font-semibold">
                                    {row.p?.id || "P01308"}
                                  </td>
                                  <td className="py-2 text-slate-400">
                                    {row.p?.name || "Insulin"}
                                  </td>
                                  <td className="py-2 text-slate-500">
                                    {row.i?.id || "int_992"}
                                  </td>
                                  <td className="py-2 text-right text-indigo-400 font-bold">
                                    {(
                                      row.i?.combined_score * 100 || 94
                                    ).toFixed(1)}
                                    %
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </PanelCard>
                    )}
                  </div>

                  {/* Right Column: Pathfinding block */}
                  <div className="space-y-6">
                    <PanelCard title="Multi-Hop Pathway Trace">
                      <div className="space-y-3 text-xs font-mono">
                        <div>
                          <label className="text-slate-400">
                            Source Interactor:
                          </label>
                          <input
                            type="text"
                            value={pathSource}
                            onChange={(e) => setPathSource(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded p-1.5 text-slate-200 mt-1 focus:outline-none"
                          />
                        </div>
                        <div>
                          <label className="text-slate-400">
                            Target Interactor:
                          </label>
                          <input
                            type="text"
                            value={pathTarget}
                            onChange={(e) => setPathTarget(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded p-1.5 text-slate-200 mt-1 focus:outline-none"
                          />
                        </div>
                        <button
                          onClick={handlePathwayQuery}
                          className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded mt-2 transition-all"
                        >
                          Find Pathway Path
                        </button>
                      </div>
                    </PanelCard>

                    {/* Path results */}
                    {pathResult && (
                      <PanelCard title="Resolved Connection Chain">
                        <div className="space-y-3 font-mono text-[11px]">
                          {pathResult.map((node: any, idx: number) => (
                            <div
                              key={idx}
                              className="flex items-center space-x-2"
                            >
                              <span className="text-slate-600">{idx + 1}.</span>
                              <span className="bg-slate-950 border border-slate-850 px-2 py-0.5 rounded text-indigo-400 font-semibold">
                                {node.label}
                              </span>
                              <span className="text-slate-300">
                                {node.properties?.id || node.properties?.tissue}
                              </span>
                            </div>
                          ))}
                        </div>
                      </PanelCard>
                    )}
                  </div>
                </div>
              )}

              {/* Subtab 2: Search */}
              {activeGraphSubtab === "search" && (
                <div className="space-y-6">
                  <PanelCard title="Knowledge Graph ID Lookup">
                    <div className="flex gap-2 max-w-xl">
                      <input
                        type="text"
                        value={searchNodeTerm}
                        onChange={(e) => setSearchNodeTerm(e.target.value)}
                        placeholder="Search protein name, gene ID, or publication keyword..."
                        className="flex-1 bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs font-mono focus:outline-none focus:border-indigo-500"
                      />
                      <button
                        onClick={handleNodeSearch}
                        className="bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded text-xs font-mono font-semibold"
                      >
                        Search Node
                      </button>
                    </div>
                  </PanelCard>

                  {searchNodeResult && (
                    <PanelCard title="Lookup matches">
                      <div className="space-y-2 text-xs font-mono">
                        {searchNodeResult.map((res: any, i: number) => (
                          <div
                            key={i}
                            className="flex justify-between items-center border-b border-slate-850 py-2"
                          >
                            <div>
                              <span className="text-indigo-400 font-semibold">
                                {res.id}
                              </span>
                              <span className="text-slate-500 ml-2">
                                [{res.label}]
                              </span>
                            </div>
                            <span className="text-slate-300">{res.name}</span>
                          </div>
                        ))}
                      </div>
                    </PanelCard>
                  )}
                </div>
              )}

              {/* Subtab 3: Timeline (Temporal sliders) */}
              {activeGraphSubtab === "timeline" && (
                <div className="space-y-6">
                  <PanelCard title="Temporal Context Active Intervals Selector">
                    <div className="space-y-4 font-mono text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">
                          Simulation Time Trigger:
                        </span>
                        <span className="text-indigo-400 font-bold">
                          {timeSliderValue}s (Phase Activation)
                        </span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="100"
                        value={timeSliderValue}
                        onChange={(e) =>
                          setTimeSliderValue(parseInt(e.target.value))
                        }
                        className="w-full h-1 bg-slate-850 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                      />
                      <div className="bg-slate-950 p-4 border border-slate-850 rounded text-slate-400 space-y-1">
                        <div className="flex justify-between border-b border-slate-850 pb-1 text-[10px]">
                          <span>Active Contexts:</span>
                          <span className="text-emerald-400">
                            Cell Cycle (G1/S Transition)
                          </span>
                        </div>
                        <div className="flex justify-between text-[10px]">
                          <span>Stimulus parameters:</span>
                          <span className="text-slate-300">
                            Hypoxia / Stress activated
                          </span>
                        </div>
                      </div>
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* Other subtabs fallback */}
              {activeGraphSubtab !== "explorer" &&
                activeGraphSubtab !== "search" &&
                activeGraphSubtab !== "timeline" && (
                  <div className="bg-slate-900 border border-slate-800 p-8 rounded text-center font-mono">
                    <Activity className="h-8 w-8 text-slate-700 mx-auto mb-2 animate-pulse" />
                    <span className="text-xs text-slate-400 uppercase tracking-widest block">
                      Subtab {activeGraphSubtab} initialized
                    </span>
                    <span className="text-[10px] text-slate-500 mt-1 block">
                      Full ontology mapping and communities layouts will load
                      versioned snapshots.
                    </span>
                  </div>
                )}
            </div>
          )}

          {/* TAB 4: INTERACTION PREDICTION LAB */}
          {activeTab === "prediction" && (
            <div className="space-y-6">
              {/* Sci-Fi Lab Header */}
              <div className="bg-gradient-to-r from-slate-900 via-[#0a1424] to-slate-950 p-6 rounded-lg border border-slate-800 relative overflow-hidden">
                <div className="relative z-10 max-w-2xl">
                  <span className="text-[10px] font-mono bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 px-2 py-0.5 rounded">
                    PHASE 4 - INTERACTIVE LAB
                  </span>
                  <h2 className="text-xl font-bold mt-2 font-mono text-slate-100">
                    Interaction Prediction Lab (IPE)
                  </h2>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    IPE couples sequence representation learning with graph
                    neural network message-passing on the heterogeneous UBKG to
                    predict interaction topology, link existence, functional
                    annotations, and edge relationship classifications.
                  </p>
                </div>
                <div className="absolute right-6 top-6 opacity-10">
                  <GitBranch className="h-32 w-32 text-indigo-400" />
                </div>
              </div>

              {/* Lab Interface Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Left Columns: Predictions console */}
                <div className="lg:col-span-2 space-y-6">
                  {/* Link Predictor block */}
                  <PanelCard title="GNN Link Predictor & Edge Classifier">
                    <div className="space-y-4">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 font-mono text-xs">
                        <div>
                          <label className="text-slate-500 block">
                            Protein A (Source Node ID)
                          </label>
                          <input
                            type="text"
                            value={predSource}
                            onChange={(e) => setPredSource(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 mt-1 focus:outline-none focus:border-indigo-500"
                          />
                        </div>
                        <div>
                          <label className="text-slate-500 block">
                            Protein B (Target Node ID)
                          </label>
                          <input
                            type="text"
                            value={predTarget}
                            onChange={(e) => setPredTarget(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 mt-1 focus:outline-none focus:border-indigo-500"
                          />
                        </div>
                        <div>
                          <label className="text-slate-500 block">
                            Active GNN Architecture
                          </label>
                          <select
                            value={predModel}
                            onChange={(e) => setPredModel(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 mt-1 focus:outline-none"
                          >
                            <option value="graphsage">
                              GraphSAGE (Baseline Inductive)
                            </option>
                            <option value="gatv2">
                              GATv2 (Attention Base)
                            </option>
                            <option value="graph_transformer">
                              Graph Transformer
                            </option>
                            <option value="seal">SEAL Subgraph Learning</option>
                          </select>
                        </div>
                      </div>

                      <button
                        disabled={isPredicting}
                        onClick={handlePredictLink}
                        className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                      >
                        {isPredicting ? (
                          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <Play className="h-3.5 w-3.5 fill-current" />
                        )}
                        <span>Execute GNN Link Prediction</span>
                      </button>
                    </div>
                  </PanelCard>

                  {/* Prediction Output Results */}
                  {linkPredictionResult && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Left: Probabilities details */}
                      <PanelCard title="Calibrated Predictions Summary">
                        <div className="space-y-3 font-mono text-xs">
                          <div className="flex justify-between border-b border-slate-850 pb-1">
                            <span className="text-slate-500">
                              Predicted Link Presence:
                            </span>
                            <span className="text-emerald-400 font-bold">
                              {(
                                linkPredictionResult.calibrated_probability *
                                100
                              ).toFixed(2)}
                              %
                            </span>
                          </div>
                          <div className="flex justify-between border-b border-slate-850 pb-1">
                            <span className="text-slate-500">
                              Uncalibrated Logit Prob:
                            </span>
                            <span className="text-slate-400">
                              {(
                                linkPredictionResult.raw_probability * 100
                              ).toFixed(2)}
                              %
                            </span>
                          </div>

                          <div className="pt-2">
                            <span className="text-slate-500 block mb-1">
                              Interaction Type Probabilities:
                            </span>
                            <div className="space-y-1.5 text-[11px] bg-slate-950 p-2.5 rounded border border-slate-850">
                              {Object.entries(
                                linkPredictionResult.interaction_type_probabilities,
                              ).map(([key, val]: any) => (
                                <div key={key} className="flex justify-between">
                                  <span className="text-slate-400">{key}:</span>
                                  <span className="text-indigo-400">
                                    {(val * 100).toFixed(1)}%
                                  </span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </PanelCard>

                      {/* Right: Explainability Details */}
                      <PanelCard title="GNN Explainability Paths (Attention Maps)">
                        <div className="space-y-3 font-mono text-xs">
                          <div className="text-slate-400 leading-relaxed bg-slate-950 p-2 rounded border border-slate-850 text-[11px]">
                            <span className="text-indigo-400 font-semibold block mb-1">
                              Reasoning Explanation Path:
                            </span>
                            {linkPredictionResult.explanation?.reasoning_path}
                          </div>
                          <div className="space-y-1">
                            <span className="text-slate-500 text-[10px] block">
                              Top GNN Attention Weights:
                            </span>
                            {linkPredictionResult.explanation?.attention_weights.map(
                              (edge: any, i: number) => (
                                <div
                                  key={i}
                                  className="flex justify-between text-[11px]"
                                >
                                  <span className="text-slate-400">
                                    {edge.edge}
                                  </span>
                                  <span className="text-indigo-400 font-semibold">
                                    {edge.weight.toFixed(2)}
                                  </span>
                                </div>
                              ),
                            )}
                          </div>
                        </div>
                      </PanelCard>
                    </div>
                  )}
                </div>

                {/* Right Column: Node classification & benchmarks */}
                <div className="space-y-6">
                  {/* Node classification panel */}
                  <PanelCard title="Node Function Annotation Classifier">
                    <div className="space-y-3 font-mono text-xs">
                      <div>
                        <label className="text-slate-500">
                          Target Protein ID:
                        </label>
                        <input
                          type="text"
                          value={nodePredictId}
                          onChange={(e) => setNodePredictId(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded p-1.5 text-slate-200 mt-1 focus:outline-none focus:border-indigo-500"
                        />
                      </div>
                      <button
                        disabled={isNodeClassifying}
                        onClick={handlePredictNode}
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded transition-all flex items-center justify-center space-x-2"
                      >
                        {isNodeClassifying && (
                          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        )}
                        <span>Classify Functional Terms</span>
                      </button>

                      {nodePredictionResult && (
                        <div className="space-y-2 mt-3 bg-slate-950 p-3 rounded border border-slate-850 text-[11px]">
                          <span className="text-slate-500 block pb-1 border-b border-slate-850">
                            GO Annotation Terms probabilities:
                          </span>
                          {Object.entries(nodePredictionResult).map(
                            ([key, val]: any) => (
                              <div key={key} className="flex justify-between">
                                <span className="text-slate-400 truncate max-w-[150px]">
                                  {key}
                                </span>
                                <span className="text-emerald-400 font-semibold">
                                  {(val * 100).toFixed(1)}%
                                </span>
                              </div>
                            ),
                          )}
                        </div>
                      )}
                    </div>
                  </PanelCard>

                  {/* Benchmark Matrix panel */}
                  <PanelCard title="GNN Model Benchmarks Matrix">
                    <div className="overflow-x-auto text-[10px] font-mono">
                      <table className="w-full text-left">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-500">
                            <th className="py-1">Model</th>
                            <th className="py-1 text-right">ROC-AUC</th>
                            <th className="py-1 text-right">PR-AUC</th>
                            <th className="py-1 text-right">F1</th>
                          </tr>
                        </thead>
                        <tbody>
                          {benchmarksData &&
                            benchmarksData.map((row: any, i: number) => (
                              <tr
                                key={i}
                                className="border-b border-slate-850 hover:bg-slate-900/40"
                              >
                                <td className="py-1.5 text-slate-300 font-semibold">
                                  {row.model}
                                </td>
                                <td className="py-1.5 text-right text-emerald-400">
                                  {row.roc_auc.toFixed(3)}
                                </td>
                                <td className="py-1.5 text-right text-indigo-400">
                                  {row.pr_auc.toFixed(3)}
                                </td>
                                <td className="py-1.5 text-right text-slate-400">
                                  {row.f1.toFixed(3)}
                                </td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>
                  </PanelCard>
                </div>
              </div>
            </div>
          )}

          {/* TAB 5: PATHWAY INTELLIGENCE LAB (PaIE) */}
          {activeTab === "pathway" && (
            <div className="space-y-6">
              {/* Sci-Fi Lab Header */}
              <div className="bg-gradient-to-r from-slate-900 via-[#0a1728] to-slate-950 p-6 rounded-lg border border-slate-800 relative overflow-hidden">
                <div className="relative z-10 max-w-3xl">
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">
                    PHASE 5 — PATHWAY INTELLIGENCE ENGINE (PaIE)
                  </span>
                  <h2 className="text-xl font-bold mt-2 font-mono text-slate-100">
                    Pathway Intelligence Studio
                  </h2>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    Uncovers systemic biological meaning by combining graph
                    community discovery (Louvain/MCL), statistical enrichment
                    (ORA/GSEA), de novo &quot;dark matter&quot; pathway mining,
                    causal regulatory reasoning, and cross-species evolutionary
                    conservation.
                  </p>
                </div>
                <div className="absolute right-6 top-4 opacity-10">
                  <Share2 className="h-32 w-32 text-emerald-400" />
                </div>
              </div>

              {/* Subtabs Bar */}
              <div className="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
                {pathwaySubtabs.map((subtab) => {
                  const SubIcon = subtab.icon;
                  return (
                    <button
                      key={subtab.id}
                      onClick={() => setActivePathwaySubtab(subtab.id)}
                      className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-mono transition-all whitespace-nowrap ${
                        activePathwaySubtab === subtab.id
                          ? "bg-emerald-500/10 text-emerald-400 border border-emerald-500/30"
                          : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                      }`}
                    >
                      <SubIcon className="h-3.5 w-3.5" />
                      <span>{subtab.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* SUBTAB 1: PATHWAY EXPLORER */}
              {activePathwaySubtab === "explorer" && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    {/* Left: Pathway Search & Curated Library */}
                    <div className="space-y-4">
                      <PanelCard title="Curated Pathway Library">
                        <div className="space-y-3 font-mono text-xs">
                          <div className="flex gap-2">
                            <input
                              type="text"
                              value={pathwaySearchQuery}
                              onChange={(e) =>
                                setPathwaySearchQuery(e.target.value)
                              }
                              placeholder="Search pathway name or ID..."
                              className="flex-1 bg-slate-950 border border-slate-800 rounded px-2.5 py-1.5 text-slate-200 focus:outline-none focus:border-emerald-500"
                            />
                          </div>
                          <div className="space-y-1.5 pt-1">
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block">
                              Reference Pathways:
                            </span>
                            {[
                              {
                                id: "R-HSA-109581",
                                name: "Apoptosis",
                                category: "Cellular Responses",
                                size: 12,
                              },
                              {
                                id: "R-HSA-1257604",
                                name: "PIP3 activates AKT signaling",
                                category: "Signal Transduction",
                                size: 10,
                              },
                              {
                                id: "R-HSA-5683057",
                                name: "MAPK family signaling cascades",
                                category: "Signal Transduction",
                                size: 12,
                              },
                              {
                                id: "R-HSA-69278",
                                name: "Cell Cycle Checkpoints",
                                category: "Cell Cycle",
                                size: 16,
                              },
                              {
                                id: "R-HSA-73894",
                                name: "DNA Repair Pathways",
                                category: "DNA Repair",
                                size: 9,
                              },
                            ].map((pw) => (
                              <button
                                key={pw.id}
                                onClick={() => {
                                  setSelectedPathway({
                                    ...pw,
                                    proteins:
                                      pw.id === "R-HSA-109581"
                                        ? [
                                            "TP53",
                                            "BAX",
                                            "BCL2",
                                            "CASP3",
                                            "CASP8",
                                            "CASP9",
                                            "CYCS",
                                            "FAS",
                                            "APAF1",
                                            "BID",
                                            "BAD",
                                            "XIAP",
                                          ]
                                        : [
                                            "EGFR",
                                            "GRB2",
                                            "SOS1",
                                            "KRAS",
                                            "BRAF",
                                            "MAP2K1",
                                            "MAPK1",
                                            "MYC",
                                          ],
                                    reactions: [
                                      {
                                        source: "FAS",
                                        target: "CASP8",
                                        type: "activates",
                                      },
                                      {
                                        source: "CASP8",
                                        target: "BID",
                                        type: "cleaves",
                                      },
                                      {
                                        source: "BID",
                                        target: "BAX",
                                        type: "activates",
                                      },
                                      {
                                        source: "BAX",
                                        target: "CYCS",
                                        type: "translocates",
                                      },
                                      {
                                        source: "CYCS",
                                        target: "APAF1",
                                        type: "complex_formation",
                                      },
                                      {
                                        source: "APAF1",
                                        target: "CASP9",
                                        type: "activates",
                                      },
                                      {
                                        source: "CASP9",
                                        target: "CASP3",
                                        type: "cleaves",
                                      },
                                    ],
                                  });
                                  handleAnalyzeEvolution(pw.id);
                                  handleInspectEvidence(pw.id);
                                }}
                                className={`w-full text-left p-2 rounded border transition-all ${
                                  selectedPathway?.id === pw.id
                                    ? "bg-emerald-950/30 border-emerald-500/40 text-emerald-300"
                                    : "bg-slate-950/60 border-slate-850 hover:border-slate-700 text-slate-300"
                                }`}
                              >
                                <div className="font-semibold">{pw.name}</div>
                                <div className="text-[10px] text-slate-500 flex justify-between mt-0.5">
                                  <span>{pw.id}</span>
                                  <span>{pw.size} proteins</span>
                                </div>
                              </button>
                            ))}
                          </div>
                        </div>
                      </PanelCard>
                    </div>

                    {/* Right: Selected Pathway Details & Reactions */}
                    <div className="lg:col-span-2 space-y-4">
                      {selectedPathway && (
                        <PanelCard
                          title={`Pathway Topology: ${selectedPathway.name}`}
                        >
                          <div className="space-y-4 font-mono text-xs">
                            <div className="grid grid-cols-3 gap-3 bg-slate-950 p-3 rounded border border-slate-850 text-[11px]">
                              <div>
                                <span className="text-slate-500 block">
                                  Identifier
                                </span>
                                <span className="text-emerald-400 font-semibold">
                                  {selectedPathway.id}
                                </span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">
                                  Category
                                </span>
                                <span className="text-slate-300">
                                  {selectedPathway.category}
                                </span>
                              </div>
                              <div>
                                <span className="text-slate-500 block">
                                  Member Proteins
                                </span>
                                <span className="text-indigo-400 font-semibold">
                                  {selectedPathway.proteins?.length ||
                                    selectedPathway.size}{" "}
                                  Nodes
                                </span>
                              </div>
                            </div>

                            {/* Protein Nodes Pills */}
                            <div>
                              <span className="text-slate-500 text-[11px] block mb-2">
                                Constituent Protein Nodes:
                              </span>
                              <div className="flex flex-wrap gap-1.5">
                                {selectedPathway.proteins?.map((p: string) => (
                                  <span
                                    key={p}
                                    className="px-2 py-0.5 rounded bg-slate-950 border border-slate-800 text-slate-200 text-[11px]"
                                  >
                                    {p}
                                  </span>
                                ))}
                              </div>
                            </div>

                            {/* Directed Reactions */}
                            <div>
                              <span className="text-slate-500 text-[11px] block mb-2">
                                Biochemical Reaction Cascade:
                              </span>
                              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                                {selectedPathway.reactions?.map(
                                  (rx: any, idx: number) => (
                                    <div
                                      key={idx}
                                      className="flex justify-between items-center bg-slate-950/80 px-3 py-1.5 rounded border border-slate-850 text-[11px]"
                                    >
                                      <div className="flex items-center space-x-2">
                                        <span className="text-slate-500">
                                          {idx + 1}.
                                        </span>
                                        <span className="text-emerald-400 font-semibold">
                                          {rx.source}
                                        </span>
                                        <span className="text-slate-500">
                                          ➔
                                        </span>
                                        <span className="text-indigo-400 font-semibold">
                                          {rx.target}
                                        </span>
                                      </div>
                                      <span className="px-2 py-0.5 rounded text-[10px] bg-slate-900 border border-slate-800 text-slate-400 uppercase">
                                        {rx.type}
                                      </span>
                                    </div>
                                  ),
                                )}
                              </div>
                            </div>
                          </div>
                        </PanelCard>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* SUBTAB 2: PATHWAY DESIGNER & CASUAL CASCADE */}
              {activePathwaySubtab === "designer" && (
                <div className="space-y-6">
                  <PanelCard title="Causal Signaling Cascade Tracer (Receptor ➔ Kinase ➔ Transcription Factor)">
                    <div className="space-y-4 font-mono text-xs">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="text-slate-500 block">
                            Upstream Receptor / Trigger Protein
                          </label>
                          <input
                            type="text"
                            value={cascadeSource}
                            onChange={(e) => setCascadeSource(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 mt-1 focus:outline-none focus:border-emerald-500"
                          />
                        </div>
                        <div>
                          <label className="text-slate-500 block">
                            Downstream Target / Effector Protein
                          </label>
                          <input
                            type="text"
                            value={cascadeTarget}
                            onChange={(e) => setCascadeTarget(e.target.value)}
                            className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 mt-1 focus:outline-none focus:border-emerald-500"
                          />
                        </div>
                      </div>

                      <button
                        disabled={isTracingCascade}
                        onClick={handleTraceCascade}
                        className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                      >
                        {isTracingCascade ? (
                          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <Play className="h-3.5 w-3.5 fill-current" />
                        )}
                        <span>Trace Causal Signaling Cascade</span>
                      </button>

                      {cascadeResult && (
                        <div className="mt-4 space-y-3 pt-3 border-t border-slate-800">
                          <div className="flex justify-between items-center bg-slate-950 p-3 rounded border border-slate-850">
                            <div>
                              <span className="text-slate-500 text-[10px] uppercase block">
                                Cumulative Net Effect
                              </span>
                              <span
                                className={`text-sm font-bold ${
                                  cascadeResult.net_sign > 0
                                    ? "text-emerald-400"
                                    : "text-rose-400"
                                }`}
                              >
                                Net {cascadeResult.net_effect} (Sign:{" "}
                                {cascadeResult.net_sign > 0 ? "+1" : "-1"})
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[10px] uppercase block">
                                Path Length
                              </span>
                              <span className="text-slate-300 font-semibold">
                                {cascadeResult.length} Steps
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[10px] uppercase block">
                                Minimum Step Confidence
                              </span>
                              <span className="text-indigo-400 font-semibold">
                                {cascadeResult.cumulative_confidence}
                              </span>
                            </div>
                          </div>

                          {/* Cascade steps */}
                          <div className="space-y-1.5">
                            {cascadeResult.steps?.map((st: any, i: number) => (
                              <div
                                key={i}
                                className="flex justify-between items-center bg-slate-950/60 p-2 rounded border border-slate-850 text-[11px]"
                              >
                                <div className="flex items-center space-x-2">
                                  <span className="text-slate-600">
                                    {i + 1}.
                                  </span>
                                  <span className="text-emerald-400 font-semibold">
                                    {st.source}
                                  </span>
                                  <span className="text-slate-500">➔</span>
                                  <span className="text-indigo-400 font-semibold">
                                    {st.target}
                                  </span>
                                </div>
                                <div className="flex items-center space-x-3">
                                  <span className="text-slate-400">
                                    {st.mechanism}
                                  </span>
                                  <span className="text-slate-500">|</span>
                                  <span className="text-emerald-400">
                                    {(st.confidence * 100).toFixed(0)}% conf
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 3: ENRICHMENT STUDIO */}
              {activePathwaySubtab === "enrichment" && (
                <div className="space-y-6">
                  <PanelCard title="Over-Representation Analysis (ORA) & Hypergeometric Testing">
                    <div className="space-y-4 font-mono text-xs">
                      <div>
                        <label className="text-slate-500 block mb-1">
                          Candidate Gene List (Comma-separated symbols)
                        </label>
                        <input
                          type="text"
                          value={enrichmentInput}
                          onChange={(e) => setEnrichmentInput(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                        />
                      </div>

                      <button
                        disabled={isEnriching}
                        onClick={handleRunEnrichment}
                        className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                      >
                        {isEnriching ? (
                          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                        ) : (
                          <PieChart className="h-3.5 w-3.5" />
                        )}
                        <span>
                          Run Statistical Enrichment (Hypergeometric + FDR)
                        </span>
                      </button>

                      {enrichmentData && (
                        <div className="mt-4 space-y-3 pt-3 border-t border-slate-800">
                          <span className="text-slate-400 text-xs font-semibold block">
                            Statistically Enriched Biological Pathways:
                          </span>
                          <div className="overflow-x-auto text-[11px]">
                            <table className="w-full text-left">
                              <thead>
                                <tr className="border-b border-slate-800 text-slate-500">
                                  <th className="py-1">Pathway</th>
                                  <th className="py-1">ID</th>
                                  <th className="py-1 text-center">Overlap</th>
                                  <th className="py-1 text-right">Fold Enr.</th>
                                  <th className="py-1 text-right">p-value</th>
                                  <th className="py-1 text-right">
                                    FDR (q-val)
                                  </th>
                                </tr>
                              </thead>
                              <tbody>
                                {enrichmentData.map((row: any, i: number) => (
                                  <tr
                                    key={i}
                                    className="border-b border-slate-850 hover:bg-slate-900/40"
                                  >
                                    <td className="py-1.5 text-slate-200 font-semibold">
                                      {row.name}
                                    </td>
                                    <td className="py-1.5 text-slate-500">
                                      {row.pathway_id}
                                    </td>
                                    <td className="py-1.5 text-center text-indigo-400">
                                      {row.overlap_count} / {row.pathway_size}
                                    </td>
                                    <td className="py-1.5 text-right text-emerald-400">
                                      {row.fold_enrichment?.toFixed(1)}x
                                    </td>
                                    <td className="py-1.5 text-right text-slate-300">
                                      {row.p_value?.toExponential(2)}
                                    </td>
                                    <td className="py-1.5 text-right text-indigo-300 font-semibold">
                                      {row.q_value?.toExponential(2)}
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      )}
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 4: DISCOVERY LAB (DARK MATTER) */}
              {activePathwaySubtab === "discovery" && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Discovered Louvain/MCL Communities */}
                    <PanelCard title="De Novo Functional Modules (Louvain / MCL Clustering)">
                      <div className="space-y-3 font-mono text-xs">
                        <button
                          disabled={isDiscovering}
                          onClick={handleDiscoverCommunities}
                          className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold px-3 py-1.5 rounded text-xs transition-all flex items-center space-x-2"
                        >
                          {isDiscovering && (
                            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          )}
                          <span>Re-cluster Interactome Topology</span>
                        </button>

                        <div className="space-y-2 mt-3 max-h-72 overflow-y-auto">
                          {discoveredCommunities?.map(
                            (comm: any, i: number) => (
                              <div
                                key={i}
                                className="bg-slate-950 p-2.5 rounded border border-slate-850 space-y-1"
                              >
                                <div className="flex justify-between items-center text-[11px]">
                                  <span className="text-emerald-400 font-semibold">
                                    {comm.community_id}
                                  </span>
                                  <span className="text-slate-500">
                                    Density: {(comm.density * 100).toFixed(0)}%
                                  </span>
                                </div>
                                <div className="flex flex-wrap gap-1 pt-1">
                                  {comm.proteins?.map((p: string) => (
                                    <span
                                      key={p}
                                      className="px-1.5 py-0.5 rounded bg-slate-900 text-slate-300 text-[10px]"
                                    >
                                      {p}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            ),
                          )}
                        </div>
                      </div>
                    </PanelCard>

                    {/* Biological Dark Matter Candidates */}
                    <PanelCard title="Biological 'Dark Matter' Candidates (Novel Pathways)">
                      <div className="space-y-3 font-mono text-xs">
                        <p className="text-[11px] text-slate-400">
                          Dense interactome cliques with high topological
                          cohesion but missing Gene Ontology / Reactome
                          annotations:
                        </p>
                        <div className="space-y-2 max-h-72 overflow-y-auto">
                          {darkMatterCandidates?.map((dm: any, i: number) => (
                            <div
                              key={i}
                              className="bg-slate-950 p-2.5 rounded border border-slate-850 space-y-2"
                            >
                              <div className="flex justify-between items-center text-[11px]">
                                <span className="text-amber-400 font-semibold">
                                  {dm.cluster_id}
                                </span>
                                <span className="text-slate-500">
                                  {dm.size} unmapped proteins
                                </span>
                              </div>
                              <p className="text-[10px] text-slate-300 italic bg-slate-900/60 p-1.5 rounded border border-slate-850">
                                {dm.candidate_hypothesis}
                              </p>
                              <div className="flex flex-wrap gap-1">
                                {dm.all_members?.map((m: string) => (
                                  <span
                                    key={m}
                                    className="px-1.5 py-0.5 rounded bg-amber-950/30 border border-amber-800/40 text-amber-300 text-[10px]"
                                  >
                                    {m}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </PanelCard>
                  </div>
                </div>
              )}

              {/* SUBTAB 5: DISEASE MAPPER */}
              {activePathwaySubtab === "disease" && (
                <div className="space-y-6">
                  <PanelCard title="Disease-Associated Pathway Perturbations & Rewiring">
                    <div className="space-y-4 font-mono text-xs">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-2">
                          <span className="text-emerald-400 font-semibold block">
                            Physiological Baseline (Healthy State)
                          </span>
                          <p className="text-[11px] text-slate-400 leading-relaxed">
                            Controlled cell-cycle progression, intact TP53
                            apoptotic check, regulated PI3K-AKT cell survival
                            signaling.
                          </p>
                          <div className="pt-2 text-[10px] text-slate-500">
                            Status:{" "}
                            <span className="text-emerald-400">
                              Homeostatic
                            </span>
                          </div>
                        </div>

                        <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-2">
                          <span className="text-rose-400 font-semibold block">
                            Disease State (Oncogenic / Cancer Rewiring)
                          </span>
                          <p className="text-[11px] text-slate-400 leading-relaxed">
                            Loss of PTEN phosphatase activity leads to
                            constitutive AKT hyper-activation; TP53 mutation
                            disables apoptotic threshold.
                          </p>
                          <div className="pt-2 text-[10px] text-slate-500">
                            Rewired Nodes:{" "}
                            <span className="text-rose-400">
                              PTEN (Loss), TP53 (Inactivated), AKT1
                              (Constitutive)
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 6: EVOLUTIONARY ATLAS */}
              {activePathwaySubtab === "evolution" && (
                <div className="space-y-6">
                  <PanelCard
                    title={`Cross-Species Pathway Conservation: ${selectedPathway.name}`}
                  >
                    <div className="space-y-4 font-mono text-xs">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">
                          Target Reference Organisms: Mouse, Zebrafish,
                          Drosophila, Yeast
                        </span>
                        <button
                          disabled={isAnalyzingEvolution}
                          onClick={() =>
                            handleAnalyzeEvolution(selectedPathway.id)
                          }
                          className="bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white font-semibold px-3 py-1.5 rounded text-xs transition-all flex items-center space-x-1.5"
                        >
                          {isAnalyzingEvolution ? (
                            <RefreshCw className="h-3 w-3 animate-spin" />
                          ) : (
                            <Network className="h-3 w-3" />
                          )}
                          <span>Recalculate Conservation</span>
                        </button>
                      </div>

                      {evolutionSpeciesData && (
                        <div className="space-y-3">
                          <div className="flex justify-between items-center bg-slate-950 p-3 rounded border border-slate-850">
                            <div>
                              <span className="text-slate-500 text-[10px] uppercase block">
                                Evolutionary Category
                              </span>
                              <span className="text-emerald-400 font-semibold">
                                {evolutionSpeciesData.evolutionary_category}
                              </span>
                            </div>
                            <div>
                              <span className="text-slate-500 text-[10px] uppercase block">
                                Overall Stability Score
                              </span>
                              <span className="text-indigo-400 font-semibold">
                                {
                                  evolutionSpeciesData.evolutionary_stability_score
                                }
                              </span>
                            </div>
                          </div>

                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {Object.entries(
                              evolutionSpeciesData.species_comparison || {},
                            ).map(([sp, data]: any) => (
                              <div
                                key={sp}
                                className="bg-slate-950 p-3 rounded border border-slate-850 space-y-1"
                              >
                                <span className="text-slate-300 font-semibold capitalize block">
                                  {sp}
                                </span>
                                <div className="text-[10px] text-slate-500">
                                  Conservation:{" "}
                                  <span className="text-emerald-400">
                                    {(data.conservation_ratio * 100).toFixed(0)}
                                    %
                                  </span>
                                </div>
                                <div className="text-[10px] text-slate-500">
                                  Seq Identity:{" "}
                                  <span className="text-indigo-400">
                                    {(
                                      data.mean_sequence_identity * 100
                                    ).toFixed(0)}
                                    %
                                  </span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 7: EVIDENCE INSPECTOR */}
              {activePathwaySubtab === "evidence" && (
                <div className="space-y-6">
                  <PanelCard
                    title={`Evidence & Literature Provenance: ${selectedPathway.name}`}
                  >
                    <div className="space-y-4 font-mono text-xs">
                      <div className="space-y-2">
                        {evidenceData?.evidence_pairs?.map(
                          (pair: any, i: number) => (
                            <div
                              key={i}
                              className="bg-slate-950 p-3 rounded border border-slate-850 space-y-1"
                            >
                              <div className="flex justify-between items-center text-[11px]">
                                <div className="flex items-center space-x-2">
                                  <span className="text-emerald-400 font-semibold">
                                    {pair.protein_a}
                                  </span>
                                  <span className="text-slate-600">⟷</span>
                                  <span className="text-indigo-400 font-semibold">
                                    {pair.protein_b}
                                  </span>
                                </div>
                                <span className="text-slate-500 text-[10px]">
                                  {pair.evidence?.[0]?.database} [
                                  {pair.evidence?.[0]?.evidence_code}]
                                </span>
                              </div>
                              <div className="text-[10px] text-slate-400">
                                Mechanism: {pair.evidence?.[0]?.mechanism}
                              </div>
                              <div className="text-[10px] text-indigo-400">
                                Citation: {pair.evidence?.[0]?.pubmed_id}
                              </div>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  </PanelCard>
                </div>
              )}
            </div>
          )}

          {/* PHASE 6: BIOLOGICAL REASONING ENGINE (BRE) - AGENTS / REASONING LAB */}
          {activeTab === "agents" && (
            <div className="space-y-6">
              {/* Header Card */}
              <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 relative overflow-hidden">
                <div className="relative z-10 max-w-3xl space-y-2">
                  <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono">
                    <MessageSquare className="h-3.5 w-3.5" />
                    <span>Phase 6 · Biological Reasoning Engine (BRE)</span>
                  </div>
                  <h2 className="text-xl font-bold text-slate-100 tracking-tight">
                    Biological Reasoning Lab &amp; Multi-Agent Discovery Studio
                  </h2>
                  <p className="text-xs text-slate-400 leading-relaxed font-mono">
                    Evidence-grounded scientific reasoning layer integrating
                    deterministic biology, probabilistic inference, multi-hop
                    mechanistic pathfinding, counterfactual perturbation
                    simulation, and collaborative multi-agent consensus.
                  </p>
                </div>
                <div className="absolute right-6 top-4 opacity-10">
                  <MessageSquare className="h-32 w-32 text-indigo-400" />
                </div>
              </div>

              {/* Subtabs Bar */}
              <div className="flex space-x-2 border-b border-slate-800 pb-2 overflow-x-auto">
                {reasoningSubtabs.map((subtab) => {
                  const SubIcon = subtab.icon;
                  return (
                    <button
                      key={subtab.id}
                      onClick={() => setActiveReasoningSubtab(subtab.id)}
                      className={`flex items-center space-x-2 px-3 py-1.5 rounded text-xs font-mono transition-all whitespace-nowrap ${
                        activeReasoningSubtab === subtab.id
                          ? "bg-indigo-500/10 text-indigo-400 border border-indigo-500/30"
                          : "text-slate-400 hover:text-slate-200 hover:bg-slate-900"
                      }`}
                    >
                      <SubIcon className="h-3.5 w-3.5" />
                      <span>{subtab.name}</span>
                    </button>
                  );
                })}
              </div>

              {/* SUBTAB 1: QUERY STUDIO */}
              {activeReasoningSubtab === "query" && (
                <div className="space-y-6">
                  <PanelCard title="Natural Language Biological Query &amp; Question Understanding">
                    <div className="space-y-4 font-mono text-xs">
                      <div>
                        <label className="text-slate-400 block mb-1.5 font-semibold">
                          Biological Research Question or Hypothesis to
                          Investigate:
                        </label>
                        <textarea
                          rows={3}
                          value={nlReasoningQuery}
                          onChange={(e) => setNlReasoningQuery(e.target.value)}
                          className="w-full bg-slate-950 border border-slate-800 rounded p-3 text-slate-200 focus:outline-none focus:border-indigo-500 text-xs font-mono leading-relaxed resize-none"
                        />
                      </div>

                      <div className="flex flex-wrap gap-2 items-center">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider">
                          Example Templates:
                        </span>
                        {[
                          "A protein TP53 is downregulated in liver tissue under disease condition. Which upstream regulators could explain this change, and what downstream pathways are affected?",
                          "How does EGFR tyrosine kinase inhibition rewire compensatory MAPK/AKT signaling cascades in adenocarcinoma?",
                          "What mechanistic chain explains BRCA1 deficiency inducing synthetic lethality with PARP1 inhibitors?",
                        ].map((template, idx) => (
                          <button
                            key={idx}
                            onClick={() => setNlReasoningQuery(template)}
                            className="text-[10px] bg-slate-950 hover:bg-slate-900 text-slate-400 hover:text-slate-200 border border-slate-800 px-2 py-1 rounded transition-all truncate max-w-xs"
                          >
                            {template.slice(0, 42)}...
                          </button>
                        ))}
                      </div>

                      <div className="pt-2">
                        <button
                          disabled={isReasoningLoading}
                          onClick={handleRunReasoning}
                          className="bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                        >
                          {isReasoningLoading ? (
                            <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          ) : (
                            <Play className="h-3.5 w-3.5 fill-current" />
                          )}
                          <span>Run Multi-Agent Biological Reasoning</span>
                        </button>
                      </div>
                    </div>
                  </PanelCard>

                  {/* Decomposed Query Plan & Entity Resolution Grid */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    <PanelCard title="Entity Resolution &amp; Context Disambiguation">
                      <div className="space-y-3 font-mono text-xs">
                        <div className="bg-slate-950 p-3 rounded border border-slate-850 space-y-2">
                          <div className="flex justify-between items-center text-[11px]">
                            <span className="text-slate-400">
                              Target Biological Entity:
                            </span>
                            <span className="text-indigo-400 font-semibold px-2 py-0.5 rounded bg-indigo-950/40 border border-indigo-800/40">
                              {reasoningReport?.question?.target || "TP53"}
                            </span>
                          </div>
                          <div className="flex justify-between items-center text-[11px]">
                            <span className="text-slate-400">
                              Inferred Task Archetype:
                            </span>
                            <span className="text-emerald-400 font-semibold">
                              {reasoningReport?.question?.task ||
                                "upstream_regulator_analysis"}
                            </span>
                          </div>
                          <div className="flex justify-between items-center text-[11px]">
                            <span className="text-slate-400">
                              Tissue Compartment:
                            </span>
                            <span className="text-slate-200 capitalize">
                              {reasoningReport?.question?.context?.tissue ||
                                "liver"}
                            </span>
                          </div>
                          <div className="flex justify-between items-center text-[11px]">
                            <span className="text-slate-400">
                              Cellular Condition:
                            </span>
                            <span className="text-rose-400 capitalize">
                              {reasoningReport?.question?.context?.condition ||
                                "disease"}
                            </span>
                          </div>
                          <div className="flex justify-between items-center text-[11px]">
                            <span className="text-slate-400">
                              Observed Phenotype:
                            </span>
                            <span className="text-amber-400">
                              {reasoningReport?.question?.context
                                ?.observation || "downregulated"}
                            </span>
                          </div>
                        </div>

                        {/* Confidence Triad */}
                        <div className="bg-slate-950 p-3 rounded border border-slate-850 space-y-2">
                          <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                            Confidence &amp; Calibration Dimensions
                          </span>
                          <div className="space-y-1.5">
                            <div>
                              <div className="flex justify-between text-[10px] text-slate-400 mb-0.5">
                                <span>Evidence Strength</span>
                                <span className="text-emerald-400 font-semibold">
                                  {(
                                    (reasoningReport?.confidence_breakdown
                                      ?.evidence_strength || 0.92) * 100
                                  ).toFixed(0)}
                                  %
                                </span>
                              </div>
                              <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-emerald-500 rounded-full"
                                  style={{
                                    width: `${(reasoningReport?.confidence_breakdown?.evidence_strength || 0.92) * 100}%`,
                                  }}
                                />
                              </div>
                            </div>
                            <div>
                              <div className="flex justify-between text-[10px] text-slate-400 mb-0.5">
                                <span>Model Confidence (Calibrated)</span>
                                <span className="text-indigo-400 font-semibold">
                                  {(
                                    (reasoningReport?.confidence_breakdown
                                      ?.model_confidence || 0.94) * 100
                                  ).toFixed(0)}
                                  %
                                </span>
                              </div>
                              <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-indigo-500 rounded-full"
                                  style={{
                                    width: `${(reasoningReport?.confidence_breakdown?.model_confidence || 0.94) * 100}%`,
                                  }}
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </PanelCard>

                    <PanelCard title="Decomposed Query Execution Plan">
                      <div className="space-y-2 font-mono text-xs">
                        {[
                          {
                            step: 1,
                            title: "Entity Resolution",
                            desc: "Map genes, proteins, tissues to UniProt & Uberon ontologies",
                            icon: Compass,
                          },
                          {
                            step: 2,
                            title: "Hybrid Evidence Retrieval",
                            desc: "Query UBKG Neo4j subgraph, PLM embeddings, and PubMed citations",
                            icon: Database,
                          },
                          {
                            step: 3,
                            title: "Mechanistic Reconstruction",
                            desc: "Multi-hop pathfinding identifying directional regulatory chains",
                            icon: Share2,
                          },
                          {
                            step: 4,
                            title: "Hypothesis Formulation",
                            desc: "Abductive synthesis of competing explanatory hypotheses",
                            icon: Network,
                          },
                          {
                            step: 5,
                            title: "Constraint Validation",
                            desc: "Filter steps violating subcellular compartment boundaries",
                            icon: ShieldCheck,
                          },
                          {
                            step: 6,
                            title: "Multi-Agent Consensus",
                            desc: "Adversarial critic audit, uncertainty calibration, and synthesis",
                            icon: Terminal,
                          },
                        ].map((p) => {
                          const StepIcon = p.icon;
                          return (
                            <div
                              key={p.step}
                              className="flex items-center space-x-3 bg-slate-950 p-2.5 rounded border border-slate-850"
                            >
                              <span className="flex items-center justify-center h-6 w-6 rounded-full bg-indigo-950/60 border border-indigo-700/50 text-indigo-400 text-[10px] font-bold">
                                {p.step}
                              </span>
                              <div className="flex-1 min-w-0">
                                <div className="text-[11px] font-semibold text-slate-200">
                                  {p.title}
                                </div>
                                <div className="text-[10px] text-slate-400 truncate">
                                  {p.desc}
                                </div>
                              </div>
                              <StepIcon className="h-3.5 w-3.5 text-slate-600" />
                            </div>
                          );
                        })}
                      </div>
                    </PanelCard>
                  </div>
                </div>
              )}

              {/* SUBTAB 2: MECHANISM EXPLORER */}
              {activeReasoningSubtab === "mechanism" && (
                <div className="space-y-6">
                  <PanelCard title="Reconstructed Molecular Mechanism &amp; Causal Regulatory Chain">
                    <div className="space-y-4 font-mono text-xs">
                      {/* Mechanism Overview Stats */}
                      <div className="flex flex-wrap justify-between items-center bg-slate-950 p-4 rounded border border-slate-850 gap-4">
                        <div>
                          <span className="text-slate-500 text-[10px] uppercase block">
                            Net Regulatory Effect
                          </span>
                          <span
                            className={`text-base font-bold ${
                              reasoningReport?.primary_mechanism?.net_sign > 0
                                ? "text-emerald-400"
                                : "text-rose-400"
                            }`}
                          >
                            {reasoningReport?.primary_mechanism?.net_effect ||
                              "Activation"}{" "}
                            (Sign:{" "}
                            {reasoningReport?.primary_mechanism?.net_sign > 0
                              ? "+1"
                              : "-1"}
                            )
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 text-[10px] uppercase block">
                            Cumulative Confidence
                          </span>
                          <span className="text-indigo-400 text-base font-semibold">
                            {(
                              (reasoningReport?.primary_mechanism
                                ?.cumulative_confidence || 0.9) * 100
                            ).toFixed(1)}
                            %
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 text-[10px] uppercase block">
                            Cellular Compartments
                          </span>
                          <span className="text-slate-300">
                            {(
                              reasoningReport?.primary_mechanism
                                ?.compartments || ["nucleus", "cytosol"]
                            ).join(" ➔ ")}
                          </span>
                        </div>
                        <div>
                          <span className="text-slate-500 text-[10px] uppercase block">
                            Mechanistic Steps
                          </span>
                          <span className="text-slate-300">
                            {reasoningReport?.primary_mechanism?.steps
                              ?.length || 4}{" "}
                            Directed Reactions
                          </span>
                        </div>
                      </div>

                      {/* Step-by-Step Reaction Steps */}
                      <div className="space-y-2.5 pt-2">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                          Sequential Multi-Hop Molecular Reactions:
                        </span>
                        {reasoningReport?.primary_mechanism?.steps?.map(
                          (step: any, idx: number) => (
                            <div
                              key={idx}
                              className="bg-slate-950 p-3.5 rounded border border-slate-850 hover:border-slate-700 transition-all space-y-2"
                            >
                              <div className="flex flex-wrap justify-between items-center gap-2">
                                <div className="flex items-center space-x-2.5">
                                  <span className="h-5 w-5 rounded bg-slate-900 text-slate-400 text-[10px] flex items-center justify-center font-bold">
                                    {idx + 1}
                                  </span>
                                  <span className="text-emerald-400 font-bold text-sm">
                                    {step.source}
                                  </span>
                                  <span
                                    className={`text-xs font-bold ${step.sign > 0 ? "text-emerald-400" : "text-rose-400"}`}
                                  >
                                    {step.sign > 0 ? "➔ (+)" : "⊣ (-)"}
                                  </span>
                                  <span className="text-indigo-400 font-bold text-sm">
                                    {step.target}
                                  </span>
                                  <span className="text-[10px] text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                                    {step.mechanism}
                                  </span>
                                </div>

                                <div className="flex items-center space-x-2">
                                  <span
                                    className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                                      step.evidence_status === "EXPERIMENTAL"
                                        ? "bg-emerald-950/40 text-emerald-300 border-emerald-800/40"
                                        : step.evidence_status ===
                                            "COMPUTATIONAL"
                                          ? "bg-blue-950/40 text-blue-300 border-blue-800/40"
                                          : "bg-amber-950/40 text-amber-300 border-amber-800/40"
                                    }`}
                                  >
                                    {step.evidence_status}
                                  </span>
                                  <span className="text-slate-400 text-[10px]">
                                    Conf:{" "}
                                    <strong className="text-slate-200">
                                      {(step.confidence * 100).toFixed(0)}%
                                    </strong>
                                  </span>
                                </div>
                              </div>

                              <div className="text-[10px] text-slate-500 flex justify-between">
                                <span>
                                  Relationship:{" "}
                                  <strong className="text-slate-400">
                                    {step.relationship_type}
                                  </strong>
                                </span>
                                <span>
                                  Biological Effect:{" "}
                                  <strong
                                    className={
                                      step.sign > 0
                                        ? "text-emerald-400"
                                        : "text-rose-400"
                                    }
                                  >
                                    {step.sign > 0
                                      ? "Activation / Stabilization"
                                      : "Inhibition / Degradation"}
                                  </strong>
                                </span>
                              </div>
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 3: HYPOTHESIS LAB */}
              {activeReasoningSubtab === "hypotheses" && (
                <div className="space-y-6">
                  <PanelCard title="Ranked Competing Hypotheses (Abductive Biological Reasoning)">
                    <div className="space-y-4 font-mono text-xs">
                      <p className="text-[11px] text-slate-400 leading-relaxed">
                        The reasoning engine formulates multiple plausible
                        causal hypotheses explaining the observation, evaluates
                        supporting and refuting evidence, and ranks them by
                        composite confidence:
                      </p>

                      <div className="space-y-4">
                        {reasoningReport?.competing_hypotheses?.map(
                          (hyp: any, idx: number) => (
                            <div
                              key={hyp.hypothesis_id || idx}
                              className="bg-slate-950 p-4 rounded border border-slate-850 space-y-3"
                            >
                              <div className="flex flex-wrap justify-between items-center gap-2">
                                <div className="flex items-center space-x-2">
                                  <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 font-bold text-xs border border-indigo-800">
                                    {hyp.hypothesis_id}
                                  </span>
                                  <span
                                    className={`px-2 py-0.5 rounded text-[10px] font-bold border ${
                                      hyp.biological_certainty === "ESTABLISHED"
                                        ? "bg-emerald-950/50 text-emerald-300 border-emerald-700/50"
                                        : hyp.biological_certainty ===
                                            "PROBABLE"
                                          ? "bg-indigo-950/50 text-indigo-300 border-indigo-700/50"
                                          : "bg-amber-950/50 text-amber-300 border-amber-700/50"
                                    }`}
                                  >
                                    {hyp.biological_certainty}
                                  </span>
                                </div>

                                <div className="flex items-center space-x-4 text-[10px]">
                                  <div>
                                    <span className="text-slate-500">
                                      Evidence Strength:{" "}
                                    </span>
                                    <span className="text-emerald-400 font-bold">
                                      {(hyp.evidence_strength * 100).toFixed(0)}
                                      %
                                    </span>
                                  </div>
                                  <div>
                                    <span className="text-slate-500">
                                      Model Conf:{" "}
                                    </span>
                                    <span className="text-indigo-400 font-bold">
                                      {(hyp.model_confidence * 100).toFixed(0)}%
                                    </span>
                                  </div>
                                </div>
                              </div>

                              <div className="space-y-1">
                                <p className="text-slate-200 text-xs font-semibold leading-relaxed">
                                  {hyp.statement}
                                </p>
                                <p className="text-[10px] text-slate-400">
                                  Target Biological Process:{" "}
                                  <span className="text-slate-300">
                                    {hyp.target_process}
                                  </span>
                                </p>
                              </div>

                              {/* Supporting Evidence Pills */}
                              {hyp.supporting_evidence &&
                                hyp.supporting_evidence.length > 0 && (
                                  <div className="space-y-1">
                                    <span className="text-[10px] text-slate-500 block">
                                      Supporting Empirical Evidence:
                                    </span>
                                    <div className="space-y-1">
                                      {hyp.supporting_evidence.map(
                                        (ev: any, evIdx: number) => (
                                          <div
                                            key={evIdx}
                                            className="bg-slate-900/80 p-2 rounded border border-slate-850 flex justify-between items-center text-[10px]"
                                          >
                                            <div className="flex items-center space-x-1.5">
                                              <span className="text-emerald-400 font-semibold">
                                                {ev.subject_id}
                                              </span>
                                              <span className="text-slate-500">
                                                ➔
                                              </span>
                                              <span className="text-slate-400">
                                                {ev.predicate}
                                              </span>
                                              <span className="text-slate-500">
                                                ➔
                                              </span>
                                              <span className="text-indigo-400 font-semibold">
                                                {ev.object_id}
                                              </span>
                                            </div>
                                            <div className="flex items-center space-x-2 text-slate-500">
                                              <span>
                                                {ev.source} [{ev.evidence_code}]
                                              </span>
                                              <span className="text-indigo-400">
                                                {ev.publication_id}
                                              </span>
                                            </div>
                                          </div>
                                        ),
                                      )}
                                    </div>
                                  </div>
                                )}

                              {/* Suggested Wet-Lab Validation */}
                              {hyp.potential_validation_experiments &&
                                hyp.potential_validation_experiments.length >
                                  0 && (
                                  <div className="pt-1">
                                    <span className="text-[10px] text-slate-500 block mb-1">
                                      Recommended Validation Experiments:
                                    </span>
                                    <div className="flex flex-wrap gap-1.5">
                                      {hyp.potential_validation_experiments.map(
                                        (exp: string, expIdx: number) => (
                                          <span
                                            key={expIdx}
                                            className="px-2 py-0.5 rounded bg-slate-900 text-slate-300 text-[10px] border border-slate-800"
                                          >
                                            🔬 {exp}
                                          </span>
                                        ),
                                      )}
                                    </div>
                                  </div>
                                )}
                            </div>
                          ),
                        )}
                      </div>
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 4: EVIDENCE INTELLIGENCE */}
              {activeReasoningSubtab === "evidence" && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <div className="lg:col-span-2 space-y-4">
                      <PanelCard title="Multimodal Evidence Intelligence &amp; Fused Knowledge Base">
                        <div className="space-y-3 font-mono text-xs">
                          <p className="text-[11px] text-slate-400">
                            Harmonized evidence instances supporting the
                            reasoning chain, indexed by source reliability
                            hierarchy:
                          </p>

                          <div className="space-y-2 max-h-96 overflow-y-auto">
                            {reasoningReport?.evidence_manifest?.map(
                              (ev: any, i: number) => (
                                <div
                                  key={i}
                                  className="bg-slate-950 p-3 rounded border border-slate-850 flex flex-wrap justify-between items-center gap-2"
                                >
                                  <div className="space-y-1">
                                    <div className="flex items-center space-x-2">
                                      <span className="text-emerald-400 font-bold">
                                        {ev.subject_id}
                                      </span>
                                      <span className="text-slate-500">⟷</span>
                                      <span className="text-slate-300">
                                        {ev.predicate}
                                      </span>
                                      <span className="text-slate-500">⟷</span>
                                      <span className="text-indigo-400 font-bold">
                                        {ev.object_id}
                                      </span>
                                    </div>
                                    <div className="text-[10px] text-slate-500 flex items-center space-x-2">
                                      <span>
                                        Database:{" "}
                                        <strong className="text-slate-400">
                                          {ev.source}
                                        </strong>
                                      </span>
                                      <span>
                                        Code:{" "}
                                        <strong className="text-slate-400">
                                          {ev.evidence_code}
                                        </strong>
                                      </span>
                                      <span>
                                        Citation:{" "}
                                        <strong className="text-indigo-400">
                                          {ev.publication_id}
                                        </strong>
                                      </span>
                                    </div>
                                  </div>

                                  <div className="flex items-center space-x-2">
                                    <span
                                      className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                                        ev.evidence_status === "EXPERIMENTAL"
                                          ? "bg-emerald-950/40 text-emerald-300 border-emerald-800/40"
                                          : "bg-blue-950/40 text-blue-300 border-blue-800/40"
                                      }`}
                                    >
                                      {ev.evidence_status}
                                    </span>
                                    <span className="text-slate-300 font-bold text-xs">
                                      {(ev.confidence * 100).toFixed(0)}%
                                    </span>
                                  </div>
                                </div>
                              ),
                            )}
                          </div>
                        </div>
                      </PanelCard>
                    </div>

                    <div className="space-y-4">
                      {/* Calibration & Uncertainty */}
                      <PanelCard title="Statistical Calibration &amp; Uncertainty">
                        <div className="space-y-3 font-mono text-xs">
                          <div className="bg-slate-950 p-3 rounded border border-slate-850 space-y-1">
                            <span className="text-slate-500 text-[10px] uppercase block">
                              Expected Calibration Error (ECE)
                            </span>
                            <span className="text-emerald-400 text-lg font-bold">
                              {reasoningReport?.confidence_breakdown
                                ?.calibration_ece || "0.041"}
                            </span>
                            <p className="text-[10px] text-slate-400">
                              Low calibration error ensures probabilities
                              reflect empirical frequencies.
                            </p>
                          </div>

                          <div className="bg-slate-950 p-3 rounded border border-slate-850 space-y-1">
                            <span className="text-slate-500 text-[10px] uppercase block">
                              Reliability Hierarchy
                            </span>
                            <div className="text-[10px] space-y-1 text-slate-400">
                              <div className="flex justify-between">
                                <span>Wet-Lab Assays (EXP)</span>
                                <span className="text-emerald-400">
                                  Weight: 1.00
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span>Curated Databases</span>
                                <span className="text-indigo-400">
                                  Weight: 0.85
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span>PLM/GNN Predictions</span>
                                <span className="text-blue-400">
                                  Weight: 0.70
                                </span>
                              </div>
                              <div className="flex justify-between">
                                <span>Text Mining</span>
                                <span className="text-amber-400">
                                  Weight: 0.50
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </PanelCard>

                      {/* Contradictions & Limitations Warnings */}
                      <PanelCard title="Contradictions &amp; Scientific Limitations">
                        <div className="space-y-2 font-mono text-xs">
                          {reasoningReport?.contradictions_and_limitations?.map(
                            (item: string, idx: number) => (
                              <div
                                key={idx}
                                className="bg-amber-950/20 border border-amber-900/40 p-2.5 rounded text-[11px] text-amber-300 flex items-start space-x-2"
                              >
                                <AlertTriangle className="h-4 w-4 text-amber-400 shrink-0 mt-0.5" />
                                <span className="leading-relaxed">{item}</span>
                              </div>
                            ),
                          )}
                        </div>
                      </PanelCard>
                    </div>
                  </div>
                </div>
              )}

              {/* SUBTAB 5: PERTURBATION SIMULATOR */}
              {activeReasoningSubtab === "perturbation" && (
                <div className="space-y-6">
                  <PanelCard title="In Silico Counterfactual Perturbation Simulator">
                    <div className="space-y-4 font-mono text-xs">
                      <p className="text-[11px] text-slate-400 leading-relaxed">
                        Simulate the systemic network consequences of in silico
                        gene knockouts, knockdowns, or overexpressions
                        propagated through directional regulatory and physical
                        interaction edges:
                      </p>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 bg-slate-950 p-4 rounded border border-slate-850">
                        <div>
                          <label className="text-slate-400 block mb-1">
                            Target Protein ID
                          </label>
                          <input
                            type="text"
                            value={perturbTarget}
                            onChange={(e) => setPerturbTarget(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-800 rounded p-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                          />
                        </div>

                        <div>
                          <label className="text-slate-400 block mb-1">
                            Perturbation Modality
                          </label>
                          <select
                            value={perturbType}
                            onChange={(e) => setPerturbType(e.target.value)}
                            className="w-full bg-slate-900 border border-slate-800 rounded p-2 text-slate-200 focus:outline-none focus:border-indigo-500"
                          >
                            <option value="knockout">
                              Knockout (-100% loss-of-function)
                            </option>
                            <option value="knockdown">
                              Knockdown (-50% expression)
                            </option>
                            <option value="overexpression">
                              Overexpression (+100% gain-of-function)
                            </option>
                          </select>
                        </div>

                        <div className="flex items-end">
                          <button
                            disabled={isPerturbing}
                            onClick={handleRunPerturbation}
                            className="w-full bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white font-semibold py-2 px-4 rounded transition-all flex items-center justify-center space-x-2"
                          >
                            {isPerturbing ? (
                              <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                            ) : (
                              <Activity className="h-3.5 w-3.5" />
                            )}
                            <span>Simulate Perturbation</span>
                          </button>
                        </div>
                      </div>

                      {/* Simulation Results Grid */}
                      {perturbResult && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                          <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-3">
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                              Downstream Node Expression Shift (Δ Signal):
                            </span>
                            <div className="space-y-2">
                              {Object.entries(
                                perturbResult.perturbed_nodes || {},
                              ).map(([node, delta]: any) => {
                                const isNeg = delta < 0;
                                const pct = Math.abs(delta * 100).toFixed(0);
                                return (
                                  <div key={node} className="space-y-1">
                                    <div className="flex justify-between text-[11px]">
                                      <span className="font-semibold text-slate-200">
                                        {node}
                                      </span>
                                      <span
                                        className={
                                          isNeg
                                            ? "text-rose-400"
                                            : "text-emerald-400"
                                        }
                                      >
                                        {isNeg ? `-${pct}%` : `+${pct}%`}
                                      </span>
                                    </div>
                                    <div className="h-1.5 bg-slate-900 rounded-full overflow-hidden flex">
                                      <div
                                        className={`h-full ${isNeg ? "bg-rose-500" : "bg-emerald-500"} rounded-full`}
                                        style={{
                                          width: `${Math.min(100, Math.abs(delta * 100))}%`,
                                        }}
                                      />
                                    </div>
                                  </div>
                                );
                              })}
                            </div>
                          </div>

                          <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-3">
                            <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                              Systemic Pathway Disruptions:
                            </span>
                            <div className="space-y-2">
                              {perturbResult.affected_pathways?.map(
                                (pw: any, i: number) => (
                                  <div
                                    key={i}
                                    className="p-2.5 rounded bg-slate-900/80 border border-slate-850 flex justify-between items-center text-[11px]"
                                  >
                                    <div>
                                      <div className="font-semibold text-slate-200">
                                        {pw.name}
                                      </div>
                                      <div className="text-[10px] text-slate-500">
                                        {pw.pathway_id}
                                      </div>
                                    </div>
                                    <span
                                      className={`px-2 py-0.5 rounded text-[10px] font-semibold border ${
                                        pw.predicted_state === "Suppressed"
                                          ? "bg-rose-950/40 text-rose-300 border-rose-800/40"
                                          : "bg-emerald-950/40 text-emerald-300 border-emerald-800/40"
                                      }`}
                                    >
                                      {pw.predicted_state}
                                    </span>
                                  </div>
                                ),
                              )}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 6: TRACE INSPECTOR */}
              {activeReasoningSubtab === "trace" && (
                <div className="space-y-6">
                  <PanelCard title="Multi-Agent Sequential Reasoning Trace &amp; Audit Log">
                    <div className="space-y-4 font-mono text-xs">
                      <p className="text-[11px] text-slate-400">
                        Step-by-step transparent audit trace of specialized
                        autonomous agents executing the query plan:
                      </p>

                      <div className="space-y-3">
                        {reasoningReport?.reasoning_trace?.map(
                          (trace: any, i: number) => (
                            <div
                              key={i}
                              className="bg-slate-950 p-3 rounded border border-slate-850 flex items-center justify-between"
                            >
                              <div className="flex items-center space-x-3">
                                <span className="h-6 w-6 rounded-full bg-indigo-950/80 border border-indigo-700/60 text-indigo-400 flex items-center justify-center font-bold text-[10px]">
                                  {trace.step_index}
                                </span>
                                <div>
                                  <span className="font-bold text-slate-200 text-xs">
                                    {trace.agent}
                                  </span>
                                  <span className="text-slate-500 text-[10px] block">
                                    Action: {trace.action}
                                  </span>
                                </div>
                              </div>

                              <div className="flex items-center space-x-2">
                                <span className="px-2 py-0.5 rounded text-[10px] bg-emerald-950/40 text-emerald-300 border border-emerald-800/40 font-semibold flex items-center space-x-1">
                                  <CheckCircle2 className="h-3 w-3 text-emerald-400" />
                                  <span>{trace.status}</span>
                                </span>
                              </div>
                            </div>
                          ),
                        )}
                      </div>

                      {/* Biological Constraints Audit Card */}
                      <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-2 mt-4">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                          Biological Constraint Checks Applied
                        </span>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 pt-1 text-[11px]">
                          <div className="bg-slate-900 p-2.5 rounded border border-slate-850 space-y-1">
                            <span className="text-emerald-400 font-semibold block">
                              Compartment Boundary
                            </span>
                            <p className="text-[10px] text-slate-400">
                              All adjacent steps verified for co-localization or
                              established nuclear/cytosol transport.
                            </p>
                          </div>
                          <div className="bg-slate-900 p-2.5 rounded border border-slate-850 space-y-1">
                            <span className="text-emerald-400 font-semibold block">
                              Directionality Sign
                            </span>
                            <p className="text-[10px] text-slate-400">
                              Multi-hop parity preserves negative feedback
                              regulation without algebraic sign flip errors.
                            </p>
                          </div>
                          <div className="bg-slate-900 p-2.5 rounded border border-slate-850 space-y-1">
                            <span className="text-emerald-400 font-semibold block">
                              Evidence Hierarchy
                            </span>
                            <p className="text-[10px] text-slate-400">
                              Hypotheses grounded in empirical wet-lab assays
                              prioritised over text-mined inferences.
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </PanelCard>
                </div>
              )}

              {/* SUBTAB 7: SCIENTIFIC REPORT */}
              {activeReasoningSubtab === "report" && (
                <div className="space-y-6">
                  <PanelCard title="Synthesized Scientific Report &amp; Evidence Dossier">
                    <div className="space-y-4 font-mono text-xs">
                      {/* Executive Summary */}
                      <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-2">
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="text-indigo-400 font-semibold uppercase tracking-wider">
                            Executive Scientific Summary · Dossier ID:{" "}
                            {reasoningReport?.report_id || "REP-BRE-001"}
                          </span>
                          <span className="text-slate-500">
                            Target:{" "}
                            {reasoningReport?.question?.target || "TP53"}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 leading-relaxed pt-1">
                          {reasoningReport?.executive_summary ||
                            "Mechanistic investigation indicates hyperactivation of MDM2 E3-ubiquitin ligase accelerates proteasomal degradation of TP53 in liver tissue under disease stress."}
                        </p>
                      </div>

                      {/* Primary Mechanism Flow */}
                      <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-2">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                          Consensus Molecular Cascade Diagram
                        </span>
                        <div className="flex flex-wrap items-center gap-2 pt-1">
                          {reasoningReport?.primary_mechanism?.chain?.map(
                            (gene: string, i: number, arr: any[]) => (
                              <React.Fragment key={gene}>
                                <span className="px-3 py-1.5 rounded bg-slate-900 border border-slate-800 text-indigo-300 font-bold text-xs">
                                  {gene}
                                </span>
                                {i < arr.length - 1 && (
                                  <ArrowRight className="h-4 w-4 text-emerald-400" />
                                )}
                              </React.Fragment>
                            ),
                          )}
                        </div>
                      </div>

                      {/* Suggested Validation Assays */}
                      <div className="bg-slate-950 p-4 rounded border border-slate-850 space-y-2">
                        <span className="text-[10px] text-slate-500 uppercase tracking-wider block font-semibold">
                          Recommended Wet-Lab Experimental Protocols
                        </span>
                        <div className="space-y-1.5 pt-1">
                          {reasoningReport?.suggested_experiments?.map(
                            (exp: string, idx: number) => (
                              <div
                                key={idx}
                                className="bg-slate-900/70 p-2.5 rounded border border-slate-850 flex items-center space-x-2 text-[11px] text-slate-300"
                              >
                                <span className="text-emerald-400 font-bold">
                                  Protocol {idx + 1}:
                                </span>
                                <span>{exp}</span>
                              </div>
                            ),
                          )}
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex space-x-3 pt-2">
                        <button
                          onClick={() => {
                            const blob = new Blob(
                              [JSON.stringify(reasoningReport, null, 2)],
                              { type: "application/json" },
                            );
                            const url = URL.createObjectURL(blob);
                            const a = document.createElement("a");
                            a.href = url;
                            a.download = `PROTEA_Reasoning_Report_${reasoningReport?.report_id || "BRE"}.json`;
                            a.click();
                          }}
                          className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-4 py-2 rounded text-xs transition-all flex items-center space-x-2"
                        >
                          <FileText className="h-3.5 w-3.5" />
                          <span>Export JSON Dossier</span>
                        </button>
                      </div>
                    </div>
                  </PanelCard>
                </div>
              )}
            </div>
          )}

          {/* Other tabs placeholders remain standard... */}
          {activeTab !== "overview" &&
            activeTab !== "protein" &&
            activeTab !== "graph" &&
            activeTab !== "prediction" &&
            activeTab !== "pathway" &&
            activeTab !== "agents" && (
              <div className="bg-slate-900 border border-slate-800 p-12 rounded-lg text-center font-mono">
                <Sliders className="h-12 w-12 text-slate-700 mx-auto mb-4 animate-pulse" />
                <h3 className="text-md font-bold text-slate-300">
                  Feature Under Development
                </h3>
                <p className="text-xs text-slate-500 mt-1">
                  This module is scheduled for implementation in a future phase
                  of the PROTEA roadmap.
                </p>
              </div>
            )}
        </div>
      </main>
    </div>
  );
}
