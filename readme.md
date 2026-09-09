# Tempus / DAMA Triadic Geometric Engine

A zero-dependency, high-performance TypeScript engine that couples a **triadic state core** with a **live Riemannian geometric reasoner**. 

Instead of relying on flat statistical probability or heavy cloud dependencies, Tempus treats text and state as a dynamic manifold, navigating trajectories using native typed arrays (`Float64Array`) and feedback-controlled phase mechanics.

## Core Architecture

* **Triadic Core (P-A-E):** Manages state across Persistence ($P$), Articulation ($A$), and Emergence ($E$) vectors.
* **Riemannian Metric Adaptation:** Dynamically computes diagonal metric tensors based on vocabulary variance rather than assuming a flat Euclidean space.
* **Bounded Hinge Logic:** Uses Jacobian trace monitoring against an $\alpha$-coupled threshold ($\tau$) to trigger phase wrapping and prevent runaway feedback loops.

## Repository Structure

* `engine.ts` - The core triadic state engine and metric solver.
* `test.ts` - Automated benchmark and trajectory validation harness.
* `vocab.json` - Raw token manifold dataset.

## Quick Start

1. Install dependencies:
   ```bash
   npm install