from analisadorLexico import lexico, salvar_arquivo
from config import palavras_reservadas
import os

# Variáveis globais
tokens = []
index = 0
errors = []

key_words = list(palavras_reservadas)
delimiters = ["{", "}", ";"]
delimiters_with_keywords = delimiters + key_words


# Função auxiliar para avançar o índice da lista de tokens
def next_token():
    global index
    if index < len(tokens) - 1:
        index += 1


# Função auxiliar para obter o token atual
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


# Função de recuperação que sincroniza o analisador até encontrar um ponto de recuperação
def synchronize(recovery_point):
    while current_token_value() not in recovery_point and current_token_value() != "":
        print(current_token_value())
        next_token()
    if current_token_value() in delimiters:
        next_token()


# Salva o erro passado na lista de erros
def save_error(e: SyntaxError, recovery_point=delimiters_with_keywords):
    message = (
        f"{e.msg}, received '{current_token_value()}' in line {current_token_line()}"
    )
    errors.append(message)
    synchronize(recovery_point)


# Verifica se um token é do tipo IDE
def check_identifier():
    return current_token_type() == "IDE"


# --------------------------------------------
# Funções para análise sintática de Classes e Objetos

def class_block():
    try:
        if current_token_value() == "class":
            next_token()
            if check_identifier():
                next_token()
                class_extends()
                if current_token_value() == "{":
                    next_token()
                    class_content()
                    if current_token_value() == "}":
                        next_token()
                    else:
                        raise SyntaxError("Expected '}'")
                else:
                    raise SyntaxError("Expected '{'")
            else:
                raise SyntaxError("Expected a valid identifier")
    except SyntaxError as e:
        save_error(e, delimiters)


def class_extends():
    if current_token_value() == "extends":
        next_token()
        if check_identifier():
            next_token()


def class_content():
    variable_block()
    constructor()
    methods()


def variable_block():
    if current_token_value() == "variables":
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
    if check_type():
        next_token()
        if check_identifier():
            next_token()
            optional_value()
            variable_same_line()
            if current_token_value() == ";":
                next_token()
                variable()
            else:
                if current_token_value() != "}":
                    raise SyntaxError("Expected ';'")
        else:
            raise SyntaxError("Expected a valid identifier")


def variable_same_line():
    if current_token_value() == ",":
        next_token()
        if check_identifier():
            next_token()
            optional_value()
            variable_same_line()
        else:
            raise SyntaxError("Expected a valid identifier")


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
    if check_type():
        next_token()
        if check_identifier():
            next_token()
            if current_token_value() == "=":
                next_token()
                assignment_value()
                constant_same_line()
                if current_token_value() == ";":
                    next_token()
                    constant()
                else:
                    if current_token_value() != "}":
                        raise SyntaxError("Expected ';'")
            else:
                raise SyntaxError("Expected '='")
        else:
            raise SyntaxError("Expected a valid identifier")


def constant_same_line():
    if current_token_value() == ",":
        next_token()
        if check_identifier():
            next_token()
            if current_token_value() == "=":
                next_token()
                assignment_value()
                constant_same_line()
            else:
                raise SyntaxError("Expected ';'")
        else:
            raise SyntaxError("Expected a valid identifier")


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


def assignment_method():
    if current_token_value() == "this.":
        next_token()
        if check_identifier():
            next_token()
            optional_value()
            if current_token_value() == ";":
                next_token()
                assignment_method()


def optional_value():
    if current_token_value() == "=":
        next_token()
        assignment_value()


def methods():
    if current_token_value() == "methods":
        next_token()
        if current_token_value() == "{":
            next_token()
            method()
            if current_token_value() == "}":
                next_token()
            else:
                raise SyntaxError("Expected '}'")
        else:
            raise SyntaxError("Expected '{'")


def method():
    if check_type() or current_token_value() == "void":
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
                        if current_token_value() == "}":
                            next_token()
                            if current_token_value() == "return":
                                next_token()
                                value()
                                if current_token_value() == ";":
                                    next_token()
                                    method()
                            else:
                                method()


def parameter():
    if check_identifier():
        next_token()
        parameter_value_list()


def parameter_value_list():
    if current_token_value() == ",":
        next_token()
        parameter()


def statement_sequence():
    if current_token_value() == "{":
        next_token()
        statement()
        if current_token_value() == "}":
            next_token()
        else:
            raise SyntaxError("Expected '}'")


def statement():
    if current_token_value() == "if":
        next_token()
        condition()
        if current_token_value() == "then":
            next_token()
            statement_sequence()
            else_statement()


def else_statement():
    if current_token_value() == "else":
        next_token()
        statement_sequence()


def for_statement():
    if current_token_value() == "for":
        next_token()
        if current_token_value() == "(":
            next_token()
            variable()
            if current_token_value() == ";":
                next_token()
                logical_and_expression()
                if current_token_value() == ";":
                    next_token()
                    unary_expression()
                    if current_token_value() == ")":
                        next_token()
                        statement_sequence()


