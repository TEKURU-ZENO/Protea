"use client";

import React, { useState, useEffect } from 'react';
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
  Info
} from 'lucide-react';
import axios from 'axios';
import { PanelCard } from '@protea/ui';

export default function BiologicalDiscoveryStudio() {
  const [activeTab, setActiveTab] = useState('overview');
  const [systemStatus, setSystemStatus] = useState({
    status: 'healthy',
    uptime: 0,
    services: {
      postgres: 'loading',
      neo4j: 'loading',
      redis: 'loading',
      qdrant: 'loading',
      minio: 'loading',
      mlflow: 'loading'
    }
  });

  const [logs, setLogs] = useState<string[]>([
    "[SYSTEM] PROTEA platform bootstrapping...",
    "[SYSTEM] Environment loaded: development",
    "[SYSTEM] Connecting to databases..."
  ]);

  // Protein Workspace State
  const [sequence, setSequence] = useState("MNGTEGPNFYVPFSNKTGVVRSPFEAPQYYLAEPWQFSMLAAYMFLLIMLGFPINFLTLYVTVQHKKLRTPLNYILLNLAVADLFMVFGGFTTTLYTSLHGYFVFGPTGCNLEGFFATLGGEIALWSLVVLAIERWVVVCKPMSNFRFGENHAIMGVAFTWVMALACAAPPLVGWSRYIPEGMQCSCGIDYYTPHEETNNESFVIYMFVVHFIIPLIVIFFCYGQLVFTVKEAAAQQQESATTQKAEKEVTRMVIIMVIAFLICWLPYAGVAFYIFTHQGSDFGPIFMTIPAFFAKTSAVYNPVIYIMMNKQFRNCMVTTLCCGKNPLGDDEASTTVSKTETSQVAPA");
  const [uniprotId, setUniprotId] = useState("OPSD_HUMAN");
  const [proteinName, setProteinName] = useState("Rhodopsin");
  const [selectedModel, setSelectedModel] = useState("esm2");
  const [pdbFileContent, setPdbFileContent] = useState("");
  
  const [embeddingResult, setEmbeddingResult] = useState<any>(null);
  const [searchResults, setSearchResults] = useState<any>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  


  const [apiOnline, setApiOnline] = useState(false);

  // Check API health
  useEffect(() => {
    const checkApi = async () => {
      try {
        const res = await axios.get("http://localhost:8000/readiness");
        if (res.data && res.data.status === "ready") {
          setApiOnline(true);
          setSystemStatus(prev => ({
            ...prev,
            services: {
              postgres: res.data.services.postgres ? 'online' : 'offline',
              neo4j: res.data.services.neo4j ? 'online' : 'offline',
              redis: res.data.services.redis ? 'online' : 'offline',
              qdrant: res.data.services.qdrant ? 'online' : 'offline',
              minio: res.data.services.minio ? 'online' : 'offline',
              mlflow: 'online'
            }
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
      setSystemStatus(prev => ({
        ...prev,
        uptime: prev.uptime + 1,
        services: apiOnline ? prev.services : {
          postgres: prev.uptime > 2 ? 'online' : 'loading',
          neo4j: prev.uptime > 3 ? 'online' : 'loading',
          redis: prev.uptime > 1 ? 'online' : 'loading',
          qdrant: prev.uptime > 4 ? 'online' : 'loading',
          minio: prev.uptime > 2 ? 'online' : 'loading',
          mlflow: prev.uptime > 3 ? 'online' : 'loading'
        }
      }));
    }, 1000);

    return () => clearInterval(timer);
  }, [apiOnline]);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  // Run Embedding Ingestion
  const handleInjest = async () => {
    setIsProcessing(true);
    addLog(`Initiating sequence embedding ingestion for: ${uniprotId} [Model: ${selectedModel}]`);
    
    try {
      const res = await axios.post("http://localhost:8000/api/v1/protein/embed", {
        sequence: sequence,
        uniprot_id: uniprotId,
        name: proteinName,
        model_name: selectedModel,
        pdb_content: pdbFileContent || null
      });
      
      setEmbeddingResult(res.data);
      addLog(`Embedding generation completed. Dimension: ${res.data.embedding_dimension}. Cache Status: ${res.data.cache_status.toUpperCase()}.`);
    } catch (err: any) {
      addLog(`Error generating embedding: ${err.message}. Running fallback mock calculations...`);
      // Fallback Mock data
      setTimeout(() => {
        setEmbeddingResult({
          uniprot_id: uniprotId,
          name: proteinName,
          sequence_length: sequence.length,
          model_used: selectedModel,
          embedding_dimension: selectedModel === 'esm2' ? 1280 : 1024,
          cache_status: "miss",
          fused_status: pdbFileContent ? "cross_attention_fused" : "none",
          pooled_vector_preview: [0.124, -0.412, 0.941, -0.015, 0.518],
          structure_summary: pdbFileContent ? { num_residues: sequence.length, secondary_structure_summary: ["H", "H", "C", "E"] } : {}
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
      const res = await axios.post("http://localhost:8000/api/v1/protein/search", {
        sequence: sequence,
        limit: 5,
        collection: `proteins_${selectedModel}`
      });
      
      setSearchResults(res.data.results);
      addLog(`Nearest neighbor search completed. Found ${res.data.results.length} neighbors.`);
    } catch (err: any) {
      addLog(`Neighbor search failed: ${err.message}. Generating mock comparison neighbors...`);
      setTimeout(() => {
        setSearchResults([
          { id: "OPSD_BOVIN", score: 0.985, payload: { name: "Rhodopsin (Bovine)", length: 348, organism: "Bos taurus", gene: "RHO" } },
          { id: "OPSD_MOUSE", score: 0.942, payload: { name: "Rhodopsin (Mouse)", length: 348, organism: "Mus musculus", gene: "Rho" } },
          { id: "OPN4_HUMAN", score: 0.712, payload: { name: "Melanopsin", length: 478, organism: "Homo sapiens", gene: "OPN4" } },
        ]);
      }, 1000);
    } finally {
      setIsSearching(false);
    }
  };

  const tabs = [
    { id: 'overview', name: 'Overview', icon: Compass },
    { id: 'protein', name: 'Protein Universe', icon: Dna },
    { id: 'graph', name: 'Knowledge Graph', icon: Database },
    { id: 'prediction', name: 'Interaction Prediction', icon: GitBranch },
    { id: 'twins', name: 'Digital Twins', icon: Layers },
    { id: 'simulation', name: 'Cellular Simulation', icon: Activity },
    { id: 'agents', name: 'AI Scientist Chat', icon: MessageSquare },
    { id: 'pathway', name: 'Pathway Designer', icon: Share2 },
    { id: 'mutation', name: 'Mutation Sandbox', icon: Sliders },
    { id: 'drug', name: 'Drug Lab', icon: FlaskConical },
    { id: 'experiments', name: 'Experiments', icon: GitPullRequest },
    { id: 'reports', name: 'Reports', icon: FileText },
    { id: 'settings', name: 'Settings', icon: SettingsIcon },
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
              <h1 className="text-md font-bold tracking-wider font-mono bg-gradient-to-r from-emerald-400 to-indigo-400 bg-clip-text text-transparent">PROTEA</h1>
              <p className="text-[10px] text-slate-500 uppercase tracking-widest font-mono">v2.0 BioAI Studio</p>
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
                      ? 'bg-gradient-to-r from-slate-800 to-slate-900 border-l-2 border-emerald-400 text-slate-100'
                      : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-200'
                  }`}
                >
                  <Icon className={`h-4 w-4 ${activeTab === tab.id ? 'text-emerald-400' : 'text-slate-500'}`} />
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
            <span className={apiOnline ? "text-emerald-400 font-semibold" : "text-amber-400 animate-pulse"}>
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
            <span className="text-xs font-semibold uppercase tracking-wider font-mono text-slate-400">Discovery Studio Workbench</span>
            <div className="h-4 w-px bg-slate-800" />
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-slate-500 font-mono">Status:</span>
              <span className="flex items-center space-x-1">
                <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
                <span className="text-emerald-400 font-mono text-[10px]">HEALTHY</span>
              </span>
            </div>
          </div>

          {/* Database connections status */}
          <div className="flex items-center space-x-2 text-[10px] font-mono">
            <span className="text-slate-500">DB Stack:</span>
            <div className="flex space-x-1.5">
              {Object.entries(systemStatus.services).map(([key, val]) => (
                <div key={key} className="flex items-center space-x-1 bg-slate-950 px-1.5 py-0.5 rounded border border-slate-800">
                  <span className="capitalize text-slate-400">{key}:</span>
                  <span className={`h-1.5 w-1.5 rounded-full ${val === 'online' ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'}`} />
                </div>
              ))}
            </div>
          </div>
        </header>

        {/* Primary Content viewport */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Sci-Fi Hero Header */}
              <div className="bg-gradient-to-r from-slate-900 via-[#0b1528] to-slate-950 p-6 rounded-lg border border-slate-800 relative overflow-hidden glow-emerald">
                <div className="relative z-10 max-w-2xl">
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">PHASE 2 - COMPLETED</span>
                  <h2 className="text-xl font-bold mt-2 font-mono text-slate-100">Protein Intelligence Engine (PIE)</h2>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    Phase 2 introduces robust sequence and structural representation models. Fusing ESM-2/ProtBERT PLM outputs against 3D residue configurations yields a unified 1024-D latent vector indexed in Qdrant collections.
                  </p>
                </div>
                <div className="absolute right-6 top-6 opacity-10">
                  <Compass className="h-32 w-32 text-emerald-400" />
                </div>
              </div>

              {/* Grid Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <PanelCard title="Embedding Versioning (PIE)">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Embedding Version:</span>
                      <span className="text-emerald-400">v2.0.0</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Feature Version:</span>
                      <span className="text-slate-300">f1.0.0</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">Dataset Version:</span>
                      <span className="text-indigo-400">db-v1.0.0</span>
                    </div>
                  </div>
                </PanelCard>

                <PanelCard title="Model Registry (MLflow)">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">esm2:</span>
                      <span className="text-emerald-400">esm2_t30_150M_UR50D</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">protbert:</span>
                      <span className="text-slate-300">Rostlab/prot_bert</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">cross_attention:</span>
                      <span className="text-indigo-400">Registered</span>
                    </div>
                  </div>
                </PanelCard>

                <PanelCard title="Qdrant Target Indexing">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">proteins_esm2:</span>
                      <span className="text-slate-300">1280-D Index</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">proteins_protbert:</span>
                      <span className="text-slate-300">1024-D Index</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">proteins_fused:</span>
                      <span className="text-emerald-400">1024-D canonical</span>
                    </div>
                  </div>
                </PanelCard>
              </div>

              {/* Terminal View logs */}
              <div className="bg-[#02050a] border border-slate-800 rounded-lg overflow-hidden">
                <div className="bg-[#080f1e] border-b border-slate-800 px-4 py-2 flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Terminal className="h-4 w-4 text-emerald-400" />
                    <span className="text-xs font-semibold font-mono text-slate-300">System Telemetry Audit Log</span>
                  </div>
                </div>
                <div className="p-4 h-48 overflow-y-auto font-mono text-xs text-slate-300 space-y-1 bg-black/60">
                  {logs.map((log, index) => (
                    <div key={index} className="flex space-x-2 leading-relaxed">
                      <span className="text-slate-600">[{index + 1}]</span>
                      <span className={log.includes("[SYSTEM]") ? "text-slate-400" : log.includes("[DATABASE]") ? "text-amber-400" : "text-emerald-400"}>
                        {log}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PROTEIN UNIVERSE - PROTEIN INTELLIGENCE WORKSPACE */}
          {activeTab === 'protein' && (
            <div className="space-y-6">
              
              {/* Toolbar console */}
              <div className="bg-slate-900 border border-slate-800 p-4 rounded-lg flex flex-wrap gap-4 items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="h-10 w-10 rounded-full bg-emerald-500/10 flex items-center justify-center border border-emerald-500/20">
                    <Dna className="h-5 w-5 text-emerald-400" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold font-mono">Protein Intelligence Workspace</h3>
                    <p className="text-[11px] text-slate-500">Comprehensive sequence parsing, embedding caching, and topological mapping console</p>
                  </div>
                </div>

                <div className="flex space-x-3 items-center">
                  <div className="flex flex-col">
                    <label className="text-[9px] font-mono text-slate-500 uppercase">Model Core</label>
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
                    <label className="text-[9px] font-mono text-slate-500 uppercase">UniProt ID</label>
                    <input
                      type="text"
                      value={uniprotId}
                      onChange={(e) => setUniprotId(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded p-1.5 text-xs font-mono text-slate-200 mt-0.5 w-24 focus:outline-none"
                    />
                  </div>

                  <div className="flex flex-col">
                    <label className="text-[9px] font-mono text-slate-500 uppercase">Name</label>
                    <input
                      type="text"
                      value={proteinName}
                      onChange={(e) => setProteinName(e.target.value)}
                      className="bg-slate-950 border border-slate-800 rounded p-1.5 text-xs font-mono text-slate-200 mt-0.5 w-28 focus:outline-none"
                    />
                  </div>
                </div>
              </div>

              {/* Main Panel Ingest Form */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                
                {/* Inputs block */}
                <div className="lg:col-span-2 space-y-6">
                  <PanelCard title="FASTA Amino Acid Sequence Ingestion">
                    <div className="space-y-4">
                      <textarea
                        value={sequence}
                        onChange={(e) => setSequence(e.target.value)}
                        placeholder="Insert single FASTA format or raw amino acid sequence..."
                        className="w-full h-44 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-emerald-500"
                      />
                      
                      <div className="space-y-1">
                        <label className="block text-[10px] font-mono text-slate-500 uppercase">Optional PDB coordinates (For Tripartite Cross-Fusion)</label>
                        <textarea
                          value={pdbFileContent}
                          onChange={(e) => setPdbFileContent(e.target.value)}
                          placeholder="Paste ATOM / HETATM lines from coordinate file..."
                          className="w-full h-24 bg-slate-950 border border-slate-800 rounded p-2 text-[10px] font-mono text-slate-500 focus:outline-none focus:border-indigo-500"
                        />
                      </div>

                      <div className="flex space-x-2">
                        <button
                          disabled={isProcessing}
                          onClick={handleInjest}
                          className="bg-emerald-500 hover:bg-emerald-600 disabled:opacity-50 text-slate-950 font-bold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                        >
                          {isProcessing ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Play className="h-3.5 w-3.5 fill-current" />}
                          <span>Generate & Index Embedding</span>
                        </button>

                        <button
                          disabled={isSearching}
                          onClick={handleSearchNeighbors}
                          className="bg-slate-800 hover:bg-slate-700 disabled:opacity-50 text-slate-300 font-bold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                        >
                          {isSearching ? <RefreshCw className="h-3.5 w-3.5 animate-spin" /> : <Search className="h-3.5 w-3.5" />}
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
                          <span className="text-slate-300 font-semibold">{embeddingResult.uniprot_id}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Model:</span>
                          <span className="text-slate-300">{embeddingResult.model_used}</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Dimensions:</span>
                          <span className="text-indigo-400">{embeddingResult.embedding_dimension}-D</span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Cache:</span>
                          <span className={embeddingResult.cache_status === "hit" ? "text-emerald-400" : "text-amber-400"}>
                            {embeddingResult.cache_status.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex justify-between border-b border-slate-800 pb-1">
                          <span className="text-slate-500">Fusion:</span>
                          <span className="text-indigo-400">{embeddingResult.fused_status}</span>
                        </div>
                        <div className="pt-1">
                          <span className="text-slate-500 block">Vector Preview:</span>
                          <span className="text-[10px] text-slate-400 break-all block bg-slate-950 p-1.5 rounded mt-1 border border-slate-800">
                            {JSON.stringify(embeddingResult.pooled_vector_preview)}...
                          </span>
                        </div>
                      </div>
                    ) : (
                      <div className="flex flex-col items-center justify-center h-48 text-center text-slate-500 text-xs font-mono">
                        <Info className="h-6 w-6 mb-2 text-slate-700" />
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
                          <th className="py-2">UniProt ID</th>
                          <th className="py-2">Protein Name</th>
                          <th className="py-2">Organism</th>
                          <th className="py-2">Gene</th>
                          <th className="py-2 text-right">Similarity Score</th>
                        </tr>
                      </thead>
                      <tbody>
                        {searchResults.map((res: any, i: number) => (
                          <tr key={i} className="border-b border-slate-850 hover:bg-slate-900/40">
                            <td className="py-2 text-emerald-400 font-semibold">{res.id}</td>
                            <td className="py-2 text-slate-300">{res.payload?.name || "Unidentified"}</td>
                            <td className="py-2 text-slate-400">{res.payload?.organism || "Unknown"}</td>
                            <td className="py-2 text-slate-500">{res.payload?.gene || "N/A"}</td>
                            <td className="py-2 text-right text-indigo-400 font-bold">{(res.score * 100).toFixed(2)}%</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </PanelCard>
              )}

            </div>
          )}

          {/* TAB 3: KNOWLEDGE GRAPH */}
          {activeTab === 'graph' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Universal Biological Knowledge Graph</h3>
                  <p className="text-xs text-slate-400 mt-1">Directly query OptimusKG using Cypher relational queries across multiple organism scales.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 3
                </div>
              </div>
            </div>
          )}

          {/* Other tabs placeholders remain standard... */}
          {activeTab !== 'overview' && activeTab !== 'protein' && activeTab !== 'graph' && (
            <div className="bg-slate-900 border border-slate-800 p-12 rounded-lg text-center font-mono">
              <Sliders className="h-12 w-12 text-slate-700 mx-auto mb-4 animate-pulse" />
              <h3 className="text-md font-bold text-slate-300">Feature Under Development</h3>
              <p className="text-xs text-slate-500 mt-1">This module is scheduled for implementation in a future phase of the PROTEA roadmap.</p>
            </div>
          )}

        </div>
      </main>

    </div>
  );
}
