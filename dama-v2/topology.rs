#[derive(Debug, Clone, Copy)]
pub struct Vertex {
    pub position: [f64; 3],
    pub momentum: [f64; 3],
}

#[derive(Debug, Clone, Copy)]
pub struct Simplex {
    #[allow(dead_code)]
    pub vertex_indices: [usize; 4],
    #[allow(dead_code)]
    pub curvature_tensor: f64,
}

#[derive(Debug, Clone, Copy)]
pub struct MeshVertex {
    pub position: [f64; 3],
    #[allow(dead_code)]
    pub momentum: [f64; 3],
    pub potential: f64,
    pub neighbor_indices: [usize; 3],
    pub neighbor_count: usize,
}

impl MeshVertex {
    pub fn propagate_wave(&mut self, all_vertices: &[MeshVertex; 4], dt: f64, damping: f64) {
        if self.neighbor_count == 0 { return; }
        
        let mut sum_potential = 0.0;
        for i in 0..self.neighbor_count {
            let n_idx = self.neighbor_indices[i];
            sum_potential += all_vertices[n_idx].potential;
        }

        let laplacian = (sum_potential / (self.neighbor_count as f64)) - self.potential;
        
        self.momentum[0] += laplacian * dt * 0.1;
        self.momentum[1] += laplacian * dt * 0.1;
        self.momentum[2] += laplacian * dt * 0.1;

        self.potential += laplacian * dt * damping;
    }
}

#[derive(Debug, Clone, Copy)]
pub enum SemanticOperator {
    Refrak,
    Hinzh,
    Fuzen,
    Plika,
    Rezon,
    Blum,
    Mokra,
    Collapse,
}

pub struct Manifold {
    pub vertices: Vec<Vertex>,
    #[allow(dead_code)]
    pub simplices: Vec<Simplex>,
    pub tetra_mesh: [MeshVertex; 4],
}

impl Manifold {
    pub fn evolve(&mut self, dt: f64, tensor_mod: f64) {
        for vertex in &mut self.vertices {
            vertex.position[0] += vertex.momentum[0] * dt;
            vertex.position[1] += vertex.momentum[1] * dt;
            vertex.position[2] += vertex.momentum[2] * dt;
        }

        let mut updated_mesh = self.tetra_mesh;
        for i in 0..4 {
            let dynamic_damping = 0.1 + (tensor_mod * 0.0001);
            updated_mesh[i].propagate_wave(&self.tetra_mesh, dt, dynamic_damping);
            
            updated_mesh[i].position[0] += updated_mesh[i].momentum[0] * dt;
            updated_mesh[i].position[1] += updated_mesh[i].momentum[1] * dt;
            updated_mesh[i].position[2] += updated_mesh[i].momentum[2] * dt;
        }
        self.tetra_mesh = updated_mesh;
    }

    pub fn inject_operator(&mut self, vertex_idx: usize, op: SemanticOperator) {
        if vertex_idx >= self.tetra_mesh.len() { 
            return; 
        }

        if let SemanticOperator::Hinzh = op {
            let target = &self.tetra_mesh[vertex_idx];
            let v_potential = target.potential;
            let n_indices = target.neighbor_indices;
            
            let mut trace = 0.0;
            for &idx in &n_indices {
                trace += self.tetra_mesh[idx].potential - v_potential;
            }
            
            let v = &mut self.tetra_mesh[vertex_idx];
            if trace > 0.0 {
                v.momentum[0] = -v.momentum[0];
                v.momentum[1] = -v.momentum[1];
            }
            return;
        }
        
        let v = &mut self.tetra_mesh[vertex_idx];

        match op {
            SemanticOperator::Fuzen => {
                v.potential += 0.5;
            }
            SemanticOperator::Plika => {
                v.position[0] *= 1.05;
                v.position[1] *= 1.05;
                v.position[2] *= 1.05;
            }
            SemanticOperator::Refrak => {
                v.momentum[2] += 0.05;
            }
            SemanticOperator::Rezon => {
                v.momentum[0] *= 0.5;
                v.momentum[1] *= 0.5;
                v.momentum[2] *= 0.5;
            }
            SemanticOperator::Blum => {
                v.potential *= 1.2;
            }
            SemanticOperator::Mokra => {
                v.position[0] += 0.01;
            }
            SemanticOperator::Collapse => {
                v.potential = 0.0;
                v.momentum = [0.0; 3];
            }
            SemanticOperator::Hinzh => {}
        }
    }
}