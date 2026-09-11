# Docker no projeto G7

Este documento serve como material de estudo e como guia para a futura
containerização do projeto **Avaliação de Professores UnB**. Ele explica os
conceitos essenciais de Docker, relaciona esses conceitos à arquitetura do G7
e apresenta uma configuração de desenvolvimento como referência.

> **Estado deste documento:** material de estudo. Os exemplos de `Dockerfile` e
> Docker Compose abaixo são propostas e ainda não representam configuração
> executável do repositório.

## 1. Por que usar Docker?

Sem Docker, cada integrante precisa instalar e configurar Python, Node.js,
PostgreSQL e suas dependências diretamente no computador. Diferenças de versão
ou de sistema operacional podem fazer o projeto funcionar em uma máquina e
falhar em outra.

Docker empacota cada serviço com o ambiente necessário para executá-lo. Assim,
o time consegue iniciar os serviços de forma reproduzível e isolada.

No G7, a divisão planejada é:

| Serviço | Tecnologia | Responsabilidade |
|---|---|---|
| `backend` | Python 3.12, FastAPI e Uvicorn | Expor a API HTTP |
| `db` | PostgreSQL | Persistir os dados da aplicação |
| `frontend` | Next.js | Oferecer a interface web |

Atualmente, somente o backend possui um scaffold implementado. A configuração
do frontend e a integração efetiva com PostgreSQL ainda dependem da evolução do
projeto.

## 2. Conceitos fundamentais

### Imagem

Uma **imagem** é um pacote imutável que contém o sistema-base, as dependências e
os arquivos necessários para executar um serviço. Ela funciona como um molde.

Exemplo: uma imagem do backend pode partir de `python:3.12-slim`, instalar o
`requirements.txt` e copiar o código da API.

### Container

Um **container** é uma instância em execução de uma imagem. A mesma imagem pode
originar vários containers, todos com o mesmo ambiente inicial.

### Dockerfile

O `Dockerfile` é a receita usada para construir uma imagem. Cada instrução cria
uma etapa do processo, como escolher a imagem-base, copiar arquivos ou definir o
comando de inicialização.

### Docker Compose

O Docker Compose descreve como vários containers trabalham juntos. Ele é útil
para iniciar, com um único comando, a API, o banco e futuramente o frontend.

### Volume

O sistema de arquivos interno de um container é descartável. Um **volume**
mantém dados fora desse ciclo de vida. O PostgreSQL deve usar um volume para que
os dados não desapareçam quando seu container for recriado.

### Rede

O Compose cria uma rede interna e fornece resolução de nomes entre serviços.
Por isso, o backend deve acessar o banco pelo nome do serviço, por exemplo
`db:5432`, e não por `localhost:5432`. Dentro do container do backend,
`localhost` aponta para o próprio backend.

## 3. Como os arquivos se relacionam

```text
docker-compose.yml
├── backend
│   ├── constrói a imagem com backend/Dockerfile
│   ├── publica a porta 8000
│   └── recebe DATABASE_URL e outras variáveis
└── db
    ├── usa uma imagem oficial do PostgreSQL
    └── persiste os dados em um volume
```

Arquivos normalmente envolvidos:

- `backend/Dockerfile`: receita da imagem da API;
- `.dockerignore`: arquivos que não devem entrar no contexto de build;
- `docker-compose.yml`: orquestração dos serviços locais;
- `.env`: valores locais e secretos, nunca versionados;
- `.env.example`: nomes e exemplos seguros das variáveis necessárias.

## 4. Leitura de um Dockerfile para o backend

O exemplo abaixo é compatível com a estrutura atual, na qual a aplicação está
em `backend/app/main.py`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

O papel de cada instrução:

| Instrução | Efeito |
|---|---|
| `FROM` | Seleciona uma imagem oficial e enxuta do Python |
| `WORKDIR` | Define `/app` como diretório de trabalho no container |
| primeiro `COPY` | Copia apenas o manifesto de dependências |
| `RUN` | Instala as dependências sem manter o cache do `pip` |
| segundo `COPY` | Copia o código da aplicação |
| `EXPOSE` | Documenta a porta usada pela API |
| `CMD` | Inicia o Uvicorn e o torna acessível fora do container |

A ordem das cópias aproveita o cache de camadas: alterações no código não
obrigam o Docker a reinstalar dependências enquanto `requirements.txt` não
mudar.

## 5. O papel do `.dockerignore`

O arquivo reduz o contexto enviado ao Docker e evita copiar arquivos locais ou
sensíveis para a imagem. Uma configuração inicial seria:

```dockerignore
venv/
__pycache__/
*.pyc
.git/
.env
*.log
.pytest_cache/
```

O `.dockerignore` não substitui o `.gitignore`: o primeiro controla o conteúdo
enviado ao build; o segundo controla o que é versionado no Git.

## 6. Leitura de uma configuração Compose

Este exemplo demonstra uma possível configuração local para backend e banco:

```yaml
services:
  backend:
    build:
      context: ./backend
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      - db

  db:
    image: postgres:16
    env_file:
      - ./backend/.env
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
```

Pontos importantes:

