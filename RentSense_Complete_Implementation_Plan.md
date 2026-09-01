# RentSense Control Tower — Complete Implementation Plan
**Solo Build — Phase by Phase**

This is the execution-level companion to the RD. Each phase has: goal, concrete tasks, commands/scaffolding, and an exit test. Don't move to the next phase until the exit test passes — that's your safety net for a solo 24h build.

---

## Phase 0 — Setup (30–45 min)

**Goal:** Repo, tooling, and hosting accounts exist before you write feature code.

**Tasks:**
- Create repo `rentsense-control-tower` with `frontend/`, `backend/`, `simulator/`, `docs/` folders.
- Backend: `python -m venv venv`, install `fastapi uvicorn sqlalchemy psycopg[binary] pydantic alembic python-dotenv`.
- Frontend: `npx create-next-app@latest frontend --typescript --tailwind --app`, add `shadcn/ui`, `recharts`, `html5-qrcode`.
- Create a Supabase project → grab `DATABASE_URL`.
- Create `.env.example` with every variable from the RD §6 env list.
- Push an empty commit to `main`, create `develop` branch. Work on short-lived feature branches off `develop`.

**Exit test:** `uvicorn main:app --reload` serves an empty FastAPI app; `npm run dev` serves the default Next.js page; both connect to no errors.

---

## Phase 1 — Foundation: Schema, Seed, Core APIs (Hours 0–4)

**Goal:** Real data in a real DB, reachable over HTTP.

**Tasks:**
1. Write SQLAlchemy models for all 9 tables from the RD data model (`equipment`, `rentals`, `telemetry`, `sites`, `operators`, `alerts`, `forecasts`, `recommendations`, `audit_events`).
2. `alembic init alembic`, generate + run initial migration.
3. Write `backend/app/seed/seed.py`:
   - Insert the 7 challenge assets (EQX1001–EQX1007) with type, dealer, daily_rate.
   - Insert 2–3 sites, 3–4 operators.
   - Insert rentals so that EQX1002/EQX1007-equivalents come out **unassigned**, EQX1001-equivalent **under-utilized**, EQX1005-equivalent **high-use**.
   - Make seeding idempotent (`TRUNCATE ... RESTART IDENTITY CASCADE` before insert) — you'll re-run this a lot.
4. Build `GET /api/v1/equipment` and `GET /api/v1/equipment/{id}` (join rentals + latest telemetry + timeline).
5. Build `GET /api/v1/dashboard` (KPI counts by status).
6. Write `services/status_service.py` as a **pure function** `derive_status(rental, telemetry) -> Status` — every other module calls this, nothing stores status redundantly.

**Exit test:** `curl localhost:8000/api/v1/equipment` returns 7 assets with correct derived statuses; re-running the seed script doesn't duplicate or break anything.

---

## Phase 2 — Core UI: Control Tower Dashboard + Asset Detail (Hours 4–8)

**Goal:** This has to read as a control tower, not a generic admin CRUD table. The map moves up from Phase 4 — Phase 2 builds it static with seeded markers, Phase 4 just makes it live. This is a deliberate reordering: it de-risks the map integration early and makes the product look finished well before the intelligence layer exists.

**Design system (define before building any component):**
Use a consistent industrial/enterprise visual language, not default shadcn/dashboard styling. Lock these down first, then build every component against them:
- Typography scale (2–3 weights max, one display font for KPI numbers if you want that "control tower" feel).
- Spacing scale (4/8px-based, applied consistently — no ad-hoc padding per component).
- Border radius — pick one value (or two: cards vs. buttons) and use it everywhere.
- Shadow/elevation — one subtle system for cards vs. modals, not per-component guesses.
- Status color palette — the 6 status colors, defined once as tokens/CSS vars, referenced everywhere (cards, map markers, table rows, badges, charts).
- Chart styling — consistent axis/gridline/tooltip treatment across Recharts instances so KPI, utilization, and forecast charts feel like one system, not three defaults.
- Icon set — pick one (e.g. lucide) and stick to it; don't mix icon styles.
- Button hierarchy — primary/secondary/ghost/destructive, used consistently (e.g. "Resolve" vs "Dismiss" should never look the same weight).
- Responsive breakpoints — desktop and tablet explicitly, since that's what's judged on a laptop/projector.
This is worth 20–30 minutes upfront; it's the difference between "technically has all the features" and "looks like a real product" to judges seeing it for five minutes.

