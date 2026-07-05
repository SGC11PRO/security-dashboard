import { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <span style={{ color: 'var(--accent)' }}>{payload[0].payload.label}</span>
      <br />
      {payload[0].value} intentos
    </div>
  );
};

function AttackCharts({ attempts }) {
  const [view, setView] = useState('credentials');

  const credCounts = {};
  attempts.forEach((a) => {
    const key = `${a.username}/${a.password}`;
    credCounts[key] = (credCounts[key] || 0) + 1;
  });
  const credData = Object.entries(credCounts)
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);

  const hourCounts = {};
  attempts.forEach((a) => {
    const hour = a.timestamp ? a.timestamp.split(' ')[1]?.split(':')[0] + 'h' : '??';
    hourCounts[hour] = (hourCounts[hour] || 0) + 1;
  });
  const hourData = Object.entries(hourCounts)
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => a.label.localeCompare(b.label));

  const data = view === 'credentials' ? credData : hourData;

  return (
    <div>
      <div className="chart-tabs">
        <button
          className={view === 'credentials' ? 'chart-tab active' : 'chart-tab'}
          onClick={() => setView('credentials')}
        >
          Top Credentials
        </button>
        <button
          className={view === 'hourly' ? 'chart-tab active' : 'chart-tab'}
          onClick={() => setView('hourly')}
        >
          By Hour
        </button>
      </div>

      {data.length === 0 ? (
        <div className="empty-state">// no data yet</div>
      ) : (
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 4" stroke="var(--border)" vertical={false} />
            <XAxis dataKey="label" axisLine={{ stroke: 'var(--border)' }} tickLine={false} interval={0} angle={-35} textAnchor="end" height={60} />
            <YAxis axisLine={false} tickLine={false} allowDecimals={false} />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: 'var(--accent-dim)' }} />
            <Bar dataKey="value" radius={[2, 2, 0, 0]}>
              {data.map((_, i) => (
                <Cell key={i} fill={i === 0 ? 'var(--accent)' : 'var(--border)'} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default AttackCharts;