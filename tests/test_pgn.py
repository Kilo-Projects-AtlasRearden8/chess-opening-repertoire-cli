"""Tests for PGN parsing module."""

import pytest
from chess_repertoire.pgn import PGNParser, parse_pgn, Game


SAMPLE_PGN = '''[Event "Test Game"]
[Site "Online"]
[Date "2026.01.15"]
[Round "1"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]
[ECO "B90"]
[Opening "Sicilian Defense"]
1. e4 c5 2. Nf3 d6 3. d4 cxd4 4. Nxd4 Nf6 5. Nc3 a6 6. Be3 e5 7. Nb3 Be6 8. f3 Be7 9. Qd2 O-O 10. O-O-O Nbd7 1-0

[Event "Another Game"]
[Site "Club"]
[Date "2026.01.16"]
[Round "2"]
[White "Player3"]
[Black "Player4"]
[Result "0-1"]
[ECO "C50"]
[Opening "Italian Game"]
1. e4 e5 2. Nf3 Nc6 3. Bc4 Bc5 4. c3 Nf6 5. d4 exd4 6. cxd4 Bb4+ 7. Nc3 Nxe4 8. O-O Nxc3 9. bxc3 Bxc3 10. Ba3 d5 0-1
'''

SAMPLE_PGN_WITH_COMMENTS = '''[Event "Commented Game"]
[White "PlayerA"]
[Black "PlayerB"]
[Result "1/2-1/2"]
[ECO "E60"]
[Opening "King's Indian Defense"]
1. d4 Nf6 2. c4 g6 3. Nc3 Bg7 4. e4 d6 5. Nf3 O-O 6. Be2 e5 7. O-O Nc6 8. d5 Ne7 9. Ne1 Nd7 10. Nd3 f5 {This is a comment} 1/2-1/2
'''

SAMPLE_PGN_WITH_VARIATIONS = '''[Event "Variation Game"]
[White "PlayerX"]
[Black "PlayerY"]
[Result "*"]
[ECO "A00"]
[Opening "Uncommon Opening"]
1. g3 (1. e4 e5 2. Nf3) d5 2. Bg2 c5 3. Nf3 Nc6 4. O-O Bg4 5. d3 e5 6. Nbd2 Nge7 7. e4 O-O 8. Re1 d4 9. Ne1 Nd7 10. Nd3 *
'''


class TestPGNParser:
    """Tests for PGNParser class."""

    def test_parse_simple_game(self):
        parser = PGNParser()
        games = parser.parse_string(SAMPLE_PGN)
        assert len(games) == 2

        game1 = games[0]
        assert game1.event == "Test Game"
        assert game1.white == "Player1"
        assert game1.black == "Player2"
        assert game1.result == "1-0"
        assert game1.eco == "B90"
        assert game1.opening == "Sicilian Defense"
        assert game1.moves == [
            "e4", "c5", "Nf3", "d6", "d4", "cxd4", "Nxd4", "Nf6",
            "Nc3", "a6", "Be3", "e5", "Nb3", "Be6", "f3", "Be7",
            "Qd2", "O-O", "O-O-O", "Nbd7"
        ]

        game2 = games[1]
        assert game2.eco == "C50"
        assert game2.opening == "Italian Game"

    def test_parse_with_comments(self):
        parser = PGNParser()
        games = parser.parse_string(SAMPLE_PGN_WITH_COMMENTS)
        assert len(games) == 1

        game = games[0]
        assert game.eco == "E60"
        assert "f5" in game.moves
        # Comment should be stripped
        assert not any("{" in move for move in game.moves)

    def test_parse_with_variations(self):
        parser = PGNParser()
        games = parser.parse_string(SAMPLE_PGN_WITH_VARIATIONS)
        assert len(games) == 1

        game = games[0]
        assert game.eco == "A00"
        # Variation moves should not be in main line
        assert "e4" not in game.moves[:2]  # First move should be g3, not e4

    def test_extract_opening_lines(self):
        parser = PGNParser()
        games = parser.parse_string(SAMPLE_PGN)
        openings = parser.extract_opening_lines(min_moves=10)

        assert "B90" in openings
        assert "C50" in openings
        assert len(openings["B90"]) == 1
        assert len(openings["B90"][0]) == 10

    def test_empty_pgn(self):
        parser = PGNParser()
        games = parser.parse_string("")
        assert games == []

    def test_parse_file(self, tmp_path):
        pgn_file = tmp_path / "test.pgn"
        pgn_file.write_text(SAMPLE_PGN)
        games = parse_pgn(str(pgn_file))
        assert len(games) == 2


class TestGameDataclass:
    """Tests for Game dataclass."""

    def test_default_values(self):
        game = Game()
        assert game.moves == []
        assert game.event == ""
        assert game.white == ""

    def test_custom_moves(self):
        game = Game(moves=["e4", "e5"])
        assert game.moves == ["e4", "e5"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])