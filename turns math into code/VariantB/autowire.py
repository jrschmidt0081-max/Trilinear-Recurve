import json
import random

def autowire_step(engine):
    """Grow new invariant formulas and structural rules safely."""
    if not getattr(engine, "autowire_enabled", True):
        return

    graph = engine.graph
    rules = graph.setdefault("autowire_rules", [])
    operators_changed = False

    # --- 1. Generate new formula rule if space allows ---
    if len(rules) < getattr(engine, "autowire_max_rules", 50):
        growth_rate = getattr(engine, "autowire_growth_rate", 0.05)
        new_formula = f"engine.entropy + {random.uniform(0, growth_rate):.4f}"
        if new_formula not in rules:
            rules.append(new_formula)

    # --- 2. Process structured emergent rules ---
    # Iterate over a snapshot list so modifications during iteration don't cause skip bugs
    for rule in list(rules):
        
        # emergent_mid → mutated_drift
        if isinstance(rule, dict) and rule.get("trigger") == "emergent_mid":
            graph.setdefault("operators", {})["mutated_drift"] = {
                "formula": "engine.nu += 0.005\nengine.omega += 0.005"
            }
            rules.remove(rule)
            operators_changed = True

        # continuity_mutation → mutated_operator
        elif isinstance(rule, dict) and rule.get("trigger") == "continuity_mutation":
            graph.setdefault("operators", {})["mutated_operator"] = {
                "formula": "engine.nu += 0.005\nengine.omega += 0.005"
            }
            rules.remove(rule)
            operators_changed = True

        # prune_autowire → safely remove oldest rule
        elif rule == "prune_autowire":
            rules.remove(rule)
            if rules:
                rules.pop(0)  # Prune the actual oldest rule safely

    # --- 3. Dynamic Re-compilation ---
    # Recompile dynamic operators into live engine code if new ones were dynamically injected
    if operators_changed and hasattr(engine, "build_runtime"):
        engine.build_runtime()

    # --- 4. Persist updated graph (Only on structural mutation or interval checkpoints) ---
    if operators_changed or (engine.tick % 50 == 0):
        try:
            with open("operator_graph.json", "w", encoding="utf-8") as f:
                json.dump(graph, f, indent=2)
        except Exception as err:
            pass # Prevent disk access issues from breaking tick pipeline