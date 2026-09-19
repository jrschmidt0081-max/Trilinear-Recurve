// semantic_working_memory.rs

use std::collections::HashMap;

/// Semantic Working Memory (SWM)
/// --------------------------------
/// This organ maintains:
/// - short-term activation
/// - long-term reinforcement
/// - decay over time
/// - episodic memory of recent tokens
///
/// It does NOT decide meaning.
/// It simply tracks *what has been active recently*.
pub struct SemanticWorkingMemory {
    /// Activation values for semantic nodes.
    activation: HashMap<usize, f64>,

    /// Episodic buffer of recent tokens.
    recent_tokens: Vec<usize>,

    /// How many tokens to keep in episodic memory.
    capacity: usize,
}

impl SemanticWorkingMemory {
    pub fn new(capacity: usize) -> Self {
        Self {
            activation: HashMap::new(),
            recent_tokens: Vec::new(),
            capacity,
        }
    }

    /// Record activation of a semantic node.
    pub fn activate(&mut self, node: usize) {
        let entry = self.activation.entry(node).or_insert(0.0);
        *entry += 0.1; // reinforcement

        self.recent_tokens.push(node);

        // Maintain episodic capacity
        if self.recent_tokens.len() > self.capacity {
            self.recent_tokens.remove(0);
        }
    }

    /// Decay all activations slightly.
    pub fn decay(&mut self) {
        for value in self.activation.values_mut() {
            *value *= 0.95;
        }
    }

    /// Get activation level for a node.
    pub fn activation_of(&self, node: usize) -> f64 {
        *self.activation.get(&node).unwrap_or(&0.0)
    }

    /// Return the most recently activated node (if any).
    pub fn last(&self) -> Option<usize> {
        self.recent_tokens.last().copied()
    }

    /// Return the episodic memory buffer.
    pub fn recent(&self) -> &[usize] {
        &self.recent_tokens
    }
}
