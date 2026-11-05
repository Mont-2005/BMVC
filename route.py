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

def _dados_livro():
    """Aceita JSON (-H 'Content-Type: application/json') ou formulário (-d)."""
    dados = request.json if request.json else request.forms
    return dados.get('titulo'), dados.get('autor'), dados.get('ano')


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
        livro = ctl.create_livro(*_dados_livro())
    except ValueError as erro:
        response.status = 400
        return {'erro': str(erro)}
    response.status = 201
    return vars(livro)


@app.route('/banco/<livro_id:int>', method='PUT')
def action_banco_update(livro_id):      # UPDATE
    if not ctl.is_logged_in():
        return _nao_autenticado()
    try:
        livro = ctl.update_livro(livro_id, *_dados_livro())
    except ValueError as erro:
        response.status = 400
        return {'erro': str(erro)}
    if livro is None:
        response.status = 404
        return {'erro': f'Livro {livro_id} não encontrado.'}
    return vars(livro)


@app.route('/banco/<livro_id:int>', method='DELETE')
def action_banco_delete(livro_id):      # DELETE
    if not ctl.is_logged_in():
        return _nao_autenticado()
    if not ctl.delete_livro(livro_id):
        response.status = 404
        return {'erro': f'Livro {livro_id} não encontrado.'}
    return {'mensagem': f'Livro {livro_id} removido.'}

#-----------------------------------------------------------------------------


if __name__ == '__main__':

    run(app, host='0.0.0.0', port=8080, debug=True)
