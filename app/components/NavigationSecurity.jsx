"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';

/**
 * NavigationSecurity component handles browser navigation security
 * - Prevents access to login page when already authenticated
 * - Handles browser back button behavior
 * - Maintains authentication state during page refresh
 */
export default function NavigationSecurity() {
  const router = useRouter();
  const { user, loading } = useAuth();

  useEffect(() => {
    // Handle navigation security when authentication state changes
    if (!loading) {
      // Get current path
      const currentPath = window.location.pathname;
      
      // If user is authenticated and trying to access login/register pages
      // redirect to dashboard
      if (user && ["/login", "/register", "/forgot-password", "/reset-password"].includes(currentPath)) {
        router.replace("/dashboard");
      }
    }
  }, [user, loading, router]);

  useEffect(() => {
    // Handle browser back button
    const handlePopState = () => {
      const currentPath = window.location.pathname;
      
      // If user is authenticated and trying to go back to login page
      if (user && ["/login", "/register", "/forgot-password", "/reset-password"].includes(currentPath)) {
        // Prevent navigation to login page
        router.replace("/dashboard");
      }
      
      // If user is not authenticated and trying to access protected pages
      if (!user && !['/login', '/register', '/forgot-password', '/reset-password'].includes(currentPath)) {
        router.replace("/login");
      }
    };

    // Add event listener for popstate (back/forward buttons)
    window.addEventListener('popstate', handlePopState);
    
    // Clean up event listener
    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [user, router]);

  // This component doesn't render anything
  return null;
}