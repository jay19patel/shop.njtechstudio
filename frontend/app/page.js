import React from 'react';
import Navbar from '../components/Navbar';
import Categories from '../components/Categories';
import Testimonials from '../components/Testimonials';
import FAQ from '../components/FAQ';
import Footer from '../components/Footer';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col font-sans text-slate-900 selection:bg-slate-900/30">
      <Navbar />

      <main className="flex-grow w-full mx-auto px-4 py-16 flex flex-col items-center">
        <Categories />
      </main>

      <Testimonials />
      <FAQ />

      <Footer />
    </div>
  );
}
