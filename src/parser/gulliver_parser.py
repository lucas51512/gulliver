import ply.yacc as yacc
from src.lexer.tokens import Tokens

class GulliverParser:
    def __init__(self):
        self.parser = yacc.yacc(module=self)

    # Definição da gramática da linguagem Gulliver
    def p_programa(self, p):
        '''programa : MAIN LBRACE corpo RBRACE'''

    def p_corpo(self, p):
        '''corpo : comando
                 | corpo comando'''

    def p_comando(self, p):
        '''comando : declaracao
                   | condicional
                   | expressao
                   | funcao'''

    def p_declaracao(self, p):
        '''declaracao : tipo IDENTIFIER SEMICOLON
                      | tipo IDENTIFIER ASSIGN expressao SEMICOLON'''

    def p_tipo(self, p):
        '''tipo : INT
                | STRING
                | BOOL
                | FLOAT
                | COMPLEX
                | DOUBLE'''

    def p_condicional(self, p):
        '''condicional : IF LPAREN expressao RPAREN LBRACE corpo RBRACE
                       | IF LPAREN expressao RPAREN LBRACE corpo RBRACE ELSE LBRACE corpo RBRACE'''

    def p_expressao(self, p):
        '''expressao : NUMBER
                     | IDENTIFIER
                     | expressao PLUS expressao
                     | expressao MINUS expressao
                     | expressao TIMES expressao
                     | expressao DIVIDE expressao'''

    def p_funcao(self, p):
        '''funcao : DEF IDENTIFIER LPAREN parametro RPAREN LBRACE corpo RBRACE'''

    def p_parametro(self, p):
        '''parametro : tipo IDENTIFIER
                     | parametro COMMA tipo IDENTIFIER'''

    def p_error(self, p):
        print("Erro de sintaxe")

    def parse(self, data):
        return self.parser.parse(data)
