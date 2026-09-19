use std::time::Instant;

/// Configuration for the TriadLanguageEngine.
#[derive(Clone, Copy, Debug)]
pub struct EngineConfig {
    pub max_steps: usize,
}

impl Default for EngineConfig {
    fn default() -> Self {
        Self { max_steps: 100 }
    }
}

/// The TriadLanguageEngine processes a sequence of tokens
/// and produces a decoded semantic token + step count + loop time.
pub struct TriadLanguageEngine {
    config: EngineConfig,
}

impl TriadLanguageEngine {
    pub fn new(config: EngineConfig) -> Self {
        Self { config }
    }

    /// Process a sequence of tokens using the internal config bound:
    /// - decoded token (String)
    /// - loop time in ms (f64)
    /// - number of steps executed (usize)
    pub fn process_context(
        &mut self,
        tokens: &[String],
    ) -> (String, f64, usize) {
        let start = Instant::now();

        // Basic decode: last token wins
        let decoded = if tokens.is_empty() {
            "Null".to_string()
        } else {
            tokens.last().unwrap().clone()
        };

        // Step count is bounded by tokens and the config's max_steps limit
        let steps = std::cmp::min(tokens.len() * 5, self.config.max_steps);

        let elapsed = start.elapsed().as_secs_f64() * 1000.0;

        (decoded, elapsed, steps)
    }
}