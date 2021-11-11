from typing import List

from fastapi import WebSocket
from fastapi import status

class ConnectionManager():
    active_connections: List[WebSocket]
    
    def __init__(self) -> None:
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket) -> None:
        await websocket.close(code=status.WS_1000_NORMAL_CLOSURE)
        self.active_connections.remove(websocket)
    
    async def receive(self, websocket: WebSocket):
        return await websocket.receive_json()
    
    async def send(self, websocket: WebSocket) -> None:
        return await websocket.send_json({'name': 'Nami'})