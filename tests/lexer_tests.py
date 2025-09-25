import unittest
from src.lexer.lexer import Lexer

class TestLexer(unittest.TestCase):

    def test_tokens(self):
        data = 'int x = 10;'
        lexer = Lexer()
        tokens = [token.type for token in lexer.tokenize(data)]
        expected_tokens = ['INT', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'SEMICOLON']
        self.assertEqual(tokens, expected_tokens)

if __name__ == '__main__':
    unittest.main()