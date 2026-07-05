function LiveFeed({ attempts, commands }) {
  const events = [...attempts, ...commands].sort(
    (a, b) => new Date(b.timestamp) - new Date(a.timestamp)
  );

  if (events.length === 0) {
    return <div className="empty-state">// waiting for incoming connections...</div>;
  }

  return (
    <div className="terminal-feed">
      {events.map((e, i) => (
        <div key={e.attempt_id ? `${e.type}-${e.attempt_id}-${i}` : i} className={`log-line ${e.type}`}>
          <span className="branch">{i === events.length - 1 ? '└─' : '├─'}</span>
          {e.type === 'login' ? (
            <span className="ip">
              {e.ip} <span className="cred">{e.username}:{e.password}</span>
            </span>
          ) : (
            <span className="cmd">$ {e.command}</span>
          )}
          <span className="meta">{e.timestamp?.split(' ')[1]}</span>
        </div>
      ))}
    </div>
  );
}

export default LiveFeed;