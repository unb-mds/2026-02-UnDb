# UnDb — Avaliação de Professores da UnB

Grupo G7 - Métodos de Desenvolvimento de Software 2026/2

## Sobre o projeto

Aplicação web para avaliação de professores da UnB, com dados de disciplinas e turmas integrados a partir do SIGAA.

## Documentação do produto

Aplicação pública: [undb.app.br](https://undb.app.br). API:
[health](https://api.undb.app.br/health) (verifica o processo HTTP).
[Hospedagem e operação](docs/hospedagem.md),
[v1.1.0](docs/releases/1.1.0.md) e
[estado da R2](docs/releases/2.0.0-reconciliacao.md) distinguem publicação,
integrações em develop e verificações ainda pendentes.

- [Documento de visão](docs/visao.md)
- [Engenharia de requisitos](docs/requisitos.md)
- [Site de documentação](https://unb-mds.github.io/2026-02-UnDb/)
- [Board de requisitos no Figma](https://www.figma.com/board/qs0bvgeJXyfCxYFEDSX9VH/G7---Requisitos--Avalia%C3%A7%C3%A3O-de-Professores-UnB-)
- [Especificação de implementação](specs.md)
- [Arquitetura](docs/arquitetura.md)
- [ADRs — catálogo, manutenção e template](docs/adrs/index.md)
- [Estratégia de qualidade — ADR 09 proposto](docs/adrs/09-estrategia-qualidade.md)

## Equipe

| Nome | GitHub | Papel no Sprint atual |
|---|---|---|
| _Nicolas_ | [@nicolaszanin06](https://github.com/nicolaszanin06) | Product Owner |
| _Yasmin_ | [@ailoiol](https://github.com/ailoiol) | Scrum Master |
| _Vinicius_ | [@ViniGvdo](https://github.com/ViniGvdo) | Dev Team |
| _Gabriel_ | [@gabrielrdaraujo](https://github.com/gabrielrdaraujo) | Dev Team |
| _Tiago_ | [@TiagoVieira-596](https://github.com/TiagoVieira-596) | Dev Team |
| _Warlley_ | [@warlleymedeiros](https://github.com/warlleymedeiros) | Dev Team |

## Tecnologias

- **Backend:** Python 3.12 + FastAPI + Uvicorn
- **Banco de dados:** PostgreSQL via Docker Compose + SQLAlchemy + Alembic
- **Frontend:** Next.js + Tailwind CSS
- **Integração:** dados extraídos do SIGAA
- **CI/CD:** GitHub Actions

## Metodologia

O time trabalha com **Scrum**, em sprints de **1 semana**. O acompanhamento fica no
[G7 - Board de Desenvolvimento](https://github.com/orgs/unb-mds/projects/60) e as tarefas
são gerenciadas via [Issues](../../issues) e [milestones](../../milestones).

- **Planning:** toda segunda-feira
- **Daily:** assíncrona, via grupo do time
- **Review + Retrospectiva:** toda sexta-feira

### Releases

- **Release 1:** 28/09/2026
- **Release 2 (final):** 25/11/2026

A Release 1.0.0 usa importação manual dos dados públicos do SIGAA no ambiente local.
A atualização periódica automática ficou para a Release 2. Consulte as
[notas da Release 1.0.0](docs/releases/1.0.0.md).

## Como rodar o projeto localmente

### Ambiente completo com Docker Compose

**Pré-requisito:** Docker Engine com o plugin Docker Compose disponível.

O arquivo `backend/.env` deve definir `SECRET_KEY`, `DEBUG`, as credenciais locais do
PostgreSQL (`POSTGRES_USER`, `POSTGRES_PASSWORD` e `POSTGRES_DB`) e a `DATABASE_URL` com
o host `db`. O `.env` real nunca deve ser versionado.

```bash
# clonar o repositório
git clone https://github.com/unb-mds/2026-02-UnDb.git
cd 2026-02-UnDb

# configurar variáveis de ambiente
cp backend/.env.example backend/.env  # Windows: copy backend\.env.example backend\.env
# edite backend/.env e troque os valores de exemplo, principalmente as senhas

# construir as imagens, iniciar PostgreSQL, API e frontend, e aplicar as migrações
# usando as variáveis configuradas em backend/.env
docker compose --env-file backend/.env up --build
```

A API sobe em `http://127.0.0.1:8000`, o health check em
`http://127.0.0.1:8000/health` e a documentação interativa em
`http://127.0.0.1:8000/docs`. O frontend fica em `http://localhost:3000`.
Para encerrar os serviços, use `docker compose --env-file backend/.env down`.
O volume `postgres_data` preserva os dados do banco entre recriações dos containers.

O serviço `descarte-moderacao` acompanha a API e remove dados de moderação vencidos.
Ao subir somente parte do Compose, inclua `backend db descarte-moderacao` para manter
o descarte ativo. Sem Docker, execute `python -m app.commands.descartar_moderacao --continuo`
no mesmo ambiente da API. O prazo aprovado é de sete dias; o worker verifica a cada
60 segundos e consultas privadas/autor também limpam registros vencidos antes de responder.

Por determinação do PO, o operador pode conceder ou revogar o papel de moderador
de uma conta confirmada de membro da equipe:

```bash
docker compose --env-file backend/.env exec backend \
  python -m app.commands.moderador membro@aluno.unb.br conceder
# para retirar a permissão, use revogar no lugar de conceder
```

Não existe concessão pública de papel. Consulte o
[contrato e as verificações das APIs de denúncia/moderação](docs/estudos/alinhamento-denuncias-issues-160-161.md).

O frontend executa o servidor Next.js com build otimizado, sem recarga automática no
container. Depois de alterar seu código, execute novamente o comando com `--build`.
O build precisa de acesso à internet para instalar dependências e baixar as fontes Geist
usadas por `next/font/google`. Não precisa de dados do backend durante a compilação.

O navegador acessa a API por `NEXT_PUBLIC_API_URL` (padrão `http://localhost:8000`),
enquanto o servidor Next.js usa `API_INTERNAL_URL=http://backend:8000` na rede do Compose.
Nunca use `http://backend:8000` como URL pública: esse nome só existe entre containers.
Para personalizar a URL pública, adicione `NEXT_PUBLIC_API_URL` ao `backend/.env` passado
ao Compose e reconstrua o frontend. Ajuste também `CORS_ORIGINS` com a origem do frontend
aberta no navegador. `frontend/.env.local` é usado apenas na execução fora do Docker;
nenhum `.env` entra na imagem do frontend.

Por padrão, `EMAIL_BACKEND=console`: após um cadastro válido, o link de confirmação aparece
nos logs do backend e pode ser aberto no navegador, sem domínio ou serviço externo. Para
acompanhar o link:

```bash
docker compose --env-file backend/.env logs -f backend
```

Na Release 1, o fluxo de confirmação permanece exclusivamente nesse modo de teste. A
ativação do envio real fica planejada para a Release 2; quando houver domínio remetente
verificado, configure `EMAIL_BACKEND=resend`, `RESEND_API_KEY` e `EMAIL_FROM` no ambiente.
Nunca versione a chave.

Para verificar a composição e acompanhar a inicialização:

```bash
docker compose --env-file backend/.env config --quiet
docker compose --env-file backend/.env ps
docker compose --env-file backend/.env logs backend frontend
```

O health check do frontend verifica seu servidor HTTP. Aguarde também a conclusão das
migrações e a API ficar disponível antes de consultar dados; a ordem de início dos
containers não garante prontidão da API. A configuração atende ao ambiente local e não
define hospedagem pública, TLS ou operação em produção.

A decisão de persistência e as restrições do modelo estão registradas em
[`sprints/sprint02/banco-de-dados.md`](sprints/sprint02/banco-de-dados.md).

Para carregar as turmas de graduação de todas as unidades antes de apresentar a
Release 1, mantenha o Compose ativo e execute:

```bash
docker compose --env-file backend/.env exec backend \
  python -m app.commands.importar_sigaa_agendado \
  --todas-unidades --ano 2026 --periodo 2
```

Ajuste ano e período para o semestre consultado. O comando retorna sucesso somente
quando todas as unidades são processadas; o resultado fica registrado no banco.
As instruções de consulta do registro estão em
[`docs/operacao-importacao-sigaa.md`](docs/operacao-importacao-sigaa.md).

O procedimento para coletar e persistir dados institucionais do SIGAA, incluindo o contrato
de resultado consumível pela rotina de atualização, está em
[`docs/importacao-sigaa.md`](docs/importacao-sigaa.md).

### Frontend com recarga automática, fora do Docker

**Pré-requisitos:** Node.js 20.9 ou superior com npm (a imagem usa Node.js 24) e o backend
acessível. Para usar apenas backend e banco no Compose, sem ocupar a porta 3000:

```bash
docker compose --env-file backend/.env up --build backend db
```

```bash
cd frontend
npm ci
cp .env.example .env.local  # Windows: copy .env.example .env.local
npm run dev
```

A aplicação sobe em `http://localhost:3000` e consome por padrão a API em
`http://localhost:8000`. Ajuste `NEXT_PUBLIC_API_URL` em `.env.local` quando o backend estiver
publicado em outro endereço. Os comandos disponíveis para lint, build de produção e execução
do build estão documentados em [`frontend/README.md`](frontend/README.md).

A estratégia implementada para revisão na [Issue #36](https://github.com/unb-mds/2026-02-UnDb/issues/36) usa servidor
Next.js, sem exportação estática. A justificativa, as alternativas e as consequências
estão no [ADR 08](docs/arquitetura.md).

## Fluxo de contribuição

### Verificações automatizadas

Lint e formatação Python usam Ruff, fixado em `backend/requirements-dev.txt`, sobre
aplicação, testes, migrações e scripts. O frontend preserva ESLint e oferece
`npm run typecheck` (`next typegen && tsc --noEmit`) sem depender de build anterior.
Instalação, comandos de verificação/correção e escopo estão no
[guia de contribuição](CONTRIBUTING.md).

O check `Backend` executa os testes determinísticos com `python -m unittest discover -s tests -v`,
sob instrumentação do coverage.py. O job também valida aplicação e migrações em um PostgreSQL 16
descartável de CI, compara o schema com os modelos, testa downgrade/upgrade, constrói a imagem
e verifica a presença das migrações Alembic.
A versão do banco de CI não define, por si só, a versão de produção.

Os checks `Backend` e `Frontend` publicam relatórios de cobertura como artefatos
do GitHub Actions. Consulte os comandos locais, o escopo e a linha de base no
[registro de cobertura da #190](docs/estudos/cobertura-testes-issue-190.md).

O acesso real ao SIGAA permanece uma verificação manual documentada na
[POC](docs/estudos/sigaa-poc.md); não é dependência dos testes determinísticos.

### Branches e revisão

O projeto usa Gitflow: `main` representa releases e `develop` integra o trabalho da
próxima release. Features e correções comuns partem de `develop`; releases e
hotfixes são integrados em `main` por Pull Request.

Consulte o [guia de contribuição](CONTRIBUTING.md) para a nomenclatura de branches,
destinos permitidos, checks e regras de aprovação.

## Licença

_(a definir)_
