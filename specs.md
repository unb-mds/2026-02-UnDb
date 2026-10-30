# specs.md — Especificação de implementação

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

---

## 3. Modelo de dados

Esta seção descreve o modelo da Release 1 e da Release 2 (RF20). As regras de RF21 e
RF22 (denúncia e moderação) ainda dependem das issues #160/#161; seus modelos
físicos e contratos não estão definidos aqui.

### `usuarios`
| Campo | Tipo | Regra |
|---|---|---|
| `id` | UUID | PK |
| `nome` | VARCHAR(100) | obrigatório |
| `email` | VARCHAR(150) | UNIQUE, obrigatório, domínio `@aluno.unb.br` |
| `password_hash` | VARCHAR(255) | hash forte |
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

`total_avaliacoes` acompanha sempre o agregado (RF09).

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
11. Na Release 1, `EMAIL_BACKEND=console` escreve o link no terminal e é o único modo
    previsto. A ativação de `EMAIL_BACKEND=resend`, com chave e remetente configurados
    externamente, fica planejada para a Release 2.
12. O cookie de sessão chama-se `undb_session`. O servidor persiste somente o hash do token
    aleatório e renova tanto `expires_at` quanto o `Max-Age` do cookie quando uma rota passa
    pela dependência de autenticação. Rotas públicas não renovam sessão.
13. Login não exige e-mail já confirmado; a dependência de escrita de avaliação exige
    autenticação e `email_confirmado = true`.

---

## 8. Contrato de API

Prefixo `/api`. Schemas Pydantic para toda entrada e saída — nunca retornar instância de
modelo SQLAlchemy diretamente.

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/auth/cadastro` | não | Cria usuário, dispara e-mail de confirmação |
| `POST` | `/auth/confirmar` | não | Confirma e-mail a partir do token no corpo |
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
| Estratégia de povoamento inicial da base | Não decidido |
| Lista de termos do filtro de comentários | Solicitante definirá depois; moderação humana até então |
| IA sem aprovação humana prévia | Objetivo futuro condicionado, sem mecanismo/provedor aprovado; não substituir moderação humana nesta etapa |
| Dados e contratos de RF20–RF22 | RF20 implementado em #156: migration `comentario_versoes`, endpoints de
  leitura pública, acompanhamento do autor e retirada. RF21/RF22 ainda dependem
  de #160/#161 — modelos e contratos de denúncia e moderação não definidos. |

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
da fonte. O restante deste documento mantém os contratos entregues na R1.

### Escrita, consulta e substituição de comentário

- Comentário opcional da avaliação única estudante/professor/disciplina. Escrita e retirada
  pertencem ao autor autenticado com e-mail confirmado; ausência de novo texto no reenvio
  mantém o existente. Texto informado: 1–500 caracteres, desconsiderando espaços nas extremidades.
- Leitura pública do texto publicado, sem nome/e-mail/identificador do autor ou vínculo
  público com a conta. A consulta não expõe os cinco critérios individuais; RNF02 continua
  protegendo os critérios agregados abaixo de três avaliações.
- Novos textos e substitutos exigem moderação vigente. Nesta etapa, aprovação humana
  antes de publicar; não ativar filtro enquanto a lista não estiver definida. IA é evolução
  condicionada, não mecanismo atual. Crítica acadêmica negativa não é motivo de rejeição.
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

> Implementação limitada à RF20. RF21 (denúncia) e RF22 (moderação) permanecem
> em #160/#161; seus contratos não são definidos aqui.

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
  `PUBLICADO` atual (se houver) via `substitui_id`.
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

#### Retirada pelo autor

| Endpoint | Método | Auth | Sucesso | Erros |
|---|---|---|---|---|
| `/api/comentarios/{comentario_id}/retirar` | PATCH | confirmado | 200 → `ComentarioDoAutorResponse` | 401 (sem sessão), 403 (e-mail não confirmado, alheio ou estado bloqueado), 404 (comentário inexistente) |

- Só pode retirar `PENDENTE`, `PUBLICADO` ou `SUSPENSO`.
- Cancela evento `PENDENTE` que substitui este comentário (deleta-o).
- Preserva os cinco critérios estruturados da avaliação.

#### Contratos ainda não definidos (restam para #160/#161)

As APIs de **denúncia** (#160, RF21) e **moderação** (#161, RF22) devem ainda
preservar os cenários AC21-01 a AC22-06, incluindo falta de sessão/confirmação,
alvo inexistente/obsoleto, motivo inválido, duplicidade, acesso alheio, impedimento
e transição incompatível.
