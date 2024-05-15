import ply.lex as lex
import ply.yacc as yacc

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