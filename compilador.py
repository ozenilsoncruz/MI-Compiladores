from config import palavras_reservadas

tokens = []
index = 0
errors = []
semantic_errors = []

key_words = list(palavras_reservadas)
delimiters = ["{", "}", ";"]
delimiters_with_keywords = delimiters + key_words


semantic_errors_table = {
    "already_declared": "Identifier already declared",
    "not_declared": "Identifier not declared",
    "incorrect_type": "Incorrect type",
}


# LEXEMA | TIPO | ESCOPO | BLOCO
symbols_table = []


lexeme = ""
type = ""
escope = ""

expected_type = ""
current_parameter = {}
parameter_list = []

argument_list = []

type_equivalent = {
    "int": "NUM",
    "real": "NUM",
    "string": "STR",
    "boolean": "KEY",
}

is_argument = False


def search_identifier():
    global lexeme, escope

    for symbol in symbols_table:
        if symbol["lexeme"] == lexeme and symbol["escope"] == escope:
            return symbol


def insert_identifier():
    global lexeme, type, escope

    symbols_table.append(
        {
            "lexeme": lexeme,
            "type": type,
            "escope": escope,
        }
    )


def save_parameter():
    global current_parameter
    parameter_list.append(current_parameter)
    current_parameter = {}


def save_argument():
    global current_parameter
    argument_list.append(current_parameter)
    current_parameter = {}


def update_identifier_parameters():
    global lexeme, escope, parameter_list
    for symbol in symbols_table:
        if symbol["lexeme"] == lexeme and symbol["escope"] == escope:
            symbol["parameters_list"] = parameter_list
            break
    parameter_list = []


def compare_lists(expected_list):
    if len(expected_list) != len(argument_list):
        save_semantic_error(
            f"Incorrect number of arguments, expected {len(expected_list)}, received {len(argument_list)}"
        )
        return False
    for i, (dict1, dict2) in enumerate(zip(expected_list, argument_list), start=1):
        if dict1["type"] != dict2["type"]:
            save_semantic_error(
                f"Incorrect type of arguments, expected {dict1['type']} in parameter number {i}, received {dict2['type']}"
            )
            return False
    return True


def get_key_from_value(value):
    for key, val in type_equivalent.items():
        if val == value:
            return key
    return None


def save_semantic_error(message: str):
    global lexeme
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


def check_identifier_syntactic():
    return current_token_type() == "IDE"


def check_object_declaration():
    global lexeme
    if lexeme not in type_equivalent and not any(
        symbol["lexeme"] == lexeme and "Class" in symbol["escope"]
        for symbol in symbols_table
    ):
        save_semantic_error(f"Object with undefined type '{lexeme}'")
    else:
        return lexeme


def value():
    return current_token_type() in [
        "NUM",
        "STR",
    ] or current_token_value() in [
        "true",
        "false",
    ]


def method_call():
    global type, lexeme, escope, argument_list, is_argument

    if check_identifier():
        symbol = search_identifier()
        escope = "Class " + type
        symbol = search_identifier()
        if not symbol:
            save_semantic_error(f"Method '{lexeme}' not declared")
        next_token()
        if current_token_value() == "(":
            next_token()
            argument_list = []
            args_list()
            if symbol:
                type = symbol["type"]
                compare_lists(symbol["parameters_list"])
            if current_token_value() == ")":
                is_argument = False
                next_token()
            else:
                raise SyntaxError("Expected ')'")
        else:
            raise SyntaxError("Expected '('")
    else:
        raise SyntaxError("Expected a valid identifier")


def object_value():
    global type
    if current_token_value() == ".":
        next_token()
        if check_identifier():
            # TODO: Check if the attribute exists
            next_token()
        else:
            raise SyntaxError("Expected a valid identifier")
    if current_token_value() == "->":
        symbol = search_identifier()
        type = symbol["type"]
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
    global type, expected_type
    if current_token_value() in ["int", "string", "real", "boolean"]:
        type = current_token_value()
        next_token()
        if current_token_value() == "[":
            type += "(Array)"
        definition_access_array()  # int[b][c] a =
        expected_type = type
        return True
    return False


def check_type_syntactic():
    if current_token_value() in ["int", "string", "real", "boolean"]:
        type = current_token_value()
        next_token()
        if current_token_value() == "[":
            type += "(Array)"
        definition_access_array()  # int[b][c] a =
        return type
    return None


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
    global type_equivalent, current_parameter, type
    if check_identifier():
        symbol = search_identifier()
        if not symbol:
            save_semantic_error(semantic_errors_table["not_declared"])
            type = ""
        next_token()
        definition_access_array()
        object_value()
        if expected_type != type and not is_argument:
            save_semantic_error(semantic_errors_table["incorrect_type"])
        type = symbol["type"]
        current_parameter = {"lexeme": lexeme, "type": type}
        save_argument()
    elif value():
        if (
            type_equivalent.get(type) is not None
            and current_token_type() != type_equivalent[type]
            and not is_argument
        ):
            save_semantic_error(semantic_errors_table["incorrect_type"])
        type = current_token_type()
        current_parameter = {"lexeme": lexeme, "type": get_key_from_value(type)}
        save_argument()
        next_token()
    elif current_token_value() == "[":
        array()
        current_parameter = {"lexeme": lexeme, "type": type}
        save_argument()
    else:
        raise SyntaxError("Expected a valid value")


def args_list():
    global is_argument
    is_argument = True
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
    global is_argument
    if current_token_value() == "=":
        next_token()
        is_argument = False
        logical_and_expression()


