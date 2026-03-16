import React, { useState, useEffect } from 'react';
import { 
  Users, 
  Activity, 
  Database, 
  Send, 
  Menu, 
  LogOut, 
  ExternalLink, 
  MessageSquare, 
  ThumbsUp, 
  Repeat,
  RefreshCw,
  Clock
} from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [profiles, setProfiles] = useState([]);
  const [sheetsData, setSheetsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(new Date().toLocaleTimeString());
  const [toasts, setToasts] = useState([]);

  const addToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Auto-refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    setLoading(true);
    try {
      const timestamp = new Date().getTime();
      const [profilesRes, sheetsRes] = await Promise.all([
        axios.get(`${API_BASE}/profiles?t=${timestamp}`),
        axios.get(`${API_BASE}/sheets-status?t=${timestamp}`)
      ]);
      setProfiles(profilesRes.data);
      setSheetsData(sheetsRes.data.entries);
      setLastUpdated(new Date().toLocaleTimeString());
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data:", error);
      addToast("Failed to sync with backend", "error");
      setLoading(false);
    }
  };

  const triggerScrape = async () => {
    setScraping(true);
    addToast("Starting LinkedIn Scraper...", "info");
    try {
      await axios.post(`${API_BASE}/scrape`);
      addToast("Scraper is now running in the background", "success");
    } catch (error) {
      console.error("Error triggering scraper:", error);
      addToast("Failed to start scraper", "error");
    }
    setScraping(false);
  };

  return (
    <div className="app-container">
      {/* Toast Notifications */}
      <div className="toast-container">
        <AnimatePresence>
          {toasts.map(toast => (
            <motion.div
              key={toast.id}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className={`toast toast-${toast.type}`}
            >
              {toast.type === 'success' && <Activity size={18} />}
              {toast.type === 'error' && <Database size={18} />}
              {toast.type === 'info' && <Clock size={18} />}
              <span>{toast.message}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Sidebar */}
      <aside className="sidebar">
        <div className="logo">
          <Activity size={28} />
          <span>LinkedIn Scraper</span>
        </div>
        
        <nav style={{ marginTop: '3rem', flex: 1 }}>
          <motion.div 
            whileHover={{ x: 5 }}
            style={{ display: 'flex', alignItems: 'center', gap: '1rem', color: '#0a66c2', marginBottom: '2rem', cursor: 'pointer' }}
          >
            <Users size={20} />
            <span style={{ fontWeight: 600 }}>Tracked Profiles</span>
          </motion.div>
          <motion.a 
            href="https://docs.google.com/spreadsheets/d/1H68sixKlA1kiqiKc1yv4kapV2UQYEPNz9Pjj5VQwguo/edit?usp=sharing"
            target="_blank"
            rel="noreferrer"
            whileHover={{ x: 5 }}
            style={{ display: 'flex', alignItems: 'center', gap: '1rem', color: '#b0b0b0', marginBottom: '2rem', cursor: 'pointer', textDecoration: 'none' }}
          >
            <Database size={20} />
            <span>Open Google Sheet</span>
          </motion.a>
        </nav>

        <div className="btn btn-primary" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', justifyContent: 'center' }}>
          <LogOut size={18} />
          <span>Sign Out</span>
        </div>
      </aside>

      {/* Main Content */}
      <main className="main-content">
        <header className="header">
          <div>
            <h1>Activity Dashboard</h1>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#b0b0b0', fontSize: '0.9rem' }}>
              <Clock size={14} />
              <span>Last updated: {lastUpdated}</span>
            </div>
          </div>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ color: '#b0b0b0', fontSize: '0.8rem', fontStyle: 'italic' }}>
              Auto-saves to sheet on new posts only
            </span>
            <button 
              className="btn" 
              style={{ background: '#353535', color: 'white', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              onClick={fetchData}
            >
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
              Refresh
            </button>
            <button 
              className="btn btn-primary" 
              onClick={triggerScrape}
              disabled={scraping}
            >
              {scraping ? 'Starting...' : 'Run Scraper Now'}
            </button>
          </div>
        </header>

        {loading && profiles.length === 0 ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
            >
              <RefreshCw size={40} color="#0a66c2" />
            </motion.div>
          </div>
        ) : (
          <>
            <div className="grid">
              <AnimatePresence>
                {profiles.map((profile, index) => (
                  <motion.div 
                    key={profile.url}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="card"
                  >
                    <div className="card-header">
                      {profile.photo_url ? (
                        <img 
                          src={profile.photo_url} 
                          alt={profile.username}
                          className="profile-photo"
                        />
                      ) : (
                        <div className="avatar">
                          {profile.username.charAt(0)}
                        </div>
                      )}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        <h3 style={{ fontSize: '1.1rem', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{profile.username}</h3>
                        <a href={profile.url} target="_blank" rel="noreferrer" style={{ fontSize: '0.8rem', color: '#0a66c2', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.2rem' }}>
                          View Profile <ExternalLink size={12} />
                        </a>
                      </div>
                      <span className="status-badge status-synced">Active</span>
                    </div>
                    
                    <p className="post-content">
                      {profile.last_post}
                    </p>

                    <div className="stats">
                      <div className="stat-item tooltip">
                        <ThumbsUp size={14} /> <span>{profile.stats?.likes || 0}</span>
                      </div>
                      <div className="stat-item tooltip">
                        <MessageSquare size={14} /> <span>{profile.stats?.comments || 0}</span>
                      </div>
                      <div className="stat-item tooltip">
                        <Repeat size={14} /> <span>{profile.stats?.reposts || 0}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>

            <section style={{ marginTop: '3rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.5rem' }}>
                <Database size={24} color="#057642" />
                <h2>Sheet Sync History</h2>
              </div>
              <div className="table-container">
                <table className="sheet-table">
                  <thead>
                    <tr>
                      <th>User</th>
                      <th>Activity</th>
                      <th>Likes</th>
                      <th>Timestamp</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sheetsData.length > 0 ? (
                      sheetsData.map((entry, i) => (
                        <tr key={i}>
                          <td style={{ fontWeight: 600 }}>{entry.user || entry.User || entry.Name || entry["User "] || "Unknown"}</td>
                          <td style={{ color: '#b0b0b0', maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {entry.text || entry.Post || entry.activity || "Activity Recorded"}
                          </td>
                          <td>
                            <div className="stat-item" style={{ color: '#0a66c2' }}>
                              <ThumbsUp size={14} /> {entry.likes || entry.Likes || 0}
                            </div>
                          </td>
                          <td style={{ color: '#b0b0b0', fontSize: '0.85rem' }}>
                            {entry.timestamp || entry.Timestamp || "Recently"}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan="4" style={{ textAlign: 'center', padding: '2rem', color: '#b0b0b0' }}>
                          No recent activity found in Google Sheets.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>
          </>
        )}
      </main>

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .animate-spin {
          animation: spin 1s linear infinite;
        }
      `}} />
    </div>
  );
}

export default App;
