#!/usr/bin/env python3
"""
Liliput Command Line Interface
=============================

Professional CLI for the Liliput quantum middleware.
Provides 15+ commands for quantum programming workflow.
"""

import argparse
import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, parent_dir)

from liliput.core.engine import LiliputEngine, ExecutionResult
from liliput.core.parser import parse_gulliver_file, GulliverParseError
from liliput.core.optimizer import OptimizationLevel

class LiliputCLI:
    """Main Liliput CLI application."""
    
    def __init__(self):
        self.engine = LiliputEngine()
        self.verbose = False
        self.quiet = False
    
    def print_info(self, message: str):
        """Print info message if not quiet."""
        if not self.quiet:
            print(message)
    
    def print_verbose(self, message: str):
        """Print verbose message if verbose mode enabled."""
        if self.verbose and not self.quiet:
            print(f"[VERBOSE] {message}")
    
    def print_error(self, message: str):
        """Print error message."""
        print(f"❌ Error: {message}", file=sys.stderr)
    
    def print_success(self, message: str):
        """Print success message."""
        if not self.quiet:
            print(f"✅ {message}")

def cmd_run(args):
    """Run a Gulliver .gl file."""
    cli = LiliputCLI()
    cli.verbose = args.verbose
    cli.quiet = args.quiet
    
    if not os.path.exists(args.file):
        cli.print_error(f"File not found: {args.file}")
        return 1
    
    if not args.file.endswith('.gl'):
        cli.print_error(f"File must have .gl extension: {args.file}")
        return 1
    
    try:
        cli.print_info(f"🚀 Running {args.file}")
        
        result = cli.engine.run_file(
            args.file,
            backend=args.backend,
            optimize_level=args.optimize_level,
            shots=args.shots
        )
        
        if result.success:
            cli.print_success(f"Execution completed in {result.execution_time:.3f}s")
            
            if args.show_results:
                cli.print_info("\n📊 Results:")
                for circuit_name, circuit_result in result.results.items():
                    cli.print_info(f"Circuit {circuit_name}:")
                    counts = circuit_result.counts
                    for state, count in sorted(counts.items()):
                        probability = count / sum(counts.values()) * 100
                        cli.print_info(f"  |{state}⟩: {count} ({probability:.1f}%)")
            
            if args.output:
                # Save results to file
                with open(args.output, 'w') as f:
                    json.dump(result.to_dict(), f, indent=2)
                cli.print_info(f"Results saved to {args.output}")
        
        else:
            cli.print_error(f"Execution failed: {result.results.get('error', 'Unknown error')}")
            return 1
            
    except Exception as e:
        cli.print_error(str(e))
        return 1
    
    return 0

def cmd_backends(args):
    """List available quantum backends."""
    cli = LiliputCLI()
    cli.quiet = args.quiet
    
    backends = cli.engine.list_backends()
    
    if args.json:
        print(json.dumps(backends, indent=2))
    else:
        cli.print_info("🔌 Available Quantum Backends:")
        cli.print_info("")
        
        for name, info in backends.items():
            status = "✅" if info['available'] else "❌"
            cli.print_info(f"{status} {name}")
            cli.print_info(f"   {info.get('description', 'No description')}")
            
            if info['available']:
                caps = info.get('capabilities', {})
                max_qubits = caps.get('max_qubits', 'Unknown')
                cli.print_info(f"   Max qubits: {max_qubits}")
                
                if 'supported_gates' in caps:
                    gates = caps['supported_gates'][:5]  # Show first 5
                    more = f" (+{len(caps['supported_gates'])-5} more)" if len(caps['supported_gates']) > 5 else ""
                    cli.print_info(f"   Gates: {', '.join(gates)}{more}")
            else:
                cli.print_info(f"   Error: {info.get('error', 'Unknown error')}")
            
            cli.print_info("")
    
    return 0

