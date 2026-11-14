# CLAUDE.md — Space Mission Design Game (NASA Space Apps Challenge 2026)

Notes for Claude Code sessions run by the Tech Lead. Since 2026-11-14 the whole team works together on the Tech Lead's PC through Claude Code; teammates no longer edit or push files from their own machines (the old per-person Gemini workflow is retired).

## ⚠️ React + FastAPI only (read first)
- **The game is ONLY `frontend/` (React + Vite + Tailwind + Framer Motion) + `backend/main.py` (FastAPI).** Every feature, fix, polish and check happens there.
- The old Streamlit version (`app.py`, `assets/flight.html`, `.streamlit/`, root `requirements.txt`) was deleted from the repo on 2026-11-15. Do not bring it back, run `streamlit` or talk about the streamlit.app site.
- The shared game logic (`data.py`, `calculations.py`, `artwork.py`) is imported by the backend, so changes there still follow the contract rules below.
- Run and check with the `backend` (port 8000) + `frontend` (port 5173) preview servers: http://localhost:5173.

## Project
- Space mission design game: pick a target (Moon, Venus, Mars, Psyche, Europa, Titan), science objectives and an orbit; design a spacecraft (rocket, power, battery, flight computer, attitude control, radiation shield, comms antenna, ground station, instruments); launch; get a report card, post-mission analysis and the closest real NASA mission. Single player only (team mode was removed on 2026-11-14). Difficulties easy / normal / hard (random design twist) / sandbox. Main menu (name, difficulty, Leaderboard, Space School, Options) → 3-column game screen → launch animation → the Science Run mini game when the mission succeeds.
- Repo: https://github.com/se-250717020/space-mission-game (branch `main`). Live on Render (free plan) at https://space-mission-game.onrender.com since 2026-11-15: `Dockerfile` builds `frontend/dist` and `backend/main.py` serves it at `/` next to `/api`; `render.yaml` auto-deploys every push to `main` (so a push changes the live site). Free plan: sleeps after 15 min idle (~1 min cold start) and the disk is not persistent, so the JSON leaderboards reset.
- The 4-person team is on its first hackathon, with no web experience. The user is the Tech Lead and speaks Turkish, so reply in Turkish.
- UI: dark, minimal, kid-friendly. Animated main menu, then a 3-column game screen (left `Workshop` tabs, center `Dashboard` with the workshop scene, resource bars, a systems strip with "Fix it" jumps and a giant LAUNCH button, right `InfoPanel` with Space School info that follows the left selection; a first-time `Coach`). After launch `LaunchSequence.jsx` runs the countdown and flight; on success `MiniGame.jsx` (Science Run: collect science, send it home in Earth's zone, combos, pilot ranks). Colored bars instead of numbers, 1-3 emoji part ratings (`calc.part_ratings`), simple engineer tips, technical details inside "📚 Why? (Learn more)". Keep on-screen text short and simple enough for a primary-school kid. Further visual polish is done together with the user.

## Files
| File | Role |
|---|---|
| `data.py` | Pure data dicts + `validate_schema()` |
| `calculations.py` | Pure functions, no web/UI code; public API documented in its top docstring |
| `artwork.py` | Pure SVG art (reads `data` only): unique look per rocket (`rocket_image`), spacecraft that changes with the chosen parts (`spacecraft_image`), workshop scene (`workshop_scene`) |
| `backend/main.py`, `backend/requirements.txt` | FastAPI server (no math): `GET /api/game-data`, `POST /api/design`, `POST /api/launch`, `GET /api/leaderboard`, `POST /api/flight-score`, `GET /api/flight-leaderboard`; imports the root `data.py` / `calculations.py` / `artwork.py` (AI_CONTEXT.md section 9); serves `frontend/dist` at `/` when it exists |
| `frontend/` | React UI (AI_CONTEXT.md section 7). On-screen word tables in `src/words.js`, sounds and music in `src/sound.js` (Web Audio, no files), API calls in `src/api.js` |
| `Dockerfile`, `.dockerignore`, `render.yaml` | Render deploy (free web service, Frankfurt) |
| `AI_CONTEXT.md`, `.gitignore`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md` | Contract and docs |

Data flow: `data.py` → `calculations.py` → `backend/main.py` → `frontend/` (`artwork.py` reads `data.py` for drawings). The shared contract is `AI_CONTEXT.md`: every data key, the 15-key `selection` dict (`data.SELECTION_KEYS`; `calculations.normalize_selection` fills missing keys so old 8-key selections still work), public functions and their result dicts, and the API. `data.CHECK_IDS` fixes the 12 check ids in order; each difficulty's `active_checks` decides which are scored.

## Contract rules
- All identifiers, IDs, dict keys **and all on-screen text are English**. Code comments and team docs (`README.md`, `TEAM_RULES.md`, `AI_CONTEXT.md`) are Turkish.
- Never rename or delete existing dict keys, IDs, public function names/parameters, returned dict keys or API fields. Adding new items is fine.
- The backend and the frontend do no math; every number comes from `calculations.py`.
- If the contract changes, update `AI_CONTEXT.md` and the `calculations.py` docstring together (plus the `README.md` rules table if game rules change).
- `data.TEAM_ROLES` and the calc team functions stay (contract) but the UI no longer uses them.

## Checks before any commit
```bash
.venv\Scripts\python.exe data.py          # must print the ✅ schema check
.venv\Scripts\python.exe calculations.py  # self-test must pass
cd frontend; npm run build                # React version must build (delete frontend/dist afterwards)
```
- Preview config is in `.claude/launch.json` (use `backend` port 8000 and `frontend` port 5173). The backend runs with `--reload`, so it picks up `data.py` / `calculations.py` edits by itself.
- Check the UI at desktop and mobile width (preset `mobile`).
- Balance rule: every mission must be passable by at least one design on every difficulty and twist, but not trivially.

## Git
- **Ask the user before every commit and push.** The repo is shared, and a push to `main` redeploys the live site.
- Run `git fetch` and check for unexpected commits before pushing. Never use `--force` or `reset --hard`.
- Stage specific files (`git add <file>`), not `git add .`.
