import axios from 'axios';

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 15000,
});

export const getTargets = async () => {
  const { data } = await api.get('/targets');
  return data as { target: string; sessions: string[] }[];
};

export const getReportUrl = (target: string, session: string) =>
  `${API_BASE}/report/${encodeURIComponent(target)}/${encodeURIComponent(session)}`;

export const getStatus = async (scanId: string) => {
  const { data } = await api.get(`/status/${scanId}`);
  return data as { scan_id: string; lines: string[] };
};

export const getToolStatus = async () => {
  const { data } = await api.get('/tools');
  return data as Record<string, boolean>;
};

export const startScan = async (target: string, mode: string) => {
  const { data } = await api.post('/scan', { target, mode });
  return data as { scan_id: string; target: string; mode: string; status: string };
};

export const getCurrentScan = async () => {
  const { data } = await api.get('/scan/current');
  return data as { scan_id: string | null; target: string | null; mode: string | null; status: string; phase: string | null; started_at: string | null };
};

export const getScanHistory = async () => {
  const { data } = await api.get('/scan/history');
  return data as { scan_id: string; target: string; mode: string; status: string; phase: string | null; started_at: string | null }[];
};