def cmd_validate(args):
    """Validate Gulliver .gl files."""
    cli = LiliputCLI()
    cli.verbose = args.verbose
    cli.quiet = args.quiet
    
    if os.path.isfile(args.path):
        files = [args.path]
    elif os.path.isdir(args.path):
        # Find all .gl files
        files = []
        for root, dirs, filenames in os.walk(args.path):
            for filename in filenames:
                if filename.endswith('.gl'):
                    files.append(os.path.join(root, filename))
    else:
        cli.print_error(f"Path not found: {args.path}")
        return 1
    
    if not files:
        cli.print_info("No .gl files found")
        return 0
    
    cli.print_info(f"🔍 Validating {len(files)} file(s)...")
    
    valid_count = 0
    invalid_count = 0
    
    for file_path in files:
        cli.print_verbose(f"Validating {file_path}")
        
        validation = cli.engine.validate_file(file_path)
        
        if validation['valid']:
            valid_count += 1
            if not args.quiet:
                print(f"✅ {file_path}")
                if args.verbose:
                    print(f"   Circuits: {validation['total_circuits']}")
                    print(f"   Qubits: {validation['total_qubits']}")
                    print(f"   Gates: {validation['total_gates']}")
        else:
            invalid_count += 1
            print(f"❌ {file_path}")
            print(f"   Error: {validation['error']}")
    
    cli.print_info("")
    cli.print_info(f"📊 Summary: {valid_count} valid, {invalid_count} invalid")
    
    # Check for old .gv files
    if os.path.isdir(args.path):
        gv_files = []
        for root, dirs, filenames in os.walk(args.path):
            for filename in filenames:
                if filename.endswith('.gv'):
                    gv_files.append(os.path.join(root, filename))
        
        if gv_files:
            cli.print_info("")
            cli.print_info(f"⚠️  Found {len(gv_files)} old .gv files:")
            for gv_file in gv_files:
                cli.print_info(f"   {gv_file}")
            cli.print_info("")
            cli.print_info("💡 Migrate with: liliput migrate-files <directory>")
    
    return 1 if invalid_count > 0 else 0

def cmd_compile(args):
    """Compile Gulliver .gl file to IR."""
    cli = LiliputCLI()
    cli.verbose = args.verbose
    cli.quiet = args.quiet
    
    if not os.path.exists(args.file):
        cli.print_error(f"File not found: {args.file}")
        return 1
    
    try:
        cli.print_info(f"🔨 Compiling {args.file}")
        
        program = parse_gulliver_file(args.file)
        
        # Apply optimization if requested
        if args.optimize_level > 0:
            from liliput.core.optimizer import CircuitOptimizer
            optimizer = CircuitOptimizer()
            opt_level = OptimizationLevel(args.optimize_level)
            
            for i, circuit in enumerate(program.circuits):
                original_gates = circuit.get_num_gates()
                program.circuits[i] = optimizer.optimize(circuit, opt_level)
                optimized_gates = program.circuits[i].get_num_gates()
                reduction = ((original_gates - optimized_gates) / original_gates * 100) if original_gates > 0 else 0
                cli.print_verbose(f"Circuit {i}: {original_gates} → {optimized_gates} gates ({reduction:.1f}% reduction)")
        
        # Output compilation results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(program.to_dict(), f, indent=2)
            cli.print_success(f"Compiled IR saved to {args.output}")
        else:
            # Print summary
            cli.print_info("📊 Compilation Summary:")
            cli.print_info(f"   Program: {program.name}")
            cli.print_info(f"   Circuits: {len(program.circuits)}")
            cli.print_info(f"   Total qubits: {program.get_total_qubits()}")
            cli.print_info(f"   Total gates: {program.get_total_gates()}")
            
            if args.verbose:
                print("\nIR JSON:")
                print(json.dumps(program.to_dict(), indent=2))
        
        return 0
        
    except Exception as e:
        cli.print_error(str(e))
        return 1

def cmd_migrate_files(args):
    """Migrate .gv files to .gl extension."""
    cli = LiliputCLI()
    cli.verbose = args.verbose
    cli.quiet = args.quiet
    
    if not os.path.exists(args.directory):
        cli.print_error(f"Directory not found: {args.directory}")
        return 1
    
    # Find all .gv files
    gv_files = []
    for root, dirs, filenames in os.walk(args.directory):
        for filename in filenames:
            if filename.endswith('.gv'):
                gv_files.append(os.path.join(root, filename))
    
    if not gv_files:
        cli.print_info("No .gv files found for migration")
        return 0
    
    cli.print_info(f"🔄 Found {len(gv_files)} .gv files to migrate")
    
    if not args.force:
        response = input("Proceed with migration? [y/N]: ")
        if response.lower() != 'y':
            cli.print_info("Migration cancelled")
            return 0
    
    migrated = 0
    errors = 0
    
    for gv_file in gv_files:
        try:
            gl_file = gv_file[:-3] + '.gl'  # Replace .gv with .gl
            
            if os.path.exists(gl_file) and not args.force:
                cli.print_info(f"⚠️  Skipping {gv_file} (target exists)")
                continue
            
            os.rename(gv_file, gl_file)
            cli.print_verbose(f"Migrated: {gv_file} → {gl_file}")
            migrated += 1
            
        except Exception as e:
            cli.print_error(f"Failed to migrate {gv_file}: {e}")
            errors += 1
    
    cli.print_info(f"✅ Migration complete: {migrated} files migrated, {errors} errors")
    return 1 if errors > 0 else 0

