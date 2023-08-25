import re, os
from config import palavras_reservadas, estrutura_lexica, codigos


def delimitadorOuOperador(lexema):
    return any(
        lexema in estrutura_lexica.get(key)
        for key in [
            "delimitadores",
            "operadores_relacionais",
            "operadores_aritmeticos",
            "operadores_logicos",
        ]
    )


def analisa_lexema(lexema):
    # verifica se começa com " para se encaixar em cadeia de caracteres
    if re.match(r'^"', lexema) is not None:
        if re.match(estrutura_lexica.get("cadeia_caracteres"), lexema) is not None:
            # token = f"{num_linha} {codigos.get('cac')}"
            print("Cadeia de caracteres")
        else:
            print("Erro na cadeia de caracteres")
    elif re.match(r"^[0-9]", lexema) is not None:
        if re.match(estrutura_lexica.get("numero"), lexema) is not None:
            print("Numero")
        else:
            print("Erro no numero")
    elif re.match(r"^[a-zA-Z]", lexema) is not None:
        if re.match(estrutura_lexica.get("identificador"), lexema) is not None:
            print("Identificador")
        else:
            print(f"Erro no identificador ")


def analisador_lexico(linha, num_linha: int, tokens_saida: list):
    index = 0  # Manter o controle da posição atual na linha
    cadeia_caracteres = False  # Indica se esta sendo analisado uma cadeia de caracteres
    comentario_bloco = False
    while index < len(linha):
        letra = linha[index]
        if letra == '"' and not cadeia_caracteres:
            cadeia_caracteres = True
        elif letra == '"' and cadeia_caracteres:
            analisa_lexema(lexema)
            lexema = ""
            cadeia_caracteres = False
        elif letra == " " and not cadeia_caracteres:
            analisa_lexema(lexema)
            lexema = ""
        elif delimitadorOuOperador(letra) and not cadeia_caracteres:
            possivel_combinacao = letra + linha[index + 1]
            if delimitadorOuOperador(possivel_combinacao):
                analisa_lexema(possivel_combinacao)
                index += 2  # Avança para a próxima da próxima letra
            else:
                analisa_lexema(lexema)
                analisa_lexema(letra)
                index += 1
            lexema = ""
        else:
            lexema += letra


# Salva as palavras lidas em um dicionário do tipo {número da linha: [palavras, da, linha]}
def ler_arquivo(pasta, arquivo):
    palavras_entrada = {}
    # Verifique se é realmente um arquivo
    if os.path.isfile(os.path.join(pasta, arquivo)):
        with open(os.path.join(pasta, arquivo), "r") as a:
            # Divida o aquivo em linhas.
            linhas = a.read().split("\n")
            # Divisão do conteúdo em palavras, considerando espaços e tabulações como separadores.
            for num_linha, linha in enumerate(linhas):
                if linha.strip():  # Verifica se a linha não é vazia
                    num_linha += 1
                    palavras_entrada[num_linha] = linha
    return palavras_entrada


def main():
    pasta = "./files"
    arquivos = os.listdir(pasta)
    tokens_saida = []
    for arquivo in arquivos:
        palavras_entrada = ler_arquivo(pasta, arquivo)
        for num_linha, palavras in palavras_entrada.items():
            print(palavras, num_linha)
            # analisador_lexico(palavras, num_linha, tokens_saida)


if __name__ == "__main__":
    main()
