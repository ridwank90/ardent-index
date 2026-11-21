"""Focused rule/search tests for main.py's compact 0x88 engine.

Run with: python3.13 -m unittest -v test_engine.py
No third-party packages are needed. The AST loader executes imports, constants,
classes, and function definitions only; it deliberately skips main.py's HTTP loop.
"""
import ast
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent


def load_engine():
    tree = ast.parse((ROOT / "main.py").read_text())
    allowed = {"V", "B", "R", "N", "D", "nodes"}
    body = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
            body.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in allowed
            for target in node.targets
        ):
            body.append(node)
    module = ast.Module(body=body, type_ignores=[])
    namespace = {"__name__": "engine_under_test"}
    exec(compile(module, str(ROOT / "main.py"), "exec"), namespace)
    return namespace


class EngineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = load_engine()
        required = ("parse", "sq", "attacked", "play", "gen", "choose")
        missing = [name for name in required if name not in cls.e]
        if missing:
            raise AssertionError("main.py lacks engine functions: " + ", ".join(missing))

    def state(self, fen):
        return self.e["parse"](fen)

    def attacked(self, fen, target, side):
        b, _, _, _ = self.state(fen)
        return self.e["attacked"](b, self.e["sq"](target), side)

    def moves(self, fen):
        return set(self.e["gen"](self.state(fen)))

    def assert_generated_moves_are_legal(self, fen):
        st = self.state(fen)
        b, side, _, _ = st
        for m in self.e["gen"](st):
            child = self.e["play"](st, m)
            cb = child[0]
            king = next(i for i, p in enumerate(cb) if p == ("K" if side == 1 else "k"))
            self.assertFalse(self.e["attacked"](cb, king, -side), m)

    def test_01_white_pawn_attacks(self):
        fen = "8/8/8/3k4/4P3/8/8/7K w - - 0 1"
        self.assertTrue(self.attacked(fen, "d5", 1))
        self.assertTrue(self.attacked(fen, "f5", 1))

    def test_02_black_pawn_attacks(self):
        fen = "8/8/8/4p3/3K4/8/8/8 w - - 0 1"
        self.assertTrue(self.attacked(fen, "d4", -1))
        self.assertTrue(self.attacked(fen, "f4", -1))

    def test_03_knight_all_eight_attack_offsets(self):
        fen = "7k/8/8/8/3N4/8/8/K7 w - - 0 1"
        for target in ("c2", "b3", "b5", "c6", "e6", "f5", "f3", "e2"):
            with self.subTest(target=target):
                self.assertTrue(self.attacked(fen, target, 1))
        self.assertFalse(self.attacked(fen, "d5", 1))

    def test_04_bishop_ray_and_blocker(self):
        self.assertTrue(self.attacked("8/8/1k6/8/3B4/8/8/7K w - - 0 1", "b6", 1))
        self.assertFalse(self.attacked("8/8/1k6/2P5/3B4/8/8/7K w - - 0 1", "b6", 1))

    def test_05_rook_ray_and_blocker(self):
        self.assertTrue(self.attacked("3k4/8/8/8/3R4/8/8/K7 w - - 0 1", "d8", 1))
        self.assertFalse(self.attacked("3k4/8/3P4/8/3R4/8/8/K7 w - - 0 1", "d8", 1))

    def test_06_queen_diagonal_and_orthogonal_rays(self):
        fen = "8/6k1/8/8/3Q4/8/8/K7 w - - 0 1"
        self.assertTrue(self.attacked(fen, "g7", 1))
        self.assertTrue(self.attacked(fen, "d7", 1))

    def test_07_castling_white_both_sides(self):
        self.assertTrue({"e1g1", "e1c1"} <= self.moves("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"))

    def test_08_castling_black_both_sides(self):
        self.assertTrue({"e8g8", "e8c8"} <= self.moves("r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"))

    def test_09_king_move_clears_own_castling_rights(self):
        fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
        self.assertEqual(self.e["play"](self.state(fen), "e1e2")[2], "kq")
        fen = "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"
        self.assertEqual(self.e["play"](self.state(fen), "e8e7")[2], "KQ")

    def test_10_rook_move_clears_only_matching_right(self):
        fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
        self.assertEqual(self.e["play"](self.state(fen), "h1h2")[2], "Qkq")
        self.assertEqual(self.e["play"](self.state(fen), "a1a2")[2], "Kkq")
        fen = "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"
        self.assertEqual(self.e["play"](self.state(fen), "h8h7")[2], "KQq")
        self.assertEqual(self.e["play"](self.state(fen), "a8a7")[2], "KQk")

    def test_11_capture_of_corner_rook_clears_captured_right(self):
        fen = "r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1"
        self.assertEqual(self.e["play"](self.state(fen), "h1h8")[2], "KQq")
        self.assertEqual(self.e["play"](self.state(fen), "a1a8")[2], "KQk")
        fen = "r3k2r/8/8/8/8/8/8/R3K2R b KQkq - 0 1"
        self.assertEqual(self.e["play"](self.state(fen), "h8h1")[2], "Qkq")
        self.assertEqual(self.e["play"](self.state(fen), "a8a1")[2], "Kkq")

    def test_12_en_passant_capture_and_board_update(self):
        fen = "4k3/8/8/3pP3/8/8/8/4K3 w - d6 0 2"
        st = self.state(fen)
        self.assertIn("e5d6", self.e["gen"](st))
        child = self.e["play"](st, "e5d6")
        b = child[0]
        self.assertEqual(b[self.e["sq"]("d5")], ".")
        self.assertEqual(b[self.e["sq"]("d6")], "P")

    def test_13_en_passant_discovered_check_is_illegal(self):
        fen = "k7/8/8/4KPpr/8/8/8/8 w - g6 0 1"
        self.assertNotIn("f5g6", self.moves(fen))
        self.assert_generated_moves_are_legal(fen)

    def test_14_all_quiet_promotion_choices(self):
        fen = "k7/P7/8/8/8/8/8/7K w - - 0 1"
        self.assertTrue({"a7a8q", "a7a8r", "a7a8b", "a7a8n"} <= self.moves(fen))

    def test_15_all_capture_promotion_choices(self):
        fen = "1r5k/P7/8/8/8/8/8/7K w - - 0 1"
        self.assertTrue({"a7b8q", "a7b8r", "a7b8b", "a7b8n"} <= self.moves(fen))

    def test_16_checkmate_and_stalemate(self):
        mate = "7k/6Q1/5K2/8/8/8/8/8 b - - 0 1"
        stale = "7k/5Q2/5K2/8/8/8/8/8 b - - 0 1"
        self.assertEqual(self.moves(mate), set())
        self.assertTrue(self.attacked(mate, "h8", 1))
        self.assertEqual(self.moves(stale), set())
        self.assertFalse(self.attacked(stale, "h8", 1))

    def test_17_0x88_board_edge_does_not_wrap(self):
        fen = "7k/8/8/8/8/8/8/N6K w - - 0 1"
        knight_moves = {m for m in self.moves(fen) if m.startswith("a1")}
        self.assertEqual(knight_moves, {"a1b3", "a1c2"})

    def test_18_search_limit_interrupts_without_partial_score(self):
        self.assertIn("search", self.e)
        self.assertIn("Stop", self.e)
        self.e["nodes"] = 1200
        with self.assertRaises(self.e["Stop"]):
            self.e["search"](self.state("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"), 2, -32000, 32000)
        self.assertGreater(self.e["nodes"], 1200)

    def test_19_choose_returns_only_supplied_root_move(self):
        fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        supplied = ["e2e4"]
        self.assertEqual(self.e["choose"](fen, supplied), "e2e4")


if __name__ == "__main__":
    unittest.main(verbosity=2)
