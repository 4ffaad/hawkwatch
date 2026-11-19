const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

// DEV ONLY: matches the API's X-User-Id stub. Replace with real auth.
const DEV_USER = "dev-user";

export type JobStatus = "queued" | "running" | "completed" | "failed";
export type Decision = "confirmed" | "dismissed";

export interface Job {
  id: string;
  video_id: string;
  status: JobStatus;
  attempts: number;
  error: string | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface Incident {
  id: string;
  category: "possible_fight" | "fire_smoke" | "possible_fall";
  start_ms: number;
  end_ms: number;
  score: number;
  model_version: string;
  summary: string | null;
  latest_decision: Decision | null;
}

async function req<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", "X-User-Id": DEV_USER, ...init?.headers },
  });
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json() as Promise<T>;
}

export const api = {
  listJobs: () => req<Job[]>("/jobs"),
  getJob: (id: string) => req<Job>(`/jobs/${id}`),
  listIncidents: (id: string) => req<Incident[]>(`/jobs/${id}/incidents`),
  review: (incidentId: string, decision: Decision) =>
    req(`/incidents/${incidentId}/review`, { method: "POST", body: JSON.stringify({ decision }) }),

  async upload(file: File): Promise<Job> {
    const { video_id, upload_url } = await req<{ video_id: string; upload_url: string }>(
      "/uploads",
      {
        method: "POST",
        body: JSON.stringify({ filename: file.name, content_type: file.type, size: file.size }),
      },
    );
    const put = await fetch(upload_url, {
      method: "PUT",
      body: file,
      headers: { "Content-Type": file.type },
    });
    if (!put.ok) throw new Error(`storage upload failed: ${put.status}`);
    return req<Job>(`/uploads/${video_id}/complete`, { method: "POST" });
  },
};

export function fmtMs(ms: number) {
  const s = Math.floor(ms / 1000);
  return `${String(Math.floor(s / 60)).padStart(2, "0")}:${String(s % 60).padStart(2, "0")}`;
}

export const CATEGORY_LABEL: Record<Incident["category"], string> = {
  possible_fight: "Possible physical altercation",
  fire_smoke: "Visible fire or smoke",
  possible_fall: "Possible fall",
};
