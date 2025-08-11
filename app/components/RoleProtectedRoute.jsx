"use client";

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import { hasPermission, hasRole } from '../config/roles';

const RoleProtectedRoute = ({ 
  children, 
  requiredRole = null,
  requiredPermissions = [],
  fallbackPath = '/dashboard'
}) => {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      if (!user) {
        router.push('/login');
        return;
      }

      // Check role if required
      if (requiredRole && !hasRole(user.role, requiredRole)) {
        router.push(fallbackPath);
        return;
      }

      // Check permissions if required
      if (requiredPermissions.length > 0) {
        const hasAllPermissions = requiredPermissions.every(permission =>
          hasPermission(user.permissions || [], permission)
        );
        
        if (!hasAllPermissions) {
          router.push(fallbackPath);
          return;
        }
      }
    }
  }, [user, loading, requiredRole, requiredPermissions, router, fallbackPath]);

  // Show loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // If all checks pass, render children
  return user ? children : null;
};

export default RoleProtectedRoute; 