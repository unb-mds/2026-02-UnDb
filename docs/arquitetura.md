# 🏛️ Arquitetura e Decisões Técnicas — G7

Sistema de avaliação de professores e disciplinas da UnB.
Requisitos em [`requisitos.md`](requisitos.md).

> **Estado:** cada ADR informa seu próprio estado. O ADR 03 foi validado pelo grupo para a
> Release 1; os demais permanecem como **proposta do PO** até validação específica do time.

---

## 1. Visão geral

```mermaid
flowchart LR
    subgraph Fonte["Fonte pública"]
        SIGAA[SIGAA - páginas públicas]
    end

    subgraph Coleta["Importação"]
        SCRAPER[Scraper por departamento]
    end

    subgraph Persistencia["Persistência"]
        DB[(PostgreSQL)]
    end

    subgraph Backend["Backend"]
        API[FastAPI]
        AGG[Camada de agregação]
        AUTH[Autenticação e confirmação de e-mail]
    end

    subgraph Consumo["Consumo"]
        WEB[Frontend Next.js]
    end

    SIGAA --> SCRAPER
    SCRAPER --> DB
    DB --> AGG
    AGG --> API
    AUTH --> API
    API --> WEB
```

O scraper **grava** no banco; a API apenas **lê**. Nenhum endpoint dispara importação em
tempo real, para que a resposta ao usuário não dependa da disponibilidade do SIGAA.

---

## 2. Arquitetura em camadas do backend

```
backend/app/
├── routers/         # endpoints FastAPI
├── schemas/         # Pydantic — validação de entrada e saída
├── services/        # casos de uso e orquestração
├── domain/          # regras de agregação (fato x opinião), puras e testáveis sem banco
├── repositories/    # consultas e persistência via SQLAlchemy
├── models/          # entidades relacionais
├── scrapers/        # importação do SIGAA
└── core/            # configuração, segurança, sessão de banco
```

A separação atende ao **RNF06**. A camada `domain/` existe para que as regras de agregação
sejam testáveis sem banco ativo — são a lógica mais sujeita a erro do sistema.

Entidades de domínio em português (`Avaliacao`, `Professor`, `Disciplina`), estrutura técnica
em inglês, conforme convenção já definida no `CLAUDE.md`.

---

## 3. Diagrama Entidade-Relacionamento

```mermaid
erDiagram
    USUARIOS ||--o{ AVALIACOES : "registra"
    PROFESSORES ||--o{ TURMAS : "leciona"
    DISCIPLINAS ||--o{ TURMAS : "e ofertada em"
    PROFESSORES ||--o{ AVALIACOES : "recebe"
    DISCIPLINAS ||--o{ AVALIACOES : "contextualiza"
```

A avaliação referencia **professor e disciplina juntos**, não a turma. O aluno avalia como
aquele professor ensina aquela matéria; se ele leciona a mesma disciplina em vários
semestres, as avaliações se acumulam no mesmo par.

`TURMAS` existe para saber **quais professores oferecem quais disciplinas** — é o que
alimenta a comparação (RF12).

---

## 4. Modelo relacional

### `usuarios`
| Campo | Tipo | Observação |
|---|---|---|
| `id` | UUID, PK | |
| `nome` | VARCHAR(100) | |
| `email` | VARCHAR(150), UNIQUE | Domínio institucional da UnB |
| `password_hash` | VARCHAR(255) | Hash forte (RNF03) |
| `email_confirmado` | BOOLEAN | Avaliação só é aceita se verdadeiro |
| `created_at` | TIMESTAMPTZ | |

Não são armazenados matrícula, CPF ou histórico acadêmico (RF01, RNF01).

### `professores`
`id` (UUID, PK), `nome`, `departamento`.

### `disciplinas`
`id` (UUID, PK), `codigo` (UNIQUE), `nome`, `departamento`, `creditos`.

`departamento` é o que permite a busca entre departamentos do RF07 — e é por isso que a
importação precisa cobrir todos eles (RF17).

### `turmas`
`id` (UUID, PK), `disciplina_id` (FK), `professor_id` (FK), `semestre`.

### `avaliacoes`
| Campo | Tipo | Natureza |
|---|---|---|
| `id` | UUID, PK | |
| `usuario_id` | FK → usuarios | |
| `professor_id` | FK → professores | |
| `disciplina_id` | FK → disciplinas | |
| `didatica` | SMALLINT (1–5) | Opinião |
| `dificuldade` | ENUM (`FACIL`, `MEDIO`, `DIFICIL`) | Opinião |
| `chamada` | BOOLEAN | Fato |
| `disponibiliza_material` | BOOLEAN | Fato |
| `qualidade_material` | ENUM (`RUIM`, `MEDIO`, `BOM`) (NULL se `disponibiliza_material=false`) | Fato + opinião |
| `recomenda` | BOOLEAN | Opinião |
| `created_at` | TIMESTAMPTZ | |
| `updated_at` | TIMESTAMPTZ | Atualizado em substituição |

