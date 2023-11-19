import re, os
from config import palavras_reservadas, estrutura_lexica, codigos


def delimitadorOuOperador(lexema: str) -> bool:
    return any(
        lexema in estrutura_lexica.get(key)
        for key in [
            "delimitadores",
            "operadores_relacionais",
            "operadores_aritmeticos",
            "operadores_logicos",
        ]
    )

def analisa_lexema(lexema: str, num_linha: int) -> dict[str, list]:
    token = {}

    token["num_linha"] = num_linha
    token["valor"] = lexema

    if re.match(r"^/\*", lexema) is not None:
        token["tipo"] = codigos.get("coment")[
            re.match(estrutura_lexica.get("comentario"), lexema, re.DOTALL) is not None
        ]
    elif lexema in palavras_reservadas:
        token["tipo"] = "KEY"
    elif re.match(r"^[0-9]", lexema) is not None:
        token["tipo"] = codigos.get("num")[
            re.match(estrutura_lexica.get("numero"), lexema, re.DOTALL) is not None
        ]
    elif re.match(r"^[a-zA-Z]", lexema) is not None:
        token["tipo"] = codigos.get("ident")[
            re.match(estrutura_lexica.get("identificador"), lexema, re.DOTALL) is not None
        ]
    elif re.match(r'^"', lexema) is not None:
        token["tipo"] = codigos.get("str")[
            re.match(estrutura_lexica.get("cadeia_caracteres"), lexema, re.DOTALL) is not None
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

def mescla_comentario_bloco(palavras_entrada: dict[int, list[str]]) -> dict[int, list]:
    novo_palavras_entrada = {}
    bloco_iniciado = None

    for num_linha, linha in palavras_entrada.items():
        sub_string = "".join(re.findall(r'"([^"]*)"', linha)) # busca e junta todas as strings da linha
        sub_string2 = "".join(re.findall(r'^"([^"]*)', linha))
        
        # se estiver na linha e nao estiver dentro de uma string
        if '/*' in linha and '/*' not in sub_string and '/*' not in sub_string2:
            if "*/" not in linha:
                bloco_iniciado = num_linha
                novo_palavras_entrada[num_linha] = linha
            else:
                novo_palavras_entrada[num_linha] = linha
        elif '*/' in linha and bloco_iniciado is not None:
            index = linha.find('*/')
            novo_palavras_entrada[bloco_iniciado] += '\n' + linha[:index+2]
            novo_palavras_entrada[num_linha] = linha[index+2:]
            bloco_iniciado = None
        elif bloco_iniciado is not None:
            novo_palavras_entrada[bloco_iniciado] += '\n' + linha
        else:
            novo_palavras_entrada[num_linha] = linha

    return novo_palavras_entrada

def analisador_lexico(linha: str, num_linha: int) -> list:
    tokens = []
    index = 0  # Manter o controle da posição atual na linha
    cadeia_caracteres = False  # Indica se esta sendo analisado uma cadeia de caracteres
    comentario_bloco = False # Indica se esta sendo analisado um comentario de bloco
    lexema = ""
    while index < len(linha):
        letra = linha[index]
        possivel_combinacao = letra + linha[index + 1] if index + 1 < len(linha) else letra
                        
        if letra == '"' and not cadeia_caracteres and not comentario_bloco:
            cadeia_caracteres = True
            lexema += letra
        elif letra == '"' and cadeia_caracteres:
            if lexema:
                lexema += letra
                tokens.append(analisa_lexema(lexema, num_linha))
            lexema = ""
            cadeia_caracteres = False
        elif possivel_combinacao == "/*" and not cadeia_caracteres and not comentario_bloco:
            comentario_bloco = True
            lexema += possivel_combinacao
            index += 1
        elif possivel_combinacao == '*/' and comentario_bloco:
            if lexema:
                lexema += possivel_combinacao
                token = analisa_lexema(lexema, num_linha)
                if token.get('tipo'): # se o token for analisado, adiciono token
                    tokens.append(token)
            index += 1
            lexema = ""
            comentario_bloco = False
        elif possivel_combinacao == "//" and not cadeia_caracteres and not comentario_bloco:
            break 
        elif letra == " " and not cadeia_caracteres and not comentario_bloco:
            if lexema:
                tokens.append(analisa_lexema(lexema, num_linha))
            lexema = ""
        elif delimitadorOuOperador(letra) and not cadeia_caracteres and not comentario_bloco:
            if (
                re.match(estrutura_lexica.get("numero"), lexema) is not None
                and letra == "."
            ):  # 3.
                lexema += letra
            else:
                if lexema:
                    tokens.append(analisa_lexema(lexema, num_linha))
                    lexema = ""
                if delimitadorOuOperador(possivel_combinacao):
                    tokens.append(analisa_lexema(possivel_combinacao, num_linha))
                    index += 1  # Avança para a próxima da próxima letra
                else:
                    tokens.append(analisa_lexema(letra, num_linha))
        else:
            lexema += letra
        index += 1
    if lexema:
        tokens.append(analisa_lexema(lexema, num_linha))
    return tokens

def ler_arquivo(pasta: str, arquivo: str) -> dict[int, list]:
    '''
    Salva as palavras lidas em um dicionário 
        returns {número da linha: ['palavras', 'da', 'linha']}
    '''
    palavras_entrada = {}
    # Verifique se é realmente um arquivo

    if os.path.isfile(os.path.join(pasta, arquivo)):
        with open(os.path.join(pasta, arquivo), "r") as a:
            # Divida o aquivo em linhas.
            linhas = a.read().replace('\t', '').replace('\r', '').split('\n')
            
            # Divisão do conteúdo em palavras, considerando espaços e tabulações como separadores.
            for num_linha, linha in enumerate(linhas):
                if linha.strip():  # Verifica se a linha não é vazia
                    num_linha += 1
                    palavras_entrada[num_linha] = linha
    return palavras_entrada

def salvar_arquivo(pasta: str, arquivo: str, conteudo: str) -> bool:
    try:
        with open(os.path.join(pasta, arquivo), "w") as a:
            a.write(conteudo)
        print('Arquivo de saída salvo!')
    except:
        print('Um erro ocorreu ao salvar o arquivo!')

def lexico(pasta: str, arquivo: str) -> list:
    tokens_saida = []
    if 'saida' not in arquivo:
        palavras_entrada = mescla_comentario_bloco(ler_arquivo(pasta, arquivo))
        for num_linha, palavras in palavras_entrada.items():
            tokens = analisador_lexico(palavras, num_linha)
            if tokens:
                tokens_saida.extend(tokens)

    return tokens_saida
