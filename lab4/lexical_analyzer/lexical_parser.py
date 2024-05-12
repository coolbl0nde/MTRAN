from lexical_analyzer.constants import DATA_TYPE, SYMBOLS


def tokenize(input_text):
    tokens = []
    token = ""
    separators = " ;,(){}[]+-*/<>=&|!"

    for char in input_text:
        if char in separators:
            if token:
                tokens.append(token)
                token = ""
            if char.strip():
                tokens.append(char)
        else:
            token += char
    if token:
        tokens.append(token)

    tokens = combine_tokens(tokens, DATA_TYPE)

    return tokens


def combine_tokens(tokens, data_types):
    combined_tokens = []
    i = 0

    #print(tokens)

    while i < len(tokens):
        combined_token = tokens[i]
        #print(combined_token)

        if i + 1 < len(tokens) and (tokens[i] + tokens[i + 1] in {">=", "<=", "==", "!=", "++", "--", ">>", "<<", "->", "+=",
                                                                  "-=", "*=", "/="}):
            combined_token += tokens[i + 1]
            i += 2
            combined_tokens.append(combined_token)
            continue

        elif tokens[i] == "#include" and tokens[i+1] == "<" and tokens[i + 3] == ">":
            combined_token += tokens[i + 1] + tokens[i + 2] + tokens[i + 3]
            i += 4
            combined_tokens.append(combined_token)
            continue

        elif tokens[i].startswith('"'):
            if not tokens[i].endswith('"') or tokens[i].count('"') == 1:
                i += 1

                while i < len(tokens) and not tokens[i].endswith('"'):
                    combined_token += ' ' + tokens[i]
                    i += 1
                if i < len(tokens):
                    combined_token += ' ' + tokens[i]

        elif tokens[i].startswith("'"):
            if not tokens[i].endswith("'") or tokens[i].count("'") == 1:
                i += 1

                while i < len(tokens) and not tokens[i].endswith("'"):
                    combined_token += ' ' + tokens[i]
                    i += 1
                if i < len(tokens):
                    combined_token += ' ' + tokens[i]

        elif i + 1 < len(tokens):
            if tokens[i] + tokens[i + 1] == "//":
                i += 2
                while i + 1 < len(tokens) and not tokens[i].endswith('\n'):
                    i += 1
                continue

            elif tokens[i] + tokens[i + 1] == "/*":
                combined_token += tokens[i + 1]
                i += 2
                combined_tokens.append(combined_token)
                while i + 1 < len(tokens) and tokens[i] + tokens[i + 1] != '*/':
                    i += 1
                if i + 1 < len(tokens):
                    combined_tokens.append(tokens[i] + tokens[i + 1])
                i += 2
                continue

            elif i and tokens[i] in ["*", "&"] and tokens[i - 1] in DATA_TYPE + list(SYMBOLS.keys()):
                combined_token += tokens[i + 1]
                combined_tokens.append(combined_token)
                i += 2
                continue

        for j in range(i + 1, len(tokens)):
            potential_combination = f"{combined_token} {tokens[j]}"
            if any(dt.startswith(potential_combination) for dt in data_types):
                combined_token = potential_combination
                i = j
            else:
                break

        combined_tokens.append(combined_token)
        i += 1

    #print(combined_tokens)
    return combined_tokens

