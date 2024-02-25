from re import match
from constants import DATA_TYPE, SYMBOLS, KEYWORDS
from utils import get_correct_token
from errors import UnknownTokenError, IncorrectVariableError


def analyze_tokens(tokens):
    tokens_with_types = []
    prev_token = None
    next_token = None
    prev_token_type = {
        'data_type': "",
    }
    params = {
        'line': 1,
        'symbol': 1,
    }

    for i in range(len(tokens)):
        if i:
            prev_token = tokens[i - 1]
        if i + 1 < len(tokens):
            next_token = tokens[i + 1]

        token_type = get_token_type(tokens[i], prev_token, next_token, tokens_with_types, prev_token_type, params)
        tokens_with_types.append({tokens[i]: token_type})

    # for token in tokens:
    #     token_type = get_token_type(token, prev_token, tokens_with_types)
    #     tokens_with_types.append({token: token_type})
    #     #tokens_with_types[token] = token_type
    #     prev_token = token
    return tokens_with_types


def get_token_type(token, prev_token, next_token, tokens_with_types, prev_token_type, params):
    params["symbol"] += len(str(token))

    if token in DATA_TYPE:
        return "data type"
    elif token in KEYWORDS:
        return KEYWORDS[token]
    elif prev_token == ",":
        return prev_token_type["data_type"]
    elif token in SYMBOLS:
        return SYMBOLS[token]
    elif prev_token == "struct":
        if next_token == "{":
            DATA_TYPE.append(token)
            return f"structure {token}"
    elif prev_token in DATA_TYPE:
        if match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', token.replace('*', '')):
            if next_token == "(":
                return f"function ({prev_token})"
            if token.startswith('*'):
                return f"{prev_token} pointer"

            prev_token_type["data_type"] = f"{prev_token} variable"
            return f"{prev_token} variable"
        else:
            raise IncorrectVariableError(token, params["line"], params["symbol"])
    elif token.startswith('*'):
        return 'pointer'
    elif token.isdigit():
        return "integer"
    elif token.replace('.', '', 1).isdigit() and ('.' in token or 'e' in token.lower() or 'E' in token):
        return "float"
    elif token.startswith("<") and token.endswith:
        return "library"
    elif len(token) == 3 and token.startswith("'") and token.endswith("'"):
        return "character constant"
    elif token.startswith('"') and token.endswith('"'):
        return "string constant"
    elif token == '\n':
        params["line"] += 1
        params["symbol"] = 1
    else:
        for t in tokens_with_types:
            modified_token = token.replace('&', '')
            if modified_token in t:
                if token.startswith('&'):
                    return f"'{modified_token}' variable reference"

                return t[token]

        raise UnknownTokenError(token, params["line"], params["symbol"], get_correct_token(token))
