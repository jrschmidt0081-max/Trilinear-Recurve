import fs from 'node:fs';
import { performance } from 'node:perf_hooks';
import { TriadLanguageEngine } from './engine.js';

// 1. INITIALIZATION
const engine = new TriadLanguageEngine();
console.log("=== NEEDLEPOINT CYBERNETICS: TRIAD ENGINE BENCHMARK ===");

// 2. VOCABULARY INGESTION & FALLBACK
let rawData = "";
try {
  rawData = fs.readFileSync('./vocab.json', 'utf-8');
} catch (err) {
  console.warn("[!] vocab.json not found. Injecting fallback manifold data.");
  rawData = JSON.stringify([
    "Refrak", "Plika", "action", "extremization", "wormhole", 
    "lambdaphi", "integrated", "high", "manifold", "geodesic", "tensor"
  ]);
}

const vocabGraph = JSON.parse(rawData);

function extractTokens(node: any): string[] {
  let tokens: string[] = [];
  if (typeof node === 'string') {
    tokens.push(node); // Full phrase
    const words = node.replace(/[^\w\s]/g, '').toLowerCase().split(/\s+/);
    tokens.push(...words.filter(w => w.length > 0)); // Individual words
  } else if (Array.isArray(node)) {
    node.forEach(item => tokens.push(...extractTokens(item)));
  } else if (typeof node === 'object' && node !== null) {
    Object.values(node).forEach(val => tokens.push(...extractTokens(val)));
  }
  return tokens;
}

const tokenList = [...new Set(extractTokens(vocabGraph))];
const embedStart = performance.now();
tokenList.forEach(token => engine.embedToken(token));
const embedTime = performance.now() - embedStart;

console.log(`[System] Embedded ${tokenList.length} unique tokens in ${embedTime.toFixed(3)} ms.`);

// 3. GENERATION PHASE
let sequence = ["Refrak", "Plika"];
const stepsToGenerate = 10; // Increased to test longer manifold trajectories
const maxContextWindow = 12; // Bounds the phase-shift accumulation

console.log(`\n[System] Commencing Autoregressive Loop`);
console.log(`[Prompt] [${sequence.join(", ")}]`);
console.log("-----------------------------------------------------");

const globalStart = performance.now();
let totalEngineSteps = 0;

for (let i = 0; i < stepsToGenerate; i++) {
  // Sliding window: only feed the last N tokens so P-vector phase doesn't blow up
  const contextWindow = sequence.slice(-maxContextWindow);
  
  const result = engine.processContext(contextWindow);
  sequence.push(result.token);
  totalEngineSteps += result.steps;
  
  console.log(`Step ${String(i + 1).padStart(2, '0')} -> Predicted: '${result.token.padEnd(12, ' ')}' \t(Engine Steps: ${String(result.steps).padStart(3, ' ')}, Compute: ${result.loopMs.toFixed(3)} ms)`);
}

const globalTime = performance.now() - globalStart;
const tokensPerSec = (stepsToGenerate / (globalTime / 1000)).toFixed(2);

console.log("-----------------------------------------------------");
console.log(`Final Output: [${sequence.join(", ")}]`);

// 4. TELEMETRY & PROFILING
console.log(`\n=== METRICS: TEMPUS/DAMA GEOMETRY ===`);
console.log(`Total Generation Time : ${globalTime.toFixed(3)} ms`);
console.log(`Average per Token     : ${(globalTime / stepsToGenerate).toFixed(3)} ms`);
console.log(`Throughput Speed      : ${tokensPerSec} tokens/sec`);
console.log(`Mean Relaxation Steps : ${(totalEngineSteps / stepsToGenerate).toFixed(1)} steps/token`);