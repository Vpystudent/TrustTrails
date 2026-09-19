import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import CytoscapeComponent from 'react-cytoscapejs';
import { Shield, AlertTriangle, CheckCircle, Info, Copy, ExternalLink, ChevronDown, ChevronUp } from 'lucide-react';
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
      console.warn("Could not fetch chains from backend", err);
      // Fallback
      setAvailableChains([
        {id: 'ethereum', name: 'Ethereum', explorer_tx_url: 'https://etherscan.io/tx/{h}', explorer_addr_url: 'https://etherscan.io/address/{a}'},
        {id: 'base', name: 'Base', explorer_tx_url: 'https://basescan.org/tx/{h}', explorer_addr_url: 'https://basescan.org/address/{a}'}
      ]);
    });
  }, []);

  const fetchReport = async (addr, chs) => {
    setLoading(true);
    setError(null);
    setReport(null);
    try {
      const res = await axios.get(`${API_URL}/report`, {
        params: { address: addr, chains: chs.join(',') }
      });
      setReport(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDemo = (demo) => {
    setAddress(demo.address);
    setChains(demo.chains);
    fetchReport(demo.address, demo.chains);
  };

  const handleSample = async () => {
    setLoading(true);
    setError(null);
    try {
      const mockData = await import('../../mock/report.json');
      setReport(mockData.default);
    } catch (err) {
      setError("Could not load sample report");
    } finally {
      setLoading(false);
    }
  };

  const getChainUrl = (chain_id, hash, type='tx') => {
    const chainInfo = availableChains.find(c => c.id === chain_id);
    if (!chainInfo) return '#';
    const tpl = type === 'tx' ? chainInfo.explorer_tx_url : chainInfo.explorer_addr_url;
    if (!tpl) return '#';
    return tpl.replace('{h}', hash).replace('{a}', hash);
  };

  const filteredSignals = report ? (activeTab === 'all' ? report.signals : report.signals.filter(s => s.chain === activeTab)) : [];

  return (
    <div className="container">
      <header className="mb-4 flex items-center gap-4">
        <img src="/logo.png" alt="TrustTrail Logo" style={{ height: '64px', borderRadius: '12px', filter: 'invert(1) opacity(0.9)' }} />
        <div>
          <h1 style={{ marginBottom: 0 }}>TrustTrail</h1>
          <p className="label" style={{ marginTop: '0.25rem' }}>Every risk flag comes with proof.</p>
        </div>
      </header>

      <div className="card">
        <div className="flex items-center gap-4 mb-4">
          <input 
            type="text" 
            placeholder="0x..." 
            value={address} 
            onChange={e => setAddress(e.target.value)}
            style={{marginBottom: 0, flex: 1}}
          />
          <button className="btn btn-primary" onClick={() => fetchReport(address, chains)} disabled={loading}>
            {loading ? 'Analyzing...' : 'Check Address'}
          </button>
        </div>
        
        <div className="flex gap-4 mb-4">
          {availableChains.map(c => (
            <label key={c.id} className="flex items-center gap-2">
              <input 
                type="checkbox" 
                checked={chains.includes(c.id)}
                onChange={(e) => {
                  if (e.target.checked) setChains([...chains, c.id]);
                  else setChains(chains.filter(x => x !== c.id));
                }}
              />
              {c.name}
            </label>
          ))}
        </div>

        <div className="flex gap-2">
          {demoAddresses.map((d, i) => (
            <button key={i} className="btn" onClick={() => handleDemo(d)}>Demo: {d.label}</button>
          ))}
          <button className="btn" onClick={handleSample}>Use sample report</button>
        </div>
      </div>

      {error && (
        <div className="card" style={{borderLeft: '4px solid var(--color-high)'}}>
          <h3>Error</h3>
          <p>{error}</p>
          <button className="btn" onClick={() => fetchReport(address, chains)}>Retry</button>
        </div>
      )}

      {loading && (
        <div className="card">
          <p>Analyzing cross-chain history... This may take up to a minute.</p>
        </div>
      )}

      {report && !loading && (
        <>
          <div className="card">
            <div className="flex justify-between items-center mb-4">
              <div>
                <h2 className="flex items-center gap-2">
                  Address Report 
                  <span className={`badge ${report.overall_risk}`}>Risk: {report.overall_risk}</span>
                </h2>
                <div className="flex items-center gap-2 text-label">
                  {report.address} 
                  <Copy size={14} className="cursor-pointer" onClick={() => navigator.clipboard.writeText(report.address)}/>
                </div>
              </div>
              <div style={{textAlign: 'right'}}>
                <h2>Score: {report.score} / 100</h2>
                <p className="label">Generated: {new Date(report.generated_at).toLocaleString()}</p>
              </div>
            </div>

            {report.cache?.hit && (
              <div className="badge low mb-4" style={{display: 'inline-block'}}>Demo mode: saved report</div>
            )}
            
            {report.history_truncated && (
              <div className="badge medium mb-4" style={{display: 'inline-block', marginLeft: '10px'}}>Warning: History truncated ({'>'}10k records)</div>
            )}
            
            {report.warnings && report.warnings.length > 0 && (
              <div className="badge medium mb-4" style={{display: 'inline-block', marginLeft: '10px'}}>
                Chain Warnings: {report.warnings.map(w => w.chain).join(', ')}
              </div>
            )}

            <div className="flex gap-4">
              <div style={{flex: 1}}>
                <h3>AI explanation</h3>
                <p className="label">narrates the evidence; rules set the score</p>
                <div style={{padding: '1rem', backgroundColor: 'var(--bg-dark)', borderRadius: '4px'}}>
                  {report.summary}
                </div>
              </div>
              <div style={{flex: 1}}>
                <h3>How we scored</h3>
                <ul style={{listStyleType: 'none', padding: 0}}>
                  {report.points.map((pt, i) => (
                    <li key={i} className="mb-2">
                      <strong>+{pt.points}</strong> {pt.signal_id} <br/>
                      <span className="label">{pt.reason}</span>
                    </li>
                  ))}
                  {report.points.length === 0 && <li>No risk points</li>}
                </ul>
              </div>
            </div>
          </div>

          <div className="card">
            <h3>Evidence Graph</h3>
            <div style={{height: '400px', backgroundColor: 'var(--bg-dark)', borderRadius: '4px'}}>
               <EvidenceGraph graph={report.graph} availableChains={availableChains} />
            </div>
          </div>

          <div className="flex gap-2 mb-4">
            <button className={`btn ${activeTab === 'all' ? 'btn-primary' : ''}`} onClick={() => setActiveTab('all')}>All Chains</button>
            {report.chains.map(c => (
              <button key={c} className={`btn ${activeTab === c ? 'btn-primary' : ''}`} onClick={() => setActiveTab(c)}>{c}</button>
            ))}
          </div>

          {filteredSignals.length === 0 ? (
            <div className="card" style={{borderLeft: '4px solid var(--color-low)'}}>
              <h3 className="flex items-center gap-2"><CheckCircle color="var(--color-low)"/> No risk signals found</h3>
              <p>Checks run: Unlimited Approvals, Scam Counterparties, Contract Permissions, Fresh Wallets, Risky Interactions.</p>
            </div>
          ) : (
            filteredSignals.map((sig, i) => <SignalCard key={i} signal={sig} getChainUrl={getChainUrl} />)
          )}
        </>
      )}
    </div>
  );
}

function SignalCard({ signal, getChainUrl }) {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className={`card border-${signal.severity}`}>
      <div className="flex justify-between items-center mb-2">
        <h3 style={{margin: 0}}>{signal.title}</h3>
        <span className={`badge ${signal.severity}`}>{signal.severity} ({signal.chain})</span>
      </div>
      <p className="label" style={{textTransform: 'none'}}>{signal.rule}</p>
      
      <div className="mt-4">
        <h4>Evidence</h4>
        <ul style={{listStyleType: 'none', padding: 0}}>
          {(expanded ? signal.evidence : signal.evidence.slice(0, 3)).map((ev, i) => (
            <li key={i} className="mb-2" style={{backgroundColor: 'var(--bg-dark)', padding: '0.5rem', borderRadius: '4px'}}>
              <div>{ev.detail}</div>
              {ev.tx_hash && (
                <a href={getChainUrl(signal.chain, ev.tx_hash, 'tx')} target="_blank" rel="noreferrer" className="flex items-center gap-1" style={{color: 'var(--color-medium)', textDecoration: 'none', fontSize: '0.9rem', marginTop: '0.25rem'}}>
                  <ExternalLink size={14}/> View Transaction (Block {ev.block})
                </a>
              )}
            </li>
          ))}
        </ul>
        {signal.evidence.length > 3 && (
          <button className="btn" onClick={() => setExpanded(!expanded)} style={{display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.5rem'}}>
            {expanded ? <><ChevronUp size={16}/> Show less</> : <><ChevronDown size={16}/> Show {signal.evidence.length - 3} more</>}
          </button>
        )}
      </div>
    </div>
  );
}

function EvidenceGraph({ graph, availableChains }) {
  if (!graph || !graph.nodes || graph.nodes.length === 0) return <div style={{padding: '1rem'}}>No graph data.</div>;
  
  const elements = [
    ...graph.nodes.map(n => ({ data: { id: n.id, label: n.label, type: n.type } })),
    ...graph.edges.map((e, i) => ({ data: { id: `e${i}`, source: e.source, target: e.target, label: e.label } }))
  ];

  const stylesheet = [
    { selector: 'node', style: { 'label': 'data(label)', 'color': '#fff', 'text-valign': 'bottom', 'text-halign': 'center', 'font-size': '10px' } },
    { selector: 'node[type="wallet"]', style: { 'background-color': '#3b82f6' } },
    { selector: 'node[type="contract"]', style: { 'background-color': '#8b5cf6' } },
    { selector: 'node[type="flagged_address"]', style: { 'background-color': '#ef4444' } },
    { selector: 'node[type="risky_contract"]', style: { 'background-color': '#f59e0b' } },
    { selector: 'edge', style: { 'width': 2, 'line-color': '#4b5563', 'target-arrow-color': '#4b5563', 'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '8px', 'color': '#a6a6a6', 'text-rotation': 'autorotate' } }
  ];

  const handleTap = (evt) => {
    const node = evt.target;
    if (node.isNode()) {
      const chainInfo = availableChains.find(c => c.id === 'ethereum');
      if (chainInfo) {
        window.open(chainInfo.explorer_addr_url.replace('{a}', node.id()), '_blank');
      }
    }
  };

  return (
    <CytoscapeComponent 
      elements={elements} 
      style={{ width: '100%', height: '100%' }} 
      stylesheet={stylesheet}
      layout={{ name: 'cose', padding: 30 }}
      cy={(cy) => {
        cy.on('tap', 'node', handleTap);
        cy.fit();
      }}
    />
  );
}

export default App;
