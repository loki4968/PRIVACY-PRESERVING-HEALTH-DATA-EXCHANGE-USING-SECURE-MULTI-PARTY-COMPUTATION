'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../../context/AuthContext';
import { toast } from 'sonner';
import { 
  ArrowLeft, 
  Upload, 
  Shield, 
  CheckCircle, 
  AlertCircle,
  FileText,
  Lock
} from 'lucide-react';
import Link from 'next/link';
import { secureComputationService } from '../../../services/secureComputationService';

export default function SubmitDataPage() {
  const { id } = useParams();
  const router = useRouter();
  const { user } = useAuth();

  // Check if user has permission to access secure computations
  if (user?.role === 'patient') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600 mb-6">You don't have permission to access secure computations.</p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }
  const [computation, setComputation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [submissionDetails, setSubmissionDetails] = useState(null);
  const [formData, setFormData] = useState({
    dataPoints: '',
    parsedDataPoints: [],
    description: '',
    securityMethod: 'standard',
    inputMethod: 'manual',
    fileName: ''
  });
  const [csvState, setCsvState] = useState({
    file: null,
    hasHeader: true,
    delimiter: ',',
    column: '',
    columns: '',
    columnIndex: ''
  });

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    fetchComputationDetails();
  }, [id, user]);

  // Effect to validate security method against computation type
  useEffect(() => {
    if (computation && computation.type && !computation.type.startsWith('secure_')) {
      if (formData.securityMethod === 'hybrid') {
        setFormData(prev => ({ ...prev, securityMethod: 'standard' }));
        toast.info('Hybrid encryption is only for secure computation types. Switched to Standard Encryption.');
      }
    }
  }, [computation, formData.securityMethod]);

  const fetchComputationDetails = async () => {
    try {
      setLoading(true);
      const token = user?.token || localStorage.getItem('token');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch computation details');
      }

      const computationData = await response.json();
      setComputation(computationData);

      // Refresh submissions after successful upload
      await checkSubmissionStatus();
      
      // Fetch updated submission details for display
      try {
        const updatedSubmission = await secureComputationService.getUserSubmission(id, token);
        setSubmissionDetails(updatedSubmission);
      } catch (err) {
        console.warn('Could not fetch updated submission details:', err);
      }

    } catch (err) {
      console.error('Error fetching computation details:', err);
      setError(err.message);
      toast.error('Failed to load computation details');
    } finally {
      setLoading(false);
    }
  };

  const checkSubmissionStatus = async (token) => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}/my-submission`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const submissionData = await response.json();
        if (submissionData && submissionData.data_points) {
          setHasSubmitted(true);
          setSubmissionDetails(submissionData);
        }
      }
    } catch (err) {
      // If endpoint doesn't exist or fails, assume no submission
      console.log('Could not check submission status:', err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.csv')) {
      toast.error('Please upload a CSV file');
      return;
    }
    // Store file and show simple confirmation; backend will parse using mapping
    setCsvState(prev => ({ ...prev, file }));
    setFormData(prev => ({
      ...prev,
      dataPoints: '',
      parsedDataPoints: [],
      fileName: file.name
    }));
    toast.success('CSV file selected. It will be parsed on the server with your mapping.');
  };

  // Function to reset form fields
  const resetForm = () => {
    setFormData({
      dataPoints: '',
      parsedDataPoints: [],
      description: '',
      securityMethod: 'standard',
      inputMethod: 'manual',
      fileName: ''
    });
    
    // Clear file input if it exists
    const fileInput = document.getElementById('csvFile');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.dataPoints.trim() && formData.inputMethod !== 'csv') {
      toast.error('Please enter data points');
      return;
    }
    
    try {
      setSubmitting(true);
      const token = user?.token || localStorage.getItem('token');
      
      // Parse data points (expecting comma-separated numbers)
      let dataPoints = [];
      
      if (formData.dataPoints && formData.dataPoints.trim()) {
        dataPoints = formData.dataPoints.split(',').map(point => {
          const trimmedPoint = point.trim();
          if (!trimmedPoint) return null; // Skip empty entries
          
          const num = parseFloat(trimmedPoint);
          if (isNaN(num)) {
            throw new Error(`Invalid data point: ${trimmedPoint}`);
          }
          return num;
        }).filter(point => point !== null); // Remove any null values
      }
      
      // Validate that we have data points
      if (dataPoints.length === 0 && formData.inputMethod !== 'csv') {
        throw new Error('No valid data points provided');
      }

      let result;
      let submissionSuccessful = false;
      
      try {
        if (formData.inputMethod === 'csv' && formData.fileName) {
          // Submit the raw file to backend with mapping options
          if (!csvState.file) {
            throw new Error('No CSV file selected');
          }
          const csvOptions = {
            has_header: csvState.hasHeader,
            delimiter: csvState.delimiter || ',',
            column: csvState.columns ? undefined : (csvState.column || undefined),
            columns: csvState.columns || undefined,
            column_index: csvState.columnIndex !== '' ? parseInt(csvState.columnIndex, 10) : undefined,
            security_method: formData.securityMethod || 'standard'
          };
          console.log('Submitting CSV via /submit-csv with options:', csvOptions);
          result = await secureComputationService.submitCsv(id, csvState.file, csvOptions, token);
          submissionSuccessful = true;
        } else {
          // Use JSON for manual data entry
          const submissionData = {
            value: dataPoints,  // Array of numeric values
            encryption_type: formData.securityMethod || 'standard'
          };
          
          console.log('Submitting data:', JSON.stringify(submissionData));
          result = await secureComputationService.submitData(id, submissionData, token);
          submissionSuccessful = true;
        }
      } catch (error) {
        console.error('Error submitting data:', error);
        
        // Extract error details from the error object
        let errorMessage = 'Failed to submit data';
        let errorDetails = '';
        
        if (error.message) {
          errorMessage = error.message;
        }
        
        if (error.status) {
          errorDetails += ` (Status: ${error.status})`;
        }
        
        // Handle specific error codes if available
        if (error.error_code) {
          switch(error.error_code) {
            case 'INVALID_DATA_FORMAT':
              errorDetails += ' Please check that your data is in the correct format (comma-separated numbers).';
              break;
            case 'NO_VALID_DATA':
              errorDetails += ' No valid numeric data points were found in your submission.';
              break;
            case 'ALREADY_SUBMITTED':
              errorDetails += ' You have already uploaded data for this computation. Each organization can only submit data once.';
              toast.error('Data Already Uploaded', {
                description: 'You have already submitted data for this computation. Each organization can only submit data once.',
                duration: 5000
              });
              return; // Exit early for duplicate submissions
            case 'NOT_A_PARTICIPANT':
              errorDetails += ' You must join this computation before submitting data.';
              break;
            default:
              errorDetails += ` Error code: ${error.error_code}`;
          }
        }
        
        const fullErrorMessage = errorDetails 
          ? `${errorMessage}${errorDetails}` 
          : errorMessage;
        
        throw new Error(fullErrorMessage);
      }
      
      // Only proceed with success actions if submission was successful
      if (submissionSuccessful) {
        // Show enhanced success message
        const dataPointsCount = result.data_points_count || dataPoints.length || formData.parsedDataPoints.length;
        const encryptionType = result.encryption_type || formData.securityMethod;
        
        toast.success('Data Uploaded Successfully!', {
          description: `Successfully submitted ${dataPointsCount} data points using ${encryptionType} encryption. Your data is now securely stored and ready for computation.`,
          duration: 6000
        });
        
        // Reset form
        resetForm();
        
        // Redirect to computation details page
        setTimeout(() => {
          router.push(`/secure-computations/${id}`);
        }, 1500);
      }

    } catch (err) {
      console.error('Error submitting data:', err);
      toast.error(err.message || 'Failed to submit data');
      // Stay on the current page when there's an error
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading computation details...</p>
        </div>
      </div>
    );
  }

  if (error || !computation) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Error Loading Computation</h1>
          <p className="text-gray-600 mb-6">{error || 'Computation not found'}</p>
          <Link
            href="/secure-computations"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href={`/secure-computations/${id}`}
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Computation Details
          </Link>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Submit Data
              </h1>
              <p className="text-gray-600 mt-1">
                Computation {computation.computation_id.slice(0, 8)}... • {computation.type || 'Secure Computation'}
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-500" />
              <span className="text-sm font-medium text-green-700">Secure Submission</span>
            </div>
          </div>
        </div>

        {/* Already Submitted Notice */}
        {hasSubmitted && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6 mb-6">
            <div className="flex items-start gap-3">
              <CheckCircle className="w-6 h-6 text-green-600 mt-0.5" />
              <div className="flex-1">
                <h3 className="font-semibold text-green-900 mb-2">Data Already Submitted</h3>
                <p className="text-green-700 mb-3">
                  You have already uploaded data for this computation. Each organization can only submit data once.
                </p>
                {submissionDetails && (
                  <div className="bg-white rounded-lg p-4 border border-green-200">
                    <h4 className="font-medium text-gray-900 mb-2">Submission Details:</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-gray-500">Data Points:</span>
                        <span className="ml-2 font-medium">{submissionDetails.data_points?.length || 0}</span>
                      </div>
                      <div>
                        <span className="text-gray-500">Submitted:</span>
                        <span className="ml-2 font-medium">
                          {submissionDetails.created_at ? new Date(submissionDetails.created_at).toLocaleDateString() : 'N/A'}
                        </span>
                      </div>
                      <div>
                        <span className="text-gray-500">Encryption:</span>
                        <span className="ml-2 font-medium">{submissionDetails.encryption_type || 'Standard'}</span>
                      </div>
                    </div>
                  </div>
                )}
                <div className="flex gap-3 mt-4">
                  <Link
                    href={`/secure-computations/${id}`}
                    className="inline-flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <ArrowLeft className="w-4 h-4" />
                    Back to Computation
                  </Link>
                  <Link
                    href={`/secure-computations/${id}/view-submission`}
                    className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <FileText className="w-4 h-4" />
                    View My Submission
                  </Link>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Submission Form */}
        <div className={`bg-white rounded-lg shadow-sm border p-8 ${hasSubmitted ? 'opacity-50 pointer-events-none' : ''}`}>
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
              <FileText className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h2 className="text-xl font-semibold text-gray-900">Data Submission</h2>
              <p className="text-gray-600">
                {hasSubmitted ? 'Data has already been submitted for this computation' : 'Enter your data points for secure computation'}
              </p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Data Input Method Selection */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Data Input Method
              </label>
              <div className="flex gap-4 mb-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="inputMethod"
                    value="manual"
                    checked={formData.inputMethod === 'manual'}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  Manual Entry
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    name="inputMethod"
                    value="csv"
                    checked={formData.inputMethod === 'csv'}
                    onChange={handleInputChange}
                    className="mr-2"
                  />
                  CSV File Upload
                </label>
              </div>
            </div>

            {/* Manual Data Entry */}
            {formData.inputMethod === 'manual' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Points *
                </label>
                <textarea
                  name="dataPoints"
                  value={formData.dataPoints}
                  onChange={handleInputChange}
                  placeholder="Enter comma-separated numbers (e.g., 120, 118, 122, 115, 125)"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows={4}
                  required
                />
                <p className="text-sm text-gray-500 mt-1">
                  Enter numeric values separated by commas
                </p>
              </div>
            )}

            {/* CSV File Upload */}
            {formData.inputMethod === 'csv' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload CSV File *
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <input
                    type="file"
                    accept=".csv"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="csvFile"
                  />
                  <label htmlFor="csvFile" className="cursor-pointer">
                    <div className="text-gray-500">
                      <svg className="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                        <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <p className="mt-2 text-sm">Click to upload CSV file</p>
                      <p className="text-xs text-gray-400">CSV files only</p>
                    </div>
                  </label>
                </div>
                {formData.fileName && (
                  <p className="text-sm text-green-600 mt-2">
                    File selected: {formData.fileName}
                  </p>
                )}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mt-4">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Has Header</label>
                    <select
                      className="w-full border border-gray-300 rounded p-2 text-sm"
                      value={csvState.hasHeader ? 'true' : 'false'}
                      onChange={(e) => setCsvState(prev => ({ ...prev, hasHeader: e.target.value === 'true' }))}
                    >
                      <option value="true">True</option>
                      <option value="false">False</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Delimiter</label>
                    <input
                      className="w-full border border-gray-300 rounded p-2 text-sm"
                      value={csvState.delimiter}
                      onChange={(e) => setCsvState(prev => ({ ...prev, delimiter: e.target.value }))}
                      placeholder=","/>
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Column Index (no header)</label>
                    <input
                      className="w-full border border-gray-300 rounded p-2 text-sm"
                      value={csvState.columnIndex}
                      onChange={(e) => setCsvState(prev => ({ ...prev, columnIndex: e.target.value }))}
                      placeholder="e.g., 0"
                    />
                  </div>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mt-3">
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Single Column (header name)</label>
                    <input
                      className="w-full border border-gray-300 rounded p-2 text-sm"
                      value={csvState.column}
                      onChange={(e) => setCsvState(prev => ({ ...prev, column: e.target.value }))}
                      placeholder="e.g., BloodSugar_mg_dL"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-600 mb-1">Multiple Columns (comma-separated)</label>
                    <input
                      className="w-full border border-gray-300 rounded p-2 text-sm"
                      value={csvState.columns}
                      onChange={(e) => setCsvState(prev => ({ ...prev, columns: e.target.value }))}
                      placeholder="e.g., systolic,diastolic"
                    />
                  </div>
                </div>
                <p className="text-xs text-gray-500 mt-2">
                  If both Single and Multiple Columns are provided, Multiple Columns take precedence. If none provided, the first column is used.
                </p>
              </div>
            )}

            {/* Description */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (Optional)
              </label>
              <input
                type="text"
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                placeholder="Brief description of your data"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            {/* Security Method */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Security Method
              </label>
              <select
                name="securityMethod"
                value={formData.securityMethod}
                onChange={handleInputChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="standard">Standard Encryption</option>
                <option value="homomorphic">Homomorphic Encryption</option>
                {computation && computation.type && computation.type.startsWith('secure_') && (
                  <option value="hybrid">Hybrid (HE + SMPC)</option>
                )}
              </select>
            </div>

            {/* Security Notice */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-start gap-3">
                <Lock className="w-5 h-5 text-blue-600 mt-0.5" />
                <div>
                  <h3 className="font-medium text-blue-900">Secure Data Handling</h3>
                  <p className="text-sm text-blue-700 mt-1">
                    Your data will be encrypted using the selected security method before transmission and computation. 
                    Only aggregated results will be visible to participants.
                  </p>
                </div>
              </div>
            </div>

            {/* Submit Button */}
            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                disabled={submitting || hasSubmitted}
                className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-lg transition-colors ${
                  hasSubmitted 
                    ? 'bg-gray-400 text-white cursor-not-allowed' 
                    : 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed'
                }`}
              >
                {hasSubmitted ? (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Data Already Submitted
                  </>
                ) : submitting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Submitting...
                  </>
                ) : (
                  <>
                    <Upload className="w-4 h-4" />
                    Submit Data
                  </>
                )}
              </button>
              
              <Link
                href={`/secure-computations/${id}`}
                className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors"
              >
                {hasSubmitted ? 'Back to Computation' : 'Cancel'}
              </Link>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
