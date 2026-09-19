import math

class InvariantCodeGenerator:
    def __init__(self, graph):
        self.graph = graph

    def _build_scope(self, engine):
        """Builds execution scope containing globals, math, and live engine variables."""
        scope = {
            "engine": engine,
            "math": math,
            "framing": getattr(engine, "framing", {})
        }
        # Inject live engine attributes into scope so formulas can read 'phi' or 'engine.phi'
        scope.update(engine.__dict__)
        return scope

    def generate_invariant_functions(self):
        invariants = {}

        for name, spec in self.graph.get("invariants", {}).items():
            # Special Invariants
            if name == "identity_continuity":
                def fn(engine):
                    if getattr(engine, "baseline_identity", None) is None:
                        engine.baseline_identity = engine.compute_state_signature()
                        return 1.0
                    
                    baseline = engine.baseline_identity
                    curr = engine.compute_state_signature()

                    delta = sum(abs(curr.get(k, 0.0) - baseline.get(k, 0.0)) for k in ["entropy", "phi", "theta", "nu", "omega"])
                    return math.exp(-delta)
                invariants[name] = fn
                continue

            if name == "continuity_phase":
                def fn(engine):
                    C = getattr(engine, "identity_continuity", 1.0)
                    if C > 0.90: return "growth"
                    elif C >= 0.50: return "mutation"
                    else: return "collapse"
                invariants[name] = fn
                continue

            if name == "continuity_velocity":
                def fn(engine):
                    C = getattr(engine, "identity_continuity", 1.0)
                    prev = getattr(engine, "previous_continuity", 1.0)
                    engine.previous_continuity = C
                    return C - prev
                invariants[name] = fn
                continue

            if name == "continuity_acceleration":
                def fn(engine):
                    v = getattr(engine, "continuity_velocity", 0.0)
                    prev_v = getattr(engine, "previous_continuity_velocity", 0.0)
                    engine.previous_continuity_velocity = v
                    return v - prev_v
                invariants[name] = fn
                continue

            if name == "continuity_backfeed":
                def fn(engine):
                    v = getattr(engine, "continuity_velocity", 0.0)
                    a = getattr(engine, "continuity_acceleration", 0.0)
                    phase = getattr(engine, "continuity_phase", "growth")
                    
                    B = 0.1 * v + 0.05 * a
                    if phase == "growth": B += 0.02
                    elif phase == "collapse": B -= 0.03
                    return B
                invariants[name] = fn
                continue

            if name == "structure_backfeed":
                def fn(engine):
                    structures = engine.graph.get("structures", [])
                    if not structures: return 0.0
                    avg_stability = sum(s.get("stability", 0.5) for s in structures) / len(structures)
                    return 0.02 * len(structures) + 0.1 * (avg_stability - 0.5)
                invariants[name] = fn
                continue

            # Default Invariant
            formula = spec.get("formula", "") if isinstance(spec, dict) else str(spec)
            def fn(engine, f=formula):
                scope = self._build_scope(engine)
                return eval(f, scope, scope)
            invariants[name] = fn

        return invariants

    def generate_operator_functions(self):
        operators = []

        for name, spec in self.graph.get("operators", {}).items():
            # Special Operators
            if name == "emergent_scheduler":
                def op(engine):
                    phase = getattr(engine, "continuity_phase", "growth")
                    mapping = {"growth": "expand", "mutation": "compress", "collapse": "prune"}
                    engine.scheduler_action = mapping.get(phase, None)
                operators.append(op)
                continue

            if name == "identity_stabilizer":
                def op(engine):
                    C = getattr(engine, "identity_continuity", 1.0)
                    engine.nu = getattr(engine, "nu", 0.05) * C
                    engine.omega = getattr(engine, "omega", 0.02) * C
                operators.append(op)
                continue

            if name == "apply_continuity_backfeed":
                def op(engine):
                    B = getattr(engine, "continuity_backfeed", 0.0)
                    C = getattr(engine, "identity_continuity", 1.0)
                    engine.identity_continuity = max(0.0, min(1.0, C + B))
                operators.append(op)
                continue

            if name == "apply_structure_backfeed":
                def op(engine):
                    B_s = getattr(engine, "structure_backfeed", 0.0)
                    C = getattr(engine, "identity_continuity", 1.0)
                    engine.identity_continuity = max(0.0, min(1.0, C + B_s))
                operators.append(op)
                continue

            if name == "collapse_continuity":
                def op(engine):
                    # Only apply collapse degradation during low-continuity phase
                    if getattr(engine, "continuity_phase", "growth") == "collapse":
                        engine.identity_continuity *= 0.95
                operators.append(op)
                continue

            # Default Operator (with variable write-back to engine)
            formula = spec.get("formula", "") if isinstance(spec, dict) else str(spec)
            def op(engine, f=formula):
                scope = self._build_scope(engine)
                if isinstance(f, list):
                    f = "\n".join(f)
                exec(f, scope)
                
                # Write updated variables back to the engine instance
                for key, val in scope.items():
                    if key not in ["engine", "math", "framing"] and hasattr(engine, key):
                        setattr(engine, key, val)
                        
            operators.append(op)

        return operators