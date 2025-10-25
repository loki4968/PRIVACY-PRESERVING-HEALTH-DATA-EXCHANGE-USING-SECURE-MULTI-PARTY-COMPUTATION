from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set, List, Optional, Any, Tuple
import json
import asyncio
import logging
import time
from datetime import datetime, timedelta
from enum import Enum

# Configure logging
logger = logging.getLogger("websocket")
# Set logging level to reduce noise from ping messages
logger.setLevel(logging.WARNING)


class MessageType(Enum):
    COMPUTATION_STATUS = "computation_status"
    PARTICIPANT_JOINED = "participant_joined"
    PARTICIPANT_LEFT = "participant_left"
    DATA_SUBMITTED = "data_submitted"
    COMPUTATION_COMPLETED = "computation_completed"
    ERROR = "error"
    METRICS_UPDATE = "metrics_update"
    CONNECTION_HEALTH = "connection_health"
    RECONNECT = "reconnect"
    SYSTEM_NOTIFICATION = "system_notification"
    PENDING_REQUEST = "pending_request"
    REQUEST_EXPIRING_SOON = "request_expiring_soon"
    
    # Federated Learning message types
    FEDERATED_MODELS = "federated_models"
    MODEL_UPDATE = "model_update"
    AGGREGATION_RESULT = "aggregation_result"
    JOIN_TRAINING = "join_training"
    LEAVE_TRAINING = "leave_training"
    
    # Heartbeat message types
    PING = "ping"
    PONG = "pong"
    HEARTBEAT = "heartbeat"
    HEARTBEAT_ACK = "heartbeat_ack"

class ConnectionState(Enum):
    CONNECTED = "connected"
    UNSTABLE = "unstable"
    RECONNECTING = "reconnecting"
    DISCONNECTED = "disconnected"

class SMPCWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.computation_rooms: Dict[str, Set[WebSocket]] = {}
        self.user_computations: Dict[int, List[str]] = {}
        self.connection_health: Dict[WebSocket, datetime] = {}
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.connection_state: Dict[WebSocket, ConnectionState] = {}
        self.message_queue: Dict[Tuple[int, str], List[Dict[str, Any]]] = {}  # (org_id, computation_id) -> messages
        self.heartbeat_intervals: Dict[WebSocket, float] = {}  # WebSocket -> seconds
        self.missed_heartbeats: Dict[WebSocket, int] = {}  # WebSocket -> count
        self.background_task = None
        self.health_check_task = None
        self.heartbeat_task = None
        self.expiring_requests_task = None
        
        # Configuration
        self.heartbeat_interval = 15  # seconds
        self.heartbeat_timeout = 45  # seconds
        self.max_missed_heartbeats = 3
        self.connection_timeout = 120  # seconds
        self.health_check_interval = 30  # seconds
        self.queue_max_size = 100  # maximum number of messages to queue per computation

    async def connect(self, websocket: WebSocket, org_id: int, client_info: Optional[Dict] = None):
        await websocket.accept()
        
        # Store connection metadata
        metadata = client_info or {}
        current_time = datetime.utcnow()
        metadata.update({
            "org_id": org_id,
            "connected_at": current_time,
            "last_activity": current_time,
            "client_ip": "127.0.0.1",  # Use a fixed value since we can't reliably get client IP
            "reconnect_count": 0,
            "latency_ms": 0
        })
        self.connection_metadata[websocket] = metadata
        
        # Add to active connections
        if org_id not in self.active_connections:
            self.active_connections[org_id] = set()
        self.active_connections[org_id].add(websocket)
        
        # Track connection health and state
        self.connection_health[websocket] = current_time
        self.connection_state[websocket] = ConnectionState.CONNECTED
        self.heartbeat_intervals[websocket] = self.heartbeat_interval
        self.missed_heartbeats[websocket] = 0
        
        # Start background tasks if not already running
        if not self.background_task:
            self.background_task = asyncio.create_task(self.broadcast_metrics())
            
        if not self.health_check_task:
            self.health_check_task = asyncio.create_task(self.monitor_connection_health())
            
        if not self.heartbeat_task:
            self.heartbeat_task = asyncio.create_task(self.send_heartbeats())
            
        # Start expiring requests check task
        if not self.expiring_requests_task:
            self.expiring_requests_task = asyncio.create_task(self.check_expiring_requests())
            
        # Send welcome message
        welcome_data = {
            "message": "Connected to Health Data Exchange WebSocket",
            "org_id": org_id,
            "active_computations": self.user_computations.get(org_id, []),
            "heartbeat_interval": self.heartbeat_interval,
            "connection_id": id(websocket)  # Use object id as a unique identifier
        }
        await websocket.send_text(json.dumps({
            "type": MessageType.SYSTEM_NOTIFICATION.value,
            "data": welcome_data,
            "timestamp": current_time.isoformat()
        }))
        
        # Send initial heartbeat
        await self.send_heartbeat(websocket)
        
        # Deliver any queued messages
        await self.deliver_queued_messages(org_id)
        
        logger.info(f"WebSocket connection established for organization {org_id}")

    def update_connection_activity(self, websocket: WebSocket):
        """Update the last activity timestamp for a connection"""
        current_time = datetime.utcnow()
        if websocket in self.connection_health:
            self.connection_health[websocket] = current_time
            
        if websocket in self.connection_state:
            # Reset missed heartbeats when we see activity
            self.missed_heartbeats[websocket] = 0
            
            # Update connection state if it was unstable
            if self.connection_state[websocket] == ConnectionState.UNSTABLE:
                self.connection_state[websocket] = ConnectionState.CONNECTED
                logger.info(f"Connection restored to stable for {self.get_connection_identifier(websocket)}")
            
    def get_connection_identifier(self, websocket: WebSocket) -> str:
        """Get a human-readable identifier for a connection"""
        metadata = self.connection_metadata.get(websocket, {})
        org_id = metadata.get("org_id", "unknown")
        return f"org_id={org_id}, conn_id={id(websocket)}"
            
    def disconnect(self, websocket: WebSocket, org_id: int):
        # Log the disconnection
        logger.info(f"Disconnecting WebSocket for {self.get_connection_identifier(websocket)}")
        
        # Clean up connection tracking
        if websocket in self.connection_health:
            del self.connection_health[websocket]
            
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
            
        if websocket in self.connection_state:
            del self.connection_state[websocket]
            
        if websocket in self.heartbeat_intervals:
            del self.heartbeat_intervals[websocket]
            
        if websocket in self.missed_heartbeats:
            del self.missed_heartbeats[websocket]
        
        # Remove from active connections
        if org_id in self.active_connections:
            self.active_connections[org_id].discard(websocket)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]

        # Remove from computation rooms
        for computation_id, connections in list(self.computation_rooms.items()):
            connections.discard(websocket)
            if not connections:
                del self.computation_rooms[computation_id]
                
        logger.info(f"WebSocket connection closed for organization {org_id}")

    async def join_computation_room(self, websocket: WebSocket, computation_id: str, org_id: int):
        """Join a specific computation room for real-time updates"""
        if computation_id not in self.computation_rooms:
            self.computation_rooms[computation_id] = set()
        self.computation_rooms[computation_id].add(websocket)
        
        # Track user's computations
        if org_id not in self.user_computations:
            self.user_computations[org_id] = []
        if computation_id not in self.user_computations[org_id]:
            self.user_computations[org_id].append(computation_id)

        # Notify others in the room
        await self.broadcast_to_computation(
            computation_id,
            MessageType.PARTICIPANT_JOINED,
            {"org_id": org_id, "computation_id": computation_id}
        )

    async def leave_computation_room(self, websocket: WebSocket, computation_id: str, org_id: int):
        """Leave a computation room"""
        if computation_id in self.computation_rooms:
            self.computation_rooms[computation_id].discard(websocket)
            if not self.computation_rooms[computation_id]:
                del self.computation_rooms[computation_id]

        # Notify others in the room
        await self.broadcast_to_computation(
            computation_id,
            MessageType.PARTICIPANT_LEFT,
            {"org_id": org_id, "computation_id": computation_id}
        )

    def _validate_message_data(self, data: dict) -> bool:
        """Validate message data for security"""
        try:
            # Check data size (prevent DoS)
            if len(json.dumps(data)) > 10000:  # 10KB limit
                return False
            
            # Check for suspicious content
            data_str = json.dumps(data).lower()
            suspicious_patterns = ['<script', 'javascript:', 'eval(', 'function(']
            
            for pattern in suspicious_patterns:
                if pattern in data_str:
                    return False
            
            return True
        except Exception:
            return False
    
    def _sanitize_message_data(self, data: dict) -> dict:
        """Sanitize message data"""
        if not isinstance(data, dict):
            return {}
        
        # Remove potentially dangerous keys
        dangerous_keys = ['__proto__', 'constructor', 'prototype']
        sanitized = {}
        
        for key, value in data.items():
            if key not in dangerous_keys and isinstance(key, str):
                if isinstance(value, str):
                    # Basic XSS prevention
                    value = value.replace('<', '&lt;').replace('>', '&gt;')
                    sanitized[key] = value[:1000]  # Limit string length
                elif isinstance(value, (int, float, bool)):
                    sanitized[key] = value
                elif isinstance(value, dict):
                    sanitized[key] = self._sanitize_message_data(value)
                elif isinstance(value, list) and len(value) < 100:  # Limit array size
                    sanitized[key] = value[:100]
        
        return sanitized

    async def broadcast_to_organization(self, org_id: int, message_type: MessageType, data: dict):
        """Broadcast message to all connections of an organization with security validation"""
        if org_id in self.active_connections:
            # Validate and sanitize message data
            if not self._validate_message_data(data):
                logger.warning(f"Invalid message data blocked for org {org_id}")
                return
            
            sanitized_data = self._sanitize_message_data(data)
            
            message = {
                "type": message_type.value,
                "data": sanitized_data,
                "timestamp": datetime.utcnow().isoformat(),
                "message_id": f"{int(time.time())}-{org_id}"  # Simple message ID
            }
            
            disconnected = set()
            for connection in self.active_connections[org_id]:
                try:
                    # Check connection state before sending
                    if connection.client_state.name == 'DISCONNECTED':
                        disconnected.add(connection)
                        continue
                    
                    await connection.send_text(json.dumps(message))
                except WebSocketDisconnect:
                    disconnected.add(connection)
                except Exception as e:
                    logger.warning(f"Error sending message to organization {org_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections[org_id].discard(connection)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]

    async def broadcast_to_computation(self, computation_id: str, message_type: MessageType, data: dict):
        """Broadcast a message to all participants in a computation room with security validation"""
        if computation_id in self.computation_rooms:
            # Validate and sanitize message data
            if not self._validate_message_data(data):
                logger.warning(f"Invalid message data blocked for computation {computation_id}")
                return
            
            sanitized_data = self._sanitize_message_data(data)
            
            connections = self.computation_rooms[computation_id]
            current_time = datetime.utcnow()
            message = {
                "type": message_type.value,
                "data": sanitized_data,
                "timestamp": current_time.isoformat(),
                "computation_id": computation_id,
                "message_id": f"{int(time.time())}-{computation_id[:8]}"
            }
            
            # Track which organizations received the message
            delivered_to_orgs = set()
            failed_orgs = set()
            
            # Try to deliver to all connected participants
            for websocket in connections:
                try:
                    metadata = self.connection_metadata.get(websocket, {})
                    org_id = metadata.get("org_id")
                    
                    if not org_id:
                        continue
                        
                    # Check connection state
                    conn_state = self.connection_state.get(websocket, ConnectionState.CONNECTED)
                    if conn_state != ConnectionState.CONNECTED:
                        # Queue message for delivery when reconnected
                        await self.queue_message(org_id, computation_id, message_type, data)
                        failed_orgs.add(org_id)
                        continue
                    
                    # Send message to connected client
                    await websocket.send_text(json.dumps(message))
                    delivered_to_orgs.add(org_id)
                    
                    # Update connection activity
                    self.update_connection_activity(websocket)
                except Exception as e:
                    # Log error and queue message for later delivery
                    metadata = self.connection_metadata.get(websocket, {})
                    org_id = metadata.get("org_id")
                    
                    if org_id:
                        logger.warning(f"Failed to send message to {self.get_connection_identifier(websocket)}: {e}")
                        await self.queue_message(org_id, computation_id, message_type, data)
                        failed_orgs.add(org_id)
            
            # Log delivery statistics
            logger.info(f"Broadcast to computation {computation_id}: delivered to {len(delivered_to_orgs)} orgs, "
                       f"queued for {len(failed_orgs)} orgs")

    async def broadcast_to_organization(self, org_id: int, message_type: MessageType, data: dict):
        """Broadcast a message to all connections for an organization"""
        if org_id in self.active_connections:
            connections = self.active_connections[org_id]
            current_time = datetime.utcnow()
            message = {
                "type": message_type.value,
                "data": data,
                "timestamp": current_time.isoformat()
            }
            
            # Track delivery success
            delivered = False
            
            # Try to deliver to all connections for this org
            for websocket in connections:
                try:
                    # Check if connection is still open
                    if websocket.client_state.name == 'DISCONNECTED':
                        continue
                        
                    # Check connection state
                    conn_state = self.connection_state.get(websocket, ConnectionState.CONNECTED)
                    if conn_state != ConnectionState.CONNECTED:
                        continue
                    
                    # Send message
                    await websocket.send_text(json.dumps(message))
                    delivered = True
                    
                    # Update connection activity
                    self.update_connection_activity(websocket)
                except Exception as e:
                    # Don't log errors for closed connections
                    pass
            
            # If message couldn't be delivered to any connection, queue it
            if not delivered and message_type not in [
                MessageType.PING, MessageType.PONG, 
                MessageType.HEARTBEAT, MessageType.HEARTBEAT_ACK,
                MessageType.CONNECTION_HEALTH
            ]:
                # Find computations for this org and queue message
                computations = self.user_computations.get(org_id, [])
                if computations:
                    # Queue for the first computation (arbitrary choice)
                    await self.queue_message(org_id, computations[0], message_type, data)
                    logger.info(f"Queued message for org_id={org_id} (no active connections)")

    async def notify_computation_status(self, computation_id: str, status: str, result=None):
        """Notify all participants about computation status changes"""
        data = {
            "computation_id": computation_id,
            "status": status
        }
        
        if result is not None:
            data["result"] = result
            
        # Get all organizations participating in this computation
        participating_orgs = set()
        for org_id, computations in self.user_computations.items():
            if computation_id in computations:
                participating_orgs.add(org_id)
        
        # Broadcast to computation room
        await self.broadcast_to_computation(computation_id, MessageType.COMPUTATION_STATUS, data)
        
        # Also queue for any organizations not currently in the room
        for org_id in participating_orgs:
            # Check if org has active connections in the computation room
            org_in_room = False
            if computation_id in self.computation_rooms:
                for websocket in self.computation_rooms[computation_id]:
                    metadata = self.connection_metadata.get(websocket, {})
                    if metadata.get("org_id") == org_id:
                        org_in_room = True
                        break
            
            # Queue message if org not in room
            if not org_in_room:
                await self.queue_message(org_id, computation_id, MessageType.COMPUTATION_STATUS, data)
                logger.info(f"Queued computation status update for org_id={org_id}, computation_id={computation_id}")

    async def notify_data_submitted(self, computation_id: str, org_id: int):
        """Notify all participants that an organization has submitted data"""
        data = {
            "computation_id": computation_id,
            "org_id": org_id
        }
        
        # Broadcast to computation room
        await self.broadcast_to_computation(computation_id, MessageType.DATA_SUBMITTED, data)
        
        # Queue for any organizations not in the room
        participating_orgs = set()
        for participant_id, computations in self.user_computations.items():
            if computation_id in computations:
                participating_orgs.add(participant_id)
        
        for participant_id in participating_orgs:
            # Skip the organization that submitted the data
            if participant_id == org_id:
                continue
                
            # Check if org has active connections in the computation room
            org_in_room = False
            if computation_id in self.computation_rooms:
                for websocket in self.computation_rooms[computation_id]:
                    metadata = self.connection_metadata.get(websocket, {})
                    if metadata.get("org_id") == participant_id:
                        org_in_room = True
                        break
            
            # Queue message if org not in room
            if not org_in_room:
                await self.queue_message(participant_id, computation_id, MessageType.DATA_SUBMITTED, data)

    async def notify_computation_completed(self, computation_id: str, result: dict = None, result_summary: dict = None):
        """Notify all participants that a computation has completed"""
        # Handle both 'result' and 'result_summary' parameter names for backward compatibility
        computation_result = result if result is not None else result_summary
        if computation_result is None:
            raise ValueError("Either 'result' or 'result_summary' must be provided")
            
        data = {
            "computation_id": computation_id,
            "result": computation_result
        }
        
        # Broadcast to computation room
        await self.broadcast_to_computation(computation_id, MessageType.COMPUTATION_COMPLETED, data)
        
        # Queue for any organizations not in the room
        participating_orgs = set()
        for org_id, computations in self.user_computations.items():
            if computation_id in computations:
                participating_orgs.add(org_id)
        
        for org_id in participating_orgs:
            # Check if org has active connections in the computation room
            org_in_room = False
            if computation_id in self.computation_rooms:
                for websocket in self.computation_rooms[computation_id]:
                    metadata = self.connection_metadata.get(websocket, {})
                    if metadata.get("org_id") == org_id:
                        org_in_room = True
                        break
            
            # Queue message if org not in room
            if not org_in_room:
                await self.queue_message(org_id, computation_id, MessageType.COMPUTATION_COMPLETED, data)
                logger.info(f"Queued computation completion notification for org_id={org_id}, computation_id={computation_id}")

    async def check_expiring_requests(self):
        """Background task to periodically check for expiring computation requests"""
        while True:
            try:
                # Import here to avoid circular imports
                from secure_computation import secure_computation_service
                
                # Check for expiring requests
                await secure_computation_service.check_expiring_requests()
                
                # Check every 6 hours
                await asyncio.sleep(6 * 60 * 60)
            except Exception as e:
                logger.error(f"Error in check_expiring_requests: {e}")
                await asyncio.sleep(30 * 60)  # Wait 30 minutes before retrying
    
    async def broadcast_metrics(self):
        """Background task to periodically broadcast metric updates"""
        while True:
            try:
                for org_id in list(self.active_connections.keys()):
                    # In a real implementation, you would fetch actual metrics from your database
                    # This is just a demo that sends simulated data
                    metrics = {
                        "blood_pressure": {
                            "latest": 120,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        "blood_sugar": {
                            "latest": 100,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        "heart_rate": {
                            "latest": 75,
                            "timestamp": datetime.utcnow().isoformat()
                        },
                        "active_connections": len(self.active_connections.get(org_id, set())),
                        "active_computations": len(self.user_computations.get(org_id, []))
                    }
                    
                    await self.broadcast_to_organization(
                        org_id,
                        MessageType.METRICS_UPDATE,
                        metrics
                    )
                
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in broadcast_metrics: {e}")
                await asyncio.sleep(5)  # Wait before retrying
                
    async def send_heartbeats(self):
        """Send periodic heartbeats to all connected clients"""
        while True:
            try:
                current_time = datetime.utcnow()
                
                # Send heartbeats to all active connections
                for websocket in list(self.connection_health.keys()):
                    try:
                        # Only send heartbeats to connections that haven't had activity recently
                        last_active = self.connection_health.get(websocket)
                        if not last_active:
                            continue
                            
                        time_diff = (current_time - last_active).total_seconds()
                        if time_diff >= self.heartbeat_interval:
                            await self.send_heartbeat(websocket)
                    except Exception as e:
                        logger.warning(f"Error sending heartbeat to {self.get_connection_identifier(websocket)}: {e}")
                
                await asyncio.sleep(self.heartbeat_interval / 2)  # Check at half the heartbeat interval
            except Exception as e:
                logger.error(f"Error in send_heartbeats: {e}")
                await asyncio.sleep(self.heartbeat_interval / 2)  # Wait before retrying
    
    async def send_heartbeat(self, websocket: WebSocket):
        """Send a heartbeat message to a specific client"""
        try:
            # Check if connection is still open before sending
            if websocket.client_state.name == 'DISCONNECTED':
                return
                
            current_time = datetime.utcnow()
            heartbeat_data = {
                "timestamp": current_time.timestamp(),
                "sequence": self.missed_heartbeats.get(websocket, 0)
            }
            
            await websocket.send_text(json.dumps({
                "type": MessageType.HEARTBEAT.value,
                "data": heartbeat_data,
                "timestamp": current_time.isoformat()
            }))
            
            # Increment missed heartbeats counter
            self.missed_heartbeats[websocket] = self.missed_heartbeats.get(websocket, 0) + 1
            
            # Update connection state if too many missed heartbeats
            if self.missed_heartbeats[websocket] > 1:
                self.connection_state[websocket] = ConnectionState.UNSTABLE
        except Exception as e:
            # Don't log errors for closed connections
            pass
    
    async def handle_heartbeat_ack(self, websocket: WebSocket, message: dict):
        """Handle heartbeat acknowledgement from client"""
        try:
            # Calculate round-trip time
            current_time = datetime.utcnow()
            sent_timestamp = message.get("data", {}).get("timestamp", 0)
            if sent_timestamp:
                rtt_ms = int((current_time.timestamp() - float(sent_timestamp)) * 1000)
                
                # Update connection metadata with latency
                if websocket in self.connection_metadata:
                    self.connection_metadata[websocket]["latency_ms"] = rtt_ms
            
            # Reset missed heartbeats counter
            self.missed_heartbeats[websocket] = 0
            
            # Update connection activity
            self.update_connection_activity(websocket)
        except Exception as e:
            logger.error(f"Error handling heartbeat ack: {e}")

    async def monitor_connection_health(self):
        """Monitor connection health and clean up stale connections"""
        while True:
            try:
                current_time = datetime.utcnow()
                stale_connections = []
                unstable_connections = []
                
                # Check all connections
                for websocket, last_active in list(self.connection_health.items()):
                    time_diff = (current_time - last_active).total_seconds()
                    missed = self.missed_heartbeats.get(websocket, 0)
                    
                    # Determine connection state based on activity and missed heartbeats
                    if time_diff > self.connection_timeout:  # Complete timeout
                        stale_connections.append(websocket)
                    elif missed >= self.max_missed_heartbeats:  # Too many missed heartbeats
                        unstable_connections.append(websocket)
                    elif time_diff > self.health_check_interval:  # Send health check
                        try:
                            metadata = self.connection_metadata.get(websocket, {})
                            org_id = metadata.get("org_id")
                            
                            if org_id:
                                # Send connection health status
                                conn_state = self.connection_state.get(websocket, ConnectionState.CONNECTED)
                                health_data = {
                                    "status": conn_state.value,
                                    "connected_since": metadata.get("connected_at", current_time).isoformat(),
                                    "last_activity": last_active.isoformat(),
                                    "active_computations": len(self.user_computations.get(org_id, [])),
                                    "missed_heartbeats": missed,
                                    "latency_ms": metadata.get("latency_ms", 0)
                                }
                                
                                # Send health check only if connection is still open
                                if websocket.client_state.name not in ['DISCONNECTED', 'CLOSED']:
                                    try:
                                        await websocket.send_text(json.dumps({
                                            "type": MessageType.CONNECTION_HEALTH.value,
                                            "data": health_data,
                                            "timestamp": current_time.isoformat()
                                        }))
                                    except Exception:
                                        # Connection might be closed, mark as unstable
                                        unstable_connections.append(websocket)
                        except Exception as e:
                            logger.warning(f"Error sending health check to {self.get_connection_identifier(websocket)}: {e}")
                            unstable_connections.append(websocket)
                
                # Handle unstable connections - mark them for reconnection
                for websocket in unstable_connections:
                    if websocket in stale_connections:
                        continue  # Skip if already marked as stale
                        
                    try:
                        metadata = self.connection_metadata.get(websocket, {})
                        org_id = metadata.get("org_id")
                        
                        if org_id and websocket in self.connection_state:
                            # Mark as reconnecting
                            self.connection_state[websocket] = ConnectionState.RECONNECTING
                            
                            # Send reconnect message only if connection is still open
                            if websocket.client_state.name not in ['DISCONNECTED', 'CLOSED']:
                                try:
                                    await websocket.send_text(json.dumps({
                                        "type": MessageType.RECONNECT.value,
                                        "data": {
                                            "reason": "Connection unstable",
                                            "missed_heartbeats": self.missed_heartbeats.get(websocket, 0)
                                        },
                                        "timestamp": current_time.isoformat()
                                    }))
                                except Exception:
                                    # Connection might be closed, ignore the error
                                    pass
                            
                            logger.warning(f"Connection unstable for {self.get_connection_identifier(websocket)}, requesting reconnect")
                    except Exception as e:
                        logger.error(f"Error handling unstable connection: {e}")
                        stale_connections.append(websocket)
                
                # Clean up stale connections
                for websocket in stale_connections:
                    try:
                        metadata = self.connection_metadata.get(websocket, {})
                        org_id = metadata.get("org_id")
                        
                        if org_id:
                            # Check if connection is still open before trying to close
                            if websocket.client_state.name not in ['DISCONNECTED', 'CLOSED']:
                                try:
                                    await websocket.close(code=1001, reason="Connection timeout")
                                except Exception:
                                    # Connection might already be closed, ignore the error
                                    pass
                            self.disconnect(websocket, org_id)
                    except Exception as e:
                        # Still remove from our tracking even if close fails
                        metadata = self.connection_metadata.get(websocket, {})
                        org_id = metadata.get("org_id")
                        if org_id:
                            self.disconnect(websocket, org_id)
                
                await asyncio.sleep(15)  # Check every 15 seconds
            except Exception as e:
                logger.error(f"Error in monitor_connection_health: {e}")
                await asyncio.sleep(15)  # Wait before retrying

    async def handle_ping(self, websocket: WebSocket, message: dict):
        """Handle ping message and respond with pong"""
        try:
            # Get the client's timestamp or use current time
            client_timestamp = message.get("timestamp", datetime.utcnow().isoformat())
            current_time = datetime.utcnow()
            
            # Calculate round-trip time if client sent a numeric timestamp
            rtt_ms = 0
            if "data" in message and "sent_at" in message["data"]:
                try:
                    sent_at = float(message["data"]["sent_at"])
                    rtt_ms = int((current_time.timestamp() - sent_at) * 1000)
                    
                    # Update connection metadata with latency
                    if websocket in self.connection_metadata:
                        self.connection_metadata[websocket]["latency_ms"] = rtt_ms
                except (ValueError, TypeError):
                    pass
            
            # Send pong response
            await websocket.send_text(json.dumps({
                "type": MessageType.PONG.value,
                "data": {
                    "client_timestamp": client_timestamp,
                    "server_timestamp": current_time.timestamp(),
                    "rtt_ms": rtt_ms
                },
                "timestamp": current_time.isoformat()
            }))
            
            # Update connection activity
            self.update_connection_activity(websocket)
        except Exception as e:
            logger.error(f"Error handling ping from {self.get_connection_identifier(websocket)}: {e}")

    async def queue_message(self, org_id: int, computation_id: str, message_type: MessageType, data: Dict[str, Any]):
        """Queue a message for delivery when a client reconnects"""
        key = (org_id, computation_id)
        if key not in self.message_queue:
            self.message_queue[key] = []
            
        # Add message to queue with timestamp
        self.message_queue[key].append({
            "type": message_type.value,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
            "queued_at": datetime.utcnow().timestamp()
        })
        
        # Limit queue size
        if len(self.message_queue[key]) > self.queue_max_size:
            # Remove oldest messages
            self.message_queue[key] = self.message_queue[key][-self.queue_max_size:]
            
        logger.debug(f"Queued message for org_id={org_id}, computation_id={computation_id}, "
                    f"queue size={len(self.message_queue[key])}")
    
    async def notify_pending_request(self, org_id: int, computation_data: Dict[str, Any]):
        """Notify an organization about a pending computation request"""
        try:
            # Check if organization has active connections
            if org_id not in self.active_connections or not self.active_connections[org_id]:
                # Queue the notification for later delivery
                computation_id = computation_data.get("computation_id")
                if computation_id:
                    await self.queue_message(org_id, computation_id, MessageType.PENDING_REQUEST, computation_data)
                    logger.info(f"Queued pending request notification for org_id={org_id}, computation_id={computation_id}")
                return
            
            # Send notification to all active connections for this organization
            message = {
                "type": MessageType.PENDING_REQUEST.value,
                "data": computation_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Track delivery success
            delivered = False
            
            for websocket in self.active_connections[org_id]:
                try:
                    # Check connection state
                    conn_state = self.connection_state.get(websocket, ConnectionState.CONNECTED)
                    if conn_state != ConnectionState.CONNECTED:
                        continue
                    
                    # Send message
                    await websocket.send_text(json.dumps(message))
                    delivered = True
                    
                    # Update connection activity
                    self.update_connection_activity(websocket)
                except Exception as e:
                    logger.warning(f"Failed to send pending request notification to {self.get_connection_identifier(websocket)}: {e}")
            
            # If message couldn't be delivered to any connection, queue it
            if not delivered:
                computation_id = computation_data.get("computation_id")
                if computation_id:
                    await self.queue_message(org_id, computation_id, MessageType.PENDING_REQUEST, computation_data)
                    logger.info(f"Queued pending request notification for org_id={org_id}, computation_id={computation_id}")
        except Exception as e:
            logger.error(f"Error sending pending request notification to org_id={org_id}: {e}")
    
    async def notify_request_expiring_soon(self, org_id: int, computation_data: Dict[str, Any]):
        """Notify an organization about a computation request that will expire soon"""
        try:
            # Add expiration information to the data
            computation_data["expires_in_days"] = computation_data.get("expires_in_days", 1)
            computation_data["message"] = f"This computation request will expire in {computation_data['expires_in_days']} day(s)"
            
            # Check if organization has active connections
            if org_id not in self.active_connections or not self.active_connections[org_id]:
                # Queue the notification for later delivery
                computation_id = computation_data.get("computation_id")
                if computation_id:
                    await self.queue_message(org_id, computation_id, MessageType.REQUEST_EXPIRING_SOON, computation_data)
                    logger.info(f"Queued expiration notification for org_id={org_id}, computation_id={computation_id}")
                return
            
            # Send notification to all active connections for this organization
            message = {
                "type": MessageType.REQUEST_EXPIRING_SOON.value,
                "data": computation_data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Track delivery success
            delivered = False
            
            for websocket in self.active_connections[org_id]:
                try:
                    # Check connection state
                    conn_state = self.connection_state.get(websocket, ConnectionState.CONNECTED)
                    if conn_state != ConnectionState.CONNECTED:
                        continue
                    
                    # Send message
                    await websocket.send_text(json.dumps(message))
                    delivered = True
                    
                    # Update connection activity
                    self.update_connection_activity(websocket)
                except Exception as e:
                    logger.warning(f"Failed to send expiration notification to {self.get_connection_identifier(websocket)}: {e}")
            
            # If message couldn't be delivered to any connection, queue it
            if not delivered:
                computation_id = computation_data.get("computation_id")
                if computation_id:
                    await self.queue_message(org_id, computation_id, MessageType.REQUEST_EXPIRING_SOON, computation_data)
                    logger.info(f"Queued expiration notification for org_id={org_id}, computation_id={computation_id}")
        except Exception as e:
            logger.error(f"Error sending expiration notification to org_id={org_id}: {e}")
    
    async def deliver_queued_messages(self, org_id: int):
        """Deliver queued messages to a reconnected client"""
        # Find all queues for this org
        delivered_count = 0
        for (queue_org_id, computation_id), messages in list(self.message_queue.items()):
            if queue_org_id != org_id or not messages:
                continue
                
            # Get active connections for this org
            connections = self.active_connections.get(org_id, set())
            if not connections:
                continue
                
            # Send queued messages to all connections for this org
            for websocket in connections:
                try:
                    # Send notification about queued messages
                    await websocket.send_text(json.dumps({
                        "type": MessageType.SYSTEM_NOTIFICATION.value,
                        "data": {
                            "message": f"Delivering {len(messages)} queued messages for computation {computation_id}",
                            "computation_id": computation_id
                        },
                        "timestamp": datetime.utcnow().isoformat()
                    }))
                    
                    # Send each queued message
                    for message in messages:
                        await websocket.send_text(json.dumps(message))
                        delivered_count += 1
                        
                    # Update connection activity
                    self.update_connection_activity(websocket)
                except Exception as e:
                    logger.error(f"Error delivering queued messages to {self.get_connection_identifier(websocket)}: {e}")
            
            # Clear the queue after delivery
            del self.message_queue[(queue_org_id, computation_id)]
            
        if delivered_count > 0:
            logger.info(f"Delivered {delivered_count} queued messages to org_id={org_id}")

class FederatedLearningWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.training_rooms: Dict[str, Set[WebSocket]] = {}
        self.user_trainings: Dict[int, List[str]] = {}
        self.connection_health: Dict[WebSocket, datetime] = {}
        self.connection_metadata: Dict[WebSocket, Dict] = {}
        self.background_task = None
        self.health_check_task = None

    async def connect(self, websocket: WebSocket, user_id: int, client_info: Optional[Dict] = None):
        await websocket.accept()
        
        # Store connection metadata
        metadata = client_info or {}
        metadata.update({
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "client_ip": getattr(websocket, "client", {}).get("host", "unknown")
        })
        self.connection_metadata[websocket] = metadata
        
        # Add to active connections
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        
        # Track connection health
        self.connection_health[websocket] = datetime.utcnow()
        
        # Start background tasks if not already running
        if not self.health_check_task:
            self.health_check_task = asyncio.create_task(self.monitor_connection_health())
            
        # Send welcome message
        welcome_data = {
            "message": "Connected to Federated Learning WebSocket",
            "user_id": user_id,
            "active_trainings": self.user_trainings.get(user_id, [])
        }
        await websocket.send_text(json.dumps({
            "type": MessageType.SYSTEM_NOTIFICATION.value,
            "data": welcome_data,
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        logger.info(f"Federated Learning WebSocket connection established for user {user_id}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        # Clean up connection tracking
        if websocket in self.connection_health:
            del self.connection_health[websocket]
            
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        # Remove from active connections
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

        # Remove from training rooms
        for model_id, connections in list(self.training_rooms.items()):
            connections.discard(websocket)
            if not connections:
                del self.training_rooms[model_id]
                
        logger.info(f"Federated Learning WebSocket connection closed for user {user_id}")

    async def join_training_room(self, websocket: WebSocket, model_id: str, user_id: int):
        """Join a specific training room for real-time updates"""
        if model_id not in self.training_rooms:
            self.training_rooms[model_id] = set()
        self.training_rooms[model_id].add(websocket)
        
        # Track user's trainings
        if user_id not in self.user_trainings:
            self.user_trainings[user_id] = []
        if model_id not in self.user_trainings[user_id]:
            self.user_trainings[user_id].append(model_id)

        # Notify others in the room
        await self.broadcast_to_training(
            model_id,
            MessageType.JOIN_TRAINING,
            {"user_id": user_id, "model_id": model_id}
        )

    async def leave_training_room(self, websocket: WebSocket, model_id: str, user_id: int):
        """Leave a training room"""
        if model_id in self.training_rooms:
            self.training_rooms[model_id].discard(websocket)
            if not self.training_rooms[model_id]:
                del self.training_rooms[model_id]

        # Notify others in the room
        await self.broadcast_to_training(
            model_id,
            MessageType.LEAVE_TRAINING,
            {"user_id": user_id, "model_id": model_id}
        )

    async def broadcast_to_user(self, user_id: int, message_type: MessageType, data: dict):
        """Broadcast message to all connections of a user"""
        if user_id in self.active_connections:
            message = {
                "type": message_type.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            disconnected = set()
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except WebSocketDisconnect:
                    disconnected.add(connection)
                except Exception as e:
                    print(f"Error sending message to user {user_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections[user_id].discard(connection)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_training(self, model_id: str, message_type: MessageType, data: dict):
        """Broadcast message to all connections in a training room"""
        if model_id in self.training_rooms:
            message = {
                "type": message_type.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            disconnected = set()
            for connection in self.training_rooms[model_id]:
                try:
                    await connection.send_text(json.dumps(message))
                except WebSocketDisconnect:
                    disconnected.add(connection)
                except Exception as e:
                    print(f"Error sending message to training {model_id}: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.training_rooms[model_id].discard(connection)
            if not self.training_rooms[model_id]:
                del self.training_rooms[model_id]

    async def update_model_status(self, model_id: str, status: str, participants: List[int], updates_count: int):
        """Update model training status for all participants"""
        data = {
            "model_id": model_id,
            "status": status,
            "participants": participants,
            "updates_count": updates_count,
            "total_participants": len(participants)
        }
        
        await self.broadcast_to_training(model_id, MessageType.MODEL_UPDATE, data)

    async def notify_model_update(self, model_id: str, user_id: int, metrics: dict):
        """Notify when a model update is submitted"""
        data = {
            "model_id": model_id,
            "user_id": user_id,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_training(model_id, MessageType.MODEL_UPDATE, data)

    async def notify_aggregation_completed(self, model_id: str, result_summary: dict):
        """Notify when model aggregation is completed"""
        data = {
            "model_id": model_id,
            "result": result_summary,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        await self.broadcast_to_training(model_id, MessageType.AGGREGATION_RESULT, data)

    async def monitor_connection_health(self):
        """Monitor connection health and clean up stale connections"""
        while True:
            try:
                current_time = datetime.utcnow()
                stale_connections = []
                
                # Check for stale connections (inactive for more than 2 minutes)
                for websocket, last_active in list(self.connection_health.items()):
                    time_diff = (current_time - last_active).total_seconds()
                    
                    if time_diff > 120:  # 2 minutes
                        stale_connections.append(websocket)
                    elif time_diff > 30:  # 30 seconds - send health check
                        try:
                            metadata = self.connection_metadata.get(websocket, {})
                            user_id = metadata.get("user_id")
                            
                            if user_id:
                                health_data = {
                                    "status": "active",
                                    "connected_since": metadata.get("connected_at", current_time).isoformat(),
                                    "last_activity": last_active.isoformat(),
                                    "active_trainings": len(self.user_trainings.get(user_id, []))
                                }
                                
                                await websocket.send_text(json.dumps({
                                    "type": MessageType.CONNECTION_HEALTH.value,
                                    "data": health_data,
                                    "timestamp": current_time.isoformat()
                                }))
                                
                                # Update last activity time
                                self.connection_health[websocket] = current_time
                        except Exception as e:
                            logger.warning(f"Error sending health check: {e}")
                            stale_connections.append(websocket)
                
                # Clean up stale connections
                for websocket in stale_connections:
                    try:
                        metadata = self.connection_metadata.get(websocket, {})
                        org_id = metadata.get("org_id")
                        
                        if org_id:
                            logger.info(f"Closing stale connection for org {org_id}")
                            # Don't try to send close message if connection is already closed
                            try:
                                if websocket.client_state.name != 'DISCONNECTED':
                                    await websocket.close(code=1001, reason="Connection timeout")
                            except:
                                pass  # Connection already closed
                            self.disconnect(websocket, org_id)
                    except Exception as e:
                        # Still remove from our tracking without logging errors
                        if websocket in self.connection_health:
                            del self.connection_health[websocket]
                        
                        metadata = self.connection_metadata.get(websocket, {})
                        org_id = metadata.get("org_id")
                        if org_id:
                            self.disconnect(websocket, org_id)
                
                await asyncio.sleep(15)  # Check every 15 seconds
            except Exception as e:
                logger.error(f"Error in monitor_connection_health: {e}")
                await asyncio.sleep(15)  # Wait before retrying
                
    def update_connection_activity(self, websocket: WebSocket):
        """Update the last activity time for a connection"""
        if websocket in self.connection_health:
            self.connection_health[websocket] = datetime.utcnow()

    async def handle_ping(self, websocket: WebSocket, message: dict):
        """Handle ping message and respond with pong"""
        try:
            # Check if connection is still open before sending
            if websocket.client_state.name == 'DISCONNECTED':
                return
                
            timestamp = message.get("timestamp", datetime.utcnow().isoformat())
            await websocket.send_text(json.dumps({
                "type": MessageType.PONG.value,
                "timestamp": timestamp
            }))
            self.update_connection_activity(websocket)
        except Exception as e:
            # Don't log errors for closed connections
            pass

# Create singleton instances
smpc_manager = SMPCWebSocketManager()
federated_manager = FederatedLearningWebSocketManager()