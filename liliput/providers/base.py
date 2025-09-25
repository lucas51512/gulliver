"""
Base Quantum Provider Interface
==============================

Abstract base class for all quantum providers in Liliput.
Defines the common interface for executing quantum circuits.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from ..core.compiler import BackendCircuit

class QuantumExecutionResult:
    """Container for quantum execution results."""
    
    def __init__(self, counts: Dict[str, int], execution_time: float, 
                 metadata: Dict[str, Any] = None):
        self.counts = counts
        self.execution_time = execution_time
        self.metadata = metadata or {}
        self.shots = sum(counts.values()) if counts else 0
    
    def get_probabilities(self) -> Dict[str, float]:
        """Get measurement probabilities."""
        if self.shots == 0:
            return {}
        
        return {state: count / self.shots for state, count in self.counts.items()}
    
    def get_most_likely_state(self) -> Optional[str]:
        """Get the most frequently measured state."""
        if not self.counts:
            return None
        
        return max(self.counts.items(), key=lambda x: x[1])[0]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'counts': self.counts,
            'probabilities': self.get_probabilities(),
            'execution_time': self.execution_time,
            'shots': self.shots,
            'most_likely_state': self.get_most_likely_state(),
            'metadata': self.metadata
        }

class QuantumProvider(ABC):
    """
    Abstract base class for quantum providers.
    
    All quantum backends (Simulator, Qiskit, Cirq, Braket) inherit from this
    and implement the required methods.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.config = {}
        self.is_available = True
        self.error_message = None
    
    @abstractmethod
    def execute(self, circuit: BackendCircuit, shots: int = 1024, **kwargs) -> QuantumExecutionResult:
        """
        Execute a quantum circuit.
        
        Args:
            circuit: Compiled quantum circuit
            shots: Number of measurement shots
            **kwargs: Additional execution parameters
            
        Returns:
            QuantumExecutionResult: Execution results
        """
        pass
    
    @abstractmethod  
    def get_description(self) -> str:
        """Get provider description."""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get provider capabilities."""
        pass
    
    def is_provider_available(self) -> bool:
        """Check if provider is available."""
        return self.is_available
    
    def get_error_message(self) -> Optional[str]:
        """Get error message if provider is not available."""
        return self.error_message
    
    def set_config(self, config: Dict[str, Any]):
        """Set provider configuration."""
        self.config.update(config)
    
    def get_config(self) -> Dict[str, Any]:
        """Get provider configuration."""
        return self.config.copy()
    
    def validate_circuit(self, circuit: BackendCircuit) -> bool:
        """
        Validate if circuit is compatible with this provider.
        
        Args:
            circuit: Circuit to validate
            
        Returns:
            bool: True if valid
        """
        # Default implementation - can be overridden
        return True
    
    def create_circuit(self, num_qubits: int, num_classical: int = 0) -> BackendCircuit:
        """
        Create a backend-specific circuit.
        
        Args:
            num_qubits: Number of qubits
            num_classical: Number of classical bits
            
        Returns:
            BackendCircuit: Provider-specific circuit
        """
        # Default to generic circuit - providers can override
        from ..core.compiler import GenericBackendCircuit
        return GenericBackendCircuit(num_qubits, num_classical)
    
    def get_supported_gates(self) -> List[str]:
        """Get list of supported gate names."""
        # Default gate set - providers can override
        return ['x', 'y', 'z', 'h', 's', 't', 'rx', 'ry', 'rz', 
                'cnot', 'cz', 'crz', 'swap', 'ccx', 'measure']
    
    def get_max_qubits(self) -> int:
        """Get maximum number of qubits supported."""
        return 50  # Default limit - providers can override
    
    def supports_noise_simulation(self) -> bool:
        """Check if provider supports noise simulation."""
        return False  # Default - providers can override
    
    def supports_custom_gates(self) -> bool:
        """Check if provider supports custom gate definitions."""
        return False  # Default - providers can override
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get comprehensive provider information."""
        return {
            'name': self.name,
            'description': self.get_description(),
            'capabilities': self.get_capabilities(),
            'available': self.is_provider_available(),
            'error_message': self.get_error_message(),
            'supported_gates': self.get_supported_gates(),
            'max_qubits': self.get_max_qubits(),
            'supports_noise': self.supports_noise_simulation(),
            'supports_custom_gates': self.supports_custom_gates(),
            'config': self.get_config()
        }
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', available={self.is_available})"
    
    def __repr__(self) -> str:
        return self.__str__()

class QuantumProviderError(Exception):
    """Exception raised by quantum providers."""
    pass