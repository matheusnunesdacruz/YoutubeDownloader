import json
import os


ARQUIVO_CONFIG = "config.json"


class Config:

    def __init__(self):
        self.dados = {
            "pasta_download": os.path.join(
                os.path.expanduser("~"),
                "Downloads"
            ),
            "tema": "dark"
        }
        self.carregar()

    def carregar(self):
        if os.path.exists(ARQUIVO_CONFIG):
            try:
                with open(
                    ARQUIVO_CONFIG,
                    "r",
                    encoding="utf-8"
                ) as arquivo:
                    dados = json.load(arquivo)

                if isinstance(dados, dict):
                    self.dados.update(dados)
            except (OSError, json.JSONDecodeError):
                self.salvar()
        else:
            self.salvar()

    def salvar(self):

        with open(
            ARQUIVO_CONFIG,
            "w",
            encoding="utf-8"
        ) as arquivo:

            json.dump(
                self.dados,
                arquivo,
                indent=4,
                ensure_ascii=False
            )

    def get_pasta(self):

        return self.dados["pasta_download"]

    def set_pasta(self, pasta):

        self.dados["pasta_download"] = pasta

        self.salvar()