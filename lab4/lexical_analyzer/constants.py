DATA_TYPE = [
    'bool',
    'int',
    'const',
    'short int',
    'long int',
    'long long int',
    'float',
    'double',
    'long double',
    'char',
    'void',
    'unsigned char',
    'signed char',
    'unsigned short',
    'unsigned int',
    'unsigned long int',
    'unsigned long long int',
    'unsigned long long'
]

KEYWORDS = [
    'for',
    'while',
    'do',
    'if',
    'else',
    'return',
    'void',
    'struct',
    'union',
    'enum',
    'typedef',
    'const',
    'static',
    'extern',
    'volatile',
    'switch',
    'case',
    'default',
    'break',
    'continue',
    'sizeof',
    'bool',
    'int',
    'short int',
    'long int',
    'long long int',
    'float',
    'double',
    'long double',
    'char',
    'unsigned char',
    'signed char',
    'unsigned short',
    'unsigned int',
    'unsigned long int',
    'unsigned long long int',
]

SYMBOLS = {
    '(': 'PARENTHESIS',
    ')': 'PARENTHESIS',
    '{': 'BRACE',
    '}': 'BRACE',
    '[': 'BRACKET',
    ']': 'BRACKET',
    ';': 'SEMICOLON',
    ',': 'COMMA',
    ':': 'SYMBOL',
    '=': 'SYMBOL'
}

STRUCTURES = []

OPERATORS = {
    '=': 'OPERATOR',
    '+': 'OPERATOR',
    '-': 'OPERATOR',
    '*': 'OPERATOR',
    '/': 'OPERATOR',
    '%': 'OPERATOR',
    '+=': 'OPERATOR',
    '-=': 'OPERATOR',
    '&&': 'LOGICAL_OPERATOR',
    '||': 'LOGICAL_OPERATOR',
    '!': 'LOGICAL_OPERATOR',
    '==': 'COMPARISON_OPERATOR',
    '!=': 'COMPARISON_OPERATOR',
    '<': 'COMPARISON_OPERATOR',
    '>': 'COMPARISON_OPERATOR',
    '<=': 'COMPARISON_OPERATOR',
    '>=': 'COMPARISON_OPERATOR',
    '&': 'BITWISE_OPERATOR',
    '|': 'BITWISE_OPERATOR',
    '^': 'BITWISE_OPERATOR',
    '~': 'BITWISE_OPERATOR',
    '<<': 'BITWISE_OPERATOR',
    '>>': 'BITWISE_OPERATOR',
    '->': 'ACCESS_OPERATOR',
    '.': 'ACCESS_OPERATOR',
    '++': 'INCREMENT_OPERATOR',
    '--': 'DECREMENT_OPERATOR',
    '//': 'SINGLE LINE COMMENT',
    '/*': 'MULTILINE COMMENT START',
    '*/': 'MULTILINE COMMENT END'
}

