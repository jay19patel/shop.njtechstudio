"use client";

import React, { useState, useEffect } from 'react';
import Navbar from '../../../components/Navbar';
import Footer from '../../../components/Footer';
import { useAuth } from '../../../context/AuthContext';
import { useRouter } from 'next/navigation';
import { getAdminStats, getAdminOrders, updateAdminOrder } from '../../../lib/api';
import { Package, ShoppingBag, Banknote, Clock, ChevronLeft, Loader2, Search, ExternalLink, Image as ImageIcon, Mail, FileText, TrendingUp, Users } from 'lucide-react';
import Link from 'next/link';

export default function AdminDashboardPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  const [stats, setStats] = useState(null);
  const [orders, setOrders] = useState([]);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [updating, setUpdating] = useState(null);
  const [showUsersModal, setShowUsersModal] = useState(false);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.push('/login');
    else if (!authLoading && isAuthenticated && !user?.is_superuser) router.push('/profile');
  }, [authLoading, isAuthenticated, user, router]);

  useEffect(() => {
    if (isAuthenticated && user?.is_superuser) fetchData();
  }, [isAuthenticated, user]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsData, ordersData] = await Promise.all([getAdminStats(), getAdminOrders()]);
      setStats(statsData);
      setOrders(ordersData);
    } catch (err) {
      setError('Failed to load admin data');
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('auth_token') : ''}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch');
      // Fetch all users from Django admin endpoint
      const res = await fetch('/api/admin/users/', {
        headers: {
          'Authorization': `Bearer ${typeof window !== 'undefined' ? localStorage.getItem('auth_token') : ''}`
        }
      });
      const data = await res.json();
      setUsers(data.results || data || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleStatusUpdate = async (orderId, field, value) => {
    setUpdating(orderId);
    try {
      await updateAdminOrder(orderId, { [field]: value });
      setOrders(orders.map(o => o.id === orderId ? { ...o, [field]: value } : o));
      if (field === 'status' || field === 'payment_status') getAdminStats().then(setStats);
    } catch (err) {
      alert('Failed to update order');
    } finally {
      setUpdating(null);
    }
  };

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

  const filteredOrders = orders.filter(o =>
    String(o.id).includes(searchTerm) ||
    (o.customer_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (o.customer_email || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const statCards = [
    { label: 'Revenue', value: `₹${Number(stats?.total_revenue || 0).toLocaleString('en-IN')}`, icon: Banknote },
    { label: 'Orders', value: stats?.total_orders ?? 0, icon: ShoppingBag },
    { label: 'Users', value: stats?.total_users ?? 0, icon: Users },
    { label: 'Pending', value: stats?.pending_orders ?? 0, icon: Clock, highlight: (stats?.pending_orders || 0) > 0 },
    { label: 'Products', value: stats?.total_products ?? 0, icon: Package, href: '/admin/products' },
    { label: 'Messages', value: stats?.total_messages ?? 0, icon: Mail, href: '/admin/messages', badge: stats?.unread_messages > 0 ? stats.unread_messages : null },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
      <Navbar />

      <main className="flex-grow w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="flex flex-col gap-8">

          {/* ── Header ── */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
            <div>
              <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-1">Admin</p>
              <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/admin/products" className="px-4 py-2 bg-slate-900 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-800 transition-colors flex items-center gap-2">
                <Package className="w-3.5 h-3.5" /> Products
              </Link>
              <button onClick={() => { setShowUsersModal(true); fetchUsers(); }} className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2">
                <Users className="w-3.5 h-3.5" /> Users
              </button>
              <Link href="/admin/messages" className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2">
                <Mail className="w-3.5 h-3.5" /> Inbox
                {(stats?.unread_messages || 0) > 0 && (
                  <span className="bg-orange-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{stats.unread_messages}</span>
                )}
              </Link>
              <button onClick={fetchData} className="px-4 py-2 bg-white border border-slate-200 text-slate-600 text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-slate-50 transition-colors">
                Refresh
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>
          )}

          {/* ── Stats ── */}
          {stats && (
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
              {statCards.map(({ label, value, icon: Icon, highlight, href, badge }) => {
                const card = (
                  <div className={`bg-white border rounded-xl p-5 flex flex-col gap-3 ${highlight ? 'border-orange-200 bg-orange-50/30' : 'border-slate-200'} ${href ? 'hover:border-slate-300 hover:shadow-sm transition-all cursor-pointer' : ''}`}>
                    <div className="flex items-center justify-between">
                      <Icon className={`w-4 h-4 ${highlight ? 'text-orange-500' : 'text-slate-400'}`} />
                      {badge && <span className="bg-orange-500 text-white text-[10px] font-bold px-1.5 py-0.5 rounded-full">{badge} new</span>}
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 font-medium uppercase tracking-wider">{label}</p>
                      <p className={`text-xl font-bold mt-0.5 ${highlight ? 'text-orange-600' : 'text-slate-900'}`}>{value}</p>
                    </div>
                  </div>
                );
                return href ? <Link key={label} href={href}>{card}</Link> : <div key={label}>{card}</div>;
              })}
            </div>
          )}

          {/* ── Orders Table ── */}
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            {/* Table header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-bold text-slate-900">Recent Orders</h2>
                <span className="text-xs text-slate-400 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">{orders.length}</span>
              </div>
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search orders..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-9 pr-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[900px]">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/50">
                    <th className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Order</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Customer</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Payment Info</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Payment</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Invoice</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredOrders.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-12 text-center text-sm text-slate-400">No orders found.</td>
                    </tr>
                  ) : filteredOrders.map((order) => (
                    <tr key={order.id} className="border-b border-slate-50 hover:bg-slate-50 transition-colors group">
                      {/* Order */}
                      <td className="px-6 py-4 align-top">
                        <div className="flex flex-col gap-0.5">
                          <Link href={`/orders/${order.id}`} className="font-bold text-sm text-indigo-600 hover:underline flex items-center gap-1">
                            #{order.id}
                            <ExternalLink className="w-3 h-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                          </Link>
                          <span className="text-xs text-slate-400">{new Date(order.created_at).toLocaleDateString('en-IN')}</span>
                          <span className="text-xs text-slate-500 font-medium mt-0.5">{order.items?.length || 0} item{order.items?.length !== 1 ? 's' : ''} · ₹{Number(order.total_amount).toLocaleString('en-IN')}</span>
                        </div>
                      </td>
                      {/* Customer */}
                      <td className="px-4 py-4 align-top">
                        <div className="flex flex-col gap-0.5">
                          <span className="font-semibold text-sm text-slate-800">{order.customer_name || '—'}</span>
                          <span className="text-xs text-slate-400">{order.customer_email || '—'}</span>
                          <span className="text-xs text-slate-400">{order.customer_phone || '—'}</span>
                        </div>
                      </td>
                      {/* Payment info */}
                      <td className="px-4 py-4 align-top">
                        <div className="flex flex-col gap-1.5">
                          {order.payment_reference && (
                            <span className="font-mono text-xs bg-slate-100 px-2 py-0.5 rounded w-fit text-slate-600">{order.payment_reference}</span>
                          )}
                          {order.screenshot_url ? (
                            <a href={order.screenshot_url} target="_blank" rel="noreferrer" className="text-xs text-indigo-600 hover:underline font-medium flex items-center gap-1">
                              <ImageIcon className="w-3 h-3" /> Screenshot
                            </a>
                          ) : (
                            <span className="text-xs text-slate-300">No screenshot</span>
                          )}
                        </div>
                      </td>
                      {/* Payment status */}
                      <td className="px-4 py-4 align-top">
                        <select
                          value={order.payment_status}
                          onChange={(e) => handleStatusUpdate(order.id, 'payment_status', e.target.value)}
                          disabled={updating === order.id}
                          className={`text-xs font-semibold rounded-lg px-2.5 py-1.5 border outline-none cursor-pointer appearance-none transition-colors ${
                            order.payment_status === 'VERIFIED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                            order.payment_status === 'RECEIVED' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                            order.payment_status === 'FAILED' ? 'bg-red-50 text-red-700 border-red-200' :
                            'bg-orange-50 text-orange-700 border-orange-200'
                          }`}
                        >
                          <option value="PENDING">Pending</option>
                          <option value="RECEIVED">Received</option>
                          <option value="VERIFIED">Verified</option>
                          <option value="FAILED">Failed</option>
                        </select>
                      </td>
                      {/* Order status */}
                      <td className="px-4 py-4 align-top">
                        <select
                          value={order.status}
                          onChange={(e) => handleStatusUpdate(order.id, 'status', e.target.value)}
                          disabled={updating === order.id}
                          className={`text-xs font-semibold rounded-lg px-2.5 py-1.5 border outline-none cursor-pointer appearance-none transition-colors ${
                            order.status === 'DELIVERED' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' :
                            order.status === 'SHIPPED' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                            order.status === 'CANCELLED' ? 'bg-red-50 text-red-700 border-red-200' :
                            order.status === 'PROCESSING' ? 'bg-indigo-50 text-indigo-700 border-indigo-200' :
                            'bg-slate-50 text-slate-600 border-slate-200'
                          }`}
                        >
                          <option value="PENDING">Pending</option>
                          <option value="PROCESSING">Processing</option>
                          <option value="SHIPPED">Shipped</option>
                          <option value="DELIVERED">Delivered</option>
                          <option value="CANCELLED">Cancelled</option>
                        </select>
                      </td>
                      {/* Invoice */}
                      <td className="px-4 py-4 align-top">
                        <Link href={`/orders/${order.id}/invoice`} target="_blank"
                          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors">
                          <FileText className="w-3 h-3" /> Invoice
                        </Link>
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

      {/* Users Modal */}
      {showUsersModal && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={(e) => e.target === e.currentTarget && setShowUsersModal(false)}>
          <div className="bg-white rounded-xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center">
              <h3 className="text-base font-bold text-slate-900">All Users ({users.length})</h3>
              <button onClick={() => setShowUsersModal(false)} className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-6">
              {users.length === 0 ? (
                <div className="text-center py-8 text-slate-400">
                  <Users className="w-12 h-12 mx-auto mb-2 opacity-50" />
                  <p>No users found</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {users.map((user) => (
                    <div key={user.id || user.pk} className="border border-slate-200 rounded-lg p-4 hover:bg-slate-50 transition-colors">
                      <div className="flex items-start justify-between">
                        <div>
                          <h4 className="font-semibold text-slate-900">{user.first_name && user.last_name ? `${user.first_name} ${user.last_name}` : user.username}</h4>
                          <p className="text-xs text-slate-500 mt-1">{user.email}</p>
                          <div className="mt-2 flex items-center gap-2">
                            {user.is_superuser && (
                              <span className="text-[9px] font-bold uppercase tracking-widest bg-slate-900 text-white px-2 py-0.5 rounded-full">Admin</span>
                            )}
                            {user.is_staff && !user.is_superuser && (
                              <span className="text-[9px] font-bold uppercase tracking-widest bg-slate-400 text-white px-2 py-0.5 rounded-full">Staff</span>
                            )}
                            {!user.is_superuser && !user.is_staff && (
                              <span className="text-[9px] font-bold uppercase tracking-widest bg-slate-200 text-slate-700 px-2 py-0.5 rounded-full">User</span>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] text-slate-400">ID: {user.id || user.pk}</p>
                          {user.date_joined && (
                            <p className="text-[10px] text-slate-400 mt-1">Joined: {new Date(user.date_joined).toLocaleDateString('en-IN')}</p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
