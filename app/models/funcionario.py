class Funcionario():
    """Funcionário da locadora (conta de acesso).

    papel: 'gerente'   -> CRUD completo do acervo
           'atendente' -> só consulta e registra aluguel/devolução
    A senha nunca é guardada em texto: só o hash PBKDF2 e o sal.
    """
    def __init__(self, username, nome, papel, salt, senha_hash):
        self.username = username
        self.nome = nome
        self.papel = papel
        self.salt = salt
        self.senha_hash = senha_hash
