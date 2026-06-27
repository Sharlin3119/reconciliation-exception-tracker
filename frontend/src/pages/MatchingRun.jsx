import { useState } from "react";
import { runPipeline } from "../api/matching";

const DEMO_BANK = JSON.stringify(
  [
    { external_id: "B-001", amount: "1500.00", transaction_date: "2024-01-15", description: "ACME Corp invoice payment" },
    { external_id: "B-002", amount: "2200.50", transaction_date: "2024-01-16", description: "Office supplies purchase" },
    { external_id: "B-003", amount: "850.00",  transaction_date: "2024-01-18", description: "Electricity bill January" },
    { external_id: "B-004", amount: "300.00",  transaction_date: "2024-01-20", description: "Unmatched bank entry" },
  ],
  null,
  2
);

const DEMO_GL = JSON.stringify(
  [
    { external_id: "B-001", amount: "1500.00", transaction_date: "2024-01-15", description: "ACME Corp invoice payment" },
    { external_id: "GL-002", amount: "2200.50", transaction_date: "2024-01-16", description: "Office supplies" },
    { external_id: "GL-003", amount: "855.00",  transaction_date: "2024-01-19", description: "Electric utility" },
    { external_id: "GL-004", amount: "999.00",  transaction_date: "2024-01-22", description: "Unmatched GL entry" },
  ],
  null,
  2
);

const DEMO_RULES = JSON.stringify(
  [{ amount_tolerance: 10, date_tolerance_days: 2, requires_approval: true }],
  null,
  2
);

function Section({ title, color, children }) {
  const borderCls = {
    green:  "border-green-300  bg-green-50",
    yellow: "border-yellow-300 bg-yellow-50",
    orange: "border-orange-300 bg-orange-50",
    red:    "border-red-200    bg-red-50",
  }[color];
  return (
    <div className={`border rounded p-4 mb-4 ${borderCls}`}>
      <h3 className="text-sm font-semibold text-gray-700 mb-2">{title}</h3>
      {children}
    </div>
  );
}

