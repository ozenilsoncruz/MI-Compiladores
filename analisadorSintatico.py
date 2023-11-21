from analisadorLexico import lexico, salvar_arquivo
import os
import re

# Variáveis globais
tokens = []
index = 0
errors = []


# Função auxiliar para avançar para o próximo token
def next_token():
    global index
    index += 1


# Função auxiliar para obter o token atual
def current_token():
    return tokens[index] if index < len(tokens) else None


def current_token_value() -> str:
    return current_token()["valor"]


def current_token_line() -> str:
    return current_token()["num_linha"]


def current_token_type() -> str:
    return current_token()["tipo"]


def if_else_check(funcoes: list, expect: str):
    try:
        if current_token_value() == expect:
            for funcao in funcoes:
                funcao()
        else:
            raise SyntaxError(f"Expected {expect}")
    except SyntaxError as e:
        save_error(e)


# Função de recuperação que sincroniza o analisador até encontrar um delimitador
def synchronize():
    delimiters = [";", "{", "}"]
    while current_token_value() not in delimiters:
        print(current_token_value())
        next_token()


# Salva o erro passado na lista de erros
def save_error(e: SyntaxError):
    message = (
        f"{e.msg}, received {current_token_value()} in line {current_token_line()}"
    )
    errors.append(message)
    synchronize()


# Verifica se um token pertence ao TYPE
def check_type():
    value = current_token_value()
    simple_type_pattern = re.compile(r"^(int|string|real|boolean)$")

    # Padrão para tipos de vetor (int[], string[], real[], boolean[])
    vector_type_pattern = re.compile(r"^(int|string|real|boolean)\[\d*\]$")

    return bool(simple_type_pattern.match(value) or vector_type_pattern.match(value))


# Verifica se um token é do tipo IDE
def check_identifier():
    return current_token_type() == "IDE"


# ------------------------------------------------------------------
# Função para análise sintática da regra <Value>
def value():
    return current_token_type() in ["NUM", "STR"] or current_token_value in ["true", "false"]
        


# Função para análise sintática da regra <Object-Value>
def object_value():
    if current_token_value() == ".":
        next_token()
        ide = current_token()
        next_token()


# Função para análise sintática da regra <Possible-Value>
def possible_value():
    if current_token_value() == "IDE":
        next_token()
        object_value()
    else:
        value()


# Função para análise sintática da regra <Array-Value>
def array_value():
    possible_value()
    array()


# Função para análise sintática da regra <More-Array-Value>
def more_array_value():
    if current_token_value() == ",":
        next_token()
        array_value()
        more_array_value()


# Função para análise sintática da regra <Array>
def array():
    if current_token_value() == "[":
        next_token()
        array_value()
        more_array_value()
        if current_token_value() == "]":
            next_token()


# Função para análise sintática da regra <Assignment-Value>
def assignment_value():
    if check_identifier():
        next_token()
        object_value()
    elif value():
        next_token()
    # elif array():
    #     pass  
    # A função já trata o <Array>


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
            next_token()
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
        save_error(e)


# Função para análise sintática da regra <Variable-Same-Line>
# Da pra usar um loop while
def variable_same_line():
    if current_token_value() == ",":
        next_token()
        if check_identifier():
            next_token()
            optional_value()
            variable_same_line()


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
