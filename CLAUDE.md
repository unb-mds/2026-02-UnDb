# G7 — Avaliação de Disciplinas (UnB MDS)

## Sobre o projeto

- Disciplina: Métodos de Desenvolvimento de Software (MDS), UnB — professora Carla Rocha.
- Objetivo: aplicativo web de avaliação de disciplinas + professores da UnB, com dados públicos extraídos do SIGAA.
- Equipe: G7, 6 integrantes, Scrum com sprints semanais.

## Documentos do projeto

Antes de implementar qualquer coisa, leia:

- `docs/requisitos.md` — **fonte de verdade** dos requisitos (RF e RNF), personas, pesquisa com usuário, matriz de rastreabilidade e decisões pendentes.
- `docs/arquitetura.md` — camadas, modelo de dados e decisões arquiteturais (ADRs).
- `specs.md` — especificação de implementação **derivada** dos dois anteriores. É onde estão os tipos exatos, regras de agregação, constraints e restrições permanentes.

Regra de hierarquia: mudança de requisito ocorre primeiro em `docs/requisitos.md`, e o `specs.md` é regenerado a partir dela. O `specs.md` nunca é editado isoladamente. Se houver divergência, os documentos em `docs/` prevalecem.

## Stack atual

- **Backend:** FastAPI + Uvicorn + Python 3.12. Migrado de Django (pedido da professora, por separação insuficiente entre front e back).
- **ORM:** SQLAlchemy. **Migrações:** Alembic. Nenhuma alteração de schema fora de migração versionada (ver ADR 01 e RNF05).
- **Frontend:** Next.js, em pasta `frontend/` separada (ver ADR 02).
- **Banco de dados:** PostgreSQL via Docker Compose.
- **Identificação:** cadastro com e-mail institucional da UnB confirmado por link (ver ADR 03).
- **Scraping SIGAA:** páginas públicas, sem autenticação (referência: `unb-mds/SuaGradeUnB`).

> As decisões de ORM, frontend e identificação são **proposta do PO**, fundamentadas nos requisitos validados. Passam a valer como decisão do projeto após validação do time.

## Como este projeto usa Skills

Antes de qualquer tarefa, verifique se existe uma skill relevante dentro de `skills/<categoria>/<nome>/SKILL.md`:

- `skills/governance/` — `project-governance` (autoridade, evidência, escopo, aprovação humana) e `skill-authoring` (ciclo de vida das skills). Leia `skill-authoring` antes de criar uma skill nova.
- `skills/process/` — `requirements` (requisitos e critérios de aceite). Scrum e fluxo de GitHub ainda a criar.
- `skills/engineering/` — `architecture`, `implementation`, `testing`, `code-review`.
- `skills/technology/` — guias por tecnologia (`docker`, `fastapi`).

Compare a tarefa pedida com a `description` de cada `SKILL.md` dessas pastas antes de agir. Se uma skill for aplicável, leia o arquivo inteiro e siga as instruções nela antes de gerar código ou configuração.

Não transforme uma skill de `proposed` para `defined` sem aprovação humana explícita.

## Convenções gerais

- Segredos nunca são commitados: variáveis sensíveis ficam em `.env` (fora do Git), lidas via `python-decouple`.
- Fluxo de Git: GitHub Flow — sempre branch de feature + Pull Request, nunca push direto na `main`.
- Nomenclatura: entidades de domínio em português (`Avaliacao`, `Usuario`, `Professor`, `Disciplina`, `Turma`), estrutura técnica (routers, schemas, etc.) em inglês.
- Lógica de negócio nunca dentro da função do router. Regras de agregação ficam em `app/domain/`, sem dependência de banco.

## Restrições permanentes do produto

Estas valem para qualquer implementação e não devem ser contornadas sem alterar `docs/requisitos.md`:

- Não criar nota geral do professor nem índice composto ponderando os critérios de avaliação.
- Não exibir dificuldade e chamada com codificação de valor (cor de alerta, ranking, ícone de positivo/negativo). São informativos, não avaliativos.
- Não exibir valor de critério abaixo do mínimo de avaliações definido em `specs.md`.
- Não armazenar matrícula, CPF ou histórico acadêmico do avaliador.
- Não introduzir campo de texto livre antes do Release 2.

## Estado atual

- Engenharia de requisitos concluída: pesquisa com usuários, personas, requisitos numerados e ADRs.
- Skills `docker` e `fastapi`: status `proposed`.
- Skill `requirements`: status `proposed`.
- Decisão pendente: SQLAlchemy síncrono ou assíncrono (impacta driver e assinatura de repositories; ver `skills/technology/fastapi/SKILL.md`, seção 15).
- Decisões ainda pendentes: domínio de e-mail institucional, provedor de envio de e-mail, formato de sessão, viabilidade técnica do scraping do SIGAA (páginas em JSF) e estratégia de povoamento inicial da base. Ver `docs/requisitos.md`, seção 11.