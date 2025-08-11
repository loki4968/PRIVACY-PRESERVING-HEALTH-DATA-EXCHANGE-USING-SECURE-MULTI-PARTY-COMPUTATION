import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import ComputationResults from './ComputationResults';

const SecureComputation = () => {
  const [computations, setComputations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedComputation, setSelectedComputation] = useState(null);
  const [newComputation, setNewComputation] = useState({
    computation_type: '',
    data_points: []
  });
  const { token } = useAuth();

  useEffect(() => {
    fetchComputations();
  }, []);

  const fetchComputations = async () => {
    try {
      const response = await fetch('http://localhost:8000/secure-computations', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch computations');
      }

      const data = await response.json();
      setComputations(data);
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleInitiateComputation = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/secure-computation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newComputation)
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to initiate computation');
      }

      toast.success('Computation initiated successfully');
      setNewComputation({
        computation_type: '',
        data_points: []
      });
      fetchComputations();
    } catch (error) {
      toast.error(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddDataPoint = () => {
    setNewComputation(prev => ({
      ...prev,
      data_points: [...prev.data_points, { value: 0, type: 'numeric' }]
    }));
  };

  const handleDataPointChange = (index, field, value) => {
    setNewComputation(prev => ({
      ...prev,
      data_points: prev.data_points.map((point, i) => 
        i === index ? { ...point, [field]: value } : point
      )
    }));
  };

  const handleRemoveDataPoint = (index) => {
    setNewComputation(prev => ({
      ...prev,
      data_points: prev.data_points.filter((_, i) => i !== index)
    }));
  };

  const handleViewResults = (computationId) => {
    setSelectedComputation(computationId);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">
              Secure Computations
            </h2>

            {/* New Computation Form */}
            <form onSubmit={handleInitiateComputation} className="space-y-6 mb-8">
              <div>
                <label htmlFor="computation_type" className="block text-sm font-medium text-gray-700">
                  Computation Type
                </label>
                <select
                  id="computation_type"
                  name="computation_type"
                  required
                  value={newComputation.computation_type}
                  onChange={(e) => setNewComputation(prev => ({
                    ...prev,
                    computation_type: e.target.value
                  }))}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                >
                  <option value="">Select a type</option>
                  <option value="statistics">Statistical Analysis</option>
                  <option value="aggregation">Data Aggregation</option>
                  <option value="comparison">Data Comparison</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Data Points
                </label>
                {newComputation.data_points.map((point, index) => (
                  <div key={index} className="flex items-center space-x-4 mb-2">
                    <input
                      type="number"
                      value={point.value}
                      onChange={(e) => handleDataPointChange(index, 'value', parseFloat(e.target.value))}
                      className="block w-32 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Value"
                    />
                    <select
                      value={point.type}
                      onChange={(e) => handleDataPointChange(index, 'type', e.target.value)}
                      className="block w-32 border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    >
                      <option value="numeric">Numeric</option>
                      <option value="categorical">Categorical</option>
                    </select>
                    <button
                      type="button"
                      onClick={() => handleRemoveDataPoint(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      Remove
                    </button>
                  </div>
                ))}
                <button
                  type="button"
                  onClick={handleAddDataPoint}
                  className="mt-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Add Data Point
                </button>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
              >
                {isLoading ? 'Initiating...' : 'Initiate Computation'}
              </button>
            </form>

            {/* Computations List */}
            <div className="mt-8">
              <h3 className="text-lg font-medium text-gray-900 mb-4">
                Recent Computations
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        ID
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Status
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Created At
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {computations.map((computation) => (
                      <tr key={computation.computation_id}>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                          {computation.computation_id}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {computation.type}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            computation.status === 'completed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {computation.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          {new Date(computation.created_at).toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                          <button
                            onClick={() => handleViewResults(computation.computation_id)}
                            className="text-indigo-600 hover:text-indigo-900"
                          >
                            View Results
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Results Visualization */}
            {selectedComputation && (
              <div className="mt-8">
                <ComputationResults computationId={selectedComputation} />
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default SecureComputation; 