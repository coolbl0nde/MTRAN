from lexical_analyzer.constants import DATA_TYPE, SYMBOLS, KEYWORDS


def get_correct_token(element: str):
    symbols = list(SYMBOLS.keys())
    keywords = KEYWORDS

    result = ""
    max_count = 0

    for string in DATA_TYPE + keywords + symbols:
        count = 0

        for i, (char_from_string, char_from_element) in enumerate(zip(string, element)):
            if char_from_string == char_from_element:
                count += 1
            else:
                break

        if count > max_count:
            max_count = count
            result = string

    return result
