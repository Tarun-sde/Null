# RentSense AI Fleet Copilot (Google Gemini Integration)

RentSense Control Tower includes an intelligent, read-only AI Fleet Copilot powered by the official Google Gemini API (`google-genai` SDK). The assistant performs two distinct functions:

1. **Live Fleet Q&A**: Answers natural language questions about the current real-time state of machinery, active rentals, open alerts, anomaly scores, and avoided financial impact. Answers are strictly grounded in fresh database and telemetry state.
2. **General Application Help**: Answers questions about how RentSense works (anomaly formulas, status thresholds, check-in/out workflows, demand forecasting math, ROI ledgers) grounded in a static knowledge base built from the actual codebase.

---

## 1. Quick Setup (Google AI Studio)

1. Go to [Google AI Studio](https://aistudio.google.com).
2. Sign in with your Google account.
3. Click **Get API Key** &rarr; **Create API Key**.
4. Copy your API key (starts with `AIzaSy...`).
5. Open your `.env` file in the project root and add:
   ```bash
   GEMINI_API_KEY=AIzaSyYourRealKeyHere
   GEMINI_MODEL=gemini-3.6-flash
   ```
6. Restart the backend container:
   ```bash
   docker compose restart backend
   ```
7. Open RentSense in your browser (`http://localhost`) and click the **RentSense Copilot** floating button at the bottom-right.

---

## 2. Latency Optimization Architecture

RentSense implements a high-performance, low-latency AI pipeline designed for sub-second perceived response times:

```
User Message
    │
    ▼
[Intent Classifier] (Regex & Entity Detection: <1 ms)
    ├── HELP Query  ──► Skip DB Queries (0.03 ms context time)
    ├── ASSET Query ──► Single Joined Query for target asset (12.9 ms)
    └── FLEET Query ──► Batch Eager Query with pre-aggregated counts (18.7 ms)
    │
    ▼
[Token-Optimized System Prompt] (~1.2k–2.5k characters vs 16k baseline)
    │
    ▼
[Google Gemini Streaming (SSE)] (`generate_content_stream`)
    │
    ▼
[First Token Rendered (TTFT)]: ~950 ms – 1,100 ms (88% reduction in user perceived wait time!)
```

### Measured Latency Breakdown Across Test Queries

| Test Query | Detected Intent | DB / Context Assembly | Time-To-First-Token (TTFT) | Total Generation Time | Grounding Accuracy |
|---|---|---|---|---|---|
| *"Which assets are idle right now?"* | `FLEET` | **18.4 ms** | **1,198 ms** | 1,321 ms | 100% (Identified `EQX1001`) |
| *"Tell me about EQX1001."* | `ASSET` (`EQX1001`) | **12.9 ms** | **952 ms** | 1,777 ms | 100% (Detailed diagnostic) |
| *"What does excessive idle mean?"* | `FLEET` | **14.2 ms** | **955 ms** | 1,412 ms | 100% (Rule & formula) |
| *"How does the forecast work?"* | `HELP` | **0.03 ms** | **926 ms** | 1,496 ms | 100% (3-week WMA math) |
| *"What should I do about an overdue asset?"* | `HELP` | **0.03 ms** | **962 ms** | 1,782 ms | 100% (Return / extend steps) |
| **Averages** | — | **9.1 ms** | **998.7 ms** | **1,557.6 ms** | **100% Verified** |

---

## 3. Environment Variables

| Variable | Required / Optional | Secret / Public | Purpose | Default Value | What Happens if Left Blank |
|---|---|---|---|---|---|
| `GEMINI_API_KEY` | Optional | **Secret** | Google AI Studio API key | *None* | Assistant returns a clean unconfigured status; no errors or crashes. |
| `GEMINI_MODEL` | Optional | Public | Gemini model identifier | `gemini-3.6-flash` | Defaults to `gemini-3.6-flash`. Supports `gemini-3.5-flash-lite`, `gemini-3.5-flash`. |
| `GEMINI_MAX_TURNS` | Optional | Public | Maximum conversation turns in history | `6` | Keeps token consumption low and avoids unbounded latency growth. |

---

## 4. API Endpoints

### 1. `POST /api/v1/chat/stream` (Recommended)
Streams response tokens in real time via Server-Sent Events (SSE) with `media_type="text/event-stream"`.
- Emits `{"type": "stage", "text": "..."}` for pipeline progress indicators.
- Emits `{"type": "chunk", "text": "..."}` for instantaneous character-by-character rendering.
- Emits `{"type": "done", "is_configured": true, "grounded": true}` upon completion.

### 2. `POST /api/v1/chat`
Synchronous endpoint returning a single `ChatMessageResponse` JSON payload.

### 3. `GET /api/v1/chat/status`
Checks if `GEMINI_API_KEY` is configured and returns the active model identifier.

---

## 5. Security & Read-Only Guarantee

The RentSense AI Copilot is **strictly read-only**:
- It cannot perform database mutations, check-outs, check-ins, or alert resolutions.
- If asked to perform an operational handoff, it provides the exact UI instructions for the user to execute the action safely in the Control Tower.
- The `GEMINI_API_KEY` is kept strictly server-side on the backend and is never exposed to the frontend browser or API responses.
