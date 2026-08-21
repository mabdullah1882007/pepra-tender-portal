import { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function TenderDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tender, setTender] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get(`/tenders/${id}`)
      .then(res => setTender(res.data))
      .catch(() => toast.error('Failed to load tender'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleDownload = () => {
    window.open(`/api/tenders/${id}/download`, '_blank');
  };

  const handleGenerateChecklist = async () => {
    try {
      await api.post(`/tenders/${id}/checklist`);
      toast.success('Checklist generated!');
      navigate(`/tenders/${id}/checklist`);
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Failed to generate checklist');
    }
  };

  if (loading) return <div className="flex justify-center py-12"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div></div>;
  if (!tender) return <div className="text-center py-12 text-gray-500">Tender not found</div>;

  const extraction = tender.extraction;

  const renderSection = (title, data, isList = true) => {
    if (!data) return null;
    const items = isList && data.items ? data.items : null;
    return (
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">{title}</h3>
        {isList && items ? (
          <ul className="space-y-1">
            {items.map((item, i) => (
              <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                <span className="text-primary-500 mt-1">&#8226;</span>
                {typeof item === 'string' ? item : JSON.stringify(item)}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-sm text-gray-700 whitespace-pre-wrap">{typeof data === 'string' ? data : JSON.stringify(data)}</p>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <button onClick={() => navigate(-1)} className="text-gray-500 hover:text-gray-700">
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
        </button>
        <h1 className="text-2xl font-bold text-gray-900 flex-1">{tender.title}</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Tender Details</h2>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div><span className="text-gray-500">Tender Number:</span> <span className="font-medium">{tender.tender_number || 'N/A'}</span></div>
              <div><span className="text-gray-500">Category:</span> <span className="font-medium capitalize">{tender.category}</span></div>
              <div><span className="text-gray-500">Status:</span> <span className={`font-medium ${tender.status === 'active' ? 'text-green-600' : 'text-red-600'}`}>{tender.status}</span></div>
              <div><span className="text-gray-500">Source Portal:</span> <span className="font-medium">{tender.source_portal || 'N/A'}</span></div>
              {tender.published_date && <div><span className="text-gray-500">Published:</span> <span className="font-medium">{tender.published_date}</span></div>}
              {tender.deadline && <div><span className="text-gray-500">Deadline:</span> <span className="font-medium text-red-600">{new Date(tender.deadline).toLocaleString()}</span></div>}
              {tender.estimated_value && <div><span className="text-gray-500">Est. Value:</span> <span className="font-medium">PKR {Number(tender.estimated_value).toLocaleString()}</span></div>}
            </div>
            {tender.description && (
              <div className="mt-4 pt-4 border-t border-gray-100">
                <p className="text-sm text-gray-700">{tender.description}</p>
              </div>
            )}
          </div>

          {extraction && (
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Extracted Information</h2>
                <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">
                  Confidence: {extraction.extraction_confidence}%
                </span>
              </div>
              {renderSection('Scope of Work', extraction.scope_of_work, false)}
              {renderSection('Required Documents', extraction.required_documents)}
              {renderSection('Eligibility Criteria', extraction.eligibility_criteria)}
              {renderSection('Financial Requirements', extraction.financial_requirements)}
              {renderSection('Technical Requirements', extraction.technical_requirements)}
              {renderSection('Experience Requirements', extraction.experience_requirements)}
              {renderSection('Terms & Conditions', extraction.terms_and_conditions)}
              {renderSection('Submission Instructions', extraction.submission_instructions, false)}
            </div>
          )}
        </div>

        <div className="space-y-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
            <div className="space-y-3">
              {tender.document_filename && (
                <button onClick={handleDownload}
                  className="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 font-medium flex items-center justify-center gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
                  Download Document
                </button>
              )}
              <button onClick={handleGenerateChecklist}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 font-medium flex items-center justify-center gap-2">
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" /></svg>
                Generate Checklist
              </button>
              <Link to={`/tenders/${id}/checklist`}
                className="block w-full bg-purple-600 text-white py-2 px-4 rounded-md hover:bg-purple-700 font-medium text-center">
                View Checklist
              </Link>
            </div>
          </div>

          {tender.source_url && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-sm font-semibold text-gray-900 mb-2">Source</h3>
              <a href={tender.source_url} target="_blank" rel="noopener noreferrer"
                className="text-primary-600 hover:text-primary-700 text-sm break-all">
                {tender.source_url}
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
