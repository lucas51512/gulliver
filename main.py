import ply.lex as lex
import ply.yacc as yacc

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

t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_QUOTE = r'\''
t_SEMICOLON = r';'
t_ignore = ' \t'
t_ASSIGN = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'*'
t_COMMA = r','

def t_identifier(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENTIFIER')
    return t

def t_number(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Caracter inválido: '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()

# Definição da gramática da linguagem Gulliver

def p_programa(p):
    '''programa : MAIN LBRACE corpo RBRACE'''

def p_corpo(p):
    '''corpo : comando
             | corpo comando'''

def p_comando(p):
    '''comando : declaracao
               | condicional
               | expressao
               | funcao'''

def p_declaracao(p):
    '''declaracao : tipo IDENTIFIER SEMICOLON
                  | tipo IDENTIFIER ASSIGN expressao SEMICOLON'''

def p_tipo(p):
    '''tipo : INT
            | STRING
            | BOOL
            | FLOAT
            | COMPLEX
            | DOUBLE'''

def p_condicional(p):
    '''condicional : IF LPAREN expressao RPAREN LBRACE corpo RBRACE
                   | IF LPAREN expressao RPAREN LBRACE corpo RBRACE ELSE LBRACE corpo RBRACE'''

def p_expressao(p):
    '''expressao : NUMBER
                 | IDENTIFIER
                 | expressao PLUS expressao
                 | expressao MINUS expressao
                 | expressao TIMES expressao
                 | expressao DIVIDE expressao'''

def p_funcao(p):
    '''funcao : DEF IDENTIFIER LPAREN parametro RPAREN LBRACE corpo RBRACE'''

def p_parametro(p):
    '''parametro : tipo IDENTIFIER
                 | parametro COMMA tipo IDENTIFIER'''

def p_error(p):
    print("Erro de sintaxe")

parser = yacc.yacc()
