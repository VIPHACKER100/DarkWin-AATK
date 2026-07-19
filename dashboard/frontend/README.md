# DARKWIN Dashboard — Frontend

Next.js 16 web UI for monitoring and controlling DARKWIN scan pipelines in real time.

## Prerequisites

- Node.js 18+
- DARKWIN backend running (`darkwin dashboard` or `python dashboard/backend/app.py`)

## Setup

```bash
npm install
npm run dev        # dev server on http://localhost:3000
```

## Env Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | `http://localhost:5000` | Backend REST API base URL |
| `NEXT_PUBLIC_SOCKET_URL` | `http://localhost:5000` | Socket.IO server URL |

## Design System

| Token | Value | Usage |
|-------|-------|-------|
| Font (display) | **Calistoga** | Headings, section titles |
| Font (UI) | **Inter** | Body text, UI elements |
| Font (labels) | **JetBrains Mono** | Section labels, badges, technical data |
| Accent | `#0052FF → #4D7CFF` | Gradient on CTAs, icons, progress bars |
| Background | `#0a0a0f` | Dark theme canvas |

## Project Structure

```
dashboard/frontend/
├── app/
│   ├── layout.tsx       — Root layout, font loading, metadata
│   ├── page.tsx         — Main dashboard page (full UI)
│   └── globals.css      — Design tokens, utilities, scrollbar
├── components/
│   ├── ui/
│   │   ├── button.tsx   — Button (primary/secondary/ghost/danger)
│   │   ├── card.tsx     — Card (standard/elevated/featured)
│   │   └── input.tsx    — Input with label + focus ring
│   ├── animated-section.tsx  — AnimatedSection, StaggerContainer, StaggerItem
│   └── section-label.tsx     — Badge with pulse dot + monospace label
├── lib/
│   ├── api.ts           — Axios REST client (targets, scan, tools, delete)
│   ├── socket.ts        — Socket.IO client with reconnection
│   └── utils.ts         — cn() classname helper
└── public/              — Static assets
```

## Build for Production

```bash
npm run build
npm start
```
