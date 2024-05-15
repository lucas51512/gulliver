import unittests
from lexer.lexer import lexer

class TestLexer(unittests.TestCase):

    def test_tokens(self):
        data = 'int x = 10;'
        lexer.input(data)
        tokens = [token.type for token in lexer]
        expected_tokens = ['INT', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'SEMICOLON']
        self.assertEqual(tokens, expected_tokens)

if __name__ == '__main__':
    unittests.main()