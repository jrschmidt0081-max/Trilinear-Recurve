// dynamics_engine.rs

use crate::small_metrics::CoreMetrics;

/// Full dynamics state for manifold evolution.
#[derive(Default)]
pub struct DynamicsState {
    pub value: f64,
    pub momentum: f64,
    pub curvature: f64,
    pub drift: f64,
    pub invariants: f64,

    // Extended organs
    pub semantic_curvature: f64,
    pub operator_pressure: f64,
    pub collapse_tension: f64,
}

/// Dynamics Engine — evolves the manifold state based on:
/// - metrics (stress, hinge events, gradients)
/// - geometry (Chronon-driven coordinates)
/// - semantic operators (pressure, curvature, collapse)
pub struct DynamicsEngine;

impl DynamicsEngine {
    pub fn new() -> Self {
        Self
    }
    
    /// Main update function — called once per tick.
    pub fn update(
        &self,
        state: &mut DynamicsState,
        metrics: &CoreMetrics,
        geo: &[f64; 3],
        tokens: &[String],
    ) {
        // === Momentum ===
        state.momentum += metrics.avg_grad_norm * 0.1;
        state.momentum += (geo[0].abs() + geo[1].abs() + geo[2].abs()) * 0.05;

        // === Curvature ===
        state.curvature += metrics.spectral_stress * 0.05;
        state.curvature += (geo[0] * geo[1] * geo[2]) * 0.01;

        // === Semantic Curvature ===
        state.semantic_curvature += metrics.hinge_events as f64 * 0.03;

        // === Drift ===
        state.drift += metrics.hinge_events as f64 * 0.02;

        // Drift correction via invariants
        state.drift -= state.invariants * 0.01;

        // === Collapse Tension ===
        if metrics.spectral_stress > 0.4 {
            state.collapse_tension += 0.05;
        } else {
            state.collapse_tension *= 0.9;
        }

        // === Invariants ===
        if metrics.spectral_stress < 0.1 {
            state.invariants += 0.03;
        } else {
            state.invariants -= 0.02;
        }

        // Clamp invariants to [0, 1]
        state.invariants = state.invariants.clamp(0.0, 1.0);

        // === Operator-driven dynamics ===
        for token in tokens {
            match token.as_str() {
                "Refrak" => {
                    state.curvature += 0.05;
                    state.semantic_curvature += 0.04;
                    state.operator_pressure += 0.03;
                }
                "Hinzh" => {
                    state.drift += 0.04;
                    state.operator_pressure += 0.05;
                }
                "Rezon" => {
                    state.invariants += 0.03;
                    state.semantic_curvature -= 0.02;
                }
                "Plika" => {
                    state.momentum += 0.02;
                    state.operator_pressure += 0.02;
                }
                "Fuzen" => {
                    state.momentum += 0.08;
                    state.collapse_tension += 0.04;
                }
                "Blum" => {
                    state.curvature += 0.06;
                    state.semantic_curvature += 0.05;
                }
                "Mokra" => {
                    state.invariants += 0.02;
                    state.semantic_curvature -= 0.03;
                }
                "Recursive" => {
                    state.semantic_curvature += 0.08;
                }
                "Collapse" => {
                    state.collapse_tension += 0.10;
                }
                "Field" => {
                    state.operator_pressure += 0.04;
                }
                "Vphi" => {
                    state.curvature += 0.03;
                }
                _ => {}
            }
        }

        // === Decay ===
        state.operator_pressure *= 0.95;
        state.semantic_curvature *= 0.97;

        // === Clamp collapse tension ===
        state.collapse_tension = state.collapse_tension.clamp(0.0, 1.0);
    }
}
