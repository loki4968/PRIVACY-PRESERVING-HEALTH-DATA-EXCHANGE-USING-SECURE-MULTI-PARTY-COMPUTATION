"use client";

import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';
import { 
  createReportRequest, 
  getReportRequests, 
  downloadReportFile,
  getHealthcareOrganizations
} from '../services/reportRequestService';
import { 
  Calendar, 
  Building, 
  FileText, 
  Send, 
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  HelpCircle
} from 'lucide-react';

const PatientReportRequest = () => {
  const { user } = useAuth();
  const [organizations, setOrganizations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [requests, setRequests] = useState([]);
  const [formData, setFormData] = useState({
    organizationId: '',
    visitDate: '',
    description: ''
  });

  // Fetch organizations when component mounts
  useEffect(() => {
    fetchOrganizations();
    fetchRequests();
  }, []);

  const fetchOrganizations = async () => {
    try {
      setLoading(true);
      // Fetch organizations from the API
      const { data } = await getHealthcareOrganizations();
      setOrganizations(data);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching organizations:', error);
      toast.error('Failed to fetch organizations');
      setLoading(false);
    }
  };

  const fetchRequests = async () => {
    try {
      // Fetch report requests from the API
      const { data } = await getReportRequests();
      setRequests(data);
    } catch (error) {
      console.error('Error fetching requests:', error);
      toast.error('Failed to fetch requests');
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.organizationId || !formData.visitDate) {
      toast.error('Please select an organization and visit date');
      return;
    }

    try {
      // Create a new report request using the API
      const requestData = {
        organization_id: formData.organizationId,
        visit_date: formData.visitDate,
        description: formData.description
      };
      
      await createReportRequest(requestData);
      toast.success('Report request submitted successfully');
      
      // Reset form
      setFormData({
        organizationId: '',
        visitDate: '',
        description: ''
      });
      
      // Refresh the requests list
      fetchRequests();
    } catch (error) {
      console.error('Error submitting request:', error);
      toast.error('Failed to submit request');
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'approved':
        return (
          <span className="flex items-center gap-1 text-green-700 bg-green-100 px-2 py-1 rounded-full text-xs">
            <CheckCircle className="w-3 h-3" />
            Approved
          </span>
        );
      case 'pending':
        return (
          <span className="flex items-center gap-1 text-yellow-700 bg-yellow-100 px-2 py-1 rounded-full text-xs">
            <Clock className="w-3 h-3" />
            Pending
          </span>
        );
      case 'rejected':
        return (
          <span className="flex items-center gap-1 text-red-700 bg-red-100 px-2 py-1 rounded-full text-xs">
            <XCircle className="w-3 h-3" />
            Rejected
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-gray-700 bg-gray-100 px-2 py-1 rounded-full text-xs">
            Unknown
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-64">
        <RefreshCw className="w-8 h-8 animate-spin text-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header with Help */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Request Medical Reports</h2>
          <p className="text-gray-600">Get your health records from your healthcare providers</p>
        </div>
        <div className="relative group">
          <button className="p-2 rounded-full bg-blue-50 text-blue-600 hover:bg-blue-100">
            <HelpCircle className="w-5 h-5" />
          </button>
          <div className="absolute right-0 w-64 p-3 mt-2 bg-white rounded-lg shadow-lg border border-gray-200 hidden group-hover:block z-10">
            <p className="text-sm text-gray-600">Request your medical reports from any healthcare organization you've visited. Once approved, you can download your reports directly.</p>
          </div>
        </div>
      </div>

      {/* Quick Guide */}
      <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
        <h3 className="text-md font-medium text-blue-800 mb-2 flex items-center">
          <FileText className="w-5 h-5 mr-2" /> How to request your medical reports:
        </h3>
        <ol className="list-decimal list-inside text-sm text-blue-700 space-y-1 ml-2">
          <li>Select the healthcare organization</li>
          <li>Enter the date of your visit</li>
          <li>Describe what report you need (optional)</li>
          <li>Submit your request</li>
        </ol>
      </div>

      {/* Request Form - Simplified */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">New Report Request</h3>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Healthcare Provider
            </label>
            <div className="relative">
              <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <select
                name="organizationId"
                value={formData.organizationId}
                onChange={handleInputChange}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select your healthcare provider</option>
                {organizations.map(org => (
                  <option key={org.id} value={org.id}>
                    {org.name} ({org.type})
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Date of Visit
            </label>
            <div className="relative">
              <Calendar className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="date"
                name="visitDate"
                value={formData.visitDate}
                onChange={handleInputChange}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              What report do you need? (Optional)
            </label>
            <div className="relative">
              <FileText className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Example: Blood test results, X-ray images, Vaccination records"
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500"
                rows="2"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full flex items-center justify-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Send className="w-5 h-5" />
            Request My Report
          </button>
        </form>
      </div>

      {/* Request History */}
      <div>
        <h3 className="text-lg font-semibold mb-4">Your Report Requests</h3>
        {requests.length === 0 ? (
          <div className="text-center py-8 bg-gray-50 rounded-lg border border-gray-200">
            <FileText className="w-12 h-12 text-gray-400 mx-auto mb-3" />
            <p className="text-gray-600">You haven't requested any reports yet</p>
            <p className="text-sm text-gray-500 mt-2">Your report requests will appear here after you submit them</p>
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map(request => (
              <div key={request.id} className="bg-white rounded-lg border border-gray-200 p-4">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-medium text-gray-900">{request.organizationName}</h4>
                  {getStatusBadge(request.status)}
                </div>
                <div className="text-sm text-gray-600 mb-2">
                  <p><span className="font-medium">Visit Date:</span> {request.visitDate}</p>
                  {request.description && (
                    <p><span className="font-medium">Description:</span> {request.description}</p>
                  )}
                </div>
                <div className="text-xs text-gray-500 flex justify-between">
                  <span>Requested: {request.requestDate}</span>
                  {request.responseDate && (
                    <span>Response: {request.responseDate}</span>
                  )}
                </div>
                {request.status === 'rejected' && request.rejectionReason && (
                  <div className="mt-2 text-sm text-red-600 bg-red-50 p-2 rounded">
                    <span className="font-medium">Reason:</span> {request.rejectionReason}
                  </div>
                )}
                {request.status === 'approved' && (
                  <div className="mt-3">
                    <button 
                      className="text-white bg-green-600 hover:bg-green-700 px-4 py-2 rounded-lg text-sm flex items-center gap-1"
                      onClick={() => {
                        downloadReportFile(request.id);
                        toast.success('Report download initiated');
                      }}
                    >
                      <FileText className="w-4 h-4" /> Download My Report
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default PatientReportRequest;