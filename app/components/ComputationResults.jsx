import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'react-hot-toast';

const ComputationResults = ({ computationId }) => {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [exportFormat, setExportFormat] = useState('json');
  const [isExporting, setIsExporting] = useState(false);
  const { user } = useAuth();
  const token = user?.token;

  useEffect(() => {
    if (computationId) {
      fetchResult();
    }
  }, [computationId]);

  const fetchResult = async () => {
    if (!token) {
      toast.error('Authentication required. Please log in.');
      setIsLoading(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${computationId}/result`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch computation result');
      }

      const data = await response.json();
      
      // Debug: Log the actual response data
      console.log('Computation result data:', data);
      console.log('Status:', data.status);
      console.log('Participants:', data.participants);
      console.log('Submissions:', data.submissions);
      
      // Check if computation is still in progress or has error
      if (data.status && data.status !== 'completed') {
        if (data.status === 'error') {
          toast.error(`Computation error: ${data.error_message || 'Unknown error'}`);
        } else if (data.status === 'ready_to_compute') {
          toast.success('All data submitted! Ready to compute results.');
        } else {
          toast(`Computation status: ${data.status_message || data.status}`);
          // If still processing, set up polling
          if (data.status === 'processing' || data.status === 'initialized' || data.status === 'waiting_for_data') {
            setTimeout(fetchResult, 5000); // Poll every 5 seconds
          }
        }
      }
      
      setResult(data);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (format) => {
    if (!token) {
      toast.error('Authentication required. Please log in.');
      return;
    }

    setIsExporting(true);
    try {
      // Use the export endpoint
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${computationId}/export?format=${format}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`Failed to export computation result: ${response.statusText}`);
      }

      // Get the filename from the Content-Disposition header if available
      const contentDisposition = response.headers.get('Content-Disposition');
      let filename = `computation_${computationId}.${format}`;
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename=([^;]+)/);
        if (filenameMatch && filenameMatch[1]) {
          filename = filenameMatch[1].replace(/"/g, '');
        }
      }

      // Create a blob from the response
      const blob = await response.blob();
      
      // Create a download link and trigger the download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success(`Exported computation result as ${format.toUpperCase()}`);
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsExporting(false);
    }
  };



  const renderStatisticsCards = () => {
    if (!result || (!result.mean && !result.sum && !result.count && !result.variance)) {
      return <div className="text-center py-10 text-gray-500">No statistical data available</div>;
    }

    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {result.mean && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <p className="text-sm font-medium text-blue-900">Average</p>
            <p className="text-2xl font-bold text-blue-700">{Number(result.mean).toFixed(2)}</p>
          </div>
        )}
        {result.sum && (
          <div className="bg-green-50 p-4 rounded-lg">
            <p className="text-sm font-medium text-green-900">Sum</p>
            <p className="text-2xl font-bold text-green-700">{Number(result.sum).toFixed(2)}</p>
          </div>
        )}
        {result.count && (
          <div className="bg-purple-50 p-4 rounded-lg">
            <p className="text-sm font-medium text-purple-900">Count</p>
            <p className="text-2xl font-bold text-purple-700">{result.count}</p>
          </div>
        )}
        {result.variance && (
          <div className="bg-orange-50 p-4 rounded-lg">
            <p className="text-sm font-medium text-orange-900">Variance</p>
            <p className="text-2xl font-bold text-orange-700">{Number(result.variance).toFixed(2)}</p>
          </div>
        )}
      </div>
    );
  };


  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="text-center text-gray-500 py-8">
        No results available
      </div>
    );
  }

  return (
    <div className="bg-white shadow sm:rounded-lg p-6">
      <div className="mb-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Computation Results
        </h3>
        
        <div className="flex justify-between items-center mb-4">
          <div className="flex flex-wrap gap-2 mb-2">
            <button
              onClick={() => handleExport('json')}
              disabled={isExporting}
              className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {isExporting ? 'Exporting...' : 'Export JSON'}
            </button>
            <button
              onClick={() => handleExport('csv')}
              disabled={isExporting}
              className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {isExporting ? 'Exporting...' : 'Export CSV'}
            </button>
          </div>
        </div>

        <div className="space-y-6">
          {/* Statistics Cards */}
          {renderStatisticsCards()}
          
          {/* Raw Results */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Raw Results</h3>
            <pre className="text-sm text-gray-800 whitespace-pre-wrap">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        </div>
      </div>

      <div className="mt-8">
        <h4 className="text-md font-medium text-gray-900 mb-4">
          Computation Details
        </h4>
        <div className="bg-gray-50 rounded-lg p-4">
          <dl className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Type</dt>
              <dd className="mt-1 text-sm text-gray-900">{result.type}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Status</dt>
              <dd className="mt-1 text-sm text-gray-900">{result.status}</dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Created At</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {new Date(result.created_at).toLocaleString()}
              </dd>
            </div>
            <div>
              <dt className="text-sm font-medium text-gray-500">Completed At</dt>
              <dd className="mt-1 text-sm text-gray-900">
                {result.completed_at ? new Date(result.completed_at).toLocaleString() : 'Pending'}
              </dd>
            </div>
          </dl>
        </div>
      </div>
    </div>
  );
};

export default ComputationResults;