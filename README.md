# BMVC – Nível II: Locadora Cine Nacional (CRUD completo no navegador)

Este projeto usa o framework **BMVC (Bottle + MVC)**. No Nível II, a página pública **Locadora** (`GET /locadora`) virou um sistema com **CRUD completo**, feito diretamente pelo navegador, sem login e sem cURL.

**Propósito:** gerenciar o acervo e os aluguéis de uma locadora de cinema nacional.

**Modelo:** `FilmeLocadora` (`app/models/filme_locadora.py`), com os campos `id`, `titulo`, `diretor`, `ano`, `genero`, `sinopse` e `alugado`. Ele é separado do modelo `Filme` usado no recurso `banco` do Nível 3, e seus dados ficam em `app/controllers/db/locadora.json`.

## Arquivos do Nível II

| Camada | Arquivo | Função |
|---|---|---|
| Model | `app/models/filme_locadora.py` | Estrutura do filme da locadora. |
| Controller | `app/controllers/datarecord.py` | CRUD, validação e gravação em JSON. |
| Controller | `app/controllers/application.py` | Liga as rotas ao model e renderiza a página. |
| Rotas | `route.py` | Rotas `/locadora`. |
| View | `app/views/html/locadora.tpl` | Página HTML/TPL, com a lista gerada pelo servidor (`% for`). |
| CSS | `app/static/css/locadora.css` | Visual da página, com tema claro e escuro. |
| JS | `app/static/js/locadora.js` | Chamadas `fetch()` do CRUD, busca, filtros, ordenação e tema. |

## Rotas

| Operação | Método e rota | Resposta |
|---|---|---|
| READ | `GET /locadora` | Página HTML com os filmes. |
| CREATE | `POST /locadora` (JSON) | `201` com o filme criado. |
| UPDATE | `PUT /locadora/<id>` (JSON) | `200` com o filme atualizado. Também é usada em Alugar/Devolver. |
| DELETE | `DELETE /locadora/<id>` | `200` com mensagem de remoção. |

Erros tratados: `400` (validação: título, diretor e gênero obrigatórios; ano inteiro entre 1888 e 2100) e `404` (filme não encontrado).

## O que a página faz

- **Cadastrar** um filme pelo formulário.
- **Editar** um filme (o formulário é preenchido com os dados do card).
- **Alugar / Devolver** um filme (o estado é gravado no servidor e continua após recarregar a página).
- **Excluir** um filme, com confirmação.
- **Buscar** por título ou diretor, **filtrar** por gênero, século e só alugados, e **ordenar** por título ou ano.
- **Alternar** entre tema claro e escuro (preferência salva no `localStorage`).

## Como executar

```bash
pip install bottle
python route.py
```

Acesse `http://localhost:8080/locadora`. No Windows, use `python route.py` (ou `py route.py`).

---

# BMVC – Nível 3: Portal e Banco de Filmes

Este projeto foi desenvolvido utilizando o framework **BMVC (Bottle + MVC)**, seguindo a estrutura do projeto base e ampliando suas funcionalidades.

Além das operações de CRUD, o sistema também conta com uma página pública chamada **Locadora**, acessível pela rota `GET /locadora`, que apresenta uma página estática com arquivos HTML, CSS e JavaScript.

O projeto possui duas áreas principais:

| Recurso | Rota | Descrição |
|---|---|---|
| `portal` | `/portal` | Página de login dos usuários. |
| `banco` | `/banco` | Exibe a lista de filmes cadastrados. Acesso permitido apenas após o login. |

Para o cadastro, foi escolhido o tema **Filmes**, com os seguintes campos: `id`, `titulo`, `diretor` e `ano`.

## Organização do projeto

O sistema segue o padrão MVC, separando as responsabilidades em diferentes partes:

- **Model:** contém os arquivos `user_account.py` e `filme.py`, responsáveis pela estrutura dos dados.
- **View:** contém as páginas `portal.tpl` e `banco.tpl`, utilizadas na interface do sistema.
- **Controller:** concentra as regras de funcionamento, autenticação e comunicação com os dados.
- **Rotas:** definidas em `route.py`, conectam os endereços às funcionalidades correspondentes.
- **Persistência:** os dados são armazenados em arquivos JSON, localizados em `db/user_accounts.json` e `db/filmes.json`.

