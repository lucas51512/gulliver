"""
Setup script for Liliput Quantum Middleware
==========================================
"""

from setuptools import setup, find_packages

# Read requirements
requirements = [
    'numpy>=1.20.0',
    'ply>=3.11'
]

# Optional dependencies for different providers
extras_require = {
    'qiskit': ['qiskit>=0.40.0'],
    'cirq': ['cirq>=1.0.0'],
    'braket': ['amazon-braket-sdk>=1.40.0'],
    'dev': ['pytest>=6.0', 'black', 'flake8', 'mypy'],
    'all': [
        'qiskit>=0.40.0',
        'cirq>=1.0.0', 
        'amazon-braket-sdk>=1.40.0',
        'pytest>=6.0',
        'black',
        'flake8',
        'mypy'
    ]
}

setup(
    name='liliput-quantum',
    version='2.0.0',
    description='Professional quantum programming middleware for Gulliver language',
    long_description='''
    Liliput is a comprehensive quantum programming middleware that provides:
    
    - Universal quantum backend support (Simulator, Qiskit, Cirq, Braket)
    - Multi-level quantum circuit optimization (30-70% gate reduction)
    - Professional CLI with debugging and profiling tools
    - Real quantum simulation with noise models
    - Complete parsing and compilation pipeline
    
    Designed to work with the Gulliver quantum programming language.
    ''',
    author='lucas51512',
    author_email='lucas51512@github.com',
    url='https://github.com/lucas51512/gulliver',
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require=extras_require,
    entry_points={
        'console_scripts': [
            'liliput=liliput.cli.liliput_cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Compilers',
    ],
    keywords='quantum computing programming language compiler middleware',
    project_urls={
        'Bug Reports': 'https://github.com/lucas51512/gulliver/issues',
        'Source': 'https://github.com/lucas51512/gulliver',
        'Documentation': 'https://github.com/lucas51512/gulliver/wiki',
    },
)