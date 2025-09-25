"""
Liliput Quantum Middleware
=========================

A comprehensive quantum programming middleware for the Gulliver language.
Provides universal quantum backend support, optimization, and professional tooling.

Key Features:
- Universal backend support (Simulator, Qiskit, Cirq, Braket)
- Multi-level quantum circuit optimization
- Professional CLI with debugging and profiling
- Real quantum simulation with noise models
- Comprehensive testing framework

Author: lucas51512
License: MIT
"""

__version__ = "2.0.0"
__author__ = "lucas51512"

from .core.engine import LiliputEngine
from .core.parser import GulliverToIR
from .core.compiler import QuantumCompiler
from .core.optimizer import CircuitOptimizer

# Main entry point
def create_engine(**kwargs):
    """Create a new Liliput quantum engine instance."""
    return LiliputEngine(**kwargs)

# Version info
def version_info():
    """Get version information."""
    return {
        'version': __version__,
        'author': __author__,
        'components': [
            'Core Engine',
            'Quantum Compiler', 
            'Circuit Optimizer',
            'Provider System',
            'CLI Tools'
        ]
    }

__all__ = [
    'LiliputEngine',
    'GulliverToIR', 
    'QuantumCompiler',
    'CircuitOptimizer',
    'create_engine',
    'version_info'
]