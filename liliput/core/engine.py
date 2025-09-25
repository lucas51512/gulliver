"""
Liliput Quantum Engine
=====================

The main execution engine for Liliput middleware.
Coordinates parsing, compilation, optimization, and execution.
"""

from typing import Dict, List, Any, Optional, Union
import os
import json
from pathlib import Path

from .parser import GulliverToIR, parse_gulliver_file, GulliverParseError
from .compiler import QuantumCompiler, CompilationError
from .optimizer import CircuitOptimizer, OptimizationLevel
from .ir import ProgramIR, QuantumCircuitIR
from ..providers.base import QuantumProvider
from ..providers.simulator import SimulatorProvider

class LiliputEngineError(Exception):
    """Exception raised by the Liliput engine."""
    pass

class ExecutionResult:
    """Container for execution results."""
    
    def __init__(self, success: bool, results: Dict[str, Any], 
                 execution_time: float, metadata: Dict[str, Any] = None):
        self.success = success
        self.results = results
        self.execution_time = execution_time
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'success': self.success,
            'results': self.results,
            'execution_time': self.execution_time,
            'metadata': self.metadata
        }

class LiliputEngine:
    """
    Main Liliput quantum programming engine.
    
    Provides a high-level interface for:
    - Parsing Gulliver code
    - Compiling to backend-specific formats
    - Optimizing quantum circuits
    - Executing on various quantum backends
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the Liliput engine.
        
        Args:
            config: Configuration dictionary
        """
        self.config = config or {}
        self.parser = GulliverToIR()
        self.compiler = QuantumCompiler()
        self.optimizer = CircuitOptimizer()
        
        # Provider registry
        self.providers: Dict[str, QuantumProvider] = {}
        self.default_provider = "simulator"
        
        # Initialize default simulator provider
        self._initialize_providers()
        
        # Execution history
        self.execution_history: List[ExecutionResult] = []
    
    def _initialize_providers(self):
        """Initialize available quantum providers."""
        # Always available: local simulator
        self.providers["simulator"] = SimulatorProvider()
        
        # Try to initialize other providers
        try:
            from ..providers.qiskit_provider import QiskitProvider
            self.providers["qiskit"] = QiskitProvider()
        except ImportError:
            pass
        
        try:
            from ..providers.cirq_provider import CirqProvider
            self.providers["cirq"] = CirqProvider()
        except ImportError:
            pass
        
        try:
            from ..providers.braket_provider import BraketProvider
            self.providers["braket"] = BraketProvider()
        except ImportError:
            pass
    
    def list_backends(self) -> Dict[str, Dict[str, Any]]:
        """List all available quantum backends."""
        backends = {}
        
        for name, provider in self.providers.items():
            try:
                backends[name] = {
                    'available': True,
                    'description': provider.get_description(),
                    'capabilities': provider.get_capabilities(),
                    'devices': provider.list_devices() if hasattr(provider, 'list_devices') else []
                }
            except Exception as e:
                backends[name] = {
                    'available': False,
                    'error': str(e)
                }
        
        return backends
    
    def run_file(self, file_path: str, backend: str = None, 
                 optimize_level: int = 1, **kwargs) -> ExecutionResult:
        """
        Run a Gulliver .gl file.
        
        Args:
            file_path: Path to .gl file
            backend: Quantum backend to use
            optimize_level: Optimization level (0-3)
            **kwargs: Additional execution parameters
            
        Returns:
            ExecutionResult: Execution results
        """
        import time
        start_time = time.time()
        
        try:
            # Validate file
            if not os.path.exists(file_path):
                raise LiliputEngineError(f"File not found: {file_path}")
            
            if not file_path.endswith('.gl'):
                raise LiliputEngineError(f"File must have .gl extension: {file_path}")
            
            # Parse the file
            print(f"📝 Parsing {file_path}...")
            program = parse_gulliver_file(file_path)
            
            # Execute the program
            result = self.run_program(program, backend, optimize_level, **kwargs)
            
            execution_time = time.time() - start_time
            result.execution_time = execution_time
            
            # Add to history
            self.execution_history.append(result)
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_result = ExecutionResult(
                success=False,
                results={'error': str(e)},
                execution_time=execution_time,
                metadata={'file_path': file_path}
            )
            self.execution_history.append(error_result)
            return error_result
    
    def run_program(self, program: ProgramIR, backend: str = None,
                    optimize_level: int = 1, **kwargs) -> ExecutionResult:
        """
        Run a parsed Gulliver program.
        
        Args:
            program: Parsed program IR
            backend: Quantum backend to use  
            optimize_level: Optimization level (0-3)
            **kwargs: Additional execution parameters
            
        Returns:
            ExecutionResult: Execution results
        """
        import time
        start_time = time.time()
        
        try:
            backend = backend or self.default_provider
            
            if backend not in self.providers:
                raise LiliputEngineError(f"Backend '{backend}' not available. Use: {list(self.providers.keys())}")
            
            provider = self.providers[backend]
            
            print(f"🚀 Executing program '{program.name}' on backend '{backend}'")
            print(f"📊 Program stats: {len(program.circuits)} circuits, {program.get_total_qubits()} qubits, {program.get_total_gates()} gates")
            
            # Process each circuit
            all_results = {}
            
            for i, circuit in enumerate(program.circuits):
                print(f"⚡ Processing circuit {i+1}/{len(program.circuits)}: {circuit.name}")
                
                # Optimize if requested
                if optimize_level > 0:
                    print(f"🔧 Optimizing circuit (level {optimize_level})...")
                    opt_level = OptimizationLevel(optimize_level)
                    original_gates = circuit.get_num_gates()
                    optimized_circuit = self.optimizer.optimize(circuit, opt_level)
                    reduction = ((original_gates - optimized_circuit.get_num_gates()) / original_gates * 100) if original_gates > 0 else 0
                    print(f"✨ Optimization complete: {original_gates} → {optimized_circuit.get_num_gates()} gates ({reduction:.1f}% reduction)")
                    circuit = optimized_circuit
                
                # Compile for backend
                print(f"🔨 Compiling for backend '{backend}'...")
                compiled_circuit = self.compiler.compile(circuit, provider)
                
                # Execute
                print(f"⚡ Executing circuit...")
                circuit_result = provider.execute(compiled_circuit, **kwargs)
                all_results[f"circuit_{i}"] = circuit_result
            
            execution_time = time.time() - start_time
            
            result = ExecutionResult(
                success=True,
                results=all_results,
                execution_time=execution_time,
                metadata={
                    'program_name': program.name,
                    'backend': backend,
                    'optimization_level': optimize_level,
                    'total_circuits': len(program.circuits),
                    'total_qubits': program.get_total_qubits(),
                    'total_gates': program.get_total_gates()
                }
            )
            
            print(f"✅ Execution complete in {execution_time:.3f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            print(f"❌ Execution failed: {str(e)}")
            
            return ExecutionResult(
                success=False,
                results={'error': str(e)},
                execution_time=execution_time,
                metadata={'program_name': program.name if program else 'unknown'}
            )
    
    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """
        Validate a Gulliver .gl file without executing.
        
        Args:
            file_path: Path to .gl file
            
        Returns:
            Dict with validation results
        """
        try:
            # Check file existence and extension
            if not os.path.exists(file_path):
                return {'valid': False, 'error': f'File not found: {file_path}'}
            
            if not file_path.endswith('.gl'):
                return {'valid': False, 'error': f'File must have .gl extension: {file_path}'}
            
            # Try to parse
            program = parse_gulliver_file(file_path)
            
            # Validate circuits
            validation_results = []
            for circuit in program.circuits:
                circuit_validation = {
                    'name': circuit.name,
                    'qubits': circuit.get_num_qubits(),
                    'gates': circuit.get_num_gates(),
                    'depth': circuit.get_depth(),
                    'valid': True
                }
                
                # Basic validation checks
                if circuit.get_num_qubits() == 0:
                    circuit_validation['warnings'] = ['No qubits defined']
                
                if circuit.get_num_gates() == 0:
                    circuit_validation['warnings'] = circuit_validation.get('warnings', []) + ['No gates defined']
                
                validation_results.append(circuit_validation)
            
            return {
                'valid': True,
                'program_name': program.name,
                'total_circuits': len(program.circuits),
                'total_qubits': program.get_total_qubits(),
                'total_gates': program.get_total_gates(),
                'circuits': validation_results
            }
            
        except Exception as e:
            return {'valid': False, 'error': str(e)}
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get execution history."""
        return [result.to_dict() for result in self.execution_history]
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get engine information."""
        return {
            'version': '2.0.0',
            'available_backends': list(self.providers.keys()),
            'default_backend': self.default_provider,
            'executions_count': len(self.execution_history),
            'config': self.config
        }

# Convenience functions
def create_engine(config: Dict[str, Any] = None) -> LiliputEngine:
    """Create a new Liliput engine instance."""
    return LiliputEngine(config)

def run_gulliver_file(file_path: str, backend: str = "simulator", 
                      optimize_level: int = 1, **kwargs) -> ExecutionResult:
    """
    Quick function to run a Gulliver file.
    
    Args:
        file_path: Path to .gl file
        backend: Quantum backend
        optimize_level: Optimization level
        **kwargs: Additional parameters
        
    Returns:
        ExecutionResult: Results
    """
    engine = create_engine()
    return engine.run_file(file_path, backend, optimize_level, **kwargs)

# Example usage
if __name__ == "__main__":
    # Test the engine
    engine = create_engine()
    
    print("=== Liliput Engine Test ===")
    print(f"Engine info: {engine.get_engine_info()}")
    print(f"Available backends: {list(engine.list_backends().keys())}")
    
    # Test simple program
    test_code = """
    def main() -> void {
        let qubit: int = 0;
        qubit = had(qubit);
        let result: int = measure(qubit);
    }
    """
    
    parser = GulliverToIR()
    try:
        program = parser.parse_program(test_code, "test")
        result = engine.run_program(program)
        print(f"Test execution result: {result.success}")
    except Exception as e:
        print(f"Test failed: {e}")