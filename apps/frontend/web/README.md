# AgroSpace — Web Frontend

An educational storytelling and decision-making web application developed for the NASA Space Apps Challenge. Inspired by [Saving Satoshi](https://savingsatoshi.com/en/chapters), **AgroSpace** translates Earth Observation datasets (NASA POWER, satellite vegetation indexes, soil and climate indicators) into accessible visual chapters, spoken dialogues, and interactive farming challenges adapted to Mozambique (Gaza, Tete, and Zambézia).

---

## 1. Tech Stack

- **Framework:** [React 19](https://react.dev/) + [TypeScript](https://www.typescriptlang.org/)
- **Build Tool & Dev Server:** [Vite](https://vite.dev/)
- **Icons:** [lucide-react](https://lucide.dev/) + custom vector badges
- **Speech Synthesis:** Web Speech API TTS (`speechSynthesis`) with multi-accent support (Portuguese / English)
- **Styling:** Modular native CSS with responsive variables, dark space theme, and accessible touch controls
- **Linting:** [Oxlint](https://oxc.rs/docs/guide/usage/linter.html)

---

## 2. Architecture & Directory Structure

```
apps/frontend/web/
├── public/                 # Static assets and icons
├── src/
│   ├── assets/             # Scene graphics, hero banners, and vector assets
│   ├── components/         # React presentation and interactive components
│   │   ├── Challenges.tsx      # Interactive mini-game engine (quizzes, maps, soil tests, etc.)
│   │   ├── ChaptersPage.tsx    # Chapter selection grid, status banner, region chips
│   │   ├── PlayPage.tsx        # Chapter player, scene stage, dialogue dock, speech synthesis
│   │   ├── LanguageSwitch.tsx  # Quick language toggle (PT / EN)
│   │   ├── SceneArt.tsx        # Dynamic illustration renderer per scene/speaker
│   │   └── Icon.tsx            # Accessible icon helper
│   ├── content/            # Local chapters and story slide definitions
│   │   ├── chapters.ts         # 12 Chapter metadata and visual accents
│   │   ├── story.ts            # Slide narrative sequences and challenge triggers
│   │   └── helpers.ts          # Story slide creation utilities
│   ├── services/           # Backend API integration client
│   │   └── api.ts              # FastAPI client (health, regions, AI hints, indicators)
│   ├── translations/       # Multilingual dictionary
│   │   ├── challenges.ts       # Challenge questions and options (PT/EN)
│   │   └── story.ts            # Narrative dialogues (PT/EN)
│   ├── App.tsx             # Root application orchestrator
│   ├── i18n.ts             # Internationalization helpers
│   ├── main.tsx            # Vite entry point
│   ├── progress.ts         # LocalStorage persistence & save file state
│   ├── speech.ts           # Speech synthesis audio driver
│   └── types.ts            # Shared TypeScript domain types
├── index.html              # HTML shell
├── package.json            # Scripts and dependencies
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite configuration with backend proxy
```

---

## 3. Backend Integration & Offline Resilience

The frontend is built to communicate with the **AgroSight FastAPI** backend (`apps/backend`):

- **Configurable API Endpoint:** Controlled via `VITE_API_URL` (defaults to `/api/v1` or `http://localhost:8000/api/v1`).
- **Development Proxy:** Configured in `vite.config.ts` to forward `/api` and `/health` requests to `http://localhost:8000`.
- **Health & Connectivity Badge:** On startup, the frontend polls `/health`. When connected, a green `🛰️ Connected (Region)` badge appears; if the backend is unavailable, it gracefully shifts to `📡 Offline Mode`.
- **Regional Context:** Pulls agricultural study regions (`/api/v1/regions` — Gaza, Tete, Zambézia) and allows players to switch context.
- **AI Scientific Hints:** During complex farming challenges, players can request deterministic AI hints (`/api/v1/ai/hint`) rooted in NASA POWER and CENACARTA data.
- **Zero-Failure Offline Fallback:** If the network is absent, player progress is safely stored in `localStorage` (`agrospace-progress-v1`), and all 12 chapters remain fully playable.

---

## 4. Development & Running Locally

### Prerequisites
- Node.js >= 20
- npm or pnpm

### Installation
```bash
cd apps/frontend/web
npm install
```

### Running the Development Server
```bash
npm run dev
```
The application will be served at `http://localhost:3000` (or `http://localhost:5173`).

### Production Build & Linting
```bash
# Type check and build production bundle into dist/
npm run build

# Run Oxlint
npx oxlint src

# Preview production build locally
npm run preview
```

---

## 5. Environment Variables

Create `.env` in `apps/frontend/web/` or rely on the root `.env`:

| Variable | Description | Default |
|---|---|---|
| `VITE_API_URL` | Base URL for backend API requests | `/api/v1` |
| `VITE_BACKEND_URL` | Dev proxy destination in `vite.config.ts` | `http://localhost:8000` |
| `VITE_PORT` | Local dev server port | `3000` |

---

## 6. Educational Design

The 12 chapters guide smallholder farmers and students through real-world space agricultural concepts:
1. **The Arrival:** The value of space-based earth observation.
2. **Eyes from Space:** Remote sensing, satellites, and orbit basics.
3. **The Rainfall Mystery:** Rainfall variability, NASA POWER precipitation metrics.
4. **The Heat Wave:** Temperature anomalies and evaporative stress.
5. **The Last Drop:** Soil moisture and water conservation techniques.
6. **The Green Signal:** NDVI and vegetation health indexes.
7. **Beneath Our Feet:** Soil types, organic matter, and erosion control.
8. **The Crop Academy:** Crop cycles, drought-resistant varieties.
9. **The Rotation Lab:** Legume-cereal crop rotation and nutrient fixing.
10. **The Extreme Mission:** Resilient practices against cyclones and flash floods.
11. **The Farmer's Choice:** Community planning and collective resource stewardship.
12. **The Final Harvest:** Sustainable yields, post-harvest storage, and food security.
