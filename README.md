# BMVC – Nível 3: Portal + Banco de Filmes

> Além do CRUD, o projeto serve a página estática pública **Locadora** em `GET /locadora`
> (`locadora.tpl` + `static/css/locadora.css` + `static/js/locadora.js`).

Sistema construído sobre o framework **BMVC** (Bottle + MVC), mantendo a mesma
arquitetura do projeto base. Oferece dois recursos:

| Recurso  | Rota      | Função |
|----------|-----------|--------|
| `portal` | `/portal` | Login de usuários (modelo `UserAccount`) |
| `banco`  | `/banco`  | Lista de objetos cadastrados (modelo `Filme`) – **só para autenticados** |

Tema livre escolhido: **Filme** (`id`, `titulo`, `diretor`, `ano`).

## Arquitetura (MVC)

- **Model** – `app/models/user_account.py` e `app/models/filme.py`.
- **View** – `app/views/html/portal.tpl` (login) e `banco.tpl` (lista de filmes).
- **Controller** – `app/controllers/application.py` (regras de autenticação e
  orquestração) e `datarecord.py` (persistência em JSON:
  `db/user_accounts.json` e `db/filmes.json`).
- **Rotas** – `route.py`.

## Como funciona

1. O usuário faz login em `POST /portal`. Se as credenciais conferem, o servidor
   cria um `session_id` (UUID) guardado em memória e o envia no cookie
   `session_id`.
2. `GET /banco` (**READ**) verifica o cookie. Sem login, redireciona para
   `/portal`; com login, mostra a tabela de filmes no próprio sistema.
3. **CREATE**, **UPDATE** e **DELETE** são feitos via cURL, e também exigem o
   cookie de sessão (sem ele a resposta é `401`). Erros de validação voltam
   `400` e IDs inexistentes voltam `404`.

Usuários de teste (`app/controllers/db/user_accounts.json`):
`Henrique / 123456` e `Moura / 456789`.

## Executando

```bash
pip install bottle
python3 route.py            # http://localhost:8080
```

Ou com Docker:

```bash
docker build -t bmvci .
docker run -d -p 8080:8080 -v $(pwd):/bmeta bmvci
```

## CRUD via cURL (terminal Linux)

```bash
# 1) Login: guarda o cookie de sessão no arquivo cookies.txt
curl -i -c cookies.txt -d "username=Henrique" -d "password=123456" \
     http://localhost:8080/portal

# 2) CREATE – cria um filme (retorna 201 + JSON)
curl -b cookies.txt -X POST \
     -d "titulo=Central do Brasil" -d "diretor=Walter Salles" -d "ano=1998" \
     http://localhost:8080/banco

#    (também aceita JSON)
curl -b cookies.txt -X POST -H "Content-Type: application/json" \
     -d '{"titulo":"Tropa de Elite","diretor":"José Padilha","ano":2007}' \
     http://localhost:8080/banco

# 3) READ – no navegador: http://localhost:8080/banco (após logar em /portal)
#    ou pelo terminal, conferindo o HTML:
curl -b cookies.txt http://localhost:8080/banco

# 4) UPDATE – altera o filme de id 1 (todos os campos são reenviados)
curl -b cookies.txt -X PUT \
     -d "titulo=Central do Brasil" -d "diretor=Walter Salles" -d "ano=1999" \
     http://localhost:8080/banco/1

# 5) DELETE – remove o filme de id 2
curl -b cookies.txt -X DELETE http://localhost:8080/banco/2

# Sem cookie a resposta é 401:
curl -i -X DELETE http://localhost:8080/banco/1
```

## Observações

- O cookie é `httponly`. Foi removido o `secure=True` original porque o servidor
  roda em HTTP puro; com `secure`, o cURL e o navegador não devolveriam o cookie.
- Senhas estão em texto puro no JSON, por simplicidade didática; em produção
  seriam armazenadas com hash.
