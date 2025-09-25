import unittest
from src.lexer.lexer import Lexer

class TestLexer(unittest.TestCase):

    def test_tokens(self):
        """Test basic tokenization."""
        data = 'int x = 10;'
        lexer = Lexer()
        tokens = [token.type for token in lexer.tokenize(data)]
        expected_tokens = ['INT', 'IDENTIFIER', 'ASSIGN', 'NUMBER', 'SEMICOLON']
        self.assertEqual(tokens, expected_tokens)
    
    def test_quantum_tokens(self):
        """Test quantum gate tokenization."""
        data = 'let q: int = had(0);'
        lexer = Lexer()
        tokens = [token.type for token in lexer.tokenize(data)]
        # Should tokenize: let q : int = had ( 0 ) ;
        expected_types = ['IDENTIFIER', 'IDENTIFIER', 'COLON', 'INT', 'ASSIGN', 'IDENTIFIER', 'LPAREN', 'NUMBER', 'RPAREN', 'SEMICOLON']
        self.assertEqual(tokens, expected_types)
    
    def test_gulliver_language_support(self):
        """Test that lexer supports .gl files (Gulliver Language)."""
        # This is a symbolic test - actual file handling is in the parser
        gulliver_code = '''
        def main() -> void {
            let qubit: int = 0;
            qubit = had(qubit);
        }
        '''
        lexer = Lexer()
        tokens = lexer.tokenize(gulliver_code)
        
        # Should have DEF, MAIN, and quantum gate tokens
        token_types = [token.type for token in tokens]
        self.assertIn('DEF', token_types)
        self.assertIn('MAIN', token_types)
        self.assertIn('IDENTIFIER', token_types)  # 'had' should be an identifier
        
        # Count tokens - should have a reasonable number
        self.assertGreater(len(tokens), 10)

if __name__ == '__main__':
    unittest.main()