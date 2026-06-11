'use client';
import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { getProducts, normalizeProduct, getCategories } from '../lib/api';

const SkeletonCard = () => (
  <div className="flex flex-col gap-4 animate-pulse">
    <div className="aspect-square rounded-2xl bg-slate-100" />
    <div className="flex flex-col gap-2 px-1">
      <div className="h-4 bg-slate-100 rounded w-3/4" />
      <div className="h-3 bg-slate-100 rounded w-1/4" />
    </div>
  </div>
);

const Products = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch(() => setCategories([]));
  }, []);

  const fetchProducts = () => {
    setLoading(true);
    const params = { page_size: 8 };
    if (selectedCategory !== 'all') params.category_id = selectedCategory;
    if (searchQuery.trim()) params.search = searchQuery.trim();

    getProducts(params)
      .then((data) => setProducts((data?.results ?? []).map(normalizeProduct)))
      .catch(() => setProducts([]))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory]);

  return (
    <section id="products" className="w-full flex flex-col gap-10 py-8">
      
      {/* Search and Category Filters */}
      <div className="flex flex-col items-center gap-6 mb-4 px-4">
        {/* Search Bar */}
        <div className="relative w-full max-w-md">
          <input
            type="text"
            placeholder="Search products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                fetchProducts();
              }
            }}
            className="w-full pl-12 pr-4 py-3 rounded-full border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all shadow-sm"
          />
          <svg 
            className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {/* Category Filters */}
        <div className="flex flex-wrap justify-center gap-3">
          <button
            key="category-all"
            onClick={() => setSelectedCategory('all')}
            className={`px-6 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all duration-300 ${
              selectedCategory === 'all'
                ? 'bg-slate-900 text-white shadow-md'
                : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 shadow-sm'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-6 py-2 rounded-full text-xs font-bold uppercase tracking-wider transition-all duration-300 ${
                selectedCategory === cat.id
                  ? 'bg-slate-900 text-white shadow-md'
                  : 'bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 shadow-sm'
              }`}
            >
              {cat.name}
            </button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-x-6 gap-y-10">
        {loading
          ? Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)
          : products.map((prod) => (
              <Link
                href={`/shop/${prod.id}`}
                key={prod.id}
                className="flex flex-col group"
              >
                {/* Image Container */}
                <div className="aspect-square relative rounded-2xl overflow-hidden bg-slate-50 border border-slate-100 transition-all duration-300">
                  {prod.image ? (
                    <img
                      src={prod.image}
                      alt={prod.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-full bg-slate-50 flex items-center justify-center">
                      <svg className="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}
                  {(prod.tag || (prod.hasDiscount ? 'Offer' : null)) && (
                    <div className="absolute top-4 left-4 px-2.5 py-1 bg-white/90 backdrop-blur-md rounded-lg text-[9px] font-bold uppercase tracking-wider text-slate-700 shadow-sm border border-slate-100">
                      {prod.tag || 'Offer'}
                    </div>
                  )}
                </div>

                {/* Details Footer */}
                <div className="flex flex-col gap-1 mt-3.5 px-1">
                  <div className="flex justify-between items-start gap-2">
                    <h3 className="text-sm font-semibold text-slate-800 group-hover:text-slate-600 transition-colors duration-200 line-clamp-1">
                      {prod.name}
                    </h3>
                    <div className="flex flex-col items-end whitespace-nowrap shrink-0">
                      {prod.hasDiscount ? (
                        <>
                          <span className="text-sm font-bold text-slate-900">
                            {prod.discountedPriceDisplay}
                          </span>
                          <span className="text-[9px] font-medium text-slate-400 line-through">
                            {prod.priceDisplay}
                          </span>
                        </>
                      ) : (
                        <span className="text-sm font-bold text-slate-900">
                          {prod.priceDisplay}
                        </span>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-slate-500 font-medium capitalize">
                    {(typeof prod.category === 'object' ? prod.category?.name : prod.category) || 'Creations'}
                  </span>
                </div>
              </Link>
            ))}
      </div>

      <div className="flex justify-center mt-12">
        <Link
          href="/shop"
          className="px-6 py-3 bg-slate-900 text-white font-semibold text-xs uppercase tracking-wider rounded-xl hover:bg-slate-800 transition-all flex items-center gap-2"
        >
          Explore All Products
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="3.5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M17 8l4 4m0 0l-4 4m4-4H3" />
          </svg>
        </Link>
      </div>
    </section>
  );
};

export default Products;
