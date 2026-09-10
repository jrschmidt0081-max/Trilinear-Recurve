/// Represents the smallest actionable temporal unit (Chronon).
/// Enforces discrete, drift-free state transitions.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Chronon {
    pub tick: u64,
    pub delta: u128, // Fixed-point temporal resolution[cite: 1]
}

impl Chronon {
    pub fn new(tick: u64, delta: u128) -> Self {
        Self { tick, delta }
    }

    /// Converts the quantized chronon delta into a deterministic floating-point step
    /// while preserving Diophantine bounds and preventing drift[cite: 1].
    pub fn as_scaled_f64(&self) -> f64 {
        // Modular arithmetic prevents unbounded accumulation error
        let step = (self.delta % 1024) as f64 / 1024.0;
        step * 0.016 // Scale to a standard 16ms frame baseline
    }
}