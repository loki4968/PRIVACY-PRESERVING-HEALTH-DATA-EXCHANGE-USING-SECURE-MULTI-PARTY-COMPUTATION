import asyncio
import json
import websockets
import jwt
import logging
import sys
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "ws://localhost:8000/ws/federated"
SECRET_KEY = "your_secret_key"  # Replace with your actual secret key

# Test user data
TEST_USER = {
    "id": 1,
    "sub": "test@example.com",
    "role": "organization"
}

# Create a JWT token
def create_token(user_data):
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {
        **user_data,
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

# WebSocket client for testing
async def test_federated_websocket():
    token = create_token(TEST_USER)
    uri = f"{API_URL}?token={token}"
    
    logger.info(f"Connecting to {uri}")
    
    try:
        async with websockets.connect(uri) as websocket:
            logger.info("Connected to WebSocket server")
            
            # Test ping/pong
            await test_ping_pong(websocket)
            
            # Test getting federated models
            await test_get_federated_models(websocket)
            
            # Keep connection alive for a while to observe any server messages
            await asyncio.sleep(10)
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")

# Test ping/pong functionality
async def test_ping_pong(websocket):
    logger.info("Testing ping/pong...")
    
    ping_message = {
        "type": "ping",
        "timestamp": datetime.now().isoformat()
    }
    
    await websocket.send(json.dumps(ping_message))
    logger.info(f"Sent: {ping_message}")
    
    response = await websocket.recv()
    logger.info(f"Received: {response}")
    
    try:
        response_data = json.loads(response)
        if response_data.get("type") == "pong":
            logger.info("Ping/pong test successful")
        else:
            logger.warning(f"Unexpected response type: {response_data.get('type')}")
    except json.JSONDecodeError:
        logger.error("Failed to parse response as JSON")

# Test getting federated models
async def test_get_federated_models(websocket):
    logger.info("Testing get_federated_models...")
    
    message = {
        "type": "get_federated_models"
    }
    
    await websocket.send(json.dumps(message))
    logger.info(f"Sent: {message}")
    
    response = await websocket.recv()
    logger.info(f"Received: {response}")
    
    try:
        response_data = json.loads(response)
        if response_data.get("type") == "federated_models":
            logger.info(f"Received {len(response_data.get('models', []))} federated models")
        else:
            logger.warning(f"Unexpected response type: {response_data.get('type')}")
    except json.JSONDecodeError:
        logger.error("Failed to parse response as JSON")

# Run the test
if __name__ == "__main__":
    asyncio.run(test_federated_websocket())