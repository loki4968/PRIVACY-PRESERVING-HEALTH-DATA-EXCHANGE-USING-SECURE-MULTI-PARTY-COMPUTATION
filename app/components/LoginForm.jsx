'use client';

import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';
import Link from 'next/link';
import { Mail, Lock } from 'lucide-react';
import OTPVerification from './OTPVerification';
import PasswordInput from './PasswordInput';

export default function LoginForm() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [showOtpInput, setShowOtpInput] = useState(false);
    const { login } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            await login(email, password);
            // Login success is handled by AuthContext (redirects to dashboard)
        } catch (error) {
            // If the error indicates email verification needed
            if (error.message?.toLowerCase().includes('verify')) {
                setShowOtpInput(true);
                toast.info('Please verify your email with OTP.');
            } else {
                toast.error(error.message || 'Failed to login');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleOtpSubmit = async (otp) => {
        setLoading(true);

        try {
            const res = await fetch('http://localhost:8000/verify-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, otp }),
            });

            if (res.ok) {
                toast.success('OTP verified successfully!');
                setShowOtpInput(false);
            } else {
                const errorData = await res.json();
                toast.error(errorData.detail || 'Invalid OTP');
            }
        } catch (error) {
            toast.error('Failed to verify OTP');
        } finally {
            setLoading(false);
        }
    };

    const handleResendOtp = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/send-otp', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email }),
            });

            if (res.ok) {
                toast.success('OTP resent successfully!');
            } else {
                const errorData = await res.json();
                toast.error(errorData.detail || 'Failed to resend OTP');
            }
        } catch (error) {
            toast.error('Failed to resend OTP');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-gray-100 transform transition-all duration-300 hover:shadow-2xl">
                <div className="text-center">
                    <div className="mx-auto h-12 w-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4">
                        <Lock className="h-6 w-6 text-white" />
                    </div>
                    <h2 className="mt-2 text-center text-3xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Welcome Back
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Sign in to your account to continue
                    </p>
                </div>

                {showOtpInput ? (
                    <OTPVerification
                        email={email}
                        onVerify={handleOtpSubmit}
                        resendOTP={handleResendOtp}
                        loading={loading}
                    />
                ) : (
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-4">
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                                    Email address
                                </label>
                                <div className="relative mt-1 group">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <Mail className="h-5 w-5 text-gray-400 group-hover:text-gray-500 transition-colors duration-200" />
                                    </div>
                                    <input
                                        id="email"
                                        name="email"
                                        type="email"
                                        required
                                        className="block w-full pl-10 px-4 py-3 border border-gray-200 rounded-lg shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ease-in-out group-hover:border-gray-300"
                                        placeholder="Enter your email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                    />
                                </div>
                            </div>
                            <PasswordInput
                                id="password"
                                name="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                                required
                                label="Password"
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <div className="text-sm">
                                <Link 
                                    href="/forgot-password" 
                                    className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200 hover:underline"
                                >
                                    Forgot your password?
                                </Link>
                            </div>
                        </div>

                        <div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 ease-in-out transform hover:scale-[1.02] hover:shadow-lg"
                            >
                                {loading ? (
                                    <span className="flex items-center">
                                        <svg
                                            className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                                            xmlns="http://www.w3.org/2000/svg"
                                            fill="none"
                                            viewBox="0 0 24 24"
                                        >
                                            <circle
                                                className="opacity-25"
                                                cx="12"
                                                cy="12"
                                                r="10"
                                                stroke="currentColor"
                                                strokeWidth="4"
                                            ></circle>
                                            <path
                                                className="opacity-75"
                                                fill="currentColor"
                                                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                                            ></path>
                                        </svg>
                                        Signing in...
                                    </span>
                                ) : (
                                    'Sign in'
                                )}
                            </button>
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-gray-600">
                                Don't have an account?{' '}
                                <Link 
                                    href="/register" 
                                    className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200 hover:underline"
                                >
                                    Register your organization
                                </Link>
                            </p>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
} 