# CLAUDE.md — Space Mission Design Game (NASA Space Apps Challenge 2026)

Notes for Claude Code sessions run by the Tech Lead. Since 2026-11-14 the whole team works together on the Tech Lead's PC through Claude Code; teammates no longer edit or push files from their own machines (the old per-person Gemini workflow is retired).

## Project
- Python + Streamlit game: pick a target (Moon, Venus, Mars, Psyche, Europa, Titan), science objectives and an orbit; design a spacecraft (rocket, power, battery, flight computer, attitude control, radiation shield, comms antenna, ground station, instruments); launch; get a report card, post-mission analysis and the closest real NASA mission. Single player or team mode (up to 4 players on their own devices, one or more roles each). Difficulties easy / normal / hard (random design twist) / sandbox. Learn, Leaderboard and Compare & Share tabs.
- Repo: https://github.com/se-250717020/space-mission-game (branch `main`). Deploys to Streamlit Community Cloud with main file `app.py`: https://space-mission-game.streamlit.app/ (auto-redeploys on every push to `main`).
- The 4-person team is on its first hackathon, with no web experience. The user is the Tech Lead and speaks Turkish, so reply in Turkish.
- Visual UI design is still to be done together with the user; the current UI is functional but plain.

## Files
| File | Role |
|---|---|
| `data.py` | Pure data dicts + `validate_schema()` |
| `calculations.py` | Pure functions, **no `import streamlit`**; public API documented in its top docstring |
| `team_room.py` | `RoomStore` (in-memory shared team rooms, thread-safe), **no `import streamlit`** |
| `app.py`, `assets/` | Whole Streamlit UI; `RoomStore` opened via `st.cache_resource`, live team view via `st.fragment(run_every=3)` |
| `AI_CONTEXT.md`, `requirements.txt`, `.gitignore`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md` | Contract and docs |

Data flow: `data.py` → `calculations.py` → `app.py` (+ `team_room.py`). The shared contract is `AI_CONTEXT.md`: every data key, the 15-key `selection` dict (`data.SELECTION_KEYS`; `calculations.normalize_selection` fills missing keys so old 8-key selections still work), public functions and their result dicts. `data.CHECK_IDS` fixes the 12 check ids in order; each difficulty's `active_checks` decides which are scored.

## Contract rules
- All identifiers, IDs, dict keys **and all on-screen text are English**. Code comments and team docs (`README.md`, `TEAM_RULES.md`, `AI_CONTEXT.md`) are Turkish.
- Never rename or delete existing dict keys, IDs, public function names/parameters, or returned dict keys. Adding new items is fine.
- `app.py` does no math; it asks `calculations.py` for every number.
- If the contract changes, update `AI_CONTEXT.md` and the `calculations.py` docstring together (plus the `README.md` rules table if game rules change).
- Widget keys: single player `s_<key>`, team `t_<key>`; team widgets stay in sync through the `_sync` / `_seen` pattern in `app.py`.

## Checks before any commit
```bash
.venv\Scripts\python.exe data.py          # must print the ✅ schema check
.venv\Scripts\python.exe calculations.py  # self-test must pass
.venv\Scripts\python.exe team_room.py     # must print ✅
.venv\Scripts\python.exe -m streamlit run app.py
```
- Preview config is in `.claude/launch.json` (name `streamlit`, port 8502). Streamlit caches imported modules, so restart the server after editing `data.py`, `calculations.py` or `team_room.py`.
- Test team mode with two browser tabs joining the same room code.
- Balance rule: every mission must be passable by at least one design on every difficulty and twist, but not trivially.

## Git
- **Ask the user before every commit and push.** The repo is shared.
- Run `git fetch` and check for unexpected commits before pushing. Never use `--force` or `reset --hard`.
- Stage specific files (`git add <file>`), not `git add .`.
