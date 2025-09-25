"""
Gulliver to IR Parser
====================

Converts Gulliver language AST to Liliput's Intermediate Representation.
This is the bridge between the frontend language and the quantum backend.
"""

from typing import Dict, List, Any, Optional, Union
import re
from ..core.ir import (
    QuantumCircuitIR, ProgramIR, GateType, Qubit, ClassicalBit,
    QuantumGate, MeasurementOp
)

class GulliverParseError(Exception):
    """Exception raised during Gulliver code parsing."""
    pass

class GulliverToIR:
    """
    Converts Gulliver language code to Liliput IR.
    
    This parser understands Gulliver syntax and converts quantum operations
    to the internal IR format that can be optimized and executed on any backend.
    """
    
    def __init__(self):
        self.current_circuit: Optional[QuantumCircuitIR] = None
        self.current_program: Optional[ProgramIR] = None
        self.variable_map: Dict[str, Union[Qubit, ClassicalBit]] = {}
        self.function_registry: Dict[str, Any] = {}
        
        # Initialize quantum gate mappings
        self.gate_mappings = {
            'x': GateType.X,
            'y': GateType.Y,
            'z': GateType.Z,
            'h': GateType.H,
            'had': GateType.H,  # Hadamard alias
            's': GateType.S,
            't': GateType.T,
            'rx': GateType.RX,
            'ry': GateType.RY,
            'rz': GateType.RZ,
            'cnot': GateType.CNOT,
            'cz': GateType.CZ,
            'crz': GateType.CRZ,
            'swap': GateType.SWAP,
            'toffoli': GateType.TOFFOLI,
            'ccx': GateType.TOFFOLI,  # Toffoli alias
            'measure': GateType.MEASURE
        }
    
    def parse_program(self, gulliver_code: str, program_name: str = "main") -> ProgramIR:
        """
        Parse complete Gulliver program into IR.
        
        Args:
            gulliver_code: Gulliver source code string
            program_name: Name for the program
            
        Returns:
            ProgramIR: Complete program representation
        """
        self.current_program = ProgramIR(program_name)
        self.current_circuit = QuantumCircuitIR("main_circuit")
        self.variable_map = {}
        
        try:
            # Simple parsing approach - can be enhanced with full AST
            lines = self._preprocess_code(gulliver_code)
            
            for line_num, line in enumerate(lines, 1):
                try:
                    self._parse_line(line, line_num)
                except Exception as e:
                    raise GulliverParseError(f"Line {line_num}: {str(e)}")
            
            # Add the main circuit to program
            if self.current_circuit.get_num_qubits() > 0 or self.current_circuit.get_num_gates() > 0:
                self.current_program.add_circuit(self.current_circuit)
            
            return self.current_program
            
        except Exception as e:
            raise GulliverParseError(f"Failed to parse program: {str(e)}")
    
    def _preprocess_code(self, code: str) -> List[str]:
        """Preprocess Gulliver code for parsing."""
        lines = []
        
        # Remove comments and empty lines
        for line in code.split('\n'):
            line = line.strip()
            if line and not line.startswith('//'):
                # Remove inline comments
                if '//' in line:
                    line = line[:line.find('//')].strip()
                if line:
                    lines.append(line)
        
        return lines
    
    def _parse_line(self, line: str, line_num: int):
        """Parse a single line of Gulliver code."""
        line = line.strip()
        
        # Skip empty lines and braces
        if not line or line in ['{', '}']:
            return
        
        # Function definitions
        if line.startswith('def '):
            self._parse_function_definition(line)
        
        # Variable declarations
        elif self._is_variable_declaration(line):
            self._parse_variable_declaration(line)
        
        # Assignment statements (including quantum operations)
        elif '=' in line and not line.startswith('let '):
            self._parse_assignment(line)
        
        # Control flow
        elif line.startswith('if ') or line.startswith('for '):
            pass  # Skip control flow for now
        
        # Print statements
        elif line.startswith('print'):
            self._parse_print_statement(line)
        
        # Return statements
        elif line.startswith('return'):
            pass  # Skip return statements for now
    
    def _is_variable_declaration(self, line: str) -> bool:
        """Check if line is a variable declaration."""
        # Pattern: let variable: type = value;
        return (line.startswith('let ') and ':' in line) or \
               any(line.startswith(t + ' ') for t in ['int', 'float', 'bool'])
    
    def _parse_variable_declaration(self, line: str):
        """Parse variable declaration and create qubits/classical bits."""
        # Remove semicolon
        line = line.rstrip(';')
        
        # Extract variable info
        if line.startswith('let '):
            # Pattern: let varname: type = value
            parts = line[4:].split('=', 1)  # Split only on first =
            var_part = parts[0].strip()
            
            if ':' in var_part:
                var_name, var_type = var_part.split(':')
                var_name = var_name.strip()
                var_type = var_type.strip()
                
                # For quantum programming, most int variables are qubits
                if var_type == 'int':
                    if len(parts) > 1:
                        # Check if it's a quantum operation
                        value = parts[1].strip()
                        if self._is_quantum_expression(value) or value == '0':
                            # Create qubit (0 means |0⟩ state)
                            qubit = self.current_circuit.add_qubit(var_name)
                            self.variable_map[var_name] = qubit
                            
                            # Parse the quantum operation if present and not just initialization
                            if value != '0':
                                self._parse_quantum_assignment(var_name, value)
                        else:
                            # Classical variable
                            cbit = self.current_circuit.add_classical_bit(var_name)
                            self.variable_map[var_name] = cbit
                    else:
                        # Default int to qubit for quantum programming
                        qubit = self.current_circuit.add_qubit(var_name)
                        self.variable_map[var_name] = qubit
                else:
                    # Other types default to classical bit
                    cbit = self.current_circuit.add_classical_bit(var_name)
                    self.variable_map[var_name] = cbit
    
    def _parse_assignment(self, line: str):
        """Parse assignment statements (including quantum operations)."""
        line = line.rstrip(';')
        
        if '=' in line:
            parts = line.split('=', 1)  # Split only on first =
            if len(parts) == 2:
                var_name = parts[0].strip()
                operation = parts[1].strip()
                
                # Ensure variable exists as qubit
                if var_name not in self.variable_map:
                    qubit = self.current_circuit.add_qubit(var_name)
                    self.variable_map[var_name] = qubit
                
                # Parse the assignment value
                if self._is_quantum_expression(operation):
                    self._parse_quantum_assignment(var_name, operation)
                else:
                    # Handle classical assignment
                    pass
    
    def _is_quantum_expression(self, expr: str) -> bool:
        """Check if expression is a quantum operation."""
        expr = expr.strip()
        
        # Check for quantum gate calls
        for gate_name in self.gate_mappings.keys():
            if expr.startswith(f'{gate_name}('):
                return True
        
        return False
    
    def _parse_quantum_operation(self, line: str):
        """Parse quantum operation assignment."""
        line = line.rstrip(';')
        
        if '=' in line:
            parts = line.split('=', 1)  # Split only on first =
            if len(parts) == 2:
                var_name = parts[0].strip()
                operation = parts[1].strip()
                
                self._parse_quantum_assignment(var_name, operation)
    
    def _parse_quantum_assignment(self, var_name: str, operation: str):
        """Parse quantum gate assignment."""
        # Ensure variable exists
        if var_name not in self.variable_map:
            qubit = self.current_circuit.add_qubit(var_name)
            self.variable_map[var_name] = qubit
        
        target_var = self.variable_map[var_name]
        
        # Parse the operation
        if isinstance(target_var, Qubit):
            self._parse_gate_operation(operation, target_qubit=target_var)
    
    def _parse_gate_operation(self, operation: str, target_qubit: Qubit = None):
        """Parse individual gate operation."""
        # Extract gate name and arguments
        if '(' in operation and operation.endswith(')'):
            gate_name = operation[:operation.find('(')]
            args_str = operation[operation.find('(') + 1:-1]
            
            if gate_name in self.gate_mappings:
                gate_type = self.gate_mappings[gate_name]
                
                # Parse arguments
                args = [arg.strip() for arg in args_str.split(',') if arg.strip()]
                qubits = []
                parameters = []
                
                for arg in args:
                    if arg.replace('.', '').replace('-', '').isdigit():
                        # Numeric parameter
                        parameters.append(float(arg))
                    elif arg in self.variable_map and isinstance(self.variable_map[arg], Qubit):
                        # Qubit argument
                        qubits.append(self.variable_map[arg])
                    elif arg.isdigit():
                        # Create qubit with index
                        qubit_index = int(arg)
                        if qubit_index == 0:
                            # Qubit initialized to |0⟩
                            temp_qubit = self.current_circuit.add_qubit(f"temp_{len(self.variable_map)}")
                            qubits.append(temp_qubit)
                
                # Add target qubit if specified
                if target_qubit and target_qubit not in qubits:
                    qubits.insert(0, target_qubit)
                
                # Create and add gate
                if qubits:
                    self.current_circuit.add_gate(gate_type, qubits, parameters)
                    
                    # Handle measurement specially
                    if gate_type == GateType.MEASURE:
                        cbit = self.current_circuit.add_classical_bit(f"measure_{qubits[0].name}")
                        self.current_circuit.add_measurement(qubits[0], cbit)
    
    def _parse_function_definition(self, line: str):
        """Parse function definition (placeholder)."""
        # Extract function name
        if 'def ' in line and '(' in line:
            func_name = line[4:line.find('(')].strip()
            self.function_registry[func_name] = {'line': line}
    
    def _parse_print_statement(self, line: str):
        """Parse print statement (add as classical code)."""
        self.current_program.add_classical_code(line)
    
    def get_circuit_summary(self) -> Dict[str, Any]:
        """Get summary of the parsed circuit."""
        if not self.current_circuit:
            return {}
        
        return {
            'name': self.current_circuit.name,
            'qubits': self.current_circuit.get_num_qubits(),
            'gates': self.current_circuit.get_num_gates(),
            'depth': self.current_circuit.get_depth(),
            'variables': len(self.variable_map),
            'functions': len(self.function_registry)
        }

def parse_gulliver_file(file_path: str) -> ProgramIR:
    """
    Parse a Gulliver .gl file into IR.
    
    Args:
        file_path: Path to .gl file
        
    Returns:
        ProgramIR: Parsed program
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        parser = GulliverToIR()
        program_name = file_path.split('/')[-1].replace('.gl', '')
        return parser.parse_program(content, program_name)
        
    except FileNotFoundError:
        raise GulliverParseError(f"File not found: {file_path}")
    except Exception as e:
        raise GulliverParseError(f"Failed to parse file {file_path}: {str(e)}")

# Example usage and testing
if __name__ == "__main__":
    # Test simple Gulliver code
    test_code = """
    def main() -> void {
        let qubit: int = 0;
        qubit = had(qubit);
        let result: int = measure(qubit);
        print("Result: ", result);
    }
    """
    
    parser = GulliverToIR()
    try:
        program = parser.parse_program(test_code, "test")
        print("Parse successful!")
        print(f"Program: {program}")
        print(f"Summary: {parser.get_circuit_summary()}")
    except GulliverParseError as e:
        print(f"Parse error: {e}")