import sys
import math
import numpy as np

# ---------------------------------------------------------------------------
# Allow running as   python -m engine.tests   or   pytest engine/tests.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import importlib, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from engine.constants import (
    HIDER_WIN_SCORE, HIDER_LOSE_SCORE,
    PROXIMITY_MULTIPLIER, PROXIMITY_DEFAULT_MULTIPLIER,
)
from engine.models import WorldCell, SolverResult
from engine.world import generate_world, cell_distance
from engine.payoff import build_payoff_matrix
from engine.lp_solver import solve_game
from engine.engine import GameEngine


# ── colour helpers ───────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

_passed = 0
_failed = 0


def _ok(name: str) -> None:
    global _passed
    _passed += 1
    print(f"  {GREEN}PASS{RESET}  {name}")


def _fail(name: str, reason: str) -> None:
    global _failed
    _failed += 1
    print(f"  {RED}FAIL{RESET}  {name}")
    print(f"         {YELLOW}{reason}{RESET}")


def _section(title: str) -> None:
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


# ============================================================================
# 1. World generation
# ============================================================================
_section("1. World generation")

cells = generate_world(N=6, grid_2d=False, seed=0)
try:
    assert len(cells) == 6
    _ok("linear world has exactly N cells")
except AssertionError as e:
    _fail("linear world has exactly N cells", str(e))

valid_types = {"hard", "neutral", "easy"}
try:
    assert all(c.place_type in valid_types for c in cells)
    _ok("all cells have a valid place_type")
except AssertionError:
    _fail("all cells have a valid place_type", "some cells have unknown place_type")

try:
    assert all(c.row == 0 and c.col == c.index for c in cells)
    _ok("linear cells have row=0 and col=index")
except AssertionError:
    _fail("linear cells have row=0 and col=index", "mismatch found")

cells_2d = generate_world(N=9, grid_2d=True, seed=42)
try:
    assert len(cells_2d) == 9
    rows = {c.row for c in cells_2d}
    cols = {c.col for c in cells_2d}
    assert rows == {0, 1, 2} and cols == {0, 1, 2}
    _ok("2-D world (9 cells) has correct 3×3 grid positions")
except AssertionError as e:
    _fail("2-D world (9 cells) has correct 3×3 grid positions", str(e))

cells_2d_nm = generate_world(N=12, rows=3, cols=4, grid_2d=True, seed=42)
try:
    assert len(cells_2d_nm) == 12
    nm_rows = {c.row for c in cells_2d_nm}
    nm_cols = {c.col for c in cells_2d_nm}
    assert nm_rows == {0, 1, 2} and nm_cols == {0, 1, 2, 3}
    _ok("2-D world (12 cells) has correct 3×4 grid positions")
except AssertionError as e:
    _fail("2-D world (12 cells) has correct 3×4 grid positions", str(e))

try:
    assert all(c.index == c.row * 4 + c.col for c in cells_2d_nm)
    _ok("3×4 world flat indices match row * cols + col")
except AssertionError:
    _fail("3×4 world flat indices", "index mismatch found")

cells_a = generate_world(N=5, seed=7)
cells_b = generate_world(N=5, seed=7)
try:
    assert [c.place_type for c in cells_a] == [c.place_type for c in cells_b]
    _ok("same seed produces same world")
except AssertionError:
    _fail("same seed produces same world", "types differ between two seeded calls")

cells_c = generate_world(N=10, seed=1)
cells_d = generate_world(N=10, seed=999)
try:
    assert [c.place_type for c in cells_c] != [c.place_type for c in cells_d]
    _ok("different seeds produce different worlds")
except AssertionError:
    _fail("different seeds produce different worlds",
          "extremely unlikely – re-run to confirm")


# ============================================================================
# 2. Cell distance
# ============================================================================
_section("2. Cell distance")

a = WorldCell(index=0, row=0, col=0, place_type="neutral")
b = WorldCell(index=3, row=0, col=3, place_type="hard")

