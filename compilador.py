from config import palavras_reservadas

tokens = []
index = 0
errors = []
semantic_errors = []

key_words = list(palavras_reservadas)
delimiters = ["{", "}", ";"]
delimiters_with_keywords = delimiters + key_words



semantic_errors_table = {
    "variable_already_declared": "Variable with identifier already declared",
    "variable_incorrect_type": "Variable with incorrect type",
    "method_already_declared": "Method with identifier already declared",
    "class_already_declared": "Class with identifier already declared",
    "object_already_declared": "Object with identifier already declared",
    "variable_not_declared": "Variable with identifier not declared",
    "method_not_declared": "Method with identifier not declared",
    "class_not_declared": "Class with identifier not declared",
    "object_not_declared": "Object with identifier not declared",
    "identifier_not_declared": "Identifier not declared",
    # "method_not_return": "Method with identifier not return",
    # "method_return": "Method void with identifier return",
    # "method_return_type": "Method with incorrect return type",
    # "method_parameter_not_declared": "Method with parameter not declared",
    # "method_parameter_declared": "Method with parameter already declared",
    # "method_parameter_type": "Method with parameter incorrect type",
    # "method_parameter_missing": "Method with parameter missing",
    # "method_parameter_excess": "Method with parameter excess"
}


# LEXEMA | TIPO | ESCOPO | BLOCO
symbols_table = {}


lexeme = ""
type = ""
escope = ""
block = ""



def search_identifier(lexeme: str, escope: str):
    for symbol in symbols_table:
        if symbol["lexeme"] == lexeme and symbol["escope"] == escope:
            return symbol
    


def insert_identifier(lexeme: str, type: str, escope: str, bloco: str):
    symbols_table.append(
        {
            "lexeme": lexeme,
            "type": type,
            "escope": escope,
            "block": bloco,
        }
    )


def save_semantic_error(message):
    msg_error = f"Line {current_token_line()} - {message}"
    semantic_errors.append(msg_error)


def next_token():
    global index
    if index < len(tokens) - 1:
        index += 1


def current_token():
    return (
        tokens[index] if index < len(tokens) else dict(valor="", num_linha="", tipo="")
    )


def current_token_value() -> str:
    return current_token()["valor"]


def current_token_line() -> str:
    return current_token()["num_linha"]


def current_token_type() -> str:
    return current_token()["tipo"]


def synchronize(recovery_point):
    while current_token_value() not in recovery_point and current_token_value() != "":
        next_token()
    if current_token_value() in delimiters:
        next_token()


def save_error(e: SyntaxError, recovery_point=None):
    recovery_point = recovery_point or delimiters_with_keywords
    message = (
        f"{e.msg}, received '{current_token_value()}' in line {current_token_line()}"
    )
    errors.append(message)
    synchronize(recovery_point)


def check_identifier():
    global lexeme
    lexeme = current_token_value() 
    return current_token_type() == "IDE"


def value():
    return current_token_type() in [
        "NUM",
        "STR",
    ] or current_token_value() in [
        "true",
        "false",
    ]


def method_call():
    if check_identifier():
        next_token()
        if current_token_value() == "(":
            next_token()
            args_list()
            if current_token_value() == ")":
                next_token()
            else:
                raise SyntaxError("Expected ')'")
        else:
            raise SyntaxError("Expected '('")
    else:
        raise SyntaxError("Expected a valid identifier")


def object_value():
    if current_token_value() == ".":
        next_token()
        if check_identifier():
            next_token()
        else:
            raise SyntaxError("Expected a valid identifier")
    if current_token_value() == "->":
        next_token()
        method_call()


def array_possible_value():
    if check_identifier():
        next_token()
        object_value()
    elif current_token_type() == "NUM":
        next_token()
    else:
        raise SyntaxError("Expected a valid index for array")


