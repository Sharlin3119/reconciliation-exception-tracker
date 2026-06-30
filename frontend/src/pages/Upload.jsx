import { useState } from "react";

export default function Upload({ onNavigate }) {
  const [files, setFiles] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setError(null);
    setResult(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError("Please select at least one file");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const resp = await fetch("http://localhost:8000/files/run_matching_from_upload", {
        method: "POST",
        body: formData,
      });
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}: ${resp.statusText}`);
      }
      const data = await resp.json();
      setResult(data);
    } catch (err) {
      setError("Upload or matching failed. Is the backend running on http://localhost:8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-6 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">Upload & Run Matching</h1>
        <p className="text-sm text-slate-600 mb-4">
          Upload reconciliation files (bank statements, ledger exports) to run matching and create exceptions.
        </p>

        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Select files
            </label>
            <input
              type="file"
              multiple
              accept=".pdf,.xls,.xlsx,.doc,.docx,.csv"
              onChange={handleFileChange}
              className="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
            />
          </div>

          {files.length > 0 && (
            <div className="border-t pt-4">
              <h3 className="text-sm font-medium text-slate-700 mb-2">
                Selected files ({files.length})
              </h3>
              <ul className="divide-y divide-slate-200">
                {files.map((file) => (
                  <li key={file.name} className="py-2 text-sm">
                    <span className="font-medium">{file.name}</span>
                    <span className="ml-4 text-slate-400">
                      {(file.size / 1024).toFixed(1)} KB
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="flex items-center justify-between">
            <button
              type="submit"
              disabled={loading || files.length === 0}
              className="px-4 py-2 text-sm font-medium bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? "Running matching..." : "Upload & Run Matching"}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-slate-50 border border-slate-200 rounded text-sm text-slate-600">
            {error}
          </div>
        )}

        {result && (
          <div className="mt-4">
            <h3 className="text-sm font-medium text-slate-700 mb-2">
              Matching Results
            </h3>
            <div className="grid grid-cols-1 gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Total transactions:</span>
                <span className="text-xl font-semibold text-slate-900">
                  {result.total_transactions || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Matched transactions:</span>
                <span className="text-xl font-semibold text-slate-900">
                  {result.matched || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Exceptions created:</span>
                <span className="text-xl font-semibold text-slate-900">
                  {result.exceptions_created || 0}
                </span>
              </div>
            </div>
          </div>
        )}

        {result && (
          <div className="mt-4 flex space-x-2">
            <button
              onClick={() => {
                // Navigate to Exception Queue page
                onNavigate && onNavigate("exceptions");
              }}
              className="inline-flex items-center rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              View Exceptions
            </button>
            <button
              onClick={() => {
                // Navigate to Dashboard page
                onNavigate && onNavigate("dashboard");
              }}
              className="inline-flex items-center rounded-md border border-slate-200 px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
            >
              View Dashboard
            </button>
          </div>
        )}
      </div>
    </div>
  );
}