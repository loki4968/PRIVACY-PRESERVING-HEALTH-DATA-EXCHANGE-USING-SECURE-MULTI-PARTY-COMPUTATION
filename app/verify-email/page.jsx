"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import { Card, CardTitle, CardContent, CardFooter } from '../components/ui/card';
import { CustomButton } from '../components/ui/custom-button';
import { Mail, ArrowRight, RefreshCw } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { API_ENDPOINTS } from '../config/api';

export default function VerifyEmailPage() {
  const [verificationCode, setVerificationCode] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [resending, setResending] = useState(false);
  const router = useRouter();
  const { user } = useAuth();

  useEffect(() => {
    if (!user) {
      router.push('/login');
    }
  }, [user, router]);

  const handleResendCode = async () => {
    setResending(true);
    try {
      const response = await fetch(API_ENDPOINTS.sendOtp, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          email: user.email,
          purpose: 'email_verification'
        })
      });

      if (response.ok) {
        toast.success('Verification code sent! Please check your email.');
      } else {
        const data = await response.json();
        throw new Error(data.detail || 'Failed to send verification code');
      }
    } catch (error) {
      console.error('Error sending verification code:', error);
      toast.error(error.message);
    } finally {
      setResending(false);
    }
  };

  const handleVerify = async (e) => {
    e.preventDefault();
    if (!verificationCode) {
      toast.error('Please enter the verification code');
      return;
    }

    setIsSubmitting(true);
    try {
      const response = await fetch(API_ENDPOINTS.verifyOtp, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${user.token}`
        },
        body: JSON.stringify({
          email: user.email,
          code: verificationCode,
          purpose: 'email_verification'
        })
      });

      const responseData = await response.json();

      if (response.ok) {
        toast.success('Email verified successfully!');
        // Redirect back to upload page
        router.push('/upload');
      } else {
        throw new Error(responseData.detail || 'Verification failed');
      }
    } catch (error) {
      console.error('Verification error:', error);
      toast.error(error.message);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-green-50 p-6">
      <Card className="w-full max-w-md">
        <CardTitle className="p-6 text-center">
          <div className="flex flex-col items-center space-y-4">
            <div className="p-3 bg-blue-100 rounded-full">
              <Mail className="w-8 h-8 text-blue-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900">Verify Your Email</h1>
          </div>
        </CardTitle>

        <CardContent className="space-y-4">
          <p className="text-center text-gray-600">
            We've sent a verification code to<br />
            <span className="font-medium text-gray-900">{user?.email}</span>
          </p>

          <form onSubmit={handleVerify} className="space-y-4">
            <div>
              <input
                type="text"
                value={verificationCode}
                onChange={(e) => setVerificationCode(e.target.value)}
                placeholder="Enter verification code"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                disabled={isSubmitting}
              />
            </div>

            <CustomButton
              type="submit"
              variant="primary"
              size="large"
              className="w-full"
              disabled={isSubmitting}
              loading={isSubmitting}
              icon={ArrowRight}
            >
              {isSubmitting ? 'Verifying...' : 'Verify Email'}
            </CustomButton>
          </form>
        </CardContent>

        <CardFooter className="flex flex-col items-center space-y-4 border-t border-gray-200 p-6">
          <p className="text-sm text-gray-600">
            Didn't receive the code?
          </p>
          <CustomButton
            onClick={handleResendCode}
            variant="outline"
            size="small"
            disabled={resending}
            loading={resending}
            icon={RefreshCw}
          >
            Resend Code
          </CustomButton>
        </CardFooter>
      </Card>
    </div>
  );
}