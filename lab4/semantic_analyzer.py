#from lab4.app_types import *
from semantic_errors import *
from lexical_analyzer.constants import *

C_FUNCS = ["printf", "scanf", "sizeof"]

class Analyzer:
    def __init__(self, tree):
        self._tree = tree
        self.current_scope = {
            "sizeof": "int",
        }
        self.scopes = [self.current_scope]

        self.analyze(self._tree)

    def analyze(self, node):
        if node is None:
            return

        if node.type == 'Func Definition':
            func_name = node.value

            if func_name in self.current_scope:
                raise RedeclareIdentifierError(func_name)

            self.current_scope[func_name] = {
                'type': f'{node.data_type} Function',
                'parameters': [(param.value.replace('[]', ''), param.data_type) for param in node.children[0].children if
                               param.type == 'Parameter']
            }
            self.enter_scope()
            for child in node.children:
                self.analyze(child)
            self.exit_scope()

        elif node.type == 'Structure':
            structure_name = node.value

            if structure_name in self.current_scope:
                raise RedeclareIdentifierError(structure_name)

            self.current_scope[structure_name] = {
                'type': f'{node.value} Structure',
                'parameters': []
            }

            for child in node.children:
                for param in child.children:
                    if param.value and param.data_type:
                        self.current_scope[structure_name]['parameters'] = self.current_scope[structure_name]['parameters'] + [(param.value, param.data_type)]

        elif node.type == 'Struct Variable Definition':
            struct_name = node.data_type
            struct_details = self.get_function_or_struct_details(struct_name)

            if not struct_details:
                raise Exception(f'Unexpected identifier: {node.value}')

            expected_params = struct_details['parameters']
            provided_args = node.children[0].children

            if len(provided_args) != len(expected_params):
                raise ParameterMismatchError(struct_name, len(expected_params), len(provided_args))

            for arg, (param_name, param_type) in zip(provided_args, expected_params):
                arg_type = self.evaluate_type(arg)
                if not self.compare_types(arg_type, param_type):
                    raise IncorrectTypeError(arg_type, param_type)

        elif node.type == 'Parameters':
            for param in node.children:
                param_name = param.value.replace('[]','')
                param_type = param.data_type

                if param_name in self.current_scope:
                    raise RedeclareIdentifierError(param_name)

                if param_type:
                    self.current_scope[param_name] = param_type

        elif node.type == 'Var Definition':
            var_node = node.children[0]
            var_name = var_node.value
            var_type = var_node.data_type

            if var_name in self.current_scope and var_type:
                raise RedeclareIdentifierError(var_name)

            self.current_scope[var_name] = var_type

            if len(node.children) > 2:
                expression_node = node.children[2]
                self.analyze(expression_node)
                expr_type = self.evaluate_type(expression_node)

                if not self.compare_types(var_type, expr_type):
                    raise IncorrectTypeError(var_type, expr_type)

        elif node.type == 'Var Reassignment':
            var_node = node.children[0]
            var_name = var_node.value
            var_type = self.evaluate_type(var_node)

            if not var_type:
                raise Exception(f'Unexpected identifier: {var_name}')

            if 'const' in var_type:
                raise ReassignConstantError(var_name)

            expression_node = node.children[2]
            self.analyze(expression_node)
            # print(expression_node.type)
            expr_type = self.evaluate_type(expression_node)

            if not self.compare_types(var_type, expr_type):
                raise IncorrectTypeError(var_type, expr_type)

        elif node.type == 'Array Element Call':
            array_name = node.children[0].value
            index_node = node.children[1].children[0]

            index_data_type = self.evaluate_type(index_node)

            if index_data_type != 'int':
                raise Exception(f'Cannot use {index_data_type} as index for array {array_name}')

        elif node.type in ['For Loop', 'While Loop']:
            self.enter_scope()
            parameters_node = node.children[0]
            for child in parameters_node.children:
                self.analyze(child)

            self.analyze(node.children[1])
            self.exit_scope()

        elif node.type == 'Array Definition':
            array_node = node.children[0]
            array_type = array_node.data_type
            array_name = array_node.value

            if array_name in self.current_scope:
                raise RedeclareIdentifierError(array_name)

            if len(node.children) > 1:
                array_parameters = node.children[1].children

                for param in array_parameters:
                    data_type = self.evaluate_type(param)
                    if data_type != array_type:
                        raise IncorrectTypeError(array_type, data_type)

            self.current_scope[array_name] = array_type

        elif node.type == 'Condition':
            for child in node.children:
                if 'operator' in child.type.lower():
                    continue

                var_type = child.data_type or self.evaluate_type(child)
                if not var_type:
                    raise Exception(f'Unexpected identifier: {child.value}')

                if var_type.replace('const ', '') not in ['int', 'double', 'float', 'unsigned']:
                    raise Exception(
                        f'Incorrect variable type of variable {child.value}! '
                        f'Expected on of the following types: int, double, float'
                    )

            constant_node = node.children[2]
            var_type = constant_node.data_type or self.evaluate_type(constant_node)

            if var_type.replace('const ', '') not in ['int', 'double', 'float', 'unsigned']:
                raise Exception(
                    f'Incorrect variable type of variable {constant_node.value}! '
                    f'Expected on of the following types: int, double, float'
                )

        elif node.type == 'Function Call':
            func_name = node.value
            function_details = self.get_function_or_struct_details(func_name)

            if func_name in C_FUNCS:
                return

            if not function_details:
                raise Exception(f'Unexpected identifier: {node.value}()')

            expected_params = function_details['parameters']
            provided_args = node.children[0].children

            if len(provided_args) != len(expected_params):
                raise ParameterMismatchError(func_name, len(expected_params), len(provided_args))

            for arg, (param_name, param_type) in zip(provided_args, expected_params):
                arg_type = self.evaluate_type(arg)
                if not self.compare_types(arg_type, param_type):
                    raise IncorrectTypeError(arg_type, param_type)

        elif node.type in ["If", "Else"]:
            self.enter_scope()
            for child in node.children:
                self.analyze(child)
            self.exit_scope()

        else:
            for child in node.children:
                self.analyze(child)

    def enter_scope(self):
        new_scope = {}
        self.scopes.append(new_scope)
        self.current_scope = new_scope

    def exit_scope(self):
        self.scopes.pop()
        self.current_scope = self.scopes[-1]

    def get_variable_type(self, var_name):
        for scope in reversed(self.scopes):
            if var_name in scope:
                return scope[var_name]
        raise Exception(f'Unexpected identifier: {var_name}')

    def get_variable_or_constant_type(self, node):
        if node.data_type is not None:
            return node.data_type
        elif node.type == 'Constant':
            value = node.value.strip()

            if value.lower() in ['true', 'false']:
                return 'bool'
            elif value.startswith("'") and value.endswith("'"):
                return 'char'
            elif value.isdigit() or (value.startswith('-') and value[1:].isdigit()):
                return 'int'
            elif value.replace('.', '', 1).isdigit() and '.' in value:
                return 'float'
            else:
                return 'char'

        elif node.type == 'Variable':
            return self.get_variable_type(node.value)

    def evaluate_type(self, node):
        if node.data_type:
            return node.data_type

        if node.type == 'Function Call':
            val = self.get_variable_type(node.value)

            if not val and node.value not in C_FUNCS:
                raise Exception(f'Unexpected identifier: {node.value}()')

            if type(val) is dict:
                return val['type'].replace(' Function', '')
            elif val:
                return val.replace(' Function', '')

        elif node.type == 'Expression':
            data_types = []

            for child in node.children:
                data_type = self.evaluate_type(child)

                if data_type:
                    data_types.append(data_type)

            if not data_types:
                return ''

            return self.find_most_general_type(data_types)

        elif node.type == 'Array Element Call':
            array_name = node.children[0].value

            element_type = self.get_variable_type(array_name)

            if element_type:
                return element_type

        elif node.type in ["Constant", "Variable"]:
            return self.get_variable_or_constant_type(node)

    def get_function_or_struct_details(self, func_name):
        for scope in reversed(self.scopes):
            if func_name in scope and 'parameters' in scope[func_name]:
                return scope[func_name]
        return None

    def find_most_general_type(self, types):
        promotion_rules = {
            'short': ['int', 'long', 'float', 'double'],
            'int': ['long', 'float', 'double'],
            'long': ['float', 'double'],
            'float': ['double'],
            'char': [],
            'double': [],
        }

        most_general_type = types[0]

        for type in types[1:]:
            while most_general_type not in promotion_rules[type]:
                if type == most_general_type or not promotion_rules[most_general_type]:
                    break
                most_general_type = type

        return most_general_type

    def compare_types(self, var_type, expr_type):
        var_type = var_type.replace('const ', '') if var_type else ''
        expr_type = expr_type.replace('const ', '') if expr_type else ''

        compatibility = {
            'short': ['int'],
            'int': ['long'],
            'long': ['float', 'double', 'decimal'],
            'float': ['double'],
            'double': ['int', 'float', 'decimal', 'short'],
            'char': [],
            'bool': [],
        }

        return var_type == expr_type or expr_type in compatibility[var_type]
