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
      <h1>Agents Center</h1>
      <div className="card">
        <h2>Run Agent</h2>
        <select className="select" value={agentName} onChange={(e) => setAgentName(e.target.value)}>
          <option value="market_pattern">Market Pattern</option>
          <option value="hook_generator">Hook Generator</option>
          <option value="winner_prediction">Winner Prediction</option>
          <option value="strategy_budget">Strategy & Budget</option>
          <option value="explainability">Explainability</option>
          <option value="market_saturation">Market Saturation</option>
          <option value="differentiation">Differentiation</option>
        </select>
        <button className="button" style={{ marginTop: 12 }} onClick={runAgent}>Run Agent</button>
      </div>
      <div className="card">
        <h2>Agent Runs</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Agent</th>
              <th>Status</th>
              <th>Created</th>
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
