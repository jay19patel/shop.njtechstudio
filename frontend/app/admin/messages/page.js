"use client";

import React, { useState, useEffect } from 'react';
import Navbar from '../../../components/Navbar';
import Footer from '../../../components/Footer';
import { useAuth } from '../../../context/AuthContext';
import { useRouter } from 'next/navigation';
import { getAdminMessages, updateAdminMessage, deleteAdminMessage } from '../../../lib/api';
import { Mail, Search, Trash2, CheckCircle2, Circle, ChevronLeft, Loader2, AlertTriangle, MessageSquare } from 'lucide-react';
import Link from 'next/link';

export default function AdminMessagesPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [deleting, setDeleting] = useState(false);
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) router.push('/login');
    else if (!authLoading && isAuthenticated && !user?.is_superuser) router.push('/profile');
  }, [authLoading, isAuthenticated, user, router]);

  useEffect(() => {
    if (isAuthenticated && user?.is_superuser) fetchMessages();
  }, [isAuthenticated, user]);

  const fetchMessages = async () => {
    try {
      setLoading(true);
      const data = await getAdminMessages();
      setMessages(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const toggleRead = async (msg) => {
    try {
      await updateAdminMessage(msg.id, { is_read: !msg.is_read });
      setMessages(prev => prev.map(m => m.id === msg.id ? { ...m, is_read: !m.is_read } : m));
    } catch (err) {
      console.error(err);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await deleteAdminMessage(deleteTarget.id);
      setMessages(prev => prev.filter(m => m.id !== deleteTarget.id));
      setDeleteTarget(null);
    } catch (err) {
      console.error(err);
    } finally {
      setDeleting(false);
    }
  };

  const filteredMessages = messages.filter(m =>
    (m.name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (m.email || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (m.subject || '').toLowerCase().includes(searchTerm.toLowerCase())
  );

  const unreadCount = messages.filter(m => !m.is_read).length;

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
              <h1 className="text-2xl font-bold text-slate-900">Inbox</h1>
              <p className="text-xs text-slate-400 mt-0.5">
                {messages.length} messages{unreadCount > 0 && ` · ${unreadCount} unread`}
              </p>
            </div>
            {unreadCount > 0 && (
              <div className="flex items-center gap-2 px-3 py-2 bg-orange-50 border border-orange-200 rounded-lg text-xs font-semibold text-orange-700">
                <Mail className="w-3.5 h-3.5" />
                {unreadCount} unread message{unreadCount !== 1 ? 's' : ''}
              </div>
            )}
          </div>

          {/* Table */}
          <div className="bg-white border border-slate-200 rounded-xl overflow-hidden">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 px-6 py-4 border-b border-slate-100">
              <div className="flex items-center gap-3">
                <h2 className="text-sm font-bold text-slate-900">All Messages</h2>
                <span className="text-xs text-slate-400 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">{filteredMessages.length}</span>
              </div>
              <div className="relative w-full sm:w-64">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search messages..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full bg-slate-50 border border-slate-200 rounded-lg py-2 pl-9 pr-3 text-sm outline-none focus:border-slate-400 focus:bg-white transition-all"
                />
              </div>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full text-left min-w-[700px]">
                <thead>
                  <tr className="border-b border-slate-100 bg-slate-50/50">
                    <th className="px-6 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider w-10">Read</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Sender</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Subject</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Message</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider">Date</th>
                    <th className="px-4 py-3 text-[10px] font-bold text-slate-400 uppercase tracking-wider text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredMessages.length === 0 ? (
                    <tr>
                      <td colSpan="6" className="px-6 py-16 text-center">
                        <div className="flex flex-col items-center gap-2 text-slate-400">
                          <MessageSquare className="w-8 h-8" />
                          <span className="text-sm">No messages found</span>
                        </div>
                      </td>
                    </tr>
                  ) : filteredMessages.map((msg) => (
                    <React.Fragment key={msg.id}>
                      <tr
                        className={`border-b border-slate-50 hover:bg-slate-50 transition-colors group cursor-pointer ${!msg.is_read ? 'bg-indigo-50/30' : ''}`}
                        onClick={() => setExpanded(expanded === msg.id ? null : msg.id)}
                      >
                        {/* Read toggle */}
                        <td className="px-6 py-4 align-top" onClick={(e) => { e.stopPropagation(); toggleRead(msg); }}>
                          <button title={msg.is_read ? 'Mark unread' : 'Mark read'} className="mt-0.5">
                            {msg.is_read
                              ? <CheckCircle2 className="w-4 h-4 text-slate-300 hover:text-slate-500 transition-colors" />
                              : <Circle className="w-4 h-4 text-indigo-500 fill-indigo-100 hover:text-indigo-600 transition-colors" />
                            }
                          </button>
                        </td>
                        {/* Sender */}
                        <td className="px-4 py-4 align-top">
                          <div className="flex flex-col gap-0.5">
                            <span className={`text-sm ${!msg.is_read ? 'font-bold text-slate-900' : 'font-medium text-slate-700'}`}>{msg.name}</span>
                            <span className="text-xs text-slate-400">{msg.email}</span>
                          </div>
                        </td>
                        {/* Subject */}
                        <td className="px-4 py-4 align-top max-w-[200px]">
                          <span className={`text-sm line-clamp-1 ${!msg.is_read ? 'font-semibold text-slate-900' : 'text-slate-600'}`}>{msg.subject}</span>
                        </td>
                        {/* Message preview */}
                        <td className="px-4 py-4 align-top max-w-[240px]">
                          <p className="text-xs text-slate-500 line-clamp-2">{msg.message}</p>
                        </td>
                        {/* Date */}
                        <td className="px-4 py-4 align-top whitespace-nowrap">
                          <span className="text-xs text-slate-400">
                            {new Date(msg.created_at).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                          </span>
                        </td>
                        {/* Actions */}
                        <td className="px-4 py-4 align-top text-right" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => setDeleteTarget(msg)}
                            className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors opacity-0 group-hover:opacity-100"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>

                      {/* Expanded message body */}
                      {expanded === msg.id && (
                        <tr className="border-b border-slate-100 bg-slate-50">
                          <td colSpan="6" className="px-6 py-4">
                            <div className="max-w-2xl">
                              <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-2">Full Message</p>
                              <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{msg.message}</p>
                              <a href={`mailto:${msg.email}`} className="inline-flex items-center gap-1.5 mt-3 text-xs text-indigo-600 hover:underline font-semibold">
                                <Mail className="w-3.5 h-3.5" /> Reply to {msg.email}
                              </a>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </main>

      <Footer />

      {/* Delete Confirm */}
      {deleteTarget && (
        <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl w-full max-w-sm shadow-2xl p-6 flex flex-col gap-5">
            <div className="flex items-start gap-3">
              <div className="w-9 h-9 bg-red-50 rounded-lg flex items-center justify-center flex-shrink-0">
                <AlertTriangle className="w-4 h-4 text-red-500" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-900">Delete Message?</h3>
                <p className="text-xs text-slate-500 mt-1">Message from <span className="font-semibold text-slate-700">{deleteTarget.name}</span> will be permanently deleted.</p>
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <button onClick={() => setDeleteTarget(null)} disabled={deleting} className="px-4 py-2 text-xs font-bold uppercase tracking-wider text-slate-500 hover:bg-slate-50 rounded-lg transition-colors">Cancel</button>
              <button onClick={confirmDelete} disabled={deleting} className="flex items-center gap-1.5 px-4 py-2 bg-red-600 text-white text-xs font-bold uppercase tracking-wider rounded-lg hover:bg-red-700 transition-colors disabled:opacity-60">
                {deleting && <Loader2 className="w-3 h-3 animate-spin" />} Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
