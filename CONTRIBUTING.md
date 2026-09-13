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

- PRs para `develop`: somente `feature/*`, `fix/*`, `chore/*`, `docs/*`,
  `release/*` ou `hotfix/*`.
- PRs para `main`: somente `release/*` ou `hotfix/*`.
- PRs de `release/*` e `hotfix/*` integrados em `main` também devem voltar para
  `develop`, evitando divergência entre as branches permanentes.
- Os checks `Gitflow policy` e `Backend` devem passar.
- É necessária pelo menos uma aprovação humana e a aprovação é descartada quando
  novos commits alteram o PR.
- Conversas pendentes bloqueiam o merge.

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