**Layout shell (build once, reuse everywhere):**
- Left sidebar nav: Dashboard / Assets / Scan / Actions / Forecast / Impact.
- Top bar: search, notifications icon (stub), profile/avatar stub.
- Responsive down to tablet width — sidebar collapses to icons, cards reflow to 2-col then 1-col.

**`/dashboard` page — build in this order:**
1. KPI cards (counts per status: active, idle, unassigned, due-soon, overdue).
2. Asset status distribution (donut/bar — Recharts).
3. Fleet map — static Leaflet/MapLibre instance, one marker per seeded asset at its site's lat/lng, colored by status. No live movement yet; that's Phase 4.
4. Utilization chart (engine vs idle hours per asset, current snapshot).
5. Urgent alerts panel (real data once Phase 5 exists; empty-state card until then — don't block the layout on data that doesn't exist yet).
6. Recommended actions panel (same — empty state until Phase 6, but the card and its position in the grid exist now).
7. Recent activity feed (reads from `audit_events`; empty until Phase 3 produces events).
8. Searchable/filterable asset table below the fold — still needed, just not the whole page anymore.

**`/assets/[id]` page:**
- Header: type, name/ID, large status badge.
- Current location mini-map (same static map component, single marker).
- Usage metrics panel (engine/idle/fuel — static until Phase 4 telemetry lands).
- Rental information (site, operator, checkout/due dates).
- Utilization history chart (stub with seeded/flat data until real telemetry accumulates).
- Timeline (empty state until Phase 3 audit events exist).
- Alerts/anomalies panel (empty state until Phase 5).
- AI recommendation panel (empty state until Phase 6).

**Shared components:**
- Status → color mapping (`ACTIVE` green, `IDLE`/`DUE_SOON` amber, `UNASSIGNED`/`OVERDUE` red, `RETURNED` gray) — one component, reused on cards, table, map markers, badges.
- Loading / empty / error states for every panel — several panels above are intentionally empty-state-only in Phase 2, so this isn't optional polish, it's load-bearing from day one.

**Exit test:** Load `/dashboard` and it visually reads as a control tower — sidebar, map with 7 markers, KPI cards, charts, and clearly-labeled empty-state panels for alerts/actions/activity, all using the same typography/spacing/color/shadow tokens (no component looks like it wandered in from a different template). Click into an asset and get a full detail page, not just a name and a status pill.

---

## Phase 3 — Handoff Loop: QR / Manual Check-in-out (Hours 8–11)

**Goal:** The "Act" beat of the demo works end-to-end.

**Tasks:**
1. `POST /api/v1/rentals/checkout` — validate asset is free, create rental row, write `audit_events` row, recompute status.
2. `POST /api/v1/rentals/checkin` — close rental (`checked_in_at`), capture condition note, write audit event, recompute status.
3. `/scan` page: `html5-qrcode` camera reader + a manual equipment-ID text-input fallback that's *always visible*, not hidden behind a "camera not working?" link.
4. Generate printable/displayable QR codes for the 7 seed assets (`qr_code` field → simple QR image, store under `frontend/public/qr/`).
5. Wire the asset detail page's audit timeline to real `audit_events` rows.

**Exit test:** Scan (or manually enter) an asset ID, check it out, confirm the derived status updates according to `derive_status()`'s rules (not a hardcoded value) and a new audit event appears in the timeline; check it back in and confirm it clears from the active list.

---

## Phase 4 — Live Behavior: Telemetry + Realtime (Hours 11–14)

**Goal:** The dashboard feels alive without you touching anything.

**Tasks:**
1. `simulator/telemetry_simulator.py` — every `SIMULATOR_INTERVAL_SECONDS`, POST a telemetry event per active asset to `/api/v1/telemetry` with plausible drifting values (engine_hours, idle_hours, fuel_pct, lat/lng jitter).
2. `POST /api/v1/telemetry` — validate ranges, insert row, recompute status, push update.
3. `services/event_stream.py` — SSE endpoint `GET /api/v1/events/stream` broadcasting status/alert changes; heartbeat every ~15s so dead connections are detectable.
4. Frontend: SSE client hook; on message, patch the relevant asset in state. On SSE error/close, fall back to 5-second polling of `/dashboard` and `/equipment`.
5. Wire the Phase 2 static map to live data: markers move/recolor on SSE update instead of sitting fixed at seed positions.

