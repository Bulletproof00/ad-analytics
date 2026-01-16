import Link from 'next/link';

export default function Home() {
  return (
    <div className="card">
      <h1>AdRadar</h1>
      <p>Willkommen im AdRadar MVP.</p>
      <Link href="/dashboard">Zum Dashboard</Link>
    </div>
  );
}
