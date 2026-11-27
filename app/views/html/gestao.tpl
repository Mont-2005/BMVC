<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gestão do acervo | Cine Nacional</title>
    <link rel="stylesheet" type="text/css" href="/static/css/locadora.css">
    <script src="/static/js/locadora.js" defer></script>
</head>
<body data-modo="gestao" data-gerente="{{ 'true' if pode_gerenciar else 'false' }}" data-ws-porta="{{ ws_porta }}">

    <header class="topo">
        <div>
            <h1>Gestão do acervo</h1>
            <p class="subtitulo">Área restrita &mdash; {{ 'CRUD completo do acervo' if pode_gerenciar else 'registro de aluguéis e devoluções' }}</p>
        </div>
        <div class="topo-acoes">
            <span class="usuario">{{ usuario.nome }} <small class="selo">{{ usuario.papel }}</small></span>
            <a class="btn-link" href="/locadora">Ver catálogo</a>
            <form action="/sair" method="post" class="form-sair"><button type="submit">Sair</button></form>
            <span id="status-ws" class="status-ws off" title="Conexão em tempo real">&#9679; conectando...</span>
            <span id="presenca" class="presenca"></span>
            <button id="btn-tema" type="button" aria-label="Alternar tema claro/escuro">Modo claro</button>
        </div>
    </header>

    <main>
        % if pode_gerenciar:
        <section class="bmvc" aria-label="Cadastro">
            <h2 id="titulo-form">Cadastrar filme</h2>
            <form id="form-filme" class="form-filme">
                <input type="hidden" id="filme-id">
                <label>Título <input id="f-titulo" type="text" required></label>
                <label>Diretor <input id="f-diretor" type="text" required></label>
                <label>Ano <input id="f-ano" type="number" min="1888" max="2100" required></label>
                <label>Gênero
                    <select id="f-genero" required>
                        <option value="Ação">Ação</option>
                        <option value="Comédia">Comédia</option>
                        <option value="Drama" selected>Drama</option>
                        <option value="Suspense">Suspense</option>
                    </select>
                </label>
                <label class="larga">Sinopse <input id="f-sinopse" type="text" placeholder="Resumo curto (opcional)"></label>
                <div class="acoes">
                    <button type="submit" id="btn-salvar" class="btn-alugar">Adicionar filme</button>
                    <button type="button" id="btn-cancelar" hidden>Cancelar edição</button>
                </div>
            </form>
        </section>
        % else:
        <section class="bmvc aviso-papel">
            <p>Você está como <strong>atendente</strong>: pode registrar aluguéis e devoluções. Cadastrar, editar e excluir filmes é só para o gerente.</p>
        </section>
        % end
        <p id="mensagem" role="status" aria-live="polite"></p>

        <section class="bmvc atividades-box" aria-label="Atividade em tempo real">
            <h2>Atividade em tempo real</h2>
            <ul id="atividades" class="atividades"></ul>
            <p id="sem-atividade" class="vazio-feed">Nenhuma ação registrada ainda. Quando alguém alugar, cadastrar ou excluir um filme, aparece aqui na hora.</p>
        </section>

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
                <div class="botoes">
                    <button class="btn-alugar" type="button">{{ 'Devolver' if f.alugado else 'Alugar' }}</button>
                    % if pode_gerenciar:
                    <button class="btn-editar" type="button">Editar</button>
                    <button class="btn-excluir" type="button">Excluir</button>
                    % end
                </div>
            </article>
            % end
        </section>

        <p id="vazio" class="vazio" hidden>Nenhum filme encontrado com esses filtros.</p>
    </main>

    <div id="toasts" class="toasts" aria-live="polite"></div>

    <footer class="rodape">
        <p>Projeto BMVC &ndash; Nível IV &bull; Área restrita</p>
    </footer>

</body>
</html>
