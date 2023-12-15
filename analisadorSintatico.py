from lexico import lexico
from config import palavras_reservadas, salvar_arquivo
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


# ------------------------------------------------------------------
# Função para análise sintática da regra <Value>
def value():
    return current_token_type() in ["NUM", "STR"] or current_token_value in [
        "true",
        "false",
    ]


# Função para análise sintática da regra <Method-Call>
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


# Função para análise sintática da regra <Object-Value>
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


# Verifica se o que está dento dos colchetes é um valor válido
def array_possible_value():
    if check_identifier():
        next_token()
        object_value()
    elif current_token_type() == "NUM":
        next_token()
    else:
        raise SyntaxError("Expected a valid index for array")


# Verifica se a produção é um tipo array ou um acesso a uma posição de um array/matriz.
def definition_access_array():
    if current_token_value() == "[":
        next_token()
        array_possible_value()
        if current_token_value() == "]":
            next_token()
            definition_access_array()
        else:
            raise SyntaxError("Expected ']'")


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
    if current_token_value() == "[":
        next_token()
        array_value()
        more_array_value()
        if current_token_value() == "]":
            next_token()
        else:
            raise SyntaxError("Expected ']'")


# Função para análise sintática da regra <Assignment-Value>
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


# Função para análise sintática da regra <Args-List>
def args_list():
    if check_identifier() or value() or current_token_value() == "[":
        logical_and_expression()
        assignment_value_list()


# Função para análise sintática da regra <Assignment-Value-List>
def assignment_value_list():
    if current_token_value() == ",":
        next_token()
        if check_identifier() or value() or current_token_value() == "[":
            args_list()
        else:
            raise SyntaxError("Expected a valid value")


# Função para análise sintática da regra <Optional-Value>
def optional_value():
    if current_token_value() == "=":
        next_token()
        logical_and_expression()


# Função para análise sintática da regra <Variable-Block>
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
        save_error(e)
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
        save_error(e)
        # variable_same_line()


# Função para análise sintática da regra <Constant-Block>
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


# Função para análise sintática da regra <Constant>
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


# Função para análise sintática da regra <Constant-Same-Line>
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
        # constant_same_line()


# Função para análise sintática da regra <Class-Block>
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
        sinc = ["objects", "class"] if "extends" in str(e) else delimiters_with_keywords
        save_error(e, sinc)
        class_block()


# Função para análise sintática da regra <Class-Extends>
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


# Função para análise sintática da regra <Class-Content>
def class_content():
    variable_block()
    constructor()
    methods()


# Função para análise sintática da regra <Methods>
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


# Função para análise sintática da regra <Method>
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
                                    # if value() or check_identifier():
                                    #     next_token()
                                    if current_token_value() == ";":
                                        next_token()
                                        if current_token_value() == "}":
                                            next_token()
                                            method()
                                        else:
                                            raise SyntaxError("Expected '}'")
                                    else:
                                        raise SyntaxError("Expected ';'")
                                # else:
                                #     raise SyntaxError("Expected a valid value")
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


# Função para análise sintática da regra <Constructor>
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


# Função para análise sintática da regra <Main-Class>
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


# Função para análise sintática da regra <Main-Class-Content>
def main_class_content():
    variable_block()
    object_block()
    statement_sequence()


# Função para análise sintática da regra <Main-Class-Content>
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


# Função para análise sintática da regra <Object-Declaration>
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


# Função para análise sintática da regra <Object-same-line>
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


# Função para análise sintática da regra <Assignment-Method>
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


# Função para análise sintática da regra <Parameter>
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


# Função para análise sintática da regra <Parameter-Value-List>
def parameter_value_list():
    if current_token_value() == ",":
        next_token()
        parameter()


# Função para análise sintática da regra <Unary-Expression>
def unary_expression():
    assignment_value()
    unary_expression_list()


# Função para análise sintática da regra <Unary-Expression-List>
def unary_expression_list():
    if current_token_value() in ["++", "--"]:
        next_token()


# Função para análise sintática da regra <Multiplicative-Expression>
def multiplicative_expression():
    unary_expression()
    multiplicative_expression_list()


# Função para análise sintática da regra <Multiplicative-Expression-List>
def multiplicative_expression_list():
    if current_token_value() in ["*", "/"]:
        next_token()
        multiplicative_expression()


# Função para análise sintática da regra <Additive-Expression>
def additive_expression():
    multiplicative_expression()
    additive_expression_list()


# Função para análise sintática da regra <Additive-Expression-List>
def additive_expression_list():
    if current_token_value() in ["+", "-"]:
        next_token()
        additive_expression()


# Função para análise sintática da regra <Relational-Expression>
def relational_expression():
    additive_expression()
    relational_expression_list()


# Função para análise sintática da regra <Relational-Expression-List>
def relational_expression_list():
    if current_token_value() in ["<", ">", "<=", ">="]:
        next_token()
        relational_expression()


# Função para análise sintática da regra <Equality-Expression>
def equality_expression():
    relational_expression()
    equality_expression_list()


# Função para análise sintática da regra <Equality-Expression-List>
def equality_expression_list():
    if current_token_value() in ["!=", "=="]:
        next_token()
        equality_expression()


# Função para análise sintática da regra <Logical-Not-Expression>
def logical_not_expression():
    if current_token_value() == "!":
        next_token()
        logical_not_expression()
    else:
        equality_expression()


# Função para análise sintática da regra <Logical-Or-Expression-Tail>
def logical_or_expression_tail():
    if current_token_value() == "||":
        next_token()
        logical_and_expression()


# Função para análise sintática da regra <Logical-Or-Expression>
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


# Função para análise sintática da regra <Logical-And-Expression-Tail>
def logical_and_expression_tail():
    if current_token_value() == "&&":
        next_token()
        logical_and_expression()


# Função para análise sintática da regra <Logical-And-Expression>
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


# Função para análise sintática da regra <If-Statement>
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


# Função para análise sintática da regra <Else-Statement>
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
    # else: No else part, so do nothing


# Função para análise sintática da regra <For-Variable-Initialization>
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


# Função para análise sintática da regra <For-Statement>
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


# Função para análise sintática da regra <Print-Command>
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


# Função para análise sintática da regra <Read-Command>
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


# Função para análise sintática da regra <Program>
def program():
    constant_block()
    variable_block()
    class_block()
    object_block()
    main_class()


def main():
    global tokens, index
    pasta = "./files"
    arquivos = os.listdir(pasta)

    for arquivo in arquivos:
        if "saida" not in arquivo:
            tokens = lexico(pasta=pasta, arquivo=arquivo)
            index = 0
            try:
                program()
            except SyntaxError as e:
                save_error(e)

            # print(*errors, sep="\n")

            erros = ""
            for e in errors:
                erros += e + "\n"

            if erros.strip() == "":
                erros = "Sucesso!"

            print(pasta, arquivo.split(".")[0] + "-saida.txt")

            salvar_arquivo(pasta, arquivo.split(".")[0] + "-saida.txt", erros)


if __name__ == "__main__":
    main()
