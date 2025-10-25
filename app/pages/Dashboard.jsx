import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { API_ENDPOINTS } from '../config/api';
import SecureComputationDashboard from '../components/SecureComputationDashboard';
import HealthMetricsDashboard from '../components/HealthMetricsDashboard';
import { AlertTriangle } from 'lucide-react';

const Dashboard = () => {
  const { user } = useAuth();
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchHealthData();
  }, []);

  const fetchHealthData = async () => {
    try {
      setLoading(true);
      const response = await fetch(API_ENDPOINTS.analytics, {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch health data');
      }

      const data = await response.json();
      setHealthData(data.health_metrics);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Health Data Exchange Dashboard</h1>

      {error && (
        <div className="mb-8 bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}
      
      {/* Health Metrics Overview */}
      <div className="mb-12">
        <h2 className="text-2xl font-semibold mb-6">Health Metrics Overview</h2>
        <HealthMetricsDashboard patientData={healthData} />
      </div>

      {/* Secure Computation Section */}
      <div className="mb-8">
        <h2 className="text-2xl font-semibold mb-6">Secure Computations</h2>
        <SecureComputationDashboard user={user} />
      </div>
    </div>
  );
};

export default Dashboard; 