## Funcionamento

O funcionamento do sistema começa pela tela de login, onde o usuário informa suas credenciais.

1. **Login:** o usuário envia seus dados por `POST /portal`. Se estiverem corretos, o sistema cria uma sessão utilizando um UUID e armazena seu identificador em um cookie chamado `session_id`.
2. **Consulta:** ao acessar `/banco`, o sistema verifica se existe uma sessão válida. Caso contrário, o usuário é redirecionado para a página de login. Se estiver autenticado, poderá visualizar os filmes cadastrados.
3. **Operações CRUD:** as operações de criação, atualização e exclusão são realizadas por meio de requisições cURL. Todas exigem uma sessão válida.

O sistema também trata diferentes situações, retornando os seguintes códigos HTTP:

- `201`: cadastro realizado com sucesso.
- `400`: erro de validação dos dados.
- `401`: usuário não autenticado.
- `404`: registro não encontrado.

**Usuários disponíveis para teste:**

- Henrique / 123456
- Moura / 456789

Os dados estão no arquivo `app/controllers/db/user_accounts.json`.

## Como executar

Primeiro, instale a dependência necessária:

```bash
pip install bottle
```

Em seguida, execute o servidor:

```bash
python3 route.py
```

O sistema estará disponível em:

`http://localhost:8080`

### Executando com Docker

Também é possível executar o projeto utilizando Docker:

```bash
docker build -t bmvci .
docker run -d -p 8080:8080 -v $(pwd):/bmeta bmvci
```

## Testando as operações CRUD

As operações de criação, consulta, atualização e exclusão podem ser testadas pelo terminal utilizando cURL.

### 1. Login

Primeiro, faça login para gerar o cookie de sessão. Ele será salvo no arquivo `cookies.txt` e utilizado nas próximas requisições.

```bash
curl -i -c cookies.txt -d "username=Henrique" -d "password=123456" \
     http://localhost:8080/portal
```

### 2. CREATE – Cadastrar filme

Para cadastrar um filme, envie uma requisição POST:

```bash
curl -b cookies.txt -X POST \
     -d "titulo=Central do Brasil" -d "diretor=Walter Salles" -d "ano=1998" \
     http://localhost:8080/banco
```

Também é possível enviar os dados no formato JSON:

```bash
curl -b cookies.txt -X POST -H "Content-Type: application/json" \
     -d '{"titulo":"Tropa de Elite","diretor":"José Padilha","ano":2007}' \
     http://localhost:8080/banco
```

### 3. READ – Consultar filmes

Após realizar o login, acesse o endereço abaixo pelo navegador para visualizar a lista de filmes:

`http://localhost:8080/banco`

Também é possível consultar pelo terminal:

```bash
curl -b cookies.txt http://localhost:8080/banco
```

### 4. UPDATE – Atualizar filme

Para atualizar um registro, utilize uma requisição PUT informando o ID do filme. Neste exemplo, será alterado o filme de ID 1:

```bash
curl -b cookies.txt -X PUT \
     -d "titulo=Central do Brasil" -d "diretor=Walter Salles" -d "ano=1999" \
     http://localhost:8080/banco/1
```

### 5. DELETE – Excluir filme

Para remover um filme, utilize uma requisição DELETE. O exemplo abaixo exclui o registro de ID 2:

```bash
curl -b cookies.txt -X DELETE http://localhost:8080/banco/2
```

**Teste de autenticação:** se uma operação for realizada sem o cookie de sessão, o sistema retornará o código `401`.

```bash
curl -i -X DELETE http://localhost:8080/banco/1
```

## Observações

- O cookie de sessão utiliza a configuração `httponly`, ajudando a impedir seu acesso direto por scripts executados no navegador.
- A opção `secure=True` foi removida porque o servidor utiliza HTTP, sem HTTPS. Mantê-la impediria o envio do cookie em conexões HTTP.
- As senhas são armazenadas em texto puro nos arquivos JSON. Essa escolha foi feita para simplificar o projeto, mas, em uma aplicação real, o ideal seria utilizar hash para proteger as senhas.
