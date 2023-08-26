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


def analisa_lexema(lexema, num_linha):
    token = {}

    token["num_linha"] = num_linha
    token["valor"] = lexema

    if re.match(r"^/\*", lexema) is not None:
        token["tipo"] = codigos.get("coment")[
            re.match(estrutura_lexica.get("comentario"), lexema) is not None
        ]
    elif lexema in palavras_reservadas:
        token["tipo"] = "KEY"
    elif re.match(r"^[0-9]", lexema) is not None:
        token["tipo"] = codigos.get("num")[
            re.match(estrutura_lexica.get("numero"), lexema) is not None
        ]
    elif re.match(r"^[a-zA-Z]", lexema) is not None:
        token["tipo"] = codigos.get("ident")[
            re.match(estrutura_lexica.get("identificador"), lexema) is not None
        ]
    elif re.match(r'^"', lexema) is not None:
        token["tipo"] = codigos.get("str")[
            re.match(estrutura_lexica.get("cadeia_caracteres"), lexema) is not None
        ]
    elif delimitadorOuOperador(lexema):
        for key in [
            "delimitadores",
            "operadores_relacionais",
            "operadores_aritmeticos",
            "operadores_logicos",
        ]:
            if lexema in estrutura_lexica.get(key):
                token["tipo"] = codigos.get(key)[1]
                break
    else:
        token["tipo"] = "TMF"

    return token


def analisa_comentario_bloco(linhas: list[str]) -> list:
    comentario = ""
    bloco_iniciado = False
    tokens = []
    num_linha = len(linhas)
    for linha in linhas:
        if bloco_iniciado:
            if "*/" in linha:
                bloco_iniciado = False
                comentario = ""
            else:
                comentario += linha
        elif "/*" in linha:
            if "\*" not in linha:
                bloco_iniciado = True
                comentario += linha
    if bloco_iniciado:  # Fim do arquivo e comentário iniciado
        tokens.append(analisa_lexema(comentario, num_linha))

    return tokens


# TODO: Ordenar pelo número da linha
# TODO: Ignorar os comentários de bloco dentro do analisador_lexico


# TODO: Adicionar o número da linha nos tokens  OK
# TODO: Ajustar a verificação de palavras reservadas. OK
# TODO: Remover os arrays vazios e nones dos tokens.   OK
# TODO: Adicionar a verificação de número e o delimitador '.'  OK
# TODO: Remover os /t   OK


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
            break
        elif letra == '"' and not cadeia_caracteres:
            cadeia_caracteres = True
            lexema += letra
        elif letra == '"' and cadeia_caracteres:
            if lexema:
                lexema += letra
                tokens.append(analisa_lexema(lexema, num_linha))
            lexema = ""
            cadeia_caracteres = False
        elif letra == " " and not cadeia_caracteres:
            if lexema:
                tokens.append(analisa_lexema(lexema, num_linha))
            lexema = ""
        elif delimitadorOuOperador(letra) and not cadeia_caracteres:
            if delimitadorOuOperador(possivel_combinacao):
                if possivel_combinacao:
                    tokens.append(analisa_lexema(possivel_combinacao, num_linha))
                lexema = ""
                index += 2  # Avança para a próxima da próxima letra
                continue
            else:
                if (
                    re.match(estrutura_lexica.get("numero"), lexema) is not None
                    and letra == "."
                ):  # 3.
                    lexema += letra
                else:
                    if lexema:
                        tokens.append(analisa_lexema(lexema, num_linha))
                    tokens.append(analisa_lexema(letra, num_linha))
                    lexema = ""
        else:
            lexema += letra
        index += 1
    if lexema:
        tokens.append(analisa_lexema(lexema, num_linha))
    return tokens


# Salva as palavras lidas em um dicionário do tipo {número da linha: [palavras, da, linha]}
def ler_arquivo(pasta, arquivo):
    palavras_entrada = {}
    # Verifique se é realmente um arquivo

    if os.path.isfile(os.path.join(pasta, arquivo)):
        with open(os.path.join(pasta, arquivo), "r") as a:
            # Divida o aquivo em linhas.
            linhas = a.read().split('\n')
            #linhas = [linha.strip() for linha in a.readlines()]

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
        tokens_comentario = analisa_comentario_bloco(palavras_entrada.values())
        if tokens_comentario:
            tokens_saida.extend(tokens_comentario)
        for num_linha, palavras in palavras_entrada.items():
            tokens = analisador_lexico(palavras, num_linha)
            if tokens:
                tokens_saida.extend(analisador_lexico(palavras, num_linha))

    for token in tokens_saida:
        print(f"{token['num_linha']:02d} {token['tipo']} {token['valor']}\n")


if __name__ == "__main__":
    main()
