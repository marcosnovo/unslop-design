export function Home({ stats }) {
  return <div className="grid grid-cols-2 gap-4">{stats.map(s => (
    <div key={s.id} className="rounded-xl border bg-card p-4"><p className="text-2xl">{s.value}</p></div>))}</div>;
}
