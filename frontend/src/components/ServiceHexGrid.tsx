import React from 'react';

interface ServiceHexGridProps {
  onTrigger: (name: string) => void;
  activeService: string | null;
}

const services = [
  { name: 'Penetration Testing', icon: '💻' },
  { name: 'Security Consulting', icon: '💼' },
  { name: 'Secure Code Reviews', icon: '🔍' },
  { name: 'Threat Emulation', icon: '🕵️' },
  { name: 'Vulnerability Assessments', icon: '🎯' },
  { name: 'Training', icon: '🎓' },
  { name: 'Incident Response', icon: '🚨' },
];

const ServiceHexGrid: React.FC<ServiceHexGridProps> = ({ onTrigger, activeService }) => {
  return (
    <section className="services-section">
      <h2>Security Services</h2>
      <div className="service-grid">
        {services.map((service) => (
          <div
            key={service.name}
            className="service-card"
            onClick={() => onTrigger(service.name)}
          >
            {activeService === service.name ? (
              <div className="spinner" style={{ width: '30px', height: '30px', borderWidth: '3px', marginBottom: '0' }}></div>
            ) : (
              <>
                <div className="service-icon">{service.icon}</div>
                <p className="service-title">{service.name}</p>
              </>
            )}
          </div>
        ))}
      </div>
    </section>
  );
};

export default ServiceHexGrid;
