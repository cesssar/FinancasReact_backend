class Excecao(Exception):
    ...

class CadastroExistente(Excecao):
    def __init__(self) -> None:
        self.status_code = 409
        self.detail = "Cadastro já existe"