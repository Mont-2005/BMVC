<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Banco de Livros</title>
</head>
<body>
    <h1>Banco de Livros</h1>
    <p>Usuário autenticado: <strong>{{ username }}</strong></p>

    % if livros:
        <table border="1" cellpadding="6">
            <tr><th>ID</th><th>Título</th><th>Autor</th><th>Ano</th></tr>
            % for livro in livros:
                <tr>
                    <td>{{ livro.id }}</td>
                    <td>{{ livro.titulo }}</td>
                    <td>{{ livro.autor }}</td>
                    <td>{{ livro.ano }}</td>
                </tr>
            % end
        </table>
    % else:
        <p>Nenhum livro cadastrado. Use o cURL para criar (veja o README).</p>
    % end

    <form action="/logout" method="post">
        <button type="submit">Logout</button>
    </form>
</body>
</html>
