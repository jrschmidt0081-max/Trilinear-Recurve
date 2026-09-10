mod tensor;
mod topology;
mod engine;
mod memory;
mod chronon;
mod dynamics;
mod lexiconcompiler;

use tensor::StateTensor;
use topology::{Manifold, Vertex, Simplex, MeshVertex};
use engine::{Engine, CommandStream};
use lexiconcompiler::LexiconCompiler;

fn main() {
    let tensor: StateTensor<3, 3> = StateTensor::new();

    let manifold = Manifold {
        vertices: vec![Vertex {
            position: [1.0, 0.0, 0.0],
            momentum: [0.0, 0.1, 0.0],
        }],
        simplices: vec![Simplex {
            vertex_indices: [0, 0, 0, 0],
            curvature_tensor: 0.2,
        }],
        tetra_mesh: [
            MeshVertex { position: [0.0, 0.0, 0.0], momentum: [0.0; 3], potential: 1.0, neighbor_indices: [1, 2, 3], neighbor_count: 3 },
            MeshVertex { position: [1.0, 0.0, 0.0], momentum: [0.0; 3], potential: 0.5, neighbor_indices: [0, 2, 3], neighbor_count: 3 },
            MeshVertex { position: [0.0, 1.0, 0.0], momentum: [0.0; 3], potential: 0.0, neighbor_indices: [0, 1, 3], neighbor_count: 3 },
            MeshVertex { position: [0.0, 0.0, 1.0], momentum: [0.0; 3], potential: 0.0, neighbor_indices: [0, 1, 2], neighbor_count: 3 },
        ],
    };

    let mut dama_core = Engine::new(tensor, manifold);

    // Rich lexicon sentence driving both macro field dynamics and local execution
    let script_input = "field v(phi) recursive refrak step hinzh fuzen plika checkpoint rezon blum mokra collapse step step";
    let compiled_commands = LexiconCompiler::compile_text(script_input);

    let mut script: CommandStream<32> = CommandStream::new();
    for cmd in compiled_commands {
        script.push(cmd);
    }

    println!("Executing DAMA.v2 Thermodynamic Field-Dynamics Engine...");

    while let Some(cmd) = script.pop() {
        dama_core.execute_command(cmd);
    }

    println!("Script execution complete!");
    println!("Total ticks executed: {}", dama_core.ticks);
    println!("Final Dynamics State - Collapse Tension: {:.4}", dama_core.dynamics_state.collapse_tension);
    println!("Final Dynamics State - Operator Pressure: {:.4}", dama_core.dynamics_state.operator_pressure);
    println!("Final tetrahedral vertex 0 position: {:?}", dama_core.manifold.tetra_mesh[0].position);

    if let Some(cp) = dama_core.last_checkpoint {
        println!("Rolling back engine to checkpoint tick {}...", cp.ticks);
        dama_core.restore(cp);
        println!("Restored tick count: {}", dama_core.ticks);
        println!("Restored Collapse Tension: {:.4}", dama_core.dynamics_state.collapse_tension);
        println!("Restored tetrahedral vertex 0 position: {:?}", dama_core.manifold.tetra_mesh[0].position);
    }
}