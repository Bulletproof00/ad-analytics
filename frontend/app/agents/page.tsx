'use client';

import { useEffect, useState } from 'react';

interface AgentRun {
  id: string;
  agent_name: string;
  status: string;
  created_at: string;
}

export default function AgentsPage() {
  const [runs, setRuns] = useState<AgentRun[]>([]);
  const [agentName, setAgentName] = useState('market_pattern');

  const load = async () => {
    const res = await fetch('/api/backend/api/agents');
    const data = await res.json();
    setRuns(data.items || []);
  };

  const runAgent = async () => {
    await fetch('/api/backend/api/agents/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ agent_name: agentName, params: {} }),
    });
    load();
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Agenten Center</h1>
        <p className="page-subtitle">Regelbasierte Reports und Outputs für Entscheidungen.</p>
      </div>
      <div className="card">
        <h2 className="section-title">Agent ausführen</h2>
        <select className="select" value={agentName} onChange={(e) => setAgentName(e.target.value)}>
          <option value="market_pattern">Markt-Muster</option>
          <option value="hook_generator">Hook Generator</option>
          <option value="winner_prediction">Winner Prognose</option>
          <option value="strategy_budget">Strategie & Budget</option>
          <option value="explainability">Erklärbarkeit</option>
          <option value="market_saturation">Marktsättigung</option>
          <option value="differentiation">Differenzierung</option>
        </select>
        <button className="button" style={{ marginTop: 12 }} onClick={runAgent}>Agent starten</button>
      </div>
      <div className="card">
        <h2 className="section-title">Letzte Agenten-Runs</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Status</th>
              <th>Erstellt</th>
            </tr>
          </thead>
          <tbody>
            {runs.map((run) => (
              <tr key={run.id}>
                <td>{run.agent_name}</td>
                <td>{run.status}</td>
                <td>{new Date(run.created_at).toLocaleString()}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
