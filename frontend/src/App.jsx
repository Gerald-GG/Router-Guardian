import { useEffect, useState } from 'react';

// Utility: Format device online duration
const formatDuration = (duration) => {
  if (!duration) return '-';
  const parts = duration.split(',');
  return parts.length > 1 ? `${parts[0]} ${parts[1].trim()}` : parts[0];
};

function App() {
  // =======================
  // State definitions
  // =======================
  const [devices, setDevices] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortKey, setSortKey] = useState('hostname');
  const [sortOrder, setSortOrder] = useState('asc');
  const [isLoading, setIsLoading] = useState(false);
  const [refreshOn, setRefreshOn] = useState(true);
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') === 'true');
  const [ssid, setSsid] = useState('Fetching...');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 5;
  const [viewMode, setViewMode] = useState('laptop');

  // =======================
  // Fetch SSID on load
  // =======================
  useEffect(() => {
    fetch('http://localhost:5000/wifi')
      .then(res => res.json())
      .then(data => setSsid(data.ssid || 'Unavailable'))
      .catch(() => setSsid('Unavailable'));
  }, []);

  // =======================
  // Device auto-refresh logic
  // =======================
  useEffect(() => {
    const fetchDevices = () => {
      fetch('http://localhost:5000/devices')
        .then(res => res.json())
        .then(data => setDevices(data))
        .catch(err => console.error('Failed to fetch devices:', err));
    };

    fetchDevices();
    let interval;
    if (refreshOn) interval = setInterval(fetchDevices, 30000);
    return () => clearInterval(interval);
  }, [refreshOn]);

  // =======================
  // Handle dark mode toggle
  // =======================
  useEffect(() => {
    document.documentElement.classList.toggle('dark', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  // =======================
  // Block a device
  // =======================
  const handleBlock = async (mac) => {
    const duration = prompt('Enter block duration (e.g. 1h, 30m):');
    if (!duration) return;

    setIsLoading(true);
    try {
      await fetch('http://localhost:5000/block', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mac, duration }),
      });
      refreshDevices();
    } catch (err) {
      console.error('Block failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // =======================
  // Unblock a device
  // =======================
  const handleUnblock = async (mac) => {
    setIsLoading(true);
    try {
      await fetch('http://localhost:5000/unblock', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mac }),
      });
      refreshDevices();
    } catch (err) {
      console.error('Unblock failed:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // =======================
  // Refresh device list manually
  // =======================
  const refreshDevices = () => {
    fetch('http://localhost:5000/devices')
      .then(res => res.json())
      .then(data => setDevices(data))
      .catch(err => console.error('Failed to refresh devices:', err));
  };

  // =======================
  // Filter and sort devices
  // =======================
  const filteredDevices = devices.filter(device =>
    [device.hostname, device.ip, device.mac, device.status]
      .join(' ')
      .toLowerCase()
      .includes(searchTerm.toLowerCase())
  );

  const sortedDevices = [...filteredDevices].sort((a, b) => {
    const valA = a[sortKey] ?? '';
    const valB = b[sortKey] ?? '';
    return sortOrder === 'asc' ? valA.localeCompare(valB) : valB.localeCompare(valA);
  });

  // =======================
  // Row style based on status
  // =======================
  const getRowStyle = (status, duration) => {
    if (status === 'blocked') return 'bg-red-50 dark:bg-red-900';
    if (status === 'scheduled') return 'bg-yellow-50 dark:bg-yellow-900';
    if (status === 'online' && duration?.includes('day')) return 'bg-green-100 dark:bg-green-900';
    if (status === 'online') return 'bg-green-50 dark:bg-green-800';
    return '';
  };

  // =======================
  // Sort toggle handler
  // =======================
  const toggleSort = (key) => {
    if (sortKey === key) setSortOrder(prev => (prev === 'asc' ? 'desc' : 'asc'));
    else {
      setSortKey(key);
      setSortOrder('asc');
    }
  };

  // =======================
  // Pagination logic
  // =======================
  const totalPages = Math.ceil(sortedDevices.length / itemsPerPage);
  const paginatedDevices = sortedDevices.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  const goToNext = () => currentPage < totalPages && setCurrentPage(prev => prev + 1);
  const goToPrev = () => currentPage > 1 && setCurrentPage(prev => prev - 1);

  // =======================
  // JSX render
  // =======================
  return (
    <div className="p-6 max-w-screen-lg mx-auto">
      <h1 className="text-4xl font-bold mb-6 text-center text-gray-800 dark:text-gray-100">
        Router Guardian - Device List
      </h1>

      {/* Connected Wi-Fi SSID */}
      <div className="text-center mb-3">
        <span className="inline-block px-4 py-2 bg-blue-100 text-blue-900 rounded-full dark:bg-blue-900 dark:text-blue-100 shadow">
          Connected Wi-Fi: <strong>{ssid}</strong>
        </span>
      </div>

      {/* Controls: Search, Auto Refresh, Dark Mode */}
      <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
        <input
          type="text"
          placeholder="🔎 Search by hostname, IP, MAC, status..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full sm:max-w-md border border-gray-300 dark:border-gray-700 rounded-lg px-4 py-2 shadow-sm focus:outline-none focus:ring focus:border-blue-300"
        />
        <div className="flex items-center gap-4">
          <button
            onClick={() => setRefreshOn(prev => !prev)}
            className={`px-4 py-2 rounded-lg shadow text-white ${refreshOn ? 'bg-green-600' : 'bg-gray-500'} hover:opacity-90 transition`}
          >
            {refreshOn ? 'Auto Refresh On' : 'Auto Refresh Off'}
          </button>
          <button
            onClick={() => setDarkMode(prev => !prev)}
            className="px-4 py-2 rounded-lg bg-blue-600 text-white shadow hover:bg-blue-700 transition"
          >
            {darkMode ? '☀ Light Mode' : '🌙 Dark Mode'}
          </button>
        </div>
      </div>

      {/* Device Table */}
      <div className="overflow-x-auto rounded-xl shadow-md">
        <table className="min-w-full table-auto text-sm border-collapse text-center">
          <thead className="sticky top-0 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 font-semibold">
            <tr>
              <th className="p-3 border" onClick={() => toggleSort('hostname')}>Hostname</th>
              <th className="p-3 border" onClick={() => toggleSort('ip')}>IP</th>
              <th className="p-3 border" onClick={() => toggleSort('mac')}>MAC</th>
              <th className="p-3 border" onClick={() => toggleSort('status')}>Status</th>
              <th className="p-3 border" onClick={() => toggleSort('online_duration')}>Online Duration</th>
              <th className="p-3 border">Blocked</th>
              <th className="p-3 border">Action</th>
            </tr>
          </thead>
          <tbody>
            {paginatedDevices.length > 0 ? (
              paginatedDevices.map((device, i) => {
                const isBlocked = device.status === 'blocked' || device.status === 'scheduled';
                return (
                  <tr
                    key={i}
                    className={`${getRowStyle(device.status, device.online_duration)} border-b border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-800`}
                  >
                    <td className="p-3 border">{device.hostname || 'Unknown'}</td>
                    <td className="p-3 border">{device.ip}</td>
                    <td className="p-3 border">{device.mac}</td>
                    <td className="p-3 border capitalize">{device.status}</td>
                    <td className="p-3 border">{formatDuration(device.online_duration)}</td>
                    <td className="p-3 border">{isBlocked ? 'Yes' : 'No'}</td>
                    <td className="p-3 border">
                      {isBlocked ? (
                        <button
                          onClick={() => handleUnblock(device.mac)}
                          disabled={isLoading}
                          className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded shadow"
                        >
                          Unblock
                        </button>
                      ) : (
                        <button
                          onClick={() => handleBlock(device.mac)}
                          disabled={isLoading}
                          className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded shadow"
                        >
                          Block
                        </button>
                      )}
                    </td>
                  </tr>
                );
              })
            ) : (
              <tr>
                <td colSpan="7" className="p-6 text-center text-gray-500 dark:text-gray-400 italic">
                  No devices found.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="flex justify-center items-center gap-4 mt-6">
        <button
          onClick={goToPrev}
          disabled={currentPage === 1}
          className="px-3 py-1 rounded bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 disabled:opacity-50"
        >
          ⬅ Prev
        </button>
        <span className="text-gray-700 dark:text-gray-300">
          Page {currentPage} of {totalPages}
        </span>
        <button
          onClick={goToNext}
          disabled={currentPage === totalPages}
          className="px-3 py-1 rounded bg-gray-300 dark:bg-gray-700 hover:bg-gray-400 dark:hover:bg-gray-600 disabled:opacity-50"
        >
          Next ➡
        </button>
      </div>

      {/* View Mode Switch */}
      <div className="flex justify-center items-center gap-4 mt-8">
        {['mobile', 'tablet', 'laptop'].map(mode => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            className={`px-4 py-2 rounded-full shadow text-white transition ${
              viewMode === mode ? 'bg-blue-600' : 'bg-gray-400 hover:bg-gray-500'
            }`}
          >
            {mode === 'mobile' && '📱'}
            {mode === 'tablet' && '📲'}
            {mode === 'laptop' && '💻'}
          </button>
        ))}
      </div>
    </div>
  );
}

export default App;
