# CLAUDE.md — Space Mission Design Game (NASA Space Apps Challenge 2026)

Notes for Claude Code sessions run by the Tech Lead. Teammates use Gemini (not Claude): they upload `AI_CONTEXT.md` plus their own file and use the prompt in `TEAM_RULES.md` section D, then push their file. This file is only for Claude Code.

## Project
- Python + Streamlit game: pick a mission (Moon / Mars / Europa), design a spacecraft (rocket, power, radiation shield, comms antenna, instruments), launch, get a report card.
- Repo: https://github.com/se-250717020/space-mission-game (branch `main`, shared with 3 teammates). Deploys to Streamlit Community Cloud with main file `app.py`: https://space-mission-game.streamlit.app/ (auto-redeploys on every push to `main`).
- The 4-person team is on its first hackathon, with no web experience. The user is the Tech Lead and speaks Turkish, so reply in Turkish.

## Files and owners (do not cross these lines without the Tech Lead's OK)
| File | Owner | Role |
|---|---|---|
| `data.py` | Person 1 (NASA research & data) | Pure data dicts + `validate_schema()` |
| `calculations.py` | Person 2 (game rules) | Pure functions, **no `import streamlit`**; public API documented in its top docstring |
| `app.py`, `assets/` | Person 3 (visuals & UI) | Whole Streamlit UI incl. the 4-player team mode |
| `AI_CONTEXT.md`, `requirements.txt`, `.gitignore`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md` | Person 4 = Tech Lead (the user) | Contract, docs, merging |

Data flow: `data.py` → `calculations.py` → `app.py`. The shared contract is `AI_CONTEXT.md`: every data key, the `selection` dict (`mission, orbit, rocket, power, power_units, shield, instruments, comms`), public functions and their result dicts. `data.CHECK_IDS` fixes the 8 check ids in order.

## Contract rules
- All identifiers, IDs, dict keys **and all on-screen text are English**. Code comments and team docs (`README.md`, `TEAM_RULES.md`) are Turkish.
- Never rename or delete existing dict keys, IDs, public function names/parameters, or returned dict keys. Adding new items is fine.
- `app.py` does no math; it asks `calculations.py` for every number.
- If the contract changes, update `AI_CONTEXT.md` and the `calculations.py` docstring together (plus `README.md` rules table if game rules change). New names are decided here first, then teammates pull.
- When merging teammates' Gemini output: check that it still uses the names in `AI_CONTEXT.md`; if Gemini invented a key, align it with the contract (or add it to the contract) rather than letting two names coexist.

## Checks before any commit
```bash
.venv\Scripts\python.exe data.py          # must print the ✅ schema check
.venv\Scripts\python.exe calculations.py  # self-test must pass
.venv\Scripts\python.exe -m streamlit run app.py
```
- Streamlit caches imported modules, so restart the server after editing `data.py` or `calculations.py`.
- Balance rule: every mission must be passable by at least one design, but not trivially.

## Git
- **Ask the user before every commit and push.** The repo is shared.
- Run `git fetch` and check for teammates' commits before pushing. Never use `--force` or `reset --hard`.
- Stage specific files (`git add <file>`), not `git add .`.
