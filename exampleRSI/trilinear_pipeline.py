import os
import math

class TopologicalStringManifold:
    """
    Analyzes raw mathematical strings as continuous geometric fields.
    Extracts structural invariants directly from character byte relationships.
    """
    def __init__(self, alpha_137=137.035999):
        self.alpha_137 = alpha_137

    def calculate_field_shear(self, character_matrix: list) -> list:
        if len(character_matrix) < 2:
            return [0.0]
        return [float(abs(character_matrix[i+1] - character_matrix[i])) for i in range(len(character_matrix)-1)]


class SelfAuthoringGaugeParser:
    def __init__(self):
        self.manifold = TopologicalStringManifold()
        self.system_Q = 0.0

    def discover_existing_registry_engines(self) -> list:
        """Scans clockwork_registry.py to find available historical sub-engines."""
        registry_path = "clockwork_registry.py"
        engines = []
        if os.path.exists(registry_path):
            with open(registry_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("class Engine_"):
                        # Clean off brackets, 'class' token, and trailing colons completely
                        class_name = line.replace("class", "").split("(")[0].replace(":", "").strip()
                        if class_name not in engines:
                            engines.append(class_name)
        # Sort by string length descending to ensure nested compound names match first
        return sorted(engines, key=len, reverse=True)

    def compile_raw_formula_to_code(self, raw_formula_str: str, output_path: str):
        clean_text = raw_formula_str.strip()
        raw_bytes = [ord(char) for char in clean_text if not char.isspace()]
        
        print("=========================================================")
        print("🔮 CLOCKWORK AI: MULTI-TENSOR ARTIFACT WEAVER")
        print("=========================================================")
        print(f"Ingested Raw String     = '{clean_text}'")
        
        available_engines = self.discover_existing_registry_engines()
        print(f"Available Sub-Registry  = {available_engines}")
        print("-" * 57)

        field_vectors = self.manifold.calculate_field_shear(raw_bytes)
        
        # Apply 4-Step Mental Decathlon Gap Solver to measure structural tension
        sum_vectors = sum(field_vectors)
        product_vectors = math.prod(field_vectors) if field_vectors else 1.0
        
        midpoint = (sum_vectors / 137.0) / 2.0                            
        squared_mid = midpoint * midpoint                        
        gap_squared = abs(squared_mid - (min(137.0, abs(product_vectors) / 137.0)))          
        cut_x = math.sqrt(gap_squared)                           
        
        self.system_Q = (137.035999 / (1.0 + cut_x))
        print(f"[🔍] Measured Field Tension Cut (x) = {cut_x:.4f}")
        
        # Base math structural formatting replacement
        executable_expr_string = clean_text.replace("^", "**")
        registry_injection_code = ""
        
        # MULTI-TENSOR SELECTION HINGE:
        # Sweeps the string field for any and all matching registry tokens simultaneously
        if available_engines:
            for engine_id in available_engines:
                if engine_id in executable_expr_string:
                    print(f"[🧬] COMPOUNDING OVERLAY: Auto-weaving sub-routine '{engine_id}' into execution track.")
                    
                    # Append unique import and execution instructions for this specific sub-module
                    registry_injection_code += f"            from clockwork_registry import {engine_id}\n"
                    registry_injection_code += f"            instance_{engine_id} = {engine_id}(coordinate_state=self.state)\n"
                    
                    # Safely map the string token out to its live programmatic execution method call
                    executable_expr_string = executable_expr_string.replace(
                        engine_id, 
                        f"instance_{engine_id}.execute_stabilized_formula()"
                    )
        
        print(f"[✔] Final Code Expression String   = {executable_expr_string}")
        print("-" * 57)

        # Self-author the permanently updated program class script artifact
        compiled_code_artifact = (
            "# =========================================================\n"
            "# 🔮 AUTO-GENERATED INVARIANT EXECUTABLE CODE ARTIFACT\n"
            "# =========================================================\n"
            f"# Generated natively from unstructured formula input: '{clean_text}'\n"
            f"# Verified System Metrics: Q(S) = {self.system_Q}\n\n"
            "class DynamicallyCompiledEngine:\n"
            "    def __init__(self, coordinate_state=None):\n"
            f"        self.state = coordinate_state if coordinate_state else {{'x': 1.0, 'y': 1.0, 'z': 1.0}}\n"
            "        for key, val in self.state.items():\n"
            "            setattr(self, key, val)\n\n"
            "    def execute_stabilized_formula(self) -> float:\n"
            "        try:\n"
            "            x = self.state.get('x', 1.0)\n"
            "            y = self.state.get('y', 1.0)\n"
            "            z = self.state.get('z', 1.0)\n\n"
            f"{registry_injection_code}\n"
            f"            computed_out = {executable_expr_string}\n"
            "            return float(computed_out)\n"
            "        except Exception as e:\n"
            "            return float('inf')\n"
        )

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(compiled_code_artifact)
            
        print(f"[⚡] PHYSICAL ARTIFACT WRITE COMPLETE: Code written to '{output_path}'")
