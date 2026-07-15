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

  // Auto-fetch benchmarks on mount
  useEffect(() => {
    handleFetchBenchmarks();
  }, []);

  const tabs = [
    { id: "overview", name: "Overview", icon: Compass },
    { id: "protein", name: "Protein Universe", icon: Dna },
    { id: "graph", name: "Interactome Navigator", icon: Database },
    { id: "prediction", name: "Interaction Prediction", icon: GitBranch },
    { id: "twins", name: "Digital Twins", icon: Layers },
    { id: "simulation", name: "Cellular Simulation", icon: Activity },
    { id: "agents", name: "AI Scientist Chat", icon: MessageSquare },
    { id: "pathway", name: "Pathway Designer", icon: Share2 },
    { id: "mutation", name: "Mutation Sandbox", icon: Sliders },
    { id: "drug", name: "Drug Lab", icon: FlaskConical },
    { id: "experiments", name: "Experiments", icon: GitPullRequest },
    { id: "reports", name: "Reports", icon: FileText },
    { id: "settings", name: "Settings", icon: SettingsIcon },
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

          {/* Other tabs placeholders remain standard... */}
          {activeTab !== "overview" &&
            activeTab !== "protein" &&
            activeTab !== "graph" &&
            activeTab !== "prediction" && (
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
