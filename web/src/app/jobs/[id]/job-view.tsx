"use client";

import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { api, CATEGORY_LABEL, fmtMs, type Decision, type Incident, type Job } from "@/lib/api";

export function JobView() {
  const { id } = useParams<{ id: string }>();
  const [job, setJob] = useState<Job | null>(null);
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let alive = true;
    const load = async () => {
      try {
        const j = await api.getJob(id);
        if (!alive) return;
        setJob(j);
        if (j.status === "completed") setIncidents(await api.listIncidents(id));
      } catch (e) {
        setError(String(e));
      }
    };
    load();
    const t = setInterval(load, 3000);
    return () => {
      alive = false;
      clearInterval(t);
    };
  }, [id]);

  async function decide(inc: Incident, decision: Decision) {
    await api.review(inc.id, decision);
    setIncidents((xs) => xs.map((x) => (x.id === inc.id ? { ...x, latest_decision: decision } : x)));
  }

  if (error) return <p className="text-red-700">{error}</p>;
  if (!job) return <p className="text-zinc-500">Loading…</p>;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-lg font-semibold">Job <span className="font-mono">{job.id.slice(0, 8)}</span></h1>
        <p className="text-sm text-zinc-600">
          Status: {job.status} · attempts: {job.attempts}
          {job.error && <span className="text-red-700"> · {job.error}</span>}
        </p>
      </div>

      {job.status === "completed" && (
        <section>
          <h2 className="mb-3 font-semibold">Candidate incidents</h2>
          {incidents.length === 0 ? (
            <p className="text-sm text-zinc-500">No candidates found in this recording.</p>
          ) : (
            <ol className="space-y-3">
              {incidents.map((inc) => (
                <li key={inc.id} className="rounded-lg border bg-white p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">{CATEGORY_LABEL[inc.category]}</p>
                      <p className="text-sm text-zinc-600">
                        {fmtMs(inc.start_ms)}–{fmtMs(inc.end_ms)} · score {inc.score.toFixed(2)} ·{" "}
                        <span className="font-mono text-xs">{inc.model_version}</span>
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {(["confirmed", "dismissed"] as const).map((d) => (
                        <button
                          key={d}
                          onClick={() => decide(inc, d)}
                          className={`rounded-md border px-3 py-1 text-sm ${
                            inc.latest_decision === d ? "bg-zinc-900 text-white" : "bg-white"
                          }`}
                        >
                          {d === "confirmed" ? "Confirm" : "Dismiss"}
                        </button>
                      ))}
                    </div>
                  </div>
                  {inc.summary && <p className="mt-2 text-sm">{inc.summary}</p>}
                </li>
              ))}
            </ol>
          )}
        </section>
      )}
    </div>
  );
}
