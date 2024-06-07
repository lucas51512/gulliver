# main.py
from src.lexer.lexer import Lexer

if __name__ == "__main__":
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

    lexer = Lexer()
    tokens = lexer.tokenize(data)

    for token in tokens:
        print(token)
