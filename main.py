from lexer.lexer import lexer
from parser.parser import parser

def main():
    with open('source.gll', 'r') as file:
        data = file.read()
    lexer.input(data)
    for token in lexer:
        print(token)

    result = parser.parse(data)
    print(result)

if __name__ == '__main__':
    main()