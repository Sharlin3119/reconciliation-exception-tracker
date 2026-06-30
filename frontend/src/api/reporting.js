import { HEADERS } from "./_shared";

const BASE = "/reporting";

export async function fetchSummary() {
  const res = await fetch(`${BASE}/summary`, { headers: HEADERS });
  if (!res.ok) throw new Error("Failed to load reporting summary");
  return res.json();
}
