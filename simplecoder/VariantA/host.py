# host.py
from lattice import ClockworkLattice
from VanirOperator import VanirOperator

class ClockworkHost:
    def __init__(self, lattice: ClockworkLattice):
        """
        The Host wraps a lattice and provides:
        - injection of external operators
        - propagation across the lattice
        - hooks for engine-level response
        """
        self.lattice = lattice
        self.payload = None
        self.payload_history = []

    # ---------------------------------------------------------
    # Inject an operator (function, object, rule, Vanir output)
    # ---------------------------------------------------------
    def inject(self, operator):
        self.payload = operator
        self.payload_history.append(operator)

    # ---------------------------------------------------------
    # Propagate operator across lattice
    # ---------------------------------------------------------
    def propagate(self):
        if self.payload is None:
            return
        for row in self.lattice.engines:
            for engine in row:
                engine.external_payload = self.payload

    def run(self, ticks: int = 50, verbose: bool = False):
        trajectory = []
        for t in range(ticks):
            snapshot = self.step()
            trajectory.append(snapshot)
            if verbose:
                print(f"Host Tick {t:03d} | snapshot={snapshot}")
        return trajectory


    # ---------------------------------------------------------
    # Host tick: lattice tick + operator propagation
    # ---------------------------------------------------------
    def step(self):
        snapshot = self.lattice.step_all()
        if self.payload is not None:
            for row in self.lattice.engines:
                for engine in row:
                    if hasattr(engine, "external_payload"):
                        self.apply_payload(engine)
        return snapshot

    # ---------------------------------------------------------
    # How engines respond to payload
    # ---------------------------------------------------------
    def apply_payload(self, engine):
        payload = engine.external_payload
        if callable(payload):
            delta = payload(engine.phi, engine.theta)
            engine.nu += delta
        elif isinstance(payload, dict):
            if "nu_delta" in payload:
                engine.nu += payload["nu_delta"]
            if "omega_delta" in payload:
                engine.omega += payload["omega_delta"]
            if "bloom_boost" in payload:
                engine.nu += engine.evaluate_bloom_anti_collapse(engine.history[-1]) * payload["bloom_boost"]
        elif isinstance(payload, (int, float)):
            engine.nu += payload * 0.01

    # ---------------------------------------------------------
    # Run host for N ticks
    # ---------------------------------------------------------
    def run(self, ticks: int = 50, verbose: bool = False):
        trajectory = []
        for t in range(ticks):
            snapshot = self.step()
            trajectory.append(snapshot)
            if verbose:
                print(f"Host Tick {t:03d} | snapshot={snapshot}")
        return trajectory



# ---------------------------------------------------------
# Runtime wiring: Host + Lattice + VanirOperator
# ---------------------------------------------------------
if __name__ == "__main__":
    lattice = ClockworkLattice(size=3, ticks=20)
    host = ClockworkHost(lattice)
    operator = VanirOperator(engine=lattice, max_ticks=200)

    def host_step_fn(tick):
        return {"center": 0, "energy": tick * 0.01, "depth": 3, "width": 3}

    # Run the host directly
    host.run(ticks=200, verbose=True)

    # Run the operator on top of the host
    operator.run(host_step_fn)

