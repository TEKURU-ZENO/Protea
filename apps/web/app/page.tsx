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
  GitPullRequest
} from 'lucide-react';
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

  const [cypherQuery, setCypherQuery] = useState("MATCH (p:Protein)-[r:INTERACTS_WITH]->(g:Gene) RETURN p, r, g LIMIT 10;");
  const [sequenceInput, setSequenceInput] = useState("MNGTEGPNFYVPFSNKTGVVRSPFEAPQYYLAEPWQFSMLAAYMFLLIMLGFPINFLTLYVTVQHKKLRTPLNYILLNLAVADLFMVFGGFTTTLYTSLHGYFVFGPTGCNLEGFFATLGGEIALWSLVVLAIERWVVVCKPMSNFRFGENHAIMGVAFTWVMALACAAPPLVGWSRYIPEGMQCSCGIDYYTPHEETNNESFVIYMFVVHFIIPLIVIFFCYGQLVFTVKEAAAQQQESATTQKAEKEVTRMVIIMVIAFLICWLPYAGVAFYIFTHQGSDFGPIFMTIPAFFAKTSAVYNPVIYIMMNKQFRNCMVTTLCCGKNPLGDDEASTTVSKTETSQVAPA");
  
  // Simulate health checking and connection
  useEffect(() => {
    const timer = setInterval(() => {
      setSystemStatus(prev => ({
        ...prev,
        uptime: prev.uptime + 1,
        services: {
          postgres: prev.uptime > 2 ? 'online' : 'loading',
          neo4j: prev.uptime > 3 ? 'online' : 'loading',
          redis: prev.uptime > 1 ? 'online' : 'loading',
          qdrant: prev.uptime > 4 ? 'online' : 'loading',
          minio: prev.uptime > 2 ? 'online' : 'loading',
          mlflow: prev.uptime > 3 ? 'online' : 'loading'
        }
      }));
    }, 1000);

    const logTimer = setTimeout(() => {
      setLogs(prev => [
        ...prev,
        "[DATABASE] PostgreSQL pool established (5/20 min/max size).",
        "[GRAPH] Neo4j Bolt driver initialized at port 7687.",
        "[CACHE] Redis client ping success at port 6379.",
        "[VECTOR] Qdrant connection verified. Collections catalog parsed.",
        "[STORAGE] MinIO object store interface connected.",
        "[MONITOR] OpenTelemetry metrics exporter registered on /metrics."
      ]);
    }, 2000);

    return () => {
      clearInterval(timer);
      clearTimeout(logTimer);
    };
  }, []);

  const addLog = (msg: string) => {
    setLogs(prev => [...prev, `[USER] ${msg}`]);
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
            <span>Config:</span>
            <span className="text-slate-300">development.yaml</span>
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
                  <span className="text-[10px] font-mono bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-2 py-0.5 rounded">PHASE 1 - COMPLETED</span>
                  <h2 className="text-xl font-bold mt-2 font-mono text-slate-100">Biological Discovery Studio Shell</h2>
                  <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                    Welcome to the central intelligence workspace of PROTEA. Phase 1 sets up the foundations of model orchestration, property graphs, vectors, object databases, and microservices gateway routes. Use the navigation panel on the left to explore the system blueprint.
                  </p>
                </div>
                <div className="absolute right-6 top-6 opacity-10">
                  <Compass className="h-32 w-32 text-emerald-400" />
                </div>
              </div>

              {/* Grid Statistics */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <PanelCard title="OptimusKG Schema (Neo4j)">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Nodes Scale:</span>
                      <span className="text-slate-300">190,531 (Constraints Set)</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Edges Scale:</span>
                      <span className="text-slate-300">21,813,816 (Mapped Types)</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">Property Density:</span>
                      <span className="text-slate-300">67,249,863 instances</span>
                    </div>
                  </div>
                </PanelCard>

                <PanelCard title="Model Server (MLflow)">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Registered Registry:</span>
                      <span className="text-emerald-400">Connected</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Active Pipelines:</span>
                      <span className="text-slate-300">0 Running</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">Server Endpoint:</span>
                      <span className="text-indigo-400">http://localhost:5000</span>
                    </div>
                  </div>
                </PanelCard>

                <PanelCard title="Vector Cache (Qdrant)">
                  <div className="space-y-2 text-xs font-mono">
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Collections:</span>
                      <span className="text-slate-300">0 Created</span>
                    </div>
                    <div className="flex justify-between border-b border-slate-800/50 pb-1">
                      <span className="text-slate-500">Index Types:</span>
                      <span className="text-slate-300">HNSW Vector</span>
                    </div>
                    <div className="flex justify-between pb-1">
                      <span className="text-slate-500">GRPC status:</span>
                      <span className="text-emerald-400">Verifying</span>
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
                  <span className="text-[10px] text-slate-500 font-mono">Interactive logs</span>
                </div>
                <div className="p-4 h-48 overflow-y-auto font-mono text-xs text-slate-300 space-y-1 bg-black/60">
                  {logs.map((log, index) => (
                    <div key={index} className="flex space-x-2 leading-relaxed">
                      <span className="text-slate-600">[{index + 1}]</span>
                      <span className={log.includes("[SYSTEM]") ? "text-slate-400" : log.includes("[DATABASE]") ? "text-amber-400" : log.includes("[USER]") ? "text-indigo-400" : "text-emerald-400"}>
                        {log}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* TAB 2: PROTEIN UNIVERSE */}
          {activeTab === 'protein' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Protein Universe Explorer</h3>
                  <p className="text-xs text-slate-400 mt-1">Extract high-dimensional protein language model embeddings (ESM-2 / ProtBERT) and parse FASTA sequences.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 2
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <PanelCard title="FASTA Sequence Ingestion">
                  <div className="space-y-4">
                    <label className="block text-xs font-mono text-slate-400">Insert Protein Sequence:</label>
                    <textarea 
                      value={sequenceInput}
                      onChange={(e) => setSequenceInput(e.target.value)}
                      className="w-full h-32 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-slate-300 focus:outline-none focus:border-emerald-500"
                    />
                    <button 
                      onClick={() => {
                        addLog("Ingested sequence length: " + sequenceInput.length);
                      }}
                      className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                    >
                      <Play className="h-3 w-3 fill-current" />
                      <span>Parse Sequence</span>
                    </button>
                  </div>
                </PanelCard>

                <PanelCard title="3D Mol* Viewer Workbench">
                  <div className="bg-slate-950 border border-slate-800 rounded h-64 flex flex-col items-center justify-center text-center p-4">
                    <Dna className="h-12 w-12 text-slate-700 animate-pulse mb-3" />
                    <span className="text-xs font-mono text-slate-400">Mol* Interactive Viewer Canvas</span>
                    <span className="text-[10px] font-mono text-slate-600 mt-1">3D structure rendering will load coordinates during Phase 2 structure ingestion.</span>
                  </div>
                </PanelCard>
              </div>
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

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="md:col-span-2 space-y-4">
                  <PanelCard title="Cypher Query Editor">
                    <div className="space-y-4">
                      <textarea
                        value={cypherQuery}
                        onChange={(e) => setCypherQuery(e.target.value)}
                        className="w-full h-32 bg-slate-950 border border-slate-800 rounded p-2 text-xs font-mono text-indigo-300 focus:outline-none focus:border-indigo-500"
                      />
                      <button
                        onClick={() => addLog("Executed Cypher: " + cypherQuery)}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold px-4 py-2 rounded text-xs font-mono transition-all flex items-center space-x-2"
                      >
                        <Terminal className="h-3 w-3" />
                        <span>Run Query</span>
                      </button>
                    </div>
                  </PanelCard>
                </div>

                <PanelCard title="OptimusKG Entity Schema">
                  <div className="space-y-2 text-xs font-mono max-h-64 overflow-y-auto">
                    <span className="text-slate-500 uppercase tracking-widest block text-[9px] mb-2">Registered Labels</span>
                    {["Protein", "Gene", "Pathway", "Disease", "Drug", "Organism", "Tissue", "Publication"].map(lbl => (
                      <div key={lbl} className="flex justify-between items-center border-b border-slate-800/50 pb-1.5">
                        <span className="text-indigo-400 font-semibold">{lbl}</span>
                        <span className="text-[10px] text-slate-500">Constraint Set</span>
                      </div>
                    ))}
                  </div>
                </PanelCard>
              </div>
            </div>
          )}

          {/* TAB 4: INTERACTION PREDICTION */}
          {activeTab === 'prediction' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Interaction Prediction Engine</h3>
                  <p className="text-xs text-slate-400 mt-1">Compute link predictions over scale-free biological networks using GraphSAGE & GAT.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 4
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <PanelCard title="Link Prediction Parameters">
                  <div className="space-y-4 text-xs font-mono">
                    <div className="space-y-1">
                      <label className="text-slate-400">Upstream Node (Protein A):</label>
                      <input type="text" placeholder="e.g. BRCA1" className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-slate-400">Downstream Node (Protein B):</label>
                      <input type="text" placeholder="e.g. BARD1" className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200" />
                    </div>
                    <div className="space-y-1">
                      <label className="text-slate-400">GNN Model Architecture:</label>
                      <select className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200">
                        <option>GraphSAGE (PPI Node Aggregator)</option>
                        <option>GATv2 (Attention Weighted Network)</option>
                      </select>
                    </div>
                    <button
                      onClick={() => addLog("Triggered interaction prediction job.")}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded font-semibold"
                    >
                      Predict Interaction
                    </button>
                  </div>
                </PanelCard>

                <PanelCard title="Bayesian Confidence Bounds">
                  <div className="bg-slate-950 border border-slate-800 rounded h-56 flex flex-col items-center justify-center text-center p-4 font-mono">
                    <Activity className="h-8 w-8 text-indigo-500/40 mb-3 animate-pulse" />
                    <span className="text-xs text-slate-400">Uncertainty Variance Distribution</span>
                    <span className="text-[10px] text-slate-600 mt-1">Calculates Monte Carlo dropout outputs during predictions (Phase 4).</span>
                  </div>
                </PanelCard>
              </div>
            </div>
          )}

          {/* TAB 5: DIGITAL TWINS */}
          {activeTab === 'twins' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Digital Interactome Twin</h3>
                  <p className="text-xs text-slate-400 mt-1">Compare healthy vs tissue/cell-type specific diseased interactome profiles.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 7
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {["Healthy Brain", "Cancer Tissue", "Alzheimer's Disease"].map((twin, idx) => (
                  <PanelCard key={idx} title={twin}>
                    <div className="space-y-2 text-xs font-mono">
                      <div className="flex justify-between border-b border-slate-800 pb-1">
                        <span className="text-slate-500">Atlas Input:</span>
                        <span className="text-slate-300">{idx === 0 ? "Brain snRNA-seq" : idx === 1 ? "Patient CZ CellxGene" : "Postmortem snRNA-seq"}</span>
                      </div>
                      <div className="flex justify-between border-b border-slate-800 pb-1">
                        <span className="text-slate-500">Active Pathways:</span>
                        <span className="text-slate-300">{idx === 0 ? "Synaptic, Axonal" : idx === 1 ? "Proliferative, DNA repair" : "Neuroinflammation"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-500">Clinical Focus:</span>
                        <span className="text-indigo-400">{idx === 0 ? "Neurotransmission" : idx === 1 ? "Synthetic Lethality" : "Biomarkers"}</span>
                      </div>
                    </div>
                  </PanelCard>
                ))}
              </div>
            </div>
          )}

          {/* TAB 6: CELLULAR SIMULATION */}
          {activeTab === 'simulation' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Cellular Simulation Engine</h3>
                  <p className="text-xs text-slate-400 mt-1">Model continuous temporal concentrations utilizing NeuralODEs combined with Hill-Langmuir kinetics.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 8
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <PanelCard title="ODE Solver parameters">
                  <div className="space-y-3 text-xs font-mono">
                    <div>
                      <label className="text-slate-400">Degradation Rate (\(\alpha\)):</label>
                      <input type="number" defaultValue="0.05" step="0.01" className="w-full bg-slate-950 border border-slate-800 rounded p-1.5 text-slate-200 mt-1" />
                    </div>
                    <div>
                      <label className="text-slate-400">Solver Algorithm:</label>
                      <select className="w-full bg-slate-950 border border-slate-800 rounded p-1.5 text-slate-200 mt-1">
                        <option>Heun's 2nd Order ODE Solver</option>
                        <option>Dormand-Prince (adaptive step)</option>
                      </select>
                    </div>
                    <button
                      onClick={() => addLog("Solved ODE state transition.")}
                      className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold px-4 py-2 rounded text-xs font-mono w-full mt-2"
                    >
                      Execute Simulation Run
                    </button>
                  </div>
                </PanelCard>

                <div className="md:col-span-2">
                  <PanelCard title="State Evolution Time-Series">
                    <div className="bg-slate-950 border border-slate-800 rounded h-64 flex flex-col items-center justify-center text-center p-4">
                      <Sliders className="h-10 w-10 text-slate-700 mb-3 animate-pulse" />
                      <span className="text-xs font-mono text-slate-400">NeuralODE Trajectory Chart Canvas</span>
                      <span className="text-[10px] font-mono text-slate-600 mt-1">Calculates simulated trajectories on timeline triggers (Phase 8).</span>
                    </div>
                  </PanelCard>
                </div>
              </div>
            </div>
          )}

          {/* TAB 7: AI SCIENTIST CHAT */}
          {activeTab === 'agents' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">AI Scientist Swarm Console</h3>
                  <p className="text-xs text-slate-400 mt-1">Collaborate with autonomous multi-agent swarms orchestrated by a human-in-the-loop interface.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 9
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <PanelCard title="Agent Orchesration Swarm">
                  <div className="space-y-2 text-xs font-mono">
                    {[
                      { name: "Literature Expert", task: "Retrieves literature evidence & ECO mapping" },
                      { name: "Protein Expert", task: "Evaluates protein interface folding parameters" },
                      { name: "Mutation Expert", task: "Calculates stability variants pathogenicity" },
                      { name: "Drug Lab Expert", task: "Runs docking pose bindings scoring" }
                    ].map((agent, i) => (
                      <div key={i} className="p-2 border border-slate-800 rounded bg-slate-950">
                        <span className="text-emerald-400 font-semibold block">{agent.name}</span>
                        <span className="text-[10px] text-slate-500">{agent.task}</span>
                      </div>
                    ))}
                  </div>
                </PanelCard>

                <div className="md:col-span-3">
                  <PanelCard title="Scientific Dialog Terminal">
                    <div className="space-y-4">
                      <div className="bg-slate-950 border border-slate-800 rounded p-4 h-48 overflow-y-auto text-xs font-mono space-y-2 text-slate-300">
                        <div className="text-slate-500">[SYSTEM] Swarm standing by. Enter hypothesis or goal.</div>
                      </div>
                      <div className="flex gap-2">
                        <input type="text" placeholder="Type scientific request e.g. Analyze mutation effects on p53 pathway..." className="flex-1 bg-slate-950 border border-slate-800 rounded px-3 py-2 text-xs font-mono focus:outline-none focus:border-indigo-500" />
                        <button className="bg-indigo-600 hover:bg-indigo-700 px-4 py-2 rounded text-xs font-mono font-semibold">Send</button>
                      </div>
                    </div>
                  </PanelCard>
                </div>
              </div>
            </div>
          )}

          {/* TAB 8: PATHWAY DESIGNER */}
          {activeTab === 'pathway' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Interactive Pathway Designer</h3>
                  <p className="text-xs text-slate-400 mt-1">Design and visualize signal transduction cascades using a React Flow canvas.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 10
                </div>
              </div>

              <PanelCard title="React Flow Visual Canvas">
                <div className="bg-slate-950 border border-slate-800 rounded h-96 flex flex-col items-center justify-center text-center p-4">
                  <Share2 className="h-12 w-12 text-slate-700 mb-3 animate-pulse" />
                  <span className="text-xs font-mono text-slate-400">Interactive Pathway Layout Graph</span>
                  <span className="text-[10px] font-mono text-slate-600 mt-1">Load and configure nodes/edges interactively using Cytoscape Web / React Flow (Phase 10).</span>
                </div>
              </PanelCard>
            </div>
          )}

          {/* TAB 9: MUTATION SANDBOX */}
          {activeTab === 'mutation' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Mutation Sandbox</h3>
                  <p className="text-xs text-slate-400 mt-1">Simulate variant amino acid alterations and map localized stability values.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 10
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <PanelCard title="Amino Acid Missense Configuration">
                  <div className="space-y-3 text-xs font-mono">
                    <div>
                      <label className="text-slate-400">Mutation Target (BRCA1 variant):</label>
                      <input type="text" defaultValue="M1775R" className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 mt-1" />
                    </div>
                    <button
                      onClick={() => addLog("Evaluated mutant M1775R deltaDeltaG.")}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded font-semibold w-full mt-2"
                    >
                      Calculate Variant Effect
                    </button>
                  </div>
                </PanelCard>

                <PanelCard title="Variant Pathogenicity Report">
                  <div className="bg-slate-950 border border-slate-800 rounded h-48 flex flex-col items-center justify-center text-center p-4">
                    <Activity className="h-8 w-8 text-slate-700 mb-2" />
                    <span className="text-xs font-mono text-slate-400">Pathogenicity deltaDeltaG scoring</span>
                  </div>
                </PanelCard>
              </div>
            </div>
          )}

          {/* TAB 10: DRUG LAB */}
          {activeTab === 'drug' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Drug Lab Docking Simulator</h3>
                  <p className="text-xs text-slate-400 mt-1">Input SMILES strings to evaluate docking affinity using Boltz-2 / Chai-1 models.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 10
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <PanelCard title="SMILES Compound Ingestion">
                  <div className="space-y-3 text-xs font-mono">
                    <div>
                      <label className="text-slate-400">Input SMILES String:</label>
                      <input type="text" defaultValue="CC(=O)NC1=CC=C(C=C1)O" className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-slate-200 mt-1" />
                    </div>
                    <button
                      onClick={() => addLog("Initiated docking evaluation.")}
                      className="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-semibold px-4 py-2 rounded text-xs font-mono w-full"
                    >
                      Run Co-Folding Docking Model
                    </button>
                  </div>
                </PanelCard>

                <PanelCard title="Binding Affinity (pIC50) Output">
                  <div className="bg-slate-950 border border-slate-800 rounded h-40 flex flex-col items-center justify-center text-center p-4 font-mono">
                    <span className="text-xs text-slate-400">Affinity Prediction details</span>
                  </div>
                </PanelCard>
              </div>
            </div>
          )}

          {/* TAB 11: EXPERIMENTS */}
          {activeTab === 'experiments' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Physical Experiment Planner</h3>
                  <p className="text-xs text-slate-400 mt-1">Generate robotic liquid handler protocol scripts (Opentrons API) to validate predictions.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 9
                </div>
              </div>
            </div>
          )}

          {/* TAB 12: REPORTS */}
          {activeTab === 'reports' && (
            <div className="space-y-6">
              <div className="bg-slate-900 border border-slate-800 p-6 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold font-mono">Interactive Research Reports</h3>
                  <p className="text-xs text-slate-400 mt-1">Compile comprehensive, peer-review ready reports combining 3D structures, interaction network tables, and literature citation pathways.</p>
                </div>
                <div className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded text-xs font-mono self-start md:self-auto">
                  Coming in Phase 10
                </div>
              </div>
            </div>
          )}

          {/* TAB 13: SETTINGS */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <PanelCard title="Global Platform Settings">
                <div className="space-y-4 text-xs font-mono">
                  <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Environment Selector:</span>
                    <select className="bg-slate-950 border border-slate-800 rounded p-1 text-slate-200">
                      <option>development.yaml</option>
                      <option>production.yaml</option>
                      <option>docker.yaml</option>
                      <option>gpu.yaml</option>
                    </select>
                  </div>
                  <div className="flex justify-between items-center border-b border-slate-800 pb-2">
                    <span className="text-slate-400">Observability Exporter:</span>
                    <span className="text-emerald-400 font-semibold">OpenTelemetry OTLP (Active)</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-slate-400">Security / Auth Gateway:</span>
                    <span className="text-slate-300">Mock Middleware Keycloak Shell</span>
                  </div>
                </div>
              </PanelCard>
            </div>
          )}

        </div>
      </main>

    </div>
  );
}
