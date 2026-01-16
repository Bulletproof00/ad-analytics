'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import CopyButton from '../../components/CopyButton';
import { HookItem } from '../../lib/types';

export default function HooksPage() {
  const [hooks, setHooks] = useState<HookItem[]>([]);
  const [compare, setCompare] = useState<string[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await fetch('/api/backend/api/hooks', { cache: 'no-store' });
      const data = await res.json();
      setHooks(data.items || []);
    };
    load();
  }, []);

  const toggleCompare = (id: string) => {
    setCompare((prev) => (prev.includes(id) ? prev.filter((item) => item !== id) : [...prev, id]));
  };

  const compareHooks = hooks.filter((hook) => compare.includes(hook.id));

  return (
    <div className="grid">
      <div>
        <h1 className="page-title">Hook Library</h1>
        <p className="page-subtitle">Die stärksten Einstiege und ihre Wiederverwendung.</p>
      </div>
      {compareHooks.length > 0 && (
        <div className="card">
          <h2 className="section-title">Hook Vergleich</h2>
          <ul>
            {compareHooks.map((hook) => (
              <li key={hook.id}>
                <strong>{hook.hook_text}</strong> — Reuse {hook.reuse_count}
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="card">
        <h2 className="section-title">Alle Hooks</h2>
        <table className="table">
          <thead>
            <tr>
              <th>Hook</th>
              <th>Reuse</th>
              <th>Beispiele</th>
              <th>Kopie</th>
              <th>Vergleich</th>
            </tr>
          </thead>
          <tbody>
            {hooks.map((hook) => (
              <tr key={hook.id}>
                <td>{hook.hook_text}</td>
                <td>{hook.reuse_count}</td>
                <td>
                  {hook.example_ad_ids.map((id) => (
                    <Link key={id} href={`/ads/${id}`} style={{ marginRight: 8 }}>
                      {id.slice(0, 6)}
                    </Link>
                  ))}
                </td>
                <td>
                  <CopyButton text={hook.hook_text} />
                </td>
                <td>
                  <input type="checkbox" checked={compare.includes(hook.id)} onChange={() => toggleCompare(hook.id)} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
