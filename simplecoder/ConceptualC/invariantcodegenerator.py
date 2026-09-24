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

        if "gemini_lensing_invariant" in self.metrics:
            code_lines.extend([
                "def project_gemini_lens(psi_vector: np.ndarray, q_denom: int = 137) -> np.ndarray:",
                "    \"\"\"Inferred from: L_λ(Ψ) = P_Q(Ψ | 137) ⇔ Tr(J_L) = 0\"\"\"",
                "    \"\"\"Projects continuous semantic weights onto a rational Q-lattice.\"\"\"",
                "    quantized = np.round(psi_vector * q_denom) / q_denom",
                "    # Enforce trace boundary condition (volume preservation)",
                "    if hasattr(quantized, 'shape') and len(quantized.shape) > 1:",
                "        trace_val = np.trace(quantized)",
                "        if abs(trace_val) > 1e-12:",
                "            quantized -= (trace_val / quantized.shape[0]) * np.eye(quantized.shape[0])",
                "    return quantized",
                ""
            ])
        
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
                "        if callable(invariant):",
                "            res = invariant(expression)",
                "            if isinstance(res, bool) and not res:",
                "                return False",
                "    return True",
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
            
            # Explicitly append the Gemini Lenser tracking flag
            has_lenser = "gemini_lensing_invariant" in self.metrics
            code_lines.append(f"        self.omega6_lenser_active = {has_lenser}")
            
            code_lines.append("        pass")
            code_lines.append("")


        return "\n".join(code_lines)

if __name__ == "__main__":
    import json
    import os

    # 1. Load the active metrics.json schema
    metrics_path = "metrics.json"
    if os.path.exists(metrics_path):
        with open(metrics_path, "r") as f:
            active_metrics = json.load(f)
            
        # 2. Initialize the generator and assemble the string matrix
        generator = InvariantCodeGenerator(active_metrics)
        generated_code = generator.generate_python_module()
        
        # 3. Materialize the solid core directly to disk
        output_path = "generated_structures.py"
        # ADD encoding="utf-8" RIGHT HERE:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(generated_code)

            
        print(f"Success: [F0 Substrate Restored]. Materialized {output_path} with active invariants.")
    else:
        print("Error: metrics.json not found in the local workspace directory.")
