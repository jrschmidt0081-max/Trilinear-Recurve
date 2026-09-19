# VanirOperator.py
#
# Host-side operator that wires a running engine (Vanir-style or Clockwork-style)
# to a simple, explicit host API. The host pushes state snapshots in, and
# receives directives / patches / metrics out.

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, List, Callable


# ---------------------------------------------------------
# Minimal TickMetrics mirror (Python side)
# ---------------------------------------------------------

@dataclass
class TickMetrics:
    tick: int = 0
    center: int = 0
    energy: float = 0.0
    curvature: float = 0.0
    basin: float = 0.0
    phase_velocity: float = 0.0
    phase_drift: float = 0.0
    pll_lock_strength: float = 0.0
    inheritance_pressure: float = 0.0
    reticle_stability: float = 0.0
    depth: int = 0
    width: int = 0
    dominance_drift: float = 0.0


# ---------------------------------------------------------
# Host snapshot → metrics adapter
# ---------------------------------------------------------

def metrics_from_host_snapshot(snapshot: Dict[str, Any], tick: int) -> TickMetrics:
    """
    Convert a generic host snapshot (e.g. Clockwork lattice / engine state)
    into a TickMetrics bundle that Vanir-style engines can consume.

    Expected keys are intentionally loose; missing values fall back to defaults.
    """
    return TickMetrics(
        tick=tick,
        center=int(snapshot.get("center", 0)),
        energy=float(snapshot.get("energy", 0.0)),
        curvature=float(snapshot.get("curvature", 0.0)),
        basin=float(snapshot.get("basin", 0.0)),
        phase_velocity=float(snapshot.get("phase_velocity", 0.0)),
        phase_drift=float(snapshot.get("phase_drift", 0.0)),
        pll_lock_strength=float(snapshot.get("pll_lock_strength", 0.0)),
        inheritance_pressure=float(snapshot.get("inheritance_pressure", 0.0)),
        reticle_stability=float(snapshot.get("reticle_stability", 0.0)),
        depth=int(snapshot.get("depth", 0)),
        width=int(snapshot.get("width", 0)),
        dominance_drift=float(snapshot.get("dominance_drift", 0.0)),
    )


# ---------------------------------------------------------
# VanirOperator: host-facing API
# ---------------------------------------------------------

class VanirOperator:
    """
    Thin host operator that:
    - accepts host state snapshots
    - converts them into metrics
    - feeds metrics into a Vanir-style engine (if it supports deliver_metrics)
    - advances the engine one tick
    - exposes any directives / patches / metrics back to the host
    """

    def __init__(self, engine: Any, max_ticks: int = 1000):
        self.engine = engine
        self.max_ticks = max_ticks
        self.current_tick: int = 0
        self.history: List[TickMetrics] = []

    # -----------------------------------------------------
    # Core host API
    # -----------------------------------------------------

    def host_tick(self, host_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for the host.

        host_snapshot: arbitrary dict describing current host state
                       (Clockwork engine, lattice, etc.)

        Returns a dict with:
        - "metrics": TickMetrics (as dict)
        - "precipice_mode": optional engine mode
        - "instability": optional instability scalar
        - "bloom": optional bloom summary
        - "directive": optional coder directive / patch info
        """

        if self.current_tick >= self.max_ticks:
            return {
                "done": True,
                "reason": "max_ticks_reached",
            }

        self.current_tick += 1

        # 1) Build metrics from host snapshot
        metrics = metrics_from_host_snapshot(host_snapshot, self.current_tick)
        self.history.append(metrics)

        # 2) Deliver metrics into engine if supported
        if hasattr(self.engine, "deliver_metrics"):
            self.engine.deliver_metrics(metrics)

        # 3) Advance engine one tick
        if hasattr(self.engine, "tick"):
            # VanirEngine.tick(verbose: bool) style
            try:
                self.engine.tick(False)
            except TypeError:
                # Fallback if signature is tick() without args
                self.engine.tick()

        # 4) Collect engine-side signals / directives if available
        payload: Dict[str, Any] = {
            "done": False,
            "metrics": metrics.__dict__,
        }

        # precipice / instability
        if hasattr(self.engine, "precipice_mode"):
            payload["precipice_mode"] = getattr(self.engine, "precipice_mode")
        if hasattr(self.engine, "instability"):
            payload["instability"] = float(getattr(self.engine, "instability"))

        # bloom summary
        bloom = getattr(self.engine, "bloom", None)
        if bloom is not None:
            payload["bloom"] = {
                "center": getattr(bloom, "center", None),
                "depth": getattr(bloom, "depth", None),
                "width": getattr(bloom, "width", None),
                "phase_stability": getattr(bloom, "phase_stability", None),
                "dominance_drift": getattr(bloom, "dominance_drift", None),
            }

        # coder / directive output (if engine exposes it)
        directive = self._extract_latest_directive()
        if directive is not None:
            payload["directive"] = directive

        return payload

    # -----------------------------------------------------
    # Directive extraction (optional)
    # -----------------------------------------------------

    def _extract_latest_directive(self) -> Optional[Dict[str, Any]]:
        """
        Optional hook: if the engine writes coder_output/* or exposes
        a last directive object, surface it to the host.

        This keeps the operator generic; you can later specialize it
        for your VanirEngine / SimpleCoder wiring.
        """
        # If engine has a 'coder' with a 'last_patch' or similar, use that.
        coder = getattr(self.engine, "coder", None)
        if coder is not None:
            patch = getattr(coder, "last_patch", None)
            if patch is not None:
                # Assume patch has target/value fields or a dict-like interface
                if hasattr(patch, "__dict__"):
                    return patch.__dict__
                return {"patch": patch}

        # Otherwise, no explicit directive surfaced
        return None

    # -----------------------------------------------------
    # Convenience: run loop with external host callback
    # -----------------------------------------------------

    def run(self, host_step_fn: Callable[[int], Dict[str, Any]]) -> None:
        """
        Drive the operator for max_ticks, using a host callback:

        host_step_fn(tick) -> host_snapshot dict

        This lets you wire the operator to ClockworkEngine / lattice
        without changing their internals: the host callback just
        samples whatever state you want to expose each tick.
        """
        while self.current_tick < self.max_ticks:
            snapshot = host_step_fn(self.current_tick)
            payload = self.host_tick(snapshot)

            if payload.get("done"):
                break

            # You can log / inspect payload here, or route it to another system.
            # For now we just continue.
