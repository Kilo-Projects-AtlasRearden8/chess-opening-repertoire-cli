"""Command-line interface for Chess Opening Repertoire."""

import argparse
import sys
from pathlib import Path

from .pgn import PGNParser, parse_pgn
from .srs import SpacedRepetition, create_repertoire


def build_repertoire(args: argparse.Namespace) -> int:
    """Build repertoire from PGN file."""
    parser = PGNParser()
    games = parser.parse_file(args.pgn_file)

    if not games:
        print("No games found in PGN file.")
        return 1

    repertoire = create_repertoire(args.storage)
    openings = parser.extract_opening_lines(args.min_moves)

    added = 0
    for eco, lines in openings.items():
        for line in lines:
            if len(line) >= args.min_moves:
                # Add for both sides
                repertoire.add_card(
                    opening_name=eco,
                    eco=eco,
                    moves=line,
                    side="white"
                )
                repertoire.add_card(
                    opening_name=eco,
                    eco=eco,
                    moves=line,
                    side="black"
                )
                added += 2

    print(f"Built repertoire: {added} cards from {len(games)} games")
    print(f"Openings found: {len(openings)}")
    return 0


def quiz_repertoire(args: argparse.Namespace) -> int:
    """Quiz due cards from repertoire."""
    repertoire = create_repertoire(args.storage)
    due_cards = repertoire.get_due_cards(args.limit)

    if not due_cards:
        print("No cards due for review. Great job!")
        return 0

    print(f"Quiz: {len(due_cards)} cards due\n")
    correct = 0

    for i, card in enumerate(due_cards, 1):
        print(f"--- Card {i}/{len(due_cards)} ---")
        print(f"Opening: {card.opening_name} ({card.eco})")
        print(f"Side: {card.side.capitalize()}")
        print(f"Moves: {' '.join(card.moves)}")
        print()

        # In a real quiz, you'd prompt for the next move
        # For now, just show the answer
        print("Press Enter to continue...")
        input()

        # Auto-grade as correct for demo
        repertoire.review_card(card.id, 5)
        correct += 1

    print(f"\nQuiz complete! {correct}/{len(due_cards)} reviewed.")
    return 0


def review_repertoire(args: argparse.Namespace) -> int:
    """Review repertoire with quality grading."""
    repertoire = create_repertoire(args.storage)
    due_cards = repertoire.get_due_cards(args.limit)

    if not due_cards:
        print("No cards due for review.")
        return 0

    print(f"Review: {len(due_cards)} cards due\n")

    for i, card in enumerate(due_cards, 1):
        print(f"--- Card {i}/{len(due_cards)} ---")
        print(f"Opening: {card.opening_name} ({card.eco})")
        print(f"Side: {card.side.capitalize()}")
        print(f"Moves: {' '.join(card.moves)}")
        print()

        while True:
            try:
                quality = int(input("Quality (0-5, 5=perfect): "))
                if 0 <= quality <= 5:
                    break
            except ValueError:
                pass
            print("Please enter a number 0-5")

        repertoire.review_card(card.id, quality)
        print()

    print("Review complete!")
    return 0


def stats_repertoire(args: argparse.Namespace) -> int:
    """Show repertoire statistics."""
    repertoire = create_repertoire(args.storage)
    stats = repertoire.get_stats()

    print("Repertoire Statistics:")
    print(f"  Total cards: {stats['total_cards']}")
    print(f"  Due now: {stats['due_cards']}")
    print(f"  Total reviews: {stats['total_reviews']}")
    print(f"  Total lapses: {stats['total_lapses']}")
    return 0


def list_openings(args: argparse.Namespace) -> int:
    """List all openings in repertoire."""
    repertoire = create_repertoire(args.storage)
    openings: dict[str, int] = {}

    for card in repertoire.cards.values():
        key = f"{card.eco} - {card.opening_name}"
        openings[key] = openings.get(key, 0) + 1

    if not openings:
        print("Repertoire is empty.")
        return 0

    print("Openings in repertoire:")
    for name, count in sorted(openings.items()):
        print(f"  {name}: {count} lines")
    return 0


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="chess-repertoire",
        description="Build and quiz a personal chess opening repertoire from PGN with spaced repetition."
    )
    parser.add_argument(
        "-s", "--storage",
        default="repertoire.json",
        help="Path to JSON storage file (default: repertoire.json)"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Build command
    build_parser = subparsers.add_parser("build", help="Build repertoire from PGN file")
    build_parser.add_argument("pgn_file", help="Path to PGN file")
    build_parser.add_argument(
        "-m", "--min-moves", type=int, default=10,
        help="Minimum moves for opening line (default: 10)"
    )
    build_parser.set_defaults(func=build_repertoire)

    # Quiz command
    quiz_parser = subparsers.add_parser("quiz", help="Quiz due cards (auto-grade)")
    quiz_parser.add_argument(
        "-l", "--limit", type=int, default=10,
        help="Maximum cards to quiz (default: 10)"
    )
    quiz_parser.set_defaults(func=quiz_repertoire)

    # Review command
    review_parser = subparsers.add_parser("review", help="Review due cards with grading")
    review_parser.add_argument(
        "-l", "--limit", type=int, default=10,
        help="Maximum cards to review (default: 10)"
    )
    review_parser.set_defaults(func=review_repertoire)

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show repertoire statistics")
    stats_parser.set_defaults(func=stats_repertoire)

    # List command
    list_parser = subparsers.add_parser("list", help="List openings in repertoire")
    list_parser.set_defaults(func=list_openings)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())