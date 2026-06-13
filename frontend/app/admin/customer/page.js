"use client";

import React, { useState, useEffect } from 'react';
import Navbar from '../../../components/Navbar';
import Footer from '../../../components/Footer';
import { useAuth } from '../../../context/AuthContext';
import { useRouter } from 'next/navigation';
import { Search, ChevronLeft, Loader2, Mail, Calendar, Shield, User } from 'lucide-react';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api";

async function apiFetch(path, options = {}) {
  const cleanPath = path.startsWith("/") ? path : `/${path}`;
  const url = `${API_BASE}${cleanPath}`;
  const { requireAuth = true, ...fetchOptions } = options;

  let authHeader = {};
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("auth_token");
    if (requireAuth && token) {
      authHeader = { Authorization: `Bearer ${token}` };
    }
  }

  const headers = {
    "Content-Type": "application/json",
    ...authHeader,
    ...fetchOptions.headers,
  };

  const res = await fetch(url, {
    ...fetchOptions,
    headers,
  });

  if (!res.ok) {
    const body = await res.json();
    throw new Error(body?.detail || body?.message || `API error ${res.status}`);
  }

  return res.json();
}

export default function AdminCustomerPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.push('/login');
    else if (!authLoading && isAuthenticated && !user?.is_superuser) router.push('/profile');
  }, [authLoading, isAuthenticated, user, router]);

  useEffect(() => {
    if (isAuthenticated && user?.is_superuser) fetchCustomers();
  }, [isAuthenticated, user]);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const data = await apiFetch('/admin/users/', { requireAuth: true });
      setCustomers(data.results || data || []);
    } catch (err) {
      console.error('Failed to load customers:', err);
    } finally {
      setLoading(false);
    }
  };

  const filteredCustomers = customers.filter(c =>
    c.username?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (c.first_name && c.last_name && `${c.first_name} ${c.last_name}`.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-white flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <Loader2 className="w-8 h-8 text-slate-400 animate-spin" />
        </main>
      </div>
    );
  }

  if (!user?.is_superuser) return null;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <Navbar />

      <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col gap-8">

          {/* Header */}
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <Link href="/admin/dashboard" className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-700 uppercase tracking-wider font-bold mb-1 w-fit transition-colors">
                <ChevronLeft className="w-3.5 h-3.5" /> Dashboard
              </Link>
              <h1 className="text-2xl font-bold text-slate-900">Customers</h1>
              <p className="text-xs text-slate-400 mt-0.5">{customers.length} total customers</p>
            </div>
          </div>

          {/* Table */}
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-bold text-slate-900">All Customers</h2>
                <span className="text-xs text-slate-400 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">{filteredCustomers.length}</span>
              </div>
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search customers..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-9 pr-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[800px]">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/50">
                    <th className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Name</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Email</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Role</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Joined</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCustomers.length === 0 ? (
                    <tr>
                      <td colSpan="5" className="px-6 py-12 text-center">
                        <div className="flex flex-col items-center gap-2 text-slate-400">
                          <User className="w-8 h-8" />
                          <span className="text-sm">No customers found</span>
                        </div>
                      </td>
                    </tr>
                  ) : filteredCustomers.map((customer) => (
                    <tr key={customer.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors">
                      <td className="px-6 py-4 align-middle">
                        <div className="flex flex-col gap-0.5">
                          <span className="font-semibold text-sm text-slate-900">
                            {customer.first_name && customer.last_name ? `${customer.first_name} ${customer.last_name}` : customer.username}
                          </span>
                          <span className="text-[10px] text-slate-400 font-mono">ID: {customer.id}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 align-middle">
                        <div className="flex items-center gap-2">
                          <Mail className="w-3.5 h-3.5 text-slate-300" />
                          <span className="text-xs text-slate-600 font-mono">{customer.email}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 align-middle">
                        <div className="flex items-center gap-2">
                          {customer.is_superuser && (
                            <span className="text-[10px] font-bold uppercase tracking-widest bg-slate-900 text-white px-2.5 py-1 rounded-md flex items-center gap-1">
                              <Shield className="w-3 h-3" /> Admin
                            </span>
                          )}
                          {customer.is_staff && !customer.is_superuser && (
                            <span className="text-[10px] font-bold uppercase tracking-widest bg-slate-500 text-white px-2.5 py-1 rounded-md">Staff</span>
                          )}
                          {!customer.is_superuser && !customer.is_staff && (
                            <span className="text-[10px] font-bold uppercase tracking-widest bg-slate-200 text-slate-700 px-2.5 py-1 rounded-md">User</span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 align-middle">
                        <div className="flex items-center gap-2">
                          <Calendar className="w-3.5 h-3.5 text-slate-300" />
                          <span className="text-xs text-slate-600">
                            {customer.date_joined ? new Date(customer.date_joined).toLocaleDateString('en-IN') : '—'}
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4 align-middle">
                        <span className={`text-[10px] font-bold uppercase tracking-wider px-2.5 py-1 rounded-md ${
                          customer.is_active ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'
                        }`}>
                          {customer.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </main>

      <Footer />
    </div>
  );
}
