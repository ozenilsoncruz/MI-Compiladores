from analisadorLexico import lexico, salvar_arquivo
from config import palavras_reservadas
import os
import re

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
def synchronize(recovery_point=delimiters):
    while current_token_value() not in recovery_point and current_token_value() != "":
        print(current_token_value())
        next_token()


# Salva o erro passado na lista de erros
def save_error(e: SyntaxError, recovery_point=delimiters):
    message = (
        f"{e.msg}, received {current_token_value()} in line {current_token_line()}"
    )
    errors.append(message)
    synchronize(recovery_point)


# Verifica se um token é do tipo IDE
def check_identifier():
    return current_token_type() == "IDE"


# ------------------------------------------------------------------
# Função para análise sintática da regra <Value>
def value():
    return current_token_type() in ["NUM", "STR"] or current_token_value in [
        "true",
        "false",
    ]


# Função para análise sintática da regra <Object-Value>
def object_value():
    try:
        if current_token_value() == ".":
            next_token()
            if check_identifier():
                next_token()
            else:
                raise SyntaxError("Expected a valid identifier")
    except SyntaxError as e:
        save_error(e, delimiters_with_keywords)


# Verifica se o que está dento dos colchetes é um valor válido
def array_possible_value():
    try:
        if check_identifier():
            next_token()
            object_value()
        elif current_token_type() == "NUM":
            next_token()
        else:
            raise SyntaxError("Expected ']'")
    except SyntaxError as e:
        save_error(e, delimiters_with_keywords)


# Verifica se a produção é um tipo array.
def definition_access_array():
    try:
        if current_token_value() == "[":
            next_token()
            array_possible_value()
            if current_token_value() == "]":
                next_token()
                definition_access_array()
            else:
                raise SyntaxError("Expected ']'")
    except SyntaxError as e:
        save_error(e, delimiters_with_keywords)
        definition_access_array()


# Verifica se um token pertence ao TYPE
def check_type():
    if current_token_value() in ["int", "string", "real", "boolean"]:
        next_token()
        definition_access_array()
        return True
    return False


# Função para análise sintática da regra <Possible-Value>
def possible_value():
    if check_identifier():
        next_token()
        object_value()
    elif value():
        next_token()


# Função para análise sintática da regra <Array-Value>
def array_value():
    if current_token_value() == "[":
        array()
    else:
        possible_value()


# Função para análise sintática da regra <More-Array-Value>
def more_array_value():
    if current_token_value() == ",":
        next_token()
        array_value()
        more_array_value()


# Função para análise sintática da regra <Array>
def array():
    try:
        if current_token_value() == "[":
            next_token()
            array_value()
            more_array_value()
            if current_token_value() == "]":
                next_token()
            else:
                raise SyntaxError("Expected ']'")
    except SyntaxError as e:
        save_error(e, delimiters_with_keywords)


# Função para análise sintática da regra <Assignment-Value>
def assignment_value():
    if check_identifier():
        next_token()
        definition_access_array()
        object_value()
    elif value():
        next_token()
    elif array():
        pass


# Função para análise sintática da regra <Args-List>
def args_list():
    assignment_value()
    assignment_value_list()


# Função para análise sintática da regra <Assignment-Value-List>
def assignment_value_list():
    if current_token_value() == ",":
        next_token()
        args_list()


# Função para análise sintática da regra <Optional-Value>
def optional_value():
    if current_token_value() == "=":
        next_token()
        assignment_value()


# Função para análise sintática da regra <Variable-Block>
def variable_block():
    try:
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
    except SyntaxError as e:
        save_error(e)


# Função para análise sintática da regra <Variable>
def variable():
    try:
        if check_type():
            if check_identifier():
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
        save_error(e, delimiters_with_keywords)
        variable()


# Função para análise sintática da regra <Variable-Same-Line>
# Da pra usar um loop while
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
        save_error(e, delimiters_with_keywords)


# Função para análise sintática da regra <Constant-Block>
def constant_block():
    if current_token_value() == "const":
        next_token()
        if current_token_value() == "{":
            next_token()
            constant()
            if current_token_value() == "}":
                next_token()


# Função para análise sintática da regra <Constant>
def constant():
    type_ = current_token()
    next_token()

    ide = current_token()
    next_token()

    if current_token_value() == "=":
        next_token()
        assignment_value()

    constant_same_line()

    if current_token_value() == ";":
        next_token()
        constant()


# Função para análise sintática da regra <Constant-Same-Line>
def constant_same_line():
    if current_token_value() == ",":
        next_token()
        ide = current_token()
        next_token()
        if current_token_value() == "=":
            next_token()
            assignment_value()
        constant_same_line()


def main():
    global tokens, index
    pasta = "./files"
    arquivos = os.listdir(pasta)

    for arquivo in arquivos:
        tokens = lexico(pasta=pasta, arquivo=arquivo)
        index = 0
        # Chame a função correspondente à regra inicial aqui
        # Por exemplo, para a regra <Variable-Block>:
        variable_block()

        print(errors)
        # print(current_token())
        # next_token()
        # print(current_token())


main()
