# specs.md — Especificação de implementação

## Retenção — #266, Bloco 5

Derivado de docs/requisitos.md, decisão B do PO. DELETE /api/auth/conta exclui
logicamente a própria conta autenticada, revoga credenciais e oculta conteúdo.
DELETE /api/avaliacoes/{id} exclui avaliação própria; DELETE
/api/moderacao/avaliacoes/{id} permite remoção urgente por moderador confirmado.
Essas ações não passam pelo limitador e preservam CSRF/autorização. Conteúdo
oculto não participa das consultas públicas e não pode ser reativado por upsert
antes da purga. Estado/migração e job seguem docs/seguranca/retencao-bloco-5.md.

## Abuso e respostas temporárias — #266, Blocos 3 e 4

Derivado da restrição transversal em docs/requisitos.md, fonte PO. Avaliações,
denúncias, canal público e operações de moderação/reconciliação recebem adaptadores
do núcleo existente; nenhuma alteração de esquema. 429 e 503 incluem Retry-After.
O cliente HTTP interpreta segundos ou data HTTP sem mostrar detalhes internos,
preserva formulários e mantém alertas acessíveis. Matriz e parâmetros documentados
em docs/seguranca/limitador-fluxos-blocos-3-4.md.

## Autenticação e abuso — #266, Bloco 2

Derivada da restrição transversal de autenticação em `docs/requisitos.md`, fonte:
pedido `EXECUTAR: BLOCO 2` do PO. Núcleo do Bloco 1 será usado em todos os POST de
autenticação, exceto logout. Conta/papel não libera login, cadastro ou tokens.
429/503 usam Retry-After e respostas sem detalhes internos. Erros do provedor nos
fluxos de envio recebem 202 neutro, sem expor se houve envio/conta existente.
Novo POST `/api/auth/reenviar-confirmacao`: `{email, return_to?}`, mesmos validadores
de cadastro/retorno, 202 neutro para conta pendente, confirmada ou inexistente.
Sob restrição, nenhum desses endpoints pode criar usuário, sessão, token, trocar
senha ou enviar e-mail. Confirmação/redefinição preservam prazo e uso único.
O orçamento diário de e-mail é compartilhado e alinhado à meia-noite UTC, incluindo
reservas sem envio; não é uma janela fixa ancorada na primeira solicitação.

## Proteção de origens — #266

Derivada da restrição transversal aprovada em `docs/requisitos.md` em 16/11/2026.
Antes dos efeitos de POST/PUT/PATCH/DELETE em `/api`, conferir Origin exato na lista
`CORS_ORIGINS`. Externo, `null`, inválido ou duplicado retorna 403 genérico. Sem Origin,
validar origem de Referer se presente; sem ambos, negar login e operações com cookie
`undb_session`. Outras operações sem cookie seguem seu contrato. Não inferir origem
de Host ou cabeçalhos encaminhados; preflight e GET mantêm comportamento existente.
Frontend usa fetch JSON com credenciais. Esse controle não autentica clientes HTTP,
não define rate limit e não modifica os atributos/prazos da sessão.

## Canal de contato, solicitações de titulares e política de moderação — RF25

