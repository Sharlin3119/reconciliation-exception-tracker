import { useState, useEffect } from "react";
import { fetchSummary } from "../api/reporting";

const STATUS_COLORS = {
  Open:       "bg-yellow-400",
  Assigned:   "bg-blue-400",
  "In Review":"bg-purple-400",
  Resolved:   "bg-green-400",
  Reopened:   "bg-orange-400",
};

function StatCard({ label, value, sub }) {
  return (
    <div className="bg-white border border-gray-200 rounded p-5 min-w-[140px]">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className="text-3xl font-bold text-gray-800 mt-1">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
    </div>
  );
}

function Bar({ label, count, total, color }) {
  const pct = total > 0 ? Math.round((count / total) * 100) : 0;
  return (
    <div className="flex items-center gap-3 text-sm">
      <span className="w-24 text-right text-gray-600 shrink-0">{label}</span>
      <div className="flex-1 bg-gray-100 rounded-full h-3 overflow-hidden">
        <div
          className={`h-full rounded-full ${color ?? "bg-blue-400"}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <span className="w-8 text-gray-500 text-right">{count}</span>
    </div>
  );
}

export default function Dashboard() {
  const [data, setData]   = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSummary()
      .then(setData)
      .catch((err) => setError(err.message));
  }, []);

  function handlePrint() {
    window.print();
  }

  return (
    <div>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <h2 className="text-xl font-semibold text-gray-800">Reporting Dashboard</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Reconciliation exception summary for the current tenant.
          </p>
        </div>
        <button
          onClick={handlePrint}
          className="px-4 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50 print:hidden"
        >
          Export PDF
        </button>
      </div>

      {error && <p className="text-sm text-red-600">{error}</p>}

      {data && (
        <>
          {/* KPI row */}
          <div className="flex flex-wrap gap-4 mb-8">
            <StatCard
              label="Total exceptions"
              value={data.total_exceptions}
            />
            <StatCard
              label="Resolved"
              value={data.total_resolved}
              sub={
                data.total_exceptions > 0
                  ? `${Math.round((data.total_resolved / data.total_exceptions) * 100)}% resolution rate`
                  : undefined
              }
            />
            <StatCard
              label="Open / in-flight"
              value={data.total_exceptions - data.total_resolved}
            />
            <StatCard
              label="Total amount diff"
              value={`$${Number(data.total_amount_difference).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`}
            />
          </div>

          {/* By status */}
          <div className="grid grid-cols-2 gap-8 mb-8">
            <div className="bg-white border border-gray-200 rounded p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">By status</h3>
              <div className="space-y-3">
                {data.by_status.map((s) => (
                  <Bar
                    key={s.status}
                    label={s.status}
                    count={s.count}
                    total={data.total_exceptions}
                    color={STATUS_COLORS[s.status]}
                  />
                ))}
                {data.by_status.length === 0 && (
                  <p className="text-sm text-gray-400">No data</p>
                )}
              </div>
            </div>

            {/* By type */}
            <div className="bg-white border border-gray-200 rounded p-5">
              <h3 className="text-sm font-semibold text-gray-700 mb-4">By exception type</h3>
              <table className="min-w-full text-sm">
                <thead>
                  <tr className="text-left text-xs font-medium text-gray-500 uppercase">
                    <th className="pb-2">Type</th>
                    <th className="pb-2 text-right">Count</th>
                    <th className="pb-2 text-right">Amount diff</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {data.by_type.map((t) => (
                    <tr key={t.exception_type}>
                      <td className="py-1.5 text-gray-700">{t.exception_type}</td>
                      <td className="py-1.5 text-right text-gray-600">{t.count}</td>
                      <td className="py-1.5 text-right text-gray-600">
                        ${Number(t.total_amount_difference).toFixed(2)}
                      </td>
                    </tr>
                  ))}
                  {data.by_type.length === 0 && (
                    <tr><td colSpan={3} className="py-2 text-gray-400 text-xs">No data</td></tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </>
      )}

      {!data && !error && (
        <p className="text-sm text-gray-400 mt-4">Loading…</p>
      )}
    </div>
  );
}
