# Palavras reservadas e tokens.
reserved = {
    'int': 'INT',
    'string': 'STRING',
    'bool': 'BOOL',
    'float': 'FLOAT',
    'def': 'DEF',
    'function': 'FUNCTION',
    'if': 'IF',
    'else': 'ELSE',
    'print': 'PRINT',
    'main': 'MAIN',
    'read': 'READ',
    'complex': 'COMPLEX',
    'double': 'DOUBLE'
}

tokens = [
    'IDENTIFIER',
    'NUMBER',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'QUOTE',
    'SEMICOLON',
    'ASSIGN',
    'PLUS',
    'MINUS',
    'TIMES',
    'COMMA'
] + list(reserved.values())