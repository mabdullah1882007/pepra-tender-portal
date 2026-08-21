import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function ChecklistPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [items, setItems] = useState([]);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [tenderTitle, setTenderTitle] = useState('');

  const fetchData = () => {
    setLoading(true);
    Promise.all([
      api.get(`/tenders/${id}`),
      api.get(`/tenders/${id}/checklist`),
      api.get(`/tenders/${id}/checklist/summary`),
    ])
      .then(([tenderRes, checklistRes, summaryRes]) => {
        setTenderTitle(tenderRes.data.title);
        setItems(checklistRes.data);
        setSummary(summaryRes.data);
      })
      .catch(err => {
        if (err.response?.status === 404) {
          toast.error('No checklist found. Please generate one first.');
          navigate(`/tenders/${id}`);
        }
      })
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchData(); }, [id]);

  const toggleItem = async (itemId, completed) => {
    try {
      await api.put(`/tenders/${id}/checklist/${itemId}`, { is_completed: completed });
      setItems(prev => prev.map(item => item.id === itemId ? { ...item, is_completed: completed } : item));
      const summaryRes = await api.get(`/tenders/${id}/checklist/summary`);
      setSummary(summaryRes.data);
      toast.success(completed ? 'Marked as complete' : 'Marked as incomplete');
    } catch {
      toast.error('Failed to update item');
    }
  };

  const updateNotes = async (itemId, notes) => {
    try {
      await api.put(`/tenders/${id}/checklist/${itemId}`, { notes });
      setItems(prev => prev.map(item => item.id === itemId ? { ...item, notes } : item));
    } catch {
      toast.error('Failed to update notes');
    }
  };

  const deleteItem = async (itemId) => {
    if (!confirm('Remove this item?')) return;
    try {
      await api.delete(`/tenders/${id}/checklist/${itemId}`);
      setItems(prev => prev.filter(item => item.id !== itemId));
      const summaryRes = await api.get(`/tenders/${id}/checklist/summary`);
      setSummary(summaryRes.data);
      toast.success('Item removed');
    } catch {
      toast.error('Failed to delete item');
    }
  };

  if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;

  const grouped = items.reduce((acc, item) => {
    const cat = item.category_name || 'Other';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(item);
    return acc;
  }, {});

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="text-gray-500 hover:text-gray-700">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
        </button>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Application Checklist</h1>
          <p className="text-gray-500 text-sm">{tenderTitle}</p>
        </div>
      </div>

      {summary && (
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold">Readiness Progress</h2>
            <span className={`text-2xl font-bold ${summary.completion_percentage >= 80 ? 'text-green-600' : summary.completion_percentage >= 50 ? 'text-yellow-600' : 'text-red-600'}`}>
              {summary.completion_percentage}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
            <div
              className={`h-3 rounded-full transition-all ${summary.completion_percentage >= 80 ? 'bg-green-500' : summary.completion_percentage >= 50 ? 'bg-yellow-500' : 'bg-red-500'}`}
              style={{ width: `${summary.completion_percentage}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600">
            {summary.completed_items} of {summary.total_items} requirements completed
          </p>

          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">
            {summary.categories.map(cat => (
              <div key={cat.category_id} className="text-center p-3 bg-gray-50 rounded-lg">
                <p className="text-xs text-gray-500 mb-1">{cat.category_name}</p>
                <p className="text-lg font-bold text-gray-900">{cat.completed}/{cat.total}</p>
                <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                  <div className="bg-primary-500 h-1.5 rounded-full" style={{ width: `${cat.percentage}%` }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {Object.entries(grouped).map(([category, categoryItems]) => (
        <div key={category} className="bg-white rounded-lg shadow">
          <div className="p-4 border-b border-gray-200 bg-gray-50 rounded-t-lg">
            <h3 className="font-semibold text-gray-900">{category}</h3>
          </div>
          <div className="divide-y divide-gray-100">
            {categoryItems.map(item => (
              <div key={item.id} className={`p-4 flex items-start gap-3 ${item.is_completed ? 'bg-green-50' : ''}`}>
                <input
                  type="checkbox"
                  checked={item.is_completed}
                  onChange={(e) => toggleItem(item.id, e.target.checked)}
                  className="mt-1 h-5 w-5 text-primary-600 rounded focus:ring-primary-500"
                />
                <div className="flex-1">
                  <p className={`text-sm ${item.is_completed ? 'line-through text-gray-400' : 'text-gray-900'}`}>
                    {item.description}
                  </p>
                  <input
                    type="text"
                    placeholder="Add notes..."
                    value={item.notes || ''}
                    onChange={(e) => updateNotes(item.id, e.target.value)}
                    className="mt-2 w-full text-xs px-2 py-1 border border-gray-200 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
                <button onClick={() => deleteItem(item.id)}
                  className="text-gray-400 hover:text-red-500 text-sm">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                </button>
              </div>
            ))}
          </div>
        </div>
      ))}

      {summary && summary.missing_items.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-red-800 mb-3">Missing Requirements ({summary.missing_items.length})</h3>
          <ul className="space-y-2">
            {summary.missing_items.map(item => (
              <li key={item.id} className="flex items-center gap-2 text-sm text-red-700">
                <span className="text-red-400">&#9679;</span>
                <span className="text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded">{item.category_name}</span>
                {item.description}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
