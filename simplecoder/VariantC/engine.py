import json
import os
import math
import functools

def normalize_to_zero_frame(val: float, tolerance: float = 1e-12) -> float:
    """
    Inferred from: ∀x, x ∈ 0-frame
    Collapses floating-point numerical drift back to canonical zero ground.
    """
    if abs(val) < tolerance:
        return 0.0
    return val

class ClockworkEngine:
    def __init__(self, metrics_path: str = "metrics.json", state_path: str = "state.json"):
        self.metrics_path = metrics_path
        self.state_path = state_path
        
        # 1. Load metrics config
        self.metrics = self._load_metrics(metrics_path)
        
        # 2. Physics Invariants
        self.c = 299792458.0                  # m/s
        self.hbar = 1.054571817e-34           # J·s
        self.G = 6.67430e-11                  # m^3/(kg·s^2)
        
        # 3. Dynamic State Variables (Default values)
        self.k = 0                            # Ticks
        self.phi = 0.0                        # Internal phase
        self.theta = 0.0                      # Outer rotation angle
        self.nu = 0.05                        # Internal drift rate
        self.omega = 0.02                     # Outer rotation rate
        
        # 4. State Persistence Reload
        self._load_state()

        # 5. Watcher & Trajectory Memory
        self.history = []
        self.stagnation_count = 0
        self.omega_config = self.metrics.get("omega_operators", {})
        self.watcher_config = self.omega_config.get("omega5_watcher", {})

    def _load_metrics(self, path: str) -> dict:
        if not os.path.exists(path):
            print(f"[!] Warning: {path} not found. Running with defaults.")
            return {}
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_state(self):
        """State Persistence - Load checkpoint from state.json if present."""
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
        """State Persistence - Save current engine parameters to state.json."""
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
        """Evaluates spatial variance across trajectory history to prevent collapse."""
        if len(self.history) < 5:
            return 0.0

        recent_pts = self.history[-5:]
        avg_x = sum(pt[0] for pt in recent_pts) / 5.0
        avg_y = sum(pt[1] for pt in recent_pts) / 5.0
        
        var = sum(math.sqrt((pt[0]-avg_x)**2 + (pt[1]-avg_y)**2) for pt in recent_pts) / 5.0
        
        if var < 0.05:
            return 0.01
        return 0.0

    def evaluate_spine_step(self, F_t: float, grad_E: float, beta: float = 0.01) -> float:
        """Inferred from: F(t+1) = F(t) + β · ∇E(F(t))"""
        return F_t + (beta * grad_E)

    def evaluate_watcher_rules(self, current_coords: tuple) -> str:
        """Active Watcher Execution Guard."""
        triggers = self.watcher_config.get("triggers", {})
        max_depth = triggers.get("max_recursion_depth", 1000000)
        stag_thresh = triggers.get("stagnation_threshold", 0.0001)
        stag_pat = triggers.get("stagnation_patience", 3)
        
        if self.k >= max_depth:
            return "WATCHER_INTERVENTION: HARD_EXIT (Max Recursion Depth Reached)"

        if len(self.history) > 0:
            last_coords = self.history[-1]
            dx = current_coords[0] - last_coords[0]
            dy = current_coords[1] - last_coords[1]
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < stag_thresh:
                self.stagnation_count += 1
            else:
                self.stagnation_count = 0

            if self.stagnation_count >= stag_pat:
                self.nu *= 1.5  
                return f"WATCHER_INTERVENTION: DOWNSHIFT_PERTURBATION (nu modulated to {self.nu:.4f})"

        return "NOMINAL"

    def step(self) -> dict:
        """Runs 1 clock tick update over all mapped invariants."""
        # 1. Erdős-Tarun Spatial Projection + Zero Frame Grounding
        theta_k = self.phi * 2.0 * math.pi
        X_k = normalize_to_zero_frame(math.cos(theta_k))
        Y_k = normalize_to_zero_frame(math.sin(theta_k))
        coords = (round(X_k, 4), round(Y_k, 4))

        # 2. Watcher Safeguard Evaluation
        watcher_status = self.evaluate_watcher_rules(coords)

        # 3. Bloom Anti-Collapse & Energy Gradient Computations
        bloom_force = self.evaluate_bloom_anti_collapse(coords)
        grad_E = math.sin(self.phi) * 0.02
        
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

    def run(self, max_ticks: int = 10) -> list:
        trajectory = []
        for _ in range(max_ticks):
            current_state = self.step()
            trajectory.append(current_state)
            if "HARD_EXIT" in current_state["status"]:
                print("\n[!] Watcher triggered Hard Exit. Halting trajectory.")
                break
        
        self.save_state()
        return trajectory


