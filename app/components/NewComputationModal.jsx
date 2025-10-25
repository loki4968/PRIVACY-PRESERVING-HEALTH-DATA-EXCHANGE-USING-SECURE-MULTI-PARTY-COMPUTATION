'use client';

import { useState, useEffect } from 'react';
import { X, Check, AlertCircle } from 'lucide-react';
import { toast } from 'react-hot-toast';
import { secureComputationService } from '../services/secureComputationService';

const NewComputationModal = ({ isOpen, onClose, user, onSuccess }) => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [computationType, setComputationType] = useState('health_statistics');
  const [securityMethod, setSecurityMethod] = useState('standard');
  const [availableOrganizations, setAvailableOrganizations] = useState([]);
  const [selectedOrganizations, setSelectedOrganizations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingOrgs, setLoadingOrgs] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchAvailableOrganizations();
    }
  }, [isOpen]);

  const fetchAvailableOrganizations = async () => {
    try {
      setLoadingOrgs(true);
      const token = user?.token || localStorage.getItem('token');
      if (!token) {
        setError('Authentication required');
        return;
      }

      const response = await secureComputationService.getAvailableOrganizations(token);
      setAvailableOrganizations(response.organizations || []);
    } catch (error) {
      console.error('Error fetching organizations:', error);
      setError('Failed to fetch available organizations');
    } finally {
      setLoadingOrgs(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const token = user?.token || localStorage.getItem('token');
      if (!token) {
        setError('Authentication required');
        return;
      }

      const params = {
        title,
        description,
        computation_type: computationType,
        security_method: securityMethod,
        target_organizations: selectedOrganizations.length > 0 ? selectedOrganizations : undefined,
        participating_orgs: selectedOrganizations.length === 0 ? [String(user.id)] : undefined
      };

      const response = await secureComputationService.initializeComputation(params, token);

      if (response.success || response.computation_id) {
        toast.success(selectedOrganizations.length > 0 
          ? 'Computation request sent successfully!' 
          : 'Computation initialized successfully!');
        onSuccess();
        onClose();
      } else {
        setError(response.error || 'Failed to initialize computation');
      }
    } catch (error) {
      console.error('Error initializing computation:', error);
      setError('Failed to initialize computation');
    } finally {
      setLoading(false);
    }
  };

  const toggleOrganization = (orgId) => {
    setSelectedOrganizations(prev => {
      if (prev.includes(orgId)) {
        return prev.filter(id => id !== orgId);
      } else {
        return [...prev, orgId];
      }
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] flex flex-col">
        <div className="p-4 border-b border-gray-200 flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-700">Create New Secure Computation</h1>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 focus:outline-none transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <div className="p-6 overflow-y-auto">
          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-start">
              <AlertCircle className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="space-y-6">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                  Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter computation title"
                  required
                />
              </div>

              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  id="description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter computation description"
                  rows="3"
                  required
                ></textarea>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="computationType" className="block text-sm font-medium text-gray-700 mb-1">
                    Computation Type
                  </label>
                  <select
                    id="computationType"
                    value={computationType}
                    onChange={(e) => setComputationType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="health_statistics">Health Statistics</option>
                    <option value="federated_learning">Federated Learning</option>
                    <option value="secure_aggregation">Secure Aggregation</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="securityMethod" className="block text-sm font-medium text-gray-700 mb-1">
                    Security Method
                  </label>
                  <select
                    id="securityMethod"
                    value={securityMethod}
                    onChange={(e) => setSecurityMethod(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    required
                  >
                    <option value="standard">Standard</option>
                    <option value="homomorphic">Homomorphic Encryption</option>
                    <option value="hybrid">Hybrid (MPC + Homomorphic)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Target Organizations
                </label>
                {loadingOrgs ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
                  </div>
                ) : availableOrganizations.length === 0 ? (
                  <div className="text-center py-4 bg-gray-50 rounded-md">
                    <p className="text-gray-500">No other organizations available</p>
                  </div>
                ) : (
                  <div className="max-h-60 overflow-y-auto border border-gray-200 rounded-md">
                    {availableOrganizations.map((org) => (
                      <div 
                        key={org.id}
                        className={`flex items-center justify-between px-4 py-3 border-b border-gray-100 hover:bg-gray-50 cursor-pointer ${selectedOrganizations.includes(org.id) ? 'bg-blue-50' : ''}`}
                        onClick={() => toggleOrganization(org.id)}
                      >
                        <div>
                          <h3 className="font-medium text-gray-900">{org.name}</h3>
                          <p className="text-sm text-gray-500">{org.type}</p>
                        </div>
                        <div className={`w-6 h-6 rounded-full border ${selectedOrganizations.includes(org.id) ? 'bg-blue-500 border-blue-500' : 'border-gray-300'} flex items-center justify-center`}>
                          {selectedOrganizations.includes(org.id) && <Check className="w-4 h-4 text-white" />}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
                <p className="mt-2 text-sm text-gray-500">
                  {selectedOrganizations.length === 0 
                    ? "If no organizations are selected, the computation will be created for your organization only." 
                    : `${selectedOrganizations.length} organization(s) selected`}
                </p>
              </div>
            </div>

            <div className="mt-8 flex justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                disabled={loading}
              >
                {loading ? (
                  <span className="flex items-center">
                    <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></span>
                    Processing...
                  </span>
                ) : (
                  'Create Computation'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default NewComputationModal;