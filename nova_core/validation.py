"""Reproducible NFD v0.4 experiments; standard library only."""
from __future__ import annotations

import json
import time
import tracemalloc

from .nfd_dynamics import NFDDynamics

CORPUS = (
    "AstraCore Nova learns from repeated observations.",
    "English language processing uses explicit sentence patterns.",
    "prediction error and temporal memory",
)


def _run_variant(text: str, variant: str, width: int = 32):
    engine = NFDDynamics(width=width)
    if variant == "no_adaptation":
        engine.learning_rate = 0.0
    for char in text:
        if variant == "no_trace":
            engine.trace = [0.0] * engine.width
        elif variant == "no_tension":
            engine.tension = [0.0] * engine.width
        engine.step(char)
        if variant == "no_trace":
            engine.trace = [0.0] * engine.width
        elif variant == "no_tension":
            engine.tension = [0.0] * engine.width
    return engine.snapshot(), engine.bias


def adaptation_report(repeats: int = 8) -> dict:
    if repeats < 2:
        raise ValueError("repeats must be >= 2")
    text = "English pattern " * repeats
    learned, bias = _run_variant(text, "full")
    frozen, frozen_bias = _run_variant(text, "no_adaptation")
    return {
        "bias_l1": sum(abs(x) for x in bias),
        "frozen_bias_l1": sum(abs(x) for x in frozen_bias),
        "adapted_state_delta_l1": sum(
            abs(a - b) for a, b in zip(learned.activation, frozen.activation)
        ),
        "steps": learned.step,
        "repeats": repeats,
    }


def ablation_report() -> dict:
    text = "Astra English " * 6
    results = {}
    for variant in ("full", "no_trace", "no_tension", "no_adaptation"):
        frame, bias = _run_variant(text, variant)
        results[variant] = {
            "activation_l1": sum(abs(x) for x in frame.activation),
            "trace_l1": sum(abs(x) for x in frame.trace),
            "tension_l1": sum(abs(x) for x in frame.tension),
            "bias_l1": sum(abs(x) for x in bias),
        }
    return results


def benchmark(repeats: int = 10, width: int = 32) -> dict:
    if repeats < 1:
        raise ValueError("repeats must be >= 1")
    text = "".join(CORPUS) * repeats
    tracemalloc.start()
    started = time.perf_counter()
    engine = NFDDynamics(width=width)
    frame = engine.observe(text)
    elapsed = time.perf_counter() - started
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {
        "events": frame.step,
        "width": width,
        "repeats": repeats,
        "elapsed_seconds": round(elapsed, 6),
        "events_per_second": round(frame.step / elapsed, 2) if elapsed else None,
        "peak_traced_bytes": peak,
        "final_activation_l1": round(sum(abs(x) for x in frame.activation), 8),
        "final_tension_l1": round(sum(abs(x) for x in frame.tension), 8),
    }


def run_validation() -> dict:
    return {
        "schema": "astracore-nova-nfd-v0.4",
        "adaptation": adaptation_report(),
        "ablations": ablation_report(),
        "benchmark": benchmark(),
        "caveat": (
            "Synthetic microbenchmark; not evidence of language understanding "
            "or general intelligence."
        ),
    }


if __name__ == "__main__":
    print(json.dumps(run_validation(), ensure_ascii=False, indent=2))
