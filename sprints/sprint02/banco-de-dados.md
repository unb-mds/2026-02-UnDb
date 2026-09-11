# Banco de dados - Sprint 02

## Decisão de persistência

**Estado:** `Defined`

O backend usa SQLAlchemy síncrono, Alembic, PostgreSQL e o driver `psycopg2`. A decisão
recebeu aprovação humana explícita durante a revisão do PR #55 em 11/09/2026.

A conexão é configurada exclusivamente por `backend/app/core/config.py`, por meio da
variável obrigatória `DATABASE_URL`:

```text
postgresql+psycopg2://usuario:senha@host:porta/banco
```

O arquivo `backend/.env.example` contém um exemplo local sem credenciais reais. A sessão
síncrona está em `backend/app/core/database.py`.

## Modelo implementado

O modelo físico segue `specs.md` e `docs/arquitetura.md`:

| Entidade | Identificador e restrições principais |
|---|---|
| Usuário | UUID; e-mail único; sem matrícula, CPF ou histórico acadêmico |
| Professor | UUID; nome e departamento |
| Disciplina | UUID; código único; nome, departamento e créditos opcionais |
| Turma | UUID; única por disciplina, professor e semestre |
| Avaliação | UUID; única por usuário, professor e disciplina |

A avaliação contém apenas os campos estruturados definidos em `specs.md`. Não existe nota
geral, ranking persistido ou comentário em texto livre. `didatica` aceita valores de 1 a 5,
e `qualidade_material` só pode ser preenchida quando há material disponível.

Os PDFs conceitual e lógico podem ser regenerados com:

```bash
python docs/diagramas/gerar_modelos.py
```

O gerador documental requer `reportlab`, que não faz parte das dependências de execução do
backend.

## Migrações

Toda mudança de schema deve passar por uma migração Alembic versionada. Scripts com
`Base.metadata.create_all` e DDL manual não fazem parte do fluxo.

Com `backend/.env` configurado e as dependências instaladas:

```bash
cd backend
alembic upgrade head
```

A migração inicial cria as cinco tabelas, chaves estrangeiras, enums, checks e restrições
de unicidade descritas na especificação.

## Estado das Issues #22 e #23

As Issues #22 e #23 continuam abertas. O modelo está pronto para receber dados, mas ainda
faltam as evidências de mapeamento e do protótipo de scraping: URLs, passos de navegação,
campos disponíveis, comportamento de JSF/ViewState, comparação com oferta real e conclusão
reproduzível sobre HTTP direto ou automação de navegador.

Essas informações não devem ser apresentadas como validadas antes da investigação.
