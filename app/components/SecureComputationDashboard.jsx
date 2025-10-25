"use client";

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useSearchParams } from 'next/navigation';
import { toast } from 'react-hot-toast';
import { 
  Plus, 
  Users, 
  Activity, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Download,
  Eye,
  Play,
  RefreshCw,
  UserPlus,
  UserMinus,
  Bell,
  Check,
  X,
  Filter,
  Trash2,
  FileText,
  BarChart3
} from 'lucide-react';
import Link from 'next/link';
import { secureComputationService } from '../services/secureComputationService';
import SecureComputationWizard from './SecureComputationWizard';

const ConnectionStatusIndicator = ({ status, pingStatus, heartbeatStatus }) => {
  // Determine color based on connection status
  let color = 'bg-gray-500'; // Default gray
  let statusText = 'Unknown';
  
  switch (status) {
    case 'connected':
      color = 'bg-green-500';
      statusText = 'Connected';
      break;
    case 'connecting':
      color = 'bg-blue-500 animate-pulse';
      statusText = 'Connecting';
      break;
    case 'reconnecting':
      color = 'bg-yellow-500 animate-pulse';
      statusText = 'Reconnecting';
      break;
    case 'unstable':
      color = 'bg-orange-500';
      statusText = 'Unstable';
      break;
    case 'error':
      color = 'bg-red-500';
      statusText = 'Error';
      break;
    case 'disconnected':
      color = 'bg-red-500';
      statusText = 'Disconnected';
      break;
  }
  
  return (
    <div className="flex items-center space-x-2 text-sm">
      <div className={`w-3 h-3 rounded-full ${color}`}></div>
      <span>{statusText}</span>
      {pingStatus?.latency && status === 'connected' && (
        <span className="text-xs text-gray-500">{pingStatus.latency}ms</span>
      )}
      {heartbeatStatus?.missedHeartbeats > 0 && (
        <span className="text-xs text-orange-500">
          {heartbeatStatus.missedHeartbeats} missed
        </span>
      )}
    </div>
);
};

