import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <nav className="bg-primary-700 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              <span className="text-white text-xl font-bold">Tender Portal</span>
            </Link>
          </div>

          {user && (
            <div className="flex items-center space-x-4">
              <Link to="/dashboard" className="text-primary-100 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Dashboard
              </Link>
              <Link to="/tenders" className="text-primary-100 hover:text-white px-3 py-2 rounded-md text-sm font-medium">
                Tenders
              </Link>
              <div className="flex items-center space-x-3 ml-4">
                <span className="text-primary-200 text-sm">{user.full_name}</span>
                <span className="text-xs bg-primary-500 text-white px-2 py-1 rounded-full">{user.role}</span>
                <button
                  onClick={handleLogout}
                  className="text-primary-200 hover:text-white text-sm"
                >
                  Logout
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
}
