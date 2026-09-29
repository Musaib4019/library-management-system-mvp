import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { Routes, Route, Link, useNavigate, useLocation } from 'react-router-dom';
import api from '../../lib/api';
import { LayoutDashboard, Users, BookCopy, FileText, LogOut, Search } from 'lucide-react';

function DashboardHome() {
  const [stats, setStats] = useState(null);
  useEffect(() => {
    api.get('/dashboard/stats').then(res => setStats(res.data)).catch(console.error);
  }, []);

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Dashboard Overview</h2>
      {stats && (
        <div className="grid grid-cols-4 gap-4 mb-8">
          <div className="bg-white p-6 rounded shadow-sm border border-slate-100">
            <h3 className="text-slate-500 text-sm font-medium">Total Books</h3>
            <p className="text-3xl font-bold text-slate-800">{stats.total_books}</p>
          </div>
          <div className="bg-white p-6 rounded shadow-sm border border-slate-100">
            <h3 className="text-slate-500 text-sm font-medium">Available Copies</h3>
            <p className="text-3xl font-bold text-slate-800">{stats.available_copies}</p>
          </div>
          <div className="bg-white p-6 rounded shadow-sm border border-slate-100">
            <h3 className="text-slate-500 text-sm font-medium">Issued Books</h3>
            <p className="text-3xl font-bold text-slate-800">{stats.issued_copies}</p>
          </div>
          <div className="bg-white p-6 rounded shadow-sm border border-slate-100">
            <h3 className="text-slate-500 text-sm font-medium">Total Members</h3>
            <p className="text-3xl font-bold text-slate-800">{stats.total_members}</p>
          </div>
        </div>
      )}
    </div>
  );
}

