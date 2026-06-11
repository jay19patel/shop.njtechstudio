'use client';
import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import siteData from '../data/siteData.json';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import CartSheet from './CartSheet';
import { ShoppingBag, User as UserIcon, LogOut, Package, ChevronDown, LayoutDashboard, Store, Phone } from 'lucide-react';

const Navbar = () => {
  const { brand } = siteData;
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);
  const { toggleCart, cartCount } = useCart();
  const { user, logout, isAuthenticated } = useAuth();
  const profileRef = useRef(null);

  // Close profile dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (profileRef.current && !profileRef.current.contains(e.target)) {
        setIsProfileOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <>
      <header className="w-full px-6 py-4 flex items-center justify-between border-b border-slate-100 bg-white/80 backdrop-blur-md sticky top-0 z-50">

        {/* ── Logo (Left) ── */}
        <Link href="/" className="flex items-center gap-2.5 shrink-0">
          <div className="w-8 h-8 rounded-lg bg-slate-900 flex items-center justify-center shrink-0 shadow-sm">
            <span className="text-white font-bold text-lg leading-none">N</span>
          </div>
          <span className="font-bold uppercase text-lg text-slate-900 tracking-widest">
            {brand.name}
          </span>
        </Link>

        {/* ── Right Side: Nav + Cart + Profile (Desktop) ── */}
        <div className="hidden md:flex items-center gap-2">

          {/* Nav Links */}
          <nav className="flex items-center gap-1 text-sm font-semibold text-slate-600 mr-2">
            <Link href="/shop" className="flex items-center gap-1.5 px-4 py-2 rounded-xl hover:bg-slate-50 hover:text-slate-900 transition-all">
              <Store className="w-3.5 h-3.5" />
              Shop
            </Link>
            <Link href="/contact" className="flex items-center gap-1.5 px-4 py-2 rounded-xl hover:bg-slate-50 hover:text-slate-900 transition-all">
              <Phone className="w-3.5 h-3.5" />
              Contact
            </Link>
            {/* Admin Dashboard — only for superusers */}
            {isAuthenticated && user?.is_superuser && (
              <Link
                href="/admin/dashboard"
                className="flex items-center gap-1.5 px-4 py-2 rounded-xl hover:bg-indigo-50 hover:text-indigo-700 text-slate-600 transition-all"
              >
                <LayoutDashboard className="w-3.5 h-3.5" />
                Admin
              </Link>
            )}
          </nav>

          {/* Cart Icon */}
          <button
            onClick={toggleCart}
            className="relative p-2.5 text-slate-600 hover:text-slate-900 transition-all hover:bg-slate-50 rounded-xl"
          >
            <ShoppingBag className="w-5 h-5" />
            {cartCount > 0 && (
              <span className="absolute top-1 right-1 w-5 h-5 bg-slate-900 text-white text-[10px] font-bold flex items-center justify-center rounded-lg shadow-sm">
                {cartCount}
              </span>
            )}
          </button>

          {/* Profile Dropdown (last) */}
          {isAuthenticated ? (
            <div className="relative" ref={profileRef}>
              <button
                onClick={() => setIsProfileOpen(!isProfileOpen)}
                className="flex items-center gap-2 py-2 px-3 rounded-xl bg-slate-50 hover:bg-slate-100 text-slate-900 transition-all border border-slate-100"
              >
                <div className="w-6 h-6 rounded-lg bg-slate-200 flex items-center justify-center overflow-hidden shrink-0 border border-slate-200">
                  {user?.profile_image ? (
                    <img
                      src={user.profile_image}
                      alt=""
                      className="w-full h-full object-cover"
                      referrerPolicy="no-referrer"
                    />
                  ) : (
                    <UserIcon className="w-3.5 h-3.5 text-slate-600" />
                  )}
                </div>
                <span className="max-w-[80px] truncate text-xs font-semibold">
                  {user?.full_name?.split(' ')[0] || 'Profile'}
                </span>
                <ChevronDown className={`w-3.5 h-3.5 text-slate-400 transition-transform ${isProfileOpen ? 'rotate-180' : ''}`} />
              </button>

              {isProfileOpen && (
                <div className="absolute top-full right-0 mt-3 w-52 bg-white rounded-xl shadow-xl shadow-slate-200/50 border border-slate-100 p-1.5 flex flex-col gap-0.5 animate-in zoom-in-95 fade-in duration-200">
                  <Link
                    href="/profile"
                    onClick={() => setIsProfileOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg hover:bg-slate-50 text-slate-600 hover:text-slate-900 transition-colors"
                  >
                    <UserIcon className="w-4 h-4" />
                    <span className="text-sm font-medium">Profile Settings</span>
                  </Link>
                  <Link
                    href="/orders"
                    onClick={() => setIsProfileOpen(false)}
                    className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg hover:bg-slate-50 text-slate-600 hover:text-slate-900 transition-colors"
                  >
                    <Package className="w-4 h-4" />
                    <span className="text-sm font-medium">My Orders</span>
                  </Link>

                  <div className="h-px bg-slate-100 my-1" />
                  <button
                    onClick={() => { logout(); setIsProfileOpen(false); }}
                    className="flex items-center gap-2.5 px-3 py-2.5 rounded-lg hover:bg-red-50 text-red-600 hover:text-red-700 transition-colors w-full text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    <span className="text-sm font-medium">Logout</span>
                  </button>
                </div>
              )}
            </div>
          ) : (
            <Link
              href="/login"
              className="px-5 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-bold uppercase tracking-widest hover:bg-slate-800 transition-all shadow-md"
            >
              Login
            </Link>
          )}
        </div>

        {/* ── Mobile: Cart + Hamburger ── */}
        <div className="flex md:hidden items-center gap-3">
          <button
            onClick={toggleCart}
            className="relative p-2.5 text-slate-600 hover:text-slate-900 transition-all hover:bg-slate-50 rounded-xl"
          >
            <ShoppingBag className="w-5 h-5" />
            {cartCount > 0 && (
              <span className="absolute top-1 right-1 w-5 h-5 bg-slate-900 text-white text-[10px] font-bold flex items-center justify-center rounded-lg shadow-sm">
                {cartCount}
              </span>
            )}
          </button>
          <button
            className="p-2 text-slate-600 hover:text-slate-900 transition-colors"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            aria-label="Toggle mobile menu"
          >
            {isMenuOpen ? (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            )}
          </button>
        </div>

        {/* ── Mobile Dropdown ── */}
        {isMenuOpen && (
          <div className="absolute top-full left-0 w-full bg-white border-b border-slate-100 shadow-xl py-6 px-6 flex flex-col gap-4 md:hidden animate-in slide-in-from-top-4 duration-300">
            <nav className="flex flex-col gap-1 text-base font-medium text-slate-600">
              <Link href="/shop" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-2.5 px-4 py-3 hover:bg-slate-50 rounded-xl transition-all"><Store className="w-4 h-4" />Shop</Link>
              <Link href="/orders" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-2.5 px-4 py-3 hover:bg-slate-50 rounded-xl transition-all"><Package className="w-4 h-4" />My Orders</Link>
              <Link href="/contact" onClick={() => setIsMenuOpen(false)} className="flex items-center gap-2.5 px-4 py-3 hover:bg-slate-50 rounded-xl transition-all"><Phone className="w-4 h-4" />Contact</Link>
              {isAuthenticated && user?.is_superuser && (
                <Link href="/admin/dashboard" onClick={() => setIsMenuOpen(false)} className="px-4 py-3 hover:bg-indigo-50 text-indigo-600 rounded-xl transition-all flex items-center gap-2">
                  <LayoutDashboard className="w-4 h-4" /> Admin Dashboard
                </Link>
              )}
              {isAuthenticated && (
                <Link href="/profile" onClick={() => setIsMenuOpen(false)} className="px-4 py-3 hover:bg-slate-50 rounded-xl transition-all">Profile</Link>
              )}
            </nav>
            {!isAuthenticated ? (
              <Link
                href="/login"
                onClick={() => setIsMenuOpen(false)}
                className="py-3.5 bg-slate-900 text-white rounded-xl text-center font-bold uppercase tracking-widest text-sm shadow-md"
              >
                Login
              </Link>
            ) : (
              <button
                onClick={() => { logout(); setIsMenuOpen(false); }}
                className="py-3.5 bg-red-50 text-red-600 border border-red-100 rounded-xl text-center font-bold uppercase tracking-widest text-sm"
              >
                Logout
              </button>
            )}
          </div>
        )}
      </header>

      <CartSheet />
    </>
  );
};

export default Navbar;