def definition_access_array():
    if current_token_value() == "[":
        next_token()
        array_possible_value()
        if current_token_value() == "]":
            next_token()
            definition_access_array()
        else:
            raise SyntaxError("Expected ']'")


def check_type():
    global type
    if current_token_value() in ["int", "string", "real", "boolean"]:
        type = current_token_value()
        next_token()
        if current_token_value() == "[":
            type += "(Array)"
        definition_access_array() #int[b][c] a =
        return True
    return False


def possible_value():
    if check_identifier():
        next_token()
        object_value()
    elif value():
        next_token()


def array_value():
    if current_token_value() == "[":
        array()
    else:
        possible_value()


def more_array_value():
    if current_token_value() == ",":
        next_token()
        array_value()
        more_array_value()


def array():
    if current_token_value() == "[":
        next_token()
        array_value()
        more_array_value()
        if current_token_value() == "]":
            next_token()
        else:
            raise SyntaxError("Expected ']'")


# int a  = carro
def assignment_value():
    if check_identifier():
        symbol = search_identifier(lexeme, escope)
        if symbol:
            if symbol["type"] != type:
                save_semantic_error(semantic_errors_table["variable_incorrect_type"])
        else:
            save_semantic_error(semantic_errors_table["identifier_not_declared"])
        next_token()
        definition_access_array()
        object_value()
    elif value():
        next_token()
    elif current_token_value() == "[":
        array()
    else:
        raise SyntaxError("Expected a valid value")


def args_list():
    if check_identifier() or value() or current_token_value() == "[":
        logical_and_expression()
        assignment_value_list()


def assignment_value_list():
    if current_token_value() == ",":
        next_token()
        if check_identifier() or value() or current_token_value() == "[":
            args_list()
        else:
            raise SyntaxError("Expected a valid value")


def optional_value():
    if current_token_value() == "=":
        next_token()
        
        logical_and_expression()


def variable_block():
    global block
    if current_token_value() == "variables":
        block = "variables"
        next_token()
        if current_token_value() == "{":
            next_token()
            variable()
            if current_token_value() == "}":
                next_token()
            else:
                raise SyntaxError("Expected '}'")
        else:
            raise SyntaxError("Expected '{'")


def variable():
    try:
        if check_type():
            if check_identifier():
                if search_identifier(lexeme, escope):
                    save_semantic_error(semantic_errors_table["variable_already_declared"])
                else:
                    insert_identifier(lexeme, type, escope, block)
                next_token()
                optional_value()
                variable_same_line()
                if current_token_value() == ";":
                    next_token()
                    variable()
                else:
                    raise SyntaxError("Expected ';'")
            else:
                raise SyntaxError("Expected a valid identifier")
    except SyntaxError as e:
        save_error(e)
        variable()


def variable_same_line():
    try:
        if current_token_value() == ",":
            next_token()
            if check_identifier():
                next_token()
                optional_value()
                variable_same_line()
            else:
                raise SyntaxError("Expected a valid identifier")
    except SyntaxError as e:
        save_error(e)


def constant_block():
    if current_token_value() == "const":
        next_token()
        if current_token_value() == "{":
            next_token()
            constant()
            if current_token_value() == "}":
                next_token()
            else:
                raise SyntaxError("Expected '}")
        else:
            raise SyntaxError("Expected '{")


def constant():
    try:
        if check_type():
            if check_identifier():
                next_token()
                if current_token_value() == "=":
                    next_token()
                    logical_and_expression()
                    constant_same_line()
                    if current_token_value() == ";":
                        next_token()
                        constant()
                    else:
                        raise SyntaxError("Expected ';'")
                else:
                    raise SyntaxError("Expected '='")
            else:
                raise SyntaxError("Expected a valid identifier")
    except SyntaxError as e:
        save_error(e)
        constant()


