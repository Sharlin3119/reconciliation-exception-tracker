const BASE = "/reporting";
const DEV_TENANT_ID = "dev";
const HEADERS = { "X-Tenant-ID": DEV_TENANT_ID };

export async function fetchSummary() {
  const res = await fetch(`${BASE}/summary`, { headers: HEADERS });
  if (!res.ok) throw new Error("Failed to load reporting summary");
  return res.json();
}
