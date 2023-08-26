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
    "comentario": r"^/\*.*?\*/$",
    "delimitadores": [";", ",", ".", "(", ")", "[", "]", "{", "}", "->"],
    "operadores_relacionais": ["!=", "==", "<", "<=", ">", ">=", "="],
    "operadores_aritmeticos": ["+", "-", "*", "/", "++", "--"],
    "operadores_logicos": ["!", "&&", "||"],
}


#  Códigos dos erros/tokens.
codigos = {
    "num": ("Número mal formado", "NUM"),
    "coment": ("Comentário mal formado", "COM"),
    "str": ("Cadeia de caracteres mal formada", "STR"),
    "ident": ("Identificador mal formado", "IDE"),
    "delimitadores": ("", "DEL"),
    "operadores_relacionais": ("", "REL"),
    "operadores_aritmeticos": ("", "ART"),
    "operadores_logicos": ("", "LOG"),
}
