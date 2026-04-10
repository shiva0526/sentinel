export interface Alert {
  id: string;
  type: string;
  description: string;
  explanation: string;
  ip: string;
  source: string;
  raw_severity: string;
  verdict: 'CRITICAL' | 'SUSPICIOUS' | 'FALSE_POSITIVE' | 'UNKNOWN';
}

export interface Notification {
  to: string;
  timestamp: string;
  priority: string;
  message: string;
}

export interface ScanResponse {
  total_alerts: number;
  critical: number;
  suspicious: number;
  false_positives: number;
  report: string;
  alerts: Alert[];
  notification: Notification | null;
}

export interface ServiceResponse {
  service: string;
  result: string;
}

export interface Incident {
  mcp_logged?: boolean;
  timestamp: string;
  alert_id: string;
  type: string;
  description: string;
  ip: string;
  verdict: string;
}
