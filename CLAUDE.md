# CLAUDE.md — Space Mission Design Game (NASA Space Apps Challenge 2026)

Notes for Claude Code sessions run by the Tech Lead. Since 2026-11-14 the whole team works together on the Tech Lead's PC through Claude Code; teammates no longer edit or push files from their own machines (the old per-person Gemini workflow is retired).

## Project
- Python + Streamlit game: pick a target (Moon, Venus, Mars, Psyche, Europa, Titan), science objectives and an orbit; design a spacecraft (rocket, power, battery, flight computer, attitude control, radiation shield, comms antenna, ground station, instruments); launch; get a report card, post-mission analysis and the closest real NASA mission. Single player only (team mode was removed on 2026-11-14). Difficulties easy / normal / hard (random design twist) / sandbox. Space School (learn), Leaderboard and Share tabs.
- Repo: https://github.com/se-250717020/space-mission-game (branch `main`). Deploys to Streamlit Community Cloud with main file `app.py`: https://space-mission-game.streamlit.app/ (auto-redeploys on every push to `main`).
- The 4-person team is on its first hackathon, with no web experience. The user is the Tech Lead and speaks Turkish, so reply in Turkish.
- The UI was redesigned on 2026-11-14 as a dark, minimal, kid-friendly game: 4-step flow, colored `st.progress` resource bars instead of numbers, 1-3 emoji part ratings (`calc.part_ratings`), simple engineer tips, and every technical detail inside `st.expander("📚 Why? (Learn more)")`. Keep on-screen text short and simple enough for a primary-school kid. Further visual polish is done together with the user.

## Files
| File | Role |
|---|---|
| `data.py` | Pure data dicts + `validate_schema()` |
| `calculations.py` | Pure functions, **no `import streamlit`**; public API documented in its top docstring |
| `app.py`, `assets/`, `.streamlit/config.toml` | Whole Streamlit UI (solo only; dark theme, 4-step flow, CSS at the end of `app.py`; on-screen word tables `CHECK_WORDS`, `MAIN_GAUGE_WORDS`, `RATING_WORDS`, `DELTA_WORDS`) |
| `AI_CONTEXT.md`, `requirements.txt`, `.gitignore`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md` | Contract and docs |

Data flow: `data.py` → `calculations.py` → `app.py`. The shared contract is `AI_CONTEXT.md`: every data key, the 15-key `selection` dict (`data.SELECTION_KEYS`; `calculations.normalize_selection` fills missing keys so old 8-key selections still work), public functions and their result dicts. `data.CHECK_IDS` fixes the 12 check ids in order; each difficulty's `active_checks` decides which are scored.

## Contract rules
- All identifiers, IDs, dict keys **and all on-screen text are English**. Code comments and team docs (`README.md`, `TEAM_RULES.md`, `AI_CONTEXT.md`) are Turkish.
- Never rename or delete existing dict keys, IDs, public function names/parameters, or returned dict keys. Adding new items is fine.
- `app.py` does no math; it asks `calculations.py` for every number.
- If the contract changes, update `AI_CONTEXT.md` and the `calculations.py` docstring together (plus the `README.md` rules table if game rules change).
- Widget keys: `s_<key>`; widgets stay in sync with `single_design` through the `_sync` / `_seen` pattern in `app.py`. `data.TEAM_ROLES` and the calc team functions stay (contract) but the UI no longer uses them.

## Checks before any commit
```bash
.venv\Scripts\python.exe data.py          # must print the ✅ schema check
.venv\Scripts\python.exe calculations.py  # self-test must pass
.venv\Scripts\python.exe -m streamlit run app.py
```
- Preview config is in `.claude/launch.json` (name `streamlit`, port 8502). Streamlit caches imported modules, so restart the server after editing `data.py` or `calculations.py`.
- Check the UI at desktop and mobile width (preset `mobile`).
- Balance rule: every mission must be passable by at least one design on every difficulty and twist, but not trivially.

## Git
- **Ask the user before every commit and push.** The repo is shared.
- Run `git fetch` and check for unexpected commits before pushing. Never use `--force` or `reset --hard`.
- Stage specific files (`git add <file>`), not `git add .`.
