from bottle import template, redirect, request
from app.controllers.datarecord import DataRecord



class Application():

    def __init__(self):
        self.pages = {
            'pagina': self.pagina,
            'portal': self.portal,
            'banco': self.banco,
            'locadora': self.locadora,
            'entrar': self.entrar,
            'gestao': self.gestao
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


    def locadora(self):
        # Página pública da locadora: lista vinda do model (FilmeLocadora)
        return template('app/views/html/locadora',
                        filmes=self.models.get_locadora(),
                        usuario=self.usuario_atual())


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
    # Recurso "banco" (filmes): só para usuários autenticados

    def banco(self):
        if not self.is_logged_in():
            return redirect('/portal')
        user = self.models.get_current_user(self.get_session_id())
        return template('app/views/html/banco',
                        filmes=self.models.get_filmes(),
                        username=user.username)


    def create_filme(self, titulo, diretor, ano):
        return self.models.create_filme(titulo, diretor, ano)


    def update_filme(self, filme_id, titulo, diretor, ano):
        return self.models.update_filme(filme_id, titulo, diretor, ano)


    def delete_filme(self, filme_id):
        return self.models.delete_filme(filme_id)



    # ------------------------------------------------------------------
    # Recurso "locadora" (CRUD completo no navegador)

    def create_filme_locadora(self, titulo, diretor, ano, genero, sinopse):
        return self.models.create_filme_locadora(titulo, diretor, ano,
                                                 genero, sinopse)


    def update_filme_locadora(self, filme_id, titulo, diretor, ano, genero,
                              sinopse, alugado=None):
        return self.models.update_filme_locadora(filme_id, titulo, diretor,
                                                 ano, genero, sinopse, alugado)


    def delete_filme_locadora(self, filme_id):
        return self.models.delete_filme_locadora(filme_id)


    # ------------------------------------------------------------------
    # Controle de acesso da locadora (login, sessão e papéis)

    COOKIE_SESSAO = 'locadora_sessao'

    def get_sessao_locadora(self):
        return request.get_cookie(self.COOKIE_SESSAO)


    def usuario_atual(self):
        """Funcionario logado nesta requisição, ou None."""
        return self.models.get_funcionario_by_session(self.get_sessao_locadora())


    def login_funcionario(self, username, senha):
        return self.models.check_funcionario(username, senha)


    def logout_funcionario(self):
        self.models.logout_funcionario(self.get_sessao_locadora())


    def entrar(self):
        if self.usuario_atual():
            return redirect('/gestao')
        return template('app/views/html/entrar',
                        erro=request.query.get('erro'),
                        aviso=request.query.get('aviso'))


    def gestao(self):
        """Página de acesso restrito: exige login."""
        usuario = self.usuario_atual()
        if not usuario:
            return redirect('/entrar?aviso=1')
        return template('app/views/html/gestao',
                        filmes=self.models.get_locadora(),
                        usuario=usuario,
                        pode_gerenciar=(usuario.papel == 'gerente'))


    def alugar_filme_locadora(self, filme_id, alugado):
        return self.models.set_alugado_locadora(filme_id, alugado)
