import sys
import os

# añadimos la carpeta al server/ al path para poder importar logger.py
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'server'))

from fastapi import FastAPI
from logger import get_all_attempts, get_all_commands

app = FastAPI()

@app.get('/health')
def health_check():
    return {"status": "ok"}

@app.get('/attempts')
def attempts():
    return get_all_attempts()

@app.get('/commands')
def commands():
    return get_all_commands()