from app.models.user_account import UserAccount
from app.models.filme import Filme
from app.models.filme_locadora import FilmeLocadora
from app.models.funcionario import Funcionario
import hashlib
import hmac
import json
import uuid


class DataRecord():
    """Banco de dados JSON para os recursos Usuários e Filmes"""

    USERS_FILE = "app/controllers/db/user_accounts.json"
    FILMES_FILE = "app/controllers/db/filmes.json"
    LOCADORA_FILE = "app/controllers/db/locadora.json"
    FUNCIONARIOS_FILE = "app/controllers/db/funcionarios.json"


    def __init__(self):
        self.user_accounts= [] # banco (json)
        self.filmes = []       # banco (json)
        self.__authenticated_users = {}
        self.read()
        self.read_filmes()
        self.locadora = []     # banco (json)
        self.read_locadora()
        self.funcionarios = [] # banco (json)
        self.__sessoes = {}    # session_id -> Funcionario (memória)
        self.read_funcionarios()


    # ------------------------------------------------------------------
    # Usuários

    def read(self):
        try:
            with open(self.USERS_FILE, "r") as arquivo_json:
                user_data = json.load(arquivo_json)
                self.user_accounts = [UserAccount(**data) for data in user_data]
        except FileNotFoundError:
            self.user_accounts.append(UserAccount('Guest', '000000'))


    def book(self,username,password):
        new_user= UserAccount(username,password)
        self.user_accounts.append(new_user)
        with open(self.USERS_FILE, "w") as arquivo_json:
            user_data = [vars(user_account) for user_account in \
            self.user_accounts]
            json.dump(user_data, arquivo_json)


    def get_current_user(self, session_id):
        if session_id in self.__authenticated_users:
            return self.__authenticated_users[session_id]
        else:
            return None


    def get_username_by_session_id(self, session_id):
        if session_id in self.__authenticated_users:
            return self.__authenticated_users[session_id].username
        else:
            return None


    def get_user_session_id(self, username):
        for session_id in self.__authenticated_users:
            if username == self.__authenticated_users[session_id].username:
                return session_id
        return None  # Retorna None se o usuário não for encontrado


    def check_user(self, username, password):
        for user in self.user_accounts:
            if user.username == username and user.password == password:
                session_id = str(uuid.uuid4())  # Gera um ID de sessão único
                self.__authenticated_users[session_id] = user
                return session_id  # Retorna o ID de sessão para o usuário
        return None


    def logout(self, session_id):
        if session_id in self.__authenticated_users:
            del self.__authenticated_users[session_id] # Remove o usuário logado


    # ------------------------------------------------------------------
    # Filmes (recurso "banco")

    def read_filmes(self):
        try:
            with open(self.FILMES_FILE, "r") as arquivo_json:
                dados = json.load(arquivo_json)
                self.filmes = [Filme(**d) for d in dados]
        except FileNotFoundError:
            self.filmes = []


    def __save_filmes(self):
        with open(self.FILMES_FILE, "w") as arquivo_json:
            json.dump([vars(l) for l in self.filmes], arquivo_json,
                      ensure_ascii=False, indent=2)


    def __next_id(self):
        return max([l.id for l in self.filmes], default=0) + 1


    @staticmethod
    def __validar(titulo, diretor, ano):
        """Retorna (titulo, diretor, ano) limpos ou levanta ValueError."""
        titulo = (titulo or "").strip()
        diretor = (diretor or "").strip()
        if not titulo or not diretor:
            raise ValueError("Os campos 'titulo' e 'diretor' são obrigatórios.")
        try:
            ano = int(ano)
        except (TypeError, ValueError):
            raise ValueError("O campo 'ano' deve ser um número inteiro.")
        return titulo, diretor, ano


    def get_filmes(self):
        return self.filmes


    def get_filme(self, filme_id):
        for filme in self.filmes:
            if filme.id == filme_id:
                return filme
        return None


    def create_filme(self, titulo, diretor, ano):
        titulo, diretor, ano = self.__validar(titulo, diretor, ano)
        filme = Filme(self.__next_id(), titulo, diretor, ano)
        self.filmes.append(filme)
        self.__save_filmes()
        return filme


    def update_filme(self, filme_id, titulo, diretor, ano):
        filme = self.get_filme(filme_id)
        if filme is None:
            return None
        filme.titulo, filme.diretor, filme.ano = self.__validar(titulo, diretor, ano)
        self.__save_filmes()
        return filme


    def delete_filme(self, filme_id):
        filme = self.get_filme(filme_id)
        if filme is None:
            return False
        self.filmes.remove(filme)
        self.__save_filmes()
        return True



    # ------------------------------------------------------------------
    # Locadora (CRUD completo pelo navegador)

    def read_locadora(self):
        try:
            with open(self.LOCADORA_FILE, "r") as arquivo_json:
                self.locadora = [FilmeLocadora(**d) for d in json.load(arquivo_json)]
        except FileNotFoundError:
            self.locadora = []


    def __save_locadora(self):
        with open(self.LOCADORA_FILE, "w") as arquivo_json:
            json.dump([vars(f) for f in self.locadora], arquivo_json,
                      ensure_ascii=False, indent=2)


    @staticmethod
    def __validar_locadora(titulo, diretor, ano, genero, sinopse):
        titulo = (titulo or "").strip()
        diretor = (diretor or "").strip()
        genero = (genero or "").strip()
        sinopse = (sinopse or "").strip()
        if not titulo or not diretor or not genero:
            raise ValueError("Preencha título, diretor e gênero.")
        try:
            ano = int(ano)
        except (TypeError, ValueError):
            raise ValueError("O ano deve ser um número inteiro.")
        if ano < 1888 or ano > 2100:
            raise ValueError("Informe um ano entre 1888 e 2100.")
        return titulo, diretor, ano, genero, sinopse


    def get_locadora(self):
        return self.locadora


    def get_filme_locadora(self, filme_id):
        for f in self.locadora:
            if f.id == filme_id:
                return f
        return None


    def create_filme_locadora(self, titulo, diretor, ano, genero, sinopse):
        titulo, diretor, ano, genero, sinopse = self.__validar_locadora(
            titulo, diretor, ano, genero, sinopse)
        novo_id = max([f.id for f in self.locadora], default=0) + 1
        filme = FilmeLocadora(novo_id, titulo, diretor, ano, genero, sinopse)
        self.locadora.append(filme)
        self.__save_locadora()
        return filme


    def update_filme_locadora(self, filme_id, titulo, diretor, ano, genero,
                              sinopse, alugado=None):
        filme = self.get_filme_locadora(filme_id)
        if filme is None:
            return None
        (filme.titulo, filme.diretor, filme.ano, filme.genero,
         filme.sinopse) = self.__validar_locadora(titulo, diretor, ano,
                                                  genero, sinopse)
        if alugado is not None:
            filme.alugado = bool(alugado)
        self.__save_locadora()
        return filme


    def delete_filme_locadora(self, filme_id):
        filme = self.get_filme_locadora(filme_id)
        if filme is None:
            return False
        self.locadora.remove(filme)
        self.__save_locadora()
        return True


    def set_alugado_locadora(self, filme_id, alugado):
        """Só muda o status de aluguel (usado pelo atendente)."""
        filme = self.get_filme_locadora(filme_id)
        if filme is None:
            return None
        filme.alugado = bool(alugado)
        self.__save_locadora()
        return filme


    # ------------------------------------------------------------------
    # Funcionários: login, sessão e papéis (controle de acesso)

    def read_funcionarios(self):
        try:
            with open(self.FUNCIONARIOS_FILE, "r") as arquivo_json:
                self.funcionarios = [Funcionario(**d) for d in json.load(arquivo_json)]
        except FileNotFoundError:
            self.funcionarios = []


    @staticmethod
    def hash_senha(senha, salt_hex):
        return hashlib.pbkdf2_hmac('sha256', senha.encode(),
                                   bytes.fromhex(salt_hex), 120000).hex()


    def check_funcionario(self, username, senha):
        """Retorna um session_id novo se usuário e senha conferem."""
        username = (username or "").strip()
        senha = senha or ""
        func = next((f for f in self.funcionarios if f.username == username), None)
        # Mesmo sem o usuário, calcula um hash (tempo parecido nos dois casos)
        salt = func.salt if func else "00" * 16
        calculado = self.hash_senha(senha, salt)
        if func and hmac.compare_digest(calculado, func.senha_hash):
            session_id = str(uuid.uuid4())
            self.__sessoes[session_id] = func
            return session_id
        return None


    def get_funcionario_by_session(self, session_id):
        return self.__sessoes.get(session_id)


    def logout_funcionario(self, session_id):
        self.__sessoes.pop(session_id, None)