try:
    assert cell_distance(a, b, grid_2d=False) == 3
    _ok("linear distance |col_a - col_b| = 3")
except AssertionError:
    _fail("linear distance", f"got {cell_distance(a, b, grid_2d=False)}, expected 3")

c1 = WorldCell(index=0, row=0, col=0, place_type="easy")
c2 = WorldCell(index=5, row=2, col=1, place_type="neutral")
try:
    assert cell_distance(c1, c2, grid_2d=True) == 3
    _ok("2-D Manhattan distance = 3")
except AssertionError:
    _fail("2-D Manhattan distance", f"got {cell_distance(c1, c2, grid_2d=True)}, expected 3")

try:
    assert cell_distance(a, a, grid_2d=False) == 0
    _ok("distance to self = 0")
except AssertionError:
    _fail("distance to self = 0", "non-zero distance to self")


# ============================================================================
# 3. Payoff matrix
# ============================================================================
_section("3. Payoff matrix")

neutral_cells = [
    WorldCell(index=i, row=0, col=i, place_type="neutral") for i in range(3)
]
M = build_payoff_matrix(neutral_cells, proximity=False)
try:
    expected_diag = HIDER_LOSE_SCORE["neutral"]
    assert all(M[i, i] == expected_diag for i in range(3))
    _ok("diagonal entries equal HIDER_LOSE_SCORE for the cell's type")
except AssertionError:
    _fail("diagonal entries", f"diagonal: {[M[i,i] for i in range(3)]}")

try:
    win = HIDER_WIN_SCORE["neutral"]
    off_diag = [M[h, s] for h in range(3) for s in range(3) if h != s]
    assert all(v == win for v in off_diag)
    _ok("off-diagonal entries equal HIDER_WIN_SCORE (no proximity)")
except AssertionError:
    _fail("off-diagonal entries (no proximity)", f"got: {off_diag}")

cells4 = generate_world(N=4, seed=1)
M4 = build_payoff_matrix(cells4)
try:
    assert M4.shape == (4, 4)
    _ok("payoff matrix shape is (N, N)")
except AssertionError:
    _fail("payoff matrix shape", f"got {M4.shape}")

prox_cells = [
    WorldCell(index=0, row=0, col=0, place_type="easy"),
    WorldCell(index=1, row=0, col=1, place_type="easy"),
    WorldCell(index=2, row=0, col=2, place_type="easy"),
]
Mp = build_payoff_matrix(prox_cells, proximity=True, grid_2d=False)
win_easy = HIDER_WIN_SCORE["easy"]
try:
    assert Mp[0, 1] == win_easy * PROXIMITY_MULTIPLIER[1]
    _ok("proximity dist=1 → score × 0.5")
except AssertionError:
    _fail("proximity dist=1", f"got {Mp[0, 1]}, expected {win_easy * 0.5}")

try:
    assert Mp[0, 2] == win_easy * PROXIMITY_MULTIPLIER[2]
    _ok("proximity dist=2 → score × 0.75")
except AssertionError:
    _fail("proximity dist=2", f"got {Mp[0, 2]}, expected {win_easy * 0.75}")

example_cells = [
    WorldCell(index=0, row=0, col=0, place_type="neutral"),
    WorldCell(index=1, row=0, col=1, place_type="easy"),
    WorldCell(index=2, row=0, col=2, place_type="hard"),
    WorldCell(index=3, row=0, col=3, place_type="easy"),
]
Me = build_payoff_matrix(example_cells, proximity=False)
w = HIDER_WIN_SCORE
l = HIDER_LOSE_SCORE
types = ["neutral", "easy", "hard", "easy"]
expected = np.array([
    [l[types[h]] if h == s else float(w[types[h]])
     for s in range(4)]
    for h in range(4)
], dtype=float)
try:
    assert np.allclose(Me, expected)
    _ok("payoff matrix structure matches HIDER_WIN_SCORE / HIDER_LOSE_SCORE constants")
