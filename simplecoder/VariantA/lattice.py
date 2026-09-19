# lattice.py
from engine import ClockworkEngine
import math
import random

class ClockworkLattice:
    def __init__(self, size: int = 3, ticks: int = 10):
        self.size = size
        self.ticks = ticks

        # Build lattice of engines
        self.engines = [
            [ClockworkEngine() for _ in range(size)]
            for _ in range(size)
        ]

        # Initialize engines with random values
        for row in self.engines:
            for engine in row:
                engine.phi += random.uniform(-0.5, 0.5)
                engine.nu += random.uniform(-0.01, 0.01)
                engine.omega += random.uniform(-0.01, 0.01)

    # ---------------------------------------------------------
    # Neighbor lookup
    # ---------------------------------------------------------
    def get_neighbors(self, i, j):
        neighbors = []
        for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
            ni, nj = i + di, j + dj
            if 0 <= ni < self.size and 0 <= nj < self.size:
                neighbors.append(self.engines[ni][nj])
        return neighbors

    # ---------------------------------------------------------
    # Coupling rule: drift synchronization + bloom diffusion
    # ---------------------------------------------------------
    def apply_coupling(self):
        for i in range(self.size):
            for j in range(self.size):
                engine = self.engines[i][j]
                neighbors = self.get_neighbors(i, j)

                if not neighbors:
                    continue

                # 1. Drift coupling (nu sync)
                avg_nu = sum(nu.nu for nu in neighbors) / len(neighbors)
                engine.nu = (engine.nu * 0.9) + (avg_nu * 0.1)

                # 2. Bloom diffusion
                bloom_neighbors = [
                    n.evaluate_bloom_anti_collapse(n.history[-1])
                    if len(n.history) > 0 else 0.0
                    for n in neighbors
                ]
                bloom_pressure = sum(bloom_neighbors) / len(neighbors)
                engine.nu += bloom_pressure * 0.05

                # 3. Watcher propagation
                if engine.stagnation_count >= 3:
                    for n in neighbors:
                        n.nu *= 1.1  # small perturbation ripple

    # ---------------------------------------------------------
    # Step entire lattice
    # ---------------------------------------------------------
    def step_all(self):
        lattice_state = []

        # Step each engine
        for row in self.engines:
            row_state = []
            for engine in row:
                state = engine.step()
                row_state.append(state)
            lattice_state.append(row_state)

        # Apply coupling AFTER all engines step
        self.apply_coupling()

        return lattice_state

    # ---------------------------------------------------------
    # Run lattice for N ticks
    # ---------------------------------------------------------
    def run(self):
        trajectory = []
        for _ in range(self.ticks):
            snapshot = self.step_all()
            trajectory.append(snapshot)

        # Persist each engine's state
        for row in self.engines:
            for engine in row:
                engine.save_state()

        return trajectory


# ---------------------------------------------------------
# Pretty printer
# ---------------------------------------------------------
def run_lattice(size: int = 3, ticks: int = 10) -> str:
    lattice = ClockworkLattice(size=size, ticks=ticks)
    trajectory = lattice.run()

    output = "=== CLOCKWORK LATTICE ENGINE ===\n"
    for t, snapshot in enumerate(trajectory):
        output += f"\nTick {t:02d}:\n"
        for i, row in enumerate(snapshot):
            row_str = []
            for j, cell in enumerate(row):
                x, y = cell["coords"]
                status = cell["status"]
                row_str.append(f"({x:>6},{y:>6}) {status}")
            output += f"  Row {i}: " + " | ".join(row_str) + "\n"
    return output
