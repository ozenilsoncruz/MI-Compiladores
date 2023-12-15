from config import palavras_reservadas


class SyntacticParser:
    def __init__(self):
        self.tokens = []
        self.index = 0
        self.errors = []

        self.key_words = list(palavras_reservadas)
        self.delimiters = ["{", "}", ";"]
        self.delimiters_with_keywords = self.delimiters + self.key_words

    def next_token(self):
        if self.index < len(self.tokens) - 1:
            self.index += 1

    def current_token(self):
        return (
            self.tokens[self.index]
            if self.index < len(self.tokens)
            else dict(valor="", num_linha="", tipo="")
        )

    def current_token_value(self) -> str:
        return self.current_token()["valor"]

    def current_token_line(self) -> str:
        return self.current_token()["num_linha"]

    def current_token_type(self) -> str:
        return self.current_token()["tipo"]

    def synchronize(self, recovery_point):
        while (
            self.current_token_value() not in recovery_point
            and self.current_token_value() != ""
        ):
            self.next_token()
        if self.current_token_value() in self.delimiters:
            self.next_token()

    def save_error(self, e: SyntaxError, recovery_point=None):
        recovery_point = recovery_point or self.delimiters_with_keywords
        message = f"{e.msg}, received '{self.current_token_value()}' in line {self.current_token_line()}"
        self.errors.append(message)
        self.synchronize(recovery_point)

    def check_identifier(self):
        return self.current_token_type() == "IDE"

    def value(self):
        return self.current_token_type() in [
            "NUM",
            "STR",
        ] or self.current_token_value() in [
            "true",
            "false",
        ]

    def method_call(self):
        if self.check_identifier():
            self.next_token()
            if self.current_token_value() == "(":
                self.next_token()
                self.args_list()
                if self.current_token_value() == ")":
                    self.next_token()
                else:
                    raise SyntaxError("Expected ')'")
            else:
                raise SyntaxError("Expected '('")
        else:
            raise SyntaxError("Expected a valid identifier")

    def object_value(self):
        if self.current_token_value() == ".":
            self.next_token()
            if self.check_identifier():
                self.next_token()
            else:
                raise SyntaxError("Expected a valid identifier")
        if self.current_token_value() == "->":
            self.next_token()
            self.method_call()

    def array_possible_value(self):
        if self.check_identifier():
            self.next_token()
            self.object_value()
        elif self.current_token_type() == "NUM":
            self.next_token()
        else:
            raise SyntaxError("Expected a valid index for array")

    def definition_access_array(self):
        if self.current_token_value() == "[":
            self.next_token()
            self.array_possible_value()
            if self.current_token_value() == "]":
                self.next_token()
                self.definition_access_array()
            else:
                raise SyntaxError("Expected ']'")

    def check_type(self):
        if self.current_token_value() in ["int", "string", "real", "boolean"]:
            self.next_token()
            self.definition_access_array()
            return True
        return False

    def possible_value(self):
        if self.check_identifier():
            self.next_token()
            self.object_value()
        elif self.value():
            self.next_token()

    def array_value(self):
        if self.current_token_value() == "[":
            self.array()
        else:
            self.possible_value()

    def more_array_value(self):
        if self.current_token_value() == ",":
            self.next_token()
            self.array_value()
            self.more_array_value()

    def array(self):
        if self.current_token_value() == "[":
            self.next_token()
            self.array_value()
            self.more_array_value()
            if self.current_token_value() == "]":
                self.next_token()
            else:
                raise SyntaxError("Expected ']'")

    def assignment_value(self):
        if self.check_identifier():
            self.next_token()
            self.definition_access_array()
            self.object_value()
        elif self.value():
            self.next_token()
        elif self.current_token_value() == "[":
            self.array()
        else:
            raise SyntaxError("Expected a valid value")

    def args_list(self):
        if self.check_identifier() or self.value() or self.current_token_value() == "[":
            self.logical_and_expression()
            self.assignment_value_list()

    def assignment_value_list(self):
        if self.current_token_value() == ",":
            self.next_token()
            if (
                self.check_identifier()
                or self.value()
                or self.current_token_value() == "["
            ):
                self.args_list()
            else:
                raise SyntaxError("Expected a valid value")

    def optional_value(self):
        if self.current_token_value() == "=":
            self.next_token()
            self.logical_and_expression()

    def variable_block(self):
        if self.current_token_value() == "variables":
            self.next_token()
            if self.current_token_value() == "{":
                self.next_token()
                self.variable()
                if self.current_token_value() == "}":
                    self.next_token()
                else:
                    raise SyntaxError("Expected '}'")
            else:
                raise SyntaxError("Expected '{'")

    def variable(self):
        try:
            if self.check_type():
                if self.check_identifier():
                    self.next_token()
                    self.optional_value()
                    self.variable_same_line()
                    if self.current_token_value() == ";":
                        self.next_token()
                        self.variable()
                    else:
                        raise SyntaxError("Expected ';'")
                else:
                    raise SyntaxError("Expected a valid identifier")
        except SyntaxError as e:
            self.save_error(e)
            self.variable()

    def variable_same_line(self):
        try:
            if self.current_token_value() == ",":
                self.next_token()
                if self.check_identifier():
                    self.next_token()
                    self.optional_value()
                    self.variable_same_line()
                else:
                    raise SyntaxError("Expected a valid identifier")
        except SyntaxError as e:
            self.save_error(e)

    def constant_block(self):
        if self.current_token_value() == "const":
            self.next_token()
            if self.current_token_value() == "{":
                self.next_token()
                self.constant()
                if self.current_token_value() == "}":
                    self.next_token()
                else:
                    raise SyntaxError("Expected '}")
            else:
                raise SyntaxError("Expected '{")

    def constant(self):
        try:
            if self.check_type():
                if self.check_identifier():
                    self.next_token()
                    if self.current_token_value() == "=":
                        self.next_token()
                        self.logical_and_expression()
                        self.constant_same_line()
                        if self.current_token_value() == ";":
                            self.next_token()
                            self.constant()
                        else:
                            raise SyntaxError("Expected ';'")
                    else:
                        raise SyntaxError("Expected '='")
                else:
                    raise SyntaxError("Expected a valid identifier")
        except SyntaxError as e:
            self.save_error(e)
            self.constant()

    def constant_same_line(self):
        try:
            if self.current_token_value() == ",":
                self.next_token()
                if self.check_identifier():
                    self.next_token()
                    if self.current_token_value() == "=":
                        self.next_token()
                        self.logical_and_expression()
                        self.constant_same_line()
                    else:
                        raise SyntaxError("Expected ';'")
                else:
                    raise SyntaxError("Expected a valid identifier")
        except SyntaxError as e:
            self.save_error(e)

    def class_block(self):
        try:
            if self.current_token_value() == "class":
                self.next_token()
                if self.current_token_value() != "main":
                    if self.check_identifier():
                        self.next_token()
                        self.class_extends()
                        if self.current_token_value() == "{":
                            self.next_token()
                            self.class_content()
                            if self.current_token_value() == "}":
                                self.next_token()
                                self.class_block()
                            else:
                                raise SyntaxError("Expected '}'")
                        else:
                            raise SyntaxError("Expected '{'")
                    else:
                        raise SyntaxError("Expected a valid class identifier")
        except SyntaxError as e:
            sincronize_points = (
                ["objects", "class"]
                if "extends" in str(e)
                else self.delimiters_with_keywords
            )
            self.save_error(e, sincronize_points)
            self.class_block()

    def class_extends(self):
        if self.current_token_value() == "extends":
            self.next_token()
            if self.check_identifier():
                self.next_token()
            else:
                raise SyntaxError("Expected a valid class identifier")
        else:
            if self.current_token_value() != "{":
                raise SyntaxError("Expected 'extends'")

    def class_content(self):
        self.variable_block()
        self.constructor()
        self.methods()

    def methods(self):
        if self.current_token_value() == "methods":
            self.next_token()
            if self.current_token_value() == "{":
                self.next_token()
                self.method()
                if self.current_token_value() == "}":
                    self.next_token()
                else:
                    if self.current_token_value() != "class":
                        raise SyntaxError("Expected '}'")

    def method(self):
        try:
            tipo = self.check_type()
            if tipo or self.current_token_value() == "void":
                if self.current_token_value() == "void":
                    self.next_token()
                if self.check_identifier():
                    self.next_token()
                    if self.current_token_value() == "(":
                        self.next_token()
                        self.parameter()
                        if self.current_token_value() == ")":
                            self.next_token()
                            if self.current_token_value() == "{":
                                self.next_token()
                                self.statement_sequence()
                                if tipo:
                                    if self.current_token_value() == "return":
                                        self.next_token()
                                        self.assignment_value()
                                        if self.current_token_value() == ";":
                                            self.next_token()
                                            if self.current_token_value() == "}":
                                                self.next_token()
                                                self.method()
                                            else:
                                                raise SyntaxError("Expected '}'")
                                        else:
                                            raise SyntaxError("Expected ';'")
                                    else:
                                        raise SyntaxError("Expected 'return'")
                                else:
                                    if self.current_token_value() == "}":
                                        self.next_token()
                                        self.method()
                                    else:
                                        raise SyntaxError("Expected '}'")
                            else:
                                raise SyntaxError("Expected '{'")
                        else:
                            raise SyntaxError("Expected ')'")
                    else:
                        raise SyntaxError("Expected '('")
                else:
                    raise SyntaxError("Expected a valid method identifier")
        except SyntaxError as e:
            sinc = (
                ["int", "string", "real", "boolean", "void", "class", "objects", "}"]
                if "}" in str(e) and self.current_token_value() == "return"
                else self.delimiters_with_keywords
            )
            self.save_error(e, sinc)
            self.method()

    def constructor(self):
        if self.current_token_value() == "constructor":
            self.next_token()
            if self.current_token_value() == "(":
                self.next_token()
                self.parameter()
                if self.current_token_value() == ")":
                    self.next_token()
                    if self.current_token_value() == "{":
                        self.next_token()
                        self.assignment_method()
                        if self.current_token_value() == "}":
                            self.next_token()
                        else:
                            raise SyntaxError("Expected '}'")
                    else:
                        raise SyntaxError("Expected '{'")
                else:
                    raise SyntaxError("Expected ')'")
            else:
                raise SyntaxError("Expected '('")

    def main_class(self):
        if self.current_token_value() == "class":
            self.next_token()
            if self.current_token_value() == "main":
                self.next_token()
                if self.current_token_value() == "{":
                    self.next_token()
                    self.main_class_content()
                    if self.current_token_value() == "}":
                        self.next_token()
                    else:
                        raise SyntaxError("Expected '}'")
                else:
                    raise SyntaxError("Expected '{'")
            else:
                raise SyntaxError("Expected 'main'")

    def main_class_content(self):
        self.variable_block()
        self.object_block()
        self.statement_sequence()

    def object_block(self):
        if self.current_token_value() == "objects":
            self.next_token()
            if self.current_token_value() == "{":
                self.next_token()
                self.object_declaration()
                if self.current_token_value() == "}":
                    self.next_token()
                else:
                    raise SyntaxError("Expected '}'")
            else:
                raise SyntaxError("Expected '{'")

    def object_declaration(self):
        try:
            if self.check_identifier():
                self.next_token()
                if self.check_identifier():
                    self.next_token()
                    if self.current_token_value() == "=":
                        self.next_token()
                        if self.check_identifier():
                            self.next_token()
                            if self.current_token_value() == "->":
                                self.next_token()
                                if self.current_token_value() == "constructor":
                                    self.next_token()
                                    if self.current_token_value() == "(":
                                        self.next_token()
                                        self.args_list()
                                        if self.current_token_value() == ")":
                                            self.next_token()
                                            self.object_same_line()
                                            if self.current_token_value() == ";":
                                                self.next_token()
                                                self.object_declaration()
                                            else:
                                                raise SyntaxError("Expected ';'")
                                        else:
                                            raise SyntaxError("Expected ')'")
                                    else:
                                        raise SyntaxError("Expected '('")
                                else:
                                    raise SyntaxError("Expected 'constructor'")
                            else:
                                raise SyntaxError("Expected '->'")
                        else:
                            raise SyntaxError("Expected a valid identifier")
                    else:
                        raise SyntaxError("Expected '='")
                else:
                    raise SyntaxError("Expected a valid identifier")
        except SyntaxError as e:
            self.save_error(e)
            self.object_declaration()

    def object_same_line(self):
        if self.current_token_value() == ",":
            self.next_token()
            if self.check_identifier():
                self.next_token()
                if self.current_token_value() == "=":
                    self.next_token()
                    if self.check_identifier():
                        self.next_token()
                        if self.current_token_value() == "->":
                            self.next_token()
                            if self.current_token_value() == "constructor":
                                self.next_token()
                                if self.current_token_value() == "(":
                                    self.next_token()
                                    self.args_list()
                                    if self.current_token_value() == ")":
                                        self.next_token()
                                        self.object_same_line()
                                    else:
                                        raise SyntaxError("Expected ')'")
                                else:
                                    raise SyntaxError("Expected '('")
                            else:
                                raise SyntaxError("Expected 'constructor'")
                        else:
                            raise SyntaxError("Expected '->'")
                    else:
                        raise SyntaxError("Expected a valid identifier")
                else:
                    raise SyntaxError("Expected '='")
            else:
                raise SyntaxError("Expected a valid identifier")

    def assignment_method(self):
        try:
            if self.current_token_value() == "this":
                self.next_token()
                if self.current_token_value() == ".":
                    self.next_token()
                    if self.check_identifier():
                        self.next_token()
                        if self.current_token_value() == "=":
                            self.next_token()
                            self.assignment_value()
                            if self.current_token_value() == ";":
                                self.next_token()
                                self.assignment_method()
                            else:
                                raise SyntaxError("Expected ';'")
                        else:
                            raise SyntaxError("Expected '='")
                    else:
                        raise SyntaxError("Expected a valid identifier")
                else:
                    raise SyntaxError("Expected '.'")
        except SyntaxError as e:
            self.save_error(e)
            self.assignment_method()

    def parameter(self):
        if self.check_type():
            if self.check_identifier():
                self.next_token()
                self.parameter_value_list()
            else:
                raise SyntaxError("Expected a valid identifier")
        else:
            if self.current_token_value() != ")":
                raise SyntaxError("Expected a valid type")

    def parameter_value_list(self):
        if self.current_token_value() == ",":
            self.next_token()
            self.parameter()

    def unary_expression(self):
        self.assignment_value()
        self.unary_expression_list()

    def unary_expression_list(self):
        if self.current_token_value() in ["++", "--"]:
            self.next_token()

    def multiplicative_expression(self):
        self.unary_expression()
        self.multiplicative_expression_list()

    def multiplicative_expression_list(self):
        if self.current_token_value() in ["*", "/"]:
            self.next_token()
            self.multiplicative_expression()

    def additive_expression(self):
        self.multiplicative_expression()
        self.additive_expression_list()

    def additive_expression_list(self):
        if self.current_token_value() in ["+", "-"]:
            self.next_token()
            self.additive_expression()

    def relational_expression(self):
        self.additive_expression()
        self.relational_expression_list()

    def relational_expression_list(self):
        if self.current_token_value() in ["<", ">", "<=", ">="]:
            self.next_token()
            self.relational_expression()

    def equality_expression(self):
        self.relational_expression()
        self.equality_expression_list()

    def equality_expression_list(self):
        if self.current_token_value() in ["!=", "=="]:
            self.next_token()
            self.equality_expression()

    def logical_not_expression(self):
        if self.current_token_value() == "!":
            self.next_token()
            self.logical_not_expression()
        else:
            self.equality_expression()

    def logical_or_expression_tail(self):
        if self.current_token_value() == "||":
            self.next_token()
            self.logical_and_expression()

    def logical_or_expression(self):
        if self.current_token_value() == "(":
            self.next_token()
            self.logical_not_expression()
            self.logical_or_expression_tail()
            if self.current_token_value() == ")":
                self.next_token()
                self.logical_and_expression_tail()
            else:
                raise SyntaxError("Expected ')'")
        else:
            self.logical_not_expression()
            self.logical_or_expression_tail()

    def logical_and_expression_tail(self):
        if self.current_token_value() == "&&":
            self.next_token()
            self.logical_and_expression()

    def logical_and_expression(self):
        if self.current_token_value() == "(":
            self.next_token()
            self.logical_or_expression()
            self.logical_and_expression_tail()
            if self.current_token_value() == ")":
                self.next_token()
                self.logical_and_expression_tail()
            else:
                raise SyntaxError("Expected ')'")
        else:
            self.logical_or_expression()
            self.logical_and_expression_tail()

    def command(self):
        if self.current_token_value() == "print":
            self.print_command()
        else:
            self.read_command()

    def statement(self):
        if self.current_token_value() == "if":
            self.if_statement()
        elif self.current_token_value() == "for":
            self.for_statement()
        elif self.current_token_value() == "pass":
            self.next_token()

    def assignment(self):
        self.definition_access_array()
        self.object_value()
        if self.current_token_value() == "=":
            self.next_token()
            self.logical_and_expression()
            if self.current_token_value() == ";":
                self.next_token()
            else:
                raise SyntaxError("Expected ';'")

    def statement_sequence(self):
        try:
            if self.current_token_value() in ["print", "read"]:
                self.command()
                self.statement_sequence()
            elif self.current_token_value() in ["if", "for", "pass"]:
                self.statement()
                self.statement_sequence()
            elif self.check_identifier():
                self.next_token()
                self.assignment()
                self.statement_sequence()
        except SyntaxError as e:
            self.save_error(e)
            self.statement_sequence()

    def if_statement(self):
        if self.current_token_value() == "if":
            self.next_token()
            if self.current_token_value() == "(":
                self.next_token()
                self.logical_and_expression()
                if self.current_token_value() == ")":
                    self.next_token()
                    if self.current_token_value() == "then":
                        self.next_token()
                        if self.current_token_value() == "{":
                            self.next_token()
                            self.statement_sequence()
                            if self.current_token_value() == "}":
                                self.next_token()
                                self.else_statement()
                            else:
                                raise SyntaxError(
                                    "Expected '}' after if statement body"
                                )
                        else:
                            raise SyntaxError("Expected '{' after 'then'")
                    else:
                        raise SyntaxError(
                            "Expected 'then' after condition in if statement"
                        )
                else:
                    raise SyntaxError("Expected ')' after expression in if statement")

    def else_statement(self):
        if self.current_token_value() == "else":
            self.next_token()
            if self.current_token_value() == "{":
                self.next_token()
                self.statement_sequence()
                if self.current_token_value() == "}":
                    self.next_token()
                else:
                    raise SyntaxError("Expected '}' after else statement body")

    def for_variable_initialization(self):
        if self.check_identifier():
            self.next_token()
            if self.current_token_value() == "=":
                self.next_token()
                if self.current_token_type() in ["NUM", "IDE"]:
                    self.next_token()
                else:
                    raise SyntaxError("Expected a valid value in For Loop variable")
            else:
                raise SyntaxError("Expected '='")
        else:
            raise SyntaxError("Expected a valid identifier")

    def for_statement(self):
        if self.current_token_value() == "for":
            self.next_token()
            if self.current_token_value() == "(":
                self.next_token()
                self.for_variable_initialization()
                self.next_token()
                self.logical_and_expression()
                if self.current_token_value() == ";":
                    self.next_token()
                    self.unary_expression()
                    if self.current_token_value() == ")":
                        self.next_token()
                        if self.current_token_value() == "{":
                            self.next_token()
                            self.statement_sequence()
                            if self.current_token_value() == "}":
                                self.next_token()
                            else:
                                raise SyntaxError("Expected '}' ")
                        else:
                            raise SyntaxError("Expected '{' ")
                    else:
                        raise SyntaxError("Expected ')'")
                else:
                    raise SyntaxError("Expected ';'")
            else:
                raise SyntaxError("Expected '('")

    def print_command(self):
        if self.current_token_value() == "print":
            self.next_token()
            if self.current_token_value() == "(":
                self.next_token()
                self.logical_and_expression()
                if self.current_token_value() == ")":
                    self.next_token()
                    if self.current_token_value() == ";":
                        self.next_token()
                    else:
                        raise SyntaxError("Expected ';'")
                else:
                    raise SyntaxError("Expected ')'")
            else:
                raise SyntaxError("Expected '('")

    def read_command(self):
        try:
            if self.current_token_value() == "read":
                self.next_token()
                if self.current_token_value() == "(":
                    self.next_token()
                    if self.check_identifier():
                        self.next_token()
                        self.object_value()
                        if self.current_token_value() == ")":
                            self.next_token()
                            if self.current_token_value() == ";":
                                self.next_token()
                            else:
                                raise SyntaxError("Expected ';'")
                        else:
                            raise SyntaxError("Expected ')'")
                    else:
                        raise SyntaxError("Expected a valid identifier")
                else:
                    raise SyntaxError("Expected '('")
        except SyntaxError as e:
            self.save_error(e)

    def program(self):
        self.constant_block()
        self.variable_block()
        self.class_block()
        self.object_block()
        self.main_class()
