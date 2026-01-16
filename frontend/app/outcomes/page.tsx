'use client';

import { useEffect, useState } from 'react';

export default function OutcomesPage() {
  const [items, setItems] = useState<any[]>([]);
  const [form, setForm] = useState({ blueprint_id: '', ad_id: '', leads_count: 0, cpl: 0, notes: '' });

  const load = async () => {
    const res = await fetch('/api/backend/api/outcomes');
    const data = await res.json();
    setItems(data.items || []);
  };

  const submit = async () => {
    await fetch('/api/backend/api/outcomes', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    setForm({ blueprint_id: '', ad_id: '', leads_count: 0, cpl: 0, notes: '' });
    load();
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="grid">
      <h1>Outcome Feedback</h1>
      <div className="card">
        <div className="filters">
          <input className="input" placeholder="Blueprint ID" value={form.blueprint_id} onChange={(e) => setForm({ ...form, blueprint_id: e.target.value })} />
          <input className="input" placeholder="Ad ID" value={form.ad_id} onChange={(e) => setForm({ ...form, ad_id: e.target.value })} />
          <input className="input" type="number" placeholder="Leads" value={form.leads_count} onChange={(e) => setForm({ ...form, leads_count: Number(e.target.value) })} />
          <input className="input" type="number" placeholder="CPL" value={form.cpl} onChange={(e) => setForm({ ...form, cpl: Number(e.target.value) })} />
          <input className="input" placeholder="Notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
        <button className="button" style={{ marginTop: 12 }} onClick={submit}>Save Outcome</button>
      </div>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Blueprint</th>
              <th>Ad</th>
              <th>Leads</th>
              <th>CPL</th>
              <th>Notes</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id}>
                <td>{item.blueprint_id}</td>
                <td>{item.ad_id}</td>
                <td>{item.leads_count}</td>
                <td>{item.cpl}</td>
                <td>{item.notes}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
