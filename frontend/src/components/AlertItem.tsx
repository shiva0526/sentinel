import React from 'react';
import { Alert } from '../types';

interface AlertItemProps {
  alert: Alert;
}

const AlertItem: React.FC<AlertItemProps> = ({ alert }) => {
  const verdict = alert.verdict || 'UNKNOWN';

  return (
    <div className="alert-item">
      <div className="alert-header">
        <strong className="alert-desc">{alert.type}</strong>
        <span className={`badge ${verdict}`}>{verdict}</span>
      </div>
      <p className="alert-desc" style={{ fontSize: '1rem', fontWeight: 500, color: 'var(--text-main)', opacity: 0.9 }}>
        {alert.description}
      </p>
      <p className="alert-exp">
        <em>AI Explanation:</em> {alert.explanation || 'No explanation provided.'}
      </p>
      <div className="alert-meta">
        <span>IP: {alert.ip || 'N/A'}</span>
        <span>Source: {alert.source}</span>
        <span>Raw Severity: {alert.raw_severity}</span>
      </div>
    </div>
  );
};

export default AlertItem;
