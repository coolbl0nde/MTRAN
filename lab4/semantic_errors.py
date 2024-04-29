class RedeclareIdentifierError(Exception):
    def __init__(self, identifier):
        message = f'\nSemantic Error! \nIdentifier \'{identifier}\' already declared in current scope.'

        self.message = message
        super().__init__(self.message)


class IncorrectTypeError(Exception):
    def __init__(self, var_type, expr_type):
        message = f'\nSemantic Error! \nType mismatch: Cannot assign {expr_type if expr_type else "expression"} to {var_type}.'

        self.message = message
        super().__init__(self.message)


class ReassignConstantError(Exception):
    def __init__(self, var):
        message = f'\nSemantic Error! \nCannot redefine constant variable \'{var}\'.'

        self.message = message
        super().__init__(self.message)


class ParameterMismatchError(Exception):
    def __init__(self, func_name, expected_len, actual_len):
        message = f'Expected {expected_len} arguments but got {actual_len} for function \'{func_name}\'.'

        self.message = message
        super().__init__(self.message)
