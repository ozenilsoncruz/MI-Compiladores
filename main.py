from lexico import lexico
from config import salvar_arquivo
from sintatico import SyntacticParser
import os


class MainExecutor(SyntacticParser):
    def __init__(self):
        super().__init__()

    def process_files(self, folder_path="./files"):
        files = []
        for filename in os.listdir(folder_path):
            if "saida" not in filename:
                files.append(filename)

        for file in files:
            self.tokens = lexico(pasta=folder_path, arquivo=file)
            self.index = 0
            self.errors = []
            try:
                self.program()
            except SyntaxError as e:
                self.save_error(e)

            error_message = "\n".join(self.errors) if self.errors else "Sucesso!"

            save_path = f"{file.split('.')[0]}-saida.txt"
            salvar_arquivo(folder_path, save_path, error_message)


if __name__ == "__main__":
    main_executor = MainExecutor()
    main_executor.process_files()
