'use client';

import { useEffect, useState } from 'react';

interface ScanState {
  state: string;
  keywords_total: number;
  keywords_done: number;
  ads_upserted: number;
  pages_discovered: number;
  errors: string[];
}

export default function ScanPage() {
  const [keywords, setKeywords] = useState('');
  const [sinceDays, setSinceDays] = useState(90);
  const [status, setStatus] = useState('ALL');
  const [scanId, setScanId] = useState<string | null>(null);
  const [scanState, setScanState] = useState<ScanState | null>(null);

  useEffect(() => {
    if (!scanId) return;
    const interval = setInterval(async () => {
      const res = await fetch(`/api/backend/api/scan/${scanId}`);
      const data = await res.json();
      setScanState(data);
      if (data.state !== 'running') {
        clearInterval(interval);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, [scanId]);

  const startScan = async () => {
    const payload = {
      keywords: keywords.split('\n').map((k) => k.trim()).filter(Boolean),
      country: 'DE',
      since_days: sinceDays,
      status,
      max_results_per_keyword: 2000,
    };
    const res = await fetch('/api/backend/api/scan', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    setScanId(data.scan_id);
  };

  return (
    <div className="grid">
      <h1>Neuer Scan</h1>
      <div className="card">
        <label>Keywords (1 pro Zeile)</label>
        <textarea
          className="textarea"
          rows={8}
          value={keywords}
          onChange={(e) => setKeywords(e.target.value)}
        />
        <div className="filters" style={{ marginTop: 12 }}>
          <div>
            <label>Since Days</label>
            <select className="select" value={sinceDays} onChange={(e) => setSinceDays(Number(e.target.value))}>
              <option value={30}>30</option>
              <option value={90}>90</option>
              <option value={365}>365</option>
            </select>
          </div>
          <div>
            <label>Status</label>
            <select className="select" value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="ALL">ALL</option>
              <option value="ACTIVE">ACTIVE</option>
              <option value="INACTIVE">INACTIVE</option>
            </select>
          </div>
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={startScan}>
          Scan starten
        </button>
      </div>

      {scanState && (
        <div className="card">
          <h2>Scan Status</h2>
          <p>Status: {scanState.state}</p>
          <p>Keywords: {scanState.keywords_done} / {scanState.keywords_total}</p>
          <p>Ads upserted: {scanState.ads_upserted}</p>
          <p>Pages discovered: {scanState.pages_discovered}</p>
          {scanState.errors.length > 0 && (
            <div>
              <h4>Errors</h4>
              <ul>
                {scanState.errors.map((err) => (
                  <li key={err}>{err}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
