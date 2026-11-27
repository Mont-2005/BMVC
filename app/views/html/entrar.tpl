<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Entrar | Cine Nacional</title>
    <link rel="stylesheet" type="text/css" href="/static/css/locadora.css">
    <script src="/static/js/entrar.js" defer></script>
</head>
<body data-modo="login">

    <header class="topo">
        <div>
            <h1>Locadora Cine Nacional</h1>
            <p class="subtitulo">Acesso restrito para funcionários</p>
        </div>
        <div class="topo-acoes">
            <a class="btn-link" href="/locadora">Ver catálogo</a>
            <button id="btn-tema" type="button" aria-label="Alternar tema claro/escuro">Modo claro</button>
        </div>
    </header>

    <main>
        <section class="login-card bmvc">
            <h2>Entrar</h2>
            % if aviso:
                <p class="msg aviso">Faça login para acessar a gestão do acervo.</p>
            % end
            % if erro:
                <p class="msg erro" role="alert">Usuário ou senha incorretos.</p>
            % end
            <form action="/entrar" method="post" class="form-login">
                <label>Usuário
                    <input id="username" name="username" type="text" autocomplete="username" required autofocus>
                </label>
                <label>Senha
                    <input id="password" name="password" type="password" autocomplete="current-password" required>
                </label>
                <label class="mostrar-senha">
                    <input id="mostrar" type="checkbox"> Mostrar senha
                </label>
                <button type="submit" class="btn-alugar">Entrar</button>
            </form>
        </section>
    </main>

    <footer class="rodape">
        <p>Projeto BMVC &ndash; Nível IV</p>
    </footer>

</body>
</html>
