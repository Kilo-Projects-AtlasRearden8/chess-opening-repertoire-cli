"""Tests for spaced-repetition module."""

import pytest
import time
from chess_repertoire.srs import SpacedRepetition, Card, create_repertoire


class TestCard:
    """Tests for Card dataclass."""

    def test_card_creation(self):
        card = Card(
            id="test1",
            opening_name="Sicilian",
            eco="B90",
            moves=["e4", "c5"],
            side="white"
        )
        assert card.id == "test1"
        assert card.interval == 0
        assert card.ease_factor == 2.5
        assert card.reviews == 0

    def test_card_to_dict(self):
        card = Card(
            id="test1",
            opening_name="Sicilian",
            eco="B90",
            moves=["e4", "c5"],
            side="white",
            interval=5,
            ease_factor=2.3
        )
        data = card.to_dict()
        assert data["id"] == "test1"
        assert data["interval"] == 5
        assert data["ease_factor"] == 2.3

    def test_card_from_dict(self):
        data = {
            "id": "test1",
            "opening_name": "Sicilian",
            "eco": "B90",
            "moves": ["e4", "c5"],
            "side": "white",
            "interval": 5,
            "ease_factor": 2.3,
            "due_date": time.time(),
            "reviews": 1,
            "lapses": 0,
            "last_reviewed": 0
        }
        card = Card.from_dict(data)
        assert card.id == "test1"
        assert card.interval == 5


class TestSpacedRepetition:
    """Tests for SpacedRepetition class."""

    def test_add_card(self, tmp_path):
        storage = tmp_path / "test_repertoire.json"
        srs = SpacedRepetition(str(storage))

        card = srs.add_card("Sicilian", "B90", ["e4", "c5", "Nf3"], "white")
        assert card.opening_name == "Sicilian"
        assert card.eco == "B90"
        assert card.side == "white"
        assert card.moves == ["e4", "c5", "Nf3"]
        assert card.due_date <= time.time() + 1  # Due immediately

        # Card should be saved
        assert storage.exists()

    def test_get_due_cards(self, tmp_path):
        storage = tmp_path / "test_repertoire.json"
        srs = SpacedRepetition(str(storage))

        # Add cards
        srs.add_card("Sicilian", "B90", ["e4", "c5"], "white")
        srs.add_card("Italian", "C50", ["e4", "e5"], "black")

        due = srs.get_due_cards(limit=10)
        assert len(due) == 2

        # Add a card with future due date
        future_card = srs.add_card("French", "C00", ["e4", "e6"], "white")
        future_card.due_date = time.time() + 86400  # Tomorrow
        srs.save()

        due = srs.get_due_cards(limit=10)
        assert len(due) == 2  # Only the two immediate ones

    def test_review_card_pass(self, tmp_path):
        storage = tmp_path / "test_repertoire.json"
        srs = SpacedRepetition(str(storage))

        card = srs.add_card("Sicilian", "B90", ["e4", "c5"], "white")
        original_due = card.due_date

        # Review with quality 5 (perfect)
        reviewed = srs.review_card(card.id, 5)

        assert reviewed.reviews == 1
        assert reviewed.interval == 1  # First interval is 1 day
        assert reviewed.due_date > original_due
        assert reviewed.ease_factor >= 2.5

    def test_review_card_fail(self, tmp_path):
        storage = tmp_path / "test_repertoire.json"
        srs = SpacedRepetition(str(storage))

        # First pass to get interval > 0
        card = srs.add_card("Sicilian", "B90", ["e4", "c5"], "white")
        srs.review_card(card.id, 5)
        srs.review_card(card.id, 5)  # interval = 6

        # Now fail
        reviewed = srs.review_card(card.id, 2)  # Failed

        assert reviewed.lapses == 1
        assert reviewed.interval == 0
        assert reviewed.ease_factor <= 2.5

    def test_sm2_algorithm_progression(self, tmp_path):
        storage = tmp_path / "test_repertoire.json"
        srs = SpacedRepetition(str(storage))

        card = srs.add_card("Test", "A00", ["e4"], "white")

        # First review: interval 0 -> 1
        card = srs.review_card(card.id, 5)
        assert card.interval == 1

        # Second review: interval 1 -> 6
        card = srs.review_card(card.id, 5)
        assert card.interval == 6

        # Third review: interval 6 -> ~15 (6 * 2.5)
        card = srs.review_card(card.id, 5)
        assert card.interval >= 14  # 6 * 2.5 = 15

    def test_persistence(self, tmp_path):
        storage = tmp_path / "test_repertoire.json"
        srs1 = SpacedRepetition(str(storage))

        card = srs1.add_card("Sicilian", "B90", ["e4", "c5"], "white")
        card_id = card.id

        # Create new instance - should load from file
        srs2 = SpacedRepetition(str(storage))
        loaded_card = srs2.cards[card_id]

        assert loaded_card.opening_name == "Sicilian"
        assert loaded_card.eco == "B90"
        assert loaded_card.moves == ["e4", "c5"]

    def test_get_stats(self, tmp_path):
        storage = tmp_path / "test_repertoire.json"
        srs = SpacedRepetition(str(storage))

        srs.add_card("Sicilian", "B90", ["e4", "c5"], "white")
        srs.add_card("Italian", "C50", ["e4", "e5"], "black")

        # Review one
        card = list(srs.cards.values())[0]
        srs.review_card(card.id, 5)
        srs.review_card(card.id, 2)  # One lapse

        stats = srs.get_stats()
        assert stats["total_cards"] == 2
        assert stats["total_reviews"] == 2
        assert stats["total_lapses"] == 1

    def test_create_repertoire_factory(self, tmp_path):
        storage = tmp_path / "factory_test.json"
        srs = create_repertoire(str(storage))
        assert isinstance(srs, SpacedRepetition)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])