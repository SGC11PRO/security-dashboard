import ipaddress
import requests

def is_private_ip(ip):
    try:
        return ipaddress.ip_address(ip).is_private
    except ValueError:
        return True # Si la IP no es válida, la consideramos privada para evitar problemas de geolocalización
    
    
def geolocate_ip (ip):
    if is_private_ip(ip):
        return {'country': 'Local/Unknown', 'city': 'N/A', 'lat': None, 'lon': None}
    
    try: 
        response = requests.get(f"https://ip-api.com/json/{ip}", timeout=5)
        data = response.json()
        
        if data.get('status') == 'success':
            return {
                'country': data.get('country'),
                'city': data.get('city'),
                'lat': data.get('lat'),
                'lon': data.get('lon')
            }
            
    except requests.RequestException:
        pass
    
    return {'country': 'Unknown', 'city': 'Unknown', 'lat': None, 'lon': None}