def variable_block():
    global escope
    if current_token_value() == "variables":
        if "Class" not in escope:
            escope = "global"
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
                if search_identifier():
                    save_semantic_error(semantic_errors_table["already_declared"])
                else:
                    insert_identifier()
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
                if search_identifier():
                    save_semantic_error(semantic_errors_table["already_declared"])
                else:
                    insert_identifier()
                next_token()
                optional_value()
                variable_same_line()
            else:
                raise SyntaxError("Expected a valid identifier")
    except SyntaxError as e:
        save_error(e)


def constant_block():
    global escope
    if current_token_value() == "const":
        escope = "global"
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
    global is_argument
    try:
        if check_type():
            if check_identifier():
                if search_identifier():
                    save_semantic_error(semantic_errors_table["already_declared"])
                else:
                    insert_identifier()
                next_token()
                if current_token_value() == "=":
                    next_token()
                    is_argument = False
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
    global is_argument
    try:
        if current_token_value() == ",":
            next_token()
            if check_identifier():
                if search_identifier():
                    save_semantic_error(semantic_errors_table["already_declared"])
                else:
                    insert_identifier()
                next_token()
                if current_token_value() == "=":
                    next_token()
                    is_argument = False
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
        global escope, type, lexeme
        if current_token_value() == "class":
            next_token()
            if current_token_value() != "main":
                if check_identifier():
                    escope = "global"
                    type_equivalent[lexeme] = "IDE"
                    type = ""
                    if search_identifier():
                        save_semantic_error(semantic_errors_table["already_declared"])
                    else:
                        insert_identifier()
                    next_token()
                    current_lexeme = lexeme
                    class_extends()
                    if current_token_value() == "{":
                        next_token()
                        escope = "Class " + current_lexeme
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
            if not search_identifier():
                save_semantic_error(semantic_errors_table["not_declared"])
            next_token()
        else:
            raise SyntaxError("Expected a valid class identifier")
    else:
        if current_token_value() != "{":
            raise SyntaxError("Expected 'extends'")


def class_content():
    global escope
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
    global lexeme, escope
    try:
        tipo = check_type()
        if tipo or current_token_value() == "void":
            if current_token_value() == "void":
                next_token()
            if check_identifier():
                if search_identifier():
                    save_semantic_error(semantic_errors_table["already_declared"])
                else:
                    insert_identifier()
                next_token()
                if current_token_value() == "(":
                    next_token()
                    parameter()
                    update_identifier_parameters()
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
    global lexeme, escope
    if current_token_value() == "constructor":
        next_token()
        if current_token_value() == "(":
            next_token()
            parameter()
            current_escope = escope
            lexeme = escope.split(" ")[1]
            escope = "global"
            update_identifier_parameters()
            escope = current_escope
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
    global escope
    if current_token_value() == "objects":
        escope = "global"
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
    global type, lexeme, escope, argument_list
    try:
        if check_identifier():
            type = lexeme
            current_type = type
            if not search_identifier():
                save_semantic_error(f"Object with undefined type '{lexeme}'")
            next_token()
            if check_identifier():
                if search_identifier():
                    save_semantic_error(semantic_errors_table["already_declared"])
                else:
                    insert_identifier()
                next_token()
                if current_token_value() == "=":
                    next_token()
                    if check_identifier():
                        if type and type != lexeme:
                            save_semantic_error(
                                f"Object with mismatch initialization type '{lexeme}'"
                            )
                        next_token()
                        if current_token_value() == "->":
                            next_token()
                            if current_token_value() == "constructor":
                                next_token()
                                if current_token_value() == "(":
                                    next_token()
                                    argument_list = []
                                    args_list()
                                    lexeme = current_type
                                    escope = "global"
                                    symbol = search_identifier()
                                    if symbol:
                                        compare_lists(symbol["parameters_list"])
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
    global type, lexeme, escope, argument_list
    if current_token_value() == ",":
        next_token()
        if check_identifier():
            if search_identifier():
                save_semantic_error(semantic_errors_table["already_declared"])
            else:
                insert_identifier()
            next_token()
            if current_token_value() == "=":
                next_token()
                if check_identifier():
                    if type and type != lexeme:
                        save_semantic_error(
                            f"Object with mismatch initialization type '{lexeme}'"
                        )
                    next_token()
                    if current_token_value() == "->":
                        next_token()
                        if current_token_value() == "constructor":
                            next_token()
                            if current_token_value() == "(":
                                next_token()
                                argument_list = []
                                args_list()
                                lexeme = type
                                escope = "global"
                                symbol = search_identifier()
                                if symbol:
                                    compare_lists(symbol["parameters_list"])
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
    global is_argument
    try:
        if current_token_value() == "this":
            next_token()
            if current_token_value() == ".":
                next_token()
                if check_identifier():
                    next_token()
                    if current_token_value() == "=":
                        next_token()
                        is_argument = False
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
    global current_parameter
    type = check_type_syntactic()
    if type:
        if check_identifier_syntactic():
            lexeme = current_token_value()
            current_parameter = {"lexeme": lexeme, "type": type}
            save_parameter()
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
    global is_argument
    definition_access_array()
    object_value()
    if current_token_value() == "=":
        next_token()
        is_argument = False
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

    constant_block()
    variable_block()
    class_block()
    object_block()

    main_class()
    print(symbols_table)
    print()
    print(semantic_errors)


def CompilerParse(tokens_list: list):
    global tokens, errors
    tokens = tokens_list
    try:
        program()
    except SyntaxError as e:
        save_error(e)
    error_messages = "\n".join(errors) if errors else "Sucesso!"
    return error_messages
