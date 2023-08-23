import re, os


def analisa_lexema(texto: list, dict_lexema: dict):
    for n_linha, linha in enumerate(texto):
        for palavra in linha.split():
            caractere = 0
            # verifica se começa com " para se encaixar em cadeia de caracteres
            if re.match(r'^"', palavra) is not None:
                if re.match(dict_lexema.get('cadeia_caracteres'), palavra) is not None:
                    print('Cadeia de caracteres')
                else:
                    print('Erro na cadeia de caracteres')
            elif re.match(r'^[0-9]', palavra) is not None:
                if re.match(dict_lexema.get('numero'), palavra) is not None:
                    print('Numero')
                else:
                    print('Erro no numero')
            elif re.match(r'^[a-zA-Z]', palavra) is not None:
                if re.match(dict_lexema.get('identificador'), palavra) is not None:
                    print('Identificador')
                else:
                    print('Erro no identificador')


reservadas = {
'variables', 'const', 'class', 'methods',
'objects', 'main', 'return', 'if', 'else',
'then', 'for', 'read', 'print', 'void', 'int',
'real', 'boolean', 'string', 'true', 'false'
}
delimitadores = [';', ',', '.', '(', ')', '[', ']', '{', '}', '->']
operadores_relacionados = ['!=', '==', '<', '<=', '>', '>=', '=']
operadores_aritmeticos = ['+', '-', '*', '/', '++', '--']
operadores_logicos = ['!', '&&', '||']

# seu tipo de dado e a expressoes regular equivaalente
tipo_dado = {
    'identificador': r'^[a-zA-Z][a-zA-Z0-9_]*$',
    'numero': r'^[0-9]+(\.[0-9]+)?$',
    'cadeia_caracteres': r'^".*"?$'
}


pasta = '/content/files'
arquivos = os.listdir(pasta)

for arquivo in arquivos:
    # Verifique se é realmente um arquivo
    if os.path.isfile(os.path.join(pasta, arquivo)):
        with open(os.path.join(pasta, arquivo), 'r') as a:
            analisa_lexema(a.readlines(), tipo_dado)



