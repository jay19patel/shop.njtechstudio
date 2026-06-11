import React from 'react';
import siteData from '../data/siteData.json';

const Footer = () => {
    const { brand } = siteData;

    return (
        <footer id="footer" className="w-full py-12 border-t border-slate-100 mt-auto bg-white font-sans">
            <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
                <div className="flex flex-col gap-1 text-center md:text-left">
                    <p className="text-slate-400 font-semibold text-[10px] uppercase tracking-wider">
                        © {new Date().getFullYear()} {brand.name}. All rights reserved.
                    </p>
                    <p className="text-slate-400 font-medium text-[9px] uppercase tracking-widest">
                        Designed by <a href="https://njtechstudio.in" target="_blank" rel="noopener noreferrer" className="text-slate-600 hover:text-slate-900 transition-colors">njtechstudio</a>
                    </p>
                </div>
                
                <div className="flex flex-wrap justify-center gap-6 text-[10px] font-bold uppercase tracking-wider text-slate-400">
                    <a href="/shop" className="hover:text-slate-900 transition-colors">Shop</a>
                    <a href="/contact" className="hover:text-slate-900 transition-colors">Contact</a>
                    <a href="/terms" className="hover:text-slate-900 transition-colors">Policies</a>
                    {brand.instagram && (
                        <a href={brand.instagram} target="_blank" rel="noopener noreferrer" className="hover:text-slate-900 transition-colors">Instagram</a>
                    )}
                </div>
            </div>
        </footer>
    );
};

export default Footer;
