document.addEventListener('DOMContentLoaded', function () {
    var senha = document.getElementById('password');
    var mostrar = document.getElementById('mostrar');
    var btnTema = document.getElementById('btn-tema');

    mostrar.addEventListener('change', function () {
        senha.type = mostrar.checked ? 'text' : 'password';
    });

    // Mesmo tema escolhido nas outras páginas (localStorage)
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
    aplicarTema(salvo);
});
