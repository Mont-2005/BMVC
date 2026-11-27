document.addEventListener('DOMContentLoaded', function () {
    function byId(i) { return document.getElementById(i); }

    var modo = document.body.dataset.modo;                 // 'catalogo' ou 'gestao'
    var gerente = document.body.dataset.gerente === 'true'; // papel vem do servidor (TPL)
    var lista = byId('lista');
    var msg = byId('mensagem');
    var form = byId('form-filme');                          // só existe para o gerente
    var busca = byId('busca'), genero = byId('filtro-genero'), seculo = byId('filtro-seculo');
    var ordem = byId('ordem'), soAlugados = byId('so-alugados');
    var contador = byId('contador'), vazio = byId('vazio'), btnTema = byId('btn-tema');
    var limparForm = null, campos = null;     // preenchidos para o gerente

    function aviso(texto, tipo) {
        if (!msg) { return; }
        msg.textContent = texto; msg.className = tipo || '';
    }

    // Todas as chamadas ao servidor passam por aqui (cookie de sessão vai junto)
    function api(metodo, url, dados) {
        return fetch(url, {
            method: metodo,
            headers: { 'Content-Type': 'application/json' },
            body: dados ? JSON.stringify(dados) : undefined
        }).then(function (r) {
            if (r.status === 401) {                     // sessão expirou: volta ao login
                window.location.href = '/entrar?aviso=1';
                throw new Error('Sessão expirada.');
            }
            return r.json().then(function (j) {
                if (!r.ok) { throw new Error(j.erro || 'Erro inesperado'); }
                return j;
            });
        });
    }

    function cards() { return Array.prototype.slice.call(lista.querySelectorAll('.filme')); }
    function semAcento(t) { return t.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase(); }

    function dadosDoCard(card) {
        return {
            titulo: card.dataset.titulo, diretor: card.dataset.diretor,
            ano: card.dataset.ano, genero: card.dataset.genero,
            sinopse: card.dataset.sinopse, alugado: card.dataset.alugado === 'true'
        };
    }

    // Preenche (ou recria) o card a partir dos dados do servidor
    function montarCard(f, card) {
        card = card || document.createElement('article');
        card.className = 'filme' + (f.alugado ? ' alugado' : '');
        card.dataset.id = f.id; card.dataset.titulo = f.titulo; card.dataset.diretor = f.diretor;
        card.dataset.ano = f.ano; card.dataset.genero = f.genero; card.dataset.sinopse = f.sinopse || '';
        card.dataset.alugado = f.alugado ? 'true' : 'false';
        card.innerHTML = '<span class="etiqueta"></span><h2></h2><p class="diretor"></p><p class="sinopse"></p>' +
            '<p class="status"></p>' +
            (modo === 'gestao' ? '<div class="botoes">' +
                '<button class="btn-alugar" type="button"></button>' +
                (gerente ? '<button class="btn-editar" type="button">Editar</button>' +
                           '<button class="btn-excluir" type="button">Excluir</button>' : '') +
                '</div>' : '');
        card.querySelector('.etiqueta').textContent = f.genero;
        card.querySelector('h2').textContent = f.titulo;
        card.querySelector('.diretor').textContent = 'Direção: ' + f.diretor + ' \u2022 ' + f.ano;
        card.querySelector('.sinopse').textContent = f.sinopse || '';
        card.querySelector('.status').textContent = f.alugado ? 'Alugado' : 'Disponível';
        var btn = card.querySelector('.btn-alugar');
        if (btn) { btn.textContent = f.alugado ? 'Devolver' : 'Alugar'; }
        return card;
    }

    // Cria o card se não existir ou atualiza o existente (usado pelo CRUD e pelo WebSocket)
    function upsertCard(f) {
        var atual = lista.querySelector('.filme[data-id="' + f.id + '"]');
        var card = montarCard(f, atual);
        if (!atual) { lista.appendChild(card); }
        return card;
    }

    function atualizar() {
        var termo = semAcento(busca.value.trim());
        var todos = cards();
        var visiveis = 0, alugados = 0;

        todos.sort(function (a, b) {
            if (ordem.value === 'ano') { return Number(a.dataset.ano) - Number(b.dataset.ano); }
            return a.dataset.titulo.localeCompare(b.dataset.titulo, 'pt-BR');
        });

        todos.forEach(function (card) {
            var ehAlugado = card.dataset.alugado === 'true';
            var sec = Number(card.dataset.ano) >= 2001 ? 'XXI' : 'XX';
            var texto = semAcento(card.dataset.titulo + ' ' + card.dataset.diretor);
            var ok = texto.indexOf(termo) !== -1 &&
                (genero.value === 'todos' || card.dataset.genero === genero.value) &&
                (seculo.value === 'todos' || sec === seculo.value) &&
                (!soAlugados.checked || ehAlugado);
            if (ehAlugado) { alugados++; }
            card.hidden = !ok;
            lista.appendChild(card);
            if (ok) { visiveis++; }
        });

        contador.textContent = visiveis + ' de ' + todos.length + ' filmes exibidos \u2022 ' +
            alugados + ' alugado(s) \u2022 ' + (todos.length - alugados) + ' disponível(is)';
        vazio.hidden = visiveis !== 0;
    }

    // ---------- CRUD (somente na área restrita) ----------
    if (modo === 'gestao') {
        if (form) {   // formulário existe só para o gerente
            campos = {
                id: byId('filme-id'), titulo: byId('f-titulo'), diretor: byId('f-diretor'),
                ano: byId('f-ano'), genero: byId('f-genero'), sinopse: byId('f-sinopse')
            };
            var btnSalvar = byId('btn-salvar'), btnCancelar = byId('btn-cancelar'), tituloForm = byId('titulo-form');

            limparForm = function () {
                form.reset(); campos.id.value = '';
                tituloForm.textContent = 'Cadastrar filme';
                btnSalvar.textContent = 'Adicionar filme';
                btnCancelar.hidden = true;
            };

            // CREATE e UPDATE
            form.addEventListener('submit', function (e) {
                e.preventDefault();
                var dados = {
                    titulo: campos.titulo.value, diretor: campos.diretor.value, ano: campos.ano.value,
                    genero: campos.genero.value, sinopse: campos.sinopse.value
                };
                var id = campos.id.value;
                var atual = id ? lista.querySelector('.filme[data-id="' + id + '"]') : null;
                if (atual) { dados.alugado = atual.dataset.alugado === 'true'; }
                var req = id ? api('PUT', '/api/filmes/' + id, dados) : api('POST', '/api/filmes', dados);
                req.then(function (f) {
                    upsertCard(f);
                    aviso(id ? 'Filme atualizado!' : 'Filme adicionado ao acervo!', 'ok');
                    limparForm(); atualizar();
                }).catch(function (err) { aviso(err.message, 'erro'); });
            });

            btnCancelar.addEventListener('click', function () { limparForm(); aviso(''); });

            // Editar (preenche o formulário)
            lista.addEventListener('click', function (e) {
                if (!e.target.classList.contains('btn-editar')) { return; }
                var card = e.target.closest('.filme');
                var c = dadosDoCard(card);
                campos.id.value = card.dataset.id; campos.titulo.value = c.titulo; campos.diretor.value = c.diretor;
                campos.ano.value = c.ano; campos.genero.value = c.genero; campos.sinopse.value = c.sinopse;
                tituloForm.textContent = 'Editando: ' + c.titulo;
                btnSalvar.textContent = 'Salvar alterações';
                btnCancelar.hidden = false;
                form.scrollIntoView({ behavior: 'smooth', block: 'center' });
                campos.titulo.focus();
            });
        }

        // Alugar/Devolver (gerente e atendente) e Excluir (gerente)
        lista.addEventListener('click', function (e) {
            var card = e.target.closest('.filme'); if (!card) { return; }
            var id = card.dataset.id;

            if (e.target.classList.contains('btn-alugar')) {
                var d = dadosDoCard(card);
                d.alugado = !d.alugado;
                api('PUT', '/api/filmes/' + id, d).then(function (f) {
                    upsertCard(f); atualizar();
                }).catch(function (err) { aviso(err.message, 'erro'); });
            }

            if (e.target.classList.contains('btn-excluir')) {
                if (!confirm('Excluir "' + card.dataset.titulo + '" do acervo?')) { return; }
                api('DELETE', '/api/filmes/' + id).then(function () {
                    card.remove(); aviso('Filme removido.', 'ok'); atualizar();
                }).catch(function (err) { aviso(err.message, 'erro'); });
            }
        });
    }

    // ---------- Tempo real (WebSocket) ----------
    var statusWs = byId('status-ws'), presenca = byId('presenca'), toasts = byId('toasts');
    var feed = byId('atividades'), semAtividade = byId('sem-atividade');
    var porta = document.body.dataset.wsPorta;
    var tentativas = 0;

    function toast(texto) {
        if (!toasts) { return; }
        var t = document.createElement('div');
        t.className = 'toast'; t.textContent = texto;
        toasts.appendChild(t);
        setTimeout(function () { t.classList.add('sai'); }, 3500);
        setTimeout(function () { t.remove(); }, 4200);
    }

    function piscar(card) {
        card.classList.remove('piscar'); void card.offsetWidth; card.classList.add('piscar');
    }

    function marcarStatus(on, texto) {
        if (!statusWs) { return; }
        statusWs.className = 'status-ws ' + (on ? 'on' : 'off');
        statusWs.textContent = '\u25CF ' + texto;
    }

    function adicionarAtividade(item) {
        if (!feed) { return; }
        var li = document.createElement('li');
        var hora = document.createElement('time'); hora.textContent = item.hora;
        var txt = document.createElement('span'); txt.textContent = ' ' + item.texto;
        li.appendChild(hora); li.appendChild(txt);
        feed.insertBefore(li, feed.firstChild);
        while (feed.children.length > 15) { feed.removeChild(feed.lastChild); }
        if (semAtividade) { semAtividade.hidden = true; }
    }

    function tratarEvento(ev) {
        if (ev.tipo === 'presenca') {
            if (presenca) {
                presenca.textContent = ev.total + (ev.total === 1 ? ' pessoa online' : ' pessoas online') +
                    (modo === 'gestao' ? ' \u2022 ' + ev.funcionarios + ' funcionário(s)' : '');
            }
        } else if (ev.tipo === 'filme_criado' || ev.tipo === 'filme_atualizado') {
            var f = ev.filme;
            var existia = !!lista.querySelector('.filme[data-id="' + f.id + '"]');
            var antes = existia ? lista.querySelector('.filme[data-id="' + f.id + '"]').dataset.alugado : null;
            var card = upsertCard(f);
            // se o gerente está editando justo este filme, o formulário continua como está
            atualizar(); piscar(card);
            if (!existia) { toast('Novo filme no acervo: ' + f.titulo); }
            else if (antes !== String(f.alugado)) { toast('"' + f.titulo + '" agora está ' + (f.alugado ? 'alugado' : 'disponível')); }
            else { toast('"' + f.titulo + '" foi atualizado'); }
        } else if (ev.tipo === 'filme_removido') {
            var c = lista.querySelector('.filme[data-id="' + ev.id + '"]');
            if (c) { c.remove(); atualizar(); toast('"' + ev.titulo + '" saiu do acervo'); }
            if (campos && campos.id.value === String(ev.id)) {
                limparForm(); aviso('O filme que você editava foi excluído por outra pessoa.', 'erro');
            }
        } else if (ev.tipo === 'atividade') {
            adicionarAtividade(ev);
        }
    }

    function conectar() {
        var proto = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        var ws;
        try { ws = new WebSocket(proto + window.location.hostname + ':' + porta + '/ws'); }
        catch (e) { marcarStatus(false, 'sem tempo real'); return; }

        ws.onopen = function () {
            tentativas = 0; marcarStatus(true, 'ao vivo');
            ws._ping = setInterval(function () { if (ws.readyState === 1) { ws.send('ping'); } }, 25000);
        };
        ws.onmessage = function (m) {
            try { tratarEvento(JSON.parse(m.data)); } catch (e) {}
        };
        ws.onclose = function () {
            clearInterval(ws._ping);
            tentativas++;
            marcarStatus(false, 'reconectando...');
            setTimeout(conectar, Math.min(1000 * tentativas, 8000));
        };
    }
    if (porta) { conectar(); }

    // Tema claro/escuro (apenas preferência visual no localStorage)
    function aplicarTema(escuro) {
        document.body.classList.toggle('escuro', escuro);
        btnTema.textContent = escuro ? 'Modo claro' : 'Modo escuro';
        try { localStorage.setItem('locadora_tema_escuro', JSON.stringify(escuro)); } catch (e) {}
    }
    btnTema.addEventListener('click', function () {
        aplicarTema(!document.body.classList.contains('escuro'));
    });
    var salvo = true;
    try { var v = localStorage.getItem('locadora_tema_escuro'); if (v !== null) { salvo = JSON.parse(v); } } catch (e) {}

    [busca, genero, seculo, ordem, soAlugados].forEach(function (el) {
        el.addEventListener('input', atualizar);
        el.addEventListener('change', atualizar);
    });

    aplicarTema(salvo);
    atualizar();
});
