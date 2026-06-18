"use client";

import React, { useState, useEffect } from 'react';
import Navbar from '../../../components/Navbar';
import Footer from '../../../components/Footer';
import { useAuth } from '../../../context/AuthContext';
import { useRouter } from 'next/navigation';
import { getAdminDemandForecast } from '../../../lib/api';
import { Brain, ArrowLeft, Loader2, AlertTriangle, TrendingUp, Package, RefreshCw, BarChart2 } from 'lucide-react';
import Link from 'next/link';

export default function AdminInsightsPage() {
  const { user, isAuthenticated, loading: authLoading } = useAuth();
  const router = useRouter();

  const [data, setData] = useState({ product_demand: [], category_demand: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    } else if (!authLoading && isAuthenticated && !user?.is_superuser) {
      router.push('/profile');
    }
  }, [authLoading, isAuthenticated, user, router]);

  useEffect(() => {
    if (isAuthenticated && user?.is_superuser) {
      fetchDemandData();
    }
  }, [isAuthenticated, user]);

  const fetchDemandData = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getAdminDemandForecast();
      setData(result || { product_demand: [], category_demand: [] });
    } catch (err) {
      console.error(err);
      setError('Failed to load demand forecasting insights.');
    } finally {
      setLoading(false);
    }
  };

  if (authLoading || loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex flex-col">
        <Navbar />
        <main className="flex-grow flex items-center justify-center">
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-8 h-8 text-blue-600 animate-spin" />
            <p className="text-xs font-bold uppercase tracking-widest text-slate-400">Compiling demand matrix...</p>
          </div>
        </main>
        <Footer />
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
              <Link href="/admin/dashboard" className="inline-flex items-center gap-1.5 text-xs font-extrabold uppercase tracking-wider text-slate-400 hover:text-slate-800 mb-2 transition-all">
                <ArrowLeft className="w-3.5 h-3.5" /> Dashboard
              </Link>
              <h1 className="text-2xl font-black text-slate-950 uppercase tracking-tight flex items-center gap-2">
                <Brain className="w-7 h-7 text-blue-600" />
                AI Demand Forecasting & Stock Management
              </h1>
            </div>
            
            <div className="flex items-center gap-2">
              <button 
                onClick={fetchDemandData} 
                className="px-4 py-2.5 bg-white border border-slate-200 text-slate-700 text-xs font-bold uppercase tracking-wider rounded-xl hover:bg-slate-50 transition-colors flex items-center gap-2"
              >
                <RefreshCw className="w-3.5 h-3.5" /> Refresh Data
              </button>
            </div>
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-5 py-4 rounded-2xl flex items-center gap-3">
              <AlertTriangle className="w-5 h-5 flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Grid Layout */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            
            {/* Products demand table (takes 2 cols on desktop) */}
            <div className="lg:col-span-2 bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden flex flex-col">
              <div className="px-6 py-5 border-b border-slate-100 flex items-center justify-between">
                <h2 className="text-sm font-black text-blue-950 uppercase tracking-wider flex items-center gap-2">
                  <Package className="w-4 h-4 text-blue-600" />
                  Product Affinity & Inventory Levels
                </h2>
                <span className="bg-blue-50 text-blue-600 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                  Ranked by Demand
                </span>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-slate-50/50 border-b border-slate-100">
                      <th className="py-4 px-6 text-[10px] font-black uppercase tracking-widest text-slate-400">Product</th>
                      <th className="py-4 px-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Category</th>
                      <th className="py-4 px-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Demand Score</th>
                      <th className="py-4 px-4 text-[10px] font-black uppercase tracking-widest text-slate-400">In Stock</th>
                      <th className="py-4 px-4 text-[10px] font-black uppercase tracking-widest text-slate-400">Status</th>
                      <th className="py-4 px-6 text-[10px] font-black uppercase tracking-widest text-slate-400 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {data.product_demand.length === 0 ? (
                      <tr>
                        <td colSpan="6" className="py-16 text-center text-sm font-semibold text-slate-400">
                          No product interest data recorded yet. Radar will populate as clients interact.
                        </td>
                      </tr>
                    ) : (
                      data.product_demand.map((item, idx) => (
                        <tr key={item.product_id || idx} className="border-b border-slate-50 last:border-none hover:bg-slate-50/30 transition-all">
                          <td className="py-4 px-6 text-sm font-bold text-slate-900">{item.name}</td>
                          <td className="py-4 px-4 text-xs font-semibold text-slate-500">{item.category_name}</td>
                          <td className="py-4 px-4">
                            <div className="flex items-center gap-2">
                              <span className="text-sm font-extrabold text-blue-600">{item.score}</span>
                              <div className="w-16 bg-slate-100 h-1.5 rounded-full overflow-hidden hidden sm:block">
                                <div 
                                  className="bg-blue-600 h-full rounded-full" 
                                  style={{ width: `${Math.min(100, (item.score / 20) * 100)}%` }}
                                />
                              </div>
                            </div>
                          </td>
                          <td className="py-4 px-4 text-sm font-extrabold text-slate-900">{item.stock}</td>
                          <td className="py-4 px-4">
                            <span className={`inline-flex items-center px-2 py-1 rounded-lg text-[10px] font-black tracking-wider uppercase border ${
                              item.stock_status === 'OUT OF STOCK' ? 'bg-red-50 text-red-700 border-red-100' :
                              item.stock_status === 'CRITICAL LOW' ? 'bg-orange-50 text-orange-700 border-orange-100' :
                              item.stock_status === 'LOW STOCK' ? 'bg-yellow-50 text-yellow-700 border-yellow-100' :
                              'bg-green-50 text-green-700 border-green-100'
                            }`}>
                              {item.stock_status}
                            </span>
                          </td>
                          <td className="py-4 px-6 text-right">
                            <Link 
                              href={`/admin/products?search=${encodeURIComponent(item.name)}`}
                              className={`text-[10px] font-black uppercase tracking-widest px-3 py-2 rounded-xl transition-all ${
                                item.action === 'Restock Immediately' 
                                  ? 'bg-red-600 text-white hover:bg-red-700 shadow-md shadow-red-200' 
                                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                              }`}
                            >
                              {item.action === 'Restock Immediately' ? 'Restock' : 'Adjust'}
                            </Link>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Category Heatmap & Guidelines */}
            <div className="flex flex-col gap-6">
              
              {/* Category Heatmap */}
              <div className="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden">
                <div className="px-6 py-5 border-b border-slate-100">
                  <h2 className="text-sm font-black text-blue-950 uppercase tracking-wider flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-blue-600" />
                    Category Heatmap
                  </h2>
                </div>

                <div className="p-4">
                  <div className="flex flex-col gap-3">
                    {data.category_demand.length === 0 ? (
                      <p className="py-8 text-center text-xs font-semibold text-slate-400">No category demand logs.</p>
                    ) : (
                      data.category_demand.map((cat, idx) => {
                        const progressPct = Math.min(100, (cat.score / 30) * 100);
                        return (
                          <div key={cat.category_id || idx} className="p-4 bg-slate-50/50 rounded-2xl border border-slate-100 flex flex-col gap-2">
                            <div className="flex justify-between items-center text-xs">
                              <span className="font-bold text-slate-800">{cat.name}</span>
                              <span className="font-extrabold text-blue-600">{cat.score}</span>
                            </div>
                            <div className="w-full bg-slate-100 h-2 rounded-full overflow-hidden">
                              <div 
                                className="bg-blue-600 h-full rounded-full transition-all duration-500" 
                                style={{ width: `${progressPct}%` }}
                              />
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              </div>

              {/* Guide Card */}
              <div className="bg-slate-900 text-white rounded-3xl p-6 border border-slate-800 shadow-xl relative overflow-hidden">
                <div className="absolute right-0 bottom-0 opacity-10 transform translate-x-4 translate-y-4">
                  <Brain className="w-40 h-40" />
                </div>
                <h3 className="font-black text-sm uppercase tracking-widest text-blue-400 mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4" />
                  Forecasting Rules
                </h3>
                <p className="text-xs text-slate-300 leading-relaxed mb-4">
                  Aggregated scores reflect sum semantic interest calculations mapped dynamically to current inventory status:
                </p>
                <ul className="text-xs text-slate-400 flex flex-col gap-3 list-disc pl-4 font-semibold">
                  <li>
                    <strong className="text-red-400">Restock Recommended</strong>: AI score &ge; 5.0 and stock count &lt; 10.
                  </li>
                  <li>
                    <strong className="text-orange-400">Critical Low Stock</strong>: Stock is less than 5 items.
                  </li>
                  <li>
                    <strong className="text-yellow-400">Low Stock</strong>: Stock is less than 15 items.
                  </li>
                </ul>
              </div>

            </div>

          </div>

        </div>
      </main>

      <Footer />
    </div>
  );
}
