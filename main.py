# main.py - Gulliver 2.0 Language Demo
# Now supports .gl file extension (Gulliver Language)
from src.lexer.lexer import Lexer

if __name__ == "__main__":
    # Sample Gulliver (.gl) quantum algorithm code - Grover's search
    data = """
    def main() -> void {
        def invertBits(register: int) -> int {
            return x(register);
        }

        def average(register: int, n: int) -> int {
            return ((2 * register) - n) * -1;
        }

        def searchElement(vector: int[], element: int) -> int {
            let n: int = size(vector);
            let iterations: int = round(sqrt(n));
            let register: int = 0; 

            for (let i: int = 0; i < n; i = i + 1) {
                register = had(register);
            }

            for (let i: int = 0; i < iterations; i = i + 1) {
                register = invertBits(register);

                register = average(register, n);
            }

            return register;
        }

        let vetor: int[5] = [3, 7, 2, 8, 5];
        let elementoDesejado: int = 8;

        let indiceEncontrado: int = searchElement(vetor, elementoDesejado);

        print("O índice do elemento ", elementoDesejado, " é ", indiceEncontrado);
    }
    """

    print("=== GULLIVER 2.0 LANGUAGE LEXER DEMO ===")
    print("File extension: .gl (Gulliver Language)")
    print("Parsing quantum algorithm code...\n")

    lexer = Lexer()
    tokens = lexer.tokenize(data)

    print(f"Generated {len(tokens)} tokens:")
    for i, token in enumerate(tokens):
        if i < 20:  # Show first 20 tokens
            print(f"{i+1:2d}: {token}")
        elif i == 20:
            print("... (truncated, showing first 20 tokens)")
            break
    
    print(f"\n=== Lexical analysis complete ===")
    print("✅ Gulliver 2.0 ready for quantum programming!")
    print("💡 Try running: liliput run examples/grover.gl")
