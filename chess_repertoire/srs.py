"""Spaced-repetition tracking for opening repertoire using local JSON."""

import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional


@dataclass
class Card:
    """Represents a flashcard for an opening line."""
    id: str
    opening_name: str
    eco: str
    moves: list[str]
    side: str  # "white" or "black"
    interval: int = 0  # days
    ease_factor: float = 2.5
    due_date: float = 0  # Unix timestamp
    reviews: int = 0
    lapses: int = 0
    last_reviewed: float = 0

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'Card':
        return cls(**data)


class SpacedRepetition:
    """SM-2 based spaced repetition scheduler."""

    def __init__(self, storage_path: str = "repertoire.json"):
        self.storage_path = Path(storage_path)
        self.cards: dict[str, Card] = {}
        self._load()

    def _load(self) -> None:
        """Load cards from JSON file."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        data = json.loads(content)
                        self.cards = {cid: Card.from_dict(c) for cid, c in data.items()}
            except (json.JSONDecodeError, ValueError):
                self.cards = {}

    def save(self) -> None:
        """Save cards to JSON file."""
        data = {cid: card.to_dict() for cid, card in self.cards.items()}
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def add_card(self, opening_name: str, eco: str, moves: list[str], side: str) -> Card:
        """Add a new opening line as a flashcard."""
        card_id = f"{eco}_{side}_{hash(tuple(moves)) % 1000000}"
        card = Card(
            id=card_id,
            opening_name=opening_name,
            eco=eco,
            moves=moves,
            side=side,
            due_date=time.time()  # Due immediately
        )
        self.cards[card_id] = card
        self.save()
        return card

    def get_due_cards(self, limit: int = 10) -> list[Card]:
        """Get cards due for review."""
        now = time.time()
        due = [c for c in self.cards.values() if c.due_date <= now]
        due.sort(key=lambda c: c.due_date)
        return due[:limit]

    def review_card(self, card_id: str, quality: int) -> Card:
        """Review a card with quality 0-5 (SM-2 algorithm)."""
        card = self.cards[card_id]
        card.last_reviewed = time.time()
        card.reviews += 1

        if quality < 3:
            # Failed - reset interval
            card.interval = 0
            card.lapses += 1
            card.ease_factor = max(1.3, card.ease_factor - 0.2)
        else:
            # Passed
            if card.interval == 0:
                card.interval = 1
            elif card.interval == 1:
                card.interval = 6
            else:
                card.interval = int(card.interval * card.ease_factor)
            card.ease_factor = max(1.3, card.ease_factor + (0.1 - (5 - quality) * 0.08))

        card.due_date = time.time() + card.interval * 86400  # days to seconds
        self.save()
        return card

    def get_stats(self) -> dict:
        """Get repository statistics."""
        now = time.time()
        due = sum(1 for c in self.cards.values() if c.due_date <= now)
        return {
            "total_cards": len(self.cards),
            "due_cards": due,
            "total_reviews": sum(c.reviews for c in self.cards.values()),
            "total_lapses": sum(c.lapses for c in self.cards.values()),
        }


def create_repertoire(storage_path: str = "repertoire.json") -> SpacedRepetition:
    """Factory function to create a SpacedRepetition instance."""
    return SpacedRepetition(storage_path)