'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useParams } from 'next/navigation';
import { toast } from 'sonner';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '../../../../components/ui/card';
import { Button } from '../../../../components/ui/button';
import { Skeleton } from '../../../../components/ui/skeleton';
import { secureComputationService } from '../../../services/secureComputationService';
import { useAuth } from '../../../context/AuthContext';
import { Badge } from '../../../../components/ui/badge';
import { ArrowLeft, Download, Eye, EyeOff, Shield, FileText, Calendar, Hash, CheckCircle, AlertCircle } from 'lucide-react';

export default function ViewSubmissionPage() {
  const { id } = useParams();
  const router = useRouter();
  const { token, user } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submission, setSubmission] = useState(null);
  const [showData, setShowData] = useState(false);
  const [deleting, setDeleting] = useState(false);
  
  // Redirect patients away from this page
  useEffect(() => {
    if (user?.role === 'patient') {
      toast.error('Patients cannot access secure computations');
      router.push('/');
    }
  }, [user?.role, router]);

  useEffect(() => {
    const fetchSubmission = async () => {
      if (!token) return;
      
      // Set a timeout to ensure loading state is cleared after 10 seconds
      const loadingTimeout = setTimeout(() => {
        if (loading) {
          console.log('Loading timeout reached, forcing loading state to false');
          setLoading(false);
          setError('Request timed out. Please try again.');
          toast.error('Request timed out. Please try again.');
        }
      }, 10000);
      
      try {
        setLoading(true);
        setError(null);
        
        // Try multiple endpoints to get submission data
        let data = null;
        
        // Try multiple API endpoints to find user submission
        const endpoints = [
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}/my-submission`,
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}/user-submission`,
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}/submissions/me`
        ];
        
        let lastError = null;
        
        for (const endpoint of endpoints) {
          try {
            console.log(`Trying endpoint: ${endpoint}`);
            const response = await fetch(endpoint, {
              headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            });
            
            if (response.ok) {
              data = await response.json();
              console.log('Fetched submission data from:', endpoint, data);
              break;
            } else if (response.status === 404) {
              console.log(`No data found at ${endpoint}`);
              continue;
            } else {
              const errorText = await response.text();
              console.warn(`Error from ${endpoint}:`, response.status, errorText);
              lastError = new Error(`${response.status}: ${errorText}`);
            }
          } catch (fetchErr) {
            console.warn(`Network error for ${endpoint}:`, fetchErr);
            lastError = fetchErr;
          }
        }
        
        // If no endpoint worked, check if we should show "no submission" state
        if (!data) {
          console.log('No submission data found from any endpoint');
          setSubmission(null);
          setError(null); // Don't show error for no submission
          clearTimeout(loadingTimeout);
          setLoading(false);
          return;
        }
        
        // Handle the response data
        if (data && (data.has_submitted === false || data.message === 'No submission found')) {
          setSubmission(null);
          setError(null); // Don't show error, just show no data state
        } else if (data && (data.data || data.submission_data || data.encrypted_data || data.value || data.values)) {
          // Normalize the data structure for different response formats
          const normalizedData = {
            ...data,
            data: data.data || data.submission_data || data.encrypted_data || data.value || data.values,
            data_points_count: data.data_points_count || 
                             (data.data ? (Array.isArray(data.data) ? data.data.length : 1) : 0) ||
                             (data.values ? (Array.isArray(data.values) ? data.values.length : 1) : 0) ||
                             (data.value ? 1 : 0),
            submitted_at: data.submitted_at || data.created_at || new Date().toISOString(),
            encryption_type: data.encryption_type || data.security_method || 'standard',
            has_submitted: true
          };
          console.log('Normalized submission data:', normalizedData);
          setSubmission(normalizedData);
        } else if (data && Object.keys(data).length > 0) {
          // Handle any other data format that might exist
          console.log('Found submission data in unknown format:', data);
          setSubmission({
            ...data,
            data: data,
            data_points_count: 1,
            submitted_at: data.submitted_at || new Date().toISOString(),
            encryption_type: 'standard',
            has_submitted: true
          });
        } else {
          setSubmission(null);
          setError(null);
        }
      } catch (err) {
        console.error('Error fetching user submission:', err);
        if (err.message.includes('404') || err.message.includes('not found')) {
          setSubmission(null);
          setError(null);
        } else {
          setError(err.message || 'Failed to fetch your submitted data');
          toast.error(err.message || 'Failed to fetch your submitted data');
        }
      } finally {
        clearTimeout(loadingTimeout);
        setLoading(false);
      }
    };

    fetchSubmission();
    
    // Cleanup function to clear timeout if component unmounts
    return () => {
      setLoading(false);
    };
  }, [id, token]);

  const handleBackClick = () => {
    router.push(`/secure-computations/${id}`);
  };

  const toggleShowData = () => {
    setShowData(!showData);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleString();
  };

  const downloadData = () => {
    if (!submission || !submission.data) return;
    
    const dataStr = JSON.stringify(submission.data, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `computation-${id}-submission.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const handleDeleteSubmission = async () => {
    if (!token || !id) return;
    
    if (!confirm('Are you sure you want to delete your submission? This action cannot be undone.')) {
      return;
    }
    
    try {
      setDeleting(true);
      await secureComputationService.deleteSubmission(id, token);
      toast.success('Your submission has been deleted successfully');
      router.push(`/secure-computations/${id}`);
    } catch (err) {
      console.error('Error deleting submission:', err);
      toast.error(err.message || 'Failed to delete your submission');
    } finally {
      setDeleting(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto p-4">
        <Button variant="ghost" onClick={handleBackClick} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Computation
        </Button>
        <Card>
          <CardHeader>
            <Skeleton className="h-12 w-3/4 mb-3" />
            <Skeleton className="h-6 w-1/2 mt-2" />
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <Skeleton className="h-8 w-48 mb-3" />
                <div className="grid grid-cols-2 gap-3 mt-3">
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                  <Skeleton className="h-6 w-full" />
                </div>
              </div>
              <div>
                <Skeleton className="h-8 w-64 mb-3" />
                <Skeleton className="h-32 w-full rounded-md" />
                <Skeleton className="h-5 w-3/4 mt-3" />
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex justify-between">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-40" />
          </CardFooter>
        </Card>
        <div className="text-center text-sm text-gray-500 mt-4">
          Loading your submission data...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto p-4">
        <Button variant="ghost" onClick={handleBackClick} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Computation
        </Button>
        <Card>
          <CardHeader>
            <CardTitle>Error</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-red-500">{error}</p>
            <p className="mt-4">
              You may not have submitted data for this computation yet, or there might be an issue with the server.
            </p>
          </CardContent>
          <CardFooter>
            <Button onClick={handleBackClick}>Return to Computation</Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  if (!submission) {
    return (
      <div className="container mx-auto p-4">
        <Button variant="ghost" onClick={handleBackClick} className="mb-4">
          <ArrowLeft className="mr-2 h-4 w-4" /> Back to Computation
        </Button>
        <Card>
          <CardHeader>
            <CardTitle>No Data Found</CardTitle>
          </CardHeader>
          <CardContent>
            <p>You have not submitted any data for this computation yet.</p>
          </CardContent>
          <CardFooter>
            <Button onClick={() => router.push(`/secure-computations/${id}/submit`)}>Submit Data</Button>
          </CardFooter>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Button 
            variant="ghost" 
            onClick={handleBackClick} 
            className="mb-4 text-blue-600 hover:text-blue-700 hover:bg-blue-50"
          >
            <ArrowLeft className="mr-2 h-4 w-4" /> Back to Computation
          </Button>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                Your Submission
              </h1>
              <p className="text-gray-600 mt-1">
                Data submitted for computation {id?.slice(0, 8)}...
              </p>
            </div>
            
            <div className="flex items-center gap-2">
              <Shield className="w-5 h-5 text-green-500" />
              <Badge variant="outline" className="bg-green-50 text-green-700 border-green-200">
                {submission.encryption_type || 'standard'} encryption
              </Badge>
            </div>
          </div>
        </div>

        {/* Submission Status Card */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <FileText className="w-4 h-4 text-blue-600" />
            </div>
            <h2 className="text-xl font-semibold text-gray-900">Submission Details</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Hash className="w-4 h-4 text-blue-600" />
                <span className="text-sm font-medium text-blue-900">Data Points</span>
              </div>
              <p className="text-2xl font-bold text-blue-700">
                {submission.data?.length || submission.data_points_count || 'N/A'}
              </p>
            </div>
            
            <div className="bg-green-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Calendar className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-900">Submitted</span>
              </div>
              <p className="text-sm font-semibold text-green-700">
                {formatDate(submission.submitted_at)}
              </p>
            </div>
            
            <div className="bg-purple-50 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-2">
                <Shield className="w-4 h-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-900">Security</span>
              </div>
              <p className="text-sm font-semibold text-purple-700 capitalize">
                {submission.encryption_type || 'Standard'} Encryption
              </p>
            </div>
          </div>
        </div>

        {/* Data Preview Card */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                <Eye className="w-4 h-4 text-gray-600" />
              </div>
              <h2 className="text-xl font-semibold text-gray-900">Data Preview</h2>
            </div>
            
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={toggleShowData}>
                {showData ? (
                  <>
                    <EyeOff className="mr-2 h-4 w-4" /> Hide Data
                  </>
                ) : (
                  <>
                    <Eye className="mr-2 h-4 w-4" /> Show Data
                  </>
                )}
              </Button>
              <Button variant="outline" size="sm" onClick={downloadData}>
                <Download className="mr-2 h-4 w-4" /> Download
              </Button>
            </div>
          </div>
          
          {showData && submission.data && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border overflow-auto max-h-96">
              <pre className="text-sm text-gray-800 whitespace-pre-wrap">
                {JSON.stringify(submission.data, null, 2)}
              </pre>
            </div>
          )}
          
          {!showData && (
            <div className="mt-4 p-4 bg-gray-50 rounded-lg border">
              <p className="text-sm text-gray-600">
                {submission.data_preview || 
                 `Your submission contains ${submission.data?.length || submission.data_points_count || 0} data points`}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Click "Show Data" to view all submitted data points
              </p>
            </div>
          )}
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mt-8">
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleBackClick} className="flex-1 sm:flex-none">
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Computation
            </Button>
            <Button 
              variant="destructive" 
              onClick={handleDeleteSubmission} 
              disabled={deleting}
              className="flex-1 sm:flex-none"
            >
              {deleting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Deleting...
                </>
              ) : (
                'Delete Submission'
              )}
            </Button>
          </div>
          
          <div className="sm:ml-auto">
            <Button 
              onClick={() => router.push(`/secure-computations/${id}/submit`)}
              className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700"
            >
              <FileText className="mr-2 h-4 w-4" />
              Submit New Data
            </Button>
          </div>
        </div>

        {/* Security Notice */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-6">
          <div className="flex items-start gap-3">
            <Shield className="w-5 h-5 text-blue-600 mt-0.5" />
            <div>
              <h3 className="font-medium text-blue-900">Secure Data Handling</h3>
              <p className="text-sm text-blue-700 mt-1">
                Your data has been encrypted and securely stored. Only aggregated computation results 
                will be visible to other participants. Individual data points remain private.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}