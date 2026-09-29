import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import { BookOpen } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const user = await login(email, password);
      if (user.role === 'ADMIN') navigate('/admin');
      else if (user.role === 'LIBRARIAN') navigate('/librarian');
      else navigate('/member');
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100">
      <div className="bg-white p-8 rounded-xl shadow-lg w-full max-w-md">
        <div className="flex flex-col items-center mb-8">
          <BookOpen size={48} className="text-blue-600 mb-4" />
          <h1 className="text-2xl font-bold text-slate-800">Library System</h1>
          <p className="text-slate-500">Sign in to your account</p>
        </div>
        
        {error && <div className="bg-red-50 text-red-600 p-3 rounded mb-4 text-sm text-center">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email</label>
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-slate-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
            <input 
              type="password" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-slate-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              required 
            />
          </div>
          <button 
            type="submit" 
            className="w-full bg-blue-600 text-white rounded py-2 hover:bg-blue-700 font-medium transition-colors"
          >
            Sign In
          </button>
        </form>
        
        <div className="mt-6 text-xs text-slate-500 text-center">
          <p>Demo accounts: admin@library.edu, librarian@library.edu, member1@library.edu</p>
          <p>Password for all: password123</p>
        </div>
      </div>
    </div>
  );
}
