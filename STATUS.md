# STATUS

## What Was Built

A Python CLI tool for building and quizzing a personal chess opening repertoire from PGN files, with spaced-repetition tracking stored locally in JSON. Built for Asdale Dynamics, LLC.

## Project Structure

```
chess-opening-repertoire-cli/
├── LICENSE                          # MIT License, Copyright (c) 2026 Asdale Dynamics, LLC
├── README.md                        # Usage documentation with Asdale Dynamics credit
├── pyproject.toml                   # Package config, entry point, dev dependencies
├── .gitignore                       # Python/build artifact exclusions
├── chess_repertoire/
│   ├── __init__.py                  # Package metadata
│   ├── pgn.py                       # PGN parsing (PGNParser, Game dataclass)
│   ├── srs.py                       # Spaced repetition (SM-2, JSON persistence)
│   └── cli.py                       # CLI (build, quiz, review, stats, list)
├── tests/
│   ├── test_pgn.py                  # PGN parsing tests (10 tests)
│   └── test_srs.py                  # Spaced repetition tests (9 tests)
└── .venv/                           # Virtual environment (not committed)
```

## How to Run

### Install

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/pip install pytest
```

### CLI Commands

```bash
# Build repertoire from a PGN file
.venv/bin/chess-repertoire build my_games.pgn

# Quiz due cards (auto-graded)
.venv/bin/chess-repertoire quiz

# Review due cards with manual quality grading (0-5)
.venv/bin/chess-repertoire review

# View repertoire statistics
.venv/bin/chess-repertoire stats

# List all openings in repertoire
.venv/bin/chess-repertoire list
```

### Run Tests

```bash
.venv/bin/pytest
```

## Verification Results

- **Build**: Package installs successfully with `pip install -e .`
- **CLI entry point**: `chess-repertoire` command works, all subcommands (build, quiz, review, stats, list) available
- **Tests**: 19/19 passed (10 PGN parsing, 9 spaced repetition)
- **Integration**: End-to-end PGN parse → repertoire build → review cycle verified

## Known Gaps

1. **Quiz mode is auto-graded**: The `quiz` subcommand auto-marks cards as correct (quality 5) rather than prompting the user to recall the next move. A true interactive quiz would present the position and ask for the next move.
2. **No ECO opening name resolution**: ECO codes (e.g., "B90") are stored but not translated to human-readable opening names beyond what's in the PGN tags.
3. **Single-side tracking**: Each opening line creates separate cards for white and black, but there's no linkage between them (e.g., reviewing the white side doesn't update the black side's schedule).
4. **No move validation**: Moves from PGN are stored as text strings without chess library validation (no `python-chess` dependency).
5. **No graphical board**: Text-only interface; no board visualization.

## Credits

Built by Asdale Dynamics, LLC. MIT License. Copyright (c) 2026 Asdale Dynamics, LLC.