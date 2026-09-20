# Verificação do ambiente completo — Issue #37

**Data:** 20/09/2026 (America/Sao_Paulo)  
**Responsável por esta execução:** Gabriel  
**Fonte testada:** `develop` no commit `372ede1f33b6f00e3278f9095a4802ab0576337f`

## Resultado

Esta execução foi **aprovada**. Em um clone novo do repositório, o ambiente completo
subiu com PostgreSQL, backend e frontend sem alteração de código ou configuração
manual adicional. O único arquivo criado foi `backend/.env`, por cópia direta de
`backend/.env.example`, conforme o procedimento do README.

Esta evidência corresponde ao teste de **um membro**. O critério da Issue #37 ainda
exige uma segunda execução independente por outro membro da equipe.

## Ambiente

- Windows com WSL2;
- Docker Desktop `4.91.0.239619`;
- Docker Engine e cliente `29.8.0`;
- Docker Compose `v5.5.1`.

## Procedimento executado

1. Foi criado um clone novo e isolado da branch `develop`.
2. `backend/.env.example` foi copiado para `backend/.env`, sem edição.
3. A configuração foi validada com `docker compose --env-file backend/.env config --quiet`.
4. O ambiente foi construído e iniciado com `docker compose --env-file backend/.env up --build -d`.
5. A prontidão foi confirmada com `docker compose --env-file backend/.env up -d --wait`.
6. Frontend, API, CORS, documentação OpenAPI, migração e imagens foram verificados.
7. Os containers foram recriados sem remover o volume para validar persistência.

## Evidências observadas

| Verificação | Resultado |
|---|---|
| `docker compose config --quiet` | aprovado, código de saída 0 |
| Build do backend | concluído |
| Build do frontend | concluído; Next.js e TypeScript sem erro |
| PostgreSQL | ativo e saudável |
| Backend | ativo; `GET /health` retornou `{"status":"ok"}` |
| Documentação da API | `GET /docs` retornou HTTP 200 |
| Frontend | página inicial e `/professores` retornaram HTTP 200 |
| Integração visual | busca por professor exibiu corretamente o estado vazio vindo da API |
| API real | `/api/professores` e `/api/disciplinas` retornaram HTTP 200 |
| CORS | origem `http://localhost:3000` autorizada nas respostas da API |
| Migração | revisão Alembic `20260920_01` aplicada |
| Persistência | dado de prova permaneceu após `down` e nova subida |
| Logs após reinício | nenhuma linha compatível com erro, fatal, traceback ou exceção não tratada |
| Segredos nas imagens | nenhum `.env`, `SECRET_KEY` ou `POSTGRES_PASSWORD` encontrado |

## Conclusão

Os critérios técnicos da execução individual foram atendidos: o ambiente sobe a
partir de clone novo, somente com a cópia do arquivo de exemplo e comandos Docker
documentados. Não foi identificado passo faltante no README nem defeito do projeto
durante esta execução.

Para concluir oficialmente a Issue #37, falta apenas outro membro repetir o procedimento
em sua própria máquina e registrar a segunda evidência.
