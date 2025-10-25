"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import { AlertTriangle, Activity, TrendingUp, TrendingDown, Users, FileText, Calendar } from 'lucide-react';
import HealthMetricsDashboard from '../components/HealthMetricsDashboard';
import SecureComputationDashboard from '../components/SecureComputationDashboard';
import { API_ENDPOINTS } from '../config/api';

export default function AnalyticsPage() {
  const router = useRouter();
  const { user, refreshToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analytics, setAnalytics] = useState(null);

  useEffect(() => {
    async function fetchAnalytics() {
      if (!user?.token) {
        router.push('/login');
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(API_ENDPOINTS.analytics, {
          headers: {
            'Authorization': `Bearer ${user.token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
            const refreshed = await refreshToken();
            if (refreshed) {
              return; // useEffect will run again with new token
            } else {
              setError('Your session has expired. Please log in again.');
              router.push('/login');
              return;
            }
          }
          throw new Error(`Failed to fetch analytics: ${response.statusText}`);
        }

        const data = await response.json();
        setAnalytics(data);
        setError(null);
      } catch (err) {
        console.error('Error fetching analytics:', err);
        setError(err.message || 'Failed to load analytics data');
      } finally {
        setLoading(false);
      }
    }

    fetchAnalytics();
  }, [user, router, refreshToken]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-6">
          <div className="flex flex-col items-center text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
              <AlertTriangle className="h-8 w-8 text-red-400" />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">Error Loading Analytics</h3>
            <p className="text-gray-600 mb-6">{error}</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Health Analytics Dashboard</h1>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Total Uploads</h3>
            <FileText className="h-6 w-6 text-blue-500" />
          </div>
          <p className="text-3xl font-bold">{analytics?.total_uploads || 0}</p>
          <p className="text-sm text-gray-500 mt-2">Across all categories</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Active Users</h3>
            <Users className="h-6 w-6 text-green-500" />
          </div>
          <p className="text-3xl font-bold">{analytics?.active_users || 0}</p>
          <p className="text-sm text-gray-500 mt-2">In the last 30 days</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Analysis Run</h3>
            <Activity className="h-6 w-6 text-purple-500" />
          </div>
          <p className="text-3xl font-bold">{analytics?.total_analysis || 0}</p>
          <p className="text-sm text-gray-500 mt-2">Total analysis performed</p>
        </div>
      </div>

      {/* Health Metrics Dashboard */}
      {analytics?.health_metrics && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold mb-4">Health Metrics Overview</h2>
          <HealthMetricsDashboard patientData={analytics.health_metrics} />
        </div>
      )}

      {/* Secure Computation Dashboard */}
      <div className="mb-8">
        <SecureComputationDashboard user={user} />
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-semibold mb-4">Recent Activity</h2>
        <div className="space-y-4">
          {analytics?.recent_activity?.map((activity, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center">
                <Calendar className="h-5 w-5 text-gray-400 mr-3" />
                <div>
                  <p className="font-medium">{activity.description}</p>
                  <p className="text-sm text-gray-500">{activity.timestamp}</p>
                </div>
              </div>
              <span className={`px-3 py-1 rounded-full text-sm ${
                activity.type === 'upload' ? 'bg-blue-100 text-blue-800' :
                activity.type === 'analysis' ? 'bg-green-100 text-green-800' :
                'bg-gray-100 text-gray-800'
              }`}>
                {activity.type}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}