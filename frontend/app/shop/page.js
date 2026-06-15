"use client";

import React, { useState, useEffect, useCallback, useRef } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import Link from 'next/link';
import { getProducts, getCategories, normalizeProduct, aiSearch, MEDIA_BASE } from '../../lib/api';

// ── Skeleton ───────────────────────────────────────────────────────────────
const SkeletonCard = () => (
  <div className="flex flex-col gap-6 w-full animate-pulse">
    <div className="aspect-square rounded-[32px] bg-slate-50" />
    <div className="flex flex-col gap-2 px-1">
      <div className="h-4 bg-slate-50 rounded-full w-3/4" />
      <div className="h-3 bg-slate-50 rounded-full w-1/3" />
    </div>
  </div>
);

// ── Filter Tag ─────────────────────────────────────────────────────────────
const FilterTag = ({ label, value }) => (
  <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-indigo-50 text-indigo-700 text-xs font-semibold border border-indigo-100">
    <span className="text-indigo-400">{label}</span>
    {value}
  </span>
);

// ── AI Result Card ─────────────────────────────────────────────────────────
const AIProductCard = ({ product }) => {
  const imageUrl = product.image
    ? (product.image.startsWith('/') ? `${MEDIA_BASE}${product.image}` : product.image)
    : null;

  return (
    <Link href={`/shop/${product.product_id}`} className="group flex flex-col gap-4 w-full">
      {/* Image */}
      <div className="relative aspect-square rounded-3xl overflow-hidden bg-white border border-slate-100 group-hover:shadow-xl transition-all duration-500">
        {product.similarity_score && (
          <div className="absolute top-3 right-3 z-10 px-2 py-0.5 bg-indigo-600/90 backdrop-blur rounded-full text-[9px] font-black text-white uppercase tracking-widest">
            {Math.round(product.similarity_score * 100)}% match
          </div>
        )}
        {imageUrl ? (
          <img src={imageUrl} alt={product.product_name} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
        ) : (
          <div className="w-full h-full bg-linear-to-br from-slate-100 to-slate-200 flex items-center justify-center">
            <svg className="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
          </div>
        )}
      </div>

      {/* Info */}
      <div className="flex flex-col gap-1 px-1">
        <div className="flex justify-between items-start gap-2">
          <h3 className="text-sm font-extrabold uppercase tracking-tight text-blue-950 leading-tight truncate">
            {product.product_name}
          </h3>
          <div className="flex flex-col items-end whitespace-nowrap shrink-0">
            {product.discount_percentage > 0 ? (
              <>
                <span className="text-sm font-black text-slate-900">
                  ₹{Math.round(product.base_price * (1 - product.discount_percentage / 100)).toLocaleString('en-IN')}
                </span>
                <span className="text-[10px] font-bold text-slate-400 line-through">
                  ₹{Math.round(product.base_price).toLocaleString('en-IN')}
                </span>
              </>
            ) : (
              <span className="text-sm font-black text-slate-600">
                ₹{Math.round(product.base_price).toLocaleString('en-IN')}
              </span>
            )}
          </div>
        </div>

        <div className="flex items-center justify-between mt-1 pt-2 border-t border-slate-100">
          <span className={`text-[10px] font-bold uppercase tracking-widest ${product.available_quantity > 0 ? 'text-emerald-500' : 'text-red-400'}`}>
            {product.available_quantity > 0 ? `${product.available_quantity} left` : 'Out of stock'}
          </span>
          <span className="text-[9px] font-black text-slate-300 uppercase tracking-widest">
            {product.category}
          </span>
        </div>
      </div>
    </Link>
  );
};

