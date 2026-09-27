import { io } from 'socket.io-client';

const SOCKET_URL = process.env.NEXT_PUBLIC_SOCKET_URL || 'http://localhost:5000';

// Optional token matching the backend DARKWIN_API_TOKEN (set both).
const API_TOKEN = process.env.NEXT_PUBLIC_API_TOKEN || '';

export const socket = io(SOCKET_URL, {
  autoConnect: false,
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 2000,
  reconnectionDelayMax: 10000,
  timeout: 10000,
  ...(API_TOKEN ? { auth: { token: API_TOKEN } } : {}),
});
