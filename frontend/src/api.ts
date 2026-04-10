import { ScanResponse, ServiceResponse, Incident } from './types';

const API_BASE_URL = 'http://127.0.0.1:8000';

export const runScan = async (url: string): Promise<ScanResponse> => {
  const response = await fetch(`${API_BASE_URL}/scan`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url }),
  });

  if (!response.ok) {
    throw new Error('Failed to run scan');
  }

  return response.json();
};

export const triggerService = async (name: string): Promise<ServiceResponse> => {
  const response = await fetch(`${API_BASE_URL}/trigger_service`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });

  if (!response.ok) {
    throw new Error('Failed to trigger service');
  }

  return response.json();
};

export const getIncidents = async (): Promise<Incident[]> => {
  const response = await fetch(`${API_BASE_URL}/incidents`);
  if (!response.ok) {
    throw new Error('Failed to fetch incidents');
  }
  const data = await response.json();
  return data.incidents;
};

export const getReport = async (): Promise<string> => {
  const response = await fetch(`${API_BASE_URL}/report`);
  if (!response.ok) {
    throw new Error('Failed to fetch report');
  }
  const data = await response.json();
  return data.report;
};
