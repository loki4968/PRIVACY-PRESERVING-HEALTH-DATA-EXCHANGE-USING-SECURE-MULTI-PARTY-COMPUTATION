import React, { useState, useEffect, useCallback } from 'react';
import { Container, Card, Button, Alert, Badge, ListGroup } from 'react-bootstrap';
import { useAuth } from '../contexts/AuthContext';

/**
 * Test component for Federated Learning WebSocket functionality
 * This component can be used to test the WebSocket connection and message handling
 */
const FederatedWebSocketTest = () => {
  const { currentUser } = useAuth();
  
  // WebSocket state
  const [websocket, setWebsocket] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState('disconnected');
  const [lastActivity, setLastActivity] = useState(null);
  const [pingStatus, setPingStatus] = useState({ lastPong: null, latency: null });
  const [messages, setMessages] = useState([]);
  const [error, setError] = useState('');
  
  // Connect to WebSocket
  const connectWebSocket = useCallback(() => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No authentication token found');
        return;
      }
      
      // Close existing connection if any
      if (websocket) {
        websocket.close();
      }
      
      // Create WebSocket URL with user info
      const wsUrl = `${process.env.REACT_APP_WS_URL || 'ws://localhost:8000'}/ws/federated?token=${token}`;
      
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        setConnectionStatus('connected');
        setLastActivity(new Date());
        setError('');
        addMessage('System', 'Connected to WebSocket server');
        
        // Send a ping immediately after connection
        sendPing();
        
        // Request federated models
        ws.send(JSON.stringify({ type: 'get_federated_models' }));
      };
      
      ws.onmessage = (event) => {
        setLastActivity(new Date());
        handleWebSocketMessage(event.data);
      };
      
      ws.onerror = (error) => {
        setError(`WebSocket error: ${error.message}`);
        setConnectionStatus('error');
      };
      
      ws.onclose = (event) => {
        setConnectionStatus('disconnected');
        addMessage('System', `Disconnected from WebSocket server: ${event.reason || 'Unknown reason'}`);
      };
      
      setWebsocket(ws);
    } catch (err) {
      setError(`Failed to connect: ${err.message}`);
      setConnectionStatus('error');
    }
  }, [websocket]);
  
  // Handle incoming WebSocket messages
  const handleWebSocketMessage = (data) => {
    try {
      const message = JSON.parse(data);
      
      // Add message to the list
      addMessage('Received', JSON.stringify(message, null, 2));
      
      // Handle different message types
      switch (message.type) {
        case 'federated_models':
          // Handle federated models list
          break;
          
        case 'model_update':
          // Handle model update notification
          break;
          
        case 'aggregation_result':
          // Handle aggregation result
          break;
          
        case 'pong':
          // Calculate latency
          if (message.timestamp) {
            const sentTime = new Date(message.timestamp);
            const receivedTime = new Date();
            const latency = receivedTime - sentTime;
            
            setPingStatus({
              lastPong: receivedTime,
              latency: latency
            });
          }
          break;
          
        case 'connection_health':
          // Update connection health status
          break;
          
        case 'system_notification':
          // Handle system notification
          break;
          
        default:
          // Unknown message type
          break;
      }
    } catch (err) {
      setError(`Failed to parse message: ${err.message}`);
    }
  };
  
  // Send a ping message
  const sendPing = () => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      const pingMessage = {
        type: 'ping',
        timestamp: new Date().toISOString()
      };
      
      websocket.send(JSON.stringify(pingMessage));
      addMessage('Sent', JSON.stringify(pingMessage, null, 2));
    }
  };
  
  // Add a message to the messages list
  const addMessage = (direction, content) => {
    setMessages(prevMessages => [
      {
        id: Date.now(),
        timestamp: new Date().toISOString(),
        direction,
        content
      },
      ...prevMessages
    ].slice(0, 50)); // Keep only the last 50 messages
  };
  
  // Send a test message
  const sendTestMessage = (type) => {
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      let message = { type };
      
      switch (type) {
        case 'get_federated_models':
          // No additional data needed
          break;
          
        case 'join_training':
          message.training_id = prompt('Enter training ID:');
          if (!message.training_id) return;
          break;
          
        case 'leave_training':
          message.training_id = prompt('Enter training ID:');
          if (!message.training_id) return;
          break;
          
        default:
          // Default message
          break;
      }
      
      websocket.send(JSON.stringify(message));
      addMessage('Sent', JSON.stringify(message, null, 2));
    } else {
      setError('WebSocket is not connected');
    }
  };
  
  // Connect on component mount
  useEffect(() => {
    connectWebSocket();
    
    // Cleanup on unmount
    return () => {
      if (websocket) {
        websocket.close();
      }
    };
  }, [connectWebSocket]);
  
  return (
    <Container className="mt-4">
      <Card>
        <Card.Header as="h5">Federated Learning WebSocket Test</Card.Header>
        <Card.Body>
          <div className="mb-3">
            <Badge bg={connectionStatus === 'connected' ? 'success' : connectionStatus === 'error' ? 'danger' : 'secondary'} className="me-2">
              {connectionStatus}
            </Badge>
            
            {lastActivity && (
              <small className="text-muted">
                Last activity: {lastActivity.toLocaleTimeString()}
              </small>
            )}
            
            {pingStatus.lastPong && (
              <small className="text-muted ms-3">
                Latency: {pingStatus.latency}ms
              </small>
            )}
          </div>
          
          {error && <Alert variant="danger">{error}</Alert>}
          
          <div className="mb-3">
            <Button variant="primary" onClick={connectWebSocket} className="me-2">
              Reconnect
            </Button>
            <Button variant="secondary" onClick={sendPing} className="me-2">
              Send Ping
            </Button>
            <Button variant="info" onClick={() => sendTestMessage('get_federated_models')} className="me-2">
              Get Models
            </Button>
            <Button variant="info" onClick={() => sendTestMessage('join_training')} className="me-2">
              Join Training
            </Button>
            <Button variant="info" onClick={() => sendTestMessage('leave_training')}>
              Leave Training
            </Button>
          </div>
          
          <h6>Message Log:</h6>
          <ListGroup className="message-log" style={{ maxHeight: '400px', overflowY: 'auto' }}>
            {messages.map(msg => (
              <ListGroup.Item key={msg.id} className={msg.direction === 'Sent' ? 'bg-light' : ''}>
                <div className="d-flex justify-content-between">
                  <Badge bg={msg.direction === 'Sent' ? 'primary' : msg.direction === 'System' ? 'secondary' : 'success'}>
                    {msg.direction}
                  </Badge>
                  <small className="text-muted">{new Date(msg.timestamp).toLocaleTimeString()}</small>
                </div>
                <pre className="mt-2 mb-0" style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</pre>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Card.Body>
      </Card>
    </Container>
  );
};

export default FederatedWebSocketTest;