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
    "comentario": r'^/\*.*?\*/$',
    "delimitadores": [";", ",", ".", "(", ")", "[", "]", "{", "}", "->"],
    "operadores_relacionais": ["!=", "==", "<", "<=", ">", ">=", "="],
    "operadores_aritmeticos": ["+", "-", "*", "/", "++", "--"],
    "operadores_logicos": ["!", "&&", "||"],
}


#  Código identificadores dos tokens e dos erros. 
codigos = {
    'pr': "palavra reservada",
    'tmf': "token mal formado",
    'num': ("numero mal formado", "numero"),
    'coment': ("comentario mal formado", "comentario"),
    'str': ("cadeia mal formada", "cadeia de caracteres"),
    'ident': ("identificador mal formado", "identificador")
}
