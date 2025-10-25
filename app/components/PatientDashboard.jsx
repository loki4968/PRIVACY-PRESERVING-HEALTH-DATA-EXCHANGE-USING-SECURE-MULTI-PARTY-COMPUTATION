"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardTitle } from './ui/card';
import { toast } from 'react-hot-toast';
import { FileText, Activity, Calendar, Clock, ArrowRight, Heart, Droplet, Pill, Download } from 'lucide-react';

const PatientDashboard = () => {
  const router = useRouter();
  const { user } = useAuth();
  
  // Health metrics state
  const [healthMetrics, setHealthMetrics] = useState({
    bloodPressure: {
      current: '120/80',
      status: 'normal'
    },
    bloodSugar: {
      current: '99 mg/dL',
      status: 'normal'
    },
    heartRate: {
      current: '72 bpm',
      status: 'normal'
    },
    cholesterol: {
      current: '180 mg/dL',
      status: 'normal'
    }
  });
  
  // Report request state
  const [loading, setLoading] = useState(false);
  const [requests, setRequests] = useState([
    { id: 1, organization: 'City General Hospital', date: '2023-05-15', status: 'completed', fileUrl: '#' },
    { id: 2, organization: 'Westside Medical Center', date: '2023-06-20', status: 'pending' }
  ]);
  
  const quickActions = [
    {
      title: 'Medical Records',
      description: 'Request and view your health records from providers',
      icon: <FileText className="h-8 w-8 text-blue-500" />,
      action: () => router.push('/reports'),
      color: 'bg-blue-50 border-blue-200 hover:bg-blue-100'
    },
    {
      title: 'Health Status',
      description: 'View your current health status and metrics',
      icon: <Activity className="h-8 w-8 text-green-500" />,
      action: () => router.push('/health-status'),
      color: 'bg-green-50 border-green-200 hover:bg-green-100'
    },
    {
      title: 'Appointments',
      description: 'Schedule and manage your medical appointments',
      icon: <Calendar className="h-8 w-8 text-purple-500" />,
      action: () => toast.success('Appointments feature coming soon!'),
      color: 'bg-purple-50 border-purple-200 hover:bg-purple-100'
    },
    {
      title: 'Secure Messaging',
      description: 'Communicate securely with your healthcare providers',
      icon: <Clock className="h-8 w-8 text-orange-500" />,
      action: () => toast.success('Secure messaging feature coming soon!'),
      color: 'bg-orange-50 border-orange-200 hover:bg-orange-100'
    }
  ];

  // Function to get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'normal':
        return 'text-green-600';
      case 'elevated':
        return 'text-yellow-600';
      case 'high':
        return 'text-red-600';
      case 'low':
        return 'text-blue-600';
      case 'completed':
        return 'text-green-500';
      case 'pending':
        return 'text-yellow-500';
      case 'rejected':
        return 'text-red-500';
      default:
        return 'text-gray-600';
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Welcome, {user?.name || 'Patient'}</h2>
        <p className="text-gray-600">Manage your health information and records</p>
      </div>

      {/* Welcome Card */}
      <div className="mb-8">
        <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold text-blue-800 mb-2">Your Health Portal</h3>
                <p className="text-gray-600">Access and manage your medical information securely in one place</p>
              </div>
              <Activity className="h-10 w-10 text-blue-500" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Health Services Section */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold mb-4">Health Services</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {quickActions.map((action, index) => (
            <Card 
              key={index} 
              className={`cursor-pointer hover:shadow-md transition-shadow ${action.color}`}
              onClick={action.action}
            >
              <CardContent className="p-6">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="text-lg font-semibold mb-2">{action.title}</CardTitle>
                    <p className="text-sm text-gray-600">{action.description}</p>
                  </div>
                  <div className="flex-shrink-0">
                    {action.icon}
                  </div>
                </div>
                <div className="mt-4 flex justify-end">
                  <span className="text-sm font-medium flex items-center gap-1 text-gray-700">
                    View <ArrowRight className="h-4 w-4" />
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      {/* Recent Report Requests */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-xl font-semibold">Recent Medical Records</h3>
          <button 
            onClick={() => router.push('/reports')} 
            className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
          >
            View All <ArrowRight className="h-4 w-4" />
          </button>
        </div>
        <Card className="shadow-sm border-gray-200">
          <CardContent className="p-6">
            {requests.length > 0 ? (
              <div className="space-y-4">
                {requests.map(request => (
                  <div key={request.id} className="border border-gray-100 rounded-lg p-4 hover:bg-gray-50 transition-colors">
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-medium text-gray-900">{request.organization}</h4>
                        <p className="text-sm text-gray-500">Requested on: {request.date}</p>
                      </div>
                      <span className={`px-2 py-1 text-xs rounded-full ${request.status === 'completed' ? 'bg-green-100 text-green-800' : request.status === 'pending' ? 'bg-yellow-100 text-yellow-800' : 'bg-red-100 text-red-800'}`}>
                        {request.status.charAt(0).toUpperCase() + request.status.slice(1)}
                      </span>
                    </div>
                    {request.status === 'completed' && (
                      <button 
                        className="mt-2 text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                        onClick={() => toast.success('Report downloaded successfully!')}
                      >
                        <Download className="h-4 w-4" />
                        Download Record
                      </button>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8 bg-gray-50 rounded-lg">
                <FileText className="h-12 w-12 text-gray-300 mx-auto mb-3" />
                <p className="text-gray-600 font-medium mb-2">No Medical Records Yet</p>
                <p className="text-gray-500 text-sm mb-4">Request your medical records from healthcare providers</p>
                <button
                  onClick={() => router.push('/reports')}
                  className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors"
                >
                  Request Records
                </button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Health Resources Section */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-100 shadow-sm">
        <div className="flex items-start mb-4">
          <div className="bg-white p-2 rounded-full mr-3">
            <Activity className="h-6 w-6 text-blue-500" />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-blue-800 mb-2">Health Resources</h3>
            <p className="text-gray-600 mb-4">Maximize your healthcare experience with these best practices</p>
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg p-4 border border-blue-50">
            <h4 className="font-medium text-blue-700 mb-2">Medical Records</h4>
            <p className="text-sm text-gray-600">Request your records after each visit to maintain a complete health history</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-blue-50">
            <h4 className="font-medium text-blue-700 mb-2">Provider Communication</h4>
            <p className="text-sm text-gray-600">Share your complete health data with all your healthcare providers</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-blue-50">
            <h4 className="font-medium text-blue-700 mb-2">Profile Accuracy</h4>
            <p className="text-sm text-gray-600">Keep your contact and insurance information up to date</p>
          </div>
          <div className="bg-white rounded-lg p-4 border border-blue-50">
            <h4 className="font-medium text-blue-700 mb-2">Privacy Protection</h4>
            <p className="text-sm text-gray-600">Regularly review who has access to your health information</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatientDashboard;