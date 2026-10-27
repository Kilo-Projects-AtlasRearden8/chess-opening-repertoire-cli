# Chess Opening Repertoire CLI

A Python command-line tool to build and quiz your personal chess opening repertoire from PGN files, with spaced-repetition tracking stored locally in JSON.

Built by [Asdale Dynamics, LLC](https://dylanasdale.github.io) — beginner-friendly AI education, books, and practical tools.

## Features

- **Import from PGN**: Parse your games and extract opening lines automatically
- **Spaced Repetition**: SM-2 algorithm schedules reviews for optimal retention
- **Local-First**: All data stored in a local JSON file — no cloud, no accounts
- **Quiz & Review Modes**: Test yourself with auto-graded quizzes or manual quality grading
- **Statistics**: Track your progress with review counts, lapses, and due cards

## Installation

```bash
pip install -e .
```

Or run directly with Python:

```bash
python -m chess_repertoire.cli --help
```

## Usage

### Build your repertoire from a PGN file

```bash
chess-repertoire build my_games.pgn
```

Options:
- `-m, --min-moves N` — Minimum moves for an opening line (default: 10)
- `-s, --storage FILE` — JSON storage file (default: `repertoire.json`)

### Quiz due cards (auto-graded)

```bash
chess-repertoire quiz
```

Options:
- `-l, --limit N` — Maximum cards to quiz (default: 10)

### Review due cards with quality grading (0-5)

```bash
chess-repertoire review
```

Quality scale (SM-2):
- 5: Perfect recall
- 4: Correct with hesitation
- 3: Correct with difficulty
- 2: Incorrect but knew it
- 1: Incorrect, familiar
- 0: Complete blackout

### View statistics

```bash
chess-repertoire stats
```

### List all openings in your repertoire

```bash
chess-repertoire list
```

## Data Storage

Your repertoire is stored in `repertoire.json` (or custom path via `--storage`):

```json
{
  "B90_white_123456": {
    "id": "B90_white_123456",
    "opening_name": "Sicilian Defense",
    "eco": "B90",
    "moves": ["e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6", "Nc3", "a6"],
    "side": "white",
    "interval": 6,
    "ease_factor": 2.5,
    "due_date": 1705344000.0,
    "reviews": 3,
    "lapses": 0,
    "last_reviewed": 1704739200.0
  }
}
```

## Testing

```bash
pytest
```

## License

MIT License — Copyright (c) 2026 Asdale Dynamics, LLC

See [LICENSE](LICENSE) for details.