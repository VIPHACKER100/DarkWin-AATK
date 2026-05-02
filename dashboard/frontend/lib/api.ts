import axios from 'axios';

const API_BASE = 'http://localhost:5000';

export const api = axios.create({
  baseURL: API_BASE,
});

export const getTargets = async () => {
  const response = await api.get('/targets');
  return response.data;
};

export const getReportUrl = (target: string, session: string) => {
  return `${API_BASE}/report/${target}/${session}`;
};

export const getStatus = async (scanId: string) => {
  const response = await api.get(`/status/${scanId}`);
  return response.data;
};
