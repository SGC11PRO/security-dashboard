import sqlite3
import os 

from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'db', 'server.db')

def init_db():
    # Crea la base de datos si no existe. Se llama una vez al iniciar el servidor
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
                    CREATE TABLE IF NOT EXISTS auth_attempts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT NOT NULL,
                        username TEXT NOT NULL,
                        password TEXT NOT NULL,
                        timestamp TEXT NOT NULL
                    )
    ''')
    
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS commands (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       attempt_id INTEGER,
                       command TEXT NOT NULL,
                       timestamp TEXT NOT NULL,
                       FOREIGN KEY (attempt_id) REFERENCES auth_attempts(id)
                   )
                ''')
    
    conn.commit()
    conn.close()
    
def log_attempt(ip, username, password):
    # Guarda un intento de login en la base de datos
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(
        'INSERT INTO auth_attempts (ip, username, password, timestamp) VALUES (?, ?, ?, ?)',
        (ip, username, password, timestamp)
    )
    
    conn.commit()
    attempt_id = cursor.lastrowid  # Obtiene el ID del intento de login que acaba de generar
    conn.close()
    
    return attempt_id

def log_command(attempt_id, command):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    cursor.execute(
        'INSERT INTO commands (attempt_id, command, timestamp) VALUES (?, ?, ?)',
        (attempt_id, command, timestamp)
    )
    
    conn.commit()
    conn.close()