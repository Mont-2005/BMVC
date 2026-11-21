<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Banco de Filmes</title>
</head>
<body>
    <h1>Banco de Filmes</h1>
    <p>Usuário autenticado: <strong>{{ username }}</strong></p>

    % if filmes:
        <table border="1" cellpadding="6">
            <tr><th>ID</th><th>Título</th><th>Diretor</th><th>Ano</th></tr>
            % for filme in filmes:
                <tr>
                    <td>{{ filme.id }}</td>
                    <td>{{ filme.titulo }}</td>
                    <td>{{ filme.diretor }}</td>
                    <td>{{ filme.ano }}</td>
                </tr>
            % end
        </table>
    % else:
        <p>Nenhum filme cadastrado. Use o cURL para criar (veja o README).</p>
    % end

    <form action="/logout" method="post">
        <button type="submit">Logout</button>
    </form>
</body>
</html>