// ── Main Page ──────────────────────────────────────────────────────────────
const ShopPage = () => {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [aiEnabled, setAiEnabled] = useState(false);

  // Normal mode state
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [page, setPage] = useState(1);

  // AI mode state
  const [aiResults, setAiResults] = useState([]);
  const [aiMessage, setAiMessage] = useState('');
  const [aiFilters, setAiFilters] = useState(null);
  const [isAiMode, setIsAiMode] = useState(false);

  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [error, setError] = useState(null);

  const debounceTimer = useRef(null);

  useEffect(() => {
    getCategories().then(setCategories).catch(() => setCategories([]));
  }, []);

  // ── Normal product fetch ─────────────────────────────────────────────────
  const fetchProducts = useCallback(async (isLoadMore = false) => {
    if (isLoadMore) setLoadingMore(true);
    else { setLoading(true); setPage(1); }
    setError(null);

    try {
      const params = { page: isLoadMore ? page + 1 : 1, page_size: 16 };
      if (selectedCategory !== 'all') params.category_id = selectedCategory;
      if (searchQuery.trim()) params.search = searchQuery.trim();

      const data = await getProducts(params);
      const newProducts = (data?.results ?? []).map(normalizeProduct);

      if (isLoadMore) {
        setProducts(prev => [...prev, ...newProducts]);
        setPage(prev => prev + 1);
      } else {
        setProducts(newProducts);
        setPage(1);
      }
      setTotalCount(data?.total ?? data?.count ?? 0);
    } catch (err) {
      setError(err.message || 'Failed to load products.');
      if (!isLoadMore) setProducts([]);
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  }, [selectedCategory, page, searchQuery]);

  // ── AI search fetch ──────────────────────────────────────────────────────
  const fetchAIResults = useCallback(async (query) => {
    if (!query.trim()) {
      setIsAiMode(false);
      setAiResults([]);
      setAiMessage('');
      setAiFilters(null);
      fetchProducts(false);
      return;
    }

    setLoading(true);
    setError(null);
    setIsAiMode(true);

    try {
      const data = await aiSearch(query, 16);
      setAiResults(data.results ?? []);
      setAiMessage(data.message ?? '');
      setAiFilters(data.filters_applied ?? null);
    } catch (err) {
      setError('AI search failed. Try again.');
      setAiResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // ── Handle AI toggle ─────────────────────────────────────────────────────
  const handleAiToggle = () => {
    const next = !aiEnabled;
    setAiEnabled(next);
    if (!next) {
      // Switching to simple mode — clear AI state
      setIsAiMode(false);
      setAiResults([]);
      setAiMessage('');
      setAiFilters(null);
      fetchProducts(false);
    } else if (searchQuery.trim()) {
      fetchAIResults(searchQuery);
    }
  };

  // ── Handle search input ──────────────────────────────────────────────────
  const handleSearchChange = (e) => {
    const val = e.target.value;
    setSearchQuery(val);

    clearTimeout(debounceTimer.current);
    debounceTimer.current = setTimeout(() => {
      if (aiEnabled) {
        fetchAIResults(val);
      } else {
        fetchProducts(false);
      }
    }, 350);
  };

  const handleSearchKeyDown = (e) => {
    if (e.key === 'Enter') {
      clearTimeout(debounceTimer.current);
      if (aiEnabled) fetchAIResults(searchQuery);
      else fetchProducts(false);
    }
  };

  // Initial load and category switch (only in normal mode)
  useEffect(() => {
    if (!aiEnabled) fetchProducts(false);
  }, [selectedCategory]);

  // When switching categories reset AI mode
  const handleCategoryChange = (catId) => {
    setSelectedCategory(catId);
    if (aiEnabled && !searchQuery.trim()) {
      setIsAiMode(false);
    }
  };

  const showingAI = aiEnabled && isAiMode;

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans text-slate-900 selection:bg-slate-900/30">
      <Navbar />

      <main className="grow w-full max-w-7xl mx-auto px-4 py-12 md:py-20">

        {/* ── Header ── */}
        <div className="flex flex-col items-center gap-6 mb-12 px-4">

          {/* Search Bar */}
          <div className="relative w-full max-w-xl">
            <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 pointer-events-none" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>

            <input
              type="text"
              placeholder={aiEnabled ? 'Try: "laptop under 2000" or "camera in stock"' : 'Search products...'}
              value={searchQuery}
              onChange={handleSearchChange}
              onKeyDown={handleSearchKeyDown}
              className="w-full pl-12 pr-27.5 py-3.5 rounded-full border border-slate-200 bg-white text-slate-900 focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-all shadow-sm text-sm"
            />

            {/* AI Toggle */}
            <button
              type="button"
              onClick={handleAiToggle}
              className={`absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-bold transition-all duration-300 ${
                aiEnabled
                  ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200'
                  : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
              }`}
            >
              <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17H3a2 2 0 01-2-2V5a2 2 0 012-2h14a2 2 0 012 2v10a2 2 0 01-2 2h-2" />
              </svg>
              AI
            </button>
          </div>

          {/* AI Response Banner */}
          {showingAI && aiMessage && (
            <div className="w-full max-w-xl">
              <div className="flex items-start gap-3 px-4 py-3 rounded-2xl bg-indigo-50 border border-indigo-100">
                <span className="text-indigo-500 mt-0.5 shrink-0">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                </span>
                <p className="text-sm font-medium text-indigo-800 leading-snug">{aiMessage}</p>
              </div>

              {/* Active Filter Tags */}
              {aiFilters && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {aiFilters.price_max && (
                    <FilterTag label="Max price" value={`₹${Math.round(aiFilters.price_max).toLocaleString('en-IN')}`} />
                  )}
                  {aiFilters.price_min && (
                    <FilterTag label="Min price" value={`₹${Math.round(aiFilters.price_min).toLocaleString('en-IN')}`} />
                  )}
                  {aiFilters.category && (
                    <FilterTag label="Category" value={aiFilters.category} />
                  )}
                  {aiFilters.in_stock && (
                    <FilterTag label="" value="In stock only" />
                  )}
                  {aiFilters.sort_by && aiFilters.sort_by !== 'relevance' && (
                    <FilterTag label="Sort" value={aiFilters.sort_by === 'price_asc' ? 'Lowest price' : 'Highest price'} />
                  )}
                </div>
              )}
            </div>
          )}

          {/* Category Filters (hidden in AI result mode) */}
          {!showingAI && (
            <div className="flex flex-wrap justify-center gap-3">
              <button
                onClick={() => handleCategoryChange('all')}
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
                  onClick={() => handleCategoryChange(cat.id)}
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
          )}

          {/* Count */}
          {!loading && !error && (
            <div className="text-xs font-medium text-slate-400 uppercase tracking-widest">
              {showingAI
                ? `${aiResults.length} AI result${aiResults.length !== 1 ? 's' : ''}`
                : `Showing ${products.length} of ${totalCount} Products`}
            </div>
          )}
        </div>

        {/* ── Error ── */}
        {error && (
          <div className="text-center py-12">
            <p className="text-red-500 font-medium mb-4">{error}</p>
            <button
              onClick={() => showingAI ? fetchAIResults(searchQuery) : fetchProducts(false)}
              className="px-6 py-2 bg-slate-900 text-white rounded-full text-xs font-bold uppercase tracking-wider hover:bg-slate-800 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* ── Product Grid ── */}
        {!error && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-8 gap-y-12">
            {loading
              ? Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)
              : showingAI
                ? aiResults.map((product) => (
                    <AIProductCard key={product.product_id} product={product} />
                  ))
                : products.map((product) => (
                    <div key={product.id} className="group flex flex-col gap-6 w-full">
                      <Link
                        href={`/shop/${product.id}`}
                        className="block aspect-square relative rounded-4xl overflow-hidden bg-white border border-slate-100 group-hover:shadow-xl transition-all duration-500"
                      >
                        {product.tag && (
                          <div className="absolute top-4 left-4 z-10 px-3 py-1 bg-white/90 backdrop-blur-md rounded-full text-[9px] font-black uppercase tracking-widest text-blue-950 shadow-sm border border-slate-100">
                            {product.tag}
                          </div>
                        )}
                        {product.image ? (
                          <img src={product.image} alt={product.name} className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                        ) : (
                          <div className="w-full h-full bg-linear-to-br from-slate-100 to-slate-200 flex items-center justify-center">
                            <svg className="w-12 h-12 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          </div>
                        )}
                      </Link>

                      <div className="flex flex-col gap-2 px-1">
                        <div className="flex justify-between items-center">
                          <h3 className="text-base font-extrabold tracking-tight uppercase text-blue-950 leading-tight group-hover:text-slate-900 transition-colors truncate pr-2">
                            <Link href={`/shop/${product.id}`}>{product.name}</Link>
                          </h3>
                          <div className="flex flex-col items-end whitespace-nowrap">
                            {product.hasDiscount ? (
                              <>
                                <span className="text-base font-black text-slate-900">{product.discountedPriceDisplay}</span>
                                <span className="text-[10px] font-bold text-slate-400 line-through">{product.priceDisplay}</span>
                              </>
                            ) : (
                              <span className="text-base font-black text-slate-600">{product.priceDisplay}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center justify-between mt-2 pt-3 border-t border-slate-100">
                          <span className="flex items-center gap-1.5 text-[10px] font-black uppercase tracking-widest text-slate-300">
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                            </svg>
                            {product.availableQuantity > 0 ? `${product.availableQuantity} left` : 'Out of stock'}
                          </span>
                          <span className="text-[9px] font-black text-slate-300 uppercase tracking-widest">
                            {categories.find((c) => c.id === product.category_id)?.name?.split(' ')[0] ?? ''}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
          </div>
        )}

        {/* ── Load More (normal mode only) ── */}
        {!showingAI && !loading && !error && products.length < totalCount && (
          <div className="mt-20 flex justify-center">
            <button
              onClick={() => fetchProducts(true)}
              disabled={loadingMore}
              className="px-12 py-4 bg-white border-2 border-slate-100 text-blue-950 rounded-full text-sm font-black uppercase tracking-widest hover:border-blue-200 transition-all duration-300 disabled:opacity-50 flex items-center gap-3 shadow-lg shadow-slate-100 group"
            >
              {loadingMore ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-slate-900" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Loading More...
                </>
              ) : (
                <>
                  Load More
                  <svg className="w-5 h-5 group-hover:translate-y-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M19 13l-7 7-7-7m14-8l-7 7-7-7" />
                  </svg>
                </>
              )}
            </button>
          </div>
        )}

        {/* ── Empty state ── */}
        {!loading && !error && (showingAI ? aiResults.length === 0 : products.length === 0) && (
          <div className="text-center py-20">
            <div className="w-20 h-20 bg-slate-50 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <h3 className="text-xl font-bold text-slate-800 mb-2">No products found</h3>
            <p className="text-slate-500 text-sm">
              {showingAI ? 'Try different keywords or turn off AI mode.' : "We couldn't find any products here."}
            </p>
          </div>
        )}

      </main>
      <Footer />
    </div>
  );
};

export default ShopPage;
