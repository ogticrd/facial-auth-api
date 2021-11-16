from typing import List
from abc import ABCMeta
from abc import abstractmethod

from fastapi import WebSocket
from fastapi import status

class IConnectionManager(metaclass=ABCMeta):
    active_connections: List[WebSocket]
    
    def __init__(self) -> None:
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
    
    async def disconnect(self, websocket: WebSocket, code: int = status.WS_1000_NORMAL_CLOSURE) -> None:
        await websocket.close(code=code)
        self.active_connections.remove(websocket)
    
    @abstractmethod
    async def receive(self):
        NotImplementedError('Implement it then call it')
    
    @abstractmethod
    async def send(self):
        NotImplementedError('Implement it then call it')