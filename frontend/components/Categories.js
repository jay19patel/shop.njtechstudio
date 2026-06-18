'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { getCategories, getUserInterests } from '../lib/api';
import { useAuth } from '../context/AuthContext';

const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const { isAuthenticated } = useAuth();
  const [interests, setInterests] = useState(null);
  const [interestsLoading, setInterestsLoading] = useState(false);

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => setCategories([]))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    if (isAuthenticated) {
      setInterestsLoading(true);
      getUserInterests()
        .then(setInterests)
        .catch(() => setInterests(null))
        .finally(() => setInterestsLoading(false));
    } else {
      setInterests(null);
    }
  }, [isAuthenticated]);

  return (
    <section id="categories" className="w-full max-w-5xl mx-auto flex flex-col gap-10 py-8">
      
      {/* Personalized User Interest Radar Widget */}
      <div className="w-full border border-slate-200 bg-slate-50 p-6 rounded-none flex flex-col gap-6">
        <div className="flex flex-col gap-1">
          <span className="text-indigo-600 font-bold text-[10px] uppercase tracking-widest">AI Shopping Profile</span>
          <h3 className="text-xl font-bold tracking-tight text-slate-900 uppercase">Your Interest Radar</h3>
          <p className="text-xs text-slate-500">Real-time interest ratings derived from your semantic browsing activity.</p>
        </div>

        {!isAuthenticated ? (
          <div className="text-xs text-slate-600 font-semibold uppercase tracking-wider">
            🔑 Please <Link href="/login" className="text-indigo-600 underline font-black">Login</Link> to view your personalized interest scores.
          </div>
        ) : interestsLoading ? (
          <div className="text-xs text-slate-400 font-semibold animate-pulse uppercase tracking-wider">
            Syncing semantic profile...
          </div>
        ) : interests && (interests.top_categories?.length > 0 || interests.top_products?.length > 0) ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            
            {/* Top Categories of Interest */}
            <div className="flex flex-col gap-3">
              <h4 className="text-xs font-black uppercase tracking-widest text-slate-400 border-b border-slate-200 pb-2">Top Categories</h4>
              <div className="flex flex-col gap-2">
                {interests.top_categories.map((cat) => (
                  <div key={cat.category_id} className="flex justify-between items-center text-xs border border-slate-200 bg-white p-3 rounded-none">
                    <div className="flex flex-col gap-0.5">
                      <span className="font-bold text-slate-800">{cat.name}</span>
                      <span className="text-[9px] text-slate-400 font-mono">ID: {cat.category_id}</span>
                    </div>
                    <span className="font-black bg-indigo-50 text-indigo-700 px-2 py-1 border border-indigo-100 font-mono">
                      {cat.score}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Top Products of Interest */}
            <div className="flex flex-col gap-3">
              <h4 className="text-xs font-black uppercase tracking-widest text-slate-400 border-b border-slate-200 pb-2">Top Products</h4>
              <div className="flex flex-col gap-2">
                {interests.top_products.map((prod) => (
                  <div key={prod.product_id} className="flex justify-between items-center text-xs border border-slate-200 bg-white p-3 rounded-none">
                    <div className="flex flex-col gap-0.5">
                      <span className="font-bold text-slate-800">{prod.name}</span>
                      <span className="text-[9px] text-slate-400 font-mono">ID: {prod.product_id}</span>
                    </div>
                    <span className="font-black bg-emerald-50 text-emerald-700 px-2 py-1 border border-emerald-100 font-mono">
                      {prod.score}
                    </span>
                  </div>
                ))}
              </div>
            </div>

          </div>
        ) : (
          <div className="text-xs text-slate-500 font-semibold uppercase tracking-wider">
            💡 Browse products or like them to build your shopping profile.
          </div>
        )}
      </div>

      {/* Main Categories Section */}
      <div className="flex flex-col gap-2 mb-2 text-center md:text-left">
        <span className="text-slate-500 font-semibold text-xs uppercase tracking-wider">Browse Collections</span>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
          Categories
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {loading
          ? Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-none overflow-hidden animate-pulse border border-slate-100">
                <div className="aspect-square bg-slate-100" />
              </div>
            ))
          : categories.map((cat) => (
              <Link
                href={`/shop?category_id=${cat.id}`}
                key={cat.id}
                className="group flex flex-col gap-3 cursor-pointer"
              >
                <div className="aspect-square relative rounded-none overflow-hidden bg-slate-50 border border-slate-100 transition-all duration-300">
                  {cat.img ? (
                    <img
                      src={cat.img}
                      alt={cat.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-full bg-slate-50 flex items-center justify-center">
                      <svg className="w-12 h-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}
                </div>
                <div className="flex flex-col px-1">
                  <h3 className="text-lg font-semibold text-slate-800 group-hover:text-slate-600 transition-colors duration-200">
                    {cat.name}
                  </h3>
                  {cat.description && (
                    <p className="text-sm text-slate-500 mt-1 line-clamp-2">
                      {cat.description}
                    </p>
                  )}
                </div>
              </Link>
            ))}
      </div>
    </section>
  );
};

export default Categories;
