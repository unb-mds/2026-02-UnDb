# Banco de dados - Sprint 02

## Decisão de persistência

**Estado:** `Defined`

O backend usa SQLAlchemy síncrono para mapear os modelos e PostgreSQL como
banco de dados. A decisão recebeu aprovação humana explícita durante a revisão
do PR #55 em 11/09/2026.

A conexão é configurada pela variável obrigatória `DATABASE_URL`, no formato:

```text
postgresql+psycopg2://usuario:senha@host:porta/banco
```

O arquivo `backend/.env.example` contém um exemplo local sem credenciais reais.
O módulo `backend/app/core/config.py` é a fonte única da configuração, consumida
pela sessão em `backend/app/db/session.py`.

## Entidades e identificadores de importação

As restrições abaixo fazem parte do modelo físico e garantem chaves estáveis
para deduplicação e operações de upsert:

| Entidade | Identificador | Restrição no ORM |
|---|---|---|
| Departamento | `sigla` | `UNIQUE (sigla)` |
| Disciplina | `codigo` | `UNIQUE (codigo)` |
| Professor | `nome`, `id_departamento` | `UNIQUE (nome, id_departamento)` |
| Turma | `id_disciplinas`, `cod_turma`, `semestre` | `UNIQUE (id_disciplinas, cod_turma, semestre)` |
| Avaliação | `id_usuario`, `id_turma` | `UNIQUE (id_usuario, id_turma)` |

O diagrama lógico identifica chaves únicas simples como `UQ` e agrupa as
colunas de uma mesma chave composta como `UQ1`. Os modelos SQLAlchemy são a
representação executável dessas restrições.

Os PDFs conceitual e lógico podem ser regenerados com
`python docs/diagramas/gerar_modelos.py`; esse gerador documental requer o
pacote `reportlab` e não faz parte das dependências de execução do backend.

## Lacunas conhecidas da fonte

- `Professor.email` e `Professor.lattes` são opcionais porque sua presença na
  fonte pública ainda não está garantida.
- `Turma.horario` é texto opcional para preservar formatos variados e ausências
  encontradas durante a futura validação da coleta.
- O modelo atual associa uma turma a um professor. O suporte a múltiplos
  docentes por turma continua pendente de evidência da coleta e de aprovação
  antes de qualquer mudança estrutural.

## Estado das Issues #22 e #23

As Issues #22 e #23 continuam abertas. Este trabalho prepara o modelo para
receber os dados, mas não comprova os critérios de aceite do mapeamento ou do
protótipo de scraping.

Ainda precisam ser produzidas e anexadas às respectivas Issues:

- URLs e passos de navegação nas páginas públicas;
- campos realmente disponíveis e forma de relacioná-los;
- comportamento de paginação, formulários, JSF, ViewState ou postback;
- comparação de uma extração com uma oferta real;
- instruções reproduzíveis do protótipo;
- conclusão baseada em evidência sobre HTTP direto ou automação de navegador.

Essas informações não devem ser apresentadas como validadas enquanto a
investigação e suas evidências não forem concluídas.

## Criação das tabelas

Com um `backend/.env` válido e as dependências instaladas:

```bash
cd backend
python create_tables.py
```

O script importa todos os modelos registrados e executa
`Base.metadata.create_all`. Um fluxo de migrations não faz parte desta entrega
e não deve ser citado como mecanismo já validado de evolução do schema.