except AssertionError:
    _fail("payoff matrix vs constants", f"\ngot:\n{Me}\nexpected:\n{expected}")


# ============================================================================
# 4. LP solver
# ============================================================================
_section("4. LP solver")

payoff = expected.copy()

probs_h, val_h, c_h, A_ub_h, b_ub_h = solve_game(payoff, computer_role="hider", matrix_perspective="hider")
try:
    assert np.all(probs_h >= -1e-9)
    assert abs(probs_h.sum() - 1.0) < 1e-6
    _ok("hider probabilities non-negative and sum to 1")
except AssertionError:
    _fail("hider probabilities", f"sum={probs_h.sum()}, min={probs_h.min()}")

probs_s, val_s, c_s, A_ub_s, b_ub_s = solve_game(payoff, computer_role="seeker", matrix_perspective="hider")
try:
    assert np.all(probs_s >= -1e-9)
    assert abs(probs_s.sum() - 1.0) < 1e-6
    _ok("seeker probabilities non-negative and sum to 1")
except AssertionError:
    _fail("seeker probabilities", f"sum={probs_s.sum()}, min={probs_s.min()}")

try:
    assert val_h <= val_s + 1e-6
    _ok(f"game values consistent: hider_val={val_h:.4f}, seeker_val={val_s:.4f}")
except AssertionError:
    _fail("game values", f"hider={val_h:.4f} > seeker={val_s:.4f}")

N_ex = payoff.shape[0]
try:
    assert len(c_h) == N_ex + 1
    _ok("objective vector c has length N+1")
except AssertionError:
    _fail("objective vector length", f"got {len(c_h)}, expected {N_ex+1}")

try:
    assert A_ub_h.shape == (N_ex, N_ex + 1)
    _ok("A_ub matrix has shape (N, N+1)")
except AssertionError:
    _fail("A_ub shape", f"got {A_ub_h.shape}")

uniform_payoff = np.full((3, 3), 2.0)
np.fill_diagonal(uniform_payoff, -1.0)
p_u, v_u, *_ = solve_game(uniform_payoff, computer_role="hider", matrix_perspective="hider")
try:
    assert np.allclose(p_u, [1/3, 1/3, 1/3], atol=1e-5)
    _ok("uniform payoff matrix → uniform strategy")
except AssertionError:
    _fail("uniform strategy", f"got {p_u}")


# ============================================================================
# 5. GameEngine integration
# ============================================================================
_section("5. GameEngine integration")

try:
    eng = GameEngine(N=4, seed=0)
    _ok("GameEngine(N=4) constructs without error")
except Exception as e:
    _fail("GameEngine construction", str(e))

try:
    result = eng.solve(computer_role="hider")
    assert isinstance(result, SolverResult)
    _ok("solve() returns a SolverResult")
except Exception as e:
    _fail("solve() returns SolverResult", str(e))

try:
    assert result.N == 4
    # Both matrices must be present and correctly shaped
    assert result.hider_payoff_matrix.shape == (4, 4)
    assert result.seeker_payoff_matrix.shape == (4, 4)
    # payoff_matrix property must still work (backward compat)
    assert result.payoff_matrix.shape == (4, 4)
    assert len(result.computer_probabilities) == 4
    assert abs(result.computer_probabilities.sum() - 1.0) < 1e-6
    _ok("SolverResult fields are consistent with N=4")
except AssertionError as e:
    _fail("SolverResult consistency", str(e))

# display_matrix() returns the correct perspective
try:
    dm_h = result.display_matrix("hider")
    dm_s = result.display_matrix("seeker")
    assert np.array_equal(dm_h, result.hider_payoff_matrix)
    assert np.array_equal(dm_s, result.seeker_payoff_matrix)
    _ok("display_matrix() returns correct perspective for each role")
