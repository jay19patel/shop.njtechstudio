import React from 'react';
import siteData from '../data/siteData.json';

const Footer = () => {
    const { brand } = siteData;

    return (
        <footer id="footer" className="w-full py-12 border-t border-slate-100 mt-auto bg-white font-sans">
            <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-12">
                {/* Brand Column */}
                <div className="flex flex-col gap-4 items-center md:items-start text-center md:text-left">
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center shrink-0 shadow-sm">
                            <span className="text-white font-bold text-lg leading-none">N</span>
                        </div>
                        <span className="font-bold uppercase text-lg text-slate-900 tracking-widest">
                            {brand.name}
                        </span>
                    </div>
                    <p className="text-slate-500 font-medium text-sm leading-relaxed max-w-xs">
                        {brand.tagline || 'Elevating your daily environment with curated, minimalist designs.'}
                    </p>
                </div>

                <div className="flex gap-8 text-xs font-bold uppercase tracking-wider text-slate-500">
                    <a href="/shop" className="hover:text-slate-900 transition-colors">Shop</a>
                    <a href="/contact" className="hover:text-slate-900 transition-colors">Contact</a>
                    <a href="/terms" className="hover:text-slate-900 transition-colors">Policies</a>
                </div>
            </div>

            {/* Bottom Section */}
            <div className="max-w-6xl mx-auto px-6 mt-12 pt-6 border-t border-slate-100 flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex flex-col gap-1 text-center md:text-left">
                    <p className="text-slate-400 font-semibold text-[10px] uppercase tracking-wider">
                        © {new Date().getFullYear()} {brand.name}. All rights reserved.
                    </p>
                    <p className="text-slate-400 font-medium text-[9px] uppercase tracking-widest">
                        Designed by <a href="https://njtechstudio.in" target="_blank" rel="noopener noreferrer" className="text-slate-600 hover:text-slate-900 transition-colors">njtechstudio</a>
                    </p>
                </div>
                
                <div className="flex gap-6 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    {brand.instagram && (
                        <a href={brand.instagram} target="_blank" rel="noopener noreferrer" className="hover:text-slate-900 transition-colors">Instagram</a>
                    )}
                </div>
            </div>
        </footer>
    );
};

export default Footer;
