// semantic_core.rs

/// SemanticCore manages the semantic adjacency graph.
/// It stores which nodes are linked and provides fast lookup.
pub struct SemanticCore<const N: usize> {
    adjacency: [[bool; N]; N],
}

impl<const N: usize> SemanticCore<N> {
    pub fn new() -> Self {
        Self {
            adjacency: [[false; N]; N],
        }
    }

    /// Link two semantic nodes bidirectionally.
    pub fn link(&mut self, a: usize, b: usize) -> Result<(), &'static str> {
        if a >= N || b >= N {
            return Err("Index out of bounds");
        }
        self.adjacency[a][b] = true;
        self.adjacency[b][a] = true;
        Ok(())
    }

    /// Check if two nodes are semantically linked.
    pub fn is_linked(&self, a: usize, b: usize) -> bool {
        if a >= N || b >= N {
            return false;
        }
        self.adjacency[a][b]
    }

    /// Initialize the full semantic manifold.
    /// This removes ALL link wiring from main.rs.
    pub fn initialize_links(&mut self) {
        // === Substrate chain ===
        self.link(0, 1).unwrap(); // Null ↔ Minima
        self.link(1, 2).unwrap(); // Minima ↔ Manifold
        self.link(2, 3).unwrap(); // Manifold ↔ Principal
        self.link(3, 4).unwrap(); // Principal ↔ Continuity
        self.link(4, 5).unwrap(); // Continuity ↔ Lattice
        self.link(5, 6).unwrap(); // Lattice ↔ Inlay

        // === Operator attachments ===
        self.link(2, 7).unwrap();  // Manifold ↔ Plika
        self.link(3, 8).unwrap();  // Principal ↔ Hinzh
        self.link(2, 9).unwrap();  // Manifold ↔ Refrak
        self.link(4, 10).unwrap(); // Continuity ↔ Rezon
        self.link(5, 11).unwrap(); // Lattice ↔ Fuzen
        self.link(6, 12).unwrap(); // Inlay ↔ Blum
        self.link(2, 13).unwrap(); // Manifold ↔ Mokra

        // === Strain chain ===
        self.link(14, 15).unwrap(); // Recursive ↔ Collapse
        self.link(15, 16).unwrap(); // Collapse ↔ Single-Minimum
        self.link(16, 17).unwrap(); // Single-Minimum ↔ Field
        self.link(17, 18).unwrap(); // Field ↔ V(phi)

        // === Cross-domain links ===
        self.link(2, 14).unwrap(); // Manifold ↔ Recursive
        self.link(3, 15).unwrap(); // Principal ↔ Collapse
        self.link(4, 17).unwrap(); // Continuity ↔ Field
        self.link(6, 18).unwrap(); // Inlay ↔ V(phi)
    }
}