**Constraint:** `UNIQUE(usuario_id, professor_id, disciplina_id)` — implementa o RF03 no
banco, e não apenas na aplicação.

---

## 5. Fluxo de importação

```mermaid
sequenceDiagram
    participant Job as Rotina de atualizacao
    participant Scraper
    participant SIGAA as SIGAA publico
    participant DB as PostgreSQL

    Job->>Scraper: dispara importacao por departamento
    Scraper->>SIGAA: requisicao com throttling
    SIGAA-->>Scraper: paginas de turmas
    Scraper->>Scraper: parse e validacao Pydantic
    Scraper->>DB: grava professores, disciplinas e turmas
    Scraper->>Job: registra sucesso ou falha (RF19)
```

Falha em um departamento não interrompe os demais (RNF07).

---

## 6. Estrutura de pastas

```
G7-2026-2/
├── backend/
│   ├── app/           # ver seção 2
│   ├── alembic/       # migrações
│   └── tests/
├── frontend/          # Next.js
├── docs/              # requisitos.md, arquitetura.md
├── skills/            # skills canônicas do projeto
├── docker-compose.yml
└── README.md
```

A separação `backend/` e `frontend/` no topo atende à exigência de separação entre front e
back que motivou a saída do Django.

---

## 7. Decisões arquiteturais (ADRs)

### ADR 01 — SQLAlchemy + Alembic como ORM e ferramenta de migração

**Contexto.** O RNF05 exige que toda alteração de schema seja feita por migração versionada.
A proposta anterior do projeto era Tortoise ORM, escolhida por semelhança sintática com o
ORM do Django.

**Decisão.** Adotar SQLAlchemy síncrono como ORM, `psycopg2` como driver PostgreSQL e
Alembic para migrações. A conexão usa
`postgresql+psycopg2://usuario:senha@host:porta/banco`. A decisão foi aprovada durante a
revisão do PR #55 em 11/09/2026 e substitui a proposta de Tortoise ORM.

**Justificativa.** O Alembic é a ferramenta madura de migração no ecossistema; o equivalente
no Tortoise (Aerich) tem adoção e maturidade menores, e migração é justamente o ponto que o
RNF05 exige. Dois outros grupos da mesma turma (G3 e G9) usam a mesma combinação, o que dá
suporte de pares durante o semestre. O volume de material público sobre SQLAlchemy também
melhora a qualidade do código gerado com assistência de IA, prática adotada no projeto.

**Consequência.** Curva de aprendizado maior que a do Tortoise, especialmente em sessão e
mapeamento declarativo. O argumento de familiaridade com Django perde peso porque a migração
ocorreu ainda na fase de scaffold — o time tem familiaridade com o conceito de ORM, não com
os idiomas específicos do ORM do Django.

---

### ADR 02 — Next.js no frontend

**Contexto.** O frontend estava indefinido. A proposta inicial era HTML, CSS e JavaScript
puros consumindo a API por `fetch`.

**Decisão.** Adotar Next.js.

**Justificativa.** Os cinco critérios de avaliação aparecem em três telas distintas — detalhe
do professor, comparação e formulário. Sem componentização, a mesma estrutura seria duplicada
em três lugares. A tabela de comparação com ordenação (RF12, RF13) também depende de estado
de interface. Além do ganho técnico, o aprendizado de um framework moderno é objetivo
declarado do time, e é o framework usado pelos grupos G3 e G9.

**Consequência.** Next.js exige runtime Node no container, o que torna a containerização do
frontend mais pesada do que um build estático servido por nginx. Caso isso se mostre um
problema para a Epic de Docker, existe a alternativa de usar exportação estática
(`output: 'export'`), abrindo mão de renderização no servidor.

---

### ADR 03 — Identificação por e-mail institucional confirmado

**Estado.** Validada pelo grupo para a Release 1 em reunião presencial de 09/09/2026. A
decisão será reavaliada na validação geral da release e poderá ser refinada para a Release 2.

**Contexto.** O RF03 exige impedir avaliação duplicada, o que requer identificar o avaliador.
O sistema expõe publicamente avaliações sobre pessoas identificáveis pelo nome, o que torna
a origem das avaliações uma questão de credibilidade e não apenas de integridade de dados.

