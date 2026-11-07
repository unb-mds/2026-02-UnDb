# Guia de contribuição

Este projeto usa Gitflow. Todo trabalho deve estar associado a uma Issue e entrar
por Pull Request (PR). Push direto e force-push nas branches permanentes não fazem
parte do fluxo.

## Branches

- `main`: histórico de releases. Recebe somente `release/*` e `hotfix/*`.
- `develop`: integração da próxima release. Recebe `feature/*`, `fix/*`, `chore/*`
  e `docs/*`.
- `feature/<issue>-<descricao>`: funcionalidade ou tarefa da sprint.
- `fix/<issue>-<descricao>`: correção destinada à próxima release.
- `release/<versao>`: estabilização de uma release; nasce de `develop` e termina
  em `main` e `develop`.
- `hotfix/<versao-ou-issue>`: correção urgente; nasce de `main` e termina em
  `main` e `develop`.

Use nomes em minúsculas, sem espaços e separados por hífen. Exemplos:
`feature/42-login-institucional` e `release/1.0.0`.

## Fluxo de trabalho

1. Atualize a branch-base correta.
2. Crie a branch de trabalho conforme as regras acima.
3. Faça commits pequenos e descritivos.
4. Abra um PR, vincule a Issue com `Closes #<número>` e preencha o checklist.
5. Aguarde os checks obrigatórios e pelo menos uma aprovação de alguém que não
   seja o autor.
6. Resolva todas as conversas antes do merge.
7. O merge é uma ação humana e deve respeitar as proteções configuradas no GitHub.

Fluxos usuais:

```bash
# Nova funcionalidade
git switch develop
git pull --ff-only
git switch -c feature/42-login-institucional

# Preparar release
git switch develop
git switch -c release/1.0.0

# Correção urgente em produção
git switch main
git pull --ff-only
git switch -c hotfix/1.0.1
```

## Política de Pull Request

Para registrar uma decisão técnica, consulte o
[catálogo e guia de ADRs](docs/adrs/index.md) e use o
[template versionado](docs/adrs/template.md). Preserve evidências e estados de
aprovação dos registros existentes. A estratégia de lint, testes e cobertura está
preparada no [ADR 09](docs/adrs/09-estrategia-qualidade.md), que distingue configuração
observada, entregas planejadas e decisões pendentes de aprovação.

- PRs para `develop`: somente `feature/*`, `fix/*`, `chore/*`, `docs/*`,
  `release/*` ou `hotfix/*`.
- PRs para `main`: somente `release/*` ou `hotfix/*`.
- PRs de `release/*` e `hotfix/*` integrados em `main` também devem voltar para
  `develop`, evitando divergência entre as branches permanentes.
- Os checks `Gitflow policy` e `Backend` devem passar.
- É necessária pelo menos uma aprovação humana e a aprovação é descartada quando
  novos commits alteram o PR.
- Conversas pendentes bloqueiam o merge.

## Verificações de qualidade locais

Use Python 3.12 em ambiente virtual e Node.js 22 com npm, como no CI.
Na raiz do repositório, instale as ferramentas de desenvolvimento separadas das
dependências de execução:

```bash
cd backend
python -m pip install -r requirements.txt -r requirements-dev.txt
python -m ruff check .
python -m ruff format --check .
```

O Ruff está fixado em `requirements-dev.txt` e em `pyproject.toml`, com alvo Python
3.12 e largura de 100 caracteres. As regras iniciais são `E4`, `E7`, `E9` e `F`
(erros de importação/sintaxe e Pyflakes); a formatação fica com `ruff format`.
O escopo é todo o Python do backend: aplicação, testes, migrações Alembic e scripts
na raiz. As exclusões padrão do Ruff preservam ambientes virtuais, dependências,
caches e builds; `__pycache__` é explicitamente excluído. O `.gitignore` também é
respeitado. Migrações versionadas e testes não são excluídos; `script.py.mako` é
um template, não um arquivo Python a ser analisado diretamente.

Para corrigir localmente, execute `python -m ruff check --fix .` e
`python -m ruff format .`, depois revise o diff e rode os checks novamente.
Correções que não forem automáticas precisam ser avaliadas sem alterar regras de negócio.
A imagem de execução continua instalando apenas `requirements.txt`.

No frontend, a partir da raiz:

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
```

O ESLint existente é preservado; `npm run lint -- --fix` aplica suas correções
locais disponíveis. `npm run typecheck` executa `next typegen && tsc --noEmit`,
gerando primeiro os tipos de rotas e `next-env.d.ts`. Funciona sem build prévio e
mantém o `tsconfig.json` estrito, sem emitir JavaScript. Tipos gerados e caches
continuam ignorados pelo Git. Erros de tipo precisam ser corrigidos no código.
Use `npm ci` com o `package-lock.json` versionado para reproduzir as dependências.

Em PRs para `develop` e `main`, o job `Backend` executa lint e formatação antes
dos testes; `Frontend` executa ESLint e a verificação explícita de tipos antes dos
testes/build. Falhas interrompem seus checks; o CI não executa correções automáticas.
Não há alteração de Rulesets, Definition of Done/Ready ou meta de cobertura.
As [evidências da #189](docs/estudos/verificacao-lint-tipos-issue-189.md) registram
ambientes, comandos, resultados e limites da validação.

## Proteções no GitHub

Configure Rulesets para `main` e `develop` com:

- exigir Pull Request antes do merge;
- exigir 1 aprovação e descartar aprovações obsoletas;
- exigir resolução de todas as conversas;
- exigir os status checks `Gitflow policy` e `Backend` atualizados com a branch;
- bloquear force-push e exclusão;
- impedir bypass, exceto para administradores em situações de recuperação;
- restringir criação e atualização das branches permanentes ao fluxo de PR.

A configuração remota deve ser feita por alguém com permissão administrativa no
repositório. Os arquivos deste repositório validam o fluxo, mas não substituem os
Rulesets do GitHub.

### Ordem de ativação inicial

1. Crie `develop` no GitHub a partir do estado atual de `main`.
2. Integre estes arquivos em `develop` por PR e confirme os dois checks.
3. Crie os Rulesets de `main` e `develop`, usando os nomes exatos dos checks.
4. Faça a primeira promoção para `main` por uma branch `release/*`.

Essa ordem evita bloquear o repositório antes de a branch de integração e os
checks obrigatórios existirem.
