"""
IBM Qiskit Provider (Stub Implementation)
========================================

Provides integration with IBM Qiskit for real quantum hardware access.
This is a stub implementation - full version would require qiskit installation.
"""

from typing import Dict, List, Any
from .base import QuantumProvider, QuantumExecutionResult, QuantumProviderError
from ..core.compiler import BackendCircuit

class QiskitProvider(QuantumProvider):
    """IBM Qiskit quantum provider (stub)."""
    
    def __init__(self):
        super().__init__("qiskit")
        self.is_available = False
        self.error_message = "Qiskit not installed. Install with: pip install qiskit"
    
    def execute(self, circuit: BackendCircuit, shots: int = 1024, **kwargs) -> QuantumExecutionResult:
        """Execute circuit on Qiskit backend."""
        raise QuantumProviderError(self.error_message)
    
    def get_description(self) -> str:
        """Get provider description."""
        return "IBM Qiskit provider for real quantum hardware access (requires qiskit package)"
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        return {
            'max_qubits': 1000,
            'supports_noise': True,
            'real_hardware': True,
            'cloud_access': True,
            'status': 'requires_installation'
        }