const SecureComputationDashboard = () => {
  const { user } = useAuth();
  const searchParams = useSearchParams();

  // Check if user has permission to access secure computations
  if (user?.role === 'patient') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600 mb-6">You don't have permission to access secure computations.</p>
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Return to Dashboard
          </Link>
        </div>
      </div>
    );
  }
  const computationId = searchParams.get('id');
  const [computations, setComputations] = useState([]);
  const [filteredComputations, setFilteredComputations] = useState([]);
  const [activeTab, setActiveTab] = useState('all'); // 'all', 'completed', 'in_progress', 'pending'
  const [loading, setLoading] = useState(true);
  const [websocket, setWebsocket] = useState(null);
  const [reconnectAttempt, setReconnectAttempt] = useState(0);
  const [pendingRequests, setPendingRequests] = useState([]);
  const [userSubmissions, setUserSubmissions] = useState({}); // Track user submissions by computation_id
  const [error, setError] = useState(null);
  const [showWizard, setShowWizard] = useState(false);
  const [showNewComputationModal, setShowNewComputationModal] = useState(false);
  const [showPendingRequestsModal, setShowPendingRequestsModal] = useState(false);
  const [showParticipants, setShowParticipants] = useState({});
  const [activeParticipants, setActiveParticipants] = useState({});
  const [deleteConfirmation, setDeleteConfirmation] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [pingStatus, setPingStatus] = useState(null);
  const [heartbeatStatus, setHeartbeatStatus] = useState({ lastHeartbeat: null, lastAck: null, rtt: null, missedHeartbeats: 0 });
  const [lastActivity, setLastActivity] = useState(new Date());
  const [connectionHealth, setConnectionHealth] = useState(null);
  const [queuedMessages, setQueuedMessages] = useState([]);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 3000;
  const PING_INTERVAL = 30000; // 30 seconds
  const HEARTBEAT_INTERVAL = 15000; // 15 seconds

  // Helper: collect deletable computations by creator name
  const getDeletableByCreator = useCallback((creatorName) => {
    const allowedStatuses = ['waiting_for_participants', 'initialized', 'waiting_for_data', 'error'];
    return computations.filter((c) =>
      allowedStatuses.includes(c.status) &&
      ((c.creator_name && c.creator_name.toLowerCase() === creatorName.toLowerCase()) ||
       (c.creator && typeof c.creator === 'string' && c.creator.toLowerCase() === creatorName.toLowerCase()))
    );
  }, [computations]);

  const handleBulkDeleteByCreator = async (creatorName = 'Test Hospital') => {
    try {
      const token = user?.token || localStorage.getItem('token');
      if (!token) {
        toast.error('Authentication required');
        return;
      }
      const candidates = getDeletableByCreator(creatorName);
      if (!candidates.length) {
        toast('No deletable computations found for the specified creator.');
        return;
      }
      const confirm = window.confirm(`Delete ${candidates.length} computation(s) created by ${creatorName}? This cannot be undone.`);
      if (!confirm) return;

      let success = 0;
      let failed = 0;
      for (const comp of candidates) {
        try {
          await secureComputationService.deleteComputation(comp.computation_id, token);
          success++;
        } catch (err) {
          failed++;
          console.error('Failed to delete computation', comp.computation_id, err);
        }
      }

      if (success) {
        toast.success(`Deleted ${success} computation(s) created by ${creatorName}.`);
        // Remove deleted from local state
        setComputations(prev => prev.filter(c => !candidates.some(x => x.computation_id === c.computation_id)));
      }
      if (failed) {
        toast.error(`${failed} deletion(s) failed. Check logs or try again.`);
      }

      // Refresh from server to ensure consistency
      await fetchComputations();
    } catch (e) {
      console.error('Bulk delete error:', e);
      toast.error('Bulk delete failed');
    }
  };

  const connectWebSocket = useCallback(() => {
    // Prevent multiple connections
    if (websocket && websocket.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket connection already in progress');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      if (!token || !user) {
        console.error('No auth token or user found');
        return;
      }

      // Get user info for connection metadata
      const userEmail = localStorage.getItem('userEmail') || user?.email || 'unknown';
      const userRole = localStorage.getItem('userRole') || user?.role || 'unknown';
      const userAgent = navigator.userAgent;

      setConnectionStatus('connecting');
      console.log('Connecting to WebSocket with token and metadata...');
      const wsUrl = `ws://localhost:8000/ws/metrics?token=${token}&email=${encodeURIComponent(userEmail)}&role=${encodeURIComponent(userRole)}&user_agent=${encodeURIComponent(userAgent)}`;
      console.log('WebSocket URL (sanitized):', wsUrl.replace(token, '[REDACTED]'));
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('WebSocket connected for SMPC dashboard');
        setReconnectAttempt(0);
        setConnectionStatus('connected');
        setLastActivity(new Date());
        setHeartbeatStatus(prev => ({ ...prev, missedHeartbeats: 0 }));
        toast.success('Connected to real-time updates');
        
        // Request active computations
        ws.send(JSON.stringify({
          type: 'get_active_computations'
        }));
        
        // Force refresh data after successful connection
        console.log('Refreshing data after successful WebSocket connection');
        fetchComputations();
        fetchPendingRequests();
        
        // Process any queued messages that accumulated during disconnection
        if (queuedMessages.length > 0) {
          console.log(`Processing ${queuedMessages.length} queued messages`);
          // Create a copy to avoid state mutation issues
          const messagesToProcess = [...queuedMessages];
          setQueuedMessages([]);
          
          // Process each queued message
          messagesToProcess.forEach(msg => {
            try {
              ws.send(JSON.stringify(msg));
              console.log('Sent queued message of type:', msg.type);
            } catch (err) {
              console.error('Error sending queued message:', err);
            }
          });
        }
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          console.log('WebSocket message received:', message.type);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        setConnectionStatus('error');
        toast.error('Connection error. Attempting to reconnect...');
      };

      ws.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        const wasConnected = connectionStatus === 'connected';
        setConnectionStatus('disconnected');
        
        // If this was an abnormal closure and we were previously connected, show a more specific message
        if (wasConnected && event.code !== 1000 && event.code !== 1001) {
          toast.error(`Connection lost: ${event.reason || 'Unknown reason'}. Attempting to reconnect...`);
        }
        
        if (reconnectAttempt < MAX_RECONNECT_ATTEMPTS) {
          console.log(`Attempting to reconnect (${reconnectAttempt + 1}/${MAX_RECONNECT_ATTEMPTS})...`);
          setConnectionStatus('reconnecting');
          
          // Use exponential backoff for reconnection attempts
          const backoffDelay = RECONNECT_DELAY * Math.pow(1.5, reconnectAttempt);
          setTimeout(() => {
            setReconnectAttempt(prev => prev + 1);
            connectWebSocket();
            
            // Force refresh data after reconnection attempt
            console.log('Refreshing data after reconnection attempt');
            fetchComputations();
            fetchPendingRequests();
          }, backoffDelay);
        } else {
          toast.error('Failed to connect after multiple attempts. Please refresh the page.');
        }
      };

      setWebsocket(ws);
    } catch (error) {
      console.error('Error connecting to WebSocket:', error);
    }
  }, [reconnectAttempt, connectionStatus, queuedMessages]);

  const handleWebSocketMessage = (message) => {
    // Update last activity timestamp
    setLastActivity(new Date());
    
    switch (message.type) {
      case 'computation_status':
        console.log('Computation status update:', message.data);
        updateComputationStatus(message.data);
        break;
      case 'participant_joined':
        console.log('Participant joined:', message.data);
        handleParticipantJoined(message.data);
        break;
      case 'participant_left':
        console.log('Participant left:', message.data);
        handleParticipantLeft(message.data);
        break;
      case 'data_submitted':
        console.log('Data submitted update:', message.data);
        handleDataSubmitted(message.data);
        break;
      case 'computation_completed':
        console.log('Computation completed update:', message.data);
        handleComputationCompleted(message.data);
        break;
      case 'active_participants':
        handleActiveParticipants(message.data);
        break;
      case 'connection_health':
        console.log('Connection health update:', message.data);
        handleConnectionHealth(message.data);
        break;
      case 'pong':
        // Update ping status
        setPingStatus({
          lastPong: new Date(),
          latency: new Date().getTime() - message.data.timestamp,
          serverTime: message.data.server_time
        });
        break;
      case 'heartbeat':
        // Respond to heartbeat with acknowledgment
        if (websocket && websocket.readyState === WebSocket.OPEN) {
          websocket.send(JSON.stringify({
            type: 'heartbeat_ack',
            timestamp: new Date().getTime(),
            received_at: message.data.timestamp
          }));
        }
        setHeartbeatStatus(prev => ({
          ...prev,
          lastHeartbeat: new Date()
        }));
        break;
      case 'heartbeat_ack':
        // Calculate round-trip time and update heartbeat status
        const rtt = new Date().getTime() - message.data.received_at;
        setHeartbeatStatus(prev => ({
          ...prev,
          lastAck: new Date(),
          rtt: rtt,
          missedHeartbeats: 0 // Reset missed heartbeats counter
        }));
        break;
      case 'system_notification':
        toast(message.data.message, {
          icon: message.data.level === 'error' ? '❌' : 
                message.data.level === 'warning' ? '⚠️' : '✅',
          duration: 5000
        });
        break;
      case 'active_computations':
        handleActiveComputations(message.data);
        break;
      case 'reconnect':
        // Server requested reconnection
        toast('Server requested reconnection. Reconnecting...');
        if (websocket) {
          websocket.close();
          setTimeout(() => connectWebSocket(), 1000);
        }
        break;
      case 'queued_messages':
        // Process queued messages that were stored on the server while disconnected
        if (message.data && Array.isArray(message.data.messages)) {
          message.data.messages.forEach(queuedMsg => {
            handleWebSocketMessage(queuedMsg);
          });
          toast.success(`Processed ${message.data.messages.length} messages that arrived while you were disconnected`);
        }
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const updateComputationStatus = (data) => {
    console.log(`Updating computation ${data.computation_id} status to ${data.status}`); 
    
    setComputations(prevComputations => {
      const updated = prevComputations.map(comp => 
        comp.computation_id === data.computation_id 
          ? { 
              ...comp, 
              status: data.status,
              participants_count: data.total_participants || comp.participants_count,
              submissions_count: data.submitted_count || comp.submissions_count,
              updated_at: new Date().toISOString()
            }
          : comp
      );
      console.log('Updated computations:', updated);
      
      // Force update of filtered computations
      setTimeout(() => {
        setFilteredComputations(updated.filter(comp => {
          if (activeTab === 'all') return true;
          if (activeTab === 'completed') return comp.status === 'completed';
          if (activeTab === 'in_progress') return comp.status === 'processing' || comp.status === 'waiting_for_data' || comp.status === 'ready_to_compute';
          if (activeTab === 'pending') return comp.status === 'initialized' || comp.status === 'waiting_for_participants';
          return true;
        }));
      }, 50);
      
      return updated;
    });
  };

  const handleParticipantJoined = (data) => {
    toast.success(`New participant joined computation ${data.computation_id}`);
    fetchComputations(); // Refresh the list
    fetchActiveParticipants(data.computation_id);
  };

  const handleParticipantLeft = (data) => {
    toast(`Participant left computation ${data.computation_id}`);
    fetchComputations(); // Refresh the list
    fetchActiveParticipants(data.computation_id);
  };
  
  const handleActiveParticipants = (data) => {
    setActiveParticipants(prev => ({
      ...prev,
      [data.computation_id]: data.active_participants
    }));
  };
  
  const fetchActiveParticipants = async (computationId, retryCount = 0, delay = 1000) => {
    try {
      const token = user?.token || localStorage.getItem('token');
      if (!token) {
        toast.error('Authentication required');
        return;
      }
      
      try {
        const response = await secureComputationService.getActiveParticipants(computationId, token);
        setActiveParticipants(prev => ({
          ...prev,
          [computationId]: response.participants || []
        }));
      } catch (err) {
        // Check if the error is due to authentication issues
        if (err.message && (err.message.includes('authentication') || err.message.includes('expired'))) {
          // Try to refresh the token if available
          if (user.refreshToken) {
            try {
              const refreshed = await user.refreshToken();
              if (refreshed) {
                // Retry with new token
                const response = await secureComputationService.getActiveParticipants(computationId, user.token);
                setActiveParticipants(prev => ({
                  ...prev,
                  [computationId]: response.participants || []
                }));
                return;
              }
            } catch (refreshError) {
              console.error('Error refreshing token:', refreshError);
            }
          }
        }
        
        // Handle rate limiting with exponential backoff
        if (err.message && err.message.includes('Too many requests') && retryCount < 5) {
          console.log(`Rate limited. Retrying in ${delay}ms... (Attempt ${retryCount + 1}/5)`);
          if (retryCount === 0) {
            toast(`Server is busy. Automatically retrying... (1/5)`);
          } else if (retryCount === 2) {
            toast(`Still experiencing high traffic. Continuing to retry... (${retryCount + 1}/5)`);
          }
          setTimeout(() => {
            fetchActiveParticipants(computationId, retryCount + 1, delay * 2); // Exponential backoff
          }, delay);
          return;
        }
        
        // If we get here, either token refresh failed or it was another type of error
        console.error(`Error fetching active participants for computation ${computationId}:`, err);
      }
    } catch (error) {
      console.error(`Error in fetchActiveParticipants for computation ${computationId}:`, error);
    }
  };

  const handleDataSubmitted = (data) => {
    toast.success(`Data submitted to computation ${data.computation_id} (${data.data_points} points)`);
    updateComputationStatus({
      computation_id: data.computation_id,
      status: 'waiting_for_data',
      total_participants: computations.find(c => c.computation_id === data.computation_id)?.participants_count || 0,
      submitted_count: (computations.find(c => c.computation_id === data.computation_id)?.submissions_count || 0) + 1
    });
  };

  const handleComputationCompleted = (data) => {
    toast.success(`Computation ${data.computation_id} completed successfully!`);
    updateComputationStatus({
      computation_id: data.computation_id,
      status: 'completed',
      total_participants: data.result_summary?.organizations_count || data.total_participants,
      submitted_count: data.result_summary?.data_points_count || data.submitted_count
    });
    // Refresh the computations list
    console.log('Refreshing computations after completion');
    fetchComputations();
    
    // Also refresh pending requests in case any were affected
    fetchPendingRequests();
    
    // Force re-render of filtered computations
    setTimeout(() => {
      filterComputations();
    }, 100);
  };

  const joinComputationRoom = (computationId) => {
    const message = {
      type: 'join_computation',
      computation_id: computationId
    };
    
    if (!sendMessage(message)) {
      // Only show notification once per computation ID to avoid spam
      if (!queuedMessages.some(msg => msg.type === 'join_computation' && msg.computation_id === computationId)) {
        console.log(`Will join computation ${computationId} when connection is restored`);
      }
    }
  };

  const leaveComputationRoom = (computationId) => {
    const message = {
      type: 'leave_computation',
      computation_id: computationId
    };
    
    sendMessage(message);
  };

  const fetchComputations = async (retryCount = 0, delay = 1000) => {
    try {
      setLoading(true);
      const token = user?.token || localStorage.getItem('token');
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      try {
        console.log('Fetching computations...');
        const response = await secureComputationService.listComputations(token);
        console.log('Computations response:', response);
        
        // Ensure status consistency by checking actual computation details
        const enrichedComputations = await Promise.all(
          response.map(async (comp) => {
            try {
              const details = await secureComputationService.getComputationDetails(comp.computation_id, token);
              return {
                ...comp,
                status: details.status || comp.status,
                participants_count: details.participants_count || comp.participants_count,
                submissions_count: details.submissions_count || comp.submissions_count
              };
            } catch (err) {
              console.warn(`Failed to fetch details for ${comp.computation_id}:`, err);
              return comp;
            }
          })
        );
        
        setComputations(enrichedComputations);
        setError(null); // Clear any previous errors
      } catch (err) {
        console.error('Error fetching computations:', err);
        // Check if the error is due to authentication issues
        if (err.message && (err.message.includes('authentication') || err.message.includes('expired'))) {
          // Try to refresh the token if available
          if (user.refreshToken) {
            try {
              const refreshed = await user.refreshToken();
              if (refreshed) {
                // Retry with new token
                const response = await secureComputationService.listComputations(user.token);
                console.log('Computations response after token refresh:', response);
                setComputations(response);
                return;
              }
            } catch (refreshError) {
              console.error('Error refreshing token:', refreshError);
            }
          }
        }
        
        // Handle rate limiting with exponential backoff
        if (err.message && err.message.includes('Too many requests') && retryCount < 5) {
          console.log(`Rate limited. Retrying in ${delay}ms... (Attempt ${retryCount + 1}/5)`);
          if (retryCount === 0) {
            toast(`Server is busy. Automatically retrying... (1/5)`);
          } else if (retryCount === 2) {
            toast(`Still experiencing high traffic. Continuing to retry... (${retryCount + 1}/5)`);
          }
          setTimeout(() => {
            fetchComputations(retryCount + 1, delay * 2); // Exponential backoff
          }, delay);
          return;
        }
        
        // If we get here, either token refresh failed or it was another type of error
        console.error('Error fetching computations:', err);
        setError(`Failed to fetch computations: ${err.message}`);
        toast.error(`Failed to fetch computations: ${err.message}`);
      }
    } finally {
      if (retryCount === 0) { // Only set loading to false on the initial call or final retry
        setLoading(false);
      }
    }
  };

  const initializeComputation = async () => {
    try {
      const token = user?.token || localStorage.getItem('token');
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      const response = await secureComputationService.initializeComputation({
        computation_type: 'health_statistics',
        participating_orgs: [String(user.id)]
      }, token);

      if (response.success) {
        toast.success('Computation initialized successfully!');
        fetchComputations();
      } else {
        toast.error(response.error || 'Failed to initialize computation');
      }
    } catch (error) {
      console.error('Error initializing computation:', error);
      toast.error('Failed to initialize computation');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'processing':
        return <Activity className="w-5 h-5 text-blue-500 animate-pulse" />;
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case 'waiting_for_data':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'error':
        return 'bg-red-100 text-red-800';
      case 'waiting_for_data':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };



  // Handle connection health updates
  const handleConnectionHealth = (data) => {
    setConnectionHealth(data);
    
    // Update UI based on connection state
    switch (data.status) {
      case 'stale':
        toast('Connection appears to be stale. You may experience delays in updates.');
        break;
      case 'unstable':
        toast('Connection is unstable. Some messages may be delayed.');
        break;
      case 'reconnecting':
        setConnectionStatus('reconnecting');
        toast('Server is attempting to reconnect. Please wait...');
        break;
      case 'healthy':
        // If we were previously in a degraded state, show recovery message
        if (connectionHealth && connectionHealth.status !== 'healthy') {
          toast.success('Connection has been restored.');
        }
        break;
    }
    
    // If server requests reconnection, reconnect
    if (data.action === 'reconnect') {
      if (websocket) {
        websocket.close();
        setTimeout(() => connectWebSocket(), 1000);
      }
    }
    
    // Update heartbeat status if provided
    if (data.heartbeat_info) {
      setHeartbeatStatus(prev => ({
        ...prev,
        ...data.heartbeat_info
      }));
    }
  };
  
  // Handle active computations list
  const handleActiveComputations = (data) => {
    // Join all active computation rooms
    if (data.computations && Array.isArray(data.computations)) {
      data.computations.forEach(compId => {
        joinComputationRoom(compId);
      });
    }
  };
  
  // Queue a message to be sent when connection is restored
  const queueMessage = (message) => {
    // Only queue important messages, not pings/heartbeats
    if (message.type !== 'ping' && message.type !== 'heartbeat' && message.type !== 'heartbeat_ack') {
      setQueuedMessages(prev => {
        // Limit queue size to prevent memory issues
        const maxQueueSize = 50;
        const newQueue = [...prev, message];
        return newQueue.slice(-maxQueueSize);
      });
    }
  };
  
  // Send a message with fallback to queue if disconnected
  const sendMessage = (message) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      try {
        websocket.send(JSON.stringify(message));
        return true; // Successfully sent
      } catch (error) {
        console.error('Error sending message:', error);
        queueMessage(message);
        return false; // Failed to send
      }
    } else {
      // Connection not open, queue the message
      queueMessage(message);
      return false; // Not sent immediately
    }
  };
  
  // Send periodic ping to keep connection alive
  useEffect(() => {
    if (!websocket || websocket.readyState !== WebSocket.OPEN) return;
    
    const pingInterval = setInterval(() => {
      try {
        websocket.send(JSON.stringify({
          type: 'ping',
          timestamp: new Date().getTime()
        }));
      } catch (error) {
        console.error('Error sending ping:', error);
      }
    }, PING_INTERVAL);
    
    // Send heartbeats to monitor connection health
    const heartbeatInterval = setInterval(() => {
      try {
        if (websocket.readyState === WebSocket.OPEN) {
          websocket.send(JSON.stringify({
            type: 'heartbeat',
            timestamp: new Date().getTime(),
            client_info: {
              browser: navigator.userAgent,
              screen_width: window.innerWidth,
              screen_height: window.innerHeight,
              connection_status: connectionStatus,
              missed_heartbeats: heartbeatStatus.missedHeartbeats || 0
            }
          }));
          
          // Increment missed heartbeats counter (will be reset when ack is received)
          setHeartbeatStatus(prev => ({
            ...prev,
            lastHeartbeat: new Date(),
            missedHeartbeats: prev.missedHeartbeats + 1
          }));
          
          // If too many missed heartbeats, connection might be unstable
          if (heartbeatStatus.missedHeartbeats >= 3) {
            setConnectionStatus('unstable');
            toast('Connection appears unstable. Some messages may be delayed.', {
              icon: '⚠️',
              duration: 4000
            });
          }
        }
      } catch (error) {
        console.error('Error sending heartbeat:', error);
      }
    }, HEARTBEAT_INTERVAL);
    
    return () => {
      clearInterval(pingInterval);
      clearInterval(heartbeatInterval);
    };
  }, [websocket, connectionStatus, heartbeatStatus.missedHeartbeats]);
  
  useEffect(() => {
    // Only connect if we have a user and token
    if (user && localStorage.getItem('token')) {
      connectWebSocket();
      console.log('WebSocket connection initialized');
    }
    return () => {
      if (websocket) {
        console.log('Closing WebSocket connection');
        websocket.close();
      }
    };
  }, [user]); // Remove connectWebSocket dependency to prevent infinite loops
  
  // Filter computations based on active tab
  const filterComputations = useCallback(() => {
    console.log('Filtering computations:', computations);
    console.log('Active tab:', activeTab);
    console.log('All computation statuses:', computations.map(comp => comp.status));
    
    let filtered;
    
    if (activeTab === 'all') {
      filtered = computations;
    } else if (activeTab === 'completed') {
      filtered = computations.filter(comp => comp.status === 'completed');
    } else if (activeTab === 'in_progress') {
      filtered = computations.filter(comp => 
        comp.status === 'processing' || 
        comp.status === 'waiting_for_data' || 
        comp.status === 'ready_to_compute' ||
        (comp.status !== 'completed' && comp.status !== 'error' && comp.status !== 'initialized' && comp.status !== 'waiting_for_participants')
      );
      console.log('In progress filtered statuses:', filtered.map(comp => comp.status));
    } else if (activeTab === 'pending') {
      filtered = computations.filter(comp => 
        comp.status === 'initialized' || 
        comp.status === 'waiting_for_participants'
      );
      console.log('Pending filtered statuses:', filtered.map(comp => comp.status));
    }
    
    // Log the filtered computations for debugging
    console.log('Filtered computations count:', filtered?.length);
    setFilteredComputations(filtered);
  }, [activeTab, computations]);
  

  useEffect(() => {
    filterComputations();
  }, [activeTab, computations, filterComputations]);

  useEffect(() => {
    fetchComputations();
    fetchPendingRequests();
  }, [user]);
  
  // Handle computation ID from URL if provided
  useEffect(() => {
    if (computationId && computations.length > 0) {
      console.log(`URL contains computation ID: ${computationId}, selecting this computation`);
      const computation = computations.find(comp => comp.computation_id === computationId);
      if (computation) {
        // If the computation is found, set the appropriate tab
        if (computation.status === 'completed') {
          setActiveTab('completed');
        } else if (computation.status === 'initialized' || computation.status === 'waiting_for_participants') {
          setActiveTab('pending');
        } else {
          setActiveTab('in_progress');
        }
      }
    }
  }, [computationId, computations]);
  
  const fetchPendingRequests = async (retryCount = 0, delay = 1000) => {
    try {
      const token = user?.token || localStorage.getItem('token');
      if (!token) return;
      
      try {
        // Fetch pending computation requests
        console.log('Fetching pending requests...');
        const response = await secureComputationService.getPendingRequests(token);
        console.log('Pending requests response:', response);
        setPendingRequests(response);
      } catch (err) {
        console.error('Error fetching pending requests:', err);
        // Check if the error is due to authentication issues
        if (err.isAuthError || (err.message && (err.message.includes('authentication') || err.message.includes('expired')))) {
          // Try to refresh the token if available
          if (user.refreshToken) {
            try {
              const refreshed = await user.refreshToken();
              if (refreshed) {
                // Retry with new token
                const response = await secureComputationService.getPendingRequests(user.token);
                setPendingRequests(response);
                return;
              }
            } catch (refreshError) {
              console.error('Error refreshing token:', refreshError);
            }
          }
        }
        
        // Handle rate limiting with exponential backoff
        if (err.message && err.message.includes('Too many requests') && retryCount < 5) {
          console.log(`Rate limited. Retrying in ${delay}ms... (Attempt ${retryCount + 1}/5)`);
          if (retryCount === 0) {
            toast(`Server is busy. Automatically retrying... (1/5)`);
          } else if (retryCount === 2) {
            toast(`Still experiencing high traffic. Continuing to retry... (${retryCount + 1}/5)`);
          }
          setTimeout(() => {
            fetchPendingRequests(retryCount + 1, delay * 2); // Exponential backoff
          }, delay);
          return;
        }
        
        // If we get here, either token refresh failed or it was another type of error
        console.error('Error fetching pending requests:', err);
      }
    } catch (error) {
      console.error('Error in fetchPendingRequests:', error);
    }
  };
  
  const handleAcceptRequest = async (computationId, retryCount = 0, delay = 1000) => {
    try {
      const token = user?.token || localStorage.getItem('token');
      try {
        await secureComputationService.acceptComputationRequest(computationId, token);
        toast.success('Computation request accepted');
        // Remove from pending requests
        setPendingRequests(prev => prev.filter(req => req.computation_id !== computationId));
        // Refresh computations list
        fetchComputations();
      } catch (err) {
        // Check if the error is due to authentication issues
        if (err.isAuthError || (err.message && (err.message.includes('authentication') || err.message.includes('expired')))) {
          // Try to refresh the token if available
          if (user.refreshToken) {
            try {
              const refreshed = await user.refreshToken();
              if (refreshed) {
                // Retry with new token
                await secureComputationService.acceptComputationRequest(computationId, user.token);
                toast.success('Computation request accepted');
                // Remove from pending requests
                setPendingRequests(prev => prev.filter(req => req.computation_id !== computationId));
                // Refresh computations list
                fetchComputations();
                return;
              }
            } catch (refreshError) {
              console.error('Error refreshing token:', refreshError);
            }
          }
        }
        
        // Handle rate limiting with exponential backoff
        if (err.message && err.message.includes('Too many requests') && retryCount < 5) {
          console.log(`Rate limited. Retrying in ${delay}ms... (Attempt ${retryCount + 1}/5)`);
          if (retryCount === 0) {
            toast(`Server is busy. Automatically retrying... (1/5)`);
          } else if (retryCount === 2) {
            toast(`Still experiencing high traffic. Continuing to retry... (${retryCount + 1}/5)`);
          }
          setTimeout(() => {
            handleAcceptRequest(computationId, retryCount + 1, delay * 2); // Exponential backoff
          }, delay);
          return;
        }
        
        // If we get here, either token refresh failed or it was another type of error
        console.error('Error accepting computation request:', err);
        toast.error('Failed to accept computation request');
      }
    } catch (error) {
      console.error('Error in handleAcceptRequest:', error);
      toast.error('Failed to accept computation request');
    }
  };
  
  const handleDeclineRequest = async (computationId, retryCount = 0, delay = 1000) => {
    try {
      const token = user?.token || localStorage.getItem('token');
      try {
        await secureComputationService.declineComputationRequest(computationId, token);
        toast.success('Computation request declined');
        // Remove from pending requests
        setPendingRequests(prev => prev.filter(req => req.computation_id !== computationId));
      } catch (err) {
        // Check if the error is due to authentication issues
        if (err.message && (err.message.includes('authentication') || err.message.includes('expired'))) {
          // Try to refresh the token if available
          if (user.refreshToken) {
            try {
              const refreshed = await user.refreshToken();
              if (refreshed) {
                // Retry with new token
                await secureComputationService.declineComputationRequest(computationId, user.token);
                toast.success('Computation request declined');
                // Remove from pending requests
                setPendingRequests(prev => prev.filter(req => req.computation_id !== computationId));
                return;
              }
            } catch (refreshError) {
              console.error('Error refreshing token:', refreshError);
            }
          }
        }
        
        // Handle rate limiting with exponential backoff
        if (err.message && err.message.includes('Too many requests') && retryCount < 5) {
          console.log(`Rate limited. Retrying in ${delay}ms... (Attempt ${retryCount + 1}/5)`);
          if (retryCount === 0) {
            toast(`Server is busy. Automatically retrying... (1/5)`);
          } else if (retryCount === 2) {
            toast(`Still experiencing high traffic. Continuing to retry... (${retryCount + 1}/5)`);
          }
          setTimeout(() => {
            handleDeclineRequest(computationId, retryCount + 1, delay * 2); // Exponential backoff
          }, delay);
          return;
        }
        
        // If we get here, either token refresh failed or it was another type of error
        console.error('Error declining computation request:', err);
        toast.error('Failed to decline computation request');
      }
    } catch (error) {
      console.error('Error in handleDeclineRequest:', error);
      toast.error('Failed to decline computation request');
    }
  };

  useEffect(() => {
    // Join rooms for all computations when they load
    computations.forEach(comp => {
      joinComputationRoom(comp.computation_id);
      fetchActiveParticipants(comp.computation_id);
    });

    return () => {
      // Leave all rooms when component unmounts
      computations.forEach(comp => {
        leaveComputationRoom(comp.computation_id);
      });
    };
  }, [computations]);
  
  const toggleParticipantsView = (computationId) => {
    setShowParticipants(prev => ({
      ...prev,
      [computationId]: !prev[computationId]
    }));
  };

  const handleDeleteComputation = async (computationId) => {
    try {
      const token = user?.token || localStorage.getItem('token');
      if (!token) {
        toast.error('Authentication required');
        return;
      }

      // Check current status before attempting delete
      const currentComputation = computations.find(comp => comp.computation_id === computationId);
      if (currentComputation && !['waiting_for_participants', 'initialized', 'waiting_for_data', 'error'].includes(currentComputation.status)) {
        toast.error(`Cannot delete computation with status '${currentComputation.status}'. Only computations that haven't started processing can be deleted.`);
        setDeleteConfirmation(null);
        // Refresh to get latest status
        await fetchComputations();
        return;
      }

      await secureComputationService.deleteComputation(computationId, token);
      toast.success('Computation deleted successfully');
      
      // Remove from local state
      setComputations(prev => prev.filter(comp => comp.computation_id !== computationId));
      setDeleteConfirmation(null);
      
      // Refresh the computations list to ensure consistency
      await fetchComputations();
      
    } catch (error) {
      console.error('Error deleting computation:', error);
      
      // Handle authentication errors specifically
      if (error.isAuthError) {
        toast.error('Session expired. Please log in again.');
        // Force logout and redirect to login
        localStorage.removeItem('token');
        window.location.href = '/login';
      } else {
        // Handle specific delete restriction errors
        if (error.message && error.message.includes('Cannot delete computation with status')) {
          toast.error(error.message);
          // Refresh computations to get latest status
          await fetchComputations();
        } else {
          toast.error(error.message || 'Failed to delete computation');
        }
      }
      setDeleteConfirmation(null);
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
    <>
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Secure Computations</h2>
          <p className="text-gray-600">Real-time collaborative health data analysis</p>
          <div className="mt-1">
            <ConnectionStatusIndicator 
              status={connectionStatus} 
              pingStatus={pingStatus} 
              heartbeatStatus={heartbeatStatus} 
            />
            {queuedMessages.length > 0 && (
              <div className="text-xs text-orange-500 mt-1">
                {queuedMessages.length} message(s) queued for delivery
              </div>
            )}
          </div>
        </div>
        <div className="flex gap-4">
          <button 
            onClick={() => setShowPendingRequestsModal(true)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${pendingRequests.length > 0 ? 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
          >
            <Bell className="w-5 h-5" />
            Pending Requests
            {pendingRequests.length > 0 && (
              <span className="bg-yellow-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                {pendingRequests.length}
              </span>
            )}
          </button>
          <button
            onClick={() => setShowNewComputationModal(true)}
            className="flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Start New Computation
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-8">
          <button
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'all' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('all')}
          >
            All Computations
          </button>
          <button
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'completed' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('completed')}
          >
            Completed
          </button>
          <button
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'in_progress' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('in_progress')}
          >
            In Progress
          </button>
          <button
            className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'pending' ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'}`}
            onClick={() => setActiveTab('pending')}
          >
            Pending
          </button>
        </nav>
      </div>

      {/* Real-time Status Indicator */}
      <div className="flex items-center gap-2 text-sm text-gray-600 mb-4">
        <div className={`w-2 h-2 rounded-full ${websocket?.readyState === WebSocket.OPEN ? 'bg-green-500' : 'bg-red-500'}`}></div>
        {websocket?.readyState === WebSocket.OPEN ? 'Real-time updates active' : 'Connecting to real-time updates...'}
      </div>


      {/* Computations Grid */}
      {filteredComputations.length === 0 ? (
        <div className="text-center py-12">
          <Activity className="w-16 h-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No computations yet</h3>
          <p className="text-gray-600 mb-4">Start your first secure computation to begin collaborative analysis</p>
          <button
            onClick={initializeComputation}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Create First Computation
          </button>
        </div>
      ) : (
        <>
        {/* Bulk delete quick action for Test Hospital */}
        {getDeletableByCreator('Test Hospital').length > 0 && (
          <div className="mb-4 flex items-center justify-end">
            <button
              onClick={() => handleBulkDeleteByCreator('Test Hospital')}
              className="inline-flex items-center gap-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
              title="Delete all deletable computations created by Test Hospital"
            >
              <Trash2 className="w-4 h-4" />
              Delete Test Hospital items ({getDeletableByCreator('Test Hospital').length})
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredComputations.map((computation) => (
            <div
              key={computation.computation_id}
              className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
            >
              {/* Header */}
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center gap-2">
                  {getStatusIcon(computation.status)}
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(computation.status)}`}>
                    {computation.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(computation.created_at).toLocaleDateString()}
                </span>
              </div>

              {/* Computation Info */}
              <div className="space-y-3">
                <div>
                  <h3 className="font-semibold text-gray-900">Computation {computation.computation_id.slice(0, 8)}...</h3>
                  <p className="text-sm text-gray-600">{computation.type}</p>
                  {/* Creator Information */}
                  <div className="mt-1">
                    {computation.org_id === user?.id ? (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        Created by you
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                        Created by {computation.creator_name || `Organization ${computation.org_id}`}
                      </span>
                    )}
                  </div>
                </div>

                {/* Progress */}
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <div className="flex items-center gap-1">
                      <span className="text-gray-600">Participants</span>
                      <button 
                        onClick={() => toggleParticipantsView(computation.computation_id)}
                        className="p-1 hover:bg-gray-100 rounded-full"
                      >
                        {showParticipants[computation.computation_id] ? <UserMinus className="w-3 h-3" /> : <UserPlus className="w-3 h-3" />}
                      </button>
                    </div>
                    <span className="font-medium">{computation.participants_count || 0}</span>
                  </div>
                  
                  {/* Active Participants List */}
                  {showParticipants[computation.computation_id] && activeParticipants[computation.computation_id] && (
                    <div className="mt-2 mb-3 bg-gray-50 p-2 rounded-md text-xs">
                      <div className="font-medium mb-1 text-gray-700 flex items-center gap-1">
                        <Users className="w-3 h-3" /> Active Participants ({activeParticipants[computation.computation_id].length})
                      </div>
                      <ul className="space-y-1">
                        {activeParticipants[computation.computation_id].length > 0 ? (
                          activeParticipants[computation.computation_id].map((participant, index) => (
                            <li key={participant.id || participant.org_id || `participant-${index}`} className="flex justify-between">
                              <span>{participant.name || participant.organization_name || `Organization ${participant.org_id}`}</span>
                              <span className="text-green-600 font-medium">{participant.status}</span>
                            </li>
                          ))
                        ) : (
                          <li className="text-gray-500">No active participants</li>
                        )}
                      </ul>
                    </div>
                  )}
                  
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Submissions</span>
                    <span className="font-medium">{computation.submissions_count || 0}</span>
                  </div>
                  {computation.participants_count > 0 && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.min(100, ((computation.submissions_count || 0) / computation.participants_count) * 100)}%`
                        }}
                      ></div>
                    </div>
                  )}
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-4">
                  <Link
                    href={`/secure-computations/${computation.computation_id}`}
                    className="flex-1 flex items-center justify-center gap-2 bg-gray-100 text-gray-700 px-3 py-2 rounded-lg hover:bg-gray-200 transition-colors text-sm"
                  >
                    <Eye className="w-4 h-4" />
                    View
                  </Link>
                  
                  
                  {computation.status === 'waiting_for_data' && (
                    <Link
                      href={`/secure-computations/${computation.computation_id}`}
                      className="flex-1 flex items-center justify-center gap-2 bg-blue-600 text-white px-3 py-2 rounded-lg hover:bg-blue-700 transition-colors text-sm"
                    >
                      <Play className="w-4 h-4" />
                      Submit Data
                    </Link>
                  )}
                  {computation.status === 'completed' && (
                    <>
                      <Link
                        href={`/secure-computations/${computation.computation_id}/results`}
                        className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                      >
                        <BarChart3 className="w-4 h-4" />
                        Results
                      </Link>
                      <button
                        onClick={() => secureComputationService.exportResults(computation.computation_id, 'json', user?.token)}
                        className="flex-1 flex items-center justify-center gap-2 bg-gray-600 text-white px-3 py-2 rounded-lg hover:bg-gray-700 transition-colors text-sm"
                      >
                        <Download className="w-4 h-4" />
                        Export
                      </button>
                    </>
                  )}
                  {/* Delete button - show for waiting/initialized/error computations */}
                  {['waiting_for_participants', 'initialized', 'waiting_for_data', 'error'].includes(computation.status) && (
                    <button
                      onClick={() => setDeleteConfirmation(computation.computation_id)}
                      className="flex items-center justify-center gap-2 bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                      title="Delete computation"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
        </>
      )}

      {/* Secure Computation Wizard */}
      {showNewComputationModal && (
        <SecureComputationWizard 
          user={user}
          onClose={() => setShowNewComputationModal(false)}
          onComputationCreated={fetchComputations}
        />
      )}

      {/* Pending Requests Modal */}
      {showPendingRequestsModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col">
            <div className="p-4 border-b border-gray-200 flex justify-between items-center">
              <h1 className="text-xl font-bold text-blue-700">Pending Computation Requests</h1>
              <button
                onClick={() => setShowPendingRequestsModal(false)}
                className="text-gray-500 hover:text-gray-700 focus:outline-none transition-colors"
              >
                <X size={20} />
              </button>
            </div>
            <div className="p-6 overflow-y-auto">
              {pendingRequests.length === 0 ? (
                <div className="text-center py-12">
                  <Bell className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No pending requests</h3>
                  <p className="text-gray-600">You don't have any pending computation requests from other organizations.</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {pendingRequests.map((request) => (
                    <div key={request.computation_id} className="bg-white rounded-lg shadow-md border border-gray-200 overflow-hidden">
                      <div className="bg-yellow-50 px-4 py-3 border-b border-yellow-100">
                        <div className="flex justify-between items-center">
                          <span className="font-medium text-yellow-800">Request from {request.requester_org}</span>
                          <span className="bg-yellow-200 text-yellow-800 text-xs px-2 py-1 rounded-full">Pending</span>
                        </div>
                      </div>
                      <div className="p-4">
                        <h3 className="font-semibold text-lg mb-2">{request.title || `Computation ${request.computation_id.slice(0, 8)}...`}</h3>
                        <p className="text-gray-600 text-sm mb-4">{request.description || 'No description provided'}</p>
                        
                        <div className="space-y-3 mb-4">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Computation Type</span>
                            <span className="font-medium">{request.computation_type || 'health_statistics'}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Security Method</span>
                            <span className="font-medium">{request.security_method || 'standard'}</span>
                          </div>
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Requested At</span>
                            <span className="font-medium">{new Date(request.created_at).toLocaleString()}</span>
                          </div>
                        </div>
                        
                        <div className="flex gap-2 pt-2">
                          <button
                            onClick={() => handleAcceptRequest(request.computation_id)}
                            className="flex-1 flex items-center justify-center gap-2 bg-green-600 text-white px-3 py-2 rounded-lg hover:bg-green-700 transition-colors text-sm"
                          >
                            <Check className="w-4 h-4" />
                            Accept
                          </button>
                          <button
                            onClick={() => handleDeclineRequest(request.computation_id)}
                            className="flex-1 flex items-center justify-center gap-2 bg-red-600 text-white px-3 py-2 rounded-lg hover:bg-red-700 transition-colors text-sm"
                          >
                            <X className="w-4 h-4" />
                            Decline
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="p-6">
              <div className="flex items-center mb-4">
                <div className="flex-shrink-0">
                  <Trash2 className="w-6 h-6 text-red-600" />
                </div>
                <div className="ml-3">
                  <h3 className="text-lg font-medium text-gray-900">Delete Computation</h3>
                </div>
              </div>
              <div className="mb-4">
                <p className="text-sm text-gray-500">
                  Are you sure you want to delete computation <strong>{deleteConfirmation.slice(0, 8)}...</strong>? 
                </p>
                <p className="text-sm text-gray-500 mt-2">
                  This will permanently remove the computation and all associated invitations. This action cannot be undone.
                </p>
              </div>
              <div className="flex justify-end space-x-3">
                <button
                  onClick={() => setDeleteConfirmation(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleDeleteComputation(deleteConfirmation)}
                  className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
    </>
  );
};

export default SecureComputationDashboard;