"""NFD Tri-Ledger Dynamics: an experimental, non-neural state machine.

This module is a hand-designed research mechanism. It is not a language model,
and its novelty has not been established. Input is consumed one Unicode scalar
at a time; no tokenization or learned embedding table is used.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import sin, cos, tanh, sqrt

@dataclass(frozen=True)
class NFDFrame:
    """Immutable observation of the coupled field after one input event."""
    activation: tuple[float, ...]
    trace: tuple[float, ...]
    tension: tuple[float, ...]
    surprise: float
    step: int

class NFDDynamics:
    """Three-ledger event dynamics with surprise-gated local plasticity.

    Ledgers: current activation, decaying temporal trace, and prediction-error
    tension. A bounded local bias adapts from prediction residuals. This is a
    hand-designed update rule, not backpropagation or a neural network.
    """
    def __init__(self, width: int = 32, learning_rate: float = 0.015):
        if width < 8:
            raise ValueError("width must be >= 8")
        if not 0.0 < learning_rate <= 0.1:
            raise ValueError("learning_rate must be in (0, 0.1]")
        self.width = width
        self.learning_rate = learning_rate
        self.activation = [0.0] * width
        self.trace = [0.0] * width
        self.tension = [0.0] * width
        self.bias = [0.0] * width
        self.steps = 0

    def _signal(self, scalar: int, position: int) -> list[float]:
        # Continuous phase features derived directly from a Unicode scalar.
        x = (scalar + 1) / 0x110000
        p = position + 1
        return [0.5 * (sin((i + 1) * x * 17.0 + p * 0.071)
                       + cos((i + 1) * x * 11.0 - p * 0.037))
                for i in range(self.width)]

    def step(self, char: str) -> NFDFrame:
        if not isinstance(char, str) or len(char) != 1:
            raise ValueError("step expects exactly one Unicode character")
        drive = self._signal(ord(char), self.steps)
        old = self.activation[:]
        residual = []
        for i in range(self.width):
            neighbour = 0.5 * (old[(i - 1) % self.width] + old[(i + 1) % self.width])
            estimate = tanh(0.62 * old[i] + 0.18 * neighbour + self.bias[i])
            residual.append(drive[i] - estimate)
        surprise = sqrt(sum(r * r for r in residual) / self.width)
        gate = min(1.0, surprise)
        next_activation, next_trace, next_tension, next_bias = [], [], [], []
        for i, error in enumerate(residual):
            neighbour = 0.5 * (old[(i - 1) % self.width] + old[(i + 1) % self.width])
            value = tanh(0.48 * old[i] + 0.17 * neighbour + 0.27 * drive[i]
                         + 0.08 * self.trace[i] - 0.06 * self.tension[i])
            next_activation.append(value)
            next_trace.append(0.86 * self.trace[i] + 0.14 * old[i])
            next_tension.append(min(1.0, 0.90 * self.tension[i] + 0.10 * error * error))
            next_bias.append(max(-1.0, min(1.0,
                self.bias[i] + self.learning_rate * gate * error * self.trace[i])))
        self.activation, self.trace = next_activation, next_trace
        self.tension, self.bias = next_tension, next_bias
        self.steps += 1
        return self.snapshot(surprise)

    def observe(self, text: str) -> NFDFrame:
        """Consume a complete string as an uninterrupted event stream."""
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        frame = self.snapshot()
        for char in text:
            frame = self.step(char)
        return frame

    def snapshot(self, surprise: float = 0.0) -> NFDFrame:
        return NFDFrame(tuple(self.activation), tuple(self.trace),
                        tuple(self.tension), float(surprise), self.steps)

    def reset(self) -> None:
        """Reset dynamic state and learned local bias."""
        self.activation = [0.0] * self.width
        self.trace = [0.0] * self.width
        self.tension = [0.0] * self.width
        self.bias = [0.0] * self.width
        self.steps = 0
