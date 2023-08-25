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
    token = {}

    if lexema == "":
        return
    if re.match(r"^/\*", lexema) is not None:
        token[lexema] = codigos.get("coment")[
            re.match(estrutura_lexica.get("comentario"), lexema) is not None
        ]
    elif re.match(r"^[0-9]", lexema) is not None:
        token[lexema] = codigos.get("num")[
            re.match(estrutura_lexica.get("numero"), lexema) is not None
        ]
    elif re.match(r"^[a-zA-Z]", lexema) is not None:
        token[lexema] = codigos.get("ident")[
            re.match(estrutura_lexica.get("identificador"), lexema) is not None
        ]
    elif re.match(r'^"', lexema) is not None:
        token[lexema] = codigos.get("str")[
            re.match(estrutura_lexica.get("cadeia_caracteres"), lexema) is not None
        ]
    elif lexema == "//":
        token[lexema] = "comentario"
    elif lexema in palavras_reservadas:
        token[lexema] = "palavra reservada"
    elif delimitadorOuOperador(lexema):
        for key in [
            "delimitadores",
            "operadores_relacionais",
            "operadores_aritmeticos",
            "operadores_logicos",
        ]:
            if lexema in estrutura_lexica.get(key):
                token[lexema] = key
                break
    else:
        token[lexema] = "token mal formado"

    return token


def analisa_comentario_bloco(linhas: list[str]) -> list:
    comentario = ""
    bloco_iniciado = False
    tokens = []
    for linha in linhas:
        if bloco_iniciado:
            if "*/" in linha:
                # comentário fechado - ignorar
                # comentario += linha
                # tokens.append(analisa_lexema(comentario))
                bloco_iniciado = False
                comentario = ""
            else:
                comentario += linha
        elif "/*" in linha:
            if "\*" not in linha:
                bloco_iniciado = True
                comentario += linha
    if bloco_iniciado:  # Fim do arquivo e comentário iniciado
        tokens.append(analisa_lexema(comentario))

    return tokens


# TODO: Adicionar a verificação de número e o delimitador '.'
# TODO: Remover os arrays vazios e nones dos tokens.
# TODO: Adicionar o número da linha nos tokens
# TODO: Ordenar pelo número da linha
# TODO: Ignorar os comentários de bloco dentro do analisador_lexico


def analisador_lexico(linha, num_linha: int) -> list:
    tokens = []
    index = 0  # Manter o controle da posição atual na linha
    cadeia_caracteres = False  # Indica se esta sendo analisado uma cadeia de caracteres
    lexema = ""
    while index < len(linha):
        letra = linha[index]
        possivel_combinacao = ""
        if index + 1 < len(linha):
            possivel_combinacao = letra + linha[index + 1]
        else:
            possivel_combinacao = letra
        if possivel_combinacao == "//":
            tokens.append(analisa_lexema(possivel_combinacao))
            break
        elif letra == '"' and not cadeia_caracteres:
            cadeia_caracteres = True
        elif letra == '"' and cadeia_caracteres:
            tokens.append(analisa_lexema(lexema))
            lexema = ""
            cadeia_caracteres = False
        elif letra == " " and not cadeia_caracteres:
            tokens.append(analisa_lexema(lexema))
            lexema = ""
        elif delimitadorOuOperador(letra) and not cadeia_caracteres:
            if delimitadorOuOperador(possivel_combinacao):
                tokens.append(analisa_lexema(possivel_combinacao))
                index += 2  # Avança para a próxima da próxima letra
                continue
            else:
                tokens.append(analisa_lexema(lexema))
                tokens.append(analisa_lexema(letra))
            lexema = ""
        else:
            lexema += letra
        index += 1
    return tokens


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
        tokens_saida.append(analisa_comentario_bloco(palavras_entrada.values()))
        for num_linha, palavras in palavras_entrada.items():
            print(palavras)
            tokens_saida.append(analisador_lexico(palavras, num_linha))
    print(tokens_saida)


if __name__ == "__main__":
    main()
