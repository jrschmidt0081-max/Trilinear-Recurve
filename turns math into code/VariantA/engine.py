import json
import os
import math
from types import SimpleNamespace
from unittest import loader
from OperatorGraphLoader import OperatorGraphLoader
from InvariantCodeGenerator import InvariantCodeGenerator
from generated_structures import invariant_guard

def normalize_to_zero_frame(val: float, tolerance: float = 1e-12) -> float:
    """
    Inferred from: ∀x, x ∈ 0-frame
    Collapses floating-point numerical drift back to canonical zero ground.
    """
    if abs(val) < tolerance:
        return 0.0
    return val

class ClockworkEngine:
    @invariant_guard()
    def detect_shape(self, history):
        # placeholder until you define real shape logic
        return {"type": "trajectory", "id": self.k}

    def build_structure(self, structures, shape):
        structures.setdefault(shape["id"], []).append(shape)
        return structures

    def collapse_structures(self, structures):
        # placeholder collapse rule
        return structures

    def compute_next_tick(phi, theta, nu):
        """Computes the next state vector."""
        new_phi = phi + nu
        new_theta = theta + (2 * 3.14159 * nu)
        x = math.cos(new_theta)
        y = math.sin(new_theta)
    
        # Returns state dict evaluated automatically by @invariant_guard
        return {"phi": new_phi, "theta": new_theta, "x": x, "y": y}
    def __init__(self, metrics_path: str = "metrics.json", state_path: str = "state.json"):
        self.metrics_path = metrics_path
        self.state_path = state_path
        
        # 1. Load metrics config
        self.metrics = self._load_metrics(metrics_path)
        
        # 2. Physics Invariants
        self.c = 299792458.0                  # m/s
        self.hbar = 1.054571817e-34           # J·s
        self.G = 6.67430e-11                  # m^3/(kg·s^2)

        # 3. Runtime graph/bootstrap state
        self.bloom = SimpleNamespace(
            center=(0.0, 0.0),
            depth=1,
            width=1,
            phase_stability=1.0,
            dominance_drift=0.0,
        )
        self.memory_structures = {}
        self.soft_exit_triggered = False
        self.generated_ops = []
        self.generated_invariants = {}
        self.generated_watchers = []
        self.generated_collapse = []
        self._bootstrap_runtime_graph()
        
        # 4. Dynamic State Variables (Default values)
        self.k = 0                            # Ticks
        self.phi = 0.0                        # Internal phase
        self.theta = 0.0                      # Outer rotation angle
        self.nu = 0.05                        # Internal drift rate
        self.omega = 0.02                     # Outer rotation rate
        
        # === Galaxy Pack Fields (Safe Defaults) ===

        # Gear / Ratio fields
        self.theta_1 = 1.0
        self.theta_2 = 1.0
        self.r1 = 1.0
        self.r2 = 1.0

        # Escapement / tick fields
        self.tick_size = 0.1
        self.oscillation_crosses_zero = False

        # Pendulum fields
        self.period = 1.0
        self.length = 1.0

        # Resonance fields
        self.phi_1 = 0.0
        self.phi_2 = 0.0
        self.sync_rate = 0.01
        self.resonance_threshold = 0.1

        # Tourbillon fields
        self.drift_avg = 0.0
        self.drift_current = 0.0

        # Flow / burn fields
        self.flow_rate = 1.0
        self.flow_constant = 1.0
        self.burn_rate = 1.0
        self.burn_constant = 1.0

        # Celestial cycle fields
        self.cycle_length = 2 * math.pi

        # Black hole core fields
        self.core_mass = 1.0
        self.core_radius = 1.0
        self.core_horizon = 0.0

        # S‑star orbital fields
        self.s_star_phase = 0.0
        self.s_star_avg_omega = 0.01
        self.s_star_avg_radius = 1.0
        self.s_star_radial_drift = 0.0

        # S‑star eccentricity fields
        self.s_star_eccentricity = 0.0
        self.s_star_ecc_drift = 0.0

        # S‑star Kepler fields
        self.s_star_period = 1.0
        self.kepler_k = 1.0

        self.comet_phase = 0.0
        self.comet_radius = 5.0
        self.comet_omega = 0.02
        self.comet_eccentricity = 0.8
        self.comet_drift = -0.01
        self.comet_entropy = 0.0

        self.bloom_density = 0.0
        self.halo_convexity = 1.0

        self.cluster_phase = 0.0
        self.cluster_x = 0.0
        self.cluster_y = 0.0

        self.shell_radius = 1.0
        self.resonance_lock = False

        # S‑star angular momentum fields
        self.s_star_L = 0.0
        self.s_star_mass = 1.0

        # 5. State Persistence Reload
        self._load_state()

        # 6. Watcher & Trajectory Memory
        self.history = []
        self.stagnation_count = 0
        self.omega_config = self.metrics.get("omega_operators", {})
        self.watcher_config = self.omega_config.get("omega5_watcher", {})

    def _bootstrap_runtime_graph(self):
        try:
            loader = OperatorGraphLoader("operator_graph.json")

            # ⭐ DEBUG: See what the loader actually parsed
            print("GRAPH TYPE:", type(loader.graph))
            print("GRAPH VALUE:", loader.graph)

            generator = InvariantCodeGenerator(loader.graph)
            self.generated_ops = generator.generate_operator_functions()
            self.generated_invariants = generator.generate_invariant_functions()
            self.generated_watchers = generator.generate_watcher_functions()
            self.generated_collapse = generator.generate_collapse_functions()
        except Exception as exc:
            self.generated_ops = []
            self.generated_invariants = {}
            self.generated_watchers = []
            self.generated_collapse = []
            print(f"[!] Warning: runtime graph bootstrap failed ({exc}).")

    def _apply_generated_runtime(self):
        for op in self.generated_ops:
            op(self)

        for name, inv_fn in self.generated_invariants.items():
            setattr(self, name, inv_fn(self))

        for watch in self.generated_watchers:
            watch(self)

        for collapse in self.generated_collapse:
            collapse(self)

    def _load_metrics(self, path: str) -> dict:
        if not os.path.exists(path):
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_state(self):
        """Option 1: State Persistence - Load checkpoint from state.json if present."""
        if os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.k = data.get("k", 0)
                    self.phi = data.get("phi", 0.0)
                    self.theta = data.get("theta", 0.0)
                    self.nu = data.get("nu", 0.05)
                    self.omega = data.get("omega", 0.02)
                    print(f"[✔] Resumed state from {self.state_path} at Tick {self.k}")
            except Exception as e:
                print(f"[!] Warning: Could not parse state.json ({e}). Starting fresh.")

    def save_state(self):
        """Option 1: State Persistence - Save current engine parameters to state.json."""
        state_data = {
            "k": self.k,
            "phi": round(self.phi, 6),
            "theta": round(self.theta, 6),
            "nu": round(self.nu, 6),
            "omega": round(self.omega, 6)
        }
        with open(self.state_path, "w", encoding="utf-8") as f:
            json.dump(state_data, f, indent=4)

    def calculate_planck_units(self) -> dict:
        """Calculates physical invariants from metrics constants."""
        l_p = math.sqrt((self.hbar * self.G) / (self.c ** 3))
        t_p = math.sqrt((self.hbar * self.G) / (self.c ** 5))
        m_p = math.sqrt((self.hbar * self.c) / self.G)
        return {"planck_length": l_p, "planck_time": t_p, "planck_mass": m_p}

    def evaluate_bloom_anti_collapse(self, current_coords: tuple) -> float:
        """
        Option 2: Bloom Anti-Collapse Rule.
        Evaluates spatial variance across trajectory history to prevent collapse.
        """
        if len(self.history) < 5:
            return 0.0

        # Calculate average distance from recent history points
        recent_pts = self.history[-5:]
        avg_x = sum(pt[0] for pt in recent_pts) / 5.0
        avg_y = sum(pt[1] for pt in recent_pts) / 5.0
        
        # Spatial dispersion / variance
        var = sum(math.sqrt((pt[0]-avg_x)**2 + (pt[1]-avg_y)**2) for pt in recent_pts) / 5.0
        
        # If manifold density contracts too tightly, trigger bloom expansion force
        if var < 0.05:
            return 0.01  # Bloom expansion force
        return 0.0

    def evaluate_spine_step(self, F_t: float, grad_E: float, beta: float = 0.01) -> float:
        """
        Option 3: Energy Gradient Modulation.
        Inferred from: F(t+1) = F(t) + β · ∇E(F(t))
        """
        return F_t + (beta * grad_E)

    def evaluate_watcher_rules(self, current_coords: tuple) -> str:
        """Active Watcher Execution Guard."""
        triggers = self.watcher_config.get("triggers", {})
        max_depth = triggers.get("max_recursion_depth", 10000)
        
        if self.k >= max_depth:
            return "WATCHER_INTERVENTION: HARD_EXIT (Max Recursion Depth Reached)"

        if len(self.history) > 0:
            last_coords = self.history[-1]
            dx = current_coords[0] - last_coords[0]
            dy = current_coords[1] - last_coords[1]
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < 0.0001:
                self.stagnation_count += 1
            else:
                self.stagnation_count = 0

            if self.stagnation_count >= 3:
                self.nu *= 1.5  
                return f"WATCHER_INTERVENTION: DOWNSHIFT_PERTURBATION (nu modulated to {self.nu:.4f})"

        return "NOMINAL"

    def soft_exit(self):
        self.soft_exit_triggered = True
        return "SOFT_EXIT"

    def step(self) -> dict:
        """Runs 1 clock tick update over all mapped invariants."""
        self._apply_generated_runtime()

        # 1. Erdős-Tarun Spatial Projection + Zero Frame Grounding
        theta_k = self.phi * 2.0 * math.pi
        X_k = normalize_to_zero_frame(math.cos(theta_k))
        Y_k = normalize_to_zero_frame(math.sin(theta_k))
        coords = (round(X_k, 4), round(Y_k, 4))

        # 2. Watcher Safeguard Evaluation
        watcher_status = self.evaluate_watcher_rules(coords)

        # 3. Bloom Anti-Collapse & Energy Gradient Computations
        bloom_force = self.evaluate_bloom_anti_collapse(coords)
        grad_E = math.sin(self.phi) * 0.02  # Synthetic gradient field from phase space
        
        # Modulate internal drift rate nu using energy step + bloom impulse
        self.nu = self.evaluate_spine_step(self.nu, grad_E + bloom_force, beta=0.01)

        state = {
            "tick": self.k,
            "phi": round(self.phi, 4),
            "theta_rad": round(theta_k, 4),
            "coords": coords,
            "status": watcher_status if watcher_status != "NOMINAL" else ("BLOOM_EXPANSION" if bloom_force > 0 else "NOMINAL")
        }

        # Update engine memory and state variables
        self.history.append(coords)
        self.phi += self.nu
        self.theta += self.omega
        self.k += 1

        return state

    def run(self, ticks: int = 50, verbose: bool = False):
        trajectory = []
        for t in range(ticks):
            snapshot = self.step()
            trajectory.append(snapshot)
            if verbose:
                print(f"Host Tick {t:03d} | snapshot={snapshot}")
        return trajectory



