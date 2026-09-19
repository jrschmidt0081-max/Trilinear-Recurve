mod small_metrics;
mod triad_engine;
mod semantic_core;
mod semantic_expression;
mod dynamics_engine;
mod geometric;
mod semantic_continuation;
mod semantic_working_memory;
mod solvers;

use semantic_core::SemanticCore;
use small_metrics::CoreMetrics;
use triad_engine::{EngineConfig, TriadLanguageEngine};
use semantic_expression::SemanticExpressionLayer;
use dynamics_engine::{DynamicsEngine, DynamicsState};
use semantic_continuation::continue_semantic;
use semantic_working_memory::SemanticWorkingMemory;
use crate::geometric::{Chronon, GeometricSolver, MeshSolver};
use crate::solvers::{ErdosStrausSolver, CollatzSolver};

use std::io::{self, Write};

fn load_wordbank() -> Vec<String> {
    let exe_path = std::env::current_exe().unwrap();
    let exe_dir = exe_path.parent().unwrap();
    let target_dir = exe_dir.parent().unwrap();
    let project_root = target_dir.parent().unwrap();
    let wordbank_path = project_root.join("src").join("wordbank.txt");

    let data = std::fs::read_to_string(wordbank_path)
        .expect("Failed to read wordbank");

    data.lines()
        .map(|line| line.trim().to_string())
        .filter(|s| !s.is_empty())
        .collect()
}

