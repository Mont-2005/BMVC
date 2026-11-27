# BMVC – Nível IV: Locadora Cine Nacional (CRUD + login + WebSocket em tempo real)

Este projeto usa o framework **BMVC (Bottle + MVC)**. A locadora tem **controle de acesso de usuários** (**login** e **página de acesso restrito**, com dois papéis de funcionário) e, no Nível IV, ganhou **comunicação WebSocket**: tudo o que acontece no acervo aparece **em tempo real** para todas as pessoas conectadas, sem recarregar a página.

**Propósito:** gerenciar o acervo e os aluguéis de uma locadora de cinema nacional, com o catálogo aberto ao público e a gestão restrita a funcionários.

## Modelos

| Modelo | Arquivo | Dados |
|---|---|---|
| `FilmeLocadora` | `app/models/filme_locadora.py` | `id`, `titulo`, `diretor`, `ano`, `genero`, `sinopse`, `alugado` (`db/locadora.json`) |
| `Funcionario` | `app/models/funcionario.py` | `username`, `nome`, `papel`, `salt`, `senha_hash` (`db/funcionarios.json`) |

## Páginas

| Página | Acesso | Função |
|---|---|---|
| `GET /locadora` | Público | Catálogo somente leitura, com busca, filtros e ordenação, atualizado ao vivo. |
| `GET /entrar` | Público | Página de login. |
| `GET /gestao` | **Restrita** (sem login redireciona para `/entrar`) | CRUD do acervo conforme o papel, com o painel **Atividade em tempo real**. |

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

## Tempo real (WebSocket)

O servidor WebSocket (`app/controllers/realtime.py`) segue o protocolo RFC 6455 e usa **somente a biblioteca padrão do Python**, sem instalar nada além do `bottle`. Ele roda em uma thread própria, ao lado do Bottle, na porta **8765** (`ws://localhost:8765/ws`).

| Evento enviado | Quem recebe | O que acontece na página |
|---|---|---|
| `filme_criado`, `filme_atualizado`, `filme_removido` | Todos (catálogo e gestão) | O card aparece, muda ou some na hora, com destaque visual e aviso na tela. |
| `atividade` ("Marina (gerente) alugou ...") | **Só quem está logado** | Entra no painel "Atividade em tempo real" da gestão (guarda as 15 últimas). |
| `presenca` | Todos | Mostra quantas pessoas e quantos funcionários estão online. |

- O indicador **ao vivo / reconectando** mostra o estado da conexão, e o navegador reconecta sozinho se a conexão cair.
- O servidor lê o cookie de sessão na conexão: visitantes públicos nunca recebem os nomes de quem fez cada ação.
- Conexões de outros sites (cabeçalho `Origin` diferente do host) são recusadas, e há limite de conexões e de tamanho de mensagem.
- Se a porta 8765 estiver ocupada, o site continua funcionando, só sem atualização ao vivo (o terminal avisa).

## Segurança

- Senhas **nunca** ficam em texto: `PBKDF2-HMAC-SHA256` com sal por usuário, comparado com `hmac.compare_digest`.
- Sessão por `session_id` aleatório (UUID) em cookie `HttpOnly`, guardada na memória do servidor.
- A permissão é checada **no servidor** em cada rota da API; esconder botões na tela é só conforto visual.

## Arquivos

| Camada | Arquivo |
|---|---|
| Models | `app/models/filme_locadora.py`, `app/models/funcionario.py` |
| Controller | `app/controllers/datarecord.py` (CRUD, hash, sessões), `app/controllers/application.py` (páginas, acesso e eventos), `app/controllers/realtime.py` (servidor WebSocket) |
| Rotas | `route.py` |
| Views | `app/views/html/locadora.tpl`, `entrar.tpl`, `gestao.tpl` |
| CSS | `app/static/css/locadora.css` |
| JS | `app/static/js/locadora.js` (CRUD, filtros, tema, cliente WebSocket), `app/static/js/entrar.js` (mostrar senha, tema) |

## Como executar

```bash
pip install bottle
python route.py
```

Acesse `http://localhost:8080/locadora`. No Windows, use `python route.py` (ou `py route.py`). Para ver o tempo real, abra a página em **duas janelas** (por exemplo, uma pública e outra logada) e altere o acervo em uma delas.

Com Docker, publique as duas portas: `-p 8080:8080 -p 8765:8765`.
