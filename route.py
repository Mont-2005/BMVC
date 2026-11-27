from app.controllers.application import Application
from bottle import Bottle, route, run, request, static_file
from bottle import redirect, template, response


app = Bottle()
ctl = Application()


#-----------------------------------------------------------------------------
# Rotas:

@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root='./app/static')

@app.route('/')
@app.route('/helper')
def helper(info= None):
    return ctl.render('helper')


#-----------------------------------------------------------------------------
# Suas rotas aqui:

@app.route('/pagina', methods=['GET'])
@app.route('/pagina/<username>', methods=['GET'])
def action_pagina(username=None):
    if not username:
        return ctl.render('pagina')
    else:
        return ctl.render('pagina',username)


@app.route('/locadora', method='GET')
def action_locadora():
    return ctl.render('locadora')


@app.route('/portal', method='GET')
def login():
    return ctl.render('portal')


@app.route('/portal', method='POST')
def action_portal():
    username = request.forms.get('username')
    password = request.forms.get('password')
    session_id, username= ctl.authenticate_user(username, password)
    if session_id:
        # Sem 'secure=True': o servidor roda em HTTP puro (localhost), e um
        # cookie 'secure' não seria devolvido pelo curl/navegador nesse caso.
        response.set_cookie('session_id', session_id, httponly=True, \
        max_age=3600)
        redirect('/banco')
    else:
        return redirect('/portal')


@app.route('/logout', method='POST')
def logout():
  ctl.logout_user()
  response.delete_cookie('session_id')
  redirect('/')


#-----------------------------------------------------------------------------
# Recurso "banco": READ (HTML) e CREATE / UPDATE / DELETE (via cURL).
# Todas exigem login (cookie 'session_id').

def _dados_filme():
    """Aceita JSON (-H 'Content-Type: application/json') ou formulário (-d)."""
    dados = request.json if request.json else request.forms
    return dados.get('titulo'), dados.get('diretor'), dados.get('ano')


def _nao_autenticado():
    response.status = 401
    return {'erro': 'Não autenticado. Faça login em POST /portal.'}


@app.route('/banco', method='GET')
def action_banco():
    return ctl.render('banco')          # READ: lista no próprio sistema


@app.route('/banco', method='POST')
def action_banco_create():              # CREATE
    if not ctl.is_logged_in():
        return _nao_autenticado()
    try:
        filme = ctl.create_filme(*_dados_filme())
    except ValueError as erro:
        response.status = 400
        return {'erro': str(erro)}
    response.status = 201
    return vars(filme)


@app.route('/banco/<filme_id:int>', method='PUT')
def action_banco_update(filme_id):      # UPDATE
    if not ctl.is_logged_in():
        return _nao_autenticado()
    try:
        filme = ctl.update_filme(filme_id, *_dados_filme())
    except ValueError as erro:
        response.status = 400
        return {'erro': str(erro)}
    if filme is None:
        response.status = 404
        return {'erro': f'Filme {filme_id} não encontrado.'}
    return vars(filme)


@app.route('/banco/<filme_id:int>', method='DELETE')
def action_banco_delete(filme_id):      # DELETE
    if not ctl.is_logged_in():
        return _nao_autenticado()
    if not ctl.delete_filme(filme_id):
        response.status = 404
        return {'erro': f'Filme {filme_id} não encontrado.'}
    return {'mensagem': f'Filme {filme_id} removido.'}

#-----------------------------------------------------------------------------
# Locadora (BMVC III): catálogo público + área restrita com login.
#   GET  /locadora   catálogo público (somente leitura)
#   GET  /entrar     página de login        POST /entrar  autentica
#   POST /sair       encerra a sessão
#   GET  /gestao     página RESTRITA (redireciona para /entrar sem login)
#   API (JSON, exige login e respeita o papel do usuário):
#     POST /api/filmes        cria            -> só gerente
#     PUT  /api/filmes/<id>   atualiza        -> gerente (tudo) | atendente (só aluguel)
#     DELETE /api/filmes/<id> exclui          -> só gerente

@app.route('/entrar', method='GET')
def action_entrar_form():
    return ctl.render('entrar')


@app.route('/entrar', method='POST')
def action_entrar():
    session_id = ctl.login_funcionario(request.forms.get('username'),
                                       request.forms.get('password'))
    if not session_id:
        return redirect('/entrar?erro=1')
    response.set_cookie(ctl.COOKIE_SESSAO, session_id, httponly=True,
                        max_age=3600, path='/')
    return redirect('/gestao')


@app.route('/sair', method='POST')
def action_sair():
    ctl.logout_funcionario()
    response.delete_cookie(ctl.COOKIE_SESSAO, path='/')
    return redirect('/locadora')


@app.route('/gestao', method='GET')
def action_gestao():
    return ctl.render('gestao')


def _dados_locadora():
    d = request.json or {}
    return (d.get('titulo'), d.get('diretor'), d.get('ano'),
            d.get('genero'), d.get('sinopse'))


def _checar_acesso(somente_gerente):
    """Retorna (usuario, None) se liberado ou (None, erro) com o status HTTP."""
    usuario = ctl.usuario_atual()
    if not usuario:
        response.status = 401
        return None, {'erro': 'Faça login para continuar.'}
    if somente_gerente and usuario.papel != 'gerente':
        response.status = 403
        return None, {'erro': 'Apenas o gerente pode fazer isso.'}
    return usuario, None


@app.route('/api/filmes', method='POST')
def action_filmes_create():
    usuario, erro = _checar_acesso(somente_gerente=True)
    if erro:
        return erro
    try:
        filme = ctl.create_filme_locadora(*_dados_locadora())
    except ValueError as e:
        response.status = 400
        return {'erro': str(e)}
    response.status = 201
    return vars(filme)


@app.route('/api/filmes/<filme_id:int>', method='PUT')
def action_filmes_update(filme_id):
    usuario, erro = _checar_acesso(somente_gerente=False)
    if erro:
        return erro
    alugado = (request.json or {}).get('alugado')
    try:
        if usuario.papel == 'gerente':
            filme = ctl.update_filme_locadora(filme_id, *_dados_locadora(), alugado)
        elif alugado is None:
            response.status = 400
            return {'erro': "Informe o campo 'alugado'."}
        else:
            filme = ctl.alugar_filme_locadora(filme_id, alugado)
    except ValueError as e:
        response.status = 400
        return {'erro': str(e)}
    if filme is None:
        response.status = 404
        return {'erro': f'Filme {filme_id} não encontrado.'}
    return vars(filme)


@app.route('/api/filmes/<filme_id:int>', method='DELETE')
def action_filmes_delete(filme_id):
    usuario, erro = _checar_acesso(somente_gerente=True)
    if erro:
        return erro
    if not ctl.delete_filme_locadora(filme_id):
        response.status = 404
        return {'erro': f'Filme {filme_id} não encontrado.'}
    return {'mensagem': f'Filme {filme_id} removido.'}

#-----------------------------------------------------------------------------


if __name__ == '__main__':

    ctl.iniciar_tempo_real()      # WebSocket em outra porta (thread própria)
    run(app, host='0.0.0.0', port=8080, debug=True)
