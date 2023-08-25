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
    "cadeia_caracteres": r'^".*"?$',
    "delimitadores": [";", ",", ".", "(", ")", "[", "]", "{", "}", "->"],
    "operadores_relacionais": ["!=", "==", "<", "<=", ">", ">=", "="],
    "operadores_aritmeticos": ["+", "-", "*", "/", "++", "--"],
    "operadores_logicos": ["!", "&&", "||"],
}


#  Código identificadores dos tokens e dos erros.
""" 
PRE palavra reservada
IDE identificador
CAC cadeia de caracteres
NRO numero
DEL delimitador 
REL operador relacional
LOG operador logico
ART operador aritmético
CMF cadeia mal formada
CoMF comentário mal formado
NMF numero mal formado
IMF identificador mal formado
TMF	token mal formado
"""
codigos = {
    "PRE",
    "IDE",
    "CAC",
    "NRO",
    "DEL",
    "REL",
    "LOG",
    "ART",
    "CMF",
    "COMF",
    "NMF",
    "IMF",
    "TMF",
}