Derivado de `docs/requisitos.md`, RF25 (consolidação das issues #262, #263 e #264 em 17/11/2026).
POST `/api/solicitacoes` recebe categoria, alvo, descrição e evidência textual;
devolve protocolo UUID aleatório, chave secreta e data. Consultar e complementar usam
POST com protocolo/chave no corpo, nunca URL. Apenas SHA-256 da chave fica persistido.
GET `/api/atendimento` e detalhe usam sessão confirmada e UUID em allowlist própria;
POST de eventos exige allowlist de atendentes. Leitores não podem registrar eventos.
Campos internos de triagem, providências e identidade do atendente não são retornados ao
solicitante. Não vincular solicitante a uma avaliação nem copiar dados de avaliadores.
Schema independente: `solicitacoes_titulares` 1:N `eventos_solicitacoes`; autor interno
referencia `usuarios`, sem mudar privilégios de moderadores/reconciliadores.
Recebimento exige flags de ativação/retenção e lista de atendentes configurada.

Pedidos de titulares (LGPD): verificação proporcional de identidade. Distinção entre:
(a) retirada de comentário (autor retira texto, denúncias viram CONTEUDO_RETIRADO, texto descartado
em 7 dias pela rotina; critérios estruturados permanecem); (b) desativação de conta (revogação de
sessões e tokens); e (c) exclusão de conta (limite: destino de avaliações e notas exige decisão do PO;
não apagar nem desvincular notas sem aprovação).

Política de moderação: crítica acadêmica legítima é permitida; ofensas, ameaças, discriminação
e exposição de dados são proibidas. Discordância docente não causa remoção. Triagem não rejeita
automaticamente; casos com sinal aguardam revisão humana. Gatilho de 50 contas suspende exibição,
mas uma única ocorrência fundamentada pode ser atendida manualmente. Revisão de decisão de
moderação é solicitada via protocolo/complemento. Moderação de texto não altera notas; votos de
utilidade (#278) não são denúncias e não acionam moderação.

Documento **derivado**. Fontes de verdade: [`docs/requisitos.md`](docs/requisitos.md) e
[`docs/arquitetura.md`](docs/arquitetura.md).

Este arquivo existe para eliminar ambiguidade na implementação. Não contém justificativas —
elas estão nos documentos de origem. Se algo aqui contradisser os documentos de origem,
os documentos de origem prevalecem e este arquivo deve ser corrigido.

**Regra para agentes:** o que não estiver especificado aqui e não estiver nos documentos de
origem é decisão em aberto. Não invente o valor; pare e registre a lacuna.

---

## 1. Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12, FastAPI, Uvicorn |
| ORM | SQLAlchemy síncrono |
| Migrações | Alembic |
| Banco | PostgreSQL via `psycopg2` |
| Frontend | Next.js |
| Container | Docker Compose |
| Configuração | `python-decouple`, lida via `app/core/config.py` |

Segredos nunca em código. Nenhuma alteração de schema fora de migração Alembic.
`DATABASE_URL` segue o formato
`postgresql+psycopg2://usuario:senha@host:porta/banco`.

---

## 2. Enums

```python
class Dificuldade(str, Enum):
    FACIL = "FACIL"
    MEDIO = "MEDIO"
    DIFICIL = "DIFICIL"

class QualidadeMaterial(str, Enum):
    RUIM = "RUIM"
    MEDIO = "MEDIO"
    BOM = "BOM"

class EstadoComentario(str, Enum):
    PENDENTE = "PENDENTE"
    PUBLICADO = "PUBLICADO"
    SUSPENSO = "SUSPENSO"
    REMOVIDO = "REMOVIDO"
    RETIRADO = "RETIRADO"
    SUBSTITUIDO = "SUBSTITUIDO"
```

Ordinalidade aprovada para desempate de moda:
`DIFICIL > MEDIO > FACIL` e `BOM > MEDIO > RUIM`.

O recorte de `EstadoComentario` acima registra a base da #156, anterior à moderação.
O contrato publicado pela [PR #192](https://github.com/unb-mds/2026-02-UnDb/pull/192)
e o acompanhamento integrado pela [PR #197](https://github.com/unb-mds/2026-02-UnDb/pull/197)
também contemplam `REJEITADO` e descarte de texto. Consulte a seção 12 para a
referência vigente; o recorte histórico não é uma nova definição de contrato.

---

## 3. Modelo de dados

**Complemento técnico da PR #215 (10/11/2026):** respostas institucionais de
professor/disciplina, agregado e comparação podem incluir `departamento_nome`
(`string | null`), obtido do `nome` da unidade vinculada à fonte `SIGAA`.
`departamento` continua sendo o código de identidade/filtro. A associação ORM é
somente de leitura, com carregamento junto à entidade; não cria campo físico ou
migração. Ausência de correspondência preserva o registro e produz nome nulo.
No frontend, `departamentoNome` é opcional: nome institucional válido tem
preferência; código textual permanece como fallback e código numérico aparece
como `Unidade <código>`. Não inventar siglas nem unir pessoas/unidades por nome.
Publicar API e frontend para obter o nome completo no ambiente público.

Esta seção preserva o recorte do modelo da Release 1 e da base RF20 da #156.
RF21/RF22 foram entregues pela [PR #192](https://github.com/unb-mds/2026-02-UnDb/pull/192),
integrada em `81e54be`; seus modelos e contratos estão no
[contrato publicado](docs/estudos/alinhamento-denuncias-issues-160-161.md#resolucao-pelo-po-e-contrato-de-implementacao),
referenciado na seção 12. As tabelas deste recorte não representam todo o modelo R2.

### `usuarios`
| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK |
| `nome` | VARCHAR(100) | obrigatório |
| `email` | VARCHAR(150) | UNIQUE, obrigatório, domínio `@aluno.unb.br` |
| `password_hash` | VARCHAR(255) | hash forte |
| `termos_versao` | VARCHAR(32), nullable | RF26: versão da ciência no novo cadastro; NULL nas contas anteriores |
| `termos_ciencia_em` | TIMESTAMPTZ, nullable | RF26: instante gerado pelo servidor; CHECK exige o par completo ou ambos NULL |
| `email_confirmado` | BOOLEAN | default `false` |
| `created_at` | TIMESTAMPTZ | default now |

Não armazenar matrícula, CPF, IRA ou histórico acadêmico.

### `email_confirmation_tokens`
| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK |
| `usuario_id` | FK → `usuarios` | obrigatório |
| `token_hash` | VARCHAR(64) | UNIQUE, obrigatório; nunca persistir token aberto |
| `expires_at` | TIMESTAMPTZ | obrigatório; 24 horas após emissão |
| `used_at` | TIMESTAMPTZ | nulo até o primeiro uso válido |
| `created_at` | TIMESTAMPTZ | default now |

### `sessoes_usuario`
| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK |
| `usuario_id` | FK → `usuarios` | obrigatório |
| `token_hash` | VARCHAR(64) | UNIQUE, obrigatório; nunca persistir token aberto |
| `expires_at` | TIMESTAMPTZ | obrigatório; sete dias após a última atividade autenticada válida |
| `created_at` | TIMESTAMPTZ | default now |

### `unidades`
`id` UUID PK · `fonte` VARCHAR(30) · `codigo` VARCHAR(30) ·
`identificador_externo` VARCHAR(50) nullable · `nome` VARCHAR(200)

Constraint: `UNIQUE(fonte, codigo)`.

### `professores`
`id` UUID PK · `nome` VARCHAR(150) · `nome_normalizado` VARCHAR(150) ·
`departamento` VARCHAR(100) · `siape` VARCHAR(30) nullable UNIQUE ·
`identidade_origem` VARCHAR(255) nullable UNIQUE · `identidade_confirmada` BOOLEAN

Sem SIAPE, a importação cria identidade provisória determinística por ocorrência de turma e
nome normalizado. Homônimos sem identificador externo não são unidos automaticamente.

### `disciplinas`
`id` UUID PK · `codigo` VARCHAR(20) UNIQUE · `identificador_externo` VARCHAR(50) nullable ·
`nome` VARCHAR(150) · `nome_normalizado` VARCHAR(150) · `departamento` VARCHAR(100) ·
`creditos` SMALLINT nullable

### `turmas`
`id` UUID PK · `fonte` VARCHAR(30) · `unidade_id` FK · `disciplina_id` FK ·
`codigo` VARCHAR(30) · `semestre` VARCHAR(10) · `ativa` BOOLEAN ·
`ultima_observacao_em` TIMESTAMPTZ

Constraint: `UNIQUE(fonte, unidade_id, semestre, disciplina_id, codigo)`.

### `turmas_professores`
`turma_id` FK · `professor_id` FK · PK composta (`turma_id`, `professor_id`). Uma turma
pode ter zero ou vários docentes.

### `avaliacoes`
| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK |
| `usuario_id` | FK → `usuarios` | obrigatório |
| `professor_id` | FK → `professores` | obrigatório |
| `disciplina_id` | FK → `disciplinas` | obrigatório |
| `didatica` | SMALLINT | obrigatório, 1 a 5 |
| `dificuldade` | ENUM Dificuldade | obrigatório |
| `chamada` | BOOLEAN | obrigatório |
| `disponibiliza_material` | BOOLEAN | obrigatório |
| `qualidade_material` | ENUM QualidadeMaterial | obrigatório se `disponibiliza_material` for `true`; **deve ser NULL** se `false` |
| `recomenda` | BOOLEAN | obrigatório |
| `created_at` | TIMESTAMPTZ | default now |
| `updated_at` | TIMESTAMPTZ | atualizado em substituição |

**Constraint obrigatória:** `UNIQUE(usuario_id, professor_id, disciplina_id)`.
Implementar no banco, via migração — não apenas na aplicação.

**Não criar** campo de nota geral, índice composto ou ranking persistido. Na Release 1,
não criar campo de comentário; o detalhamento de RF20 para a R2 não autoriza alterar
o schema sem o processo próprio das issues dependentes.

### `comentario_versoes`
| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK, default `uuid4` |
| `avaliacao_id` | FK → `avaliacoes` | obrigatório |
| `substitui_id` | FK → `comentario_versoes.id` | opcional; aponta para a versão anterior quando este texto substitui outro |
| `texto` | VARCHAR(500) | obrigatório, 1–500 caracteres |
| `estado` | ENUM EstadoComentario | obrigatório, default `PENDENTE` |
| `created_at` | TIMESTAMPTZ | default now |
| `updated_at` | TIMESTAMPTZ | default now, atualizado em cada modificação |

**Constraint:** `CK(texto)` — `length(texto) BETWEEN 1 AND 500`.
Cada avaliação tem **zero ou um** comentário pendente e **zero ou um** publicado;
a criação de uma nova versão pendente remove a pendência anterior.

---

## 4. Regras de agregação

Implementar em `app/domain/`, sem dependência de banco. Entrada: lista de avaliações.
Saída: objeto agregado. Devem ser testáveis unitariamente.

| Critério | Regra | Empate | Saída |
|---|---|---|---|
| `didatica` | Média aritmética | — | float, 1 casa decimal, arredondamento half-up |
| `dificuldade` | Moda | Valor mais alto pela ordinalidade | enum |
| `chamada` | Maioria simples | Empate exato → `CONFLITANTE` | `true` \| `false` \| `"CONFLITANTE"` |
| `disponibiliza_material` | Maioria simples | Empate exato → `CONFLITANTE` | `true` \| `false` \| `"CONFLITANTE"` |
| `qualidade_material` | Moda, **apenas** entre avaliações com `disponibiliza_material = true` | Valor mais alto | enum \| `null` |
| `recomenda` | Percentual de `true` sobre o total | — | inteiro 0–100, arredondamento half-up |

As regras de agregação, empate e arredondamento foram aprovadas pelo PO e estão registradas
na seção 11 dos requisitos, incluindo Material por maioria + moda.

`total_avaliacoes` acompanha sempre o agregado (RF09). Chamada significa controle de
presença. Dificuldade e Chamada têm apresentação neutra. O desempate de Dificuldade
é Difícil > Médio > Fácil; o de qualidade do material é Bom > Médio > Ruim.
Não há nota geral; destaques por quantidade não representam qualidade (restrições de
produto e decisões da seção 11 de `docs/requisitos.md`).

Se `disponibiliza_material` agregar para `false` ou `CONFLITANTE`,
`qualidade_material` retorna `null`.

Agregação é **calculada na consulta**, não materializada. Não criar tabela ou coluna de
resultado agregado sem decisão explícita.

---

## 5. Regras de exibição

```
MIN_AVALIACOES_EXIBICAO = 3
```

**Abaixo do mínimo:** retornar o professor, a disciplina e `total_avaliacoes`, com
`dados_suficientes: false`. **Nenhum valor de critério é retornado** — com uma ou duas
avaliações, a exibição pode permitir inferir respostas individuais (RNF02).

**A partir do mínimo:** retornar todos os critérios agregados, com `dados_suficientes: true`.

**Sem nenhuma avaliação:** o professor continua aparecendo normalmente na busca e na
comparação, com `total_avaliacoes: 0`. Ausência de avaliação nunca é apresentada como
avaliação negativa (RF10).

O mínimo aplica-se somente aos indicadores agregados por professor–disciplina, não
aos comentários, que seguem RF20. A confirmação do e-mail institucional não comprova
matrícula ou experiência (RF01/RF14); opiniões subjetivas, amostras pequenas e mudanças
no tempo limitam a interpretação, sem garantia de veracidade ou representatividade.
A associação interna da conta permanece; ocultação pública e mínimo de três não
garantem anonimato (RF20.3/RNF02).

O valor `3` é decisão de produto sem origem empírica e pode ser revisto pelo time.
Manter como constante configurável, nunca espalhado no código.

---

## 6. Regras de ordenação

Chaves permitidas na comparação entre professores da mesma disciplina:

| Chave | Direção | Observação |
|---|---|---|
| `recomendacao` | decrescente | **única chave permitida** |

**Desempate aprovado:** `total_avaliacoes` decrescente. Se persistir,
nome do professor em ordem alfabética. Total não é chave de ordenação selecionável.

`dificuldade` e `chamada` **não são chaves de ordenação válidas**. Não têm direção boa ou
ruim; ordenar por elas afirmaria uma direção que o projeto decidiu não afirmar.

Professores com `dados_suficientes: false` aparecem depois dos que têm
dados suficientes. Não atribuir percentual artificial aos resultados insuficientes.

---

## 7. Regras de escrita de avaliação

1. Exige usuário autenticado com `email_confirmado = true`.
2. Se já existir avaliação para o par `(usuario_id, professor_id, disciplina_id)`,
   a nova **substitui** a anterior e atualiza `updated_at`. Não criar registro novo,
   não recusar a requisição.
3. Validar `didatica` entre 1 e 5 inclusive.
4. Validar que `qualidade_material` é `null` quando `disponibiliza_material` é `false`.
5. Nenhum campo de texto livre é aceito no Release 1. Se um chegar na requisição, rejeitar.

### Regras de identificação e sessão

1. Consultas públicas não exigem conta nem sessão.
2. O cadastro aceita apenas e-mail com domínio `@aluno.unb.br` e envia um link de
   confirmação para comprovar a posse do endereço.
3. Uma conta com `email_confirmado = false` não pode registrar avaliação. As consultas
   permanecem públicas e não dependem da autenticação dessa conta.
4. A sessão fica armazenada no servidor e é identificada no navegador por valor aleatório
   em cookie `HttpOnly`, `SameSite=Lax` e `Secure` em produção.
5. A sessão expira após sete dias consecutivos de inatividade. Cada atividade autenticada
   válida renova o prazo por mais sete dias.
6. O logout invalida a sessão no servidor e remove o cookie do navegador.
7. Ex-alunos sem acesso ao domínio aceito e outros vínculos institucionais não são
   contemplados pelo cadastro da Release 1.
8. Senhas têm entre 8 e 128 caracteres e são armazenadas com Argon2id.
9. O token de confirmação é opaco, aleatório, de uso único, expira em 24 horas e somente
   seu hash é persistido.
10. Cadastro repetido retorna a mesma resposta genérica `202`, não altera a conta existente
    e não informa se o endereço já está cadastrado.
11. `EMAIL_BACKEND=console` simula envio somente em DEBUG, sem registrar link ou
    destinatário. O transporte Resend exige chave e remetente externos; sua configuração
    operacional permanece pendente de validação. Ensaios usam transporte sintético privado.
12. O cookie de sessão chama-se `undb_session`. O servidor persiste somente o hash do token
    aleatório e renova tanto `expires_at` quanto o `Max-Age` do cookie quando uma rota passa
    pela dependência de autenticação. Rotas públicas não renovam sessão.
13. Login não exige e-mail já confirmado; a dependência de escrita de avaliação exige
    autenticação e `email_confirmado = true`.
14. Recuperação de senha (RF24, aprovada em 15/11/2026): solicitar link pelo e-mail
    cadastrado com resposta genérica `202`. Token separado da confirmação, aleatório,
    com hash SHA-256 persistido, uso único e validade de uma hora. A troca mantém a
    confirmação de e-mail, usa Argon2id e senha de 8–128 caracteres, invalida todos os
    links de recuperação e sessões da conta e não autentica automaticamente.
    Falha de envio não altera senha nem invalida links anteriores.



---

## 8. Contrato de API

Prefixo `/api`. Schemas Pydantic para toda entrada e saída — nunca retornar instância de
modelo SQLAlchemy diretamente.

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/auth/cadastro` | não | Cria usuário, dispara e-mail de confirmação |
| `POST` | `/auth/confirmar` | não | Confirma e-mail a partir do token no corpo |
| `POST` | `/auth/recuperar-senha` | não | Solicita link temporário; corpo `email`, resposta genérica `202` |
| `POST` | `/auth/redefinir-senha` | não | Recebe `token` e `senha`; troca senha e invalida sessões; token inválido/expirado retorna `400` |
| `POST` | `/auth/login` | não | Autentica |
| `GET` | `/auth/sessao` | opcional | Informa se o navegador possui sessão válida e renova sua validade |
| `POST` | `/auth/logout` | sim | Invalida a sessão atual e remove seu cookie |
| `GET` | `/professores?nome=` | não | Descobre professores por nome parcial |
| `GET` | `/professores/{id}` | não | Consulta um professor |
| `GET` | `/professores/{id}/disciplinas` | não | Lista disciplinas vinculadas |
| `GET` | `/disciplinas?codigo=&nome=` | não | Descobre disciplinas por código/nome |
| `GET` | `/disciplinas/{id}` | não | Consulta uma disciplina |
| `GET` | `/disciplinas/{id}/turmas` | não | Lista turmas e docentes |
| `GET` | `/professores/{id}/disciplinas/{disciplina_id}` | não | Agregado de um professor numa disciplina |
| `GET` | `/disciplinas/{id}/professores?ordenar_por=` | não | Comparação, ordenada |
| `POST` | `/avaliacoes` | sim | Cria ou substitui avaliação |

Nenhuma busca filtra por curso ou departamento do usuário (RF07).
Nenhum endpoint dispara importação do SIGAA em tempo real.

Para o retorno à avaliação da #158, `POST /auth/cadastro` aceita o campo opcional
`return_to`: `/professores/{UUID}/disciplinas/{UUID}/avaliar`, sem origem ou
fragmento, com até 2.048 caracteres. Conforme autorização da #155 registrada nos
requisitos, pode conter a query completa `busca=professores|disciplinas`, `q=<termo>`
e `ordem=nome|unidade`. As três chaves devem aparecer exatamente uma vez; chaves
extras, controles e escapes percentuais inválidos são rejeitados. A rota sem query
continua aceita. O backend inclui esse destino em `returnTo` no link de
confirmação enviado por e-mail. O frontend valida o destino novamente e o mantém
nos links de login/cadastro. Cada link carrega seu próprio contexto, inclusive
entre abas; não há armazenamento global do destino no navegador nem persistência
de respostas do formulário. O destino não autentica, não confirma a conta e não
dispensa as verificações de sessão, e-mail e vínculo professor/disciplina da API.
Cadastros sem esse campo e links antigos de confirmação continuam válidos.

O `GET /professores/{id}/disciplinas/{disciplina_id}` retorna, além dos UUIDs e da
contagem/agregação, os dados institucionais persistidos necessários à apresentação:

```json
{
  "professor": {"id": "uuid", "nome": "...", "departamento": "..."},
  "disciplina": {
    "id": "uuid",
    "codigo": "CIC0002",
    "nome": "...",
    "departamento": "CIC"
  }
}
```

As consultas são parciais, case-insensitive e accent-insensitive. Busca válida sem resultado
retorna `[]`; recurso individual inexistente retorna 404; homônimos permanecem em itens
separados. A #25 entrega esse contrato institucional mínimo; #44/#45 implementam a
experiência de busca no frontend.

---

## 9. Estrutura do backend

```
backend/app/
├── routers/       # endpoints; sem lógica de negócio
├── schemas/       # Pydantic
├── services/      # casos de uso
├── domain/        # regras de agregação; sem dependência de banco
├── repositories/  # consultas SQLAlchemy
├── models/        # entidades
├── scrapers/      # importação SIGAA
└── core/          # config, segurança, sessão
```

Entidades de domínio em português, estrutura técnica em inglês.
Lógica de negócio nunca dentro da função do router.

---

## 10. Decisões em aberto

Não implementar nem inventar valor para os itens abaixo.

| Item | Situação |
|---|---|
| Lista de termos do filtro de comentários | Solicitante definirá depois; moderação humana até então |
| IA sem aprovação humana prévia | Autorizada pelo PO em 14/11/2026 na #239; triagem habilitada publica sem sinais e mantém demais casos pendentes |

**Itens já resolvidos — fontes:** a seção 11 de `docs/requisitos.md` aprova a
importação inicial manual na R1; sua operação/cobertura na R2 é verificada na
[#164](https://github.com/unb-mds/2026-02-UnDb/issues/164), ainda aberta.
Os dados e contratos RF20–RF22 foram entregues pelas PRs
[#191](https://github.com/unb-mds/2026-02-UnDb/pull/191) e
[#192](https://github.com/unb-mds/2026-02-UnDb/pull/192), ambas integradas em `develop`.
Não são mais decisões técnicas pendentes; ver seção 12, sem alterar os contratos.

---

## 11. Restrições permanentes

- Não criar nota geral do professor nem índice composto ponderando critérios.
- Não exibir dificuldade e chamada com codificação de valor (cor de alerta, ranking, ícone
  de positivo/negativo). São informativos.
- Não exibir valor de critério abaixo de `MIN_AVALIACOES_EXIBICAO`.
- Não armazenar dado acadêmico identificável do avaliador.
- Não introduzir campo de texto livre antes do Release 2.
- Não alterar schema fora de migração Alembic.

---

## 12. Comentários, denúncia e moderação — Release 2

**Fonte:** detalhamento de RF20–RF22 e decisões R2-DEC-01 a R2-DEC-15 em
[`docs/requisitos.md`](docs/requisitos.md), definidos nas respostas humanas da #154.
Este resumo não substitui as tabelas de estados, retenção, erros e critérios AC20/21/22
da fonte. Os contratos da R1 são preservados; as referências abaixo registram a
evolução R2 já integrada.

**Estado de entrega — fonte: PRs integradas e issues encerradas, consultadas em 09/11/2026.**
As APIs #156/#160/#161 foram integradas pelas PRs #191/#192. As interfaces
#159/#162/#193 foram integradas pelas PRs #197/#194/#196. A verificação técnica
#163 foi concluída pela PR #198; o reteste qualitativo #166 continua pendente.
Consulte [evidências e limites por release](docs/releases/2.0.0-reconciliacao.md).

### Escrita, consulta e substituição de comentário

- Comentário opcional da avaliação única estudante/professor/disciplina. Escrita e retirada
  pertencem ao autor autenticado com e-mail confirmado; ausência de novo texto no reenvio
  mantém o existente. Texto informado: 1–500 caracteres, desconsiderando espaços nas extremidades.
- Leitura pública do texto publicado, sem nome/e-mail/identificador do autor ou vínculo
  público com a conta. A consulta não expõe os cinco critérios individuais; RNF02 continua
  protegendo os critérios agregados abaixo de três avaliações.
- Novos textos e substitutos passam pela triagem #239 quando habilitada: publicação
  sem sinais locais/IA e pendência humana nos demais casos. Sem habilitação, aprovação
  humana prévia. Revisar a lista antes de ativar o filtro. Crítica acadêmica negativa
  não é motivo de rejeição.
- Critérios válidos são registrados normalmente; moderação do texto não os modifica.
  Versão anterior aprovada permanece enquanto o substituto é analisado, se não suspensa
  ou removida. Rejeitar o substituto mantém o estado anterior e descarta o texto rejeitado.
- Aprovar substituto descarta texto anterior e encerra suas denúncias como `versão substituída`,
  sem transferência. Retirada explícita cancela substituto pendente e encerra denúncias
  como `conteúdo retirado`, sem julgar procedência e sem remover as notas.

### Denúncias e suspensão

- Apenas texto é denunciável. Conta autenticada confirmada ou não e visitante sem login
  podem denunciar. Motivos fechados obrigatórios: ofensa pessoal, xingamento, palavrão,
  ameaça, discriminação, exposição de dados pessoais ou spam; sem justificativa livre.
- No máximo uma denúncia aberta por conta/versão para autenticados. Visitantes podem
  repetir; a fila agrupa por comentário/versão e separa as origens e suas contagens.
  Denúncia autenticada não implica automaticamente procedência.
- **50 contas autenticadas distintas com denúncia aberta da mesma versão publicada**
  suspendem o texto e o encaminham à revisão humana. Contas não confirmadas contam;
  anônimas, duplicadas e encerradas não contam. Suspensão não é remoção definitiva.
- Denunciantes recebem confirmação, sem acompanhamento posterior em tempo real. Na
  suspensão pelo limiar ou remoção humana de denunciado, autenticados relacionados recebem
  agradecimento na aplicação, disponível até primeira exibição e apagado depois.

### Permissão, ações e dados privados

- PO concede/retira papel a membros da equipe com conta autenticada e confirmada. Não
  permitir decisão sem permissão ou sobre comentário/denúncia próprios; sem outro moderador
  elegível o caso permanece pendente. Denúncia anônima não oferece vínculo de conta para
  garantir detecção automática de todo impedimento pessoal.
- Ações: aprovar/rejeitar pendente, manter/remover denunciado, restaurar/remover suspenso.
  Não restaurar texto retirado pelo autor ou descartado. Não modificar os cinco critérios.
- Denúncias e decisões têm registros privados: versão, data/hora, ator interno quando
  existir, transição e motivo; decisões exigem motivo. Moderador autorizado pode consultar
  nome/e-mail dos usuários envolvidos. Autor acompanha estado próprio, não os registros
  privados de denunciantes ou de outros comentários.
- Rejeitados e substituídos: não conservar o texto. Retirados pelo autor ou removidos pelo
  moderador: texto privado por sete dias após o evento. Denúncias encerradas: não conservar.
  Decisões: registros privados por sete dias após decisão. Não copiar texto descartado nos
  registros. Suspensos permanecem disponíveis internamente para revisão.

### Contratos definidos em #156 (RF20)

> Recorte histórico da entrega RF20 pela PR #191. RF21/RF22 foram entregues
> posteriormente pela PR #192; seus contratos compartilhados estão referenciados
> ao final desta seção. Não usar a descrição da migration inicial como retrato
> completo do schema após as migrations de moderação.

#### Migration

- `20261024_01_create_comentario_versoes.py` — cria a tabela `comentario_versoes`
  com colunas, constraint de tamanho (`CK length(texto) BETWEEN 1 AND 500`),
  FK para `avaliacoes` e auto-referência `substitui_id`, e o ENUM
  `estado_comentario` (`PENDENTE`, `PUBLICADO`, `SUSPENSO`, `REMOVIDO`,
  `RETIRADO`, `SUBSTITUIDO`). Reversível (drop table + drop type).

#### Escrita de comentário (via avaliação)

| Endpoint | Método | Auth | Request body | Sucesso | Erros |
|---|---|---|---|---|---|
| `/api/avaliacoes` | POST | confirmado | `AvaliacaoCreate` + `comentario?: str` | 200 | 401 (sem sessão), 403 (e-mail não confirmado), 404 (professor/disciplina/vínculo) |

- Texto de **1–500** caracteres (após strip) → cria versão `PENDENTE`.
- Texto vazio, só-espaços ou >500 → comentário omitido; avaliação persiste normalmente
  e a resposta 200 informa o motivo em `comentario_erro`. Esse campo é `null` para
  texto válido ou comentário ausente; comentário inválido não altera texto existente.
- Reenvio com novo texto: remove `PENDENTE` anterior, cria nova apontando ao
  texto vigente `PUBLICADO`, `SUSPENSO` ou `REMOVIDO` (se houver) via `substitui_id`.
  A publicação do substituto exige nova aprovação; envio nunca restaura o anterior.
- Reenvio sem texto: mantém comentário existente.

#### Leitura pública (visitante)

| Endpoint | Método | Auth | Sucesso | Erros |
|---|---|---|---|---|
| `/api/professores/{professor_id}/disciplinas/{disciplina_id}/comentarios` | GET | nenhuma | 200 → `list[ComentarioPublicoResponse]` | 404 (professor ou disciplina inexistente, ou sem vínculo) |

Retorna apenas `id`, `texto`, `created_at` — sem identidade do autor.

#### Acompanhamento pelo autor

| Endpoint | Método | Auth | Sucesso | Erros |
|---|---|---|---|---|
| `/api/comentarios/meu` | GET | confirmado | 200 → `list[ComentarioDoAutorResponse]` | 401 (sem sessão), 403 (e-mail não confirmado) |

Retorna `id`, `texto`, `created_at`, `updated_at`, `estado`, `avaliacao_id`,
`substitui_id` — apenas comentários da avaliação cujo autor é o usuário autenticado.
Para a interface da #159, a consulta aceita filtros opcionais UUID `professor_id`
e `disciplina_id`. Ambos restringem apenas as avaliações do usuário autenticado;
a omissão preserva a listagem completa anterior. UUID inválido retorna 422.
A identidade do autor continua derivada exclusivamente da sessão, sem parâmetro de conta.

Após descarte aprovado, `texto` pode ser `null`; `REJEITADO` integra os estados.
Isso não altera o schema público, que continua retornando somente textos publicados.

#### Retirada pelo autor

| Endpoint | Método | Auth | Sucesso | Erros |
|---|---|---|---|---|
| `/api/comentarios/{comentario_id}/retirar` | PATCH | confirmado | 200 → `ComentarioDoAutorResponse` | 401 (sem sessão), 403 (e-mail não confirmado, alheio ou estado bloqueado), 404 (comentário inexistente) |

- Só pode retirar `PENDENTE`, `PUBLICADO` ou `SUSPENSO`.
- Cancela evento `PENDENTE` que substitui este comentário (deleta-o).
- Preserva os cinco critérios estruturados da avaliação.
- Encerra e descarta denúncias abertas da avaliação como `conteúdo retirado`, sem
  agradecimento. Selecionar um substituto pendente também retira o texto vigente.
- Texto retirado é interno por sete dias, com descarte automático.

#### Contratos compartilhados de denúncias e moderação (#160/#161)

Contrato, rotas, schemas, transições, permissões, retenção, operação e evidências
em [Contrato compartilhado das #160/#161](docs/estudos/alinhamento-denuncias-issues-160-161.md#resolucao-pelo-po-e-contrato-de-implementacao).
Essa referência complementa RF20; a fonte de produto permanece `docs/requisitos.md`.

Migrations posteriores à #156: `20261101_01` (papel, decisões e descarte de texto),
`20261101_02` (denúncias abertas e agradecimentos), `20261101_03` (retenção de
retiradas legadas). Somente versões `PUBLICADO` aceitam denúncias. Denúncias
encerradas são apagadas na transação da decisão/retirada/substituição.


## Extensão de identidades docentes — RF23 / #207

Derivado de `docs/requisitos.md`, evolução autorizada em 11/11/2026.
UUID interno preservado; `identidades_docentes.identificador` representa a chave
externa do perfil SIGAA/UnB, sem inventar SIAPE ou promover `identidade_confirmada`.
A chave provisória continua preservada por ocorrência em `pendencias_identidade`.

| Endpoint | Método | Auth | Resultado |
|---|---|---|---|
| `/api/moderacao/identidades?estado=PENDENTE&offset=0` | GET | confirmado + reconciliador | Até 50 ocorrências ordenadas por criação/ID; estados PENDENTE, CONFIRMADA, SEPARADA, APLICADA |
| `/api/moderacao/identidades/{id}/previa?identificador=...` | GET | confirmado + reconciliador | Necessidade de união e contagens de turmas/avaliações/colisões, sem expor valores individuais |
| `/api/moderacao/identidades/{id}/decisoes` | GET | confirmado + reconciliador | Histórico de ação, responsável, justificativa, perfil, versão e data |
| `/api/moderacao/identidades/{id}/decisoes` | POST | confirmado + reconciliador | Ação CONFIRMAR ou SEPARAR, versão atual, justificativa de 1–500 caracteres; CONFIRMAR exige candidato apresentado |

Todas as leituras privadas são `no-store`. Erros: 401 sem sessão, 403 sem
confirmação/papel específico, 404 pendência inexistente, 409 versão/estado obsoleto
ou conflito, 422 entrada inválida. Identidade do decisor vem da sessão.
Não há endpoint público de concessão do papel nem de migração de avaliações.

CONFIRMADA significa aguardando aplicação: o importador pode registrar a identidade
quando isso não exige união de UUIDs; a rotina administrativa aplica as uniões em
janela sem escritores. APROVAÇÃO não significa operação de dados concluída.
SEPARADA preserva a ocorrência e não generaliza essa decisão para nomes iguais
em outros semestres. Casos seguros futuros são rechecados automaticamente.

### Evolução híbrida de RF23 — 13/11/2026

Derivado da evolução de RF23 em `docs/requisitos.md`, aprovada pelo PO em 13/11/2026.
O importador prioriza perfil institucional verificável. Busca concluída sem
perfil encontrado ou histórico sem confirmação da disciplina permite fallback por nome completo normalizado + unidade da oferta,
reutilizado entre turmas e semestres, com risco residual aceito de homônimos sem perfil.

`identidades_locais` tem PK composta `(nome_normalizado, unidade)` e FK `professor_id`.
`ASSOCIACAO_LOCAL` distingue a associação provisória aplicada; não inventa SIAPE nem
marca confirmação institucional. Perfil descoberto depois pode promover o mesmo UUID;
uniões entre UUIDs diferentes permanecem administrativas. Perfil manualmente indicado
é consultado novamente e exige nome e componente/semestre compatíveis.

Múltiplos perfis e falha de consulta exigem revisão inicial explícita para associação
local. O conjunto de candidatos revisado é preservado; um novo conjunto fica pendente.
Indisponibilidade pode reutilizar associação local existente. Conflitos institucionais
permanecem pendentes. Decisão humana de separação bloqueia fallback do mesmo nome/unidade
em novas turmas/semestres. Unidades diferentes continuam separadas sem evidência adicional.
A consolidação tem atomicidade e commit por grupo, progresso salvo e retomada dos grupos
restantes; RF03, RNF02 e a janela sem escritores continuam obrigatórios.


## Apoio assistivo à moderação — #239

Implementação autorizada pelo PO em 14/11/2026 com OpenAI, desativada por padrão.
O endpoint privado `POST /api/moderacao/comentarios/{versao_id}/triagem` recebe
apenas a versão e retorna categorias e sinalização; não decide nem altera avaliações.
Contrato, flags, limites, privacidade e validação em [docs/moderacao-ia.md](docs/moderacao-ia.md).


### Evolução autorizada — triagem automática #239 (14/11/2026)

Fonte: docs/requisitos.md, RF20 e seção “Evolução da moderação”. O envio confirma
critérios/texto pendente antes da consulta externa. Sem sinais locais/IA, publicar e
auditar como sistema; demais casos ficam pendentes. Resposta de avaliação acrescenta
comentario_estado: PUBLICADO/PENDENTE/null. DecisaoResponse.moderador_id é nulo
somente para decisão do sistema. Nenhuma restauração ou rejeição automática.
A flag MODERACAO_AUTOMATICA_ATIVA é False por padrão. Guia: docs/moderacao-ia.md.

### Detecção complementar de disfarces — etapa inicial #252 (15/11/2026)

Fonte: docs/requisitos.md, “Evolução de RF20 — etapa inicial da #252”. Escopo e critérios
aprovados pelo solicitante após a delegação de decisão esclarecida nesta sessão.

`MODERACAO_DISFARCES_ATIVO=False` controla somente o complemento. O filtro vigente
continua independente e seus sinais/categorias são unidos aos novos. U+FE0F e U+034F
devem continuar detectados. Em `filtro_moderacao.py`, NFKD/casefold/remoção de marcas
com classe combinante não zero são aplicados a uma cópia, sem compactar espaços.
Remover explicitamente U+200B/U+200C/U+200D/U+FEFF/U+2060 e mapear somente
`а→a`, `е→e`, `о→o`, `і→i`, `с→c` (caracteres de origem cirílicos).

Padrões são pré-compilados da lista existente, com fronteiras Unicode de palavra;
até três espaços/pontos/hífens/sublinhados/asteriscos entre letras e até quatro
repetições contíguas por posição. Entre palavras da expressão, exigir um a três
separadores. Limites novos não retiram detecções já cobertas pelo filtro anterior.
Não substituir números. Não mudar o texto armazenado ou o texto enviado à IA.

O fluxo automático e o apoio privado usam a união; falhas mantêm revisão e no apoio
retornam `INDISPONIVEL`, sem expor o erro bruto. Publicação automática registra a versão
`252-disfarces-v1` (ou `239-lexical-v1` com complemento desligado) no motivo privado
da auditoria existente. Não há alteração de schema/contrato ou retenção.
Desligar somente a flag nova restaura o filtro anterior. Homologação dos rótulos e
ativação em produção permanecem pendentes; não há autorização de deploy/ativação.

### Ampliação numérica da #252

Fonte: docs/requisitos.md, “Ampliação de RF20 — substituições numéricas da #252”.
`MODERACAO_SUBSTITUICOES_ATIVAS=False`, dependente de `MODERACAO_DISFARCES_ATIVO`,
adiciona padrões pré-compilados por posição: `a4`, `e3`, `i1`, `o0`, `s5`, `t7`.
Não aplica substituições globais, substring ou similaridade. Mantém fronteiras e limites
da primeira etapa e soma todas as categorias anteriores. Versão efetiva, com ambas as flags:
`252-disfarces-leet-v2`; desligar só números retorna a `252-disfarces-v1`.
Texto original e payload externo são preservados. `m4rda` não recebe exceção `4→e`.
Identificadores isolados iguais a um termo disfarçado também podem gerar sinal; não criar
exceção automática por contexto técnico, nem tratar sinal como decisão de rejeição.
Homologação/ativação em produção permanecem pendentes.

### Persistência da recuperação de senha — RF24

`password_reset_tokens`: `id` UUID PK, `usuario_id` UUID FK obrigatória para
`usuarios.id`, `token_hash` VARCHAR(64) obrigatório e único, `expires_at` TIMESTAMPTZ
obrigatório, `used_at` TIMESTAMPTZ opcional e `created_at` TIMESTAMPTZ obrigatório.
Índice em `usuario_id` para invalidar os links da conta. Não armazena token aberto,
senha ou cópia do e-mail; mantém o padrão de tokens de confirmação sem permitir
uso cruzado entre as duas finalidades.

## Transparência e ciência dos Termos — RF26 / #269

Derivado de `docs/requisitos.md`, RF26, autorizado pelo PO em 16–17/11/2026.

- `POST /api/auth/cadastro` exige `ciencia_termos: true` (booleano estrito) e
  `termos_versao: "2026-11-17"`. Ausência/falso/tipo indevido/versão diferente retorna
  422 antes dos efeitos. Não aceita data enviada pelo cliente. Resposta neutra 202 preservada.
- `usuarios.termos_versao VARCHAR(32) NULL` e `termos_ciencia_em TIMESTAMPTZ NULL`:
  par ausente nas contas antigas ou completo nas novas, garantido por CHECK. Sem default
  ou backfill; serviço registra instante UTC na mesma transação da criação. Não são
  adicionados a respostas públicas. Nenhum índice novo: não há consulta por esses campos.
- Páginas públicas `/privacidade` e `/termos-de-uso` com versão/data e links no rodapé,
  cadastro e Sobre; ciência inicialmente desmarcada, sem novo bloqueio de contas antigas.
- Natureza acadêmica estudantil independente e sem fins lucrativos; sem endosso oficial
  comprovado. Inventário factual e limites em `docs/transparencia.md`.


### Votos de utilidade — #278

Fonte: `docs/requisitos.md`, RF20 — Utilidade do comentário (R2, 16/11/2026).

- `GET /api/comentarios/{id}/utilidade`: sessão opcional; 200 com
  `{uteis: integer >= 0, nao_uteis: integer >= 0, meu_voto: "UTIL" | "NAO_UTIL" | null}`.
  O voto é sempre da sessão atual, nunca de um identificador recebido. Sem sessão, null.
- `POST /api/comentarios/{id}/voto`: sessão confirmada; corpo exclusivo
  `{voto: "UTIL" | "NAO_UTIL" | null}`. null retira. Retorna o mesmo resumo (200).
  Repetir/trocar/retirar é idempotente. 401 sem sessão; 403 e-mail não confirmado ou
  voto no próprio comentário; 404 alvo inexistente/não publicado/sem texto, com mensagem
  única; 422 corpo/UUID inválido. Respostas no-store/no-referrer, inclusive erros.
- Tabela `votos_comentario`: PK composta `(comentario_versao_id, usuario_id)`, FKs com
  ON DELETE CASCADE para versão/conta e CHECK de voto. Sem timestamp ou auditoria nova.
  Escrita usa lock da avaliação/versão existente e upsert; não atualiza a versão.
- Contagens são calculadas no banco somente para a versão publicada solicitada;
  ordenação da lista pública e seu contrato atual são preservados. Nenhuma identidade
  de votante integra respostas. Aplicar o ciclo de descarte da versão, sem retenção nova.
