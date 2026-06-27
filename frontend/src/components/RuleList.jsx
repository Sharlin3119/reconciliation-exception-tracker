export default function RuleList({ rules, onEdit, onDelete }) {
  if (rules.length === 0) {
    return <p className="text-sm text-gray-500 mt-4">No rules configured yet.</p>;
  }

  return (
    <div className="mt-4 overflow-x-auto">
      <table className="min-w-full text-sm border border-gray-200 rounded">
        <thead className="bg-gray-100 text-left text-xs font-semibold text-gray-600 uppercase tracking-wide">
          <tr>
            <th className="px-4 py-2">Name</th>
            <th className="px-4 py-2">Amount tolerance</th>
            <th className="px-4 py-2">Date tolerance (days)</th>
            <th className="px-4 py-2">Requires approval</th>
            <th className="px-4 py-2">Active</th>
            <th className="px-4 py-2">Created</th>
            <th className="px-4 py-2"></th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {rules.map((rule) => (
            <tr key={rule.id} className="hover:bg-gray-50">
              <td className="px-4 py-2 font-medium text-gray-800">{rule.name}</td>
              <td className="px-4 py-2">{Number(rule.amount_tolerance).toFixed(2)}</td>
              <td className="px-4 py-2">{rule.date_tolerance_days}</td>
              <td className="px-4 py-2">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                    rule.requires_approval
                      ? "bg-yellow-100 text-yellow-800"
                      : "bg-green-100 text-green-800"
                  }`}
                >
                  {rule.requires_approval ? "Yes" : "No"}
                </span>
              </td>
              <td className="px-4 py-2">
                <span
                  className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${
                    rule.is_active
                      ? "bg-blue-100 text-blue-800"
                      : "bg-gray-100 text-gray-500"
                  }`}
                >
                  {rule.is_active ? "Active" : "Inactive"}
                </span>
              </td>
              <td className="px-4 py-2 text-gray-500">
                {new Date(rule.created_at).toLocaleDateString()}
              </td>
              <td className="px-4 py-2 space-x-2 whitespace-nowrap">
                <button
                  onClick={() => onEdit(rule)}
                  className="text-blue-600 hover:underline text-xs"
                >
                  Edit
                </button>
                <button
                  onClick={() => onDelete(rule)}
                  className="text-red-500 hover:underline text-xs"
                >
                  Delete
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