**Decisão.** Cadastro com nome, e-mail e senha, restrito ao domínio `@aluno.unb.br`, com
confirmação por link antes de a conta poder avaliar. A consulta permanece pública. A sessão
é armazenada no servidor e identificada por valor aleatório em cookie `HttpOnly`,
`SameSite=Lax` e `Secure` em produção. Ela expira após sete dias consecutivos de inatividade;
atividade válida renova esse prazo, e o logout invalida a sessão no servidor e remove o
cookie. Nenhum dado acadêmico é armazenado.

**Justificativa.** Cadastro com e-mail livre resolveria a duplicata, mas permitiria que
qualquer pessoa fora da universidade avaliasse professores da UnB — inclusive de forma
coordenada. A restrição de domínio responde diretamente à preocupação levantada sobre
exposição de professores, sem exigir matrícula ou histórico, preservando o RNF01.

**Consequência.** Exige infraestrutura de envio de e-mail e token de confirmação com
expiração, incluindo em ambiente de desenvolvimento, além de armazenamento persistente das
sessões no backend. Ex-alunos sem acesso ao domínio aceito e outros vínculos institucionais
não conseguem concluir o cadastro na Release 1.

**Pendência.** O provedor de envio e a validade do link de confirmação ainda precisam ser
definidos antes da implementação desse fluxo.

**Evidência.** Reunião presencial de 09/09/2026 nas mesas do UAC, convocada pelo grupo de
WhatsApp. Participaram Nicolas, Vinicius, Gabriel, Tiago e Warlley; Yasmin não participou.

---

### ADR 04 — Separação entre critérios de fato e de opinião no modelo

**Contexto.** Dos cinco critérios, dois descrevem fatos verificáveis (chamada e
disponibilização de material) e três expressam opinião.

**Decisão.** Tratar as duas naturezas com regras de agregação distintas: fato agrega por
maioria e admite estado "conflitante"; opinião agrega por média, moda ou percentual.

**Justificativa.** Divergência entre opiniões é legítima e informativa. Divergência sobre um
fato significa que alguém está errado, e exibir a média de um fato produziria um resultado
sem sentido. Tratar as duas naturezas da mesma forma degradaria a informação.

**Consequência.** A camada de agregação precisa conhecer a natureza de cada critério, o que
justifica isolá-la em `domain/` com testes próprios.

---

### ADR 05 — Ordenação exclusivamente pelo percentual de recomendação

**Contexto.** A comparação entre professores (RF12) exige um critério de ordenação, e os
cinco critérios usam escalas incompatíveis entre si.

**Decisão.** Ordenar exclusivamente pelo percentual de recomendação. Não criar índice
composto ponderando os cinco critérios.

**Justificativa.** Qualquer ponderação entre os critérios seria arbitrária — não existe
pesquisa que estabeleça o peso relativo de cada um, e a hipótese sobre quais fatores são
decisivos permanece explicitamente não validada.

**Consequência.** A interface não exibirá "nota geral" do professor, ainda que essa seja a
solicitação intuitiva. A ausência é deliberada.

---

### ADR 06 — Ausência de verificação de matrícula, assumida explicitamente

**Contexto.** O escopo original previa impedir que um aluno avaliasse disciplina que não
cursou. O histórico de matrícula por aluno não está disponível em página pública do SIGAA.

**Decisão.** Não implementar verificação de matrícula no Release 1. A integridade se apoia em
identificação institucional (ADR 03) e bloqueio de duplicata (RF03).

**Justificativa.** A alternativa exigiria acesso autenticado ao SIGAA em nome do aluno, o que
está fora do escopo do projeto e do precedente técnico da disciplina.

**Consequência.** Um aluno da UnB pode avaliar um professor que nunca teve. A limitação é
conhecida e assumida, e não deve ser contornada por heurística não verificável.

---

## 8. Riscos técnicos

| Risco | Impacto | Mitigação |
|---|---|---|
| Páginas públicas do SIGAA em JSF, com ViewState e postback | Pode inviabilizar scraping por requisição HTTP simples e exigir automação de navegador, alterando dependências, Dockerfile e tempo de importação | Verificar antes de estimar RF16–RF19 |
| Partida a frio: base vazia no lançamento | O produto não responde nada ao primeiro usuário | RF10 (estado vazio explícito) e ação de povoamento inicial junto ao time |
| Identificação indireta do avaliador em disciplinas com poucas avaliações | Risco de retaliação | RNF02 — definir mínimo de avaliações antes de exibir resultado detalhado |
| Estrutura do SIGAA muda sem aviso | Importação para de funcionar silenciosamente | RF19 (log de execução) e RNF07 (falha isolada) |
| Runtime Node no container do frontend | Ambiente mais pesado | Alternativa de exportação estática (ADR 02) |
