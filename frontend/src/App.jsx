import { useEffect, useState } from 'react';

function App() {
  const [devices, setDevices] = useState([]);
  const [filter, setFilter] = useState('all');

  const fetchDevices = () => {
    fetch('http://localhost:5000/devices')
      .then(res => res.json())
      .then(data => setDevices(data))
      .catch(err => console.error('Fetch failed:', err));
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 30000); // every 30s
    return () => clearInterval(interval);
  }, []);

  const handleBlock = (mac) => {
    const duration = prompt("Enter block duration (e.g. 1h, 30m) or leave blank for indefinite:");
    fetch('http://localhost:5000/block', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mac, duration }),
    }).then(() => fetchDevices());
  };

  const handleUnblock = (mac) => {
    fetch('http://localhost:5000/unblock', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mac }),
    }).then(() => fetchDevices());
  };

  const filteredDevices = devices.filter(device => {
    if (filter === 'all') return true;
    return device.status === filter;
  });

  const formatDuration = (duration) => {
    if (!duration) return '—';
    const parts = duration.split(', ');
    const timePart = parts[parts.length - 1];
    const [h, m] = timePart.split(':');
    const days = duration.includes('day') ? duration.split(' day')[0] + 'd ' : '';
    return `${days}${parseInt(h)}h ${parseInt(m)}m`;
  };

  const statusColor = (status) => {
    switch (status) {
      case 'online': return 'green';
      case 'blocked': return 'red';
      case 'scheduled': return 'orange';
      default: return 'gray';
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h1>Router Guardian - Device Manager</h1>

      <div style={{ marginBottom: '10px' }}>
        <label>Filter: </label>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="all">All</option>
          <option value="online">Online</option>
          <option value="blocked">Blocked</option>
          <option value="scheduled">Scheduled</option>
          <option value="offline">Offline</option>
        </select>
      </div>

      <table border="1" cellPadding="10" cellSpacing="0" style={{ width: '100%' }}>
        <thead>
          <tr>
            <th>Hostname</th>
            <th>IP</th>
            <th>MAC</th>
            <th>Status</th>
            <th>Online Duration</th>
            <th>Action</th>
          </tr>
        </thead>
        <tbody>
          {filteredDevices.map((device, index) => (
            <tr key={index}>
              <td>{device.hostname || '—'}</td>
              <td>{device.ip || '—'}</td>
              <td>{device.mac}</td>
              <td style={{ color: statusColor(device.status), fontWeight: 'bold' }}>
                {device.status}
              </td>
              <td>{formatDuration(device.online_duration)}</td>
              <td>
                {(device.status === 'blocked' || device.status === 'scheduled') ? (
                  <button onClick={() => handleUnblock(device.mac)}>Unblock</button>
                ) : (
                  <button onClick={() => handleBlock(device.mac)}>Block</button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
