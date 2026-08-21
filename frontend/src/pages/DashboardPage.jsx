import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function DashboardPage() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentTenders, setRecentTenders] = useState([]);

  useEffect(() => {
    api.get('/tenders?status=active&page_size=5')
      .then(res => setRecentTenders(res.data.tenders))
      .catch(() => {});
    if (user?.role === 'admin') {
      api.get('/admin/stats')
        .then(res => setStats(res.data))
        .catch(() => {});
    }
  }, [user]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Welcome, {user?.full_name}</h1>
        <p className="text-gray-600 mt-1">Here's an overview of the tender portal</p>
      </div>

      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[
            { label: 'Total Tenders', value: stats.total_tenders, color: 'bg-blue-500' },
            { label: 'Active Tenders', value: stats.active_tenders, color: 'bg-green-500' },
            { label: 'Registered Users', value: stats.total_users, color: 'bg-purple-500' },
            { label: 'Checklists Created', value: stats.total_checklists, color: 'bg-orange-500' },
          ].map((stat, i) => (
            <div key={i} className="bg-white rounded-lg shadow p-6">
              <div className={`${stat.color} h-2 rounded-full mb-4`}></div>
              <p className="text-sm text-gray-500">{stat.label}</p>
              <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
            </div>
          ))}
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-gray-900">Recent Active Tenders</h2>
            <Link to="/tenders" className="text-primary-600 hover:text-primary-700 text-sm font-medium">View All</Link>
          </div>
        </div>
        <div className="divide-y divide-gray-200">
          {recentTenders.length === 0 && (
            <p className="p-6 text-gray-500 text-center">No active tenders found</p>
          )}
          {recentTenders.map(tender => (
            <Link key={tender.id} to={`/tenders/${tender.id}`}
              className="block p-6 hover:bg-gray-50 transition-colors">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-gray-900">{tender.title}</h3>
                  <div className="mt-1 flex flex-wrap gap-2">
                    {tender.source_portal && (
                      <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">{tender.source_portal}</span>
                    )}
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full">{tender.category}</span>
                    {tender.deadline && (
                      <span className="text-xs bg-red-100 text-red-800 px-2 py-1 rounded-full">
                        Due: {new Date(tender.deadline).toLocaleDateString()}
                      </span>
                    )}
                  </div>
                </div>
                {tender.estimated_value && (
                  <span className="text-sm font-medium text-gray-700">PKR {Number(tender.estimated_value).toLocaleString()}</span>
                )}
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
