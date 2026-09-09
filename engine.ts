export interface EngineConfig {
  dim: number;
  nStates: number;
  tau: number;
  weights: [number, number, number]; // [wP, wA, wE]
}

export const defaultConfig: EngineConfig = {
  dim: 8,
  nStates: 4,
  tau: 0.20,
  weights: [0.40, 0.35, 0.25],
};

export const wrap = (p: number): number => Math.atan2(Math.sin(p), Math.cos(p));

export class TriadLanguageEngine {
  public readonly config: EngineConfig;
  public stateSigma: number = 0;
  
  private vocab: Map<string, Float64Array> = new Map();
  private cachedGTensor: Float64Array | null = null; // Caches the metric tensor to prevent redundant calculation

  public readonly P: Float64Array;
  public readonly A: Float64Array;
  public readonly E: Float64Array;

  constructor(config: EngineConfig = defaultConfig) {
    this.config = config;
    this.P = new Float64Array(config.dim);
    this.A = new Float64Array(config.dim);
    this.E = new Float64Array(config.dim);
  }

  public embedToken(token: string): Float64Array {
    let vec = this.vocab.get(token);
    if (!vec) {
      vec = new Float64Array(this.config.dim);
      const idx = this.vocab.size;
      const basePhase = (idx * 2 * Math.PI) / 12;
      for (let i = 0; i < this.config.dim; i++) {
        vec[i] = wrap(basePhase + i * 0.1);
      }
      this.vocab.set(token, vec);
      this.cachedGTensor = null; // Invalidate cache when vocabulary expands
    }
    return vec;
  }

  public calculateCoherence(vec: Float64Array): number {
    let cosSum = 0.0;
    let sinSum = 0.0;
    for (let i = 0; i < vec.length; i++) {
      const v = vec[i] ?? 0;
      cosSum += Math.cos(v);
      sinSum += Math.sin(v);
    }
    return Math.sqrt(cosSum * cosSum + sinSum * sinSum) / vec.length;
  }

  public computeJacobianTrace(): number {
    let trace = 0.0;
    const len = this.E.length;
    for (let i = 0; i < len; i++) {
      const next = this.E[(i + 1) % len] ?? 0;
      const cur = this.E[i] ?? 0;
      trace += Math.sin(next - cur);
    }
    return trace / len;
  }

  public step(targetManifold: Float64Array): { coherence: number; trace: number; energy: number } {
    const { nStates, tau, weights, dim } = this.config;
    const [wP, wA, wE] = weights;
    const PI = Math.PI;
    const TWO_PI = 2 * PI;

    const trJ = this.computeJacobianTrace();
    const absTrJ = Math.abs(trJ);
    const coherence = this.calculateCoherence(this.E);

    // Fast O(1) target phase approximations (Replaces heavy decode() loop)
    let targetPhaseError = 0.0;
    let permeabilitySum = 0.0;
    for (let i = 0; i < dim; i++) {
      const eVal = this.E[i] ?? 0;
      const tVal = targetManifold[i] ?? 0;
      targetPhaseError += Math.abs(wrap(eVal - tVal));
      permeabilitySum += Math.cos(eVal - tVal);
    }
    
    // Normalized Vertebrae Metrics [0, 1]
    const eTrust = Math.max(0, 1.0 - (targetPhaseError / (dim * PI))); 
    const ePermeability = (permeabilitySum / dim + 1.0) / 2.0;

    // 5-Vertebrae Energy Functional (α-weighted)
    const energy = (0.35 * coherence) + 
                   (0.25 * absTrJ) + 
                   (0.20 * (1.0 - Math.min(Math.abs(trJ - tau), 1.0))) + 
                   (0.15 * eTrust) + 
                   (0.05 * ePermeability);

    // Hinge Logic: Branch switch φ_Max <-> φ_Min
    if (energy > 0.60) {
        if (trJ > tau) this.stateSigma = (this.stateSigma + 1) % nStates;
        else if (trJ < -tau) this.stateSigma = (this.stateSigma - 1 + nStates) % nStates;
    }

    const applyHinge = absTrJ > tau;
    const stateShift = (this.stateSigma * TWO_PI) / nStates;

    for (let i = 0; i < dim; i++) {
        const currentA = this.A[i] ?? 0;
        const currentE = this.E[i] ?? 0;
        const currentP = this.P[i] ?? 0;

        // Articulation (Δ): Expansion/Outward
        const deltaA = wrap((targetManifold[i] ?? 0) + stateShift - currentA);
        this.A[i] = wrap(currentA + 0.35 * deltaA);

        // Emergence (E): Vectorized Triad (Refrak Operator)
        const real = wP * Math.cos(currentP) + wA * Math.cos(this.A[i]!) + wE * Math.cos(currentE);
        const imag = wP * Math.sin(currentP) + wA * Math.sin(this.A[i]!) + wE * Math.sin(currentE);

        // Hinge-Seam Phase Flip: applyHinge triggers π-phase shift
        this.E[i] = applyHinge ? wrap(Math.atan2(imag, real) + PI) : Math.atan2(imag, real);

        // Persistence (P): Invariant/Continuity preservation
        this.P[i] = wrap(currentP + 0.25 * Math.sin(this.E[i]! - currentP));
    }

    return { coherence, trace: trJ, energy };
  }

