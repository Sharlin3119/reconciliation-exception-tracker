import { useState, useEffect, useCallback } from "react";
import { fetchRules, deleteRule } from "./api/rules";
import RuleList from "./components/RuleList";
import RuleForm from "./components/RuleForm";
import ExceptionQueue from "./pages/ExceptionQueue";
import MatchingRun from "./pages/MatchingRun";
import Dashboard from "./pages/Dashboard";
import Upload from "./pages/Upload";

const NAV = [
  { id: "exceptions", label: "Exception Queue" },
  { id: "matching",   label: "Run Matching" },
  { id: "rules",      label: "Matching Rules" },
  { id: "dashboard",  label: "Dashboard" },
  { id: "upload",     label: "Upload" },
];

export default function App() {
  const [page, setPage] = useState("exceptions");

  // --- rules state ---
  const [rules, setRules] = useState([]);
  const [editingRule, setEditingRule] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loadError, setLoadError] = useState(null);

  const loadRules = useCallback(async () => {
    try {
      const data = await fetchRules();
      setRules(data);
      setLoadError(null);
    } catch (err) {
      setLoadError(err.message);
    }
  }, []);

  useEffect(() => { if (page === "rules") loadRules(); }, [page, loadRules]);

  function handleEdit(rule) { setEditingRule(rule); setShowForm(true); }
  function handleNew()      { setEditingRule(null);  setShowForm(true); }
  function handleCancel()   { setEditingRule(null);  setShowForm(false); }
  function handleSaved()    { setEditingRule(null);  setShowForm(false); loadRules(); }

  async function handleDelete(rule) {
    if (!window.confirm(`Delete rule "${rule.name}"?`)) return;
    try { await deleteRule(rule.id); loadRules(); }
    catch (err) { alert(err.message); }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Nav */}
      <header className="bg-white border-b border-gray-200 px-8 py-3 flex items-center gap-6">
        <span className="text-sm font-semibold text-gray-700 mr-4">RET</span>
        {NAV.map((n) => (
          <button
            key={n.id}
            onClick={() => setPage(n.id)}
            className={`text-sm pb-0.5 border-b-2 transition-colors ${
              page === n.id
                ? "border-blue-600 text-blue-600 font-medium"
                : "border-transparent text-gray-500 hover:text-gray-700"
            }`}
          >
            {n.label}
          </button>
        ))}
      </header>

       <main className="max-w-5xl mx-auto px-8 py-8">
         {page === "exceptions" && <ExceptionQueue />}

         {page === "matching" && <MatchingRun />}

         {page === "dashboard" && <Dashboard />}

          {page === "upload" && <Upload onNavigate={(pageId) => setPage(pageId)} />}

         {page === "rules" && (
           <>
             <div className="flex items-center justify-between mb-4">
               <div>
                 <h2 className="text-xl font-semibold text-gray-800">Matching Rules</h2>
                 <p className="text-sm text-gray-500 mt-0.5">
                   Configure rule-based matching tolerances.
                 </p>
               </div>
               <button
                 onClick={handleNew}
                 className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
               >
                 + New rule
               </button>
             </div>

             {loadError && (
               <p className="text-sm text-red-600 mb-4">Failed to load rules: {loadError}</p>
             )}

             <RuleList rules={rules} onEdit={handleEdit} onDelete={handleDelete} />

             {showForm && (
               <div className="mt-8">
                 <RuleForm
                   initialValues={editingRule}
                   onSaved={handleSaved}
                   onCancel={handleCancel}
                 />
               </div>
             )}
           </>
         )}
       </main>
    </div>
  );
}
