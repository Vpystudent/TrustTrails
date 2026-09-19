import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import CytoscapeComponent from 'react-cytoscapejs';
import { Shield, AlertTriangle, CheckCircle, Info, Copy, ExternalLink, ChevronDown, ChevronUp, Activity, Search, RefreshCw, Zap } from 'lucide-react';
import { demoAddresses } from './demoAddresses';
import './index.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [address, setAddress] = useState('');
  const [chains, setChains] = useState(['ethereum', 'base']);
  const [availableChains, setAvailableChains] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('all');

  useEffect(() => {
    axios.get(`${API_URL}/chains`).then(res => {
      setAvailableChains(res.data);
    }).catch(err => {
      console.warn("Could not fetch chains", err);
      setAvailableChains([
        {id: 'ethereum', name: 'Ethereum', explorer_tx_url: 'https://etherscan.io/tx/{h}', explorer_addr_url: 'https://etherscan.io/address/{a}'},
        {id: 'base', name: 'Base', explorer_tx_url: 'https://basescan.org/tx/{h}', explorer_addr_url: 'https://basescan.org/address/{a}'}
      ]);
    });
  }, []);

  const fetchReport = async (addr, chs) => {
    setLoading(true); setError(null); setReport(null);
    try {
      const res = await axios.get(`${API_URL}/report`, { params: { address: addr, chains: chs.join(',') } });
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const getChainUrl = (chain_id, hash, type='tx') => {
    const chainInfo = availableChains.find(c => c.id === chain_id);
    if (!chainInfo) return '#';
    const tpl = type === 'tx' ? chainInfo.explorer_tx_url : chainInfo.explorer_addr_url;
    return tpl ? tpl.replace('{h}', hash).replace('{a}', hash) : '#';
  };

  const filteredSignals = report ? (activeTab === 'all' ? report.signals : report.signals.filter(s => s.chain === activeTab)) : [];

  return (
    <div className="min-h-screen bg-[#050505] text-gray-200 font-sans selection:bg-indigo-500/30">
      
      {/* Navbar */}
      <nav className="border-b border-white/5 bg-black/40 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="TrustTrail Logo" className="h-10 w-10 rounded-xl invert opacity-90 shadow-[0_0_15px_rgba(255,255,255,0.1)]" />
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">TrustTrail <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 text-[10px] tracking-widest uppercase border border-indigo-500/20">Beta</span></h1>
              <p className="text-xs text-gray-500 tracking-wide">Every risk flag comes with proof.</p>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10 space-y-8">
        
        {/* Search Hero */}
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-1000 group-hover:duration-200"></div>
          <div className="relative bg-[#0a0a0a] border border-white/10 rounded-2xl p-6 shadow-2xl">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="relative flex-1">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500" size={20} />
                <input 
                  type="text" 
                  placeholder="Paste any wallet or contract address (0x...)" 
                  value={address} 
                  onChange={e => setAddress(e.target.value)}
                  className="w-full bg-[#111] border border-white/10 text-white pl-12 pr-4 py-4 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500 transition-all text-lg font-mono placeholder:font-sans placeholder:text-gray-600"
                />
              </div>
              <button 
                onClick={() => fetchReport(address, chains)} 
                disabled={loading || !address}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-500 text-white px-8 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 min-w-[160px]"
              >
                {loading ? <RefreshCw className="animate-spin" size={20}/> : <Zap size={20}/>}
                {loading ? 'Scanning...' : 'Analyze'}
              </button>
            </div>
            
            <div className="mt-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-t border-white/5 pt-4">
              <div className="flex items-center gap-6">
                <span className="text-sm text-gray-500 font-medium uppercase tracking-wider">Networks:</span>
                {availableChains.map(c => (
                  <label key={c.id} className="flex items-center gap-2 cursor-pointer group">
                    <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${chains.includes(c.id) ? 'bg-indigo-500 border-indigo-500' : 'border-gray-600 group-hover:border-gray-400'}`}>
                      {chains.includes(c.id) && <CheckCircle size={12} className="text-white" />}
                    </div>
                    <input type="checkbox" className="hidden" checked={chains.includes(c.id)}
                      onChange={(e) => setChains(e.target.checked ? [...chains, c.id] : chains.filter(x => x !== c.id))}
                    />
                    <span className={`text-sm ${chains.includes(c.id) ? 'text-gray-200' : 'text-gray-500'}`}>{c.name}</span>
                  </label>
                ))}
              </div>

              <div className="flex flex-wrap gap-2">
                <span className="text-sm text-gray-500 font-medium uppercase tracking-wider self-center mr-2">Try it:</span>
                {demoAddresses.map((d, i) => (
                  <button key={i} onClick={() => { setAddress(d.address); setChains(d.chains); fetchReport(d.address, d.chains); }}
                    className="text-xs bg-white/5 hover:bg-white/10 border border-white/5 px-3 py-1.5 rounded-lg transition-colors text-gray-400 hover:text-white flex items-center gap-1.5"
                  >
                    <Activity size={12}/> {d.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-6 py-4 rounded-xl flex items-start gap-3">
            <AlertTriangle className="shrink-0 mt-0.5" size={20}/>
            <div>
              <h3 className="font-semibold text-red-300">Scan Failed</h3>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Dashboard View */}
        {report && !loading && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            
            {/* Header Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              <div className="lg:col-span-2 bg-[#111] border border-white/5 rounded-2xl p-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-[80px] rounded-full pointer-events-none"></div>
                
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-bold text-white">Trust Report</h2>
                      {report.cache?.hit && <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2 py-0.5 rounded-full flex items-center gap-1"><Zap size={10}/> Cached</span>}
                    </div>
                    <div className="flex items-center gap-2 bg-black/50 px-3 py-1.5 rounded-lg border border-white/5 w-fit">
                      <span className="font-mono text-sm text-gray-300">{report.address}</span>
                      <button onClick={() => navigator.clipboard.writeText(report.address)} className="text-gray-500 hover:text-white transition-colors">
                        <Copy size={14}/>
                      </button>
                    </div>
                  </div>
                  
                  <div className="text-right">
                    <div className="text-sm text-gray-500 uppercase tracking-widest font-semibold mb-1">Risk Score</div>
                    <div className="flex items-baseline gap-1 justify-end">
                      <span className={`text-5xl font-black tracking-tighter ${
                        report.overall_risk === 'high' ? 'text-red-500' : 
                        report.overall_risk === 'medium' ? 'text-amber-500' : 'text-emerald-500'
                      }`}>{report.score}</span>
                      <span className="text-gray-600 font-bold">/100</span>
                    </div>
                    <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mt-2 border ${
                        report.overall_risk === 'high' ? 'bg-red-500/10 text-red-400 border-red-500/20' : 
                        report.overall_risk === 'medium' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' : 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
                      }`}>
                      {report.overall_risk === 'high' ? <AlertTriangle size={12}/> : report.overall_risk === 'medium' ? <Info size={12}/> : <Shield size={12}/>}
                      {report.overall_risk} RISK
                    </div>
                  </div>
                </div>

                {report.warnings?.length > 0 && (
                  <div className="mt-6 bg-amber-500/10 border border-amber-500/20 rounded-xl p-3 text-sm text-amber-200 flex items-center gap-2">
                    <AlertTriangle size={16} className="text-amber-500"/>
                    <span><strong>Warnings:</strong> {report.warnings.map(w => w.chain).join(', ')} (API sync issues)</span>
                  </div>
                )}
                
                {report.history_truncated && (
                  <div className="mt-3 bg-blue-500/10 border border-blue-500/20 rounded-xl p-3 text-sm text-blue-200 flex items-center gap-2">
                    <Info size={16} className="text-blue-500"/>
                    <span><strong>Massive History:</strong> Scanned latest 10,000 interactions. Earlier data truncated.</span>
                  </div>
                )}
              </div>

              {/* AI Summary */}
              <div className="bg-gradient-to-br from-[#16161a] to-[#0a0a0c] border border-white/5 rounded-2xl p-6 flex flex-col">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-6 h-6 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                    <Zap size={14} className="text-indigo-400"/>
                  </div>
                  <h3 className="text-white font-bold">AI Analysis</h3>
                </div>
                <p className="text-gray-400 text-sm leading-relaxed flex-1">
                  {report.summary}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Evidence Graph */}
              <div className="lg:col-span-2 bg-[#111] border border-white/5 rounded-2xl overflow-hidden flex flex-col h-[500px]">
                <div className="px-6 py-4 border-b border-white/5 bg-black/20 flex justify-between items-center">
                  <h3 className="text-white font-bold flex items-center gap-2">
                    <Activity size={16} className="text-indigo-400"/>
                    Interaction Graph
                  </h3>
                  <div className="flex items-center gap-3 text-xs font-medium text-gray-500">
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-blue-500"></div> Target</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Flagged</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-purple-500"></div> Contract</span>
                  </div>
                </div>
                <div className="flex-1 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-black/40">
                  <EvidenceGraph graph={report.graph} availableChains={availableChains} />
                </div>
              </div>

              {/* Score Breakdown */}
              <div className="bg-[#111] border border-white/5 rounded-2xl flex flex-col h-[500px]">
                <div className="px-6 py-4 border-b border-white/5 bg-black/20">
                  <h3 className="text-white font-bold flex items-center gap-2">
                    <Shield size={16} className="text-emerald-400"/>
                    Score Breakdown
                  </h3>
                </div>
                <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
                  {report.points.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 text-sm space-y-2">
                      <CheckCircle size={32} className="text-emerald-500/50"/>
                      <p>Perfect score. No penalties applied.</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {report.points.map((pt, i) => (
                        <div key={i} className="flex gap-4 p-4 rounded-xl bg-white/[0.02] border border-white/[0.05]">
                          <div className="font-black text-lg text-red-400 pt-0.5">+{pt.points}</div>
                          <div>
                            <div className="text-white font-medium mb-1">{pt.signal_id.replace(/_/g, ' ')}</div>
                            <div className="text-sm text-gray-500 leading-snug">{pt.reason}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </div>

            {/* Signals Feed */}
            <div>
              <div className="flex items-center gap-2 mb-6 border-b border-white/5 pb-4">
                <button className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${activeTab === 'all' ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'}`} onClick={() => setActiveTab('all')}>All Signals</button>
                {report.chains.map(c => (
                  <button key={c} className={`px-4 py-2 rounded-lg text-sm font-medium transition-all capitalize ${activeTab === c ? 'bg-white/10 text-white' : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'}`} onClick={() => setActiveTab(c)}>{c}</button>
                ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {filteredSignals.length === 0 ? (
                  <div className="col-span-full py-12 flex flex-col items-center justify-center bg-[#111] border border-white/5 rounded-2xl border-dashed">
                    <CheckCircle size={48} className="text-emerald-500/50 mb-4"/>
                    <h3 className="text-xl font-bold text-white mb-2">No Risk Signals Found</h3>
                    <p className="text-gray-500 text-center max-w-md">We scanned for unlimited approvals, scam counterparties, contract privileges, and suspicious interactions. Everything looks clean.</p>
                  </div>
                ) : (
                  filteredSignals.map((sig, i) => <SignalCard key={i} signal={sig} getChainUrl={getChainUrl} />)
                )}
              </div>
            </div>

          </div>
        )}
      </main>
    </div>
  );
}

function SignalCard({ signal, getChainUrl }) {
  const [expanded, setExpanded] = useState(false);
  
  const sevColor = signal.severity === 'high' ? 'red' : signal.severity === 'medium' ? 'amber' : 'blue';
  const borderClass = `border-${sevColor}-500/30`;
  const bgClass = `bg-${sevColor}-500/5`;
  const textClass = `text-${sevColor}-400`;
  const badgeClass = `bg-${sevColor}-500/10 text-${sevColor}-400 border border-${sevColor}-500/20`;

  return (
    <div className={`rounded-2xl border bg-[#111] overflow-hidden transition-all hover:border-${sevColor}-500/50`} style={{borderColor: `var(--color-${sevColor}-500, rgba(255,255,255,0.1))`}}>
      {/* Fallback inline styles for dynamic tailwind classes that might not compile if not safelisted */}
      <div className="p-5 border-b border-white/5" style={{backgroundColor: signal.severity==='high'?'rgba(239,68,68,0.03)':signal.severity==='medium'?'rgba(245,158,11,0.03)':'rgba(59,130,246,0.03)'}}>
        <div className="flex justify-between items-start gap-4 mb-3">
          <h3 className="font-bold text-white leading-tight">{signal.title}</h3>
          <span className={`shrink-0 uppercase text-[10px] tracking-wider font-bold px-2 py-1 rounded-md`}
                style={{
                  backgroundColor: signal.severity==='high'?'rgba(239,68,68,0.1)':signal.severity==='medium'?'rgba(245,158,11,0.1)':'rgba(59,130,246,0.1)',
                  color: signal.severity==='high'?'#f87171':signal.severity==='medium'?'#fbbf24':'#60a5fa',
                  border: `1px solid ${signal.severity==='high'?'rgba(239,68,68,0.2)':signal.severity==='medium'?'rgba(245,158,11,0.2)':'rgba(59,130,246,0.2)'}`
                }}
          >
            {signal.severity}
          </span>
        </div>
        <div className="font-mono text-xs text-gray-400 bg-black/50 p-2 rounded-lg border border-white/5 break-all">
          {signal.rule}
        </div>
      </div>
      
      <div className="p-5">
        <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Evidence Log</h4>
        <div className="space-y-3">
          {(expanded ? signal.evidence : signal.evidence.slice(0, 3)).map((ev, i) => (
            <div key={i} className="text-sm bg-white/[0.02] border border-white/[0.05] p-3 rounded-xl flex flex-col gap-2">
              <span className="text-gray-300">{ev.detail}</span>
              {ev.tx_hash && (
                <a href={getChainUrl(signal.chain, ev.tx_hash, 'tx')} target="_blank" rel="noreferrer" 
                   className="flex items-center gap-1.5 text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium w-fit">
                  <ExternalLink size={12}/> View TX (Block {ev.block})
                </a>
              )}
            </div>
          ))}
        </div>
        {signal.evidence.length > 3 && (
          <button onClick={() => setExpanded(!expanded)} 
                  className="w-full mt-3 py-2 rounded-xl border border-white/5 text-xs font-bold text-gray-400 hover:bg-white/5 hover:text-white transition-colors flex items-center justify-center gap-2">
            {expanded ? <><ChevronUp size={14}/> Collapse</> : <><ChevronDown size={14}/> Show {signal.evidence.length - 3} More</>}
          </button>
        )}
      </div>
    </div>
  );
}

function EvidenceGraph({ graph, availableChains }) {
  if (!graph || !graph.nodes || graph.nodes.length === 0) return <div className="p-6 text-gray-500 text-center">No interaction data available.</div>;
  
  const elements = [
    ...graph.nodes.map(n => ({ data: { id: n.id, label: n.label, type: n.type } })),
    ...graph.edges.map((e, i) => ({ data: { id: `e${i}`, source: e.source, target: e.target, label: e.label } }))
  ];

  const stylesheet = [
    { selector: 'node', style: { 'label': 'data(label)', 'color': '#9ca3af', 'text-valign': 'bottom', 'text-halign': 'center', 'font-size': '10px', 'font-family': 'monospace', 'text-margin-y': 6 } },
    { selector: 'node[type="wallet"]', style: { 'background-color': '#3b82f6', 'width': 30, 'height': 30, 'border-width': 2, 'border-color': '#2563eb' } },
    { selector: 'node[type="contract"]', style: { 'background-color': '#8b5cf6', 'width': 20, 'height': 20 } },
    { selector: 'node[type="flagged_address"]', style: { 'background-color': '#ef4444', 'width': 35, 'height': 35, 'border-width': 3, 'border-color': '#991b1b' } },
    { selector: 'node[type="risky_contract"]', style: { 'background-color': '#f59e0b', 'width': 25, 'height': 25 } },
    { selector: 'edge', style: { 'width': 1.5, 'line-color': '#374151', 'target-arrow-color': '#374151', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '8px', 'color': '#6b7280', 'text-rotation': 'autorotate', 'text-margin-y': -6 } }
  ];

  const handleTap = (evt) => {
    const node = evt.target;
    if (node.isNode()) {
      const chainInfo = availableChains.find(c => c.id === 'ethereum');
      if (chainInfo) window.open(chainInfo.explorer_addr_url.replace('{a}', node.id()), '_blank');
    }
  };

  return (
    <CytoscapeComponent 
      elements={elements} 
      style={{ width: '100%', height: '100%' }} 
      stylesheet={stylesheet}
      layout={{ name: 'cose', padding: 40, nodeRepulsion: 400000, idealEdgeLength: 100 }}
      cy={(cy) => {
        cy.on('tap', 'node', handleTap);
        cy.fit();
      }}
    />
  );
}

export default App;