def print_command():
    if current_token_value() == "print":
        next_token()
        if current_token_value() == "(":
            next_token()
            possible_value()
            if current_token_value() == ")":
                next_token()
                if current_token_value() == ";":
                    next_token()


def read_command():
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


def condition():
    if current_token_value() == "(":
        next_token()
        logical_and_expression()
        if current_token_value() == ")":
            next_token()


def logical_not_expression():
    if current_token_value() == "!":
        next_token()
        equality_expression()
    else:
        equality_expression()


def logical_or_expression():
    logical_not_expression()
    if current_token_value() == "||":
        next_token()
        logical_not_expression()


def logical_and_expression():
    logical_or_expression()
    if current_token_value() == "&&":
        next_token()
        logical_or_expression()


def value():
    return current_token_type() in ["NUM", "STR"] or current_token_value() in ["true", "false"]


def object_value():
    if current_token_value() == ".":
        next_token()
        if check_identifier():
            next_token()


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
    if current_token_value() in ["int", "string", "real", "boolean"]:
        next_token()
        definition_access_array()
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
    else:
        raise SyntaxError("Expected '['")


def assignment_value():
    if check_identifier():
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
    assignment_value()
    assignment_value_list()


def assignment_value_list():
    if current_token_value() == ",":
        next_token()
        args_list()


def optional_value():
    if current_token_value() == "=":
        next_token()
        assignment_value()


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
    if check_identifier():
        next_token()
        if check_identifier():
            next_token()
            if current_token_value() == "=":
                next_token()
                if current_token_value() == "Carro->constructor":
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
                    raise SyntaxError("Expected 'Carro->constructor'")
            else:
                raise SyntaxError("Expected '='")
        else:
            raise SyntaxError("Expected a valid identifier")


def object_same_line():
    if current_token_value() == ",":
        next_token()
        object_declaration()


def statement_sequence_list():
    if current_token_value() == "{":
        next_token()
        statement()
        if current_token_value() == "}":
            next_token()
        else:
            raise SyntaxError("Expected '}'")


def unary_expression():
    access_expression()
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
        unary_expression()

def additive_expression():
    multiplicative_expression()
    additive_expression_list()

def additive_expression_list():
    if current_token_value() in ["+", "-"]:
        next_token()
        multiplicative_expression()

def relational_expression():
    additive_expression()
    relational_expression_list()

def relational_expression_list():
    if current_token_value() in ["<", ">", "<=", ">="]:
        next_token()
        additive_expression()

def equality_expression():
    relational_expression()
    equality_expression_list()

def equality_expression_list():
    if current_token_value() in ["!=", "=="]:
        next_token()
        relational_expression()
        

def access_expression():
    primary_expression()
    access_expression_list()


def access_expression_list():
    if current_token_value() in ["->", ".", "["]:
        while current_token_value() in ["->", ".", "["]:
            if current_token_value() == "->":
                next_token()
                if check_identifier():
                    next_token()
                else:
                    raise SyntaxError("Expected a valid identifier after '->'")
            elif current_token_value() == ".":
                next_token()
                if check_identifier():
                    next_token()
                else:
                    raise SyntaxError("Expected a valid identifier after '.'")
            elif current_token_value() == "[":
                next_token()
                expression()
                if current_token_value() == "]":
                    next_token()
                else:
                    raise SyntaxError("Expected ']' after '['")

             
def primary_expression():
    if check_identifier():
        next_token()
    elif current_token_type() == "NUM":
        next_token()
    elif current_token_type() == "BOOL":
        next_token()
    elif current_token_type() == "STR":
        next_token()
    elif current_token_value() == "(":
        next_token()
        expression()
        if current_token_value() == ")":
            next_token()
        else:
            raise SyntaxError("Expected ')' after '('")
    else:
        raise SyntaxError("Expected a valid primary expression")


def expression():
    declaration_expression()
    assignment_expression()


def declaration_expression():
    if check_type():
        next_token()
        ide_list()


def ide_list():
    if check_identifier():
        next_token()
        ide_list_list()

def ide_list_list():
    if current_token_value() == ",":
        next_token()
        ide_list()


def assignment_expression():
    if check_identifier():
        next_token()
        access_expression_list()
        if current_token_value() == "=":
            next_token()
            logical_and_expression()
        else:
            raise SyntaxError("Expected '=' after assignment expression")



def program():
    constant_block()
    variable_block()
    class_block()
    object_block()
    main_class()


# Código principal
def main():
    global tokens, index
    pasta = "./files"
    arquivos = os.listdir(pasta)

    for arquivo in arquivos:
        tokens = lexico(pasta=pasta, arquivo=arquivo)
        index = 0
        try:
            program()
        except SyntaxError as e:
            save_error(e)

        print(errors)


if __name__ == "__main__":
    main()
