# G7 - Avaliação de Professores UnB

Grupo G7 - Métodos de Desenvolvimento de Software 2026/2

## Sobre o projeto

Aplicação web para avaliação de professores da UnB, com dados de disciplinas e turmas integrados a partir do SIGAA.

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
- **Frontend:** Next.js
- **Integração:** dados extraídos do SIGAA
- **CI/CD:** GitHub Actions

## Metodologia

O time trabalha com **Scrum**, em sprints de **1 semana**. O board de acompanhamento fica em [Projects](../../projects) e as tarefas são gerenciadas via [Issues](../../issues).

- **Planning:** toda segunda-feira
- **Daily:** assíncrona, via grupo do time
- **Review + Retrospectiva:** toda sexta-feira

### Releases

- **Release 1:** 28/09/2026
- **Release 2 (final):** 25/11/2026

## Como rodar o projeto localmente

**Pré-requisito:** mantenha uma instância PostgreSQL em execução e crie nela o usuário e o
banco informados em `DATABASE_URL`. Este repositório ainda não provisiona o PostgreSQL via
Docker Compose; essa configuração é acompanhada pela [Issue #35](../../issues/35).

O arquivo `backend/.env` deve definir `SECRET_KEY` com um valor aleatório, `DEBUG` como
`True` ou `False` e `DATABASE_URL` com as credenciais e o endereço do PostgreSQL.

```bash
# clonar o repositório
git clone https://github.com/unb-mds/G7-2026-2.git
cd G7-2026-2

# criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# instalar dependências do backend
pip install -r backend/requirements.txt

# configurar variáveis de ambiente
cp backend/.env.example backend/.env  # Windows: copy backend\.env.example backend\.env
# edite backend/.env e preencha os valores (o .env real nunca é commitado)
# DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/g7

# aplicar as migrações e rodar o servidor de desenvolvimento
# (o PostgreSQL configurado em DATABASE_URL já deve estar acessível)
cd backend
alembic upgrade head
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000` e a documentação interativa fica em `http://127.0.0.1:8000/docs`.

A decisão de persistência e as restrições do modelo estão registradas em
[`sprints/sprint02/banco-de-dados.md`](sprints/sprint02/banco-de-dados.md).

## Fluxo de contribuição

1. Crie uma branch a partir da `main`: `feature/nome-curto-da-tarefa`
2. Faça commits pequenos e descritivos
3. Abra um Pull Request referenciando a Issue correspondente (`Closes #12`)
4. Peça revisão de pelo menos 1 outro membro antes de mergear

## Licença

_(a definir)_
