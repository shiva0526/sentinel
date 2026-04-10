import React from 'react';
import { Notification } from '../types';

interface NotificationModalProps {
  notification: Notification | null;
  onClose: () => void;
  serviceResult?: string | null;
  serviceName?: string | null;
}

const NotificationModal: React.FC<NotificationModalProps> = ({
  notification,
  onClose,
  serviceResult,
  serviceName,
}) => {
  if (!notification && !serviceResult) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-icon">{serviceResult ? '⚡' : '🔔'}</div>
        <h2>{serviceResult ? `SERVICE ACTIVATED: ${serviceName}` : 'AUTONOMOUS NOTIFICATION'}</h2>
        
        <p style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '1rem', background: 'none' }}>
          {serviceResult 
            ? 'Sentinel Intelligence Report Ready:' 
            : 'The following incident alert has been sent to the website owner:'}
        </p>

        <div className="modal-content">
          {serviceResult || notification?.message}
        </div>

        {notification && (
          <p className="modal-priority">PRIORITY: {notification.priority}</p>
        )}

        <button className="modal-close-btn" onClick={onClose}>
          Close Preview
        </button>
      </div>
    </div>
  );
};

export default NotificationModal;
