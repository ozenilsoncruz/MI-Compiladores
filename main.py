import os
import importlib
import sintatico 

from lexico import lexico
from config import salvar_arquivo

class MainExecutor:
    def __init__(self, folder):
        self.folder = folder

    def process_file(self, file_name):
        tokens = lexico(pasta=self.folder, arquivo=file_name)
        error_messages = sintatico.SyntacticParse(tokens)
        output_file = file_name.split(".")[0] + "-saida.txt"
        salvar_arquivo(self.folder, output_file, error_messages)
        importlib.reload(sintatico)  # Recarregue o módulo sintatico após o uso

    def run(self):
        files = os.listdir(self.folder)
        for file_name in files:
            if "saida" not in file_name:
                self.process_file(file_name)

if __name__ == "__main__":
    analisador_main = MainExecutor("./files")
    analisador_main.run()