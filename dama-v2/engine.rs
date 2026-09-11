use crate::tensor::StateTensor;
use crate::topology::{Manifold, SemanticOperator};
use crate::memory::RingBuffer;
use crate::chronon::Chronon;
use crate::dynamics::{DynamicsState, DynamicsEngine};

#[derive(Debug, Clone, Copy)]
pub struct EngineSnapshot<const N: usize, const M: usize> {
    pub ticks: u64,
    pub tensor_data: [[f64; M]; N],
    pub vertex_positions: [[f64; 3]; 4],
    pub vertex_potentials: [f64; 4],
    pub collapse_tension: f64,
}

#[derive(Debug, Clone)]
pub enum Command {
    Noop,
    Step(Chronon),
    InjectOp(usize, SemanticOperator),
    EvalTokens(Vec<String>),
    Checkpoint,
}

pub struct CommandStream<const CAPACITY: usize> {
    pub queue: [Command; CAPACITY],
    pub head: usize,
    pub tail: usize,
    pub len: usize,
}

impl<const CAPACITY: usize> CommandStream<CAPACITY> {
    pub fn new() -> Self {
        Self {
            queue: std::array::from_fn(|_| Command::Noop),
            head: 0,
            tail: 0,
            len: 0,
        }
    }

    pub fn push(&mut self, cmd: Command) -> bool {
        if self.len < CAPACITY {
            self.queue[self.tail] = cmd;
            self.tail = (self.tail + 1) % CAPACITY;
            self.len += 1;
            true
        } else {
            false
        }
    }

    pub fn pop(&mut self) -> Option<Command> {
        if self.len > 0 {
            let cmd = self.queue[self.head].clone();
            self.head = (self.head + 1) % CAPACITY;
            self.len -= 1;
            Some(cmd)
        } else {
            None
        }
    }
}

pub struct Engine<const N: usize, const M: usize> {
    pub tensor: StateTensor<N, M>,
    pub manifold: Manifold,
    pub history: RingBuffer<[f64; 3], 16>,
    pub dynamics_state: DynamicsState,
    pub dynamics_engine: DynamicsEngine,
    pub ticks: u64,
    pub last_checkpoint: Option<EngineSnapshot<N, M>>,
}

impl<const N: usize, const M: usize> Engine<N, M> {
    pub fn new(tensor: StateTensor<N, M>, manifold: Manifold) -> Self {
        Self {
            tensor,
            manifold,
            history: RingBuffer::new(),
            dynamics_state: DynamicsState::default(),
            dynamics_engine: DynamicsEngine::new(),
            ticks: 0,
            last_checkpoint: None,
        }
    }

    pub fn checkpoint(&mut self) {
        let mut positions = [[0.0; 3]; 4];
        let mut potentials = [0.0; 4];
        
        for i in 0..4 {
            positions[i] = self.manifold.tetra_mesh[i].position;
            potentials[i] = self.manifold.tetra_mesh[i].potential;
        }

        self.last_checkpoint = Some(EngineSnapshot {
            ticks: self.ticks,
            tensor_data: self.tensor.data,
            vertex_positions: positions,
            vertex_potentials: potentials,
            collapse_tension: self.dynamics_state.collapse_tension,
        });
    }

    pub fn restore(&mut self, snapshot: EngineSnapshot<N, M>) {
        self.ticks = snapshot.ticks;
        self.tensor.data = snapshot.tensor_data;
        for i in 0..4 {
            self.manifold.tetra_mesh[i].position = snapshot.vertex_positions[i];
            self.manifold.tetra_mesh[i].potential = snapshot.vertex_potentials[i];
        }
        self.dynamics_state.collapse_tension = snapshot.collapse_tension;
    }

    pub fn tick(&mut self, chronon: Chronon) {
        let dt = chronon.as_scaled_f64();

        if self.history.len > 0 {
            let historical_center = self.history.fold_recurrent(
                [0.0, 0.0, 0.0],
                |mut acc, pos, weight| {
                    acc[0] += pos[0] * weight;
                    acc[1] += pos[1] * weight;
                    acc[2] += pos[2] * weight;
                    acc
                },
            );

            let coupling = (self.dynamics_state.operator_pressure.abs() + 0.01).clamp(0.0, 0.1);
            for vertex in &mut self.manifold.vertices {
                for j in 0..3 {
                    let drift = vertex.position[j] - historical_center[j];
                    vertex.momentum[j] -= drift * coupling;
                }
            }
        }

        if let Some(vertex) = self.manifold.vertices.first() {
            self.history.push(vertex.position);
            let geo = vertex.position;
            // Update global field dynamics each tick based on geometry
            let empty_tokens: Vec<String> = Vec::new();
            self.dynamics_engine.update(&mut self.dynamics_state, &geo, &empty_tokens);
        }

        let tensor_mod = self.tensor.get_pivot(0, 1) + self.dynamics_state.operator_pressure;
        self.manifold.evolve(dt, tensor_mod);

        // TRIDG Recurrence Rule: F(t+1) = F(t) + beta * grad_E(F(t))
        // Bounded by stability thresholds, driven by local collapse tension
        let beta = 0.05; 
        let collapse_tension = self.dynamics_state.collapse_tension;

        self.tensor.transform(|x| {
            // Gradient evaluation derived from state tensor and active collapse tension
            let grad_e = x * (1.0 + collapse_tension);
            x + beta * grad_e
        });

        self.ticks += 1;
    }

    pub fn process_tokens(&mut self, tokens: &[String]) {
        let geo = self.manifold.vertices.first().map(|v| v.position).unwrap_or([0.0; 3]);
        self.dynamics_engine.update(&mut self.dynamics_state, &geo, tokens);
    }

    pub fn execute_command(&mut self, cmd: Command) {
        match cmd {
            Command::Noop => {}
            Command::Step(chronon) => self.tick(chronon),
            Command::InjectOp(idx, op) => self.manifold.inject_operator(idx, op),
            Command::EvalTokens(tokens) => self.process_tokens(&tokens),
            Command::Checkpoint => self.checkpoint(),
        }
    }
}