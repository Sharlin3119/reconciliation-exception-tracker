import { useState, useEffect } from "react";
import { createRule, updateRule } from "../api/rules";

const EMPTY = {
  name: "",
  amount_tolerance: 0,
  date_tolerance_days: 0,
  requires_approval: true,
  is_active: true,
};

export default function RuleForm({ initialValues, onSaved, onCancel }) {
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const isEdit = Boolean(initialValues?.id);

  useEffect(() => {
    setForm(initialValues ?? EMPTY);
    setError(null);
  }, [initialValues]);

  function set(field, value) {
    setForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    try {
      if (isEdit) {
        await updateRule(initialValues.id, form);
      } else {
        await createRule(form);
      }
      onSaved();
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="bg-white border border-gray-200 rounded p-6 space-y-4 max-w-lg"
    >
      <h2 className="text-base font-semibold text-gray-700">
        {isEdit ? "Edit rule" : "New rule"}
      </h2>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">Name</label>
        <input
          required
          type="text"
          value={form.name}
          onChange={(e) => set("name", e.target.value)}
          className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">
          Amount tolerance ($)
        </label>
        <input
          type="number"
          min="0"
          step="0.01"
          value={form.amount_tolerance}
          onChange={(e) => set("amount_tolerance", parseFloat(e.target.value) || 0)}
          className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
        />
      </div>

      <div>
        <label className="block text-xs font-medium text-gray-600 mb-1">
          Date tolerance (days)
        </label>
        <input
          type="number"
          min="0"
          step="1"
          value={form.date_tolerance_days}
          onChange={(e) => set("date_tolerance_days", parseInt(e.target.value, 10) || 0)}
          className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400"
        />
      </div>

      <div className="flex items-center gap-3">
        <input
          id="requires_approval"
          type="checkbox"
          checked={form.requires_approval}
          onChange={(e) => set("requires_approval", e.target.checked)}
          className="h-4 w-4 rounded border-gray-300 text-blue-600"
        />
        <label htmlFor="requires_approval" className="text-sm text-gray-700">
          Requires approval before confirming matches
        </label>
      </div>

      {isEdit && (
        <div className="flex items-center gap-3">
          <input
            id="is_active"
            type="checkbox"
            checked={form.is_active}
            onChange={(e) => set("is_active", e.target.checked)}
            className="h-4 w-4 rounded border-gray-300 text-blue-600"
          />
          <label htmlFor="is_active" className="text-sm text-gray-700">
            Active
          </label>
        </div>
      )}

      {error && <p className="text-xs text-red-600">{error}</p>}

      <div className="flex gap-2 pt-2">
        <button
          type="submit"
          disabled={saving}
          className="px-4 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {saving ? "Saving…" : isEdit ? "Save changes" : "Create rule"}
        </button>
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-1.5 text-sm border border-gray-300 rounded hover:bg-gray-50"
        >
          Cancel
        </button>
      </div>
    </form>
  );
}
