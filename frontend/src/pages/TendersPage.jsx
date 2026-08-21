import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';

export default function TendersPage() {
  const [tenders, setTenders] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('active');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    const params = { page, page_size: 12 };
    if (search) params.search = search;
    if (category) params.category = category;
    if (status) params.status = status;
    api.get('/tenders', { params })
      .then(res => {
        setTenders(res.data.tenders);
        setTotal(res.data.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [page, search, category, status]);

  const totalPages = Math.ceil(total / 12);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Tenders</h1>

      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex flex-wrap gap-4">
          <input
            type="text"
            placeholder="Search tenders..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            className="flex-1 min-w-[200px] px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
          <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option value="">All Categories</option>
            <option value="goods">Goods</option>
            <option value="services">Services</option>
            <option value="works">Works</option>
            <option value="consultancy">Consultancy</option>
          </select>
          <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="expired">Expired</option>
            <option value="closed">Closed</option>
          </select>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
        </div>
      ) : tenders.length === 0 ? (
        <div className="bg-white rounded-lg shadow p-12 text-center text-gray-500">
          No tenders found matching your criteria
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {tenders.map(tender => (
            <Link key={tender.id} to={`/tenders/${tender.id}`}
              className="bg-white rounded-lg shadow hover:shadow-md transition-shadow p-6">
              <div className="flex items-start justify-between mb-3">
                <span className={`text-xs px-2 py-1 rounded-full ${
                  tender.status === 'active' ? 'bg-green-100 text-green-800' :
                  tender.status === 'expired' ? 'bg-red-100 text-red-800' :
                  'bg-gray-100 text-gray-800'
                }`}>{tender.status}</span>
                {tender.has_extraction && (
                  <span className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">Extracted</span>
                )}
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2 line-clamp-2">{tender.title}</h3>
              {tender.description && (
                <p className="text-sm text-gray-500 mb-3 line-clamp-2">{tender.description}</p>
              )}
              <div className="flex flex-wrap gap-1 mb-3">
                {tender.source_portal && (
                  <span className="text-xs bg-blue-50 text-blue-700 px-2 py-0.5 rounded">{tender.source_portal}</span>
                )}
                <span className="text-xs bg-gray-50 text-gray-600 px-2 py-0.5 rounded">{tender.category}</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                {tender.deadline && (
                  <span className="text-red-600">Due: {new Date(tender.deadline).toLocaleDateString()}</span>
                )}
                {tender.estimated_value && (
                  <span className="font-medium text-gray-700">PKR {Number(tender.estimated_value).toLocaleString()}</span>
                )}
              </div>
              {tender.document_filename && (
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <span className="text-xs text-gray-500 flex items-center gap-1">
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 20 20"><path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" /></svg>
                    {tender.document_filename}
                  </span>
                </div>
              )}
            </Link>
          ))}
        </div>
      )}

      {totalPages > 1 && (
        <div className="flex justify-center gap-2">
          <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
            className="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-50">Prev</button>
          <span className="px-3 py-1 text-sm text-gray-600">Page {page} of {totalPages}</span>
          <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
            className="px-3 py-1 rounded border border-gray-300 text-sm disabled:opacity-50">Next</button>
        </div>
      )}
    </div>
  );
}
