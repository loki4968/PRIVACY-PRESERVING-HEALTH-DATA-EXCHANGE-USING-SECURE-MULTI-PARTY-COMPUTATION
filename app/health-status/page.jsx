"use client";

import React from 'react';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import { Activity, Heart, Droplet, LineChart, Clock } from 'lucide-react';
import { Card, CardContent, CardTitle } from '../components/ui/card';

const HealthStatusPage = () => {
  const { user } = useAuth();

  // Sample health metrics data - in a real app, this would come from an API
  const healthMetrics = {
    bloodPressure: {
      current: '120/80',
      history: [{ date: '2023-01-01', value: '118/78' }, { date: '2023-02-01', value: '122/82' }],
      status: 'normal'
    },
    bloodSugar: {
      current: '95 mg/dL',
      history: [{ date: '2023-01-01', value: '92 mg/dL' }, { date: '2023-02-01', value: '98 mg/dL' }],
      status: 'normal'
    },
    heartRate: {
      current: '72 bpm',
      history: [{ date: '2023-01-01', value: '68 bpm' }, { date: '2023-02-01', value: '74 bpm' }],
      status: 'normal'
    },
    cholesterol: {
      current: '180 mg/dL',
      history: [{ date: '2023-01-01', value: '175 mg/dL' }, { date: '2023-02-01', value: '185 mg/dL' }],
      status: 'normal'
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'normal': return 'text-green-500';
      case 'elevated': return 'text-yellow-500';
      case 'high': return 'text-red-500';
      default: return 'text-gray-500';
    }
  };

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <p className="text-sm text-yellow-700">
                Please log in to access this page.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Health Status Monitoring</h1>
        <p className="text-gray-600">Track your health metrics and trends over time</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Blood Pressure Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-lg font-semibold">Blood Pressure</CardTitle>
              <Heart className="h-6 w-6 text-red-500" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-3xl font-bold">{healthMetrics.bloodPressure.current}</p>
                <p className={`text-sm font-medium ${getStatusColor(healthMetrics.bloodPressure.status)}`}>
                  {healthMetrics.bloodPressure.status.charAt(0).toUpperCase() + healthMetrics.bloodPressure.status.slice(1)}
                </p>
              </div>
              <div className="h-16 w-32 bg-gray-100 rounded-md flex items-center justify-center">
                <LineChart className="h-10 w-10 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Blood Sugar Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-lg font-semibold">Blood Sugar</CardTitle>
              <Droplet className="h-6 w-6 text-blue-500" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-3xl font-bold">{healthMetrics.bloodSugar.current}</p>
                <p className={`text-sm font-medium ${getStatusColor(healthMetrics.bloodSugar.status)}`}>
                  {healthMetrics.bloodSugar.status.charAt(0).toUpperCase() + healthMetrics.bloodSugar.status.slice(1)}
                </p>
              </div>
              <div className="h-16 w-32 bg-gray-100 rounded-md flex items-center justify-center">
                <LineChart className="h-10 w-10 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Heart Rate Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-lg font-semibold">Heart Rate</CardTitle>
              <Activity className="h-6 w-6 text-pink-500" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-3xl font-bold">{healthMetrics.heartRate.current}</p>
                <p className={`text-sm font-medium ${getStatusColor(healthMetrics.heartRate.status)}`}>
                  {healthMetrics.heartRate.status.charAt(0).toUpperCase() + healthMetrics.heartRate.status.slice(1)}
                </p>
              </div>
              <div className="h-16 w-32 bg-gray-100 rounded-md flex items-center justify-center">
                <LineChart className="h-10 w-10 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Cholesterol Card */}
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between mb-4">
              <CardTitle className="text-lg font-semibold">Cholesterol</CardTitle>
              <Clock className="h-6 w-6 text-yellow-500" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-3xl font-bold">{healthMetrics.cholesterol.current}</p>
                <p className={`text-sm font-medium ${getStatusColor(healthMetrics.cholesterol.status)}`}>
                  {healthMetrics.cholesterol.status.charAt(0).toUpperCase() + healthMetrics.cholesterol.status.slice(1)}
                </p>
              </div>
              <div className="h-16 w-32 bg-gray-100 rounded-md flex items-center justify-center">
                <LineChart className="h-10 w-10 text-blue-500" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Recent Health Reports</h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Report Type</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Provider</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Action</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2023-03-15</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Annual Physical</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">City Hospital</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Available</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 hover:text-blue-900">
                  <a href="#">View Report</a>
                </td>
              </tr>
              <tr>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">2023-02-10</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">Blood Test</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">Metro Lab</td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Available</span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-blue-600 hover:text-blue-900">
                  <a href="#">View Report</a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-blue-50 rounded-lg border border-blue-200 p-6">
        <h2 className="text-xl font-semibold text-blue-800 mb-4">Health Recommendations</h2>
        <ul className="space-y-3">
          <li className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="ml-3 text-sm text-gray-700">Schedule your next annual physical examination</p>
          </li>
          <li className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="ml-3 text-sm text-gray-700">Maintain a balanced diet rich in fruits and vegetables</p>
          </li>
          <li className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
            </div>
            <p className="ml-3 text-sm text-gray-700">Aim for at least 30 minutes of moderate exercise daily</p>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default HealthStatusPage;