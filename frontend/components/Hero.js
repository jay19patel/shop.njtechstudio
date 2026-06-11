import React from 'react';
import Link from 'next/link';

const Hero = () => {
  return (
    <section className="w-full max-w-5xl mx-auto px-4 py-16 md:py-24 flex flex-col items-center text-center gap-6">
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-50 border border-slate-200 text-xs font-semibold text-slate-600 mb-2">
        <span className="w-2 h-2 rounded-full bg-slate-900 animate-pulse"></span>
        Handcrafted with Love
      </div>
      <h1 className="text-4xl md:text-6xl font-bold tracking-tight text-slate-900 max-w-3xl leading-tight">
        Elevate Your Space with Bespoke Wool Art
      </h1>
      <p className="text-base md:text-lg text-slate-500 max-w-xl">
        Discover our exclusive collection of handcrafted decorations and apparel designed to bring warmth and elegance to your home.
      </p>
      <div className="flex flex-col sm:flex-row gap-4 mt-6 w-full sm:w-auto">
        <Link href="/shop" className="bg-slate-900 text-white px-8 py-3.5 rounded-xl font-semibold text-sm hover:bg-slate-800 transition-all shadow-sm flex-1 sm:flex-none">
          Shop Collection
        </Link>
        <Link href="/contact" className="bg-white text-slate-900 px-8 py-3.5 rounded-xl font-semibold text-sm border border-slate-200 hover:bg-slate-50 transition-all shadow-sm flex-1 sm:flex-none">
          Custom Orders
        </Link>
      </div>
    </section>
  );
};

export default Hero;
