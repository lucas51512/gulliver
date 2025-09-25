"""
Quantum Circuit Compiler
========================

Compiles Liliput IR to backend-specific quantum circuit representations.
Handles semantic validation and backend-specific optimizations.
"""

from typing import Dict, List, Any, Optional, Union
from abc import ABC, abstractmethod
from .ir import QuantumCircuitIR, ProgramIR, GateType, QuantumGate, Qubit

class CompilationError(Exception):
    """Exception raised during circuit compilation."""
    pass

class BackendCircuit(ABC):
    """Abstract base class for backend-specific circuit representations."""
    
    @abstractmethod
    def add_gate(self, gate_type: str, qubits: List[int], parameters: List[float] = None):
        """Add a gate to the backend circuit."""
        pass
    
    @abstractmethod
    def add_measurement(self, qubit: int, classical_bit: int):
        """Add a measurement to the backend circuit."""
        pass
    
    @abstractmethod
    def get_circuit_data(self) -> Any:
        """Get the native circuit representation."""
        pass

class GenericBackendCircuit(BackendCircuit):
    """Generic backend circuit implementation."""
    
    def __init__(self, num_qubits: int, num_classical: int = 0):
        self.num_qubits = num_qubits
        self.num_classical = num_classical
        self.gates = []
        self.measurements = []
        self.metadata = {}
    
    def add_gate(self, gate_type: str, qubits: List[int], parameters: List[float] = None):
        """Add a gate to the circuit."""
        gate = {
            'type': gate_type,
            'qubits': qubits,
            'parameters': parameters or []
        }
        self.gates.append(gate)
    
    def add_measurement(self, qubit: int, classical_bit: int):
        """Add a measurement."""
        measurement = {
            'qubit': qubit,
            'classical_bit': classical_bit
        }
        self.measurements.append(measurement)
    
    def get_circuit_data(self) -> Dict[str, Any]:
        """Get circuit data."""
        return {
            'num_qubits': self.num_qubits,
            'num_classical': self.num_classical,
            'gates': self.gates,
            'measurements': self.measurements,
            'metadata': self.metadata
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.get_circuit_data()

class QuantumCompiler:
    """
    Compiles Liliput IR to backend-specific quantum circuits.
    
    Performs semantic validation and ensures the circuit is compatible
    with the target quantum backend.
    """
    
    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.gate_transpilation = self._initialize_gate_transpilation()
    
    def _initialize_validation_rules(self) -> Dict[str, Any]:
        """Initialize semantic validation rules."""
        return {
            'max_qubits': 1000,  # Reasonable limit
            'max_gates': 10000,  # Reasonable limit
            'required_gates': [GateType.H, GateType.X, GateType.CNOT],  # Common gates
            'supported_gates': list(GateType),
            'measurement_required': False
        }
    
    def _initialize_gate_transpilation(self) -> Dict[GateType, Dict[str, Any]]:
        """Initialize gate transpilation rules."""
        return {
            GateType.X: {'name': 'x', 'qubits': 1, 'parameters': 0},
            GateType.Y: {'name': 'y', 'qubits': 1, 'parameters': 0},
            GateType.Z: {'name': 'z', 'qubits': 1, 'parameters': 0},
            GateType.H: {'name': 'h', 'qubits': 1, 'parameters': 0},
            GateType.S: {'name': 's', 'qubits': 1, 'parameters': 0},
            GateType.T: {'name': 't', 'qubits': 1, 'parameters': 0},
            GateType.RX: {'name': 'rx', 'qubits': 1, 'parameters': 1},
            GateType.RY: {'name': 'ry', 'qubits': 1, 'parameters': 1},
            GateType.RZ: {'name': 'rz', 'qubits': 1, 'parameters': 1},
            GateType.CNOT: {'name': 'cnot', 'qubits': 2, 'parameters': 0},
            GateType.CZ: {'name': 'cz', 'qubits': 2, 'parameters': 0},
            GateType.CRZ: {'name': 'crz', 'qubits': 2, 'parameters': 1},
            GateType.SWAP: {'name': 'swap', 'qubits': 2, 'parameters': 0},
            GateType.TOFFOLI: {'name': 'ccx', 'qubits': 3, 'parameters': 0},
            GateType.MEASURE: {'name': 'measure', 'qubits': 1, 'parameters': 0}
        }
    
    def compile(self, circuit: QuantumCircuitIR, provider=None) -> BackendCircuit:
        """
        Compile Liliput IR circuit to backend-specific format.
        
        Args:
            circuit: QuantumCircuitIR to compile
            provider: Target quantum provider (optional)
            
        Returns:
            BackendCircuit: Compiled circuit
        """
        try:
            # Validate the circuit
            self._validate_circuit(circuit)
            
            # Create backend circuit
            backend_circuit = self._create_backend_circuit(circuit, provider)
            
            # Transpile gates
            self._transpile_gates(circuit, backend_circuit)
            
            # Add measurements
            self._add_measurements(circuit, backend_circuit)
            
            return backend_circuit
            
        except Exception as e:
            raise CompilationError(f"Failed to compile circuit '{circuit.name}': {str(e)}")
    
    def _validate_circuit(self, circuit: QuantumCircuitIR):
        """Perform semantic validation on the circuit."""
        # Check circuit size limits
        if circuit.get_num_qubits() > self.validation_rules['max_qubits']:
            raise CompilationError(f"Too many qubits: {circuit.get_num_qubits()} > {self.validation_rules['max_qubits']}")
        
        if circuit.get_num_gates() > self.validation_rules['max_gates']:
            raise CompilationError(f"Too many gates: {circuit.get_num_gates()} > {self.validation_rules['max_gates']}")
        
        # Validate individual gates
        for gate in circuit.gates:
            self._validate_gate(gate, circuit)
        
        # Check for empty circuit
        if circuit.get_num_qubits() == 0:
            raise CompilationError("Circuit has no qubits")
    
    def _validate_gate(self, gate: QuantumGate, circuit: QuantumCircuitIR):
        """Validate individual gate."""
        # Check if gate type is supported
        if gate.gate_type not in self.gate_transpilation:
            raise CompilationError(f"Unsupported gate type: {gate.gate_type}")
        
        gate_info = self.gate_transpilation[gate.gate_type]
        
        # Check qubit count
        if len(gate.qubits) != gate_info['qubits']:
            raise CompilationError(f"Gate {gate.gate_type} requires {gate_info['qubits']} qubits, got {len(gate.qubits)}")
        
        # Check parameter count
        if len(gate.parameters) != gate_info['parameters']:
            raise CompilationError(f"Gate {gate.gate_type} requires {gate_info['parameters']} parameters, got {len(gate.parameters)}")
        
        # Check qubit indices
        for qubit in gate.qubits:
            if qubit.index >= circuit.get_num_qubits():
                raise CompilationError(f"Qubit index {qubit.index} out of range for circuit with {circuit.get_num_qubits()} qubits")
    
    def _create_backend_circuit(self, circuit: QuantumCircuitIR, provider) -> BackendCircuit:
        """Create appropriate backend circuit."""
        num_classical = len(circuit.classical_bits) + len(circuit.measurements)
        
        # If provider has specific circuit creation method, use it
        if provider and hasattr(provider, 'create_circuit'):
            return provider.create_circuit(circuit.get_num_qubits(), num_classical)
        
        # Default to generic backend circuit
        return GenericBackendCircuit(circuit.get_num_qubits(), num_classical)
    
    def _transpile_gates(self, circuit: QuantumCircuitIR, backend_circuit: BackendCircuit):
        """Transpile gates to backend format."""
        for gate in circuit.gates:
            if gate.gate_type == GateType.MEASURE:
                continue  # Handle measurements separately
            
            gate_info = self.gate_transpilation[gate.gate_type]
            gate_name = gate_info['name']
            
            # Convert qubits to indices
            qubit_indices = [q.index for q in gate.qubits]
            
            # Add gate to backend circuit
            backend_circuit.add_gate(gate_name, qubit_indices, gate.parameters)
    
    def _add_measurements(self, circuit: QuantumCircuitIR, backend_circuit: BackendCircuit):
        """Add measurements to backend circuit."""
        for measurement in circuit.measurements:
            backend_circuit.add_measurement(
                measurement.qubit.index,
                measurement.classical_bit.index
            )
    
    def validate_program(self, program: ProgramIR) -> Dict[str, Any]:
        """
        Validate complete program.
        
        Args:
            program: ProgramIR to validate
            
        Returns:
            Dict with validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'circuits': []
        }
        
        try:
            for i, circuit in enumerate(program.circuits):
                circuit_result = {
                    'name': circuit.name,
                    'index': i,
                    'valid': True,
                    'errors': [],
                    'warnings': []
                }
                
                try:
                    self._validate_circuit(circuit)
                except CompilationError as e:
                    circuit_result['valid'] = False
                    circuit_result['errors'].append(str(e))
                    results['valid'] = False
                    results['errors'].append(f"Circuit {i} '{circuit.name}': {str(e)}")
                
                # Add warnings for potential issues
                if circuit.get_num_gates() == 0:
                    warning = "Circuit has no gates"
                    circuit_result['warnings'].append(warning)
                    results['warnings'].append(f"Circuit {i} '{circuit.name}': {warning}")
                
                if len(circuit.measurements) == 0:
                    warning = "Circuit has no measurements"
                    circuit_result['warnings'].append(warning)
                    results['warnings'].append(f"Circuit {i} '{circuit.name}': {warning}")
                
                results['circuits'].append(circuit_result)
            
            return results
            
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Program validation failed: {str(e)}"],
                'warnings': [],
                'circuits': []
            }
    
    def get_compilation_stats(self, circuit: QuantumCircuitIR) -> Dict[str, Any]:
        """Get compilation statistics for a circuit."""
        stats = {
            'original_qubits': circuit.get_num_qubits(),
            'original_gates': circuit.get_num_gates(),
            'original_depth': circuit.get_depth(),
            'gate_types': {},
            'qubit_usage': {}
        }
        
        # Count gate types
        for gate in circuit.gates:
            gate_type = gate.gate_type.value
            stats['gate_types'][gate_type] = stats['gate_types'].get(gate_type, 0) + 1
        
        # Count qubit usage
        for gate in circuit.gates:
            for qubit in gate.qubits:
                qubit_name = qubit.name
                stats['qubit_usage'][qubit_name] = stats['qubit_usage'].get(qubit_name, 0) + 1
        
        return stats

# Example usage and testing
if __name__ == "__main__":
    from .ir import QuantumCircuitIR, GateType
    
    # Create test circuit
    circuit = QuantumCircuitIR("test_circuit")
    q0 = circuit.add_qubit("q0")
    q1 = circuit.add_qubit("q1")
    c0 = circuit.add_classical_bit("c0")
    c1 = circuit.add_classical_bit("c1")
    
    # Add gates
    circuit.add_gate(GateType.H, [q0])
    circuit.add_gate(GateType.CNOT, [q0, q1])
    
    # Add measurements
    circuit.add_measurement(q0, c0)
    circuit.add_measurement(q1, c1)
    
    # Test compilation
    compiler = QuantumCompiler()
    try:
        compiled = compiler.compile(circuit)
        print("Compilation successful!")
        print(f"Compiled circuit: {compiled.to_dict()}")
        
        stats = compiler.get_compilation_stats(circuit)
        print(f"Compilation stats: {stats}")
        
    except CompilationError as e:
        print(f"Compilation error: {e}")