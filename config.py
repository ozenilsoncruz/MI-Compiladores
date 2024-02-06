import os


palavras_reservadas = {
    "variables",
    "const",
    "class",
    "methods",
    "objects",
    "main",
    "return",
    "if",
    "else",
    "then",
    "for",
    "read",
    "print",
    "void",
    "int",
    "real",
    "boolean",
    "string",
    "true",
    "false",
}

# expressões regulares da estrutura léxica da linguagem.
estrutura_lexica = {
    "identificador": r"^[a-zA-Z][a-zA-Z0-9_]*$",
    "numero": r"^[0-9]+(\.[0-9]+)?$",
    "cadeia_caracteres": r'^"[\x20-\x21\x23-\x7E]*"$',
    "comentario": r"^/\*.*?\*/$",
    "delimitadores": [";", ",", ".", "(", ")", "[", "]", "{", "}", "->"],
    "operadores_relacionais": ["!=", "==", "<", "<=", ">", ">=", "="],
    "operadores_aritmeticos": ["+", "-", "*", "/", "++", "--"],
    "operadores_logicos": ["!", "&&", "||"],
}


#  Códigos dos erros/tokens.
codigos = {
    "num": ("NMF", "NUM"),
    "coment": ("CMF", ""),
    "str": ("SMF", "STR"),
    "ident": ("IMF", "IDE"),
    "delimitadores": ("", "DEL"),
    "operadores_relacionais": ("", "REL"),
    "operadores_aritmeticos": ("", "ART"),
    "operadores_logicos": ("", "LOG"),
}


def ler_arquivo(pasta: str, arquivo: str) -> dict[int, list]:
    """
    Salva as palavras lidas em um dicionário
        returns {número da linha: ['palavras', 'da', 'linha']}
    """
    palavras_entrada = {}
    # Verifique se é realmente um arquivo

    if os.path.isfile(os.path.join(pasta, arquivo)):
        with open(os.path.join(pasta, arquivo), "r") as a:
            # Divida o aquivo em linhas.
            linhas = a.read().replace("\t", "").replace("\r", "").split("\n")

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
        print("Arquivo de saída salvo!")
    except:
        print("Um erro ocorreu ao salvar o arquivo!")


semantic_errors = {"already_declared": ""}
semantic_errors = {"already_declared": ""}
