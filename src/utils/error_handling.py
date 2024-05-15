def handle_lexical_error(token):
    print(f"Lexical error at line {token.lineno}: {token.value}")

def handle_syntax_error(p):
    if p:
        print(f"Syntax error at line {p.lineno}: {p.value}")
    else:
        print("Syntax error at EOF")