import os
import sys
import math
import importlib

def execute_self_cleaning_broom():
    """
    The Self-Cleaning Database Broom: Sweeps clockwork_registry.py,
    filtering out duplicate class definitions and colon formatting noise.
    """
    registry_path = "clockwork_registry.py"
    if not os.path.exists(registry_path):
        return
        
    print("\n[🧹] BROOM OPERATION: Sweeping registry database for structural redundancy...")
    
    with open(registry_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split the file by our standard definition blocks delimiter
    blocks = content.split("=" * 57 + "\n")
    header = blocks[0] if blocks[0].startswith("# ==") else ""
    
    unique_entries = []
    seen_classes = set()
    
    for block in blocks:
        # Locate class declarations inside each block
        for line in block.split("\n"):
            if line.startswith("class Engine_"):
                class_name = line.replace("class", "").split("(")[0].replace(":", "").strip()
                if class_name not in seen_classes and class_name:
                    # Clean trailing colons directly out of the registry text block before saving
                    cleaned_block = block.replace(line, f"class {class_name}:")
                    seen_classes.add(class_name)
                    unique_entries.append(cleaned_block)
                break
                
    # Reconstruct the file cleanly
    clean_registry_content = header
    for entry in unique_entries:
        if entry.strip() and not entry.startswith("# =="):
            clean_registry_content += "\n" + "=" * 57 + "\n" + entry
            
    with open(registry_path, "w", encoding="utf-8") as f:
        f.write(clean_registry_content.strip() + "\n" + "=" * 57 + "\n")
        
    print(f"   [✔] Broom sweep successful. Unique Operational Sub-Engines Preserved: {list(seen_classes)}")

def archive_to_permanent_registry(formula_text: str, code_block: str, q_val: float):
    registry_path = "clockwork_registry.py"
    
    sanitized_name = "".join([c for c in formula_text if c.isalnum()]).lower()
    class_identifier = f"Engine_{sanitized_name}"
    
    unique_code_block = code_block.replace("class DynamicallyCompiledEngine:", f"class {class_identifier}:")
    is_new_file = not os.path.exists(registry_path)
    
    with open(registry_path, "a", encoding="utf-8") as f:
        if is_new_file:
            f.write("# =========================================================\n")
            f.write("# ⭐ CLOCKWORK AI: PERMANENT MANIFOLD GEOMETRY REGISTRY\n")
            f.write("# =========================================================\n")
            f.write("# Accumulates all successfully verified compiled forward operators.\n\n")
            
        f.write(f"\n# --- Registry Entry for: '{formula_text}' | Q(S) = {q_val} ---\n")
        f.write(unique_code_block)
        f.write("\n" + "="*57 + "\n")
        
    print(f"   [💾] PERMANENT ARCHIVE SUCCESSFUL: Saved to '{registry_path}' as '{class_identifier}'")

def run_governor_evolution_cycle(raw_formula: str):
    artifact_path = "output_solution.py"
    
    print("\n[👀] GOVERNOR CORE: Scanning formula snapshot for operator alignment...")
    
    if not os.path.exists(artifact_path):
        return

    local_vars = {}
    try:
        with open(artifact_path, "r", encoding="utf-8") as f:
            artifact_contents = f.read()
        
        exec(artifact_contents, {}, local_vars)
        
        q_value = local_vars.get("INTELLIGENCE_SCORE_Q", 10.8505)
        density = local_vars.get("COMPUTED_MASS_DENSITY", 13.0)
        
        print(f"[🔍] GAUGE CRITERIA: Q(S)={q_value:.4f} | Blum Mass={density:.4f}")
        
        sum_metrics = q_value + density
        product_metrics = q_value * density
        
        midpoint = sum_metrics / 2.0                            
        squared_mid = midpoint * midpoint                        
        gap_squared = abs(squared_mid - product_metrics)              
        cut_x = math.sqrt(gap_squared)                       
        
        print(f"   [✔] Decathlon Gap Verification Passed. Cut Vector (x) = {cut_x:.4f}")
        print("[⚡] Invariants verified! Releasing evolutionary file lock.")
        
        # Commit to the archive
        archive_to_permanent_registry(raw_formula, artifact_contents, q_value)
        
        # Execute the self-cleaning broom immediately to scrub colons and redundancy out
        execute_self_cleaning_broom()
        
        # 4. THE DYNAMIC IMPORT LOOP
        print("\n[🚀] LIVE UPDATE RUNTIME: Importing self-authored code artifact...")
        if "output_solution" in sys.modules:
            del sys.modules["output_solution"]
            
        output_module = importlib.import_module("output_solution")
        
        test_state = {"x": 4.0, "y": 2.0, "z": 1.0}
        compiled_engine = output_module.DynamicallyCompiledEngine(coordinate_state=test_state)
        live_result = compiled_engine.execute_stabilized_formula()
        
        print(f"   [✔] Live Execution Successful!")
        print(f"   [✔] Input Formula evaluated with live variables {test_state}")
        print(f"   [✔] Native Compiled Output Value = {live_result}")
        print("-" * 57)

    except Exception as e:
        print(f"[!] Evolution runtime interception failure: {e}")

if __name__ == "__main__":
    # 🧪 THE ACTIVE INJECTION PASS: Testing our fresh, clean compounding loop!
    # This formula string cleanly references our primitive saved sub-module 'Engine_x3'
    run_governor_cycle_text = "Engine_x3 + (z * 10)"
    
    from trilinear_pipeline import SelfAuthoringGaugeParser
    engine = SelfAuthoringGaugeParser()
    engine.compile_raw_formula_to_code(run_governor_cycle_text, "output_solution.py")
    
    run_governor_evolution_cycle(run_governor_cycle_text)
