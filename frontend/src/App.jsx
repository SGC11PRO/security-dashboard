import { useState, useEffect, useRef } from 'react';
import 'leaflet/dist/leaflet.css';
import AttackMap from './components/AttackMap';
import LiveFeed from './components/LiveFeed';
import AttackCharts from './components/AttackCharts';
import StatsBar from './components/StatsBar';

function App() {
  const [attempts, setAttempts] = useState([]);
  const [commands, setCommands] = useState([]);
  const [connected, setConnected] = useState(false);
  const reconnectTimeout = useRef(null);

  // Cargar datos anteriores desde .db
  useEffect(() => {
    const BACKEND_HTTP = 'http://bore.pub:50468';

    fetch(`${BACKEND_HTTP}/attempts`)
      .then(res => res.json())
      .then(data => setAttempts(data));

    fetch(`${BACKEND_HTTP}/commands`)
      .then(res => res.json())
      .then(data => setCommands(data));
  }, []);

  useEffect(() => {
    let active = true;
    let ws;

    const connect = () => {
      ws = new WebSocket('ws://bore.pub:50468/ws');

      ws.onopen = () => {
        if (active) setConnected(true);
      };

      ws.onmessage = (event) => {
        if (!active) return;
        const data = JSON.parse(event.data);
        if (data.type === 'login') {
          setAttempts((prev) => [data, ...prev]);
        } else if (data.type === 'command') {
          setCommands((prev) => [data, ...prev]);
        }
      };

      ws.onclose = () => {
        if (active) {
          setConnected(false);
          reconnectTimeout.current = setTimeout(connect, 3000);
        }
      };

      ws.onerror = () => ws.close();
    };

    connect();

    return () => {
      active = false;
      clearTimeout(reconnectTimeout.current);
      ws?.close();
    };
  }, []);

  return (
    <div className="dashboard">
      <div className="header">
        <div>
          <h1>SSH Honeypot</h1>
          <div className="subtitle">Real-time intrusion monitoring</div>
        </div>
        <div className="tag-row">
          <span className={connected ? 'tag status-live' : 'tag status-offline'}>
            {connected ? 'Live' : 'Reconnecting…'}
          </span>
          <span className="tag">Port 50468</span>
          <span className="tag">{attempts.length} attempts</span>
        </div>
      </div>

      <StatsBar attempts={attempts} commands={commands} />

      <div className="panel">
        <div className="panel-header">
          <h2>Attack Origins</h2>
          <span className="count">{attempts.filter(a => a.lat).length} geolocated</span>
        </div>
        <div className="map-wrap">
          <AttackMap attempts={attempts} />
        </div>
      </div>

      <div className="grid">
        <div className="panel">
          <div className="panel-header">
            <h2>Live Feed</h2>
            <span className="count">operation_001</span>
          </div>
          <LiveFeed attempts={attempts} commands={commands} />
        </div>
        <div className="panel">
          <div className="panel-header">
            <h2>Top Credentials</h2>
          </div>
          <AttackCharts attempts={attempts} />
        </div>
      </div>
    </div>
  );
}

export default App;