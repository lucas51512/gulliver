import ply.lex as lex

class Tokens:
    reserved = {
        'int': 'INT',
        'string': 'STRING',
        'bool': 'BOOL',
        'float': 'FLOAT',
        'def': 'DEF',
        'function': 'FUNCTION',
        'if': 'IF',
        'else': 'ELSE',
        'print': 'PRINT',
        'main': 'MAIN',
        'read': 'READ',
        'complex': 'COMPLEX',
        'double': 'DOUBLE'
    }

    tokens = [
        'IDENTIFIER',
        'NUMBER',
        'LPAREN',
        'RPAREN',
        'LBRACE',
        'RBRACE',
        'QUOTE',
        'SEMICOLON',
        'ASSIGN',
        'PLUS',
        'MINUS',
        'TIMES',
        'COMMA',
        'LSQB',
        'RSQB',
        'COLON',
        'STAR',
        'SLASH',
        'VBAR',
        'LESS',
        'GREATER',
        'EQUAL',
        'DOT',
        'NOTEQUAL',
        'EQEQUAL',
        'LESSEREQUAL',
        'GREATEREQUAL',
        'TILDE',
        'CIRCUMPLEX',
        'RIGHTSHIFT',
        'PLUSEQUAL',
        'MINEQUAL',
        'DOUBLESTAR',
        'STAREQUAL',
        'SLASHEQUAL',
        'PERCENTEQUAL',
        'AT',
        'ATEEQUAL',
        'RARROW',
        'ELLIPSIS',
        'COLONEQUAL',
        'EXCLAMATION',
        'STRING'
    ] + list(reserved.values())

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_QUOTE = r'\''
    t_SEMICOLON = r';'
    t_ignore = ' \t'
    t_ASSIGN = r'='
    t_PLUS = r'\+'
    t_MINUS = r'-'
    t_TIMES = r'\*'
    t_COMMA = r','
    t_LSQB = r'\['
    t_RSQB = r'\]'
    t_COLON = r':'
    t_STAR = r'\*'
    t_SLASH = r'/'
    t_VBAR = r'\|'
    t_LESS = r'<'
    t_GREATER = r'>'
    t_EQUAL = r'='
    t_DOT = r'\.'
    t_NOTEQUAL = r'!='
    t_EQEQUAL = r'=='
    t_LESSEREQUAL = r'<='
    t_GREATEREQUAL = r'>='
    t_TILDE = r'~'
    t_CIRCUMPLEX = r'\^'
    t_RIGHTSHIFT = r'>>'
    t_PLUSEQUAL = r'\+='
    t_MINEQUAL = r'-='
    t_DOUBLESTAR = r'\*\*'
    t_STAREQUAL = r'\*='
    t_SLASHEQUAL = r'/='
    t_PERCENTEQUAL = r'%='
    t_AT = r'@'
    t_ATEEQUAL = r'@='
    t_RARROW = r'->'
    t_ELLIPSIS = r'\.\.\.'
    t_COLONEQUAL = r':='
    t_EXCLAMATION = r'!'

    def t_identifier(t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = Tokens.reserved.get(t.value, 'IDENTIFIER')
        return t

    def t_number(t):
        r'\d+'
        t.type = 'NUMBER'
        t.value = int(t.value)
        return t

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_STRING(t):
        r'\"([^\\\n]|(\\.))*?\"'
        t.value = t.value[1:-1]
        return t

    def t_error(t):
        print("Caracter inválido: '%s'" % t.value[0])
        t.lexer.skip(1)

lexer = lex.lex(module=Tokens)
