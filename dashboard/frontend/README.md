# DARKWIN Dashboard — Frontend

Next.js web UI for monitoring DARKWIN scan pipelines in real time.

## Prerequisites

- Node.js 18+
- DARKWIN backend running (`darkwin dashboard` or `python dashboard/backend/app.py`)

## Getting Started

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The frontend connects to the Flask backend at `http://localhost:5000` for REST API
data and Socket.IO real-time log streaming.

## Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
app/          — Next.js App Router pages and layouts
lib/          — API client (api.ts) and Socket.IO client (socket.ts)
public/       — Static assets
```
