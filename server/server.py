import paramiko
import socket 
import threading
import requests
import re

from pathlib import Path

# Definimos qué hace nuestro servidor cuando alguien intenta
# - autenticarse con usuario/contraseña
# - pide abrir un canal de comunición para llegar a una shell

# Credenciales aceptadas para entrar en la shell
COMMON_CREDS = {
    ('admin', 'admin'),
    ('root', 'root'),
    ('root', 'toor'),
    ('admin', 'password')
}

BASE_DIR = Path(__file__).resolve().parent
SERVER_KEY_PATH = BASE_DIR / 'server.key'
BACKEND_URL = 'http://localhost:8000'


def get_or_create_server_key():
    if SERVER_KEY_PATH.exists():
        return paramiko.RSAKey(filename=str(SERVER_KEY_PATH))

    # If the key doesn't exist yet, create one so first run works out-of-the-box.
    key = paramiko.RSAKey.generate(2048)
    key.write_private_key_file(str(SERVER_KEY_PATH))
    print(f"[*] Clave SSH generada en {SERVER_KEY_PATH}")
    return key

class Server(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip  = client_ip
        self.event = threading.Event()
        self.attempt_id = None
        
    def check_auth_password(self, username, password):
        # Aquí capturamos el usuario/contraseña probados
        print (f"[+] Intento de autenticación desde {self.client_ip} con usuario: {username} y contraseña: {password}")
        
        # Guardamos el intento en la base de datos a través del backend
        response = requests.post(f"{BACKEND_URL}/events", json={
            "type": "login",
            "ip": self.client_ip,
            "username": username,
            "password": password
        })
        
        self.attempt_id = response.json().get('attempt_id')

        # Comparamos credenciales
        if (username, password) in COMMON_CREDS:
            return paramiko.AUTH_SUCCESSFUL
        else:
            return paramiko.AUTH_FAILED
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
    
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def get_allowed_auths(self, username):
        # Le decimos al cliente que solo puede autenticarse con password
        return 'password'
    
    def check_channel_pty_request (self, channel, term, width, height, pixelWidth, pixelHeight, modes):
        return True
    
    def check_channel_shell_request(self, channel):
        self.event.set()
        return True

def send_command_event(attempt_id, command):
    """Envía un comando capturado al backend, sin tumbar la shell si el backend falla."""
    try:
        requests.post(f"{BACKEND_URL}/events", json={
            "type": "command",
            "attempt_id": attempt_id,
            "command": command
        }, timeout=3)
    except requests.RequestException as e:
        print(f"[!] No se pudo enviar el comando al backend: {e}")

def fake_shell(channel, attempt_id):
    channel.send(b'Welcome to Ubuntu 22.04 LTS (GNU/Linux 5.15.0-1051-azure x86_64)\r\n')
    prompt = b'root@server:~# '
    channel.send(prompt)

    buffer = b''
    while True:
        data = channel.recv(1024)
        if not data:
            break

        # Imprimimos lo que el atacante escribe en la shell
        channel.send(data)
        buffer += data

        # Procesamos TODOS los comandos completos que haya en el buffer,
        # por si llegan varios pegados en un mismo recv() (típico de bots)
        while b'\r' in buffer or b'\n' in buffer:
            line, buffer = re.split(rb'\r\n|\r|\n', buffer, maxsplit=1)
            command = line.strip().decode('utf-8', errors='ignore')

            if command == '':
                channel.send(b'\r\n' + prompt)
                continue

            print(f"[CMD] {command}")
            send_command_event(attempt_id, command)

            if command in ('exit', 'logout'):
                channel.send(b'\r\nlogout\r\n')
                channel.close()
                return

            response = fake_command_response(command)
            channel.send(b'\r\n' + response + b'\r\n' + prompt)

    channel.close()
    
def fake_command_response(command):
    responses = {
        'whoami': b'root',
        'pwd': b'/root',
        'ls': b'Desktop  Documents  Downloads  Music  Pictures  Public  Templates  Videos',
        'uname -a': b'Linux server 5.15.0-1051-azure #59-Ubuntu SMP Wed May 3 19:51:50 UTC 2023 x86_64 x86_64 x86_64 GNU/Linux',
    }
    
    return responses.get(command, b'command not found')
    
def handle_connection(client_socket, client_ip):
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(get_or_create_server_key())
        
        server = Server(client_ip)
        transport.start_server(server=server)
        
        # Esperamos a que el cliente intente abrir un canal
        channel = transport.accept(timeout=10)
        if channel is None:
            transport.close()
            return
        
        server.event.wait(10) # Esperamos a que pidan shell
        fake_shell(channel, server.attempt_id)
            
    except Exception as e:
        print (f"[!] Error manejando la conexión desde {client_ip}: {e}")
            
            
def start_server(host = '0.0.0.0', port = 2222):
    get_or_create_server_key()
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(100)
    
    print  (f"[*] Servidor SSH escuchando en {host}:{port}")
    
    while True: 
        client_socket, addr = server_socket.accept()
        client_ip = addr[0]
        print (f"[+] Conexión entrante desde {client_ip}")
        
        # Cada conexión la manejamos en su propio hilo
        # para poder atender múltiples conexiones al mismo tiempo
        threading.Thread(target=handle_connection, args=(client_socket, client_ip)).start()
        

if __name__ == "__main__":
    start_server()