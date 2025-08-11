"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import RegisterForm from '../components/RegisterForm';

export default function RegisterPage() {
    const { user } = useAuth();
  const router = useRouter();

  useEffect(() => {
        if (user) {
            router.push('/dashboard');
        }
    }, [user, router]);

    return <RegisterForm />;
}