  /**
   * Computes (and caches) a softened diagonal metric tensor approximation 
   * based on the variance of the vocabulary vectors.
   */
  private computeMetricTensor(): Float64Array {
    if (this.cachedGTensor) return this.cachedGTensor;

    const dim = this.config.dim;
    const gTensor = new Float64Array(dim);
    const epsilon = 1e-2;

    const allVectors = Array.from(this.vocab.values());
    if (allVectors.length === 0) {
      gTensor.fill(1.0);
      return gTensor;
    }

    const means = new Float64Array(dim);
    const variances = new Float64Array(dim);
    const n = allVectors.length;

    for (const vec of allVectors) {
      for (let i = 0; i < dim; i++) {
        means[i] += vec[i] ?? 0;
      }
    }
    for (let i = 0; i < dim; i++) {
      means[i] /= n;
    }

    for (const vec of allVectors) {
      for (let i = 0; i < dim; i++) {
        const diff = (vec[i] ?? 0) - means[i];
        variances[i] += diff * diff;
      }
    }
    for (let i = 0; i < dim; i++) {
      variances[i] /= n;
      gTensor[i] = 1.0 / (variances[i] + epsilon);
    }

    this.cachedGTensor = gTensor;
    return gTensor;
  }

  public decode(): { token: string; distance: number } {
    let closestToken = "UNK";
    let minDistance = Infinity; 

    const gTensor = this.computeMetricTensor();

    for (const [token, vec] of this.vocab.entries()) {
      let riemannianDistSq = 0.0;
      for (let i = 0; i < this.config.dim; i++) {
        const diff = wrap((this.E[i] ?? 0) - (vec[i] ?? 0));
        const g_ij = gTensor[i] ?? 1.0;
        riemannianDistSq += g_ij * diff * diff;
      }
      const dist = Math.sqrt(riemannianDistSq);

      if (dist < minDistance) {
        minDistance = dist;
        closestToken = token;
      }
    }

    return { token: closestToken, distance: minDistance };
  }

  public processContext(tokens: string[], maxSteps: number = 100): { token: string; loopMs: number; steps: number } {
    this.P.fill(0);
    
    for (let pos = 0; pos < tokens.length; pos++) {
      const vec = this.embedToken(tokens[pos]!);
      for (let i = 0; i < this.config.dim; i++) {
        this.P[i] = wrap((this.P[i] ?? 0) + (vec[i] ?? 0) + pos * 0.5);
      }
    }

    for (let i = 0; i < this.config.dim; i++) {
      this.A[i] = this.P[i]!;
      this.E[i] = this.P[i]!;
    }

    const lastToken = tokens[tokens.length - 1] ?? "EOS";
    const lastVec = this.embedToken(lastToken);
    
    const targetManifold = new Float64Array(this.config.dim);
    for (let i = 0; i < this.config.dim; i++) {
      targetManifold[i] = wrap((lastVec[i] ?? 0) + (1.5 * 2 * Math.PI / 12));
    }

    const loopStart = performance.now();
    let stepsExecuted = 0;

    for (let s = 0; s < maxSteps; s++) {
      stepsExecuted++;
      const { coherence, trace } = this.step(targetManifold);
      if (coherence >= 0.93 && Math.abs(trace) <= this.config.tau) {
        break;
      }
    }

    const loopMs = performance.now() - loopStart;

    return { token: this.decode().token, loopMs, steps: stepsExecuted };
  }
}