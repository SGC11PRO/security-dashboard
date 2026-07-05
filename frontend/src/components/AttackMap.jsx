import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';

const pulseIcon = L.divIcon({
  className: 'pulse-marker',
  html: '<span class="pulse-dot"></span><span class="pulse-ring"></span>',
  iconSize: [16, 16],
});

function AttackMap({ attempts }) {
    const geoAttempts = attempts.filter((a) => a.lat && a.lon);

    if (geoAttempts.length === 0) {
        return <div className="empty-state">// no geolocated attacks yet — waiting for public IPs</div>;
    }
  
    return (
        <MapContainer center={[20, 0]} zoom={2} style={{ height: '400px', width: '100%' }}>
        <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; OpenStreetMap contributors'
        />
        {geoAttempts.map((a) => (
            <Marker key={a.attempt_id} position={[a.lat, a.lon]} icon={pulseIcon}>
                <Popup>
                <strong>{a.ip}</strong><br />
                {a.username} / {a.password}<br />
                {a.city}, {a.country}
                </Popup>
            </Marker>
            ))}
        </MapContainer>
    );
}

export default AttackMap;