import json
import os
import math
from framing import Substrate
from InvariantCodeGenerator import InvariantCodeGenerator
from autowire import autowire_step


class Engine:
    def __init__(self, graph_path: str = "operator_graph.json", continuity_path: str = "continuity_state.json"):
        self.graph_path = graph_path
        self.continuity_path = continuity_path
        self.tick = 0
        self.history = []

        # 1. Load active substrate & pre-calculated physics constants
        self.substrate = Substrate("framing.json")
        self.framing = self.substrate.get_scope_dict()

        # 2. Invariant & Backfeed Tracking Variables (Prevents AttributeError on Tick 1)
        self.baseline_identity = None
        self.identity_continuity = 1.0
        self.previous_continuity = 1.0
        self.previous_continuity_velocity = 0.0
        self.continuity_velocity = 0.0
        self.continuity_acceleration = 0.0
        self.continuity_phase = "growth"
        self.entropy_gradient = 0.0
        self.causal_metrics = {"collapse_pressure": 0.0}
        self.scheduler_action = "expand"

        # 3. Base Physics & Orbital State Defaults
        self.entropy = 0.0
        self.phi = 0.0
        self.theta = 0.0
        self.nu = 0.05
        self.omega = 0.02
        self.bloom_density = 0.1
        self.halo_convexity = 1.0
        self.shell_radius = 1.0

        # 4. Load Graph & Continuity Checkpoint, then Sync State
        self.load_graph()
        self.load_continuity_state()
        self.sync_graph_to_state()

        # 5. Extract Autowire Parameters safely
        autowire_cfg = self.graph.get("autowire", {})
        self.autowire_enabled = autowire_cfg.get("enabled", True)
        self.autowire_growth_rate = autowire_cfg.get("growth_rate", 0.05)
        self.autowire_max_rules = autowire_cfg.get("max_rules", 50)

        # 6. Materialize Dynamic Executable Code Closures
        self.build_runtime()

    def compute_state_signature(self) -> dict:
        """Computes current vector signature for identity continuity delta calculation."""
        return {
            "entropy": getattr(self, "entropy", 0.0),
            "phi": getattr(self, "phi", 0.0),
            "theta": getattr(self, "theta", 0.0),
            "nu": getattr(self, "nu", 0.05),
            "omega": getattr(self, "omega", 0.02)
        }

    def load_graph(self):
        """Loads operator_graph.json from disk."""
        if os.path.exists(self.graph_path):
            with open(self.graph_path, "r", encoding="utf-8") as f:
                self.graph = json.load(f)
        else:
            self.graph = {
                "autowire": {"enabled": True, "growth_rate": 0.05, "max_rules": 50},
                "autowire_rules": [],
                "state": {},
                "operators": {},
                "invariants": {},
                "structures": [],
                "memory_structures": []
            }

    def load_continuity_state(self):
        """Loads or initializes identity continuity checkpoint."""
        if os.path.exists(self.continuity_path):
            with open(self.continuity_path, "r", encoding="utf-8") as f:
                c_state = json.load(f)
                self.identity_continuity = c_state.get("identity_continuity", 1.0)
                self.continuity_phase = c_state.get("last_phase", "growth")

    def sync_graph_to_state(self):
        """Hydrates Engine instance variables from self.graph['state']."""
        state_dict = self.graph.get("state", {})
        for key, val in state_dict.items():
            setattr(self, key, val)

    def sync_state_to_graph(self):
        """Pushes current active variables back to self.graph['state'] dict."""
        state_keys = [
            "entropy", "phi", "theta", "nu", "omega", 
            "bloom_density", "halo_convexity", "shell_radius"
        ]
        state_dict = self.graph.setdefault("state", {})
        for key in state_keys:
            if hasattr(self, key):
                state_dict[key] = getattr(self, key)

    def save_continuity_state(self):
        """Persists continuity state and autowire rules back to JSON."""
        self.sync_state_to_graph()
        c_state = {
            "identity_continuity": round(self.identity_continuity, 6),
            "autowire_rules": self.graph.get("autowire_rules", []),
            "last_phase": self.continuity_phase
        }
        with open(self.continuity_path, "w", encoding="utf-8") as f:
            json.dump(c_state, f, indent=4)

    def build_runtime(self):
        """Compiles operator and invariant strings into executable closures."""
        gen = InvariantCodeGenerator(self.graph)
        self.invariants = gen.generate_invariant_functions()
        self.operators = gen.generate_operator_functions()

    def step(self) -> dict:
        """Runs a single clock cycle step through the whole engine stack."""
        # Step A: Evaluate Invariants first (calculates velocity, backfeed, & updates continuity_phase)
        for name, fn in self.invariants.items():
            try:
                val = fn(self)
                setattr(self, name, val)
            except Exception:
                pass

        # Step B: Execute Operators second (mutates state variables like nu, omega, phi, theta)
        for op in self.operators:
            try:
                op(self)
            except Exception:
                pass

        # Step C: Run Autowire Step (evaluates dynamic growth, injects emergent operators, re-compiles if needed)
        autowire_step(self)

        # Step D: Advance clock and record snapshot
        self.tick += 1
        snapshot = {
            "tick": self.tick,
            "phase": getattr(self, "continuity_phase", "growth"),
            "continuity": round(getattr(self, "identity_continuity", 1.0), 4),
            "entropy": round(getattr(self, "entropy", 0.0), 4),
            "phi": round(getattr(self, "phi", 0.0), 4),
            "theta": round(getattr(self, "theta", 0.0), 4)
        }
        self.history.append(snapshot)
        return snapshot


if __name__ == "__main__":
    print("=== STARTING ENGINE 2.0 VERIFICATION TEST ===")
    engine = Engine()

    # Run 10 initial ticks to test execution pipeline
    for i in range(10):
        snap = engine.step()
        print(f"Tick {snap['tick']:03d} | Phase: {snap['phase']:<8} | Continuity: {snap['continuity']:.4f} | Phi: {snap['phi']:.4f} | Theta: {snap['theta']:.4f}")

    # Checkpoint output state
    engine.save_continuity_state()
    print("=== VERIFICATION TEST COMPLETE: continuity_state.json SAVED ===")