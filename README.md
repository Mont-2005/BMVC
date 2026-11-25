# BMVC – Nível III: Locadora Cine Nacional (CRUD completo + login e área restrita)

Este projeto usa o framework **BMVC (Bottle + MVC)**. No Nível III, a locadora ganhou **controle de acesso de usuários**: um **sistema de login** e uma **página de acesso restrito** (gestão do acervo), com dois papéis de funcionário.

**Propósito:** gerenciar o acervo e os aluguéis de uma locadora de cinema nacional, com o catálogo aberto ao público e a gestão restrita a funcionários.

## Modelos

| Modelo | Arquivo | Dados |
|---|---|---|
| `FilmeLocadora` | `app/models/filme_locadora.py` | `id`, `titulo`, `diretor`, `ano`, `genero`, `sinopse`, `alugado` (`db/locadora.json`) |
| `Funcionario` | `app/models/funcionario.py` | `username`, `nome`, `papel`, `salt`, `senha_hash` (`db/funcionarios.json`) |

## Páginas

| Página | Acesso | Função |
|---|---|---|
| `GET /locadora` | Público | Catálogo somente leitura, com busca, filtros e ordenação. |
| `GET /entrar` | Público | Página de login. |
| `GET /gestao` | **Restrita** (sem login redireciona para `/entrar`) | CRUD do acervo, conforme o papel. |

## Papéis (controle de acesso)

| Papel | O que pode fazer |
|---|---|
| `gerente` | CRUD completo: cadastrar, editar, excluir, alugar e devolver. |
| `atendente` | Apenas alugar e devolver. A tela esconde os demais botões e o **servidor também bloqueia** (`403`). |

Contas de teste (senhas guardadas só como hash PBKDF2 com sal):

| Usuário | Senha | Papel |
|---|---|---|
| `gerente` | `gerente123` | gerente |
| `atendente` | `atendente123` | atendente |

## Rotas

| Operação | Método e rota | Quem | Resposta |
|---|---|---|---|
| Login | `POST /entrar` | Público | Cria a sessão (cookie `HttpOnly`) e vai para `/gestao`; erro volta para `/entrar?erro=1`. |
| Logout | `POST /sair` | Qualquer | Encerra a sessão e vai para `/locadora`. |
| CREATE | `POST /api/filmes` (JSON) | gerente | `201` com o filme criado. |
| UPDATE | `PUT /api/filmes/<id>` (JSON) | gerente (tudo) / atendente (só `alugado`) | `200` com o filme atualizado. |
| DELETE | `DELETE /api/filmes/<id>` | gerente | `200` com mensagem de remoção. |

Erros tratados: `400` (validação), `401` (sem login), `403` (papel sem permissão) e `404` (filme não encontrado).

## Segurança

- Senhas **nunca** ficam em texto: `PBKDF2-HMAC-SHA256` com sal por usuário, comparado com `hmac.compare_digest`.
- Sessão por `session_id` aleatório (UUID) em cookie `HttpOnly`, guardada na memória do servidor.
- A permissão é checada **no servidor** em cada rota da API; esconder botões na tela é só conforto visual.

## Arquivos

| Camada | Arquivo |
|---|---|
| Models | `app/models/filme_locadora.py`, `app/models/funcionario.py` |
| Controller | `app/controllers/datarecord.py` (CRUD, hash, sessões), `app/controllers/application.py` (páginas e acesso) |
| Rotas | `route.py` |
| Views | `app/views/html/locadora.tpl`, `entrar.tpl`, `gestao.tpl` |
| CSS | `app/static/css/locadora.css` |
| JS | `app/static/js/locadora.js` (CRUD, filtros, tema), `app/static/js/entrar.js` (mostrar senha, tema) |

## Como executar

```bash
pip install bottle
python route.py
```

Acesse `http://localhost:8080/locadora`. No Windows, use `python route.py` (ou `py route.py`).
