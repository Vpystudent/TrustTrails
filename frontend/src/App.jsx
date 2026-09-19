import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import CytoscapeComponent from 'react-cytoscapejs';
import { Shield, AlertTriangle, CheckCircle, Info, Copy, ExternalLink, ChevronDown, ChevronUp, Activity, Search, RefreshCw, Zap, Code, FileJson, Clock, BookOpen } from 'lucide-react';
import { demoAddresses } from './demoAddresses';
import './index.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

function App() {
  const [address, setAddress] = useState('');
  const [chains, setChains] = useState(['ethereum']);
  const [availableChains, setAvailableChains] = useState([]);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('all');
  const [showDevPanel, setShowDevPanel] = useState(false);
  const [showMethodology, setShowMethodology] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const chainsParam = params.get('chains');
    if (chainsParam) {
      setChains(chainsParam.split(','));
    }
  }, []);

  const updateUrlChains = (newChains) => {
    setChains(newChains);
    const url = new URL(window.location);
    if (newChains.length > 0) {
      url.searchParams.set('chains', newChains.join(','));
    } else {
      url.searchParams.delete('chains');
    }
    window.history.pushState({}, '', url);
  };

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
    <div className="min-h-screen bg-[#050505] text-gray-200 font-sans selection:bg-indigo-500/30 flex flex-col">
      <nav className="border-b border-white/5 bg-black/40 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/logo.png" alt="TrustTrail Logo" className="h-10 w-10 rounded-xl invert opacity-90 shadow-[0_0_15px_rgba(255,255,255,0.1)]" />
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">TrustTrail <span className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 text-[10px] tracking-widest uppercase border border-indigo-500/20">Beta</span></h1>
              <p className="text-xs text-gray-500 tracking-wide">Every risk flag comes with proof.</p>
            </div>
          </div>
          <button onClick={() => setShowDevPanel(true)} className="flex items-center gap-2 text-sm text-gray-400 hover:text-white transition-colors bg-white/5 hover:bg-white/10 px-3 py-1.5 rounded-lg border border-white/10">
            <Code size={16} /> API
          </button>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-6 py-10 space-y-8 flex-1 w-full">
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
                disabled={loading || !address || chains.length === 0}
                className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-gray-800 disabled:text-gray-500 text-white px-8 py-4 rounded-xl font-semibold transition-all flex items-center justify-center gap-2 min-w-[160px]"
              >
                {loading ? <RefreshCw className="animate-spin" size={20}/> : <Zap size={20}/>}
                {loading ? 'Scanning...' : 'Analyze'}
              </button>
            </div>
            
            <div className="mt-6 flex flex-col md:flex-row items-start md:items-center justify-between gap-4 border-t border-white/5 pt-4">
              <div className="flex flex-wrap items-center gap-3">
                <span className="text-xs text-gray-500 font-medium uppercase tracking-wider">Networks:</span>
                {availableChains.map(c => {
                  const isSelected = chains.includes(c.id);
                  return (
                    <button 
                      key={c.id} 
                      onClick={() => updateUrlChains(isSelected ? chains.filter(x => x !== c.id) : [...chains, c.id])}
                      className={`text-xs px-3 py-1.5 rounded-full border transition-colors flex items-center gap-1.5 ${isSelected ? 'bg-indigo-500/20 text-indigo-300 border-indigo-500/50' : 'bg-white/5 text-gray-400 border-white/10 hover:bg-white/10'}`}
                    >
                      {isSelected && <CheckCircle size={12} />} {c.name}
                    </button>
                  );
                })}
              </div>

              <div className="flex flex-wrap gap-2 items-center">
                <span className="text-xs text-gray-500 font-medium uppercase tracking-wider mr-1">Demo:</span>
                {demoAddresses.map((d, i) => (
                  <div key={i} className="group relative">
                    <button onClick={() => { setAddress(d.address); updateUrlChains(d.chains); fetchReport(d.address, d.chains); }}
                      className="text-xs bg-white/5 hover:bg-white/10 border border-white/10 px-3 py-1.5 rounded-lg transition-colors text-gray-300 hover:text-white flex items-center gap-1.5"
                    >
                      <Activity size={12}/> {d.label} {d.source === 'Sample data' && <span className="ml-1 px-1 bg-amber-500/20 text-amber-500 text-[9px] uppercase rounded">Sample data</span>}
                    </button>
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max px-2 py-1 bg-black border border-white/10 text-gray-300 text-[10px] rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50">
                      Source: {d.source}
                    </div>
                  </div>
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

        {!report && !loading && !error && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-10">
            <div className="bg-[#111] p-6 rounded-2xl border border-white/5">
              <Search className="text-indigo-400 mb-4" size={24} />
              <h3 className="text-white font-bold mb-2">Paste an address</h3>
              <p className="text-sm text-gray-400">Enter any wallet or contract address above. We support Ethereum and Base.</p>
            </div>
            <div className="bg-[#111] p-6 rounded-2xl border border-white/5">
              <Shield className="text-emerald-400 mb-4" size={24} />
              <h3 className="text-white font-bold mb-2">We check the history</h3>
              <p className="text-sm text-gray-400">We analyze token approvals, counterparties, contract bytecode, and interaction graphs.</p>
            </div>
            <div className="bg-[#111] p-6 rounded-2xl border border-white/5">
              <BookOpen className="text-purple-400 mb-4" size={24} />
              <h3 className="text-white font-bold mb-2">Evidence-based</h3>
              <p className="text-sm text-gray-400">Every risk flag links directly to on-chain proof. <button onClick={() => setShowMethodology(true)} className="text-indigo-400 hover:underline">Read methodology</button></p>
            </div>
          </div>
        )}

        {report && !loading && (() => {
          const totalTxs = Object.values(report.coverage.chains).reduce((a, b) => a + b.transactions + b.token_transfers, 0);
          const flaggedSignal = report.signals.find(s => s.signal_id === "flagged_address");
          if (flaggedSignal && totalTxs === 0) {
            return (
              <div className="bg-[#0a0a0a] border border-red-500/20 p-8 rounded-2xl flex flex-col items-center text-center max-w-2xl mx-auto shadow-2xl mt-10">
                <Shield size={48} className="text-red-500 mb-6" />
                <h2 className="text-2xl font-bold text-white mb-4">Listed by ScamSniffer. No transactions found on the selected chains.</h2>
                <p className="text-gray-400 mb-8 max-w-md">This address has been flagged in a threat intelligence database, but it has no on-chain activity on the networks you selected.</p>
                <div className="flex gap-4">
                  <button onClick={() => { updateUrlChains(['ethereum', 'base', 'arbitrum']); fetchReport(address, ['ethereum', 'base', 'arbitrum']); }} className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-3 rounded-xl font-semibold transition-colors">Check other chains</button>
                  <button onClick={() => setShowMethodology(true)} className="bg-white/5 hover:bg-white/10 text-white border border-white/10 px-6 py-3 rounded-xl font-semibold transition-colors">Why this matters</button>
                </div>
              </div>
            );
          }
          return (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-700">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-[#111] border border-white/5 rounded-2xl p-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 blur-[80px] rounded-full pointer-events-none"></div>
                
                <div className="flex flex-col sm:flex-row items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-3 mb-2">
                      <h2 className="text-2xl font-bold text-white">Trust Report</h2>
                      {report.cache?.hit && <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs px-2 py-0.5 rounded-full flex items-center gap-1"><Zap size={10}/> Cached</span>}
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <div className="flex items-center gap-2 bg-black/50 px-3 py-1.5 rounded-lg border border-white/5 w-fit">
                        <span className="font-mono text-sm text-gray-300">{report.address}</span>
                        <button onClick={() => navigator.clipboard.writeText(report.address)} className="text-gray-500 hover:text-white transition-colors" aria-label="Copy address">
                          <Copy size={14}/>
                        </button>
                      </div>
                      <span className="bg-white/5 border border-white/10 text-gray-400 text-xs px-2 py-1 rounded-md uppercase tracking-wider">{report.address_type}</span>
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
                    <AlertTriangle size={16} className="text-amber-500 shrink-0"/>
                    <span><strong>Warnings:</strong> {report.warnings.map(w => w.message).join(', ')} (API sync issues)</span>
                  </div>
                )}
                
                {report.coverage && <CoverageStrip coverage={report.coverage} overallRisk={report.overall_risk} />}
              </div>

              <div className="bg-gradient-to-br from-[#16161a] to-[#0a0a0c] border border-white/5 rounded-2xl p-6 flex flex-col">
                <div className="flex items-center gap-2 mb-4">
                  <div className="w-6 h-6 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                    <Zap size={14} className="text-indigo-400"/>
                  </div>
                  <h3 className="text-white font-bold">Analysis Summary</h3>
                </div>
                <p className="text-gray-400 text-sm leading-relaxed flex-1">
                  {report.summary || "No risk signals found by these checks. Not a guarantee of safety. New or low-activity addresses can look clean."}
                </p>
                <div className="mt-4 pt-4 border-t border-white/5 text-[10px] text-gray-500 uppercase tracking-widest">
                  Not a guarantee of safety. New or low-activity addresses can look clean.
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 bg-[#111] border border-white/5 rounded-2xl overflow-hidden flex flex-col h-[500px]">
                <div className="px-6 py-4 border-b border-white/5 bg-black/20 flex justify-between items-center">
                  <h3 className="text-white font-bold flex items-center gap-2">
                    <Activity size={16} className="text-indigo-400"/>
                    Interaction Graph
                  </h3>
                  <div className="flex items-center gap-3 text-xs font-medium text-gray-500">
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full border-2 border-indigo-500 bg-blue-500"></div> Target</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-red-500"></div> Flagged</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-purple-500"></div> Contract</span>
                  </div>
                </div>
                <div className="flex-1 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-black/40 relative">
                  <EvidenceGraph graph={report.graph} availableChains={availableChains} risk={report.overall_risk} />
                </div>
              </div>

              <div className="bg-[#111] border border-white/5 rounded-2xl flex flex-col h-[500px]">
                <div className="px-6 py-4 border-b border-white/5 bg-black/20">
                  <h3 className="text-white font-bold flex items-center gap-2">
                    <Shield size={16} className="text-emerald-400"/>
                    Score Breakdown
                  </h3>
                </div>
                <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
                  {report.points.length === 0 ? (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500 text-sm space-y-2 text-center">
                      <CheckCircle size={32} className="text-gray-600 mb-2"/>
                      <p>No risk signals found by these checks.</p>
                      <p className="text-xs text-gray-600">Not a guarantee of safety.</p>
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
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-[#111] border border-white/5 rounded-2xl p-6">
                <h3 className="text-white font-bold flex items-center gap-2 mb-4">
                  <Clock size={16} className="text-blue-400"/>
                  Activity Timeline
                </h3>
                <ActivityTimeline timeline={report.timeline} />
              </div>
              <div className="bg-[#111] border border-white/5 rounded-2xl p-6 flex flex-col">
                <h3 className="text-white font-bold flex items-center gap-2 mb-4">
                  <Shield size={16} className="text-purple-400"/>
                  Active Approvals
                </h3>
                <ApprovalsTable approvals={report.approvals} address={report.address} />
              </div>
            </div>

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
                    <CheckCircle size={48} className="text-gray-600 mb-4"/>
                    <h3 className="text-xl font-bold text-white mb-2">No Risk Signals Found</h3>
                    <p className="text-gray-500 text-center max-w-md">No risk signals found by these checks. Not a guarantee of safety. New or low-activity addresses can look clean.</p>
                  </div>
                ) : (
                  filteredSignals.map((sig, i) => <SignalCard key={i} signal={sig} getChainUrl={getChainUrl} />)
                )}
              </div>
            </div>

          </div>
          );
        })()}
      </main>

      <footer className="border-t border-white/5 bg-black mt-12 py-8">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-gray-500">
          <div className="flex items-center gap-2">
            <img src="/logo.png" alt="TrustTrail Logo" className="h-6 w-6 invert opacity-50" />
            <span>TrustTrail</span>
          </div>
          <div className="flex gap-4">
            <span>Sources: Etherscan, Blockscout, public RPC, ScamSniffer</span>
            {report && <span>• Report generated: {new Date(report.generated_at).toLocaleString()}</span>}
          </div>
          <div className="text-xs max-w-sm text-center md:text-right">
            Disclaimer: Information is for advisory purposes only. Not financial or security advice.
          </div>
        </div>
      </footer>

      {showDevPanel && <DevPanel report={report} onClose={() => setShowDevPanel(false)} />}
      {showMethodology && <MethodologyPanel onClose={() => setShowMethodology(false)} />}
    </div>
  );
}

function CoverageStrip({ coverage, overallRisk }) {
  let totalTxs = 0;
  let truncated = false;
  let providerWarning = false;
  let firstSeen = null;
  let lastSeen = null;

  Object.values(coverage.chains).forEach(c => {
    totalTxs += c.transactions;
    if (c.truncated) truncated = true;
    if (!c.ok) providerWarning = true;
    if (c.first_seen && (!firstSeen || new Date(c.first_seen) < new Date(firstSeen))) firstSeen = c.first_seen;
    if (c.last_seen && (!lastSeen || new Date(c.last_seen) > new Date(lastSeen))) lastSeen = c.last_seen;
  });

  let confLevel = "Medium";
  if (totalTxs < 10 || providerWarning) confLevel = "Low";
  else if (totalTxs >= 100 && !truncated && !providerWarning) confLevel = "High";

  const confColor = confLevel === "High" ? "text-emerald-400" : confLevel === "Low" ? "text-amber-400" : "text-blue-400";

  return (
    <div className="mt-6 border-t border-white/10 pt-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Txs Analyzed</div>
        <div className="text-white font-mono">{totalTxs} {truncated && '+'}</div>
      </div>
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Activity</div>
        <div className="text-white text-xs">{firstSeen ? new Date(firstSeen).getFullYear() : 'N/A'} - {lastSeen ? new Date(lastSeen).getFullYear() : 'N/A'}</div>
      </div>
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Confidence</div>
        <div className={`font-bold flex items-center gap-1 ${confColor} group relative`}>
          {confLevel} <Info size={12} className="text-gray-500 cursor-help" />
          <div className="absolute bottom-full left-0 mb-2 w-48 px-3 py-2 bg-black border border-white/10 text-gray-300 text-[10px] rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
            Confidence is Low if &lt;10 txs or API errors. High if full history (&ge;100). Not a risk probability.
          </div>
        </div>
      </div>
      <div>
        <div className="text-xs text-gray-500 uppercase tracking-widest mb-1">Status</div>
        <div className="flex gap-2">
          {Object.entries(coverage.chains).map(([ch, data]) => (
            <span key={ch} className={`text-xs px-2 py-0.5 rounded border ${data.ok ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-400' : 'bg-red-500/10 border-red-500/20 text-red-400'}`}>
              {ch}: {data.ok ? 'OK' : 'ERR'}
            </span>
          ))}
        </div>
      </div>
      {totalTxs < 10 && overallRisk === "low" && (
        <div className="col-span-full mt-2 text-xs bg-amber-500/10 text-amber-300 border border-amber-500/20 px-3 py-2 rounded-lg">
          Limited history: a clean result here has low confidence.
        </div>
      )}
    </div>
  );
}

function ApprovalsTable({ approvals, address }) {
  if (!approvals || approvals.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-gray-500 text-sm h-full py-8 border border-white/5 rounded-xl border-dashed">
        <p>No active approvals found in the history we analysed.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      <div className="overflow-x-auto flex-1 border border-white/5 rounded-xl">
        <table className="w-full text-left text-sm">
          <thead className="bg-white/5 text-gray-400 text-xs uppercase">
            <tr>
              <th className="px-4 py-2 font-medium">Chain</th>
              <th className="px-4 py-2 font-medium">Spender</th>
              <th className="px-4 py-2 font-medium">Amount</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {approvals.map((app, i) => (
              <tr key={i} className="hover:bg-white/[0.02]">
                <td className="px-4 py-3 capitalize text-gray-300">{app.chain}</td>
                <td className="px-4 py-3 font-mono text-xs text-gray-400">{app.spender.slice(0,6)}...{app.spender.slice(-4)}</td>
                <td className="px-4 py-3">
                  {app.amount === 'unlimited' ? (
                    <span className="bg-red-500/10 text-red-400 border border-red-500/20 px-2 py-0.5 rounded text-xs">Unlimited</span>
                  ) : (
                    <span className="text-gray-400 text-xs">Limited</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <a href={`https://revoke.cash/address/${address}`} target="_blank" rel="noreferrer" className="mt-4 w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-center text-sm text-gray-300 transition-colors flex items-center justify-center gap-2">
        Review on revoke.cash <ExternalLink size={14} />
      </a>
    </div>
  );
}

function ActivityTimeline({ timeline }) {
  if (!timeline || timeline.length === 0) return <div className="text-sm text-gray-500 p-4 text-center">No timeline data available.</div>;
  
  return (
    <div className="space-y-4 max-h-[300px] overflow-y-auto custom-scrollbar pr-2">
      {timeline.map((month, i) => (
        <div key={i} className="flex gap-4 items-start">
          <div className="w-16 text-xs text-gray-500 pt-1 shrink-0">{month.month}</div>
          <div className="flex-1 relative pb-4 border-l border-white/10 pl-4">
            <div className="absolute w-2 h-2 rounded-full bg-indigo-500/50 -left-[4px] top-2"></div>
            <div className="text-sm text-gray-300">{month.transactions} transactions</div>
            {month.events.length > 0 && (
              <div className="mt-2 space-y-2">
                {month.events.map((ev, j) => (
                  <div key={j} className="text-xs bg-white/5 border border-white/10 rounded px-2 py-1 flex items-center justify-between">
                    <span className="text-gray-400">{ev.type.replace(/_/g, ' ')}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function SignalCard({ signal, getChainUrl }) {
  const [expanded, setExpanded] = useState(false);
  
  const sevColor = signal.severity === 'high' ? 'red' : signal.severity === 'medium' ? 'amber' : 'blue';

  return (
    <div className={`rounded-2xl border bg-[#111] overflow-hidden transition-all hover:border-${sevColor}-500/50`} style={{borderColor: `var(--color-${sevColor}-500, rgba(255,255,255,0.1))`}}>
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

function EvidenceGraph({ graph, availableChains, risk }) {
  if (!graph || !graph.nodes || graph.nodes.length === 0) {
    return (
      <div className="absolute inset-0 flex items-center justify-center p-6">
        <div className="bg-[#1a1a1a] border border-white/10 rounded-xl p-6 text-center max-w-sm shadow-xl">
          <Activity size={32} className="text-gray-600 mx-auto mb-4" />
          <h4 className="text-white font-bold mb-2">No data to display</h4>
          <p className="text-sm text-gray-400">There are no nodes to render in the graph.</p>
        </div>
      </div>
    );
  }
  
  const riskColor = risk === 'high' ? '#ef4444' : risk === 'medium' ? '#f59e0b' : '#10b981';

  const elements = [
    ...graph.nodes.map(n => ({ data: { id: n.id, label: n.label, type: n.type } })),
    ...graph.edges.map((e, i) => ({ data: { id: `e${i}`, source: e.source, target: e.target, label: e.label } }))
  ];

  const stylesheet = [
    { selector: 'node', style: { 'label': 'data(label)', 'color': '#9ca3af', 'text-valign': 'bottom', 'text-halign': 'center', 'font-size': '11px', 'font-family': 'monospace', 'text-margin-y': 6, 'width': 28, 'height': 28 } },
    { selector: 'node[type="wallet"]', style: { 'background-color': '#3b82f6' } },
    { selector: 'node[type="contract"]', style: { 'background-color': '#8b5cf6' } },
    { selector: 'node[type="flagged_address"]', style: { 'background-color': '#ef4444' } },
    { selector: 'node[type="risky_contract"]', style: { 'background-color': '#f59e0b' } },
    { selector: 'node[type="target"]', style: { 'background-color': '#3b82f6', 'border-width': 3, 'border-color': riskColor } },
    { selector: 'edge', style: { 'width': 1.5, 'line-color': '#374151', 'target-arrow-color': '#374151', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '9px', 'color': '#6b7280', 'text-rotation': 'autorotate', 'text-margin-y': -6 } }
  ];

  return (
    <CytoscapeComponent 
      elements={elements} 
      style={{ width: '100%', height: '100%' }} 
      stylesheet={stylesheet}
      minZoom={0.5}
      maxZoom={1.5}
      layout={{ name: 'cose', padding: 40, nodeRepulsion: 400000, idealEdgeLength: 100 }}
      cy={(cy) => {
        cy.fit();
      }}
    />
  );
}

function DevPanel({ report, onClose }) {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-6">
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-2xl shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2"><Code size={20} className="text-indigo-400"/> Use the API</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white">✕</button>
        </div>
        
        <p className="text-sm text-gray-400 mb-4">Integrate TrustTrail directly into your dApp or backend.</p>
        
        <div className="bg-black border border-white/10 p-4 rounded-xl font-mono text-xs text-gray-300 mb-6 overflow-x-auto">
          curl -X GET "{API_URL}/report?address=0x...&chains=ethereum,base" -H "accept: application/json"
        </div>
        
        <div className="flex flex-wrap gap-4">
          <a href={`${API_URL}/docs`} target="_blank" rel="noreferrer" className="bg-indigo-600 hover:bg-indigo-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            View Swagger Docs
          </a>
          {report && (
            <>
              <button onClick={() => navigator.clipboard.writeText(JSON.stringify(report, null, 2))} className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                <Copy size={16}/> Copy JSON
              </button>
              <button onClick={() => {
                const blob = new Blob([JSON.stringify(report, null, 2)], {type: "application/json"});
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `report_${report.address}.json`;
                a.click();
              }} className="bg-white/5 hover:bg-white/10 border border-white/10 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                <FileJson size={16}/> Download report.json
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function MethodologyPanel({ onClose }) {
  return (
    <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-[100] flex items-center justify-center p-6">
      <div className="bg-[#111] border border-white/10 rounded-2xl p-6 w-full max-w-2xl shadow-2xl">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white flex items-center gap-2"><BookOpen size={20} className="text-purple-400"/> How we score</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-white">✕</button>
        </div>
        <div className="space-y-4 text-sm text-gray-300">
          <p>Our scoring algorithm relies purely on deterministic on-chain data and trusted threat-intel lists. We do not use AI to generate the score.</p>
          <ul className="list-disc pl-5 space-y-2">
            <li><strong>Direct Match:</strong> If the address itself appears on a known-scam list, it immediately triggers a high risk score.</li>
            <li><strong>Approvals:</strong> We check for unlimited token approvals (`max uint256`) and verify if the spender is an unverified proxy or known scam.</li>
            <li><strong>Counterparties:</strong> Every incoming and outgoing transaction is cross-referenced against ScamSniffer's database.</li>
            <li><strong>Contract Code:</strong> If the target is a contract, we check EIP-1967 storage slots to detect hidden upgradeability, and scan the ABI for risky functions (e.g., `blacklist`, `setTax`).</li>
          </ul>
          <p className="pt-2 text-xs text-gray-500">Note: Even if an address scores 0/100, it is not a guarantee of safety. Zero-history addresses will naturally lack risk signals.</p>
        </div>
      </div>
    </div>
  );
}

export default App;