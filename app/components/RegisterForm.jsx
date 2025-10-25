'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';
import Link from 'next/link';
import { Mail, Building2, Phone, MapPin, User, Shield } from 'lucide-react';
import OTPVerification from './OTPVerification';
import PasswordInput from './PasswordInput';
import { API_ENDPOINTS } from '../config/api';

export default function RegisterForm() {
    const router = useRouter();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        organizationName: '',
        organizationType: '',
        contact: '',
        location: '',
    });
    const [loading, setLoading] = useState(false);
    const [showOtpInput, setShowOtpInput] = useState(false);
    const [currentStep, setCurrentStep] = useState(1);
    const totalSteps = 2;

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        if (formData.password !== formData.confirmPassword) {
            toast.error('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            const payload = new FormData();
            payload.append('name', formData.organizationName);
            payload.append('email', formData.email);
            payload.append('password', formData.password);
            payload.append('type', formData.organizationType.toUpperCase());
            payload.append('contact', formData.contact);
            payload.append('location', formData.location);
            payload.append('privacy_accepted', true);

            const response = await fetch(API_ENDPOINTS.register, {
                method: 'POST',
                body: payload,
            });

            const data = await response.json();

            if (response.ok) {
                toast.success('Registration successful! Please verify your email with OTP.');
                
                // Send OTP after successful registration
                const otpResponse = await fetch(API_ENDPOINTS.sendOtp, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email: formData.email }),
                });

                if (otpResponse.ok) {
                    // Show OTP verification section
                    setShowOtpInput(true);
                    setCurrentStep(2);
                    toast.success('OTP sent to your email! Please check your inbox.');
                } else {
                    const otpError = await otpResponse.json();
                    toast.error(otpError.detail || 'Failed to send OTP');
                }
            } else {
                // Display specific error message for email already registered
                if (data.detail === "Email already registered") {
                    toast.error('Email already registered. Please use a different email address.');
                } else {
                    const error = data.detail || 'Registration failed';
                    toast.error(error);
                }
            }
        } catch (error) {
            console.error('Registration error:', error);
            toast.error(error.message || 'Failed to register');
        } finally {
            setLoading(false);
        }
    };

    const handleOtpSubmit = async (otp) => {
        setLoading(true);
        try {
            const res = await fetch(API_ENDPOINTS.verifyOtp, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: formData.email, otp }),
            });

            if (res.ok) {
                toast.success('Email verified successfully! You can now login.');
                // Redirect to login page after successful verification
                router.push('/login');
            } else {
                const errorData = await res.json();
                toast.error(errorData.detail || 'Invalid OTP');
            }
        } catch (error) {
            console.error('OTP verification error:', error);
            toast.error('Failed to verify OTP');
        } finally {
            setLoading(false);
        }
    };

    const handleResendOtp = async () => {
        setLoading(true);
        try {
            const res = await fetch(API_ENDPOINTS.sendOtp, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: formData.email }),
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

    const organizationTypes = [
        { value: 'HOSPITAL', label: 'Hospital' },
        { value: 'CLINIC', label: 'Clinic' },
        { value: 'LABORATORY', label: 'Laboratory' },
        { value: 'PHARMACY', label: 'Pharmacy' },
        { value: 'RESEARCH', label: 'Research' },
        { value: 'PATIENT', label: 'Patient' },
        { value: 'OTHER', label: 'Other' },
    ];

    const nextStep = () => {
        if (currentStep < totalSteps) {
            setCurrentStep(prev => prev + 1);
        }
    };

    const prevStep = () => {
        if (currentStep > 1) {
            setCurrentStep(prev => prev - 1);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-gray-100 transform transition-all duration-300 hover:shadow-2xl">
                <div className="text-center">
                    <div className="mx-auto h-12 w-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full flex items-center justify-center mb-4">
                        <Shield className="h-6 w-6 text-white" />
                    </div>
                    <h2 className="mt-2 text-center text-3xl font-extrabold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                        Register Your Organization
                    </h2>
                    <p className="mt-2 text-center text-sm text-gray-600">
                        Create your account to get started
                    </p>
                    
                    {/* Progress Steps */}
                    <div className="mt-6 flex items-center justify-center space-x-4">
                        {[...Array(totalSteps)].map((_, index) => (
                            <div key={index} className="flex items-center">
                                <div className={`h-2 w-2 rounded-full ${
                                    currentStep > index + 1 
                                        ? 'bg-blue-600' 
                                        : currentStep === index + 1 
                                            ? 'bg-blue-600 animate-pulse' 
                                            : 'bg-gray-300'
                                }`} />
                                {index < totalSteps - 1 && (
                                    <div className={`h-0.5 w-8 ${
                                        currentStep > index + 1 ? 'bg-blue-600' : 'bg-gray-300'
                                    }`} />
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {showOtpInput ? (
                    <OTPVerification
                        email={formData.email}
                        onVerify={handleOtpSubmit}
                        resendOTP={handleResendOtp}
                        loading={loading}
                    />
                ) : (
                    <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
                        <div className="space-y-4">
                            {currentStep === 1 ? (
                                <>
                                    <div>
                                        <label htmlFor="organizationName" className="block text-sm font-medium text-gray-700">
                                            Organization Name
                                        </label>
                                        <div className="relative mt-1 group">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <Building2 className="h-5 w-5 text-gray-400 group-hover:text-gray-500 transition-colors duration-200" />
                                            </div>
                                            <input
                                                id="organizationName"
                                                name="organizationName"
                                                type="text"
                                                required
                                                className="block w-full pl-10 px-4 py-3 border border-gray-200 rounded-lg shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ease-in-out group-hover:border-gray-300"
                                                placeholder="Enter organization name"
                                                value={formData.organizationName}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>

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
                                                value={formData.email}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>

                                    <PasswordInput
                                        id="password"
                                        name="password"
                                        value={formData.password}
                                        onChange={handleChange}
                                        placeholder="Create a password"
                                        required
                                        label="Password"
                                    />

                                    <PasswordInput
                                        id="confirmPassword"
                                        name="confirmPassword"
                                        value={formData.confirmPassword}
                                        onChange={handleChange}
                                        placeholder="Confirm your password"
                                        required
                                        label="Confirm Password"
                                    />
                                </>
                            ) : (
                                <>
                                    <div>
                                        <label htmlFor="organizationType" className="block text-sm font-medium text-gray-700">
                                            Organization Type
                                        </label>
                                        <div className="relative mt-1 group">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <Building2 className="h-5 w-5 text-gray-400 group-hover:text-gray-500 transition-colors duration-200" />
                                            </div>
                                            <select
                                                id="organizationType"
                                                name="organizationType"
                                                required
                                                className="block w-full pl-10 px-4 py-3 border border-gray-200 rounded-lg shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ease-in-out group-hover:border-gray-300"
                                                value={formData.organizationType}
                                                onChange={handleChange}
                                            >
                                                <option value="">Select organization type</option>
                                                {organizationTypes.map(type => (
                                                    <option key={type.value} value={type.value}>
                                                        {type.label}
                                                    </option>
                                                ))}
                                            </select>
                                        </div>
                                    </div>

                                    <div>
                                        <label htmlFor="contact" className="block text-sm font-medium text-gray-700">
                                            Contact Number
                                        </label>
                                        <div className="relative mt-1 group">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <Phone className="h-5 w-5 text-gray-400 group-hover:text-gray-500 transition-colors duration-200" />
                                            </div>
                                            <input
                                                id="contact"
                                                name="contact"
                                                type="tel"
                                                required
                                                className="block w-full pl-10 px-4 py-3 border border-gray-200 rounded-lg shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ease-in-out group-hover:border-gray-300"
                                                placeholder="Enter contact number"
                                                value={formData.contact}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>

                                    <div>
                                        <label htmlFor="location" className="block text-sm font-medium text-gray-700">
                                            Location
                                        </label>
                                        <div className="relative mt-1 group">
                                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                                <MapPin className="h-5 w-5 text-gray-400 group-hover:text-gray-500 transition-colors duration-200" />
                                            </div>
                                            <input
                                                id="location"
                                                name="location"
                                                type="text"
                                                required
                                                className="block w-full pl-10 px-4 py-3 border border-gray-200 rounded-lg shadow-sm placeholder-gray-400 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all duration-200 ease-in-out group-hover:border-gray-300"
                                                placeholder="Enter location"
                                                value={formData.location}
                                                onChange={handleChange}
                                            />
                                        </div>
                                    </div>
                                </>
                            )}
                        </div>

                        <div className="flex items-center justify-between space-x-4">
                            {currentStep > 1 && (
                                <button
                                    type="button"
                                    onClick={prevStep}
                                    className="flex-1 py-3 px-4 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 ease-in-out transform hover:scale-[1.02]"
                                >
                                    Previous
                                </button>
                            )}
                            {currentStep < totalSteps ? (
                                <button
                                    type="button"
                                    onClick={nextStep}
                                    className="flex-1 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 ease-in-out transform hover:scale-[1.02] hover:shadow-lg"
                                >
                                    Next
                                </button>
                            ) : (
                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="flex-1 py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 ease-in-out transform hover:scale-[1.02] hover:shadow-lg"
                                >
                                    {loading ? (
                                        <span className="flex items-center justify-center">
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
                                            Registering...
                                        </span>
                                    ) : (
                                        'Register'
                                    )}
                                </button>
                            )}
                        </div>

                        <div className="text-center">
                            <p className="text-sm text-gray-600">
                                Already have an account?{' '}
                                <Link 
                                    href="/login" 
                                    className="font-medium text-blue-600 hover:text-blue-500 transition-colors duration-200 hover:underline"
                                >
                                    Sign in
                                </Link>
                            </p>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}