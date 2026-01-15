import './globals.css';
import Link from 'next/link';

export const metadata = {
  title: 'AdRadar',
  description: 'Meta Ads Market Memory',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="de">
      <body>
        <header className="card" style={{ margin: 24 }}>
          <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
            <strong>AdRadar</strong>
            <nav style={{ display: 'flex', gap: 12 }}>
              <Link href="/dashboard">Dashboard</Link>
              <Link href="/scan">Scan</Link>
              <Link href="/ads">Ads</Link>
              <Link href="/hooks">Hooks</Link>
              <Link href="/funnels">Funnels</Link>
              <Link href="/analytics">Analytics</Link>
              <Link href="/agents">Agents</Link>
              <Link href="/test-queue">Test Queue</Link>
              <Link href="/export">Export</Link>
              <Link href="/integrations">Integrations</Link>
              <Link href="/settings">Settings</Link>
            </nav>
          </div>
        </header>
        <main>{children}</main>
      </body>
    </html>
  );
}
