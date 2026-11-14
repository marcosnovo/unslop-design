export function Home() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <div className="rounded-xl border bg-card p-4"><p className="text-sm">Revenue</p><p className="text-2xl font-semibold">$12,400</p></div>
      <div className="rounded-xl border bg-card p-4"><p className="text-sm">Users</p><p className="text-2xl font-semibold">1,284</p></div>
      <div className="rounded-xl border bg-card p-4"><p className="text-sm">Churn</p><p className="text-2xl font-semibold">2.1%</p></div>
      <div className="rounded-xl border bg-card p-4"><p className="text-sm">MRR</p><p className="text-2xl font-semibold">$4,100</p></div>
    </div>
  );
}
