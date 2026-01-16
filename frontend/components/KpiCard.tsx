export default function KpiCard({ title, value, delta }: { title: string; value: string | number; delta?: string }) {
  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <p style={{ color: '#6b7280', margin: 0 }}>{title}</p>
          <h3 style={{ margin: '6px 0' }}>{value}</h3>
        </div>
        {delta && <span className="badge">{delta}</span>}
      </div>
    </div>
  );
}
