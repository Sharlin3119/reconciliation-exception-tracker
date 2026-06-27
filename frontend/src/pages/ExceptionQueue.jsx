import { useState, useEffect, useCallback } from "react";
import { fetchExceptions, transitionException } from "../api/exceptions";

const STATUS_STYLES = {
  Open:       "bg-yellow-100 text-yellow-800",
  Assigned:   "bg-blue-100 text-blue-800",
  "In Review":"bg-purple-100 text-purple-800",
  Resolved:   "bg-green-100 text-green-800",
  Reopened:   "bg-orange-100 text-orange-800",
};

const TRANSITIONS = {
  Open:       ["Assigned", "In Review"],
  Assigned:   ["In Review", "Resolved"],
  "In Review":["Resolved", "Open"],
  Resolved:   ["Reopened"],
  Reopened:   ["Assigned", "In Review", "Resolved"],
};

// DEV_ACTOR_ID: replace with real auth identity in Phase 3 auth work.
const DEV_ACTOR_ID = "dev-user";

function StatusBadge({ status }) {
  const cls = STATUS_STYLES[status] ?? "bg-gray-100 text-gray-600";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${cls}`}>
      {status}
    </span>
  );
}

function TransitionModal({ exc, onClose, onDone }) {
  const [toState, setToState]   = useState(TRANSITIONS[exc.status]?.[0] ?? "");
  const [reason, setReason]     = useState("");
  const [working, setWorking]   = useState(false);
  const [error, setError]       = useState(null);
  const options = TRANSITIONS[exc.status] ?? [];

  async function handleSubmit(e) {
    e.preventDefault();
    setWorking(true);
    setError(null);
    try {
      await transitionException(exc.id, DEV_ACTOR_ID, toState, reason || null);
      onDone();
    } catch (err) {
      setError(err.message);
    } finally {
      setWorking(false);
    }
  }

  return (
    <div className="fixed inset-0 bg-black/30 flex items-center justify-center z-50">
      <form
        onSubmit={handleSubmit}
        className="bg-white rounded shadow-lg p-6 w-full max-w-sm space-y-4"
      >
        <h3 className="text-base font-semibold text-gray-800">
          Transition exception #{exc.id}
        </h3>
        <p className="text-xs text-gray-500">
          Current status: <span className="font-medium">{exc.status}</span>
        </p>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">New status</label>
          <select
            value={toState}
            onChange={(e) => setToState(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
          >
            {options.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-600 mb-1">Reason (optional)</label>
          <textarea
            rows={2}
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
          />
        </div>

        {error && <p className="text-xs text-red-600">{error}</p>}

        <div className="flex gap-2 pt-1">
          <button
            type="submit"
            disabled={working || !toState}
            className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {working ? "Saving…" : "Apply"}
          </button>
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}

export default function ExceptionQueue() {
  const [exceptions, setExceptions] = useState([]);
  const [error, setError]           = useState(null);
  const [transitioning, setTransitioning] = useState(null);

  const load = useCallback(() => {
    fetchExceptions()
      .then(setExceptions)
      .catch((err) => setError(err.message));
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Exception Queue</h2>
        <p className="text-sm text-gray-500 mt-0.5">
          Unresolved reconciliation exceptions requiring review.
        </p>
      </div>

      {error && (
        <p className="text-sm text-red-600 mb-4">Failed to load exceptions: {error}</p>
      )}

      {!error && exceptions.length === 0 && (
        <p className="text-sm text-gray-500 mt-4">No exceptions found.</p>
      )}

      {exceptions.length > 0 && (
        <div className="overflow-x-auto">
          <table className="min-w-full text-sm border border-gray-200 rounded">
            <thead className="bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
              <tr>
                <th className="px-4 py-2">ID</th>
                <th className="px-4 py-2">Type</th>
                <th className="px-4 py-2">Status</th>
                <th className="px-4 py-2">Amount diff</th>
                <th className="px-4 py-2">Assigned to</th>
                <th className="px-4 py-2">Created</th>
                <th className="px-4 py-2">Resolved</th>
                <th className="px-4 py-2"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {exceptions.map((exc) => (
                <tr key={exc.id} className="hover:bg-gray-50">
                  <td className="px-4 py-2 text-gray-500">#{exc.id}</td>
                  <td className="px-4 py-2 font-medium text-gray-800">{exc.exception_type}</td>
                  <td className="px-4 py-2"><StatusBadge status={exc.status} /></td>
                  <td className="px-4 py-2">
                    {exc.amount_difference != null
                      ? `$${Number(exc.amount_difference).toFixed(2)}`
                      : "—"}
                  </td>
                  <td className="px-4 py-2 text-gray-600">{exc.assigned_to ?? "—"}</td>
                  <td className="px-4 py-2 text-gray-500">
                    {new Date(exc.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-2 text-gray-500">
                    {exc.resolved_at ? new Date(exc.resolved_at).toLocaleDateString() : "—"}
                  </td>
                  <td className="px-4 py-2">
                    {TRANSITIONS[exc.status]?.length > 0 && (
                      <button
                        onClick={() => setTransitioning(exc)}
                        className="text-blue-600 hover:underline text-xs whitespace-nowrap"
                      >
                        Change status
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {transitioning && (
        <TransitionModal
          exc={transitioning}
          onClose={() => setTransitioning(null)}
          onDone={() => { setTransitioning(null); load(); }}
        />
      )}
    </div>
  );
}