fn main() {
    // === Engine Initialization ===
    let mut metrics = CoreMetrics::new();
    let mut engine = TriadLanguageEngine::new(EngineConfig::default());
    let mut semantic = SemanticCore::<19>::new();
    let dyn_engine = DynamicsEngine::new();
    let mut dyn_state = DynamicsState::default();
    let solver = MeshSolver;
    let mut geo_state = [0.0, 0.0, 0.0];
    let mut swm = SemanticWorkingMemory::new(8);

    // === Semantic Graph Setup ===
    semantic.initialize_links();

    // === Interactive Input ===
    println!("=== Tempus2 Engine & Calculator ===");
    println!("Enter a math expression (e.g., sqrt 2, 42) or text tokens:");
    print!("> ");
    io::stdout().flush().unwrap();

    let mut input = String::new();
    io::stdin().read_line(&mut input).unwrap();
    let raw_input = input.trim();

    if raw_input.is_empty() {
        println!("No input provided. Exiting.");
        return;
    }

    // Determine if input is math or text tokens
    let is_math = raw_input.starts_with("sqrt") || raw_input.parse::<f64>().is_ok();
    
    let (target_val, integer_proxy, tokens): (f64, u64, Vec<String>) = if is_math {
        let val = if raw_input.starts_with("sqrt") {
            let parts: Vec<&str> = raw_input.split_whitespace().collect();
            if parts.len() > 1 {
                parts[1].parse::<f64>().unwrap_or(2.0).sqrt()
            } else {
                2.0_f64.sqrt()
            }
        } else {
            raw_input.parse::<f64>().unwrap_or(1.4142)
        };
        let proxy = (val.abs() * 1000.0) as u64;
        let generated_tokens = vec![if val % 2.0 == 0.0 { "Continuity".to_string() } else { "Momentum".to_string() }];
        (val, proxy, generated_tokens)
    } else {
        let t_vec: Vec<String> = raw_input.split_whitespace().map(|s| s.to_string()).collect();
        (1.4142, 1414, t_vec)
    };

    // Run solvers using the phase proxy
    let collatz = CollatzSolver::new();
    let erdos = ErdosStrausSolver::new();
    let (_, _, lambda_l, trapped) = collatz.analyze_trajectory(integer_proxy.max(1));
    let erdos_solution = erdos.solve((integer_proxy % 97) + 1);

    // Update dynamics state with forces
    dyn_state.value = target_val;
    dyn_state.momentum = (target_val * 0.5).clamp(0.0, 10.0);
    dyn_state.drift = lambda_l;
    if trapped {
        dyn_state.collapse_tension *= 0.3;
    }

    if is_math {
        println!("\n=== Tempus2 Physics Calculator ===");
        println!("Expression / Input: {}", raw_input);
        println!("Evaluated Scalar: {:.6}", target_val);
        println!("Integer Phase Proxy: {}", integer_proxy);
        
        println!("\n=== Number-Theoretic Telemetry ===");
        println!("Collatz Lyapunov Contraction (lambda_l): {:.4}", lambda_l);
        println!("Phase-Space Trapped (Attractor Lock): {}", trapped);
        if let Some((x, y, z)) = erdos_solution {
            println!("Erdős-Straus Invariant Triple (x, y, z): ({}, {}, {})", x, y, z);
        }
    }

    // === Wordbank & Filtering ===
    let wordbank = load_wordbank();

    let filtered_tokens: Vec<String> = tokens
        .into_iter()
        .map(|t| {
            if let Some(canonical) = wordbank.iter().find(|w| w.eq_ignore_ascii_case(&t)) {
                canonical.clone()
            } else {
                println!("Token '{}' not in wordbank — substituting UNK", t);
                "UNK".to_string()
            }
        })
        .collect();

    // === Triad Engine Decode ===
    let (decoded_token, loop_ms, steps) = engine.process_context(&filtered_tokens);

    let chronon = Chronon {
        tick: metrics.tick_count,
        delta: loop_ms as u128,
    };

    // === Semantic Stress & Transitions ===
    let mut semantic_stress = 0.0;
    let mut transition_narrative = Vec::new();

    for w in filtered_tokens.windows(2) {
        let a = &w[0];
        let b = &w[1];

        let idx_a = wordbank.iter().position(|x| x == a).unwrap_or(usize::MAX);
        let idx_b = wordbank.iter().position(|x| x == b).unwrap_or(usize::MAX);

        if idx_a < 19 && idx_b < 19 {
            let transition_str = SemanticExpressionLayer::express_transition(idx_a, idx_b);
            transition_narrative.push(transition_str);

            if semantic.is_linked(idx_a, idx_b) {
                semantic_stress -= 0.02;
                metrics.avg_grad_norm *= 0.95;
            } else {
                semantic_stress += 0.05;
                metrics.record_hinge_event();
            }
        }
    }

    metrics.add_spectral_stress(semantic_stress);

    // === Metrics Update ===
    metrics.tick();
    metrics.record_gradient_step(loop_ms / 100.0, steps as f64);
    metrics.add_spectral_stress(loop_ms * 0.01);

    // === Geometry Evolution ===
    geo_state = solver.evolve(&geo_state, chronon);

    // === Dynamics Update ===
    dyn_engine.update(&mut dyn_state, &metrics, &geo_state, &filtered_tokens);

    // === Semantic Decode Layer ===
    let mut semantic_decode = decoded_token.clone();

    if filtered_tokens.len() >= 2 {
        let a = &filtered_tokens[filtered_tokens.len() - 2];
        let b = &filtered_tokens[filtered_tokens.len() - 1];

        let idx_a = wordbank.iter().position(|x| x == a).unwrap_or(usize::MAX);
        let idx_b = wordbank.iter().position(|x| x == b).unwrap_or(usize::MAX);

        if idx_a < 19 && idx_b < 19 && semantic.is_linked(idx_a, idx_b) {
            semantic_decode = b.clone();
        }
    }

    if metrics.spectral_stress > 0.5 {
        semantic_decode = "UNK".to_string();
    }

    // === Working Memory ===
    let idx = wordbank.iter().position(|w| w == &semantic_decode).unwrap_or(0);
    swm.activate(idx);
    swm.decay();

    // === Multi-step Continuation ===
    let cont_token = continue_semantic(&semantic_decode, &dyn_state, &wordbank);

    // === Collapse Override ===
    if dyn_state.collapse_tension > 0.5 {
        semantic_decode = "Collapse".to_string();
    }

    // === Expressive Output ===
    let expressive_output = SemanticExpressionLayer::express_with_dynamics(
        wordbank.iter().position(|w| w == &semantic_decode).unwrap_or(0),
        &dyn_state
    );

    // === Output ===
    println!("\n=== Engine Output ===");
    println!("Decoded token: {}", semantic_decode);
    println!("Continuation: {}", cont_token);
    println!("Loop time: {:.3} ms", loop_ms);
    println!("Steps executed: {}", steps);

    println!("\n=== Metrics Snapshot ===");
    println!("Ticks: {}", metrics.tick_count);
    println!("Gradient Steps: {}", metrics.grad_steps);
    println!("Average Grad Norm: {:.4}", metrics.avg_grad_norm);
    println!("Max Grad Norm: {:.4}", metrics.max_grad_norm);
    println!("Loss Value: {:.4}", metrics.loss_value);
    println!("Spectral Stress: {:.4}", metrics.spectral_stress);
    println!("Hinge Events: {}", metrics.hinge_events);
    println!("Uptime: {:?}", metrics.uptime());

    println!("\n=== Geometry State ===");
    println!("Coordinates: [{:.4}, {:.4}, {:.4}]",
        geo_state[0], geo_state[1], geo_state[2]);

    println!("\n=== Expressive Output ===");
    println!("{}", expressive_output);

    println!("\n=== Dynamics State ===");
    println!("Momentum: {:.4}", dyn_state.momentum);
    println!("Curvature: {:.4}", dyn_state.curvature);
    println!("Drift: {:.4}", dyn_state.drift);
    println!("Invariants: {:.4}", dyn_state.invariants);
    println!("Semantic Curvature: {:.4}", dyn_state.semantic_curvature);
    println!("Operator Pressure: {:.4}", dyn_state.operator_pressure);
    println!("Collapse Tension: {:.4}", dyn_state.collapse_tension);

    println!("\n=== Working Memory State ===");
    println!("Recent Episodic Indices: {:?}", swm.recent());
    println!("Last Token Index: {:?}", swm.last());
    println!("Current Token Activation Score: {:.4}", swm.activation_of(idx));

    println!("\n=== Transition Narrative ===");
    if transition_narrative.is_empty() {
        println!("No valid sequential transitions to express.");
    } else {
        for t in transition_narrative {
            println!("  -> {}", t);
        }
    }
}