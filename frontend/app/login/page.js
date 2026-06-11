"use client";

import React, { Suspense, useState } from 'react';
import Navbar from '../../components/Navbar';
import Footer from '../../components/Footer';
import Link from 'next/link';
import { useAuth } from '../../context/AuthContext';
import { useRouter, useSearchParams } from 'next/navigation';
import { LogIn, Mail, Lock, AlertCircle } from 'lucide-react';
import { useGoogleLogin } from '@react-oauth/google';

function LoginPageContent() {
  const { login, loginWithGoogle } = useAuth();
  const router = useRouter();

  const searchParams = useSearchParams();
  const redirectPath = searchParams.get('redirect') || '/';

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const result = await login(email, password);
      if (result.success) {
        router.push(redirectPath);
      } else {
        setError(result.error || 'Invalid email or password');
      }
    } catch (err) {
      setError(err.message || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      setLoading(true);
      setError('');
      try {
        console.log('Google login token received');
        // allauth google endpoint usually takes access_token directly
        const result = await loginWithGoogle(tokenResponse.access_token);
        if (result.success) {
          router.push(redirectPath);
        } else {
          setError(result.error || 'Google login failed');
        }
      } catch (err) {
        setError(err.message || 'Google login failed');
      } finally {
        setLoading(false);
      }
    },
    onError: (error) => {
      console.error('Google Login Failed:', error);
      setError('Google Login Failed');
    },
    // We request the access_token implicitly for REST API auth (implicit flow instead of auth-code)
  });

  return (
    <div className="min-h-screen bg-white flex flex-col font-sans text-slate-900 selection:bg-slate-900/30">
      <Navbar />

      <main className="flex-grow flex items-center justify-center px-4 py-20">
        <div className="w-full max-w-md">
          {/* Card */}
          <div className="bg-white rounded-2xl border border-slate-100 p-8 md:p-10 flex flex-col gap-8 shadow-sm">
            <div className="text-center flex flex-col gap-2">
              <h1 className="text-2xl font-bold tracking-tight text-slate-900">
                Welcome Back
              </h1>
              <p className="text-slate-500 text-sm font-medium">
                Login to your account to manage your orders.
              </p>
            </div>

            {error && (
              <div className="bg-red-50 border border-red-100 text-red-600 px-4 py-3 rounded-xl flex items-center gap-3 text-sm">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex flex-col gap-5">
              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-600 ml-1">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="hello@example.com"
                    className="w-full bg-white border border-slate-200 rounded-xl py-3 pl-12 pr-4 text-sm focus:ring-2 focus:ring-slate-900 transition-all outline-none"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-2">
                <label className="text-xs font-semibold text-slate-600 ml-1">Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" />
                  <input
                    type="password"
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-white border border-slate-200 rounded-xl py-3 pl-12 pr-4 text-sm focus:ring-2 focus:ring-slate-900 transition-all outline-none"
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-slate-900 text-white rounded-xl py-3 font-semibold text-sm hover:bg-slate-800 transition-all disabled:opacity-50 flex items-center justify-center gap-2 mt-2"
              >
                {loading ? 'Logging in...' : (
                  <>
                    <span>Sign In</span>
                    <LogIn className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

              <div className="flex flex-col gap-5 items-center mt-4">
                <div className="w-full flex items-center gap-4">
                  <div className="h-px bg-slate-100 flex-grow" />
                  <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">or</span>
                  <div className="h-px bg-slate-100 flex-grow" />
                </div>

                <button
                  type="button"
                  onClick={() => handleGoogleLogin()}
                  disabled={loading}
                  className="w-full bg-white border border-slate-200 text-slate-700 rounded-xl py-3 font-semibold text-sm hover:bg-slate-50 transition-all flex items-center justify-center gap-3 disabled:opacity-50"
                >
                  <img src="https://www.google.com/favicon.ico" className="w-4 h-4" alt="Google" />
                  <span>{loading ? 'Processing...' : 'Continue with Google'}</span>
                </button>

                <p className="text-sm text-slate-500 mt-2">
                  Don&apos;t have an account?{' '}
                  <Link href="/register" className="text-slate-900 font-semibold hover:underline">Register here</Link>
                </p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}

function LoginPageLoadingFallback() {
  return (
    <div className="min-h-screen bg-white flex flex-col font-sans text-slate-900">
      <Navbar />
      <main className="flex-grow flex items-center justify-center px-4 py-20">
        <div className="w-full max-w-md h-[480px] rounded-[40px] bg-white border border-slate-100 shadow-xl animate-pulse" />
      </main>
      <Footer />
    </div>
  );
}

export default function LoginPage() {
  return (
    <Suspense fallback={<LoginPageLoadingFallback />}>
      <LoginPageContent />
    </Suspense>
  );
}