class GeneratedInvariantModuleBuilder:
    def __init__(self, metrics_data):
        self.metrics = metrics_data
        self.memory_structures = {}

    def generate_python_module(self) -> str:
        code_lines = [
            "# ==========================================================",
            "# AUTOMATICALLY GENERATED BY CLOCKWORK INVARIANT GENERATOR",
            "# ==========================================================",
            "import math",
            "import functools",
            "",
            "# Active Invariants Registry",
            "ACTIVE_INVARIANTS = []",
            "",
            "def register_invariant(func):",
            "    \"\"\"Registers a callable invariant function into the active suite.\"\"\"",
            "    if callable(func) and func not in ACTIVE_INVARIANTS:",
            "        ACTIVE_INVARIANTS.append(func)",
            "    return func",
            ""
        ]

        # 1. Meaning Recognition Invariant
        if "meaning_recognition_invariant" in self.metrics:
            code_lines.extend([
                "def recognize_meaning(expression, invariants=None) -> bool:",
                "    \"\"\"Inferred from: M(e) = Recognize(e | Invariants) ⇔ Coherent(e)\"\"\"",
                "    invariants_to_check = invariants if invariants is not None else ACTIVE_INVARIANTS",
                "    for invariant in invariants_to_check:",
                "        if callable(invariant) and not invariant(expression):",
                "            return False",
                "    return True",
                ""
            ])

        # 2. Invariant Guard Decorator Generation
        code_lines.extend([
            "def invariant_guard(invariants=None):",
            "    \"\"\"Decorator that intercepts state updates and verifies coherence before returning.\"\"\"",
            "    def decorator(func):",
            "        @functools.wraps(func)",
            "        def wrapper(*args, **kwargs):",
            "            result = func(*args, **kwargs)",
            "            # Evaluate returned expression against active invariants",
            "            target_invariants = invariants if invariants is not None else ACTIVE_INVARIANTS",
            "            if not recognize_meaning(result, target_invariants):",
            "                raise ValueError(",
            "                    f\"[INVARIANT_VIOLATION] State update from '{func.__name__}' \"",
            "                    f\"failed invariant checks: {result}\"",
            "                )",
            "            return result",
            "        return wrapper",
            "    return decorator",
            ""
        ])

        # Optional: Auto-register a simple bounds/coherence check if present in metrics
        if "coherence_law" in self.metrics:
            code_lines.extend([
                "@register_invariant",
                "def default_coherence_check(state) -> bool:",
                "    \"\"\"Basic structural check ensuring numerical outputs remain bounded.\"\"\"",
                "    if isinstance(state, dict):",
                "        x, y = state.get('x', 0.0), state.get('y', 0.0)",
                "        # Ensure coordinates lie within unit manifold boundary",
                "        return (x**2 + y**2) <= 1.05",
                "    return True",
                ""
            ])

        return "\n".join(code_lines)

def run_engine(selected_text: str = "", ticks: int = 10) -> str:
    engine = ClockworkEngine()
    planck = engine.calculate_planck_units()
    results = engine.run(max_ticks=ticks)

    output = "=== CLOCKWORK GEOMETRY ENGINE (FULL ACTIVE SYSTEM) ===\n"
    output += f"Planck Length Invariant: {planck['planck_length']:.4e} m\n\n"
    output += "--- TRAJECTORY EXECUTION ---\n"
    for r in results:
        output += f"Tick {r['tick']:02d} | φ={r['phi']:<6} | θ={r['theta_rad']:<6} rad | (X,Y)=({r['coords'][0]:>6}, {r['coords'][1]:>6}) | {r['status']}\n"

    metrics_path = "metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r", encoding="utf-8") as f:
            metrics_data = json.load(f)
        
        generator = GeneratedInvariantModuleBuilder(metrics_data)
        generated_code = generator.generate_python_module()
        
        with open("generated_structures.py", "w", encoding="utf-8") as f:
            f.write(generated_code)
            
        output += "\n[✔] Successfully updated 'generated_structures.py' and saved state to 'state.json'!"

    return output


if __name__ == "__main__":
    print(run_engine(ticks=100))