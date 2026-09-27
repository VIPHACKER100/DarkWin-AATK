import axios from 'axios';

export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

const API_TOKEN = process.env.NEXT_PUBLIC_API_TOKEN || '';

export const api = axios.create({ baseURL: API_BASE, timeout: 15000 });

api.interceptors.request.use((config) => {
  if (API_TOKEN) {
    config.headers.Authorization = `Bearer ${API_TOKEN}`;
  }
  return config;
});

export interface TargetSession {
  name: string;
  hasReport: boolean;
  modified: string | null;
}

export interface TargetItem {
  target: string;
  sessions: TargetSession[];
}

export interface SystemStats {
  total_targets: number;
  total_sessions: number;
  active_scans: number;
  tools_ready: string;
  tools_installed: number;
  tools_total: number;
  severity_distribution: {
    critical: number;
    high: number;
    medium: number;
    low: number;
    info: number;
  };
  current_scan: CurrentScan;
  recent_activity: CurrentScan[];
}

export interface CurrentScan {
  scan_id: string | null;
  target: string | null;
  mode: string | null;
  status: string;
  phase: string | null;
  started_at: string | null;
  progress: number;
}

export interface TargetAssets {
  target: string;
  subdomains: { host: string; status: number; tech: string[] }[];
  ports: { port: number; protocol: string; service: string; version?: string }[];
  urls: string[];
  emails: string[];
  cloud_assets: string[];
  artifacts: { name: string; path: string; size: number; modified: string }[];
}

export interface VulnerabilityFinding {
  id?: string;
  title: string;
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO';
  target: string;
  category?: string;
  description?: string;
  poc?: string;
  remediation?: string;
  timestamp?: string;
}

export const getTargets = async (): Promise<TargetItem[]> => {
  const { data } = await api.get('/targets');
  return data;
};

export const getStats = async (): Promise<SystemStats> => {
  const { data } = await api.get('/stats');
  return data;
};

export const getTargetAssets = async (target: string): Promise<TargetAssets> => {
  const { data } = await api.get(`/target/${encodeURIComponent(target)}/assets`);
  return data;
};

export const getTargetVulns = async (target: string): Promise<VulnerabilityFinding[]> => {
  const { data } = await api.get(`/target/${encodeURIComponent(target)}/vulns`);
  return data;
};

export const getReportUrl = (target: string, session: string) =>
  `${API_BASE}/report/${encodeURIComponent(target)}/${encodeURIComponent(session)}`;

export const regenerateReport = async (target: string, session: string): Promise<{ status: string; message: string; url: string }> => {
  const { data } = await api.post(`/report/${encodeURIComponent(target)}/${encodeURIComponent(session)}/generate`);
  return data;
};

export const getStatus = async (scanId: string) => {
  const { data } = await api.get(`/status/${scanId}`);
  return data as { scan_id: string; lines: string[] };
};

export const getToolStatus = async (): Promise<Record<string, boolean>> => {
  const { data } = await api.get('/tools');
  return data;
};

export const getToolsDetailed = async (): Promise<Record<string, { path: string; installed: boolean; category?: string }>> => {
  const { data } = await api.get('/api/tools/detailed');
  return data;
};

export const startScan = async (target: string, mode: string) => {
  const { data } = await api.post('/scan', { target, mode });
  return data as { scan_id: string; target: string; mode: string; status: string };
};

export const stopScan = async () => {
  const { data } = await api.post('/scan/stop');
  return data as { status: string; scan_id?: string };
};

export const getCurrentScan = async (): Promise<CurrentScan> => {
  const { data } = await api.get('/scan/current');
  return data;
};

export const getScanHistory = async (): Promise<CurrentScan[]> => {
  const { data } = await api.get('/scan/history');
  return data;
};

export const deleteTarget = async (target: string) => {
  const { data } = await api.delete(`/target/${encodeURIComponent(target)}`);
  return data as { deleted: string };
};

export const deleteSession = async (target: string, session: string) => {
  const { data } = await api.delete(`/target/${encodeURIComponent(target)}/${encodeURIComponent(session)}`);
  return data as { deleted: { target: string; session: string } };
};

export const getConfig = async (): Promise<Record<string, unknown>> => {
  const { data } = await api.get('/api/config');
  return data;
};

export const saveConfig = async (configData: Record<string, unknown>): Promise<Record<string, unknown>> => {
  const { data } = await api.post('/api/config', configData);
  return data;
};
