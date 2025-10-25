"use client";

import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Calendar, Clock } from 'lucide-react';

export default function AppointmentsPage() {
  const { user, isAuthenticated } = useAuth();

  // Sample appointments data (in a real app, this would come from an API)
  const sampleAppointments = [
    {
      id: 1,
      provider: 'Dr. Sarah Johnson',
      facility: 'City General Hospital',
      date: '2023-11-15',
      time: '09:30 AM',
      type: 'Annual Check-up',
      status: 'Upcoming'
    },
    {
      id: 2,
      provider: 'Dr. Michael Chen',
      facility: 'Wellness Medical Center',
      date: '2023-11-22',
      time: '02:00 PM',
      type: 'Follow-up Consultation',
      status: 'Upcoming'
    },
    {
      id: 3,
      provider: 'Dr. Emily Rodriguez',
      facility: 'City General Hospital',
      date: '2023-10-30',
      time: '11:15 AM',
      type: 'Lab Results Review',
      status: 'Completed'
    }
  ];

  if (!isAuthenticated) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6">
            <div className="text-center space-y-2">
              <h2 className="text-xl font-semibold">Please Log In</h2>
              <p className="text-gray-500">You need to be logged in to view your appointments.</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Your Appointments</h1>
        <p className="text-gray-600">Manage your upcoming and past medical appointments</p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {sampleAppointments.map((appointment) => (
          <Card key={appointment.id} className={`border-l-4 ${appointment.status === 'Upcoming' ? 'border-l-blue-500' : 'border-l-gray-400'}`}>
            <CardContent className="p-6">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold text-lg">{appointment.type}</h3>
                  <p className="text-gray-700">With {appointment.provider}</p>
                  <p className="text-gray-600 text-sm">{appointment.facility}</p>
                </div>
                <div className={`px-3 py-1 rounded-full text-sm font-medium ${appointment.status === 'Upcoming' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'}`}>
                  {appointment.status}
                </div>
              </div>
              
              <div className="mt-4 flex items-center space-x-6">
                <div className="flex items-center">
                  <Calendar className="h-4 w-4 text-gray-500 mr-2" />
                  <span className="text-sm text-gray-600">{appointment.date}</span>
                </div>
                <div className="flex items-center">
                  <Clock className="h-4 w-4 text-gray-500 mr-2" />
                  <span className="text-sm text-gray-600">{appointment.time}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {sampleAppointments.length === 0 && (
        <div className="text-center py-8">
          <p className="text-gray-500">You don't have any appointments scheduled.</p>
        </div>
      )}

      <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
        <h3 className="text-md font-medium text-blue-800 mb-2">Appointment Information</h3>
        <p className="text-sm text-blue-700 mb-2">
          This is a demonstration page. In a real application, you would be able to:
        </p>
        <ul className="list-disc list-inside text-sm text-blue-700 space-y-1 ml-2">
          <li>Schedule new appointments with your healthcare providers</li>
          <li>Reschedule or cancel existing appointments</li>
          <li>Receive reminders for upcoming appointments</li>
          <li>View your appointment history</li>
        </ul>
      </div>
    </div>
  );
}