function RecordTable({ records, columns }) {
  if (!records.length) return <p className="text-xs text-gray-500">None</p>;
  return (
    <table className="min-w-full text-xs border border-gray-200 rounded bg-white">
      <thead className="bg-gray-50 text-left text-xs font-semibold text-gray-500 uppercase">
        <tr>
          {columns.map((c) => <th key={c.key} className="px-3 py-1.5">{c.label}</th>)}
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-100">
        {records.map((row, i) => (
          <tr key={i}>
            {columns.map((c) => (
              <td key={c.key} className="px-3 py-1.5 text-gray-700">
                {c.render ? c.render(row) : String(row[c.key] ?? "—")}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

const pct = (n) => `${(n * 100).toFixed(0)}%`;

export default function MatchingRun() {
  const [bankJson, setBankJson]   = useState(DEMO_BANK);
  const [glJson, setGlJson]       = useState(DEMO_GL);
  const [rulesJson, setRulesJson] = useState(DEMO_RULES);
  const [threshold, setThreshold] = useState(85);
  const [result, setResult]       = useState(null);
  const [error, setError]         = useState(null);
  const [running, setRunning]     = useState(false);

  async function handleRun(e) {
    e.preventDefault();
    setError(null);
    setResult(null);

    let bank, gl, rules;
    try {
      bank  = JSON.parse(bankJson);
      gl    = JSON.parse(glJson);
      rules = JSON.parse(rulesJson);
    } catch (err) {
      setError("JSON parse error: " + err.message);
      return;
    }

    setRunning(true);
    try {
      const data = await runPipeline({
        bank_records: bank,
        gl_records: gl,
        fuzzy_threshold: threshold,
        rules,
      });
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setRunning(false);
    }
  }

  const pairCols = [
    { key: "bank_id",   label: "Bank ID",   render: (r) => r.bank.external_id },
    { key: "gl_id",     label: "GL ID",     render: (r) => r.gl.external_id },
    { key: "amount",    label: "Amount",    render: (r) => `$${Number(r.bank.amount).toFixed(2)}` },
    { key: "date",      label: "Date",      render: (r) => r.bank.transaction_date },
    { key: "conf",      label: "Confidence",render: (r) => pct(r.confidence_score) },
  ];

  const probCols = [
    ...pairCols.slice(0, 4),
    { key: "sim",  label: "Similarity", render: (r) => `${r.similarity_score.toFixed(1)}` },
    { key: "conf", label: "Confidence", render: (r) => pct(r.confidence_score) },
  ];

  const possCols = [
    ...pairCols.slice(0, 4),
    { key: "conf",  label: "Confidence",   render: (r) => pct(r.confidence_score) },
    { key: "rules", label: "Matched rules", render: (r) => r.matched_rules.join(", ") },
  ];

  const unmatchedCols = [
    { key: "external_id",      label: "ID" },
    { key: "amount",           label: "Amount",      render: (r) => `$${Number(r.amount).toFixed(2)}` },
    { key: "transaction_date", label: "Date" },
    { key: "description",      label: "Description" },
  ];

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-xl font-semibold text-gray-800">Run Matching Pipeline</h2>
        <p className="text-sm text-gray-500 mt-0.5">
          Paste bank and GL records as JSON arrays, then run exact → fuzzy → rule-based matching.
        </p>
      </div>

      <form onSubmit={handleRun} className="space-y-4 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">Bank records (JSON)</label>
            <textarea
              rows={10}
              value={bankJson}
              onChange={(e) => setBankJson(e.target.value)}
              className="w-full font-mono text-xs border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-400"
            />
          </div>
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">GL records (JSON)</label>
            <textarea
              rows={10}
              value={glJson}
              onChange={(e) => setGlJson(e.target.value)}
              className="w-full font-mono text-xs border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-400"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Rules (JSON — amount_tolerance, date_tolerance_days, requires_approval)
            </label>
            <textarea
              rows={4}
              value={rulesJson}
              onChange={(e) => setRulesJson(e.target.value)}
              className="w-full font-mono text-xs border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-1 focus:ring-blue-400"
            />
          </div>
          <div className="flex flex-col justify-end pb-1">
            <label className="block text-xs font-medium text-gray-600 mb-1">
              Fuzzy threshold: <span className="font-mono text-blue-600">{threshold}</span>
            </label>
            <input
              type="range"
              min="50"
              max="100"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="w-full"
            />
            <p className="text-xs text-gray-400 mt-1">
              Higher = stricter description similarity required for fuzzy matches.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            type="submit"
            disabled={running}
            className="px-5 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {running ? "Running…" : "Run pipeline"}
          </button>
          {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
      </form>

      {result && (
        <div>
          <h3 className="text-base font-semibold text-gray-700 mb-3">Results</h3>

          <Section title={`Confirmed matches (${result.confirmed_matches.length}) — exact, no review needed`} color="green">
            <RecordTable records={result.confirmed_matches} columns={pairCols} />
          </Section>

          <Section title={`Probable matches (${result.probable_matches.length}) — fuzzy, requires human review`} color="yellow">
            <RecordTable records={result.probable_matches} columns={probCols} />
          </Section>

          <Section title={`Possible matches (${result.possible_matches.length}) — rule-based, requires approval`} color="orange">
            <RecordTable records={result.possible_matches} columns={possCols} />
          </Section>

          <Section title={`Unmatched bank (${result.unmatched_bank.length})`} color="red">
            <RecordTable records={result.unmatched_bank} columns={unmatchedCols} />
          </Section>

          <Section title={`Unmatched GL (${result.unmatched_gl.length})`} color="red">
            <RecordTable records={result.unmatched_gl} columns={unmatchedCols} />
          </Section>
        </div>
      )}
    </div>
  );
}
