'use client';
import React, { useState, useEffect } from 'react';
import { Star } from 'lucide-react';
import { getTestimonials } from '../lib/api';

const Testimonials = () => {
  const [testimonials, setTestimonials] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getTestimonials()
      .then(setTestimonials)
      .catch(() => setTestimonials([]))
      .finally(() => setLoading(false));
  }, []);

  // Show up to 3 testimonials
  const displayList = testimonials.slice(0, 3);

  return (
    <section id="testimonials" className="w-full py-16 bg-white border-t border-slate-100">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex flex-col gap-2 mb-10 text-center md:text-left">
          <span className="text-slate-500 font-semibold text-xs uppercase tracking-wider">Reviews</span>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight text-slate-900">
            Customer Feedback
          </h2>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="rounded-2xl p-6 bg-slate-50 animate-pulse flex flex-col gap-3 border border-slate-100">
                <div className="h-4 bg-slate-200 rounded w-1/4" />
                <div className="h-3 bg-slate-200 rounded w-full" />
                <div className="h-3 bg-slate-200 rounded w-5/6" />
                <div className="h-3 bg-slate-200 rounded w-2/3" />
              </div>
            ))}
          </div>
        ) : displayList.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {displayList.map((item, idx) => (
              <div
                key={idx}
                className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm flex flex-col justify-between hover:border-slate-200 transition-colors duration-300"
              >
                <div className="flex flex-col gap-4">
                  <div className="flex gap-0.5">
                    {Array.from({ length: item.rating ?? 5 }).map((_, s) => (
                      <Star key={s} className="w-4 h-4 fill-amber-400 text-amber-400" />
                    ))}
                  </div>
                  <p className="text-slate-600 text-sm leading-relaxed font-medium">
                    &ldquo;{item.content}&rdquo;
                  </p>
                </div>
                
                <div className="flex flex-col mt-6 pt-4 border-t border-slate-50">
                  <span className="font-semibold text-slate-900 text-xs uppercase tracking-wider">
                    {item.name || item.author_name || 'Customer'}
                  </span>
                  <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mt-0.5">
                    {item.role || 'Verified Customer'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        ) : null}
      </div>
    </section>
  );
};

export default Testimonials;
