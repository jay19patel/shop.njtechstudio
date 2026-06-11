'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { getCategories } from '../lib/api';

const Categories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => setCategories([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <section id="categories" className="w-full flex flex-col gap-10 py-8">
      <div className="flex flex-col gap-2 mb-2 text-center md:text-left">
        <span className="text-slate-500 font-semibold text-xs uppercase tracking-wider">Browse Collections</span>
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
          Categories
        </h2>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {loading
          ? Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-2xl overflow-hidden animate-pulse border border-slate-100">
                <div className="aspect-square bg-slate-100" />
              </div>
            ))
          : categories.map((cat) => (
              <Link
                href={`/shop?category_id=${cat.id}`}
                key={cat.id}
                className="group flex flex-col gap-3 cursor-pointer"
              >
                <div className="aspect-square relative rounded-2xl overflow-hidden bg-slate-50 border border-slate-100 transition-all duration-300">
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
