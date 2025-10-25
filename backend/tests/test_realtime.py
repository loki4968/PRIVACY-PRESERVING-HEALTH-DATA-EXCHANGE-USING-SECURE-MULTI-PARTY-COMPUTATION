#!/usr/bin/env python3
"""
Test script for real-time WebSocket functionality
"""

import asyncio
import websockets
import json
import time
from datetime import datetime

async def test_websocket_connection():
    """Test WebSocket connection and message handling"""
    
    # Test token (valid token generated from auth_utils)
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGhvc3BpdGFsLmNvbSIsImlkIjoxLCJyb2xlIjoiZG9jdG9yIiwicGVybWlzc2lvbnMiOlsicmVhZF9wYXRpZW50X2RhdGEiLCJ3cml0ZV9wYXRpZW50X2RhdGEiLCJyZWFkX2xhYl9yZXN1bHRzIiwicHJlc2NyaWJlX21lZGljYXRpb24iLCJ2aWV3X2FuYWx5dGljcyJdLCJleHAiOjE3NTYxOTU5MjUsImlhdCI6MTc1NjE5NDEyNSwidHlwZSI6ImFjY2VzcyJ9.aS45QYUzoJpdpGPeT9-lmGVPD--dDT2bTA5ZB19h1H8"
    
    # Include client information in connection URL
    user_email = "test@hospital.com"
    user_role = "doctor"
    user_agent = "Test Script/1.0"
    
    uri = f"ws://localhost:8000/ws/metrics?token={test_token}&email={user_email}&role={user_role}&user_agent={user_agent}"
    
    try:
        print("🔌 Connecting to WebSocket...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Test joining a computation room
            test_computation_id = "test-computation-123"
            join_message = {
                "type": "join_computation",
                "computation_id": test_computation_id
            }
            
            print(f"📤 Sending join message for computation: {test_computation_id}")
            await websocket.send(json.dumps(join_message))
            
            # Listen for messages
            print("👂 Listening for messages...")
            message_count = 0
            start_time = time.time()
            
            while message_count < 5 and (time.time() - start_time) < 30:  # Listen for 30 seconds max
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    message_count += 1
                    data = json.loads(message)
                    print(f"📨 Received message {message_count}: {data.get('type', 'unknown')}")
                    
                    if data.get('type') == 'metrics_update':
                        print(f"   📊 Metrics: {data.get('data', {})}")
                    elif data.get('type') == 'computation_status':
                        print(f"   🔄 Status: {data.get('data', {})}")
                    elif data.get('type') == 'connection_health':
                        print(f"   ❤️ Connection Health: {data.get('data', {})}")
                    elif data.get('type') == 'system_notification':
                        print(f"   🔔 System Notification: {data.get('data', {})}")
                    elif data.get('type') == 'pong':
                        latency = time.time() * 1000 - data.get('data', {}).get('timestamp', 0)
                        print(f"   🏓 Pong received with {latency:.2f}ms latency")
                    
                except asyncio.TimeoutError:
                    print("⏰ Timeout waiting for message")
                    break
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            # Test ping/pong functionality
            ping_message = {
                "type": "ping",
                "data": {"timestamp": time.time() * 1000}
            }
            
            print("📤 Sending ping message")
            await websocket.send(json.dumps(ping_message))
            
            # Wait for pong response
            try:
                pong_message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                pong_data = json.loads(pong_message)
                if pong_data.get('type') == 'pong':
                    print("✅ Received pong response")
                    message_count += 1
            except (asyncio.TimeoutError, Exception) as e:
                print(f"❌ Error receiving pong: {e}")
            
            # Test get_active_computations
            active_comps_message = {
                "type": "get_active_computations"
            }
            
            print("📤 Requesting active computations")
            await websocket.send(json.dumps(active_comps_message))
            
            # Wait for active computations response
            try:
                active_comps_response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                active_comps_data = json.loads(active_comps_response)
                if active_comps_data.get('type') == 'active_computations':
                    print(f"✅ Received active computations: {active_comps_data.get('data', [])}")
                    message_count += 1
            except (asyncio.TimeoutError, Exception) as e:
                print(f"❌ Error receiving active computations: {e}")
            
            # Test leaving the computation room
            leave_message = {
                "type": "leave_computation",
                "computation_id": test_computation_id
            }
            
            print(f"📤 Sending leave message for computation: {test_computation_id}")
            await websocket.send(json.dumps(leave_message))
            
            print(f"📊 Total messages received: {message_count}")
            
    except websockets.exceptions.InvalidStatusCode as e:
        print(f"❌ WebSocket connection failed with status {e.status_code}")
        if e.status_code == 4001:
            print("   Missing authentication token")
        elif e.status_code == 4002:
            print("   Invalid token")
        elif e.status_code == 4003:
            print("   Token validation failed")
    except Exception as e:
        print(f"❌ Connection error: {e}")

async def test_multiple_connections():
    """Test multiple WebSocket connections (simulating multiple users)"""
    
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGhvc3BpdGFsLmNvbSIsImlkIjoxLCJyb2xlIjoiZG9jdG9yIiwicGVybWlzc2lvbnMiOlsicmVhZF9wYXRpZW50X2RhdGEiLCJ3cml0ZV9wYXRpZW50X2RhdGEiLCJyZWFkX2xhYl9yZXN1bHRzIiwicHJlc2NyaWJlX21lZGljYXRpb24iLCJ2aWV3X2FuYWx5dGljcyJdLCJleHAiOjE3NTYxOTU5MjUsImlhdCI6MTc1NjE5NDEyNSwidHlwZSI6ImFjY2VzcyJ9.aS45QYUzoJpdpGPeT9-lmGVPD--dDT2bTA5ZB19h1H8"
    test_computation_id = "multi-test-456"
    
    async def client_connection(client_id):
        # Include client information
        user_email = f"test{client_id}@hospital.com"
        user_role = "doctor"
        user_agent = f"Test Client {client_id}/1.0"
        
        uri = f"ws://localhost:8000/ws/metrics?token={test_token}&email={user_email}&role={user_role}&user_agent={user_agent}"
        
        try:
            async with websockets.connect(uri) as websocket:
                print(f"👤 Client {client_id}: Connected")
                
                # Join computation room
                join_message = {
                    "type": "join_computation",
                    "computation_id": test_computation_id
                }
                await websocket.send(json.dumps(join_message))
                print(f"👤 Client {client_id}: Joined computation room")
                
                # Send ping to test connection health
                ping_message = {
                    "type": "ping",
                    "data": {"timestamp": time.time() * 1000}
                }
                await websocket.send(json.dumps(ping_message))
                print(f"👤 Client {client_id}: Sent ping")
                
                # Wait for pong and other messages
                message_count = 0
                start_time = time.time()
                
                while message_count < 3 and (time.time() - start_time) < 10:
                    try:
                        message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(message)
                        message_count += 1
                        print(f"👤 Client {client_id}: Received {data.get('type', 'unknown')}")
                    except asyncio.TimeoutError:
                        break
                    except Exception as e:
                        print(f"👤 Client {client_id}: Error receiving message: {e}")
                        break
                
                # Wait a bit more
                await asyncio.sleep(2)
                
                # Leave computation room
                leave_message = {
                    "type": "leave_computation",
                    "computation_id": test_computation_id
                }
                await websocket.send(json.dumps(leave_message))
                print(f"👤 Client {client_id}: Left computation room")
                
        except Exception as e:
            print(f"👤 Client {client_id}: Connection error: {e}")
    
    print("🧪 Testing multiple WebSocket connections...")
    await asyncio.gather(*[client_connection(i) for i in range(3)])
    print("✅ Multiple connection test completed")

async def test_connection_health():
    """Test connection health monitoring and reconnection"""    
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0QGhvc3BpdGFsLmNvbSIsImlkIjoxLCJyb2xlIjoiZG9jdG9yIiwicGVybWlzc2lvbnMiOlsicmVhZF9wYXRpZW50X2RhdGEiLCJ3cml0ZV9wYXRpZW50X2RhdGEiLCJyZWFkX2xhYl9yZXN1bHRzIiwicHJlc2NyaWJlX21lZGljYXRpb24iLCJ2aWV3X2FuYWx5dGljcyJdLCJleHAiOjE3NTYxOTU5MjUsImlhdCI6MTc1NjE5NDEyNSwidHlwZSI6ImFjY2VzcyJ9.aS45QYUzoJpdpGPeT9-lmGVPD--dDT2bTA5ZB19h1H8"
    
    # Include client information
    user_email = "health_monitor@hospital.com"
    user_role = "admin"
    user_agent = "Health Monitor Test/1.0"
    
    uri = f"ws://localhost:8000/ws/metrics?token={test_token}&email={user_email}&role={user_role}&user_agent={user_agent}"
    
    try:
        print("🔌 Testing connection health monitoring...")
        async with websockets.connect(uri) as websocket:
            print("✅ Connected successfully!")
            
            # Wait for connection health messages
            health_received = False
            start_time = time.time()
            
            while not health_received and (time.time() - start_time) < 30:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(message)
                    
                    if data.get('type') == 'connection_health':
                        health_received = True
                        print(f"❤️ Received connection health: {data.get('data', {})}")
                    else:
                        print(f"📨 Received message: {data.get('type', 'unknown')}")
                        
                except asyncio.TimeoutError:
                    # Send ping to trigger activity
                    ping_message = {
                        "type": "ping",
                        "data": {"timestamp": time.time() * 1000}
                    }
                    await websocket.send(json.dumps(ping_message))
                    print("📤 Sent ping to trigger activity")
                    
                except Exception as e:
                    print(f"❌ Error receiving message: {e}")
                    break
            
            if health_received:
                print("✅ Connection health monitoring test passed")
            else:
                print("❌ Did not receive connection health message within timeout")
                
    except Exception as e:
        print(f"❌ Connection error: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting WebSocket Real-time Collaboration Tests")
    print("==================================================")
    print("\n1️⃣ Testing single WebSocket connection...")
    await test_websocket_connection()
    
    print("\n2️⃣ Testing multiple WebSocket connections...")
    await test_multiple_connections()
    
    print("\n3️⃣ Testing connection health monitoring...")
    await test_connection_health()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    asyncio.run(main())
