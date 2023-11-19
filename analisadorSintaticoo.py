from analisadorLexico import lexico, salvar_arquivo
import os

tokens = []
index = 0

def next_token():
    global index
    index += 1 # prox token 

def current_token():
    return tokens[index] if index < len(tokens) else None # token atual



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

if __name__ == "__main__":
    main()
    