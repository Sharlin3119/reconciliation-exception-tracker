import { useState } from "react";

export default function Upload() {
  const [files, setFiles] = useState([]);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
    setError(null);
    setResponse(null);
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setError("Please select at least one file");
      return;
    }
    setLoading(true);
    setError(null);
    setResponse(null);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const resp = await fetch("/files/upload", {
        method: "POST",
        body: formData,
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data.detail || "Upload failed");
      }
      setResponse(data);
    } catch (err) {
      setError("Upload failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 px-4 py-8 sm:px-6 lg:px-8">
      <div className="max-w-xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-800 mb-2">File Upload</h1>
        <p className="text-sm text-gray-600 mb-4">
          Upload reconciliation files (PDF, Excel, Word) for validation.
        </p>

        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Select files
            </label>
            <input
              type="file"
              multiple
              accept=".pdf,.xls,.xlsx,.doc,.docx"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-600 hover:file:bg-blue-100"
              disabled={loading}
            />
          </div>

          {files.length > 0 && (
            <div className="border-t pt-4">
              <h2 className="text-sm font-medium text-gray-700 mb-2">
                Selected files ({files.length})
              </h2>
              <ul className="divide-y divide-gray-200">
                {files.map((file) => (
                  <li key={file.name} className="py-2 text-sm">
                    <span className="font-medium">{file.name}</span>
                    <span className="ml-4 text-gray-500">
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
              {loading ? "Uploading..." : "Upload"}
            </button>
          </div>
        </form>

        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-800">
            Upload failed. Is the backend running?
          </div>
        )}

        {response && (
          <div className="mt-4">
            <h2 className="text-sm font-medium text-gray-700 mb-2">Results</h2>
            <div className="space-y-2">
              {response.files.map((item, idx) => (
                <div key={idx} className="flex items-center">
                  <span className="flex-1 text-sm">{item.filename}</span>
                  <span className={`ml-2 px-2 py-0.5 text-xs rounded-full ${
                    item.allowed ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
                  }`}>
                    {item.allowed ? "Allowed" : "Not allowed"}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}