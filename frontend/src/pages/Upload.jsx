import { useState } from "react";
import { DEV_TENANT_ID } from "../api/_shared";

function Stat({ label, value, accent }) {
  return (
    <div className="bg-gray-50 border border-gray-200 rounded p-4 min-w-[130px]">
      <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
      <p className={`text-3xl font-bold mt-1 ${accent ?? "text-gray-800"}`}>{value}</p>
    </div>
  );
}

export default function Upload({ onNavigate }) {
  const [files, setFiles] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setError(null);
    setSummary(null);
  };

  const handleRun = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError("Please select at least one CSV file.");
      return;
    }
    setLoading(true);
    setError(null);
    setSummary(null);

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      // ponytail: send only X-Tenant-ID. The shared HEADERS also sets
      // Content-Type: application/json, which would break the multipart upload
      // (the browser must set the multipart boundary itself).
      const resp = await fetch("/files/run_matching_from_upload", {
        method: "POST",
        headers: { "X-Tenant-ID": DEV_TENANT_ID },
        body: formData,
      });
      const data = await resp.json();
      if (!resp.ok) throw new Error(data.detail || "Matching run failed");
      setSummary(data);
    } catch (err) {
      // Keep selected files so the user can retry.
      setError("Matching run failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Upload &amp; Run Matching</h2>
        <p className="text-sm text-gray-500 mt-0.5">
          Upload reconciliation CSV file(s) to run the matching pipeline. Unmatched
          records are saved as Open exceptions.
        </p>
      </div>

      <form
        onSubmit={handleRun}
        className="bg-white border border-gray-200 rounded p-5 space-y-4"
      >
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Select CSV file(s)
          </label>
          <input
            type="file"
            multiple
            accept=".csv"
            onChange={handleFileChange}
            disabled={loading}
            className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
          />
          <p className="text-xs text-gray-400 mt-2">
            CSV only. Expected columns:{" "}
            <code>external_id,date,amount,description,source</code>
          </p>
        </div>

        {files.length > 0 && (
          <ul className="divide-y divide-gray-100 border-t border-gray-100">
            {files.map((file) => (
              <li key={file.name} className="py-2 text-sm flex justify-between">
                <span className="font-medium text-gray-700">{file.name}</span>
                <span className="text-gray-400">{(file.size / 1024).toFixed(1)} KB</span>
              </li>
            ))}
          </ul>
        )}

        <button
          type="submit"
          disabled={loading || files.length === 0}
          className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Running…" : "Run matching"}
        </button>
      </form>

      {error && <p className="text-sm text-red-600 mt-4">{error}</p>}

      {summary && (
        <div className="mt-6">
          <div className="bg-white border border-gray-200 rounded p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">Run complete</h3>
            <div className="flex flex-wrap gap-4">
              <Stat label="Transactions" value={summary.total_transactions} />
              <Stat label="Matched" value={summary.matched} accent="text-green-600" />
              <Stat label="Exceptions created" value={summary.exceptions_created} />
            </div>
          </div>

          <div className="flex gap-3 mt-4">
            <button
              onClick={() => onNavigate?.("exceptions")}
              className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              View Exceptions
            </button>
            <button
              onClick={() => onNavigate?.("dashboard")}
              className="px-4 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50"
            >
              View Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
