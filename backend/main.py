import sys
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel

# Añadimos la raíz del proyecto al path para poder importar server.logger.
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from server.logger import get_all_attempts, get_all_commands, init_db, log_attempt, log_command


app = FastAPI()

class Event(BaseModel):
    type: str
    ip: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    attempt_id: Optional[int] = None
    command: Optional[str] = None

@app.on_event("startup")
def startup_event():
    init_db()
    
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Mensaje recibido: {data}")

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
def create_event(event: Event):
    if event.type == 'login':
        if not all([event.ip, event.username, event.password]):
            raise HTTPException(status_code=400, detail='ip, username y password son obligatorios para login')
        attempt_id = log_attempt(event.ip, event.username, event.password)
        return {'attempt_id': attempt_id}

    if event.type == 'command':
        if event.attempt_id is None or not event.command:
            raise HTTPException(status_code=400, detail='attempt_id y command son obligatorios para command')
        log_command(event.attempt_id, event.command)
        return {'status': 'ok'}

    raise HTTPException(status_code=400, detail='tipo de evento no soportado')