- `build.context` determina quais arquivos estarão disponíveis para o build;
- `ports` mapeia a porta `8000` do computador para a porta `8000` do container;
- `env_file` injeta variáveis em tempo de execução, sem colocá-las na imagem;
- para o serviço `db`, a imagem `postgres` exige `POSTGRES_PASSWORD` (e, opcionalmente, `POSTGRES_USER`/`POSTGRES_DB`) via `env_file` ou `environment`;
- `depends_on` controla a ordem de inicialização, mas sozinho não garante que o
  banco já esteja pronto para aceitar conexões;
- `pgdata` preserva os dados do PostgreSQL entre recriações do container.

Quando a conexão for implementada, uma URL interna típica terá o formato:

```env
DATABASE_URL=postgresql://USUARIO:SENHA@db:5432/NOME_DO_BANCO
```

Os valores reais devem ficar somente em `.env`. O repositório já ignora esse
arquivo. Um `.env.example` versionado deve conter apenas valores fictícios ou
seguros para desenvolvimento.

## 7. Fluxo de trabalho local

Depois que os arquivos Docker forem efetivamente adicionados ao projeto, o
fluxo esperado será:

```bash
# construir as imagens e iniciar os serviços
docker compose up --build

# iniciar em segundo plano
docker compose up -d

# acompanhar os logs
docker compose logs -f

# acompanhar somente a API
docker compose logs -f backend

# listar os containers do projeto
docker compose ps

# encerrar os containers e a rede
docker compose down
```

Para apagar também os volumes locais, existe `docker compose down --volumes`.
Esse comando elimina os dados persistidos do banco e, portanto, deve ser usado
somente quando essa perda for intencional.

## 8. Desenvolvimento e produção não são iguais

Em desenvolvimento, é comum montar o código como volume e executar o Uvicorn
com `--reload`, permitindo que alterações sejam refletidas automaticamente.
Em produção, o código deve fazer parte da imagem e o modo de recarga não deve
ser usado.

O projeto ainda não definiu se terá arquivos Docker separados para produção.
Essa escolha permanece uma **decisão pendente** e exige aprovação do time antes
de virar configuração oficial.

A containerização do frontend também deve esperar a estrutura real do projeto
Next.js. Dependendo da decisão futura, ele poderá executar com runtime Node ou
ser exportado como site estático.

## 9. Segurança e boas práticas

- Use imagens oficiais e versões explícitas.
- Prefira imagens `slim` quando as dependências forem compatíveis.
- Nunca escreva senhas, tokens ou chaves no Dockerfile ou no Compose.
- Não copie `.env`, `.git` ou ambientes virtuais para a imagem.
- Instale dependências a partir de um manifesto versionado.
- Mantenha um serviço principal por container.
- Não trate `EXPOSE` como publicação de porta: quem publica é `ports` ou a opção
  `-p` de `docker run`.
- Antes de compartilhar uma imagem, confira suas camadas e seu conteúdo para
  garantir que nenhum segredo foi incluído.

## 10. Diagnóstico de problemas comuns

| Sintoma | Verificação provável |
|---|---|
| API não abre no navegador | Confirmar `ports`, `0.0.0.0` no Uvicorn e logs do backend |
| Backend não encontra o banco | Usar o host `db`, validar `DATABASE_URL` e a prontidão do PostgreSQL |
| Alteração de código não aparece | Reconstruir a imagem ou configurar volume e `--reload` em desenvolvimento |
| Dependência Python não existe | Confirmar se está declarada em `backend/requirements.txt` e reconstruir |
| Porta já está em uso | Encerrar o processo conflitante ou alterar apenas a porta do lado do host |
| Dados do banco sumiram | Confirmar se o volume está declarado e se não foi removido com `--volumes` |

Comandos úteis para investigação:

```bash
docker compose logs backend
docker compose config
docker compose exec backend sh
docker image history NOME_DA_IMAGEM
```

## 11. Exercício prático sugerido

1. Instale Docker Desktop ou Docker Engine e valide com `docker version`.
2. Crie, em uma branch de trabalho, o `backend/Dockerfile` e o
   `.dockerignore` com base nos exemplos.
3. Construa somente a API e verifique se `GET /health` responde com
   `{"status":"ok"}`.
4. Adicione o PostgreSQL ao Compose e observe a comunicação pelo hostname `db`.
5. Pare e recrie os containers para verificar a persistência do volume.
6. Inspecione a imagem e confirme que `.env` não foi copiado.

## 12. Critérios para considerar a containerização concluída

- `docker build` termina sem erros;
- `docker compose up` inicia todos os serviços sem reinicializações contínuas;
- `http://localhost:8000/health` responde corretamente;
- o backend alcança o PostgreSQL pelo nome do serviço;
- os dados persistem após recriar o container do banco;
- nenhum segredo aparece na imagem ou em seu histórico;
- `.env` não existe dentro da imagem;
- o README explica como iniciar o ambiente com um único comando.

## 13. Referências para aprofundamento

- [Docker — visão geral](https://docs.docker.com/get-started/docker-overview/)
- [Dockerfile — referência](https://docs.docker.com/reference/dockerfile/)
- [Docker Compose — documentação](https://docs.docker.com/compose/)
- [Boas práticas para Dockerfiles](https://docs.docker.com/build/building/best-practices/)
