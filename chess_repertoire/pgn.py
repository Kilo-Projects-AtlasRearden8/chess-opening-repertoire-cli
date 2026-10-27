"""PGN parsing utilities for chess opening repertoire."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Game:
    """Represents a parsed chess game from PGN."""
    event: str = ""
    site: str = ""
    date: str = ""
    round: str = ""
    white: str = ""
    black: str = ""
    result: str = ""
    eco: str = ""
    opening: str = ""
    moves: list[str] = None

    def __post_init__(self):
        if self.moves is None:
            self.moves = []


class PGNParser:
    """Parser for PGN (Portable Game Notation) files."""

    TAG_PATTERN = re.compile(r'\[(\w+)\s+"([^"]*)"\]')
    MOVE_PATTERN = re.compile(r'(\d+\.)\s*(\S+)\s*(\S*)')

    def __init__(self):
        self.games: list[Game] = []

    def parse_file(self, filepath: str) -> list[Game]:
        """Parse a PGN file and return list of games."""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return self.parse_string(content)

    def parse_string(self, content: str) -> list[Game]:
        """Parse PGN content from string and return list of games."""
        self.games = []
        # Split by double newlines to separate games
        game_blocks = re.split(r'\n\s*\n', content.strip())
        for block in game_blocks:
            if block.strip():
                game = self._parse_game_block(block)
                if game and game.moves:
                    self.games.append(game)
        return self.games

    def _parse_game_block(self, block: str) -> Optional[Game]:
        """Parse a single game block."""
        game = Game()
        lines = block.strip().split('\n')

        # Parse tags
        moves_text = ""
        for line in lines:
            line = line.strip()
            if line.startswith('['):
                match = self.TAG_PATTERN.match(line)
                if match:
                    tag, value = match.groups()
                    setattr(game, tag.lower(), value)
            elif line and not line.startswith('['):
                moves_text += " " + line

        # Parse moves
        game.moves = self._parse_moves(moves_text.strip())
        return game

    def _parse_moves(self, moves_text: str) -> list[str]:
        """Parse move sequence from text."""
        moves = []
        # Remove comments and variations
        cleaned = re.sub(r'\{[^}]*\}', '', moves_text)
        cleaned = re.sub(r'\([^)]*\)', '', cleaned)
        cleaned = re.sub(r'\d+\.\.\.', '', cleaned)  # Remove black move numbers

        # Find all moves
        tokens = cleaned.split()
        for token in tokens:
            # Skip move numbers
            if re.match(r'^\d+\.$', token):
                continue
            # Skip result markers
            if token in ('1-0', '0-1', '1/2-1/2', '*'):
                continue
            moves.append(token)

        return moves

    def extract_opening_lines(self, min_moves: int = 10) -> dict[str, list[list[str]]]:
        """Extract opening lines grouped by ECO/Opening name."""
        openings: dict[str, list[list[str]]] = {}
        for game in self.games:
            key = game.eco or game.opening or "Unknown"
            if key not in openings:
                openings[key] = []
            # Take first N moves as opening line
            line = game.moves[:min_moves]
            if line:
                openings[key].append(line)
        return openings


def parse_pgn(filepath: str) -> list[Game]:
    """Convenience function to parse a PGN file."""
    parser = PGNParser()
    return parser.parse_file(filepath)