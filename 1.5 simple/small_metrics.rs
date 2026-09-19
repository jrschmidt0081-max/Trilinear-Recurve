// small_metrics.rs

use std::time::{Instant};

/// CoreMetrics tracks the engine's physiological state:
/// - gradient norms
/// - spectral stress
/// - hinge events
/// - loss value
/// - tick counter
/// - uptime
pub struct CoreMetrics {
    pub avg_grad_norm: f64,
    pub max_grad_norm: f64,
    pub grad_steps: u64,

    pub spectral_stress: f64,
    pub hinge_events: u64,

    pub loss_value: f64,

    pub tick_count: u64,
    start_time: Instant,
}

impl CoreMetrics {
    pub fn new() -> Self {
        Self {
            avg_grad_norm: 0.0,
            max_grad_norm: 0.0,
            grad_steps: 0,

            spectral_stress: 0.0,
            hinge_events: 0,

            loss_value: 0.0,

            tick_count: 0,
            start_time: Instant::now(),
        }
    }

    /// Called once per engine tick.
    pub fn tick(&mut self) {
        self.tick_count += 1;
    }

    /// Record a gradient step.
    pub fn record_gradient_step(&mut self, grad: f64, steps: f64) {
        self.grad_steps += 1;

        self.avg_grad_norm = 
            (self.avg_grad_norm * 0.9) + (grad * 0.1);

        if grad > self.max_grad_norm {
            self.max_grad_norm = grad;
        }

        // Loss increases slightly with steps
        self.loss_value += steps * 0.001;
    }

    /// Add spectral stress.
    pub fn add_spectral_stress(&mut self, amount: f64) {
        self.spectral_stress += amount;

        // Clamp to avoid runaway stress
        if self.spectral_stress < -1.0 {
            self.spectral_stress = -1.0;
        }
        if self.spectral_stress > 2.0 {
            self.spectral_stress = 2.0;
        }
    }

    /// Record a hinge event (semantic violation).
    pub fn record_hinge_event(&mut self) {
        self.hinge_events += 1;
        self.spectral_stress += 0.05;
        self.loss_value += 0.1;
    }

    /// Engine uptime.
    pub fn uptime(&self) -> std::time::Duration {
        self.start_time.elapsed()
    }
}
