"""
Intermediate Representation (IR) for Quantum Circuits
====================================================

Defines the internal representation used by Liliput for quantum programs.
This IR is backend-agnostic and optimizable.
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import uuid

class GateType(Enum):
    """Quantum gate types supported by Liliput."""
    # Single-qubit gates
    X = "x"
    Y = "y" 
    Z = "z"
    H = "h"  # Hadamard
    S = "s"
    T = "t"
    RX = "rx"
    RY = "ry"
    RZ = "rz"
    
    # Two-qubit gates
    CNOT = "cnot"
    CZ = "cz"
    CRZ = "crz"
    SWAP = "swap"
    
    # Multi-qubit gates
    TOFFOLI = "toffoli"
    
    # Measurement
    MEASURE = "measure"
    
    # Special operations
    BARRIER = "barrier"
    RESET = "reset"

@dataclass
class Qubit:
    """Represents a quantum bit in the IR."""
    id: str
    index: int
    name: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            self.name = f"q{self.index}"

@dataclass
class QuantumGate:
    """Represents a quantum gate operation."""
    gate_type: GateType
    qubits: List[Qubit]
    parameters: List[float] = None
    condition: Optional[str] = None
    gate_id: str = None
    
    def __post_init__(self):
        if not self.gate_id:
            self.gate_id = str(uuid.uuid4())[:8]
        if self.parameters is None:
            self.parameters = []

@dataclass
class ClassicalBit:
    """Represents a classical bit for measurements."""
    id: str
    index: int
    name: Optional[str] = None
    
    def __post_init__(self):
        if not self.name:
            self.name = f"c{self.index}"

@dataclass
class MeasurementOp:
    """Represents a measurement operation."""
    qubit: Qubit
    classical_bit: ClassicalBit
    measurement_id: str = None
    
    def __post_init__(self):
        if not self.measurement_id:
            self.measurement_id = str(uuid.uuid4())[:8]

class QuantumCircuitIR:
    """
    Intermediate Representation of a quantum circuit.
    
    This is the core data structure used throughout Liliput for
    representing quantum programs in a backend-agnostic way.
    """
    
    def __init__(self, name: str = "circuit"):
        self.name = name
        self.qubits: List[Qubit] = []
        self.classical_bits: List[ClassicalBit] = []
        self.gates: List[QuantumGate] = []
        self.measurements: List[MeasurementOp] = []
        self.metadata: Dict[str, Any] = {}
        self.circuit_id = str(uuid.uuid4())[:8]
    
    def add_qubit(self, name: Optional[str] = None) -> Qubit:
        """Add a new qubit to the circuit."""
        index = len(self.qubits)
        qubit = Qubit(f"q_{self.circuit_id}_{index}", index, name)
        self.qubits.append(qubit)
        return qubit
    
    def add_classical_bit(self, name: Optional[str] = None) -> ClassicalBit:
        """Add a new classical bit to the circuit."""
        index = len(self.classical_bits)
        cbit = ClassicalBit(f"c_{self.circuit_id}_{index}", index, name)
        self.classical_bits.append(cbit)
        return cbit
    
    def add_gate(self, gate_type: GateType, qubits: List[Qubit], 
                 parameters: List[float] = None, condition: str = None) -> QuantumGate:
        """Add a quantum gate to the circuit."""
        gate = QuantumGate(gate_type, qubits, parameters, condition)
        self.gates.append(gate)
        return gate
    
    def add_measurement(self, qubit: Qubit, classical_bit: ClassicalBit) -> MeasurementOp:
        """Add a measurement operation."""
        measurement = MeasurementOp(qubit, classical_bit)
        self.measurements.append(measurement)
        return measurement
    
    def get_num_qubits(self) -> int:
        """Get the number of qubits in the circuit."""
        return len(self.qubits)
    
    def get_num_gates(self) -> int:
        """Get the number of gates in the circuit."""
        return len(self.gates)
    
    def get_depth(self) -> int:
        """Calculate circuit depth (simplified)."""
        # Simple depth calculation - can be optimized
        qubit_last_gate = {q.id: -1 for q in self.qubits}
        depth = 0
        
        for i, gate in enumerate(self.gates):
            gate_time = max(qubit_last_gate[q.id] for q in gate.qubits) + 1
            for qubit in gate.qubits:
                qubit_last_gate[qubit.id] = gate_time
            depth = max(depth, gate_time)
        
        return depth
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert circuit to dictionary representation."""
        return {
            'name': self.name,
            'circuit_id': self.circuit_id,
            'num_qubits': self.get_num_qubits(),
            'num_gates': self.get_num_gates(),
            'depth': self.get_depth(),
            'qubits': [{'id': q.id, 'index': q.index, 'name': q.name} for q in self.qubits],
            'classical_bits': [{'id': c.id, 'index': c.index, 'name': c.name} for c in self.classical_bits],
            'gates': [
                {
                    'gate_type': gate.gate_type.value,
                    'qubits': [q.id for q in gate.qubits],
                    'parameters': gate.parameters,
                    'gate_id': gate.gate_id
                }
                for gate in self.gates
            ],
            'measurements': [
                {
                    'qubit': m.qubit.id,
                    'classical_bit': m.classical_bit.id,
                    'measurement_id': m.measurement_id
                }
                for m in self.measurements
            ],
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        """String representation of the circuit."""
        return f"QuantumCircuitIR(name='{self.name}', qubits={self.get_num_qubits()}, gates={self.get_num_gates()}, depth={self.get_depth()})"
    
    def __repr__(self) -> str:
        return self.__str__()

class ProgramIR:
    """
    Complete program representation including multiple circuits and classical code.
    """
    
    def __init__(self, name: str = "program"):
        self.name = name
        self.circuits: List[QuantumCircuitIR] = []
        self.classical_code: List[str] = []
        self.imports: List[str] = []
        self.metadata: Dict[str, Any] = {}
        self.program_id = str(uuid.uuid4())[:8]
    
    def add_circuit(self, circuit: QuantumCircuitIR):
        """Add a quantum circuit to the program."""
        self.circuits.append(circuit)
    
    def add_classical_code(self, code: str):
        """Add classical code snippet."""
        self.classical_code.append(code)
    
    def get_total_qubits(self) -> int:
        """Get total number of qubits across all circuits."""
        return sum(circuit.get_num_qubits() for circuit in self.circuits)
    
    def get_total_gates(self) -> int:
        """Get total number of gates across all circuits."""
        return sum(circuit.get_num_gates() for circuit in self.circuits)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert program to dictionary representation."""
        return {
            'name': self.name,
            'program_id': self.program_id,
            'total_qubits': self.get_total_qubits(),
            'total_gates': self.get_total_gates(),
            'circuits': [circuit.to_dict() for circuit in self.circuits],
            'classical_code': self.classical_code,
            'imports': self.imports,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        return f"ProgramIR(name='{self.name}', circuits={len(self.circuits)}, total_qubits={self.get_total_qubits()})"
    
    def __repr__(self) -> str:
        return self.__str__()