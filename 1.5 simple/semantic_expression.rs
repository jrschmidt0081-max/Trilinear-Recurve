// semantic_expression.rs

use crate::dynamics_engine::DynamicsState;

pub struct SemanticExpressionLayer;

impl SemanticExpressionLayer {
    pub fn express(node: usize) -> String {
        match node {
            // === Substrates ===
            0 => "The system enters a null-state baseline.".to_string(),
            1 => "A minima forms, stabilizing the substrate.".to_string(),
            2 => "The manifold expands into a higher-order structure.".to_string(),
            3 => "A principal seam emerges, guiding the transition.".to_string(),
            4 => "Continuity asserts itself, smoothing the manifold.".to_string(),
            5 => "Lattice geometry begins to crystallize.".to_string(),
            6 => "Inlay curvature develops, embedding new structure.".to_string(),

            // === Operators ===
            7 => "Plika folds the manifold, introducing a trilinear deformation.".to_string(),
            8 => "Hinzh flips a branch, altering the principal seam.".to_string(),
            9 => "Refrak bends the manifold, refracting continuity.".to_string(),
            10 => "Rezon locks the phase, stabilizing oscillatory behavior.".to_string(),
            11 => "Fuzen fuses mass into the lattice, increasing density.".to_string(),
            12 => "Blum blooms curvature outward, expanding the inlay.".to_string(),
            13 => "Mokra matches phase alignment across manifold boundaries.".to_string(),

            // === Strain chain ===
            14 => "Recursive strain begins looping through the manifold.".to_string(),
            15 => "Collapse initiates, reducing dimensional freedom.".to_string(),
            16 => "A single-minimum state forms, collapsing the manifold.".to_string(),
            17 => "Field dynamics activate, propagating influence outward.".to_string(),
            18 => "V(phi) curvature emerges, altering the field potential.".to_string(),

            _ => "Undefined semantic state.".to_string(),
        }
    }

    pub fn express_with_dynamics(node: usize, dyn_state: &DynamicsState) -> String {
        let base = Self::express(node);

        // === Collapse tension ===
        if dyn_state.collapse_tension > 0.5 {
            return format!("{base} Collapse tension threatens structural integrity.");
        }

        // === Operator pressure ===
        if dyn_state.operator_pressure > 0.3 {
            return format!("{base} Operator pressure reshapes the manifold.");
        }

        // === Semantic curvature ===
        if dyn_state.semantic_curvature > 0.4 {
            return format!("{base} Semantic curvature intensifies across the structure.");
        }

        // === Momentum ===
        if dyn_state.momentum > 0.3 {
            return format!("{base} Momentum surges through the manifold.");
        }

        // === Curvature ===
        if dyn_state.curvature > 0.2 {
            return format!("{base} Curvature deepens, reshaping the structural frame.");
        }

        // === Drift ===
        if dyn_state.drift > 0.1 {
            return format!("{base} A subtle drift destabilizes the transition path.");
        }

        // === Invariants ===
        if dyn_state.invariants > 0.7 {
            return format!("{base} Structural invariants hold firm, reinforcing stability.");
        }

        base
    }

    pub fn express_transition(a: usize, b: usize) -> String {
        format!(
            "{} Next, {}",
            Self::express(a),
            Self::express(b).to_lowercase()
        )
    }
}
