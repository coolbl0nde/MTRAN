from lexical_analyzer.lexical_parser import tokenize
from lexical_analyzer.token_type import analyze_tokens
from syntactical_analyzer import Parser
from semantic_analyzer import Analyzer


def main():
    with open('input.txt', 'r') as file:
        input_text = file.read().replace('\n', ' \n ')

    tokens = tokenize(input_text)
    tokens_with_types = analyze_tokens(tokens)

    with open('tokens.txt', 'w') as file:
        index = 1

        for i, item in enumerate(tokens_with_types, start=1):
            file.write(f"{index}\t{item}\n")

            #print(item["lexeme"] + ": " + item["type"])

            index += 1

    parser = Parser(tokens_with_types)  # Initialize the parser with tokens
    syntax_tree = parser.parse("Program")

    parser.print_tree(syntax_tree)

    analyzer = Analyzer(syntax_tree)

    # syntax_tree.pretty_print()


if __name__ == '__main__':
    main()