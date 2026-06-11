"use client";

import React, { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { getActiveCoupon } from '../lib/api';

export default function MarqueeBanner() {
  const [mounted, setMounted] = useState(false);
  const [coupon, setCoupon] = useState(null);
  const pathname = usePathname();

  useEffect(() => {
    setMounted(true);
    // Only fetch if we are on the homepage, or always fetch, but wait, if it's layout we shouldn't fetch
    // if not on homepage. But fetching once is harmless.
    getActiveCoupon()
      .then(data => {
        if (data && data.code) {
          setCoupon(data);
        }
      })
      .catch(err => {
        // No active coupon, ignore
      });
  }, []);

  // Do not render if not mounted, not on homepage, or no coupon available
  if (!mounted || pathname !== '/' || !coupon) return null;

  return (
    <div className="w-full bg-slate-900 text-white overflow-hidden py-2 relative flex items-center">
      <div 
        className="flex whitespace-nowrap"
        style={{
          animation: 'marquee 25s linear infinite'
        }}
      >
        {/* Duplicate the content a few times so it loops seamlessly */}
        {[...Array(4)].map((_, i) => (
          <div key={i} className="flex items-center gap-8 px-4 text-[10px] md:text-xs font-black uppercase tracking-[0.2em]">
            <span>✨ USE CODE <span className="text-yellow-300">{coupon.code}</span> FOR {coupon.discount_percentage}% OFF YOUR ORDER!</span>
            <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
            <span>🎉 FREE SHIPPING ON ALL ORDERS ABOVE ₹5000</span>
            <span className="w-1.5 h-1.5 rounded-full bg-slate-700" />
          </div>
        ))}
      </div>
      
      <style jsx>{`
        @keyframes marquee {
          0% { transform: translateX(0%); }
          100% { transform: translateX(-50%); }
        }
      `}</style>
    </div>
  );
}
