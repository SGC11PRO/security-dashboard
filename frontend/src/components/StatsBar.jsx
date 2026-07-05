import { Crosshair, Globe2, KeyRound, Terminal } from 'lucide-react';

function StatCard({ icon: Icon, label, value }) {
  return (
    <div className="stat-card">
      <Icon size={16} strokeWidth={1.5} />
      <div>
        <div className="stat-value">{value}</div>
        <div className="stat-label">{label}</div>
      </div>
    </div>
  );
}

function StatsBar({ attempts, commands }) {
  const uniqueIps = new Set(attempts.map(a => a.ip)).size;
  const uniqueCountries = new Set(attempts.map(a => a.country).filter(Boolean)).size;

  return (
    <div className="stats-bar">
      <StatCard icon={Crosshair} label="Total Attempts" value={attempts.length} />
      <StatCard icon={Globe2} label="Unique IPs" value={uniqueIps} />
      <StatCard icon={KeyRound} label="Countries" value={uniqueCountries} />
      <StatCard icon={Terminal} label="Commands Run" value={commands.length} />
    </div>
  );
}

export default StatsBar;