def constant_same_line():
    try:
        if current_token_value() == ",":
            next_token()
            if check_identifier():
                next_token()
                if current_token_value() == "=":
                    next_token()
                    logical_and_expression()
                    constant_same_line()
                else:
                    raise SyntaxError("Expected ';'")
            else:
                raise SyntaxError("Expected a valid identifier")
    except SyntaxError as e:
        save_error(e)


def class_block():
    try:
        if current_token_value() == "class":
            next_token()
            if current_token_value() != "main":
                if check_identifier():
                    next_token()
                    class_extends()
                    if current_token_value() == "{":
                        next_token()
                        class_content()
                        if current_token_value() == "}":
                            next_token()
                            class_block()
                        else:
                            raise SyntaxError("Expected '}'")
                    else:
                        raise SyntaxError("Expected '{'")
                else:
                    raise SyntaxError("Expected a valid class identifier")
    except SyntaxError as e:
        sincronize_points = (
            ["objects", "class"] if "extends" in str(e) else delimiters_with_keywords
        )
        save_error(e, sincronize_points)
        class_block()


def class_extends():
    if current_token_value() == "extends":
        next_token()
        if check_identifier():
            next_token()
        else:
            raise SyntaxError("Expected a valid class identifier")
    else:
        if current_token_value() != "{":
            raise SyntaxError("Expected 'extends'")


def class_content():
    variable_block()
    constructor()
    methods()


def methods():
    if current_token_value() == "methods":
        next_token()
        if current_token_value() == "{":
            next_token()
            method()
            if current_token_value() == "}":
                next_token()
            else:
                if current_token_value() != "class":
                    raise SyntaxError("Expected '}'")


def method():
    try:
        tipo = check_type()
        if tipo or current_token_value() == "void":
            if current_token_value() == "void":
                next_token()
            if check_identifier():
                next_token()
                if current_token_value() == "(":
                    next_token()
                    parameter()
                    if current_token_value() == ")":
                        next_token()
                        if current_token_value() == "{":
                            next_token()
                            statement_sequence()
                            if tipo:
                                if current_token_value() == "return":
                                    next_token()
                                    assignment_value()
                                    if current_token_value() == ";":
                                        next_token()
                                        if current_token_value() == "}":
                                            next_token()
                                            method()
                                        else:
                                            raise SyntaxError("Expected '}'")
                                    else:
                                        raise SyntaxError("Expected ';'")
                                else:
                                    raise SyntaxError("Expected 'return'")
                            else:
                                if current_token_value() == "}":
                                    next_token()
                                    method()
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
            if "}" in str(e) and current_token_value() == "return"
            else delimiters_with_keywords
        )
        save_error(e, sinc)
        method()


def constructor():
    if current_token_value() == "constructor":
        next_token()
        if current_token_value() == "(":
            next_token()
            parameter()
            if current_token_value() == ")":
                next_token()
                if current_token_value() == "{":
                    next_token()
                    assignment_method()
                    if current_token_value() == "}":
                        next_token()
                    else:
                        raise SyntaxError("Expected '}'")
                else:
                    raise SyntaxError("Expected '{'")
            else:
                raise SyntaxError("Expected ')'")
        else:
            raise SyntaxError("Expected '('")


def main_class():
    if current_token_value() == "class":
        next_token()
        if current_token_value() == "main":
            next_token()
            if current_token_value() == "{":
                next_token()
                main_class_content()
                if current_token_value() == "}":
                    next_token()
                else:
                    raise SyntaxError("Expected '}'")
            else:
                raise SyntaxError("Expected '{'")
        else:
            raise SyntaxError("Expected 'main'")


def main_class_content():
    variable_block()
    object_block()
    statement_sequence()


def object_block():
    if current_token_value() == "objects":
        next_token()
        if current_token_value() == "{":
            next_token()
            object_declaration()
            if current_token_value() == "}":
                next_token()
            else:
                raise SyntaxError("Expected '}'")
        else:
            raise SyntaxError("Expected '{'")


