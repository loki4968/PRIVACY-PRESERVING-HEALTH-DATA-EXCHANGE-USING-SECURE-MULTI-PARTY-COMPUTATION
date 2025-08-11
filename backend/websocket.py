from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from datetime import datetime

class MetricsWebSocketManager:
    def __init__(self):
        self.active_connections: Dict[int, Set[WebSocket]] = {}
        self.background_task = None

    async def connect(self, websocket: WebSocket, org_id: int):
        await websocket.accept()
        if org_id not in self.active_connections:
            self.active_connections[org_id] = set()
        self.active_connections[org_id].add(websocket)

        if not self.background_task:
            self.background_task = asyncio.create_task(self.broadcast_metrics())

    def disconnect(self, websocket: WebSocket, org_id: int):
        self.active_connections[org_id].remove(websocket)
        if not self.active_connections[org_id]:
            del self.active_connections[org_id]

    async def broadcast_to_organization(self, org_id: int, message: str):
        if org_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[org_id]:
                try:
                    await connection.send_text(message)
                except WebSocketDisconnect:
                    disconnected.add(connection)
                except Exception as e:
                    print(f"Error sending message: {e}")
                    disconnected.add(connection)
            
            # Clean up disconnected clients
            for connection in disconnected:
                self.active_connections[org_id].remove(connection)
            if not self.active_connections[org_id]:
                del self.active_connections[org_id]

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
                        }
                    }
                    
                    await self.broadcast_to_organization(
                        org_id,
                        json.dumps(metrics)
                    )
                
                await asyncio.sleep(5)  # Update every 5 seconds
            except Exception as e:
                print(f"Error in broadcast_metrics: {e}")
                await asyncio.sleep(5)  # Wait before retrying

metrics_manager = MetricsWebSocketManager() 