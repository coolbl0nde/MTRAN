class LexicalError(Exception):
    def __init__(self, message, line, symbol):
        self.message = message + f'\nLine: {line}, Symbol: {symbol}'
        super().__init__(self.message)


class UnknownTokenError(LexicalError):
    def __init__(self, token_value, line=1, symbol=0, correct_token=None):
        self.token_value = token_value
        self.line = line
        self.symbol = symbol

        message = f'Lexical Error! \nUnknown identifier: \'{token_value}\'.'

        if correct_token:
            message += f' Maybe you wanted to use \'{correct_token}\' instead?'

        self.message = message
        super().__init__(self.message, self.line, self.symbol)


class IncorrectVariableError(LexicalError):
    def __init__(self, var_name, line=1, symbol=0):
        self.token_value = var_name
        self.line = line
        self.symbol = symbol

        message = f'Lexical Error! \nIncorrect variable naming: \'{var_name}\'.'

        self.message = message
        super().__init__(self.message, self.line, self.symbol)
