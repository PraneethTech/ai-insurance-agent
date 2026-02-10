'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/hooks/useAuth';
import { useToast } from '@/context/ToastContext';

export default function LoginPage() {
    const router = useRouter();
    const searchParams = useSearchParams();
    const { login, loading, error, isAuthenticated } = useAuth();
    const { showToast } = useToast();
    const [formData, setFormData] = useState({
        username: '',
        password: '',
    });

    // Check if user just registered
    const justRegistered = searchParams.get('registered') === 'true';

    // Redirect if already authenticated
    useEffect(() => {
        if (isAuthenticated()) {
            router.push('/dashboard/files');
        }
    }, [isAuthenticated, router]);

    // Show welcome toast for new registrations
    useEffect(() => {
        if (justRegistered) {
            showToast('Account created successfully! Please login.', 'success');
        }
    }, [justRegistered, showToast]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await login(formData);
            showToast('Login successful!', 'success');
            router.push('/dashboard/files');
        } catch (err: any) {
            showToast(err.message || 'Login failed', 'error');
        }
    };

    return (
        <div className="h-screen flex bg-white font-sans text-slate-800 overflow-hidden">
            {/* Left Side - Illustration */}
            <div className="hidden lg:flex lg:w-1/2 items-center justify-center p-12 bg-slate-50 relative overflow-hidden h-full">
                {/* Abstract Background Decoration */}
                <div className="absolute top-0 left-0 w-full h-full">
                    <div className="absolute top-10 left-10 w-32 h-32 bg-blue-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
                    <div className="absolute top-10 right-10 w-32 h-32 bg-teal-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-700"></div>
                    <div className="absolute -bottom-8 left-20 w-32 h-32 bg-pink-200 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse delay-1000"></div>
                </div>

                <div className="relative z-10 max-w-lg text-center">
                    {/* Medical/Security Illustration */}
                    <div className="mb-8 mx-auto w-64 h-64 relative drop-shadow-2xl">
                        <svg viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full h-full">
                            <circle cx="100" cy="100" r="90" fill="white" />
                            {/* Shield */}
                            <path d="M100 40C100 40 140 50 140 90C140 130 100 160 100 160C100 160 60 130 60 90C60 50 100 40 100 40Z" fill="#4F86ED" fillOpacity="0.1" stroke="#4F86ED" strokeWidth="4" />
                            {/* User Icon */}
                            <circle cx="100" cy="85" r="20" fill="#4F86ED" />
                            <path d="M60 135C60 112.909 77.9086 95 100 95C122.091 95 140 112.909 140 135" stroke="#4F86ED" strokeWidth="4" strokeLinecap="round" />
                            {/* Checkmark */}
                            <circle cx="140" cy="140" r="15" fill="#10B981" />
                            <path d="M135 140L138 143L145 136" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                    </div>
                    <h2 className="text-3xl font-bold text-slate-900 mb-4 tracking-tight">Intelligent Discharge Analysis</h2>
                    <p className="text-slate-500 text-lg">
                        Multi-Agent System for Bill Validation, Price Comparison, Nutrition Planning, and RAG-based Analysis.
                    </p>
                </div>
            </div>

            {/* Right Side - Login Form */}
            <div className="w-full lg:w-1/2 h-full overflow-y-auto flex items-center justify-center p-8 lg:p-24 relative bg-white">
                <div className="w-full max-w-md space-y-8">
                    {/* Logo/Brand (Mobile only) */}
                    <div className="lg:hidden text-center">
                        <span className="text-2xl font-bold text-[#4F86ED]">Dischargo</span>
                    </div>

                    <div className="space-y-2">
                        <h1 className="text-3xl font-bold text-slate-900">
                            {justRegistered ? 'Account Created!' : 'Welcome back'}
                        </h1>
                        <p className="text-slate-500">
                            {justRegistered
                                ? 'Your account is ready. Please sign in to continue.'
                                : 'Please sign in to your account'}
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="mt-8 space-y-6">
                        {error && (
                            <div className="p-4 bg-red-50 text-red-600 text-sm rounded-xl flex items-center gap-3 border border-red-100 animate-fade-in-down">
                                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 flex-shrink-0" viewBox="0 0 20 20" fill="currentColor">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                {error}
                            </div>
                        )}

                        <div className="space-y-5">
                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Username</label>
                                <input
                                    type="text"
                                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#4F86ED]/20 focus:border-[#4F86ED] transition-all shadow-sm"
                                    placeholder="Enter your username"
                                    value={formData.username}
                                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                                    required
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-semibold text-slate-700 mb-2">Password</label>
                                <input
                                    type="password"
                                    className="w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-[#4F86ED]/20 focus:border-[#4F86ED] transition-all shadow-sm"
                                    placeholder="••••••••"
                                    value={formData.password}
                                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="flex items-center justify-between text-sm">
                            <label className="flex items-center text-slate-600 cursor-pointer hover:text-slate-800 transition-colors">
                                <input
                                    type="checkbox"
                                    className="w-4 h-4 mr-2 rounded border-gray-300 text-[#4F86ED] focus:ring-[#4F86ED] transition-colors"
                                />
                                Remember me
                            </label>
                            <a href="#" className="text-[#4F86ED] hover:text-[#3A6BC7] font-semibold transition-colors">Forgot Password?</a>
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-[#4F86ED] hover:bg-[#3A6BC7] text-white font-bold py-3.5 px-4 rounded-xl transition-all duration-200 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/40 hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            disabled={loading}
                        >
                            {loading ? (
                                <>
                                    <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    Signing in...
                                </>
                            ) : (
                                'Sign In'
                            )}
                        </button>
                    </form>

                    <div className="mt-8 text-center text-sm text-slate-500">
                        Don't have an account?{' '}
                        <Link href="/register" className="text-[#4F86ED] hover:text-[#3A6BC7] font-bold transition-colors">
                            Create Account
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
