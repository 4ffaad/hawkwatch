"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api, type Job } from "@/lib/api";

const STATUS_STYLE: Record<Job["status"], string> = {
  queued: "bg-zinc-200 text-zinc-700",
  running: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

export default function Home() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    api.listJobs().then(setJobs).catch((e) => setError(String(e)));
  }, []);

  useEffect(() => {
    refresh();
    const t = setInterval(refresh, 3000);
    return () => clearInterval(t);
  }, [refresh]);

  async function onFile(file: File | undefined) {
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      await api.upload(file);
      refresh();
    } catch (e) {
      setError(String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-8">
      <section className="rounded-lg border bg-white p-6">
        <h1 className="text-lg font-semibold">Upload footage</h1>
        <p className="mt-1 text-sm text-zinc-600">
          Only upload recordings you are authorised to process.
        </p>
        <label className="mt-4 inline-flex cursor-pointer items-center rounded-md bg-zinc-900 px-4 py-2 text-sm text-white">
          {busy ? "Uploading…" : "Choose video"}
          <input
            type="file"
            accept="video/*"
            className="hidden"
            disabled={busy}
            onChange={(e) => onFile(e.target.files?.[0])}
          />
        </label>
        {error && <p className="mt-3 text-sm text-red-700">{error}</p>}
      </section>

      <section>
        <h2 className="mb-3 font-semibold">Jobs</h2>
        {jobs.length === 0 ? (
          <p className="text-sm text-zinc-500">No uploads yet.</p>
        ) : (
          <ul className="divide-y rounded-lg border bg-white">
            {jobs.map((j) => (
              <li key={j.id}>
                <Link href={`/jobs/${j.id}`} className="flex items-center justify-between px-4 py-3 hover:bg-zinc-50">
                  <span className="font-mono text-sm">{j.id.slice(0, 8)}</span>
                  <span className="text-xs text-zinc-500">{new Date(j.created_at).toLocaleString()}</span>
                  <span className={`rounded px-2 py-0.5 text-xs ${STATUS_STYLE[j.status]}`}>{j.status}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
