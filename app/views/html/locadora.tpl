<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Catálogo | Cine Nacional</title>
    <link rel="stylesheet" type="text/css" href="/static/css/locadora.css">
    <script src="/static/js/locadora.js" defer></script>
</head>
<body data-modo="catalogo" data-gerente="false" data-ws-porta="{{ ws_porta }}">

    <header class="topo">
        <div>
            <h1>Locadora Cine Nacional</h1>
            <p class="subtitulo">Catálogo do cinema brasileiro &mdash; consulte a disponibilidade dos filmes</p>
        </div>
        <div class="topo-acoes">
            % if usuario:
                <span class="usuario">{{ usuario.nome }} <small class="selo">{{ usuario.papel }}</small></span>
                <a class="btn-link" href="/gestao">Gestão do acervo</a>
                <form action="/sair" method="post" class="form-sair"><button type="submit">Sair</button></form>
            % else:
                <a class="btn-link" href="/entrar">Entrar (funcionários)</a>
            % end
            <span id="status-ws" class="status-ws off" title="Conexão em tempo real">&#9679; conectando...</span>
            <span id="presenca" class="presenca"></span>
            <button id="btn-tema" type="button" aria-label="Alternar tema claro/escuro">Modo claro</button>
        </div>
    </header>

    <main>
        <section class="painel" aria-label="Filtros">
            <input id="busca" type="search" placeholder="Buscar por título ou diretor...">
            <select id="filtro-genero">
                <option value="todos">Todos os gêneros</option>
                <option value="Ação">Ação</option>
                <option value="Comédia">Comédia</option>
                <option value="Drama">Drama</option>
                <option value="Suspense">Suspense</option>
            </select>
            <select id="filtro-seculo">
                <option value="todos">Todos os séculos</option>
                <option value="XX">Século XX</option>
                <option value="XXI">Século XXI</option>
            </select>
            <select id="ordem">
                <option value="titulo">Ordenar por título</option>
                <option value="ano">Ordenar por ano</option>
            </select>
            <label class="so-alugados">
                <input id="so-alugados" type="checkbox"> Só alugados
            </label>
        </section>

        <p id="contador" class="contador" aria-live="polite"></p>

        <section id="lista" class="grade">
            % for f in filmes:
            <article class="filme {{ 'alugado' if f.alugado else '' }}" data-id="{{ f.id }}" data-titulo="{{ f.titulo }}" data-diretor="{{ f.diretor }}" data-ano="{{ f.ano }}" data-genero="{{ f.genero }}" data-sinopse="{{ f.sinopse }}" data-alugado="{{ 'true' if f.alugado else 'false' }}">
                <span class="etiqueta">{{ f.genero }}</span>
                <h2>{{ f.titulo }}</h2>
                <p class="diretor">Direção: {{ f.diretor }} &bull; {{ f.ano }}</p>
                <p class="sinopse">{{ f.sinopse }}</p>
                <p class="status">{{ 'Alugado' if f.alugado else 'Disponível' }}</p>
            </article>
            % end
        </section>

        <p id="vazio" class="vazio" hidden>Nenhum filme encontrado com esses filtros.</p>
    </main>

    <div id="toasts" class="toasts" aria-live="polite"></div>

    <footer class="rodape">
        <p>Projeto BMVC &ndash; Nível IV &bull; Catálogo público, atualizado em tempo real</p>
    </footer>

</body>
</html>
