import React from 'react';

interface MetricCardProps {
  title: string;
  value: number;
  isCritical?: boolean;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, isCritical }) => {
  return (
    <div className={`metric-card ${isCritical ? 'critical' : ''}`}>
      <h3>{title}</h3>
      <p className="value">{value}</p>
    </div>
  );
};

export default MetricCard;
