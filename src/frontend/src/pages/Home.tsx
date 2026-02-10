import { useEffect, useState } from "react";
import { api } from "../api/api";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";

export default function Home() {
  const [payload, setPayload] = useState<any>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function fetchPreview() {
    setLoading(true);
    setErr(null);
    api
      .get("/users?page=1&page_size=5")
      .then((r) => setPayload(r.data))
      .catch((e) => setErr(e?.response?.data?.detail ?? "Failed"))
      .finally(() => setLoading(false));
  }

  useEffect(() => {
    fetchPreview();
  }, []);

  return (
    <div className="mx-auto max-w-5xl px-6 pb-16">
      <div className="grid gap-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="space-y-2">
            <h1 className="text-4xl font-semibold">Home</h1>
            <p className="text-sm text-muted-foreground">
              This is your protected workspace, wired to the backend API.
            </p>
          </div>
          <Button variant="outline" onClick={fetchPreview} disabled={loading}>
            {loading ? "Refreshing..." : "Refresh data"}
          </Button>
        </div>

        <Card className="border-white/60 bg-white/80 shadow-xl shadow-amber-100/50 backdrop-blur">
          <CardHeader>
            <CardTitle>API Snapshot</CardTitle>
            <CardDescription>Latest response from `/users?page=1&page_size=5`.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {err && (
              <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                {err}
              </div>
            )}
            <pre className="overflow-auto rounded-xl bg-slate-900/95 p-4 text-sm text-amber-50">
              {JSON.stringify(payload, null, 2)}
            </pre>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
