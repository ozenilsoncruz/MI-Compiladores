import re



s = '/* olá mundo 12345 \n*/'


print(re.match(r"^/\*.*?\*/$", s) is not None)