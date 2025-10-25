import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, AlertTriangle, RefreshCw, BarChart } from 'lucide-react';
import { secureComputationService } from '../services/secureComputationService';
import ErrorDisplay from './ErrorDisplay';
import SecureComputationChart from './SecureComputationChart';

const ComputationStatusPage = ({ computationId, user, onBack }) => {
  const [computation, setComputation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(null);
  const [exporting, setExporting] = useState(false);
  const [exportFormat, setExportFormat] = useState('csv');

  useEffect(() => {
    fetchComputationStatus();
    
    // Set up polling for status updates
    const interval = setInterval(() => {
      fetchComputationStatus(false); // Don't show loading indicator for polling
    }, 5000); // Poll every 5 seconds
    
    setRefreshInterval(interval);
    
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [computationId]);
  
  // Stop polling when computation is completed or failed
  useEffect(() => {
    if (computation && (computation.status === 'COMPLETED' || computation.status === 'FAILED')) {
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }
  }, [computation]);

  const fetchComputationStatus = async (showLoading = true) => {
    try {
      if (showLoading) {
        setLoading(true);
      }
      
      try {
        const data = await secureComputationService.getComputation(computationId, user.token);
        const normalized = normalizeComputation(data);
        setComputation(normalized);
        setError(null);
      } catch (err) {
        // Check if the error is due to authentication issues
        if (err.isAuthError || (err.message && (err.message.includes('authentication') || err.message.includes('expired')))) {
          // Try to refresh the token if available
          if (user.refreshToken) {
            try {
              const refreshed = await user.refreshToken();
              if (refreshed) {
                // Retry with new token
                const data = await secureComputationService.getComputation(computationId, user.token);
                const normalized = normalizeComputation(data);
                setComputation(normalized);
                setError(null);
                return;
              }
            } catch (refreshError) {
              console.error('Error refreshing token:', refreshError);
            }
          }
        }
        
        // If we get here, either token refresh failed or it was another type of error
        setError('Failed to fetch computation status: ' + (err.message || 'Unknown error'));
        console.error('Error fetching computation status:', err);
      }
    } finally {
      if (showLoading) {
        setLoading(false);
      }
    }
  };

  const normalizeComputation = (data) => {
    if (!data || typeof data !== 'object') return data;
    const statusMap = {
      initialized: 'PENDING_APPROVAL',
      processing: 'IN_PROGRESS',
      completed: 'COMPLETED',
      error: 'FAILED',
      waiting_for_data: 'IN_PROGRESS',
      waiting_for_threshold: 'IN_PROGRESS'
    };
    const backendStatus = (data.status || '').toLowerCase();
    const uiStatus = statusMap[backendStatus] || (data.status || 'UNKNOWN');
    return { ...data, status: uiStatus };
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'PENDING_APPROVAL':
        return 'text-yellow-500';
      case 'IN_PROGRESS':
        return 'text-blue-500';
      case 'COMPLETED':
        return 'text-green-500';
      case 'FAILED':
        return 'text-red-500';
      default:
        return 'text-gray-500';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'PENDING_APPROVAL':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'IN_PROGRESS':
        return <RefreshCw className="w-5 h-5 text-blue-500 animate-spin" />;
      case 'COMPLETED':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'FAILED':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <AlertTriangle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getParticipantStatusIcon = (status) => {
    switch (status) {
      case 'approved':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-red-500" />;
      case 'pending':
      default:
        return <Clock className="w-4 h-4 text-yellow-500" />;
    }
  };

  const renderParticipantStatus = () => {
    if (!computation || !computation.participants || computation.participants.length === 0) {
      return (
        <div className="mt-6 bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
          <p className="text-gray-500">No participants have joined this computation yet.</p>
        </div>
      );
    }

    return (
      <div className="mt-6">
        <div className="flex items-center mb-4">
          <h3 className="text-xl font-semibold text-gray-800">Participant Organizations</h3>
          <div className="ml-3 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
            {computation.participants.length} {computation.participants.length === 1 ? 'Organization' : 'Organizations'}
          </div>
        </div>
        <div className="bg-white rounded-lg shadow-md border border-gray-100 overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Organization</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Joined At</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {computation.participants.map((participant) => (
                <tr key={participant.org_id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{participant.org_name || `Organization ${participant.org_id}`}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      {getParticipantStatusIcon(participant.status)}
                      <span className={`ml-2 text-sm font-medium px-2.5 py-0.5 rounded-full ${participant.status === 'approved' ? 'bg-green-100 text-green-800' : participant.status === 'rejected' ? 'bg-red-100 text-red-800' : 'bg-yellow-100 text-yellow-800'}`}>
                        {participant.status.charAt(0).toUpperCase() + participant.status.slice(1)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {participant.joined_at ? new Date(participant.joined_at).toLocaleString() : 'Not joined yet'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    );
  };

  const renderComputationResult = () => {
    if (!computation || computation.status !== 'COMPLETED' || !computation.result) {
      return null;
    }

    const result = computation.result || {};
    const aggregateValue =
      result.mean ?? result.sum ?? result.aggregate_value ?? null;
    const participantCount =
      result.organizations_count ?? computation.participants_count ?? result.participant_count ?? null;
    const dataPointCount = result.data_points_count ?? result.count ?? null;
    const functionLabel = computation.function_type || computation.function || computation.type || 'Result';

    return (
      <div className="mt-8 bg-white rounded-lg shadow-md border border-gray-100 p-6">
        <h3 className="text-xl font-semibold text-gray-800 mb-5 flex items-center">
          <BarChart className="w-6 h-6 mr-2 text-blue-500" />
          Computation Results
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-blue-50 p-5 rounded-lg border border-blue-100 shadow-sm">
            <p className="text-sm text-blue-700 font-medium mb-1">Aggregate Value</p>
            <p className="text-3xl font-bold text-gray-800">{aggregateValue !== null ? aggregateValue : '—'}</p>
            <p className="text-xs text-blue-600 mt-2">{functionLabel} calculation</p>
          </div>
          
          <div className="bg-green-50 p-5 rounded-lg border border-green-100 shadow-sm">
            <p className="text-sm text-green-700 font-medium mb-1">Participants</p>
            <p className="text-3xl font-bold text-gray-800">{participantCount !== null ? participantCount : '—'}</p>
            <p className="text-xs text-green-600 mt-2">Contributing organizations</p>
          </div>
          
          <div className="bg-purple-50 p-5 rounded-lg border border-purple-100 shadow-sm">
            <p className="text-sm text-purple-700 font-medium mb-1">Data Points</p>
            <p className="text-3xl font-bold text-gray-800">{dataPointCount !== null ? dataPointCount : '—'}</p>
            <p className="text-xs text-purple-600 mt-2">Total records analyzed</p>
          </div>
        </div>
        
        <div className="mt-6 h-80 border border-gray-200 rounded-lg p-4 bg-gray-50">
          <SecureComputationChart 
            computation={computation}
            data={result.chart_data}
            type={functionLabel}
            metricTypes={[
              { id: 'average', label: 'Average', unit: '' },
              { id: 'sum', label: 'Sum', unit: '' },
              { id: 'count', label: 'Count', unit: '' },
              { id: 'min', label: 'Minimum', unit: '' },
              { id: 'max', label: 'Maximum', unit: '' }
            ]}
          />
        </div>
        
        <div className="mt-6 flex justify-end">
          <button
            onClick={handleExport}
            disabled={exporting}
            className={`px-4 py-2 ${exporting ? 'bg-blue-200 text-blue-600' : 'bg-blue-100 text-blue-700 hover:bg-blue-200'} rounded-md transition-colors font-medium flex items-center`}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            {exporting ? 'Exporting…' : 'Export Results'}
          </button>
        </div>
      </div>
    );
  };

  const handleExport = async () => {
    try {
      setExporting(true);
      const { blob, filename } = await secureComputationService.exportResults(
        computationId,
        { format: exportFormat },
        user.token
      );
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('Export failed', e);
      setError('Failed to export results: ' + (e.message || 'Unknown error'));
    } finally {
      setExporting(false);
    }
  };

  if (loading && !computation) {
    return (
      <div className="p-8 bg-white rounded-lg shadow-md border border-gray-100">
        <div className="flex flex-col justify-center items-center h-64">
          <div className="bg-blue-50 rounded-full p-4 mb-4">
            <RefreshCw className="w-10 h-10 text-blue-500 animate-spin" />
          </div>
          <h3 className="text-xl font-medium text-gray-800 mb-2">Loading Computation</h3>
          <p className="text-gray-500">Please wait while we fetch the latest computation data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 bg-white rounded-lg shadow-md border border-gray-100">
        <div className="text-center">
          <div className="bg-red-50 rounded-full p-4 w-20 h-20 flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-10 h-10 text-red-500" />
          </div>
          <h3 className="text-xl font-medium text-gray-900 mb-3">Error Loading Computation</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">{error}</p>
          <button
            onClick={fetchComputationStatus}
            className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!computation) {
    return (
      <div className="p-8 bg-white rounded-lg shadow-md border border-gray-100">
        <div className="text-center">
          <div className="bg-yellow-50 rounded-full p-4 w-20 h-20 flex items-center justify-center mx-auto mb-4">
            <AlertTriangle className="w-10 h-10 text-yellow-500" />
          </div>
          <h3 className="text-xl font-medium text-gray-900 mb-3">Computation Not Found</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">The requested computation could not be found or may have been deleted.</p>
          <button
            onClick={onBack}
            className="px-6 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors font-medium"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md border border-gray-100 overflow-hidden">
      <div className="p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">{computation.title || 'Secure Computation'}</h2>
            <p className="text-gray-600 mt-2">{computation.description || 'No description provided'}</p>
            <div className="flex items-center mt-3 bg-gray-50 px-3 py-2 rounded-md inline-block">
              <div className="flex items-center">
                {getStatusIcon(computation.status)}
                <span className={`ml-2 font-medium ${getStatusColor(computation.status)}`}>
                  {computation.status.replace('_', ' ')}
                </span>
              </div>
            </div>
          </div>
          
          <div className="flex space-x-3">
            <button
              onClick={() => fetchComputationStatus()}
              className="p-2 text-blue-500 hover:text-blue-700 hover:bg-blue-50 rounded-full transition-colors"
              title="Refresh Status"
            >
              <RefreshCw className="w-5 h-5" />
            </button>
            <button
              onClick={onBack}
              className="px-4 py-2 bg-gray-100 rounded-md text-gray-700 hover:bg-gray-200 transition-colors font-medium"
            >
              Back to List
            </button>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-blue-50 p-5 rounded-lg border border-blue-100">
            <p className="text-sm text-blue-700 font-medium mb-1">Computation ID</p>
            <p className="text-md font-mono text-gray-800 break-all">{computation.computation_id}</p>
          </div>
          
          <div className="bg-green-50 p-5 rounded-lg border border-green-100">
            <p className="text-sm text-green-700 font-medium mb-1">Function Type</p>
            <p className="text-md font-medium text-gray-800">{computation.function_type || computation.function || computation.type || 'Not specified'}</p>
          </div>
          
          <div className="bg-purple-50 p-5 rounded-lg border border-purple-100">
            <p className="text-sm text-purple-700 font-medium mb-1">Created At</p>
            <p className="text-md text-gray-800">{computation.created_at ? new Date(computation.created_at).toLocaleString() : 'Unknown'}</p>
          </div>
        </div>
        
        {renderParticipantStatus()}
        {renderComputationResult()}
        
        {computation.status === 'FAILED' && computation.error_message && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="text-lg font-medium text-red-800 mb-2 flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Computation Failed
            </h3>
            <p className="text-red-700">{computation.error_message}</p>
            {computation.error_code && (
              <p className="text-sm text-red-600 mt-1">Error code: {computation.error_code}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ComputationStatusPage;