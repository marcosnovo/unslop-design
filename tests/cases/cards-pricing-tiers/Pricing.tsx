export function Pricing() {
  return (
    <div className="grid grid-cols-3 gap-6">
      <div className="rounded-2xl border bg-white p-8"><h3>Free</h3><p className="text-4xl">$0</p><button>Start free</button></div>
      <div className="rounded-2xl border bg-white p-8"><h3>Pro</h3><p className="text-4xl">$12</p><button>Choose Pro</button></div>
      <div className="rounded-2xl border bg-white p-8"><h3>Team</h3><p className="text-4xl">$40</p><button>Choose Team</button></div>
    </div>
  );
}
