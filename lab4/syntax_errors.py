class Error(Exception):
    def __init__(self, message, line_num, symbol_num):
        self.message = message + f'\nLine: {line_num}, Symbol: {symbol_num}'
        super().__init__(self.message)


class UnexpectedTokenError(Error):
    def __init__(self, token, prev_token_value=None, expected=''):
        self.token_value = token['lexeme']
        self.line_num = token['line']
        self.symbol_num = token['symbol']

        message = f'Syntax Error! \nUnexpected identifier: \'{token["lexeme"]}\' after {prev_token_value}.'

        if expected:
            message += f'\nExpected: {expected}'

        self.message = message
        super().__init__(self.message, self.line_num, self.symbol_num)


class IncorrectLoopKeywordError(Error):
    def __init__(self, token):
        self.token_value = token['lexeme']
        self.line_num = token['line']
        self.symbol_num = token['symbol']

        message = f'Syntax Error! \nUnexpected identifier: \'{token["lexeme"]}\'. You can\'t use \'{token["lexeme"]}\' outside of a loop.'

        self.message = message
        super().__init__(self.message, self.line_num, self.symbol_num)

