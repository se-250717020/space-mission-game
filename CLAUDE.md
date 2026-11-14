# CLAUDE.md — Space Mission Design Game (NASA Space Apps Challenge 2026)

Notes for Claude Code sessions run by the Tech Lead. Teammates use claude.ai/Gemini with the prompt in `TEAM_RULES.md` (section D); this file is only for Claude Code.

## Project
- Python + Streamlit game: pick a mission (Moon / Mars / Europa), design a spacecraft (rocket, power, radiation shield, comms antenna, instruments), launch, get a report card.
- Repo: https://github.com/se-250717020/space-mission-game (branch `main`, shared with 3 teammates). Deploys to Streamlit Community Cloud with main file `app.py`.
- The 4-person team is on its first hackathon, with no web experience. The user is the Tech Lead and speaks Turkish, so reply in Turkish.

## Files and owners (do not cross these lines without the Tech Lead's OK)
| File | Owner | Role |
|---|---|---|
| `data.py` | Person 4 | Pure data dicts + `validate_schema()` |
| `calculations.py` | Person 1 | Pure functions, **no `import streamlit`**; public API documented in its top docstring |
| `app.py` SECTION A (`BÖLÜM A`) | Person 2 | Mission/part pickers, gauges |
| `app.py` SECTION B (`BÖLÜM B`) | Person 3 | Launch animation, report card |
| `app.py` `ORTAK` + `ANA AKIŞ`, `requirements.txt`, `.gitignore`, `README.md`, `TEAM_RULES.md`, `CLAUDE.md` | Tech Lead | Shared helpers, main flow, docs |
| `assets/` | Person 3 | Images/GIFs |

Data flow: `data.py` → `calculations.py` → `app.py`. The shared contract is the `selection` dict from `calc.new_selection(...)`, plus the result dicts of `evaluate_mission` and `simulate_launch` (see the `calculations.py` docstring).

## Contract rules
- All identifiers, IDs, dict keys **and all on-screen text are English**. Code comments and team docs (`README.md`, `TEAM_RULES.md`) are Turkish.
- Never rename or delete existing dict keys, IDs, public function names/parameters, or returned dict keys. Adding new items is fine.
- `app.py` does no math; it asks `calculations.py` for every number.
- If the contract changes, update the `calculations.py` docstring, `TEAM_RULES.md`, and `README.md` together.

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
