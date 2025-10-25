'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Plus, BarChart } from 'lucide-react';
import ErrorDisplay from '../components/ErrorDisplay';
import { useAuth } from '../context/AuthContext';
import SecureComputationWizard from '../components/SecureComputationWizard';
import ComputationStatusPage from '../components/ComputationStatusPage';
import { secureComputationService } from '../services/secureComputationService';

const HealthDataAnalysisPage = () => {
  const router = useRouter();
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysisData, setAnalysisData] = useState(null);
  const [computations, setComputations] = useState([]);
  const [showWizard, setShowWizard] = useState(false);
  const [selectedComputationId, setSelectedComputationId] = useState(null);

  useEffect(() => {
    // Check if user is authenticated
    if (!user) {
      router.push('/login');
      return;
    }

    // Fetch analysis data and secure computations
    const fetchData = async () => {
      try {
        setLoading(true);
        
        // Fetch secure computations
        try {
          const computationsData = await secureComputationService.listComputations(user.token);
          setComputations(computationsData);
        } catch (compError) {
          console.error('Error fetching computations:', compError);
          // Don't set the main error state, just log it
        }
        
        // Fetch analysis data
        try {
          // Simulate API call
          // In a real implementation, this would be an actual API call
          // const response = await fetch('/api/analysis');
          // const data = await response.json();
          
          // For now, we'll simulate an error for the analysis data
          // but we'll still show the secure computations section
          throw new Error('No analysis results available');
          
          // setAnalysisData(data);
        } catch (analysisError) {
          setError(analysisError.message || 'Failed to load analysis data');
        }
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user, router]);
  
  const handleCreateComputation = () => {
    setShowWizard(true);
  };
  
  const handleCloseWizard = () => {
    setShowWizard(false);
  };
  
  const handleComputationCreated = (newComputation) => {
    setComputations(prev => [newComputation, ...prev]);
    setSelectedComputationId(newComputation.computation_id);
  };
  
  const handleViewComputation = (computationId) => {
    setSelectedComputationId(computationId);
  };
  
  const handleBackFromStatus = () => {
    setSelectedComputationId(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // If a computation is selected, show its status page
  if (selectedComputationId) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-6">Secure Computation Status</h1>
        <ComputationStatusPage 
          computationId={selectedComputationId} 
          user={user} 
          onBack={handleBackFromStatus} 
        />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Secure Computations</h1>
        <button
          onClick={handleCreateComputation}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 flex items-center"
        >
          <Plus size={16} className="mr-2" />
          Start New Computation
        </button>
      </div>
      
      {/* Tabs for filtering computations */}
      <div className="mb-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              className="border-blue-500 text-blue-600 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
              onClick={() => {}}
            >
              All Computations
            </button>
            <button
              className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
              onClick={() => {}}
            >
              Completed
            </button>
            <button
              className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
              onClick={() => {}}
            >
              In Progress
            </button>
            <button
              className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm"
              onClick={() => {}}
            >
              Pending
            </button>
          </nav>
        </div>
      </div>
      
      {/* Secure Computations List */}
      <div className="mb-8">
        {computations.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {computations.map(computation => (
              <div 
                key={computation.computation_id} 
                className="bg-white rounded-lg shadow-md p-5 hover:shadow-lg transition-shadow cursor-pointer border border-gray-100"
                onClick={() => handleViewComputation(computation.computation_id)}
              >
                <div className="flex justify-between items-start mb-3">
                  <h3 className="font-medium text-gray-900 truncate text-lg">
                    {computation.title || 'Untitled Computation'}
                  </h3>
                  <span className={`text-xs px-2 py-1 rounded-full ${computation.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : computation.status === 'FAILED' ? 'bg-red-100 text-red-800' : computation.status === 'IN_PROGRESS' ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'}`}>
                    {computation.status.replace('_', ' ')}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mb-4 h-12 overflow-hidden">
                  {computation.description || 'No description provided'}
                </p>
                <div className="flex flex-col space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Function:</span>
                    <span className="font-medium">{computation.function_type || 'Average'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Created:</span>
                    <span className="font-medium">{new Date(computation.created_at).toLocaleDateString()}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">ID:</span>
                    <span className="font-medium">{computation.computation_id.substring(0, 8)}...</span>
                  </div>
                </div>
                <button
                  className="mt-4 w-full py-2 bg-gray-100 text-gray-800 rounded hover:bg-gray-200 transition-colors text-sm font-medium"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleViewComputation(computation.computation_id);
                  }}
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-md p-8 text-center border border-gray-100">
            <div className="bg-blue-50 rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-6">
              <BarChart className="w-10 h-10 text-blue-500" />
            </div>
            <h3 className="text-xl font-medium text-gray-900 mb-3">No Secure Computations Yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">Start a new secure computation to analyze health data across institutions while preserving privacy and compliance.</p>
            <button
              onClick={handleCreateComputation}
              className="px-6 py-3 bg-blue-500 text-white rounded-md hover:bg-blue-600 transition-colors font-medium"
            >
              Start Your First Computation
            </button>
          </div>
        )}
      </div>
      
      {/* Analysis Results Section */}
      {error ? (
        <div className="mt-8">
          <ErrorDisplay 
            title="Error Loading Analysis"
            message={error}
            primaryAction={{
              label: 'Return to Dashboard',
              onClick: () => router.push('/dashboard')
            }}
            secondaryAction={{
              label: 'Upload New File',
              onClick: () => router.push('/upload')
            }}
          />
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Analysis Results</h2>
          <pre>{JSON.stringify(analysisData, null, 2)}</pre>
        </div>
      )}
      
      {/* Secure Computation Wizard Modal */}
      {showWizard && (
        <SecureComputationWizard 
          user={user} 
          onClose={handleCloseWizard} 
          onComputationCreated={handleComputationCreated} 
        />
      )}
    </div>
  );
};

export default HealthDataAnalysisPage;