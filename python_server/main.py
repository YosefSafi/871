import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from game_logic import GameState

app = FastAPI()
game = GameState()

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        # Send initial state
        await websocket.send_text(json.dumps(game.get_state()))
        
        while True:
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            # Process input
            if payload.get("action") == "move":
                dx, dy = payload.get("dir", [0, 0])
                game.move_player(dx, dy)
                
            # Advance game turn (AI moves)
            game.process_turn()
            
            # Broadcast new state
            await manager.broadcast(json.dumps(game.get_state()))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