**Exit test:** Start the simulator, watch dashboard numbers (engine hours, idle hours, status) *and map markers* update live without a manual refresh; kill the SSE connection and confirm polling picks up the slack.

---

## Phase 5 — Intelligence: Anomalies + Forecast (Hours 14–17)

**Goal:** Explainable "AI" outputs, not a black box.

**Tasks:**
1. `analytics/anomaly.py`: implement the 6 rules from RD §2.3 as independent pure functions over an asset's current state; combine into a weighted score (cap 100); return `{signals, score, severity, recommendation, explanation}`.
2. `GET /api/v1/analytics/anomalies` — run rules across all assets, return sorted by score.
3. `analytics/forecast.py`: generate labeled simulated 12–16 week history, weekly-aggregate by site+type, weighted moving average (`0.5/0.3/0.2`), backtest on last 3 weeks (MAE), compute confidence.
4. `GET /api/v1/analytics/forecast` — return predicted units, confidence, backtest error, drivers per site/type/week.
5. Wire alerts: on each telemetry/status change, re-run the relevant rule and upsert into `alerts` table (don't spam duplicate open alerts for the same condition).

**Exit test:** `/api/v1/analytics/anomalies` flags your intentionally-unassigned and intentionally-idle seed assets as critical, each with signals + explanation text; `/api/v1/analytics/forecast` returns a believable weekly prediction with a backtest error number.

---

## Phase 6 — Decision Loop: Recommendations + Impact (Hours 17–19)

**Goal:** Insight converts into a ranked action and a dollar number.

**Tasks:**
1. `services/recommendation.py`: implement the 5 situation→action mappings from RD §2.5; rank by anomaly score / severity.
2. `GET /api/v1/recommendations` — ranked action queue.
3. `POST /api/v1/alerts/{id}/resolve` — apply chosen action (return/reassign/extend/investigate), write audit event, update alert status.
4. `services/impact.py`: `avoided_cost = avoided_days × daily_rate + avoided_transport` — compute as a range; store outcomes as they're resolved so the impact card is cumulative, not recomputed from scratch each time.
5. `/actions` page (the queue, resolve buttons) and `/impact` page (before/after avoided-cost, idle-hours-prevented, utilization delta).

**Exit test:** Resolve the top item in the action queue → status changes, alert closes, `/impact` numbers move.

---

## Phase 7 — Polish, Deploy, Rehearse (Hours 19–24)

**Goal:** Nothing looks broken, the URL is live, you can run the script blind.

**Tasks:**
1. Sweep every page for loading / empty / error / disconnected states — this is the #1 thing that makes a hackathon demo look unfinished.
2. Deploy: frontend → Vercel, backend → Render/Railway, confirm CORS origins match, confirm `DATABASE_URL` env is set on the host, not just locally.
3. Add a one-command reseed (`make reseed` or `npm run seed`) — you will need this right before judging.
4. Warm the hosted API before judging (cold starts kill demos).
5. Run the full acceptance checklist from the RD §7 against the **deployed** URL, not localhost.
6. Rehearse the 5-minute script three times end-to-end; record a backup video and take backup screenshots in case live wifi fails.
7. Tag a `demo-safe` commit/release the moment everything above passes.

**Exit test:** Fresh browser, deployed URL, clean reseed → full 5-minute script runs without touching code.

---

## Quick-reference: what "done" looks like per phase

| Phase | You know you're done when... |
|---|---|
| 0 | Both servers boot with no errors |
| 1 | `curl` returns real seeded assets with correct statuses |
| 2 | Dashboard reads as a control tower (sidebar, static map, KPIs, charts) and every asset has a full detail page |
| 3 | A scan/checkout/checkin round-trip changes status + timeline |
| 4 | Dashboard updates itself while you watch, hands off keyboard |
| 5 | Anomaly + forecast endpoints return explainable, believable JSON |
| 6 | Resolving an action visibly moves the impact number |
| 7 | You can run the whole demo on a strange laptop, cold, from the deployed URL |

If you're behind schedule at any checkpoint, cut inside the phase (fewer rules, simpler forecast, skip polish) rather than skipping ahead — a smaller complete loop beats a bigger broken one.
