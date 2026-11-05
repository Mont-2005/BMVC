from app.models.user_account import UserAccount
from app.models.livro import Livro
import json
import uuid


class DataRecord():
    """Banco de dados JSON para os recursos Usuários e Livros"""

    USERS_FILE = "app/controllers/db/user_accounts.json"
    LIVROS_FILE = "app/controllers/db/livros.json"


    def __init__(self):
        self.user_accounts= [] # banco (json)
        self.livros = []       # banco (json)
        self.__authenticated_users = {}
        self.read()
        self.read_livros()


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
    # Livros (recurso "banco")

    def read_livros(self):
        try:
            with open(self.LIVROS_FILE, "r") as arquivo_json:
                dados = json.load(arquivo_json)
                self.livros = [Livro(**d) for d in dados]
        except FileNotFoundError:
            self.livros = []


    def __save_livros(self):
        with open(self.LIVROS_FILE, "w") as arquivo_json:
            json.dump([vars(l) for l in self.livros], arquivo_json,
                      ensure_ascii=False, indent=2)


    def __next_id(self):
        return max([l.id for l in self.livros], default=0) + 1


    @staticmethod
    def __validar(titulo, autor, ano):
        """Retorna (titulo, autor, ano) limpos ou levanta ValueError."""
        titulo = (titulo or "").strip()
        autor = (autor or "").strip()
        if not titulo or not autor:
            raise ValueError("Os campos 'titulo' e 'autor' são obrigatórios.")
        try:
            ano = int(ano)
        except (TypeError, ValueError):
            raise ValueError("O campo 'ano' deve ser um número inteiro.")
        return titulo, autor, ano


    def get_livros(self):
        return self.livros


    def get_livro(self, livro_id):
        for livro in self.livros:
            if livro.id == livro_id:
                return livro
        return None


    def create_livro(self, titulo, autor, ano):
        titulo, autor, ano = self.__validar(titulo, autor, ano)
        livro = Livro(self.__next_id(), titulo, autor, ano)
        self.livros.append(livro)
        self.__save_livros()
        return livro


    def update_livro(self, livro_id, titulo, autor, ano):
        livro = self.get_livro(livro_id)
        if livro is None:
            return None
        livro.titulo, livro.autor, livro.ano = self.__validar(titulo, autor, ano)
        self.__save_livros()
        return livro


    def delete_livro(self, livro_id):
        livro = self.get_livro(livro_id)
        if livro is None:
            return False
        self.livros.remove(livro)
        self.__save_livros()
        return True
