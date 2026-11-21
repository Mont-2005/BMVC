<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Locadora Cine Nacional | BMVC</title>
    <link rel="stylesheet" type="text/css" href="/static/css/locadora.css">
    <script src="/static/js/locadora.js" defer></script>
</head>
<body>

    <header class="topo">
        <div>
            <h1>Locadora Cine Nacional</h1>
            <p class="subtitulo">Catálogo de clássicos do cinema brasileiro &mdash; servido pelo BMVC (Bottle + MVC)</p>
        </div>
        <button id="btn-tema" type="button" aria-label="Alternar tema claro/escuro">Modo claro</button>
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
            <article class="filme" data-titulo="Ainda Estou Aqui" data-diretor="Walter Salles" data-ano="2024" data-seculo="XXI">
                <span class="etiqueta">Drama</span>
                <h2>Ainda Estou Aqui</h2>
                <p class="diretor">Direção: Walter Salles &bull; 2024</p>
                <p>Eunice Paiva busca a verdade sobre o desaparecimento do marido na ditadura.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
            <article class="filme" data-titulo="Bacurau" data-diretor="Kleber Mendonça Filho" data-ano="2019" data-seculo="XXI">
                <span class="etiqueta">Suspense</span>
                <h2>Bacurau</h2>
                <p class="diretor">Direção: Kleber Mendonça Filho &bull; 2019</p>
                <p>Uma pequena cidade do sertão enfrenta uma ameaça misteriosa.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
            <article class="filme" data-titulo="Central do Brasil" data-diretor="Walter Salles" data-ano="1998" data-seculo="XX">
                <span class="etiqueta">Drama</span>
                <h2>Central do Brasil</h2>
                <p class="diretor">Direção: Walter Salles &bull; 1998</p>
                <p>Uma ex-professora e um menino atravessam o país em busca do pai dele.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
            <article class="filme" data-titulo="Cidade de Deus" data-diretor="Fernando Meirelles" data-ano="2002" data-seculo="XXI">
                <span class="etiqueta">Drama</span>
                <h2>Cidade de Deus</h2>
                <p class="diretor">Direção: Fernando Meirelles &bull; 2002</p>
                <p>A formação do crime organizado numa favela do Rio, vista por Buscapé.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
            <article class="filme" data-titulo="Dona Flor e Seus Dois Maridos" data-diretor="Bruno Barreto" data-ano="1976" data-seculo="XX">
                <span class="etiqueta">Comédia</span>
                <h2>Dona Flor e Seus Dois Maridos</h2>
                <p class="diretor">Direção: Bruno Barreto &bull; 1976</p>
                <p>Dona Flor é assombrada pelo fantasma do primeiro marido.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
            <article class="filme" data-titulo="O Auto da Compadecida" data-diretor="Guel Arraes" data-ano="2000" data-seculo="XX">
                <span class="etiqueta">Comédia</span>
                <h2>O Auto da Compadecida</h2>
                <p class="diretor">Direção: Guel Arraes &bull; 2000</p>
                <p>As trapaças de João Grilo e Chicó no sertão nordestino.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
            <article class="filme" data-titulo="O Pagador de Promessas" data-diretor="Anselmo Duarte" data-ano="1962" data-seculo="XX">
                <span class="etiqueta">Drama</span>
                <h2>O Pagador de Promessas</h2>
                <p class="diretor">Direção: Anselmo Duarte &bull; 1962</p>
                <p>Zé do Burro tenta cumprir uma promessa e esbarra na intolerância.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
            <article class="filme" data-titulo="Tropa de Elite" data-diretor="José Padilha" data-ano="2007" data-seculo="XXI">
                <span class="etiqueta">Ação</span>
                <h2>Tropa de Elite</h2>
                <p class="diretor">Direção: José Padilha &bull; 2007</p>
                <p>O capitão Nascimento e a rotina violenta do BOPE.</p>
                <p class="status">Disponível</p>
                <button class="btn-alugar" type="button">Alugar</button>
            </article>
        </section>

        <p id="vazio" class="vazio" hidden>Nenhum filme encontrado com esses filtros.</p>

        <section class="bmvc">
            <h2>Como esta página chega até você</h2>
            <ol>
                <li><strong>Rota</strong> <code>GET /locadora</code> em <code>route.py</code></li>
                <li><strong>Controller</strong> <code>Application.locadora()</code> escolhe a view</li>
                <li><strong>View</strong> <code>locadora.tpl</code> carrega <code>locadora.css</code> e <code>locadora.js</code> de <code>/static</code></li>
            </ol>
        </section>
    </main>

    <footer class="rodape">
        <p>Projeto BMVC &ndash; Nível 3 &bull; <a href="/portal">Portal</a> &bull; <a href="/helper">Ajuda</a></p>
    </footer>

</body>
</html>