def object_declaration():
    try:
        if check_identifier():
            next_token()
            if check_identifier():
                next_token()
                if current_token_value() == "=":
                    next_token()
                    if check_identifier():
                        next_token()
                        if current_token_value() == "->":
                            next_token()
                            if current_token_value() == "constructor":
                                next_token()
                                if current_token_value() == "(":
                                    next_token()
                                    args_list()
                                    if current_token_value() == ")":
                                        next_token()
                                        object_same_line()
                                        if current_token_value() == ";":
                                            next_token()
                                            object_declaration()
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
        save_error(e)
        object_declaration()


def object_same_line():
    if current_token_value() == ",":
        next_token()
        if check_identifier():
            next_token()
            if current_token_value() == "=":
                next_token()
                if check_identifier():
                    next_token()
                    if current_token_value() == "->":
                        next_token()
                        if current_token_value() == "constructor":
                            next_token()
                            if current_token_value() == "(":
                                next_token()
                                args_list()
                                if current_token_value() == ")":
                                    next_token()
                                    object_same_line()
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


def assignment_method():
    try:
        if current_token_value() == "this":
            next_token()
            if current_token_value() == ".":
                next_token()
                if check_identifier():
                    next_token()
                    if current_token_value() == "=":
                        next_token()
                        assignment_value()
                        if current_token_value() == ";":
                            next_token()
                            assignment_method()
                        else:
                            raise SyntaxError("Expected ';'")
                    else:
                        raise SyntaxError("Expected '='")
                else:
                    raise SyntaxError("Expected a valid identifier")
            else:
                raise SyntaxError("Expected '.'")
    except SyntaxError as e:
        save_error(e)
        assignment_method()


def parameter():
    if check_type():
        if check_identifier():
            next_token()
            parameter_value_list()
        else:
            raise SyntaxError("Expected a valid identifier")
    else:
        if current_token_value() != ")":
            raise SyntaxError("Expected a valid type")


def parameter_value_list():
    if current_token_value() == ",":
        next_token()
        parameter()


def unary_expression():
    assignment_value()
    unary_expression_list()


def unary_expression_list():
    if current_token_value() in ["++", "--"]:
        next_token()


def multiplicative_expression():
    unary_expression()
    multiplicative_expression_list()


def multiplicative_expression_list():
    if current_token_value() in ["*", "/"]:
        next_token()
        multiplicative_expression()


def additive_expression():
    multiplicative_expression()
    additive_expression_list()


def additive_expression_list():
    if current_token_value() in ["+", "-"]:
        next_token()
        additive_expression()


def relational_expression():
    additive_expression()
    relational_expression_list()


def relational_expression_list():
    if current_token_value() in ["<", ">", "<=", ">="]:
        next_token()
        relational_expression()


def equality_expression():
    relational_expression()
    equality_expression_list()


def equality_expression_list():
    if current_token_value() in ["!=", "=="]:
        next_token()
        equality_expression()


def logical_not_expression():
    if current_token_value() == "!":
        next_token()
        logical_not_expression()
    else:
        equality_expression()


def logical_or_expression_tail():
    if current_token_value() == "||":
        next_token()
        logical_and_expression()


def logical_or_expression():
    if current_token_value() == "(":
        next_token()
        logical_not_expression()
        logical_or_expression_tail()
        if current_token_value() == ")":
            next_token()
            logical_and_expression_tail()
        else:
            raise SyntaxError("Expected ')'")
    else:
        logical_not_expression()
        logical_or_expression_tail()


def logical_and_expression_tail():
    if current_token_value() == "&&":
        next_token()
        logical_and_expression()


def logical_and_expression():
    if current_token_value() == "(":
        next_token()
        logical_or_expression()
        logical_and_expression_tail()
        if current_token_value() == ")":
            next_token()
            logical_and_expression_tail()
        else:
            raise SyntaxError("Expected ')'")
    else:
        logical_or_expression()
        logical_and_expression_tail()


def command():
    if current_token_value() == "print":
        print_command()
    else:
        read_command()


