import ply.yacc as yacc
from lexer.lexer import tokens

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