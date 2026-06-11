'use client';
import React from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Sparkles, Star, ShoppingBag, ArrowRight } from 'lucide-react';
import siteData from '../data/siteData.json';

const Hero = () => {
    const { brand } = siteData;

    return (
        <section className="relative w-full min-h-[75vh] flex items-center justify-center overflow-hidden bg-background font-sans border-b border-white/5 pt-20 pb-16">
            {/* Minimal Background Gradients */}
            <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
                <div className="absolute top-[-15%] left-[20%] w-[60vw] h-[60vw] bg-primary/20 rounded-full blur-[100px] opacity-70"></div>
                <div className="absolute bottom-[-10%] right-[10%] w-[50vw] h-[50vw] bg-secondary/20 rounded-full blur-[120px] opacity-50"></div>
                <div className="absolute top-[20%] left-[-10%] w-[40vw] h-[40vw] bg-primary/10 rounded-full blur-[100px] opacity-40"></div>
            </div>

            <motion.div 
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.8 }}
                className="relative z-10 w-full max-w-4xl mx-auto px-6 sm:px-8 flex flex-col items-center text-center py-8"
            >
                <div className="w-full flex flex-col items-center">
                    {/* Sellio Style Small Pill Badge */}
                    <motion.div
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.5 }}
                        className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 mb-8 backdrop-blur-sm"
                    >
                        <Sparkles className="w-3.5 h-3.5 text-primary" />
                        <span className="text-gray-300 text-xs font-semibold tracking-wide">NJShop Premium Store</span>
                    </motion.div>

                    {/* Sellio-inspired Split Header */}
                    <motion.h1
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, delay: 0.15 }}
                        className="text-5xl sm:text-6xl md:text-7xl font-bold leading-[1.15] tracking-tight mb-8 max-w-3xl"
                    >
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-gray-300">Modern Aesthetics.</span>
                        <span className="block text-primary mt-2 font-normal drop-shadow-lg shadow-primary">Elevated Experience.</span>
                    </motion.h1>

                    <motion.p
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, delay: 0.3 }}
                        className="text-base sm:text-lg md:text-xl text-gray-400 max-w-2xl font-normal leading-relaxed mb-10"
                    >
                        Discover our premium collection of accessories, home decor, and handcrafted pieces designed to elevate your daily environment.
                    </motion.p>

                    {/* Sellio Style Action Buttons */}
                    <motion.div
                        initial={{ opacity: 0, y: 15 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.7, delay: 0.45 }}
                        className="flex flex-col sm:flex-row items-center justify-center gap-4 w-full sm:w-auto px-4 sm:px-0"
                    >
                        <Link href="/shop" className="group w-full sm:w-auto flex items-center justify-center gap-2 bg-gradient-to-r from-primary to-secondary text-white hover:opacity-90 px-8 py-3.5 rounded-xl font-bold text-sm transition-all duration-300 shadow-lg shadow-primary/30 hover:shadow-primary/50">
                            <ShoppingBag className="w-4 h-4" />
                            <span className="tracking-wide">Shop Collection</span>
                        </Link>
                        <button 
                            onClick={() => document.getElementById('products')?.scrollIntoView({ behavior: 'smooth' })}
                            className="group w-full sm:w-auto flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 text-white border border-white/10 px-8 py-3.5 rounded-xl font-semibold text-sm transition-all duration-300 backdrop-blur-sm"
                        >
                            <span className="tracking-wide">Browse Catalog</span>
                            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
                        </button>
                    </motion.div>

                    {/* Trust Rating */}
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ duration: 0.8, delay: 0.6 }}
                        className="mt-16 flex flex-col items-center gap-3 pt-8 border-t border-white/10 w-full max-w-sm"
                    >
                        <div className="flex items-center gap-1.5">
                            {[1, 2, 3, 4, 5].map((star) => (
                                <Star key={star} className="w-4 h-4 text-primary fill-primary drop-shadow-[0_0_5px_rgba(168,85,247,0.5)]" />
                            ))}
                        </div>
                        <span className="text-xs font-medium text-gray-400 tracking-wider uppercase">Trusted by design enthusiasts globally</span>
                    </motion.div>
                </div>
            </motion.div>
        </section>
    );
};

export default Hero;