class InvariantCodeGenerator:
    """Translates invariant formulas from metrics.json into generated_structures.py"""
    def __init__(self, metrics: dict):
        self.metrics = metrics

    def generate_python_module(self) -> str:
        code_lines = [
            "# ==========================================================",
            "# AUTO-GENERATED INVARIANT STRUCTURES",
            "# Materialized directly from metrics.json invariants",
            "# ==========================================================",
            "import math",
            "import functools",
            "import numpy as np",
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

        if "coherence_law" in self.metrics:
            code_lines.extend([
                "def check_coherence(user, intent, action):",
                "    \"\"\"Inferred from: Act(u,i,a) = a ⇔ Coherent(u,i,a)\"\"\"",
                "    is_coherent = (action == intent)",
                "    if not is_coherent:",
                "        raise ValueError('Coherence Violation: Action diverged from Intent')",
                "    return True",
                ""
            ])

        if "zero_frame_invariant" in self.metrics:
            code_lines.extend([
                "@register_invariant",
                "def normalize_to_zero_frame(val: float, tolerance: float = 1e-12) -> float:",
                "    \"\"\"Inferred from: ∀x, x ∈ 0-frame\"\"\"",
                "    if abs(val) < tolerance:",
                "        return 0.0",
                "    return val",
                ""
            ])

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

        code_lines.extend([
            "def invariant_guard(invariants=None):",
            "    \"\"\"Decorator that intercepts state updates and verifies coherence before returning.\"\"\"",
            "    def decorator(func):",
            "        @functools.wraps(func)",
            "        def wrapper(*args, **kwargs):",
            "            result = func(*args, **kwargs)",
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

        if "erdos_tarun_structure" in self.metrics:
            code_lines.extend([
                "def project_erdos_tarun(phi_k: float) -> tuple:",
                "    \"\"\"Inferred from: θ_k = φ_k * 2π ; (X_k, Y_k) = (cos θ_k, sin θ_k)\"\"\"",
                "    theta_k = phi_k * 2.0 * math.pi",
                "    return math.cos(theta_k), math.sin(theta_k)",
                ""
            ])

        if "spine_recurrence" in self.metrics:
            code_lines.extend([
                "def evaluate_spine_step(F_t: float, grad_E: float, beta: float = 0.01) -> float:",
                "    \"\"\"Inferred from: F(t+1) = F(t) + β · ∇E(F(t))\"\"\"",
                "    return F_t + (beta * grad_E)",
                ""
            ])

        omega_ops = self.metrics.get("omega_operators", {})
        if omega_ops:
            code_lines.extend([
                "class OmegaSupervisor:",
                "    \"\"\"Auto-generated meta-controller for dynamic invariants.\"\"\"",
                "    def __init__(self):"
            ])
            for op_name, op_data in omega_ops.items():
                enabled = op_data.get("enabled", False)
                code_lines.append(f"        self.{op_name}_active = {enabled}")
            code_lines.append("")

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
        
        generator = InvariantCodeGenerator(metrics_data)
        generated_code = generator.generate_python_module()
        
        with open("generated_structures.py", "w", encoding="utf-8") as f:
            f.write(generated_code)
            
        output += "\n[✔] Successfully updated 'generated_structures.py' and saved state to 'state.json'!"

    return output


if __name__ == "__main__":
    print(run_engine(ticks=10))