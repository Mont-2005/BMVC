document.addEventListener('DOMContentLoaded', function () {
    var lista = document.getElementById('lista');
    var cards = Array.prototype.slice.call(lista.querySelectorAll('.filme'));
    var busca = document.getElementById('busca');
    var genero = document.getElementById('filtro-genero');
    var seculo = document.getElementById('filtro-seculo');
    var ordem = document.getElementById('ordem');
    var soAlugados = document.getElementById('so-alugados');
    var contador = document.getElementById('contador');
    var vazio = document.getElementById('vazio');
    var btnTema = document.getElementById('btn-tema');

    function ler(chave, padrao) {
        try {
            var v = localStorage.getItem(chave);
            return v === null ? padrao : JSON.parse(v);
        } catch (e) { return padrao; }
    }

    function gravar(chave, valor) {
        try { localStorage.setItem(chave, JSON.stringify(valor)); } catch (e) {}
    }

    var alugados = ler('locadora_alugados', []);

    function semAcento(texto) {
        return texto.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLowerCase();
    }

    function atualizar() {
        var termo = semAcento(busca.value.trim());
        var visiveis = 0;

        cards.sort(function (a, b) {
            if (ordem.value === 'ano') {
                return Number(a.dataset.ano) - Number(b.dataset.ano);
            }
            return a.dataset.titulo.localeCompare(b.dataset.titulo, 'pt-BR');
        });

        cards.forEach(function (card) {
            var texto = semAcento(card.dataset.titulo + ' ' + card.dataset.diretor);
            var generoCard = card.querySelector('.etiqueta').textContent;
            var ok = texto.indexOf(termo) !== -1 &&
                (genero.value === 'todos' || generoCard === genero.value) &&
                (seculo.value === 'todos' || card.dataset.seculo === seculo.value) &&
                (!soAlugados.checked || alugados.indexOf(card.dataset.titulo) !== -1);
            card.hidden = !ok;
            lista.appendChild(card);
            if (ok) { visiveis++; }
        });

        contador.textContent = visiveis + ' de ' + cards.length + ' filmes exibidos \u2022 ' +
            alugados.length + ' alugado(s) \u2022 ' + (cards.length - alugados.length) + ' disponível(is)';
        vazio.hidden = visiveis !== 0;
    }

    function marcarAluguel(card) {
        var ativo = alugados.indexOf(card.dataset.titulo) !== -1;
        card.classList.toggle('alugado', ativo);
        card.querySelector('.status').textContent = ativo ? 'Alugado' : 'Disponível';
        card.querySelector('.btn-alugar').textContent = ativo ? 'Devolver' : 'Alugar';
    }

    cards.forEach(function (card) {
        marcarAluguel(card);
        card.querySelector('.btn-alugar').addEventListener('click', function () {
            var titulo = card.dataset.titulo;
            var i = alugados.indexOf(titulo);
            if (i === -1) { alugados.push(titulo); } else { alugados.splice(i, 1); }
            gravar('locadora_alugados', alugados);
            marcarAluguel(card);
            atualizar();
        });
    });

    function aplicarTema(escuro) {
        document.body.classList.toggle('escuro', escuro);
        btnTema.textContent = escuro ? 'Modo claro' : 'Modo escuro';
        gravar('locadora_tema_escuro', escuro);
    }

    btnTema.addEventListener('click', function () {
        aplicarTema(!document.body.classList.contains('escuro'));
    });

    [busca, genero, seculo, ordem, soAlugados].forEach(function (el) {
        el.addEventListener('input', atualizar);
        el.addEventListener('change', atualizar);
    });

    aplicarTema(ler('locadora_tema_escuro', true));
    atualizar();
});
