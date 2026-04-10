import React from 'react';
import { Activity, Cpu } from 'lucide-react';
import sentinalLogo from '../assets/Sentinal_logo.png';

const Header: React.FC = () => {
  return (
    <header className="glass-header">
      <div className="header-content">
        <div className="logo-section">
          <div className="logo-icon" style={{ padding: 0, overflow: 'hidden' }}>
            <img src={sentinalLogo} alt="SentinelAI Logo" style={{ width: '56px', height: '56px', objectFit: 'cover', borderRadius: '0.75rem' }} />
          </div>
          <div className="logo-text">
            <h1>SentinelAI</h1>
            <p className="subtitle">Security Automation & Intelligence</p>
          </div>
        </div>
        
        <div className="header-status">
          <div className="status-item">
            <Activity size={18} />
            <span>SOC Core: Active</span>
          </div>
          <div className="status-item">
            <Cpu size={18} />
            <span>Mcp-Server: Online</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
