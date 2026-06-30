import { HEADERS } from "./_shared";

const BASE = "/rules";

export async function fetchRules() {
  const res = await fetch(BASE, { headers: HEADERS });
  if (!res.ok) throw new Error("Failed to load rules");
  return res.json();
}

export async function createRule(data) {
  const res = await fetch(BASE, {
    method: "POST",
    headers: HEADERS,
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to create rule");
  return res.json();
}

export async function updateRule(id, data) {
  const res = await fetch(`${BASE}/${id}`, {
    method: "PUT",
    headers: HEADERS,
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to update rule");
  return res.json();
}

export async function deleteRule(id) {
  const res = await fetch(`${BASE}/${id}`, {
    method: "DELETE",
    headers: HEADERS,
  });
  if (!res.ok) throw new Error("Failed to delete rule");
}
