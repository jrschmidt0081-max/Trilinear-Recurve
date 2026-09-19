import json
import math

class Substrate:
    """Hydrates static framing.json into a live physical substrate."""
    def __init__(self, framing_path: str = "framing.json"):
        self.framing_path = framing_path
        self.raw_data = self.load_framing()
        self.constants = {}
        self.initialize_constants()

    def load_framing(self) -> dict:
        try:
            with open(self.framing_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def initialize_constants(self):
        """Pre-computes physical constants into usable floating-point values."""
        # Standard SI fundamental constants (or normalized units)
        c = 299792458.0
        hbar = 1.054571817e-34
        G = 6.67430e-11

        self.constants = {
            "c": c,
            "hbar": hbar,
            "G": G,
            "planck_length": math.sqrt((hbar * G) / (c**3)),
            "planck_time": math.sqrt((hbar * G) / (c**5)),
            "planck_mass": math.sqrt((hbar * c) / G),
        }

    def evaluate_coordinate(self, phi: float, theta: float) -> tuple:
        """Executes Erdos-Tarun orbital mapping: (X_k, Y_k) = (cos theta, sin theta)."""
        rad_theta = theta * 2.0 * math.pi
        return (math.cos(rad_theta), math.sin(rad_theta))

    def get_scope_dict(self) -> dict:
        """Exposes hydrated substrate constants to InvariantCodeGenerator."""
        scope = dict(self.raw_data)
        scope.update(self.constants)
        return scope