except AssertionError as e:
    _fail("display_matrix()", str(e))

# Hider and seeker matrices must differ (they encode opposite perspectives)
try:
    assert not np.array_equal(result.hider_payoff_matrix, result.seeker_payoff_matrix)
    _ok("hider_payoff_matrix and seeker_payoff_matrix are different")
except AssertionError:
    _fail("matrices differ", "hider and seeker matrices are identical — unexpected")

try:
    r_h = eng.solve(computer_role="hider")
    r_s = eng.solve(computer_role="seeker")
    assert r_h.computer_role == "hider"
    assert r_s.computer_role == "seeker"
    _ok("solve() works for both 'hider' and 'seeker' roles")
except Exception as e:
    _fail("solve() both roles", str(e))

try:
    eng2d = GameEngine(N=9, grid_2d=True, seed=5)
    r2d = eng2d.solve(computer_role="seeker")
    assert r2d.grid_rows == 3 and r2d.grid_cols == 3
    assert r2d.hider_payoff_matrix.shape == (9, 9)
    assert r2d.seeker_payoff_matrix.shape == (9, 9)
    _ok("2-D world (9 cells) produces 9×9 payoff matrices and 3×3 grid dims")
except Exception as e:
    _fail("2-D world", str(e))

try:
    eng_nm = GameEngine(N=12, rows=3, cols=4, grid_2d=True, seed=7)
    r_nm = eng_nm.solve(computer_role="hider")
    assert r_nm.grid_rows == 3 and r_nm.grid_cols == 4
    assert r_nm.hider_payoff_matrix.shape == (12, 12)
    assert r_nm.seeker_payoff_matrix.shape == (12, 12)
    assert len(r_nm.computer_probabilities) == 12
    assert abs(r_nm.computer_probabilities.sum() - 1.0) < 1e-6
    _ok("n×m world (3×4, 12 cells) produces 12×12 payoff matrices and 3×4 grid dims")
except Exception as e:
    _fail("n×m world (3×4)", str(e))

try:
    GameEngine(N=12, rows=3, cols=5, grid_2d=True)
    _fail("rows×cols≠N raises ValueError", "no exception raised")
except ValueError:
    _ok("GameEngine(N=12, rows=3, cols=5, grid_2d=True) raises ValueError")

try:
    eng_p = GameEngine(N=5, proximity=True, seed=3)
    rp = eng_p.solve(computer_role="hider")
    assert rp.proximity_enabled is True
    _ok("proximity_enabled flag propagates to SolverResult")
except Exception as e:
    _fail("proximity flag", str(e))

try:
    eng_r = GameEngine(N=6, seed=1)
    types_before = [c.place_type for c in eng_r.cells]
    eng_r.regenerate_world(seed=999)
    types_after = [c.place_type for c in eng_r.cells]
    assert types_before != types_after
    _ok("regenerate_world() produces a new world")
except AssertionError:
    _fail("regenerate_world()", "world did not change — very unlikely, try again")
except Exception as e:
    _fail("regenerate_world()", str(e))

try:
    GameEngine(N=1)
    _fail("N=1 raises ValueError", "no exception raised")
except ValueError:
    _ok("GameEngine(N=1) raises ValueError")

try:
    GameEngine(N=5, grid_2d=True)
    _fail("N=5 grid_2d raises ValueError", "no exception raised")
except ValueError:
    _ok("GameEngine(N=5, grid_2d=True) raises ValueError")


# ============================================================================
# Summary
# ============================================================================
total = _passed + _failed
print(f"\n{'='*60}")
print(f"  Results: {_passed}/{total} passed", end="")
if _failed == 0:
    print(f"  {GREEN}All tests passed!{RESET}")
else:
    print(f"  {RED}{_failed} failed{RESET}")
print(f"{'='*60}\n")

if __name__ == "__main__":
    sys.exit(0 if _failed == 0 else 1)