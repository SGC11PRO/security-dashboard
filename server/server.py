import paramiko
import socket 
import threading

# Definimos qué hace nuestro servidor cuando alguien intenta
# - autenticarse con usuario/contraseña
# - pide abrir un canal de comunición para llegar a una shell

class Server(paramiko.ServerInterface):
    def __init__(self, client_ip):
        self.client_ip  = client_ip
        self.event = threading.Event()
        
    def check_auth_password(self, username, password):
        # Aquí capturamos el usuario/contraseña probados
        print (f"[+] Intento de autenticación desde {self.client_ip} con usuario: {username} y contraseña: {password}")
        
        # Temporalmente, rechazamos cualquier intento de autenticación
        return paramiko.AUTH_FAILED
    
    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
    
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

            
def handle_connection(client_socket, client_ip):
    try:
        transport = paramiko.Transport(client_socket)
        transport.add_server_key(paramiko.RSAKey(filename='server/server.key'))
        
        server = Server(client_ip)
        transport.start_server(server=server)
        
        # Esperamos a que el cliente intente abrir un canal
        channel = transport.accept(timeout=10)
        if channel is None:
            transport.close()
            
    except Exception as e:
        print (f"[!] Error manejando la conexión desde {client_ip}: {e}")
            
            
def start_server(host = '0.0.0.0', port = 2222):
    server_key = paramiko.RSAKey(filename='server/server.key')
    
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