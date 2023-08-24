import re, os
from config import palavras_reservadas, estrutura_lexica, codigos


def analisa_lexema(linha: list, num_linha: int, tokens_saida: list):
    texto_saida = ""
    for palavra in linha:
        caractere = 0
        # verifica se começa com " para se encaixar em cadeia de caracteres
        if re.match(r'^"', palavra) is not None:
            if re.match(estrutura_lexica.get("cadeia_caracteres"), palavra) is not None:
                token = f"{num_linha} {codigos.get('cac')}"
                print("Cadeia de caracteres")
            else:
                print("Erro na cadeia de caracteres")
        elif re.match(r"^[0-9]", palavra) is not None:
            if re.match(estrutura_lexica.get("numero"), palavra) is not None:
                print("Numero")
            else:
                print("Erro no numero")
        elif re.match(r"^[a-zA-Z]", palavra) is not None:
            if re.match(estrutura_lexica.get("identificador"), palavra) is not None:
                print("Identificador")
            else:
                print(f"Erro no identificador ")


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
                    palavras = linha.split()
                    if num_linha not in palavras_entrada:
                        palavras_entrada[num_linha] = []
                    palavras_entrada[num_linha].extend(palavras)
    return palavras_entrada


def main():
    pasta = "./files"
    arquivos = os.listdir(pasta)
    tokens_saida = []
    for arquivo in arquivos:
        palavras_entrada = ler_arquivo(pasta, arquivo)
        for num_linha, palavras in palavras_entrada.items():
            print(palavras)
            # analisa_lexema(palavras, num_linha, tokens_saida)


if __name__ == "__main__":
    main()
