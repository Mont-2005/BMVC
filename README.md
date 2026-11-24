# BMVC – Nível II: Locadora Cine Nacional (CRUD completo no navegador)

Este projeto usa o framework **BMVC (Bottle + MVC)**. No Nível II, a página pública **Locadora** (`GET /locadora`) virou um sistema com **CRUD completo**, feito diretamente pelo navegador, sem login e sem cURL.

**Propósito:** gerenciar o acervo e os aluguéis de uma locadora de cinema nacional.

**Modelo:** `FilmeLocadora` (`app/models/filme_locadora.py`), com os campos `id`, `titulo`, `diretor`, `ano`, `genero`, `sinopse` e `alugado`. Seus dados ficam em `app/controllers/db/locadora.json`.

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
