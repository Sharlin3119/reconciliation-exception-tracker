// Phase 3: replace DEV_TENANT_ID with value from auth token/session.
export const DEV_TENANT_ID = "dev";

export const HEADERS = {
  "Content-Type": "application/json",
  "X-Tenant-ID": DEV_TENANT_ID,
};
