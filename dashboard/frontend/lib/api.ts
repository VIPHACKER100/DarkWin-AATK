export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

async function request<T>(url: string, opts?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${url}`, opts);
  const data = await res.json();
  if (!res.ok) throw Object.assign(new Error(data?.error || res.statusText), { response: { data } });
  return data;
}

export const getTargets = () =>
  request<{ target: string; sessions: { name: string; hasReport: boolean; modified: string }[] }[]>('/targets');

export const getReportUrl = (target: string, session: string) =>
  `${API_BASE}/report/${encodeURIComponent(target)}/${encodeURIComponent(session)}`;

export const getStatus = (scanId: string) =>
  request<{ scan_id: string; lines: string[] }>(`/status/${scanId}`);

export const getToolStatus = () =>
  request<Record<string, boolean>>('/tools');

export const startScan = (target: string, mode: string) =>
  request<{ scan_id: string; target: string; mode: string; status: string }>('/scan', {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ target, mode }),
  });

export const getCurrentScan = () =>
  request<{ scan_id: string | null; target: string | null; mode: string | null; status: string; phase: string | null; started_at: string | null }>('/scan/current');

export const getScanHistory = () =>
  request<{ scan_id: string; target: string; mode: string; status: string; phase: string | null; started_at: string | null }[]>('/scan/history');

export const deleteTarget = (target: string) =>
  request<{ deleted: string }>(`/target/${encodeURIComponent(target)}`, { method: 'DELETE' });

export const deleteSession = (target: string, session: string) =>
  request<{ deleted: { target: string; session: string } }>(`/target/${encodeURIComponent(target)}/${encodeURIComponent(session)}`, { method: 'DELETE' });
