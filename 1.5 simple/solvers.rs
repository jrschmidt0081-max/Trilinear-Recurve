pub struct CollatzSolver;

impl CollatzSolver {
    pub fn new() -> Self {
        Self
    }

    /// Analyzes Collatz trajectory and returns (steps, peak, Lyapunov proxy lambda_l, is_trapped)
    pub fn analyze_trajectory(&self, mut n: u64) -> (u32, u64, f64, bool) {
        let mut steps = 0;
        let mut peak = n;
        let original = n;

        while n > 1 && steps < 1000 {
            if n > peak {
                peak = n;
            }
            if n % 2 == 0 {
                n /= 2;
            } else {
                n = n * 3 + 1;
            }
            steps += 1;
        }

        let trapped = n == 1;
        // Lyapunov proxy based on contraction/expansion ratio
        let ratio = (n as f64 + 1.0) / (original as f64 + 1.0);
        let lambda_l = ratio.ln();

        (steps, peak, lambda_l, trapped)
    }
}

pub struct ErdosStrausSolver;

impl ErdosStrausSolver {
    pub fn new() -> Self {
        Self
    }

    /// Solves 4/n = 1/x + 1/y + 1/z for a given n, returning the first valid triple (x, y, z)
    pub fn solve(&self, n: u64) -> Option<(u64, u64, u64)> {
        if n == 0 {
            return None;
        }
        let limit = (4 * n) + 1; // Removed unused n_f variable

        for x in 1..limit {
            for y in x..limit {
                let numerator = 4 * x * y;
                let denominator = n * (x + y);
                if numerator > denominator {
                    let rem = (x * y * n) % (numerator - denominator);
                    if rem == 0 {
                        let z = (x * y * n) / (numerator - denominator);
                        return Some((x, y, z));
                    }
                }
            }
        }
        None
    }
}