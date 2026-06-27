const BASE = "/exceptions";

// Phase 3: replace DEV_TENANT_ID with value from auth token/session.
const DEV_TENANT_ID = "dev";

const HEADERS = {
  "Content-Type": "application/json",
  "X-Tenant-ID": DEV_TENANT_ID,
};

export async function fetchExceptions() {
  const res = await fetch(BASE, { headers: HEADERS });
  if (!res.ok) throw new Error("Failed to load exceptions");
  return res.json();
}

export async function transitionException(id, actorId, toState, reason = null) {
  const res = await fetch(`${BASE}/${id}/transition`, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify({ actor_id: actorId, to_state: toState, reason }),
  });
  if (!res.ok) {
    const detail = await res.json().catch(() => null);
    throw new Error(detail?.detail ?? "Transition failed");
  }
  return res.json();
}
