import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import api from '../../lib/api';
import { BookOpen, Users, LogOut, Search } from 'lucide-react';

function Circulation() {
  const [members, setMembers] = useState([]);
  const [searchMember, setSearchMember] = useState('');
  const [selectedMember, setSelectedMember] = useState(null);
  
  const [books, setBooks] = useState([]);
  const [searchBook, setSearchBook] = useState('');
  
  const [loans, setLoans] = useState([]);

  useEffect(() => {
    api.get('/users?search=' + searchMember).then(res => setMembers(res.data.filter(u => u.role === 'MEMBER')));
  }, [searchMember]);

  useEffect(() => {
    if (searchBook.length > 2) {
      api.get('/books?search=' + searchBook).then(res => setBooks(res.data));
    } else {
      setBooks([]);
    }
  }, [searchBook]);

  const selectMember = async (member) => {
    setSelectedMember(member);
    refreshLoans(member.id);
  };

  const refreshLoans = async (memberId) => {
    const res = await api.get(`/users/${memberId}/loans`);
    setLoans(res.data);
  };

  const returnBook = async (loanId) => {
    try {
      await api.post(`/loans/${loanId}/return`);
      alert("Book returned successfully");
      refreshLoans(selectedMember.id);
    } catch (e) {
      alert("Error returning book");
    }
  };

  const issueBook = async (bookId) => {
    try {
      const copiesRes = await api.get(`/books/${bookId}/copies`);
      const availableCopy = copiesRes.data.find(c => c.status === 'AVAILABLE');
      if (!availableCopy) {
        alert("No available copies for this book!");
        return;
      }
      await api.post('/loans/issue', { user_id: selectedMember.id, copy_id: availableCopy.id });
      alert("Book issued successfully!");
      refreshLoans(selectedMember.id);
      setSearchBook('');
      setBooks([]);
    } catch (e) {
      alert(e.response?.data?.detail || "Error issuing book");
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Circulation Desk</h2>
      <div className="flex gap-6">
        <div className="w-1/3 space-y-6">
          <div className="bg-white p-4 rounded shadow-sm">
            <h3 className="font-semibold mb-3">1. Select Member</h3>
            <div className="relative mb-2">
              <Search className="absolute left-3 top-3 text-slate-400" size={18}/>
              <input 
                className="w-full border p-2 pl-10 rounded" 
                placeholder="Search member by name..." 
                value={searchMember} onChange={e => setSearchMember(e.target.value)} 
              />
            </div>
            <ul className="max-h-48 overflow-y-auto space-y-1">
              {members.map(m => (
                <li 
                  key={m.id} 
                  onClick={() => selectMember(m)}
                  className={`p-2 rounded cursor-pointer text-sm ${selectedMember?.id === m.id ? 'bg-blue-600 text-white' : 'hover:bg-slate-50 border border-transparent'}`}
                >
                  {m.name} ({m.email})
                </li>
              ))}
            </ul>
          </div>

          {selectedMember && (
            <div className="bg-white p-4 rounded shadow-sm">
              <h3 className="font-semibold mb-3">2. Issue New Book</h3>
              <div className="relative mb-2">
                <Search className="absolute left-3 top-3 text-slate-400" size={18}/>
                <input 
                  className="w-full border p-2 pl-10 rounded" 
                  placeholder="Search book title/ISBN..." 
                  value={searchBook} onChange={e => setSearchBook(e.target.value)} 
                />
              </div>
              <ul className="max-h-48 overflow-y-auto space-y-2 mt-2">
                {books.map(b => (
                  <li key={b.id} className="border p-2 rounded text-sm flex justify-between items-center">
                    <div>
                      <p className="font-semibold truncate">{b.title}</p>
                      <p className="text-xs text-slate-500">Available: {b.available_copies}</p>
                    </div>
                    <button 
                      onClick={() => issueBook(b.id)}
                      disabled={b.available_copies === 0}
                      className="bg-blue-600 text-white px-2 py-1 rounded disabled:bg-slate-300"
                    >
                      Issue
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
        
        <div className="w-2/3">
          {selectedMember ? (
            <div className="bg-white p-6 rounded shadow-sm">
              <h3 className="text-xl font-bold mb-4">{selectedMember.name}'s Active Loans</h3>
              {loans.filter(l => l.status === 'ACTIVE').length === 0 ? (
                <p className="text-slate-500">No active loans.</p>
              ) : (
                <ul className="space-y-3">
                  {loans.filter(l => l.status === 'ACTIVE').map(l => (
                    <li key={l.id} className="border border-slate-200 p-4 rounded-lg flex justify-between items-center">
                      <div>
                        <p className="font-semibold text-lg">{l.copy.book.title}</p>
                        <p className="text-sm text-slate-600">Author: {l.copy.book.author}</p>
                        <p className="text-sm text-slate-600">Due: <span className="font-medium">{new Date(l.due_date).toLocaleDateString()}</span></p>
                      </div>
                      <button onClick={() => returnBook(l.id)} className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded shadow-sm transition-colors">
                        Return Book
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <div className="bg-white p-12 rounded shadow-sm text-center">
              <BookOpen size={48} className="mx-auto text-slate-300 mb-4" />
              <h3 className="text-xl font-medium text-slate-600">No Member Selected</h3>
              <p className="text-slate-400 mt-2">Search and select a member from the left panel to issue or return books.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function LibrarianDashboard() {
  const { logout, user } = useAuth();
  
  return (
    <div className="flex h-screen bg-slate-50">
      <div className="w-64 bg-emerald-900 text-white flex flex-col">
        <div className="p-6 border-b border-emerald-800">
          <h1 className="text-xl font-bold">Librarian Portal</h1>
          <p className="text-emerald-300 text-sm mt-1">{user?.name}</p>
        </div>
        <nav className="flex-1 px-4 py-4 space-y-2">
          <Link to="/librarian" className="flex items-center gap-3 p-3 rounded bg-emerald-800 text-white">
            <Users size={20} />
            Circulation Desk
          </Link>
        </nav>
        <div className="p-4 border-t border-emerald-800">
          <button onClick={logout} className="flex items-center gap-3 p-3 w-full rounded text-emerald-300 hover:bg-emerald-800 transition-colors">
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </div>
      <div className="flex-1 p-8 overflow-y-auto">
        <Routes>
          <Route path="/" element={<Circulation />} />
        </Routes>
      </div>
    </div>
  );
}
