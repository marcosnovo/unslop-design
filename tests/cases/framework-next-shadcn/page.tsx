import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

export default function Page() {
  return (
    <main className="mx-auto max-w-5xl p-8">
      <h1 className="text-2xl font-semibold">Revenue</h1>
      <div className="rounded-xl border bg-card text-card-foreground shadow">
        <p className="text-sm text-muted-foreground">Last 30 days</p>
      </div>
    </main>
  );
}
