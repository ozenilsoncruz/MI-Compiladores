from analisadorLexico import lexico, salvar_arquivo
import os

# Variáveis globais
tokens = []
index = 0

# Função auxiliar para avançar para o próximo token
def next_token():
    global index
    index += 1

# Função auxiliar para obter o token atual
def current_token():
    return tokens[index] if index < len(tokens) else None

# ------------------------------------------------------------------
# Função para análise sintática da regra <Value>
def value():
    if current_token() in ['NUM', 'STR', 'BOOL']:
        next_token()

# Função para análise sintática da regra <Object-Value>
def object_value():
    if current_token() == '.':
        next_token()
        ide = current_token()
        next_token()

# Função para análise sintática da regra <Possible-Value>
def possible_value():
    if current_token() == 'IDE':
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
    if current_token() == ',':
        next_token()
        array_value()
        more_array_value()

# Função para análise sintática da regra <Array>
def array():
    if current_token() == '[':
        next_token()
        array_value()
        more_array_value()
        if current_token() == ']':
            next_token()

# Função para análise sintática da regra <Assignment-Value>
def assignment_value():
    if current_token() == 'IDE':
        next_token()
        object_value()
    else:
        value()
    # A função já trata o <Array>

# Função para análise sintática da regra <Args-List>
def args_list():
    assignment_value()
    assignment_value_list()

# Função para análise sintática da regra <Assignment-Value-List>
def assignment_value_list():
    if current_token() == ',':
        next_token()
        args_list()
# ------------------------------------------------------------------

# Função para análise sintática da regra <Optional-Value>
def optional_value():
    if current_token() == '=':
        next_token()
        assignment_value()

# Função para análise sintática da regra <Variable-Block>
def variable_block():
    if current_token() == 'variables':
        next_token()
        if current_token() == '{':
            next_token()
            variable()
            if current_token() == '}':
                next_token()

# Função para análise sintática da regra <Variable>
def variable():
    type_ = current_token()
    next_token()

    ide = current_token()
    next_token()

    optional_value()

    variable_same_line()

    if current_token() == ';':
        next_token()
        variable()

# Função para análise sintática da regra <Variable-Same-Line>
def variable_same_line():
    if current_token() == ',':
        next_token()
        ide = current_token()
        next_token()
        optional_value()
        variable_same_line()

# Função para análise sintática da regra <Constant-Block>
def constant_block():
    if current_token() == 'const':
        next_token()
        if current_token() == '{':
            next_token()
            constant()
            if current_token() == '}':
                next_token()

# Função para análise sintática da regra <Constant>
def constant():
    type_ = current_token()
    next_token()

    ide = current_token()
    next_token()

    if current_token() == '=':
        next_token()
        assignment_value()

    constant_same_line()

    if current_token() == ';':
        next_token()
        constant()

# Função para análise sintática da regra <Constant-Same-Line>
def constant_same_line():
    if current_token() == ',':
        next_token()
        ide = current_token()
        next_token()
        if current_token() == '=':
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
        #variable_block()
        print(current_token())
        next_token()
        print(current_token())