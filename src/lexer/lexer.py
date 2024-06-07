# lexer.py
import ply.lex as lex
from .tokens import Tokens

class Lexer:
    def __init__(self):
        self.lexer = lex.lex(module=Tokens)

    def input(self, data):
        self.lexer.input(data)

    def token(self):
        return self.lexer.token()

    def tokenize(self, data):
        self.input(data)
        tokens = []
        while True:
            tok = self.token()
            if not tok:
                break
            tokens.append(tok)
        return tokens
