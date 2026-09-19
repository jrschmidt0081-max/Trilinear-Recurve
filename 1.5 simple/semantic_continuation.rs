// semantic_continuation.rs

use crate::dynamics_engine::DynamicsState;

/// Multi-step semantic continuation engine.
/// Determines how the thought trajectory evolves
/// based on dynamics (semantic curvature, drift, collapse tension).
pub fn continue_semantic(
    token: &str,
    dyn_state: &DynamicsState,
    wordbank: &[String],
) -> String {
    let mut cont = token.to_string();

    // === Collapse tension dominates ===
    if dyn_state.collapse_tension > 0.5 {
        return "Collapse".to_string();
    }

    // === Semantic curvature pushes toward strain chain ===
    if dyn_state.semantic_curvature > 0.3 {
        cont = "Collapse".to_string();
    }

    // === Drift pushes toward operator deformation ===
    if dyn_state.drift > 0.2 {
        cont = "Refrak".to_string();
    }

    // === Operator pressure pushes toward active operators ===
    if dyn_state.operator_pressure > 0.3 {
        cont = "Plika".to_string();
    }

    // === Momentum pushes toward manifold expansion ===
    if dyn_state.momentum > 0.4 {
        cont = "Manifold".to_string();
    }

    // === Curvature pushes toward inlay / structural bending ===
    if dyn_state.curvature > 0.3 {
        cont = "Inlay".to_string();
    }

    // === Invariants stabilize toward continuity ===
    if dyn_state.invariants > 0.7 {
        cont = "Continuity".to_string();
    }

    // Fallback if token not found in wordbank
    if !wordbank.contains(&cont) {
        return token.to_string();
    }

    cont
}
