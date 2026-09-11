# G7 - Avaliação de Professores UnB

Grupo G7 - Métodos de Desenvolvimento de Software 2026/2

## Sobre o projeto

Aplicação web para avaliação de professores da UnB, com dados de disciplinas e turmas integrados a partir do SIGAA.

## Equipe

| Nome | GitHub | Papel no Sprint atual |
|---|---|---|
| _Nome 1_ | [@nicolaszanin06](https://github.com/nicolaszanin06) | Product Owner |
| _Nome 2_ | [@usuario2](https://github.com/usuario2) | Scrum Master |
| _Nome 3_ | [@usuario3](https://github.com/usuario3) | Dev Team |
| _Nome 4_ | [@gabrielrdaraujo](https://github.com/gabrielrdaraujo) | Dev Team |
| _Nome 5_ | [@usuario5](https://github.com/usuario5) | Dev Team |
| _Nome 6_ | [@warlleymedeiros](https://github.com/warlleymedeiros) | Dev Team |

## Tecnologias

- **Backend:** Python 3.12 + FastAPI + Uvicorn
- **Banco de dados:** PostgreSQL via Docker Compose + SQLAlchemy
- **Frontend:** _(a definir — proposta: HTML/CSS/JS puro consumindo a API via `fetch`)_
- **Integração:** dados extraídos do SIGAA
- **CI/CD:** GitHub Actions

## Metodologia

O time trabalha com **Scrum**, em sprints de **1 semana**. O board de acompanhamento fica em [Projects](../../projects) e as tarefas são gerenciadas via [Issues](../../issues).

- **Planning:** toda segunda-feira
- **Daily:** assíncrona, via grupo do time
- **Review + Retrospectiva:** toda sexta-feira

### Releases

- **Release 1:** _(data a definir)_
- **Release 2 (final):** 25/11/2026

## Como rodar o projeto localmente

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

# rodar o servidor de desenvolvimento
cd backend
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
