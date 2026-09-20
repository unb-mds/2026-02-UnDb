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
```

Ordinalidade aprovada para desempate de moda:
`DIFICIL > MEDIO > FACIL` e `BOM > MEDIO > RUIM`.

---

## 3. Modelo de dados

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

**Não criar** campo de nota geral, índice composto, ranking persistido ou campo de comentário.

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
8. Senhas têm entre 15 e 128 caracteres e são armazenadas com Argon2id.
9. O token de confirmação é opaco, aleatório, de uso único, expira em 24 horas e somente
   seu hash é persistido.
10. Cadastro repetido retorna a mesma resposta genérica `202`, não altera a conta existente
    e não informa se o endereço já está cadastrado.
11. Na Release 1, `EMAIL_BACKEND=console` escreve o link no terminal e é o único modo
    previsto. A ativação de `EMAIL_BACKEND=resend`, com chave e remetente configurados
    externamente, fica planejada para a Release 2.

---

## 8. Contrato de API

Prefixo `/api`. Schemas Pydantic para toda entrada e saída — nunca retornar instância de
modelo SQLAlchemy diretamente.

| Método | Rota | Auth | Descrição |
|---|---|---|---|
| `POST` | `/auth/cadastro` | não | Cria usuário, dispara e-mail de confirmação |
| `POST` | `/auth/confirmar` | não | Confirma e-mail a partir do token no corpo |
| `POST` | `/auth/login` | não | Autentica |
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

---

## 11. Restrições permanentes

- Não criar nota geral do professor nem índice composto ponderando critérios.
- Não exibir dificuldade e chamada com codificação de valor (cor de alerta, ranking, ícone
  de positivo/negativo). São informativos.
- Não exibir valor de critério abaixo de `MIN_AVALIACOES_EXIBICAO`.
- Não armazenar dado acadêmico identificável do avaliador.
- Não introduzir campo de texto livre antes do Release 2.
- Não alterar schema fora de migração Alembic.