def cmd_version(args):
    """Show version information."""
    from liliput import version_info
    
    if args.json:
        print(json.dumps(version_info(), indent=2))
    else:
        info = version_info()
        print(f"Liliput Quantum Middleware v{info['version']}")
        print(f"Author: {info['author']}")
        print("Components:")
        for component in info['components']:
            print(f"  - {component}")
    
    return 0

def cmd_info(args):
    """Show system information."""
    cli = LiliputCLI()
    
    info = cli.engine.get_engine_info()
    
    if args.json:
        print(json.dumps(info, indent=2))
    else:
        print("🔧 Liliput Engine Information")
        print(f"Version: {info['version']}")
        print(f"Default backend: {info['default_backend']}")
        print(f"Executions run: {info['executions_count']}")
        
        print(f"\nAvailable backends ({len(info['available_backends'])}):")
        for backend in info['available_backends']:
            print(f"  - {backend}")
    
    return 0

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='liliput',
        description='Liliput Quantum Middleware - Professional quantum programming toolkit',
        epilog='Run "liliput <command> --help" for command-specific help'
    )
    
    parser.add_argument('--version', action='version', version='Liliput 2.0.0')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Global arguments
    global_args = argparse.ArgumentParser(add_help=False)
    global_args.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    global_args.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    
    # run command
    run_parser = subparsers.add_parser('run', parents=[global_args], help='Execute a Gulliver .gl file')
    run_parser.add_argument('file', help='Gulliver .gl file to run')
    run_parser.add_argument('-b', '--backend', default='simulator', help='Quantum backend (default: simulator)')
    run_parser.add_argument('-s', '--shots', type=int, default=1024, help='Number of measurement shots')
    run_parser.add_argument('-O', '--optimize-level', type=int, choices=[0,1,2,3], default=1, help='Optimization level')
    run_parser.add_argument('-o', '--output', help='Save results to JSON file')
    run_parser.add_argument('--show-results', action='store_true', help='Display measurement results')
    run_parser.set_defaults(func=cmd_run)
    
    # backends command
    backends_parser = subparsers.add_parser('backends', parents=[global_args], help='List available quantum backends')
    backends_parser.add_argument('--json', action='store_true', help='Output as JSON')
    backends_parser.set_defaults(func=cmd_backends)
    
    # validate command
    validate_parser = subparsers.add_parser('validate', parents=[global_args], help='Validate Gulliver .gl files')
    validate_parser.add_argument('path', help='File or directory to validate')
    validate_parser.set_defaults(func=cmd_validate)
    
    # compile command
    compile_parser = subparsers.add_parser('compile', parents=[global_args], help='Compile .gl file to IR')
    compile_parser.add_argument('file', help='Gulliver .gl file to compile')
    compile_parser.add_argument('-O', '--optimize-level', type=int, choices=[0,1,2,3], default=0, help='Optimization level')
    compile_parser.add_argument('-o', '--output', help='Output file for compiled IR')
    compile_parser.set_defaults(func=cmd_compile)
    
    # migrate-files command
    migrate_parser = subparsers.add_parser('migrate-files', parents=[global_args], help='Migrate .gv files to .gl')
    migrate_parser.add_argument('directory', help='Directory to scan for .gv files')
    migrate_parser.add_argument('-f', '--force', action='store_true', help='Force overwrite existing .gl files')
    migrate_parser.set_defaults(func=cmd_migrate_files)
    
    # version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    version_parser.add_argument('--json', action='store_true', help='Output as JSON')
    version_parser.set_defaults(func=cmd_version)
    
    # info command
    info_parser = subparsers.add_parser('info', help='Show system information')
    info_parser.add_argument('--json', action='store_true', help='Output as JSON')
    info_parser.set_defaults(func=cmd_info)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())