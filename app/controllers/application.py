from bottle import template, redirect, request
from app.controllers.datarecord import DataRecord



class Application():

    def __init__(self):
        self.pages = {
            'pagina': self.pagina,
            'portal': self.portal,
            'banco': self.banco
        }

        self.models= DataRecord()


    def render(self, page, parameter=None):
        content = self.pages.get(page, self.helper)
        if not parameter:
            return content()
        else:
            return content(parameter)


    def get_session_id(self):
        return request.get_cookie('session_id')


    def portal(self):
        return template('app/views/html/portal')


    def helper(self):
        return template('app/views/html/helper')


    def is_authenticated(self, username):
        session_id = self.get_session_id()
        current_username = self.models.get_username_by_session_id(session_id)
        return username == current_username


    def is_logged_in(self):
        """True se o cookie de sessão da requisição pertence a um usuário logado."""
        session_id = self.get_session_id()
        return self.models.get_username_by_session_id(session_id) is not None


    def pagina(self,username=None):
        if self.is_authenticated(username):
            session_id = self.get_session_id()
            user = self.models.get_current_user(session_id)
            return template('app/views/html/pagina', data=user)
        else:
            return template('app/views/html/pagina', data=None)


    def authenticate_user(self, username, password):
        session_id = self.models.check_user(username, password)
        if session_id:
            return session_id, username
        return None, None


    def logout_user(self):
        session_id = self.get_session_id()
        if session_id:
            self.models.logout(session_id)


    # ------------------------------------------------------------------
    # Recurso "banco" (livros): só para usuários autenticados

    def banco(self):
        if not self.is_logged_in():
            return redirect('/portal')
        user = self.models.get_current_user(self.get_session_id())
        return template('app/views/html/banco',
                        livros=self.models.get_livros(),
                        username=user.username)


    def create_livro(self, titulo, autor, ano):
        return self.models.create_livro(titulo, autor, ano)


    def update_livro(self, livro_id, titulo, autor, ano):
        return self.models.update_livro(livro_id, titulo, autor, ano)


    def delete_livro(self, livro_id):
        return self.models.delete_livro(livro_id)