def statement():
    if current_token_value() == "if":
        if_statement()
    elif current_token_value() == "for":
        for_statement()
    elif current_token_value() == "pass":
        next_token()


def assignment():
    definition_access_array()
    object_value()
    if current_token_value() == "=":
        next_token()
        logical_and_expression()
        if current_token_value() == ";":
            next_token()
        else:
            raise SyntaxError("Expected ';'")


def statement_sequence():
    try:
        if current_token_value() in ["print", "read"]:
            command()
            statement_sequence()
        elif current_token_value() in ["if", "for", "pass"]:
            statement()
            statement_sequence()
        elif check_identifier():
            next_token()
            assignment()
            statement_sequence()
    except SyntaxError as e:
        save_error(e)
        statement_sequence()


def if_statement():
    if current_token_value() == "if":
        next_token()
        if current_token_value() == "(":
            next_token()
            logical_and_expression()
            if current_token_value() == ")":
                next_token()
                if current_token_value() == "then":
                    next_token()
                    if current_token_value() == "{":
                        next_token()
                        statement_sequence()
                        if current_token_value() == "}":
                            next_token()
                            else_statement()
                        else:
                            raise SyntaxError("Expected '}' after if statement body")
                    else:
                        raise SyntaxError("Expected '{' after 'then'")
                else:
                    raise SyntaxError("Expected 'then' after condition in if statement")
            else:
                raise SyntaxError("Expected ')' after expression in if statement")


def else_statement():
    if current_token_value() == "else":
        next_token()
        if current_token_value() == "{":
            next_token()
            statement_sequence()
            if current_token_value() == "}":
                next_token()
            else:
                raise SyntaxError("Expected '}' after else statement body")


def for_variable_initialization():
    if check_identifier():
        next_token()
        if current_token_value() == "=":
            next_token()
            if current_token_type() in ["NUM", "IDE"]:
                next_token()
            else:
                raise SyntaxError("Expected a valid value in For Loop variable")
        else:
            raise SyntaxError("Expected '='")
    else:
        raise SyntaxError("Expected a valid identifier")


def for_statement():
    if current_token_value() == "for":
        next_token()
        if current_token_value() == "(":
            next_token()
            for_variable_initialization()
            next_token()
            logical_and_expression()
            if current_token_value() == ";":
                next_token()
                unary_expression()
                if current_token_value() == ")":
                    next_token()
                    if current_token_value() == "{":
                        next_token()
                        statement_sequence()
                        if current_token_value() == "}":
                            next_token()
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


def print_command():
    if current_token_value() == "print":
        next_token()
        if current_token_value() == "(":
            next_token()
            logical_and_expression()
            if current_token_value() == ")":
                next_token()
                if current_token_value() == ";":
                    next_token()
                else:
                    raise SyntaxError("Expected ';'")
            else:
                raise SyntaxError("Expected ')'")
        else:
            raise SyntaxError("Expected '('")


def read_command():
    try:
        if current_token_value() == "read":
            next_token()
            if current_token_value() == "(":
                next_token()
                if check_identifier():
                    next_token()
                    object_value()
                    if current_token_value() == ")":
                        next_token()
                        if current_token_value() == ";":
                            next_token()
                        else:
                            raise SyntaxError("Expected ';'")
                    else:
                        raise SyntaxError("Expected ')'")
                else:
                    raise SyntaxError("Expected a valid identifier")
            else:
                raise SyntaxError("Expected '('")
    except SyntaxError as e:
        save_error(e)


def program():
    escope = "global"
    constant_block()
    variable_block()
    class_block()
    object_block()
    escope = "main"
    main_class()


def CompilerParse(tokens_list: list):
    global tokens, errors
    tokens = tokens_list
    try:
        program()
    except SyntaxError as e:
        save_error(e)
    error_messages = "\n".join(errors) if errors else "Sucesso!"
    return error_messages
