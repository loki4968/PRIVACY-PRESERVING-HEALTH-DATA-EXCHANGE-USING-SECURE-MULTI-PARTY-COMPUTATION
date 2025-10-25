"use client";

import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent } from '../components/ui/card';
import { FileText, Download, Upload, Activity, Clock } from 'lucide-react';

export default function ActivitiesPage() {
  const { user, isAuthenticated } = useAuth();

  // Sample activities data (in a real app, this would come from an API)
  const sampleActivities = [
    {
      id: 1,
      type: 'report_request',
      description: 'Requested medical report from City General Hospital',
      date: '2023-11-10',
      time: '14:25',
      icon: <FileText className="h-5 w-5 text-blue-500" />
    },
    {
      id: 2,
      type: 'report_download',
      description: 'Downloaded Annual Check-up Report',
      date: '2023-11-08',
      time: '09:12',
      icon: <Download className="h-5 w-5 text-green-500" />
    },
    {
      id: 3,
      type: 'health_update',
      description: 'Updated blood pressure readings',
      date: '2023-11-05',
      time: '16:40',
      icon: <Activity className="h-5 w-5 text-purple-500" />
    },
    {
      id: 4,
      type: 'file_upload',
      description: 'Uploaded lab test results',
      date: '2023-11-01',
      time: '11:30',
      icon: <Upload className="h-5 w-5 text-orange-500" />
    },
    {
      id: 5,
      type: 'report_request',
      description: 'Requested medical report from Wellness Medical Center',
      date: '2023-10-28',
      time: '15:15',
      icon: <FileText className="h-5 w-5 text-blue-500" />
    }
  ];

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center space-y-2">
              <h2 className="text-xl font-semibold">Please Log In</h2>
              <p className="text-gray-500">You need to be logged in to view your activities.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Recent Activities</h1>
        <p className="text-gray-600">Track your recent health-related activities</p>
      </div>

      <div className="space-y-4">
        {sampleActivities.map((activity) => (
          <Card key={activity.id} className="hover:shadow-sm transition-shadow">
            <CardContent className="p-4">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-full bg-gray-50">
                  {activity.icon}
                </div>
                <div className="flex-1">
                  <p className="font-medium text-gray-900">{activity.description}</p>
                  <div className="flex items-center mt-1 text-sm text-gray-500">
                    <Clock className="h-3 w-3 mr-1" />
                    <span>{activity.date} at {activity.time}</span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {sampleActivities.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">No recent activities to display.</p>
        </div>
      )}

      <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
        <h3 className="text-md font-medium text-blue-800 mb-2">Activity Tracking</h3>
        <p className="text-sm text-blue-700 mb-2">
          This is a demonstration page. In a real application, this page would automatically track:
        </p>
        <ul className="list-disc list-inside text-sm text-blue-700 space-y-1 ml-2">
          <li>All your report requests and downloads</li>
          <li>Health data updates and uploads</li>
          <li>Appointment scheduling and changes</li>
          <li>Profile information updates</li>
        </ul>
      </div>
    </div>
  );
}