import { Suspense } from "react";
import { JobView } from "./job-view";

export default function JobPage() {
  return (
    <Suspense fallback={<p className="text-zinc-500">Loading…</p>}>
      <JobView />
    </Suspense>
  );
}
