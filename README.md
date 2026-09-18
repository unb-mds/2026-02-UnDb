# UnDb — Avaliação de Professores da UnB

Grupo G7 - Métodos de Desenvolvimento de Software 2026/2

## Sobre o projeto

Aplicação web para avaliação de professores da UnB, com dados de disciplinas e turmas integrados a partir do SIGAA.

## Documentação do produto

- [Documento de visão](docs/visao.md)
- [Engenharia de requisitos](docs/requisitos.md)
- [Site de documentação](https://unb-mds.github.io/2026-02-UnDb/)
- [Board de requisitos no Figma](https://www.figma.com/board/qs0bvgeJXyfCxYFEDSX9VH/G7---Requisitos--Avalia%C3%A7%C3%A3O-de-Professores-UnB-)
- [Especificação de implementação](specs.md)
- [Arquitetura](docs/arquitetura.md)

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

## Como rodar o projeto localmente

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

# construir as imagens, iniciar PostgreSQL e API, e aplicar as migrações
# usando as variáveis configuradas em backend/.env
docker compose --env-file backend/.env up --build
```

A API sobe em `http://127.0.0.1:8000`, o health check em
`http://127.0.0.1:8000/health` e a documentação interativa em
`http://127.0.0.1:8000/docs`. Para encerrar os serviços, use `docker compose down`.
O volume `postgres_data` preserva os dados do banco entre recriações dos containers.

A decisão de persistência e as restrições do modelo estão registradas em
[`sprints/sprint02/banco-de-dados.md`](sprints/sprint02/banco-de-dados.md).

O procedimento para coletar e persistir dados institucionais do SIGAA, incluindo o contrato
de resultado consumível pela rotina de atualização, está em
[`docs/importacao-sigaa.md`](docs/importacao-sigaa.md).

## Fluxo de contribuição

### Verificações automatizadas

O check `Backend` executa os testes determinísticos com `python -m unittest discover -s tests -v`,
valida aplicação e migrações em um PostgreSQL 16 descartável de CI, compara o schema com os modelos
e testa downgrade/upgrade. Também constrói a imagem e verifica a presença das migrações Alembic.
A versão do banco de CI não define, por si só, a versão de produção.

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
