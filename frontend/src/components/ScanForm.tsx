import React, { useState } from 'react';
import { ShieldAlert } from 'lucide-react';

interface ScanFormProps {
  onScan: (url: string) => void;
  isLoading: boolean;
}

const ScanForm: React.FC<ScanFormProps> = ({ onScan, isLoading }) => {
  const [url, setUrl] = useState('http://testphp.vulnweb.com');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (url) onScan(url);
  };

  return (
    <form className="scan-form" onSubmit={handleSubmit}>
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="https://yoursite.com"
        required
        disabled={isLoading}
      />
      <button type="submit" disabled={isLoading}>
        {isLoading ? (
          <div className="spinner" style={{ width: '20px', height: '20px', margin: 0, borderWidth: '2px' }}></div>
        ) : (
          <>
            <ShieldAlert size={20} />
            Run Analysis
          </>
        )}
      </button>
    </form>
  );
};

export default ScanForm;