function ManageBooks() {
  const [books, setBooks] = useState([]);
  const [title, setTitle] = useState('');
  const [author, setAuthor] = useState('');
  const [isbn, setIsbn] = useState('');
  const [category, setCategory] = useState('');
  const [copies, setCopies] = useState(1);

  useEffect(() => {
    fetchBooks();
  }, []);

  const fetchBooks = () => {
    api.get('/books').then(res => setBooks(res.data)).catch(console.error);
  };

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await api.post('/books', {
        title, author, isbn, category, publisher: "Unknown", year: 2024, description: "", total_copies: copies
      });
      fetchBooks();
      setTitle(''); setAuthor(''); setIsbn(''); setCategory(''); setCopies(1);
    } catch (err) {
      alert("Error adding book");
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Manage Books</h2>
      <div className="bg-white p-6 rounded shadow-sm mb-8">
        <h3 className="text-lg font-medium mb-4">Add New Book</h3>
        <form onSubmit={handleAdd} className="grid grid-cols-2 gap-4">
          <input className="border p-2 rounded" placeholder="Title" value={title} onChange={e=>setTitle(e.target.value)} required />
          <input className="border p-2 rounded" placeholder="Author" value={author} onChange={e=>setAuthor(e.target.value)} required />
          <input className="border p-2 rounded" placeholder="ISBN" value={isbn} onChange={e=>setIsbn(e.target.value)} required />
          <input className="border p-2 rounded" placeholder="Category" value={category} onChange={e=>setCategory(e.target.value)} required />
          <input className="border p-2 rounded" type="number" placeholder="Copies" value={copies} onChange={e=>setCopies(Number(e.target.value))} required />
          <button type="submit" className="bg-blue-600 text-white rounded p-2">Add Book</button>
        </form>
      </div>

      <div className="bg-white rounded shadow-sm overflow-hidden">
        <table className="w-full text-left">
          <thead className="bg-slate-50 text-slate-600">
            <tr>
              <th className="p-4">Title</th>
              <th className="p-4">Author</th>
              <th className="p-4">ISBN</th>
              <th className="p-4">Available / Total</th>
            </tr>
          </thead>
          <tbody>
            {books.map(b => (
              <tr key={b.id} className="border-t">
                <td className="p-4">{b.title}</td>
                <td className="p-4">{b.author}</td>
                <td className="p-4">{b.isbn}</td>
                <td className="p-4">{b.available_copies} / {b.total_copies}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function ManageMembers() {
  const [members, setMembers] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedMember, setSelectedMember] = useState(null);
  const [loans, setLoans] = useState([]);

  useEffect(() => {
    api.get('/users?search=' + search).then(res => setMembers(res.data.filter(u => u.role === 'MEMBER')));
  }, [search]);

  const selectMember = async (member) => {
    setSelectedMember(member);
    const res = await api.get(`/users/${member.id}/loans`);
    setLoans(res.data);
  };

  const returnBook = async (loanId) => {
    try {
      await api.post(`/loans/${loanId}/return`);
      alert("Book returned successfully");
      selectMember(selectedMember); // Refresh
    } catch (e) {
      alert("Error returning book");
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Manage Members (Issue / Return)</h2>
      <div className="flex gap-6">
        <div className="w-1/3 bg-white p-4 rounded shadow-sm h-fit">
          <div className="relative mb-4">
            <Search className="absolute left-3 top-3 text-slate-400" size={18}/>
            <input 
              className="w-full border p-2 pl-10 rounded" 
              placeholder="Search members..." 
              value={search} onChange={e => setSearch(e.target.value)} 
            />
          </div>
          <ul className="space-y-2">
            {members.map(m => (
              <li 
                key={m.id} 
                onClick={() => selectMember(m)}
                className={`p-3 rounded cursor-pointer ${selectedMember?.id === m.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-slate-50 border border-transparent'}`}
              >
                {m.name}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="w-2/3">
          {selectedMember ? (
            <div className="bg-white p-6 rounded shadow-sm">
              <h3 className="text-xl font-bold mb-4">{selectedMember.name}'s Profile</h3>
              <h4 className="font-semibold mb-2">Currently Issued Books</h4>
              {loans.filter(l => l.status === 'ACTIVE').length === 0 ? (
                <p className="text-slate-500">No active loans.</p>
              ) : (
                <ul className="space-y-3">
                  {loans.filter(l => l.status === 'ACTIVE').map(l => (
                    <li key={l.id} className="border p-4 rounded flex justify-between items-center">
                      <div>
                        <p className="font-semibold">{l.copy.book.title}</p>
                        <p className="text-sm text-slate-500">Due: {new Date(l.due_date).toLocaleDateString()}</p>
                      </div>
                      <button onClick={() => returnBook(l.id)} className="bg-green-600 text-white px-4 py-2 rounded">
                        Return Book
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          ) : (
            <div className="bg-white p-6 rounded shadow-sm text-center text-slate-500">
              Select a member to view details and process returns.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default function AdminDashboard() {
  const { logout, user } = useAuth();
  const location = useLocation();
  
  const navItems = [
    { path: '/admin', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/admin/books', label: 'Manage Books', icon: BookCopy },
    { path: '/admin/members', label: 'Manage Members', icon: Users },
  ];

  return (
    <div className="flex h-screen bg-slate-50">
      <div className="w-64 bg-slate-900 text-white flex flex-col">
        <div className="p-6">
          <h1 className="text-xl font-bold">Admin Portal</h1>
          <p className="text-slate-400 text-sm mt-1">{user?.name}</p>
        </div>
        <nav className="flex-1 px-4 space-y-2">
          {navItems.map(item => {
            const Icon = item.icon;
            const active = location.pathname === item.path;
            return (
              <Link 
                key={item.path} 
                to={item.path} 
                className={`flex items-center gap-3 p-3 rounded ${active ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-800'}`}
              >
                <Icon size={20} />
                {item.label}
              </Link>
            )
          })}
        </nav>
        <div className="p-4">
          <button onClick={logout} className="flex items-center gap-3 p-3 w-full rounded text-slate-300 hover:bg-slate-800">
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </div>
      <div className="flex-1 p-8 overflow-y-auto">
        <Routes>
          <Route path="/" element={<DashboardHome />} />
          <Route path="/books" element={<ManageBooks />} />
          <Route path="/members" element={<ManageMembers />} />
        </Routes>
      </div>
    </div>
  );
}
