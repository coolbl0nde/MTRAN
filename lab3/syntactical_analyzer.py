from syntax_errors import UnexpectedTokenError, IncorrectLoopKeywordError
from tree_node import TreeNode
from lexical_analyzer.constants import DATA_TYPE, OPERATORS


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0
        self.current_token = tokens[0]
        self.is_cycle_now = False

    def next_token(self):
        if self.position + 1 < len(self.tokens):
            self.position += 1
            self.current_token = self.tokens[self.position]
        else:
            self.current_token = {'lexeme': 'EOF', 'type': 'EOF'}

    def eat(self, tokens, type=None):
        lexeme = self.current_token['lexeme']

        if self.current_token['lexeme'] in tokens:
            self.next_token()

            if (type):
                return TreeNode(type, value=lexeme)
        else:
            raise UnexpectedTokenError(self.current_token, self.tokens[self.position - 1]['lexeme'], tokens)

    def parse(self, type="Block"):
        nodes = []
        separators = ['}', 'EOF']

        #print(self.current_token)

        while self.position < len(self.tokens) and self.current_token and self.current_token['lexeme'] not in separators:
            nodes += self.parse_program()

        return TreeNode(type, children=nodes)

    def parse_program(self):
        functions = []

        self.current_token = self.tokens[self.position]

        if self.current_token['type'] == "Preprocessor Directive":
            functions.append(TreeNode(self.current_token['type'], value=self.current_token["lexeme"]))
            self.next_token()
        elif self.current_token['lexeme'] in DATA_TYPE:
            if self.position + 2 < len(self.tokens) and self.tokens[self.position + 2]['lexeme'] == '(':
                functions.append(self.parse_function())
            elif self.position + 2 < len(self.tokens) and self.tokens[self.position + 2]['lexeme'] == '[':
                functions.append(self.parse_array())
            else:
                functions += self.parse_variable_definition()
        elif self.current_token['type'] == 'KEYWORD':
            if self.current_token['lexeme'] in ['if', 'for', 'while', 'switch', 'return', 'case']:
                method_name = f'parse_{self.current_token["lexeme"]}'
                method = getattr(self, method_name)
                self.next_token()
                res = method()

                if isinstance(res, list):
                    functions += res
                else:
                    functions.append(res)
            elif self.current_token['lexeme'] == 'struct':

                if self.position + 2 < len(self.tokens) and self.tokens[self.position + 2]['lexeme'] == "{":
                    self.next_token()
                    functions.append(self.parse_struct())
                else:
                    functions.append(self.parse_struct_call())

            elif self.current_token['lexeme'] in ['break', 'continue']:
                if not self.is_cycle_now:
                    raise IncorrectLoopKeywordError(self.current_token)
                else:
                    self.next_token()
            else:
                self.next_token()
        elif self.current_token['type'] == "IDENTIFIER":
            if self.position + 1 < len(self.tokens) and self.tokens[self.position + 1]['lexeme'] == '(':
                functions.append(self.parse_function_call())
            else:
                functions.append(self.parse_formula("Var Reassignment"))
                self.eat([";"])
        else:
            self.next_token()

        return functions

    def print_tree(self, node, level=0):
        indent = "  " * level
        # print(node.type, node.children)
        colon = ":" if node.children or node.value else ""

        print(f"{indent}- {node.type}{colon} {node.value if node.value else ''}")

        for child in node.children:
            if child:
                self.print_tree(child, level + 1)

    def parse_function(self):
        self.next_token()
        # print(self.current_token)

        function_name = self.current_token['lexeme']
        self.next_token()

        function_node = TreeNode("Func Definition", value=f"{function_name}")

        #print(1)
        self.eat('(')
        if self.current_token['lexeme'] != ')':
            parameters_node = self.parse_function_parameters(types=True)
            function_node.add_child(parameters_node)
        else:
            self.next_token()

        #print(3)

        self.eat('{')
        #print(self.current_token)
        body_node = TreeNode("Block")
        while self.current_token['lexeme'] != '}':
            #print(222)
            expressions = self.parse_program()
            for expr in expressions:
                if isinstance(expr, list):
                    for e in expr:
                        body_node.add_child(e)
                else:
                    body_node.add_child(expr)
        self.next_token()

        #print(5)

        function_node.add_child(body_node)

        return function_node

    def parse_function_parameters(self, types=True):
        parameters_node = TreeNode("Parameters")

        while self.position < len(self.tokens) and self.current_token['lexeme'] != ')':
            if types:
                self.next_token()

            if self.current_token['type'] == "IDENTIFIER":
                param_name = self.current_token['lexeme']
                self.next_token()
                if self.current_token['lexeme'] == '[':
                    param_name += '['
                    self.next_token()
                    self.eat(']')
                    param_name += ']'

                parameter_node = TreeNode("Parameter", value=f"{param_name}")
                parameters_node.add_child(parameter_node)
            else:
                previous_token_val = self.tokens[self.position - 1]['lexeme'] if self.position > 0 else 'start'
                expected = "IDENTIFIER"
                current_token = self.current_token

                raise UnexpectedTokenError(current_token, previous_token_val, expected)

            if self.position < len(self.tokens) and self.current_token['lexeme'] == ',':
                self.next_token()

        self.eat([')'])
        return parameters_node

    def parse_variable_definition(self, type="Var Definition"):

        if type == "Var Definition":
            base_type = self.current_token["lexeme"]
            self.next_token()

            if base_type == 'const':
                if self.current_token["lexeme"] in DATA_TYPE:
                    base_type += f' {self.current_token["lexeme"]}'
                    self.next_token()
                else:
                    raise UnexpectedTokenError(self.current_token)

        var_nodes = []
        while True:
            variable_name = self.current_token["lexeme"]
            #print(variable_name)
            self.next_token()

            var_node = TreeNode(type=type)
            var_node.add_child(TreeNode("Variable", value=f"{variable_name}"))

            if self.position < len(self.tokens) and self.current_token["lexeme"] == "=":
                self.next_token()

                value_node = self.parse_assignment_value()
                var_node.add_child(TreeNode("Assignment operator", value="="))
                var_node.add_child(value_node)

            var_nodes.append(var_node)

            if self.position >= len(self.tokens) or self.current_token["lexeme"] != ',':
                break

            self.next_token()

        return var_nodes

    def parse_assignment_value(self):
        res = self.parse_formula()
        self.eat([';'])
        return res


    def parse_function_call(self):
        function_name = self.current_token["lexeme"]
        self.position += 1
        self.next_token()

        args = []
        while self.current_token["lexeme"] != ')':
            arg = self.parse_formula("")
            args.extend(arg)
            if self.position < len(self.tokens) and self.current_token["lexeme"] == ',':
                self.next_token()

        self.next_token()

        function_call_node = TreeNode("Function Call", value=function_name)
        params_node = TreeNode("Call params")
        params_node.add_child(args)
        function_call_node.add_child(params_node)

        return function_call_node

    def parse_formula(self, type="Expression"):
        #print('aaaa', self.current_token)
        node = TreeNode(type=type)
        children = []

        if self.current_token['lexeme'] == "++" or self.current_token['lexeme'] == "--":
            operation_node = TreeNode("Operator", value=self.current_token["lexeme"])
            self.next_token()
            variable_node = self.parse_variable_or_constant()
            children.append(operation_node)
            children.append(variable_node)
            node.add_child(children)
            return node

        if self.position + 1 < len(self.tokens) and self.tokens[self.position + 1]['lexeme'] == '(':
            left_node = self.parse_function_call()
        else:
            left_node = self.parse_variable_or_constant()


        #if self.current_token["lexeme"] not in OPERATORS:
        children.append(left_node)

        while self.position < len(self.tokens) and self.current_token["lexeme"] in OPERATORS:
            op = self.current_token
            #print(self.current_token)
            operation_node = TreeNode("Operator", value=op['lexeme'])

            if self.current_token["lexeme"] == "++" or self.current_token["lexeme"] == "--":
                children.append(operation_node)
                self.next_token()
                break

            self.next_token()
            expr_node = self.parse_formula()
            right_node = expr_node.children[0] if len(expr_node.children) == 1 else expr_node
            children.append(operation_node)
            children.append(right_node)

        if type:
            node.add_child(children)
            return node

        return children

    def parse_variable_or_constant(self):
        if self.current_token["type"] == "CONSTANT":
            const_node = TreeNode("Constant", value=self.current_token["lexeme"])
            self.next_token()
            return const_node
        elif self.current_token["type"] == "IDENTIFIER":
            if self.tokens[self.position + 1]['lexeme'] != '[':
                var_node = TreeNode("Variable", value=self.current_token["lexeme"])
                self.next_token()
            else:
                var_node = TreeNode("Array Element Call")
                var_node.add_child(TreeNode("Name", value=self.current_token["lexeme"]))

                print(self.current_token)
                self.next_token()
                self.eat('[')
                var_node.add_child(TreeNode("Index", children=[self.parse_formula()]))
                self.eat(']')

            return var_node
        else:
            current_token = self.current_token
            previous_token_val = self.tokens[self.position - 1]['lexeme'] if self.position > 0 else 'start'

            raise UnexpectedTokenError(current_token, previous_token_val, "")

    def parse_while(self):
        while_node = TreeNode("While Loop")
        self.is_cycle_now = True
        self.eat(['('])

        params_node = TreeNode("Parameters")
        params_node.add_child(self.parse_bool("Condition"))

        while_node.add_child(params_node)

        self.eat([')'])
        self.eat(['{'])
        while_node.add_child(self.parse())
        self.eat(['}'])

        self.is_cycle_now = False
        return while_node

    def parse_for(self):
        for_node = TreeNode("For Loop")
        self.is_cycle_now = True
        self.eat(['('])

        params_node = TreeNode("Parameters")

        params_node.add_child(self.parse_for_initialization())

        params_node.add_child(self.parse_bool("Condition"))
        self.eat([';'])

        params_node.add_child(self.parse_formula("Post Expression"))
        self.eat([')'])
        self.eat(['{'])

        for_node.add_child(params_node)
        for_node.add_child(self.parse())
        self.eat(['}'])

        self.is_cycle_now = False
        return for_node

    def parse_if(self, type="If"):
        nodes = []

        if_node = TreeNode(type)

        if type == "Else If":
            self.eat(['if'], "Operator")

        self.eat(['('], "Symbol")
        condition_node = self.parse_bool()
        if_node.add_child(condition_node)
        self.eat([')'], "Symbol")
        self.eat(['{'], "Symbol")
        true_branch = self.parse()
        if_node.add_child(true_branch)
        self.eat(['}'], "Symbol")

        nodes.append(if_node)

        if self.position < len(self.tokens) and self.current_token['lexeme'] == 'else':
            self.next_token()
            if self.position < len(self.tokens) and self.current_token['lexeme'] == 'if':
                else_if_node = self.parse_if("Else If")
                nodes.extend(else_if_node)
            else:
                self.eat(['{'], "Symbol")
                else_node = TreeNode("Else")
                else_node.add_child(self.parse())
                nodes.append(else_node)
                self.eat(['}'], "Symbol")

        return nodes

    def parse_bool(self, type="Condition"):
        if self.current_token['lexeme'] in ["true", "false"]:
            bool_node = TreeNode(type, self.current_token['lexeme'])
            self.next_token()
            return bool_node
        else:
            return self.parse_formula(type)

    def parse_return(self):
        return_node = TreeNode("Return")
        expression = self.parse_formula()
        self.eat([';'], "Symbol")
        return_node.add_child(expression)
        return return_node

    def parse_for_initialization(self):
        if self.current_token["lexeme"] in DATA_TYPE:
            var_declaration = self.parse_variable_definition()
            return var_declaration
        else:
            var_node = self.parse_variable_or_constant()

            if self.current_token["lexeme"] == '=':
                self.next_token()
                value_node = self.parse_formula("")
                assignment_node = TreeNode("Var Reassignment")
                assignment_node.add_child(var_node)
                assignment_node.add_child(TreeNode("Operator", value="="))
                assignment_node.add_child(value_node)
                self.eat([';'])
                return assignment_node
            else:
                raise UnexpectedTokenError(self.current_token, var_node.value, ["="])

    def parse_array(self):

        self.next_token()
        # print(self.current_token)

        array_name = self.current_token['lexeme']
        self.next_token()

        array_node = TreeNode("Array Definition", value=f"{array_name}")

        # print(1)
        self.eat('[')

        if self.current_token["lexeme"] != "]":
            size_node = TreeNode("Size", children=[self.parse_variable_or_constant()])

            array_node.add_child(size_node)

        self.eat(']')

        if self.current_token['lexeme'] == ';':
            self.next_token()
            return array_node
        elif self.current_token['lexeme'] == '=':
            self.next_token()
            self.eat('{')
            parameters_node = TreeNode("Parameters")

            while self.current_token["type"] in ["IDENTIFIER", "CONSTANT"]:
                #print(self.current_token['lexeme'])
                parameters_node.add_child(self.parse_variable_or_constant())

                if self.current_token['lexeme'] != '}' and self.position + 1 < len(self.tokens)\
                        and self.tokens[self.position + 1]['lexeme'] != '}':
                    self.eat(',')


            array_node.add_child(parameters_node)
            self.eat('}')
            self.eat(';')
        else:
            raise UnexpectedTokenError(self.current_token, ']')

        return array_node


    def parse_struct(self):
        # self.eat(['struct'], "Keyword")
        struct_name = self.current_token["lexeme"]
        self.next_token()

        struct_node = TreeNode("Structure", value=struct_name)
        self.eat(['{'], "Symbol")

        while self.current_token["lexeme"] != '}':
            if self.position + 2 < len(self.tokens) and self.tokens[self.position + 2]['lexeme'] == '[':
                struct_node.add_child(self.parse_array())
            else:
                struct_node.add_child(self.parse_variable_definition())
                self.eat(';')

        self.next_token()

        return struct_node

    def parse_struct_call(self):
        self.next_token()
        self.next_token()
        # print(self.current_token)

        struct_name = self.current_token['lexeme']
        self.next_token()

        array_node = TreeNode("Variable Definition", value=f"{struct_name}")

        # print(1)

        if self.current_token['lexeme'] == ';':
            self.next_token()
            return array_node
        elif self.current_token['lexeme'] == '=':
            self.next_token()
            self.eat('{')
            parameters_node = TreeNode("Parameters")

            while self.current_token["type"] in ["IDENTIFIER", "CONSTANT"]:
                # print(self.current_token['lexeme'])
                parameters_node.add_child(self.parse_variable_or_constant())

                if self.current_token['lexeme'] != '}' and self.position + 1 < len(self.tokens) \
                        and self.tokens[self.position + 1]['lexeme'] != '}':
                    self.eat(',')

            array_node.add_child(parameters_node)
            self.eat('}')
            self.eat(';')
        else:
            raise UnexpectedTokenError(self.current_token, ']')

        return array_node

