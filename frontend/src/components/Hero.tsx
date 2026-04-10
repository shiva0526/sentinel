import React from 'react';
import Beams from './Beams';
import ScanForm from './ScanForm';

interface HeroProps {
  onScan: (url: string) => void;
  isLoading: boolean;
}

const Hero: React.FC<HeroProps> = ({ onScan, isLoading }) => {
  return (
    <section className="hero-section">
      {/* Animated background — scoped to hero only */}
      <Beams />

      {/* Gradient overlay fading hero → solid black */}
      <div className="hero-fade" />

      {/* Hero content */}
      <div className="hero-content">
        <p className="hero-eyebrow">AI-Powered Security Intelligence</p>
        <h1 className="hero-title">
          Detect. Analyze.<br />Neutralize.
        </h1>
        <p className="hero-subtitle">
          Enter a target URL below to launch a full multi-agent forensic investigation.
        </p>
        <div className="hero-scan-wrap">
          <ScanForm onScan={onScan} isLoading={isLoading} />
        </div>
      </div>
    </section>
  );
};

export default Hero;
