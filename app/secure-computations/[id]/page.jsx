'use client';

import React, { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'react-hot-toast';
import ComputationResults from '../../components/ComputationResults';
import { 
  Clock, 
  Users, 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertCircle, 
  Upload,
  Download,
  Eye,
  UserPlus,
  Trash2,
  Activity,
  ArrowLeft,
  Lock,
  BarChart3,
  ChevronUp,
  ChevronDown,
  X
} from 'lucide-react';
import Link from 'next/link';
import { secureComputationService } from '../../services/secureComputationService';

export default function ComputationDetailsPage() {
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
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [showAddParticipants, setShowAddParticipants] = useState(false);
  const [availableOrgs, setAvailableOrgs] = useState([]);
  const [selectedNewParticipants, setSelectedNewParticipants] = useState([]);
  const [inviting, setInviting] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [computing, setComputing] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }
    fetchComputationDetails();
  }, [id, user]);

  useEffect(() => {
    if (showAddParticipants) {
      fetchAvailableOrganizations();
    }
  }, [showAddParticipants, participants]);

  const fetchComputationDetails = async () => {
    try {
      setLoading(true);
      const token = user?.token || localStorage.getItem('token');
      let computationData = null;
      
      // Fetch computation details
      try {
        computationData = await secureComputationService.getComputationDetails(id, token);
        console.log('Computation data:', computationData);
        console.log('Status:', computationData.status);
        console.log('Submissions count:', computationData.submissions_count);
        setComputation(computationData);
      } catch (err) {
        console.error('Error fetching computation details from service:', err);
        // Fallback to direct fetch if service method fails
        const computationResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });

        if (!computationResponse.ok) {
          const errorText = await computationResponse.text();
          console.error('API error response:', errorText);
          throw new Error(`Failed to fetch computation details: ${computationResponse.status} ${errorText}`);
        }

        computationData = await computationResponse.json();
        console.log('Computation data (fallback):', computationData);
        setComputation(computationData);
      }

      // Fetch participants
      try {
        const participantsData = await secureComputationService.getActiveParticipants(id, token);
        setParticipants(participantsData.participants || []);
      } catch (err) {
        console.warn('Failed to fetch participants:', err);
        setParticipants([]);
      }

      // Fetch result if computation is completed
      if (computationData && computationData.status === 'completed') {
        try {
          const resultData = await secureComputationService.getComputationResult(id, token);
          setResult(resultData);
        } catch (err) {
          console.warn('Failed to fetch result:', err);
        }
      }

    } catch (err) {
      console.error('Error fetching computation details:', err);
      setError(err.message);
      toast.error('Failed to load computation details');
    } finally {
      setLoading(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'in_progress':
        return <Activity className="w-5 h-5 text-blue-500" />;
      case 'waiting_for_participants':
        return <Users className="w-5 h-5 text-yellow-500" />;
      case 'waiting_for_data':
        return <Clock className="w-5 h-5 text-orange-500" />;
      default:
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'in_progress':
        return 'bg-blue-100 text-blue-800';
      case 'waiting_for_participants':
        return 'bg-yellow-100 text-yellow-800';
      case 'waiting_for_data':
        return 'bg-orange-100 text-orange-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleExport = async () => {
    try {
      const token = user?.token || localStorage.getItem('token');
      await secureComputationService.exportResults(id, 'json', token);
      toast.success('Results exported successfully');
    } catch (err) {
      console.error('Export failed:', err);
      toast.error('Failed to export results');
    }
  };

  const fetchAvailableOrganizations = async () => {
    try {
      const token = user?.token || localStorage.getItem('token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/organizations`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch organizations');
      
      const orgs = await response.json();
      
      // Filter out organizations that are already participants
      const participantOrgIds = participants.map(p => p.org_id || p.id);
      console.log('All orgs:', orgs);
      console.log('Participant org IDs:', participantOrgIds);
      console.log('Current user ID:', user.id);
      
      const available = orgs.filter(org => 
        !participantOrgIds.includes(org.id) && 
        org.id !== user.id && 
        org.role !== 'PATIENT'
      );
      
      console.log('Available orgs after filtering:', available);
      
      setAvailableOrgs(available);
    } catch (err) {
      console.error('Error fetching organizations:', err);
      toast.error('Failed to load available organizations');
    }
  };

  const handleAddParticipants = async () => {
    if (selectedNewParticipants.length === 0) {
      toast.error('Please select at least one participant');
      return;
    }

    try {
      setInviting(true);
      const token = user?.token || localStorage.getItem('token');
      
      for (const orgId of selectedNewParticipants) {
        await secureComputationService.inviteParticipant(id, orgId, token);
      }
      
      toast.success(`Invited ${selectedNewParticipants.length} new participant(s)`);
      setShowAddParticipants(false);
      setSelectedNewParticipants([]);
      
      // Refresh computation details
      await fetchComputationDetails();
    } catch (err) {
      console.error('Error inviting participants:', err);
      toast.error('Failed to invite participants');
    } finally {
      setInviting(false);
    }
  };

  const handleParticipantSelection = (orgId) => {
    setSelectedNewParticipants(prev => 
      prev.includes(orgId) 
        ? prev.filter(id => id !== orgId)
        : [...prev, orgId]
    );
  };

  const handleComputeResults = async () => {
    try {
      setComputing(true);
      const token = user?.token || localStorage.getItem('token');
      
      console.log('Starting computation for ID:', id);
      console.log('Using token:', token ? 'Present' : 'Missing');
      
      // First trigger the computation
      const computeResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}/compute`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (!computeResponse.ok) {
        const errorData = await computeResponse.json();
        console.error('Compute endpoint error:', errorData);
        console.error('Response status:', computeResponse.status);
        console.error('Response headers:', computeResponse.headers);
        throw new Error(errorData.detail || `Failed to compute results (${computeResponse.status})`);
      }

      // Now fetch the results
      const resultResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/secure-computations/computations/${id}/result`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (resultResponse.ok) {
        const resultData = await resultResponse.json();
        setResult(resultData);
        setShowResults(true); // Automatically show results
      }

      toast.success('Computation completed successfully!');
      await fetchComputationDetails(); // Refresh computation status
    } catch (err) {
      console.error('Error computing results:', err);
      toast.error(err.message || 'Failed to compute results');
    } finally {
      setComputing(false);
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
      <div className="max-w-6xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/secure-computations"
            className="inline-flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-4"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Dashboard
          </Link>
          
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Computation {computation.computation_id.slice(0, 8)}...
              </h1>
              <p className="text-gray-600 mt-1">
                {computation.type || 'Secure Computation'}
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              {getStatusIcon(computation.status)}
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(computation.status)}`}>
                {computation.status?.replace('_', ' ').toUpperCase()}
              </span>
              
              {/* Debug Info */}
              <div className="text-xs text-gray-500">
                Status: {computation.status} | Submissions: {computation.submissions_count} | Participants: {participants.length}
              </div>
              
              {/* Action Buttons */}
              <div className="flex items-center gap-3">
                {/* Submit Data Button */}
                {computation.status === 'waiting_for_data' && (
                  <Link
                    href={`/secure-computations/${id}/submit`}
                    className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Upload className="w-4 h-4" />
                    Submit Data
                  </Link>
                )}
                
                {/* View Submitted Data Button */}
                {computation.status !== 'pending' && (
                  <Link
                    href={`/secure-computations/${id}/view-submission`}
                    className="flex items-center gap-2 bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    View My Submission
                  </Link>
                )}
                
                {/* Compute Results Button */}
                {(computation.status === 'waiting_for_data' || computation.status === 'ready_to_compute' || computation.status === 'error') && (computation.submissions_count >= 2 || participants.length >= 2) && (
                  <button
                    onClick={handleComputeResults}
                    disabled={computing}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {computing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Computing...
                      </>
                    ) : (
                      <>
                        <Activity className="w-4 h-4" />
                        Compute Results
                      </>
                    )}
                  </button>
                )}
                
                {/* View Results Button */}
                {(computation.status === 'completed' || computation.status === 'ready_to_compute') && (
                  <Link
                    href={`/secure-computations/${id}/results`}
                    className="flex items-center gap-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
                  >
                    <Eye className="w-4 h-4" />
                    View Results
                  </Link>
                )}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Computation Info */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Shield className="w-5 h-5" />
                Computation Details
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Computation ID</label>
                    <p className="text-gray-900 font-mono text-sm mt-1">{computation.computation_id}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Type</label>
                    <p className="text-gray-900 mt-1">{computation.type || 'health_statistics'}</p>
                  </div>
                </div>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium text-gray-500">Created</label>
                    <p className="text-gray-900 mt-1">
                      {computation.created_at ? new Date(computation.created_at).toLocaleDateString() : 'N/A'}
                    </p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-500">Security Method</label>
                    <p className="text-gray-900 flex items-center gap-1 mt-1">
                      <Lock className="w-4 h-4" />
                      {computation.security_method || 'SMPC'}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            {/* Participants */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  Participants ({participants.length})
                </h3>
                {(computation.status === 'waiting_for_participants' || computation.status === 'waiting_for_data' || computation.status === 'initialized') && (
                  <button
                    onClick={() => setShowAddParticipants(true)}
                    className="flex items-center gap-1 text-sm bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <UserPlus className="w-4 h-4" />
                    Add
                  </button>
                )}
              </div>
              
              <div className="space-y-3">
                {participants.length > 0 ? (
                  participants.map((participant, index) => (
                    <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                          <Users className="w-4 h-4 text-blue-600" />
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {participant.organization_name || `Organization ${participant.org_id || participant.id}`}
                          </p>
                          <p className="text-sm text-gray-500">
                            {participant.joined_at ? `Joined ${new Date(participant.joined_at).toLocaleDateString()}` : 'Active'}
                          </p>
                        </div>
                      </div>
                      
                      {/* Submission Status */}
                      <div className="flex items-center gap-2">
                        {participant.has_submitted ? (
                          <div className="flex items-center gap-1">
                            <CheckCircle className="w-4 h-4 text-green-500" />
                            <span className="text-xs font-medium text-green-700">Submitted</span>
                            {participant.submitted_at && (
                              <span className="text-xs text-gray-500 ml-1">
                                {new Date(participant.submitted_at).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        ) : (
                          <div className="flex items-center gap-1">
                            <Clock className="w-4 h-4 text-orange-500" />
                            <span className="text-xs font-medium text-orange-700">Pending</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">No participants data available</p>
                )}
              </div>
            </div>

            {/* Progress */}
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Activity className="w-5 h-5" />
                Progress
              </h3>
              
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Participants</span>
                    <span>{computation.participants_count || 0}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${Math.min(100, (computation.participants_count || 0) * 33)}%` }}
                    ></div>
                  </div>
                </div>
                
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Data Submissions</span>
                    <span>{computation.submissions_count || 0}</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-600 h-2 rounded-full" 
                      style={{ width: `${computation.progress_percentage || 0}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Computation Results Section */}
      {(computation.status === 'completed' || computation.status === 'error' || showResults) && (
        <div className="max-w-6xl mx-auto px-4 mb-8">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900 flex items-center gap-2">
                  <BarChart3 className="w-5 h-5" />
                  Computation Results
                </h2>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handleExport}
                    className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Export
                  </button>
                  <button
                    onClick={() => setShowResults(!showResults)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    {showResults ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
                  </button>
                </div>
              </div>
              
              {showResults && (
                <div className="border-t pt-4">
                  <ComputationResults 
                    computationId={id}
                    computation={computation}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Add Participants Modal */}
      {showAddParticipants && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            <div className="flex items-center justify-between p-6 border-b">
              <h3 className="text-lg font-semibold text-gray-900">Add Participants</h3>
              <button
                onClick={() => setShowAddParticipants(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-6">
              <p className="text-sm text-gray-600 mb-4">
                Select organizations to invite to this computation:
              </p>
              
              <div className="space-y-3 max-h-64 overflow-y-auto">
                {availableOrgs.length > 0 ? (
                  availableOrgs.map((org) => (
                    <label key={org.id} className="flex items-center gap-3 p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={selectedNewParticipants.includes(org.id)}
                        onChange={() => handleParticipantSelection(org.id)}
                        className="rounded border-gray-300"
                      />
                      <div className="flex-1">
                        <p className="font-medium text-gray-900">{org.name}</p>
                        <p className="text-sm text-gray-500">{org.type}</p>
                      </div>
                    </label>
                  ))
                ) : (
                  <p className="text-gray-500 text-center py-4">
                    No available organizations to invite
                  </p>
                )}
              </div>
            </div>
            
            <div className="flex items-center justify-end gap-3 p-6 border-t">
              <button
                onClick={() => setShowAddParticipants(false)}
                className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Cancel
              </button>
              <button
                onClick={handleAddParticipants}
                disabled={selectedNewParticipants.length === 0 || inviting}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {inviting ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    Inviting...
                  </>
                ) : (
                  <>
                    <UserPlus className="w-4 h-4" />
                    Invite {selectedNewParticipants.length} Participant{selectedNewParticipants.length !== 1 ? 's' : ''}
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
