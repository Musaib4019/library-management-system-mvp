import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import api from '../../lib/api';
import { Home, Search, Book, Bell, LogOut, Clock, AlertCircle, CheckCircle } from 'lucide-react';

function MemberHome() {
  const { user } = useAuth();
  const [loans, setLoans] = useState([]);
  const [notifications, setNotifications] = useState([]);
  const [fines, setFines] = useState([]);
  const [reservations, setReservations] = useState([]);

  useEffect(() => {
    fetchData();
  }, [user]);

  const fetchData = async () => {
    try {
      const [lRes, nRes, fRes, rRes] = await Promise.all([
        api.get(`/users/${user.id}/loans`),
        api.get(`/users/${user.id}/notifications`),
        api.get(`/users/${user.id}/fines`),
        api.get(`/users/${user.id}/reservations`)
      ]);
      setLoans(lRes.data);
      setNotifications(nRes.data);
      setFines(fRes.data);
      setReservations(rRes.data);
    } catch (e) {
      console.error(e);
    }
  };

  const renewBook = async (loanId) => {
    try {
      await api.post(`/loans/${loanId}/renew`);
      alert("Book renewed successfully!");
      fetchData();
    } catch (e) {
      alert(e.response?.data?.detail || "Error renewing book");
    }
  };

  const activeLoans = loans.filter(l => l.status === 'ACTIVE');
  const unpaidFines = fines.filter(f => f.status === 'UNPAID');
  const totalFine = unpaidFines.reduce((sum, f) => sum + f.amount, 0);

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-slate-800">Welcome back, {user.name.split(' ')[0]}!</h2>
        <p className="text-slate-500 mt-2">Here's an overview of your library account.</p>
      </div>

      {totalFine > 0 && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-lg mb-8 flex items-start gap-4">
          <AlertCircle className="text-red-500 mt-0.5" />
          <div>
            <h3 className="text-red-800 font-bold">Outstanding Fines</h3>
            <p className="text-red-700 mt-1">You have pending fines totaling Rs {totalFine}. Please visit the library desk to clear them.</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-3 gap-6 mb-8">
        <div className="col-span-2 bg-white rounded-xl shadow-sm p-6 border border-slate-100">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              <Book size={24} className="text-blue-600" />
              Currently Borrowed ({activeLoans.length})
            </h3>
            <Link to="/member/browse" className="text-sm font-medium text-blue-600 hover:text-blue-800">Browse Books &rarr;</Link>
          </div>
          
          {activeLoans.length === 0 ? (
            <div className="text-center py-10 bg-slate-50 rounded-lg">
              <Book className="mx-auto text-slate-300 mb-3" size={32} />
              <p className="text-slate-500">You don't have any books currently borrowed.</p>
            </div>
          ) : (
            <div className="space-y-4">
              {activeLoans.map(loan => {
                const isOverdue = new Date(loan.due_date) < new Date();
                return (
                  <div key={loan.id} className="flex items-center justify-between p-4 border rounded-lg hover:shadow-md transition-shadow">
                    <div className="flex items-start gap-4">
                      <div className="w-12 h-16 bg-blue-100 rounded flex items-center justify-center text-blue-800 font-bold text-xl">
                        {loan.copy.book.title.charAt(0)}
                      </div>
                      <div>
                        <h4 className="font-bold text-slate-800 text-lg leading-tight">{loan.copy.book.title}</h4>
                        <p className="text-slate-500 text-sm mt-1">{loan.copy.book.author}</p>
                        <div className={`text-sm mt-2 flex items-center gap-1 font-medium ${isOverdue ? 'text-red-600' : 'text-slate-600'}`}>
                          <Clock size={14} /> 
                          {isOverdue ? 'Overdue! Due on ' : 'Due on '}
                          {new Date(loan.due_date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div>
                      <button 
                        onClick={() => renewBook(loan.id)}
                        disabled={isOverdue || loan.renewals >= 2}
                        className="px-4 py-2 text-sm font-medium border border-slate-300 rounded hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Renew
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {reservations.length > 0 && (
            <div className="mt-8 border-t pt-8">
              <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-6">
                <Clock size={24} className="text-purple-600" />
                Active Reservations ({reservations.length})
              </h3>
              <div className="space-y-4">
                {reservations.map(res => (
                  <div key={res.id} className="flex items-center justify-between p-4 border rounded-lg bg-slate-50">
                    <div>
                      <h4 className="font-bold text-slate-800">{res.book?.title || 'Unknown Book'}</h4>
                      <p className="text-slate-500 text-sm mt-1">Status: {res.status}</p>
                    </div>
                    <span className="text-xs font-medium bg-purple-100 text-purple-700 px-2 py-1 rounded">
                      Reserved on {new Date(res.created_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        <div className="bg-white rounded-xl shadow-sm p-6 border border-slate-100 h-fit">
          <h3 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-6">
            <Bell size={20} className="text-yellow-500" />
            Notifications
          </h3>
          {notifications.length === 0 ? (
            <p className="text-slate-500 text-sm text-center py-4">No new notifications.</p>
          ) : (
            <ul className="space-y-4">
              {notifications.slice(0, 5).map(n => (
                <li key={n.id} className="text-sm border-b pb-3 last:border-0 last:pb-0">
                  <p className="text-slate-800">{n.message}</p>
                  <p className="text-xs text-slate-400 mt-1">{new Date(n.created_at).toLocaleDateString()}</p>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  )
}

function BrowseBooks() {
  const [books, setBooks] = useState([]);
  const [search, setSearch] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    api.get(`/books?search=${search}`).then(res => setBooks(res.data));
  }, [search]);

  const reserveBook = async (bookId) => {
    try {
      await api.post('/reservations', { book_id: bookId });
      alert("Book reserved successfully! You will be notified when it is available.");
    } catch (e) {
      alert(e.response?.data?.detail || "Error reserving book");
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <h2 className="text-3xl font-bold text-slate-800 mb-6">Library Catalogue</h2>
      
      <div className="bg-white p-4 rounded-xl shadow-sm mb-8 relative">
        <Search className="absolute left-7 top-7 text-slate-400" size={24}/>
        <input 
          type="text"
          className="w-full bg-slate-50 border-none text-lg p-4 pl-14 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
          placeholder="Search for books by title, author, or ISBN..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {books.map(book => (
          <div key={book.id} className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden flex flex-col">
            <div className="h-32 bg-gradient-to-br from-blue-100 to-indigo-50 p-6 flex items-end">
              <h3 className="text-xl font-bold text-slate-800 line-clamp-2">{book.title}</h3>
            </div>
            <div className="p-6 flex-1 flex flex-col">
              <p className="text-slate-600 font-medium mb-1">{book.author}</p>
              <p className="text-slate-400 text-sm mb-4">{book.category} &bull; {book.year}</p>
              
              <div className="mt-auto">
                {book.available_copies > 0 ? (
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-emerald-600 bg-emerald-50 px-2 py-1 rounded">
                      <CheckCircle size={14} /> Available ({book.available_copies})
                    </span>
                  </div>
                ) : (
                  <div className="flex items-center justify-between">
                    <span className="inline-flex items-center gap-1 text-sm font-medium text-slate-500 bg-slate-100 px-2 py-1 rounded">
                      <Clock size={14} /> Checked Out
                    </span>
                    <button 
                      onClick={() => reserveBook(book.id)}
                      className="text-sm font-medium text-blue-600 hover:text-blue-800"
                    >
                      Reserve Book
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default function MemberDashboard() {
  const { logout, user } = useAuth();
  const location = useLocation();
  
  const navItems = [
    { path: '/member', label: 'My Dashboard', icon: Home },
    { path: '/member/browse', label: 'Browse Books', icon: Search },
  ];

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Top Navbar */}
      <nav className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-8">
              <div className="flex-shrink-0 flex items-center gap-2">
                <Book className="text-blue-600" size={28} />
                <span className="font-bold text-xl text-slate-800">Library</span>
              </div>
              <div className="hidden md:flex space-x-4">
                {navItems.map(item => (
                  <Link 
                    key={item.path} 
                    to={item.path} 
                    className={`inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors ${
                      location.pathname === item.path 
                        ? 'bg-blue-50 text-blue-700' 
                        : 'text-slate-600 hover:bg-slate-100'
                    }`}
                  >
                    <item.icon size={18} className="mr-2" />
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
            <div className="flex items-center gap-4">
              <span className="text-sm font-medium text-slate-700">{user?.name}</span>
              <button 
                onClick={logout}
                className="text-slate-500 hover:text-slate-700 p-2 rounded-full hover:bg-slate-100"
                title="Logout"
              >
                <LogOut size={20} />
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
        <Routes>
          <Route path="/" element={<MemberHome />} />
          <Route path="/browse" element={<BrowseBooks />} />
        </Routes>
      </main>
    </div>
  );
}
