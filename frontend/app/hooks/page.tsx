'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import CopyButton from '../../components/CopyButton';
import { HookItem } from '../../lib/types';

export default function HooksPage() {
  const [hooks, setHooks] = useState<HookItem[]>([]);

  useEffect(() => {
    const load = async () => {
      const res = await fetch('/api/backend/api/hooks', { cache: 'no-store' });
      const data = await res.json();
      setHooks(data.items || []);
    };
    load();
  }, []);

  return (
    <div className="grid">
      <h1>Hooks</h1>
      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Hook</th>
              <th>Reuse</th>
              <th>Beispiele</th>
              <th>Copy</th>
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
