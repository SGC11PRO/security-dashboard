import sys
import json
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel

from geolocation import geolocate_ip

# Añadimos la raíz del proyecto al path para poder importar server.logger.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.logger import get_all_attempts, get_all_commands, init_db, log_attempt, log_command


app = FastAPI()

connected_clients = [] # Lista para almacenar los WebSockets conectados

class Event(BaseModel):
    type: str
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    attempt_id: Optional[int] = None
    command: Optional[str] = None
    
    
async def broadcast(data: dict):
    for client in connected_clients:
        await client.send_text(json.dumps(data))

@app.on_event("startup")
def startup_event():
    init_db()
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    print (f"[WS] Cliente conectado: {websocket.client}. Total: {len(connected_clients)}")
    
    try: 
        while True:
            await websocket.receive_text()  # Esperamos a recibir mensajes, aunque no los usemos
    
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
        print (f"[WS] Cliente desconectado: {websocket.client}. Total: {len(connected_clients)}")

@app.get('/health')
def health_check():
    return {"status": "ok"}

@app.get('/attempts')
def attempts():
    return get_all_attempts()

@app.get('/commands')
def commands():
    return get_all_commands()

@app.post('/events')
async def create_event(event: Event):
    if event.type == 'login':
        geo = geolocate_ip(event.ip)
        attempt_id = log_attempt(event.ip, event.username, event.password, geo['country'], geo['city'], geo['lat'], geo['lon'])
        await broadcast({
            "type": "login",
            "ip": event.ip,
            "username": event.username,
            "password": event.password,
            "attempt_id": attempt_id,
            **geo
        })
        
        return {"attempt_id": attempt_id}
    
    elif event.type == 'command':
        log_command(event.attempt_id, event.command)
        await broadcast({
            "type": "command",
            "attempt_id": event.attempt_id,
            "command": event.command
        })
        
        return {"status": "ok"}