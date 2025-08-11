import React, { useState, useEffect } from 'react';
import { AlertTriangle, Play, Plus, RefreshCw, Check, X, Clock } from 'lucide-react';
import { toast } from 'react-hot-toast';

const SecureComputationDashboard = ({ user }) => {
  const [computations, setComputations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showNewComputationModal, setShowNewComputationModal] = useState(false);
  const [metricValue, setMetricValue] = useState('');
  const [selectedMetric, setSelectedMetric] = useState({
    type: 'blood_pressure',
    value: null
  });

  const metricTypes = [
    { id: 'blood_pressure', label: 'Blood Pressure', unit: 'mmHg' },
    { id: 'blood_sugar', label: 'Blood Sugar', unit: 'mg/dL' },
    { id: 'heart_rate', label: 'Heart Rate', unit: 'bpm' }
  ];

  useEffect(() => {
    fetchComputations();
  }, []);

  const fetchComputations = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/secure-computations', {
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch computations');
      }

      const data = await response.json();
      setComputations(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const initializeComputation = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/secure-computations/initialize', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          metric_type: selectedMetric.type,
          participating_orgs: [user.id] // Initially just the creating org
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to initialize computation');
      }

      setShowNewComputationModal(false);
      await fetchComputations();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const submitMetric = async (computationId) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/secure-computations/${computationId}/submit`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          value: parseFloat(metricValue) 
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to submit metric');
      }

      setMetricValue('');
      await fetchComputations();
      toast.success('Metric submitted successfully');
    } catch (err) {
      setError(err.message);
      toast.error(err.message);
    } finally {
      setLoading(false);
    }
  };

  const computeResults = async (computationId) => {
    try {
      setLoading(true);
      const response = await fetch(`http://localhost:8000/secure-computations/${computationId}/compute`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${user.token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to compute results');
      }

      await fetchComputations();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'ready_for_computation':
        return 'bg-yellow-100 text-yellow-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <Check className="w-4 h-4" />;
      case 'ready_for_computation':
        return <Play className="w-4 h-4" />;
      case 'error':
        return <X className="w-4 h-4" />;
      default:
        return <Clock className="w-4 h-4" />;
    }
  };

  if (loading && computations.length === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-semibold text-gray-800">Secure Computations</h2>
        <button
          onClick={() => setShowNewComputationModal(true)}
          className="flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
        >
          <Plus className="w-5 h-5 mr-2" />
          New Computation
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-center">
            <AlertTriangle className="w-5 h-5 text-red-400 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 gap-6">
        {computations.map((computation) => (
          <div
            key={computation.computation_id}
            className="bg-white rounded-lg shadow-lg p-6"
          >
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-medium text-gray-900">
                  {metricTypes.find(m => m.id === computation.metric_type)?.label || computation.metric_type}
                </h3>
                <p className="text-sm text-gray-500">
                  ID: {computation.computation_id}
                </p>
              </div>
              <div className={`flex items-center px-3 py-1 rounded-full ${getStatusColor(computation.status)}`}>
                {getStatusIcon(computation.status)}
                <span className="ml-2">{computation.status}</span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div>
                <p className="text-sm text-gray-600">Participating Organizations</p>
                <p className="text-lg font-medium">
                  {computation.participating_orgs.length}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Submitted Data</p>
                <p className="text-lg font-medium">
                  {computation.submitted_orgs.length} / {computation.participating_orgs.length}
                </p>
              </div>
            </div>

            {!computation.submitted_orgs.includes(user.id) && (
              <div className="flex items-center gap-2 mb-4">
                <input
                  type="number"
                  placeholder={`Enter ${metricTypes.find(m => m.id === computation.metric_type)?.label || 'metric'} value`}
                  value={metricValue}
                  onChange={(e) => setMetricValue(e.target.value)}
                  className="flex-1 border border-gray-300 rounded-lg px-3 py-2"
                />
                <span className="text-gray-600">
                  {metricTypes.find(m => m.id === computation.metric_type)?.unit}
                </span>
                <button
                  onClick={() => submitMetric(computation.computation_id)}
                  className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors"
                >
                  Submit
                </button>
              </div>
            )}

            {computation.status === 'ready_for_computation' && (
              <button
                onClick={() => computeResults(computation.computation_id)}
                className="w-full flex items-center justify-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
              >
                <Play className="w-5 h-5 mr-2" />
                Compute Results
              </button>
            )}

            {computation.status === 'completed' && computation.result && (
              <div className="mt-4 p-4 bg-gray-50 rounded-lg">
                <h4 className="text-md font-medium mb-2">Results</h4>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600">Aggregate Value</p>
                    <p className="text-lg font-medium">
                      {computation.result.final_result.toFixed(2)} {metricTypes.find(m => m.id === computation.metric_type)?.unit}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Participants</p>
                    <p className="text-lg font-medium">
                      {computation.result.num_parties}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {showNewComputationModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-medium mb-4">New Secure Computation</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Metric Type
                </label>
                <select
                  value={selectedMetric.type}
                  onChange={(e) => setSelectedMetric({ type: e.target.value, value: null })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  {metricTypes.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex justify-end gap-2">
                <button
                  onClick={() => setShowNewComputationModal(false)}
                  className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={initializeComputation}
                  className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                >
                  Create
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SecureComputationDashboard; 