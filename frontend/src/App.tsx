import { useState } from 'react';
import { runScan, triggerService } from './api';
import { ScanResponse, Notification } from './types';
import Hero from './components/Hero';
import Header from './components/Header';
import MetricCard from './components/MetricCard';
import AlertItem from './components/AlertItem';
import ServiceHexGrid from './components/ServiceHexGrid';
import NotificationModal from './components/NotificationModal';
import { Terminal, Shield } from 'lucide-react';

function App() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<ScanResponse | null>(null);
  const [activeService, setActiveService] = useState<string | null>(null);
  const [serviceResult, setServiceResult] = useState<string | null>(null);
  const [notification, setNotification] = useState<Notification | null>(null);

  const handleScan = async (url: string) => {
    setLoading(true);
    setData(null);
    setNotification(null);
    try {
      const response = await runScan(url);
      setData(response);
      if (response.notification) {
        setNotification(response.notification);
      }
    } catch (error) {
      alert('Error running scan. Is the API server running?');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleTriggerService = async (name: string) => {
    setActiveService(name);
    try {
      const response = await triggerService(name);
      setServiceResult(response.result);
    } catch (error) {
      alert('Error connecting to service agent.');
    } finally {
      setActiveService(null);
    }
  };

  const closeModals = () => {
    setNotification(null);
    setServiceResult(null);
  };

  return (
    <div className="page-root">
      {/* ── STICKY HEADER ─────────────────────────────────── */}
      <Header />

      {/* ── HERO SECTION ─────────────────────────────────────── */}
      <Hero onScan={handleScan} isLoading={loading} />

      {/* ── SOLID DARK CONTENT AREA ───────────────────────── */}
      <main className="dark-section">
        <div className="container">

          {/* Loading indicator */}
          {loading && (
            <div id="loader">
              <div className="spinner"></div>
              <p>Agents are running… This might take a minute.</p>
            </div>
          )}

          {/* Results */}
          {data && (
            <div id="results">
              <div className="metrics">
                <MetricCard title="Total Alerts" value={data.total_alerts} />
                <MetricCard title="Critical" value={data.critical} isCritical />
                <MetricCard title="Suspicious" value={data.suspicious} />
                <MetricCard title="False Positives" value={data.false_positives} />
              </div>

              <div className="report-section">
                <h2><Terminal size={20} /> Incident Intelligence Report</h2>
                <pre id="reportText">{data.report || 'No report available.'}</pre>
              </div>

              <div className="alerts-section">
                <h2><Shield size={20} /> Forensic Alert Logs</h2>
                <div id="alertsList">
                  {data.alerts.map((alert, idx) => (
                    <AlertItem key={alert.id || idx} alert={alert} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Services */}
          <ServiceHexGrid onTrigger={handleTriggerService} activeService={activeService} />

        </div>
      </main>

      <NotificationModal
        notification={notification}
        serviceResult={serviceResult}
        serviceName={serviceResult ? 'Intelligence Report' : null}
        onClose={closeModals}
      />
    </div>
  );
}

export default App;
