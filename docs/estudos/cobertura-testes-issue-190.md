# Cobertura de testes — Issue #190

## Execução local

No backend, use um ambiente virtual com Python 3.12, como no CI. Execute em
`backend/` com uma configuração de teste. Para a suíte determinística, as fixtures
criam seus próprios bancos SQLite em memória. A configuração abaixo evita usar
o banco ou o segredo do ambiente de desenvolvimento.

```bash
cd backend
python -m pip install -r requirements.txt -r requirements-coverage.txt
export SECRET_KEY=ci-only-secret
export DEBUG=False
export DATABASE_URL=sqlite+pysqlite:///:memory:
python -m coverage run --branch --source=app -m unittest discover -s tests -v
python -m coverage report -m
python -m coverage html -d coverage/html
python -m coverage xml -o coverage/coverage.xml
```

No PowerShell, configure as mesmas variáveis com `$env:SECRET_KEY = 'ci-only-secret'`,
`$env:DEBUG = 'False'` e `$env:DATABASE_URL = 'sqlite+pysqlite:///:memory:'`.
Abra `backend/coverage/html/index.html` para ver as linhas e ramificações por arquivo.

No frontend, use Node.js 22 (22.12 ou superior) e npm. Execute os comandos abaixo
a partir da raiz do repositório.

```bash
cd frontend
npm ci
npm run test:coverage
```

O resumo aparece no terminal. Os relatórios ficam em `frontend/coverage/index.html`
e `frontend/coverage/lcov.info`. `npm test` usa a mesma suíte sem instrumentação.
O coverage.py está fixado em `requirements-coverage.txt` e o c8 e suas dependências
estão fixados no lockfile do frontend.

## Escopo dos relatórios

- **Backend.** O `unittest discover` mede linhas e ramificações em `backend/app`,
  incluindo módulos sem execução, como os comandos administrativos. Testes,
  migrações Alembic, scripts fora de `app` e dependências ficam fora desse escopo.
  Os jobs separados de PostgreSQL, Docker Compose e navegador verificam fluxos
  adicionais. Sua execução fica fora da medição desta suíte.
- **Frontend.** O c8 coleta dados do V8 enquanto `node --test` executa os testes
  existentes. `next typegen` fornece os tipos de rota usados na compilação.
  O TypeScript emite `src/**/*.ts` e `src/**/*.tsx` com sourcemaps inline em um
  diretório temporário. O c8 usa `--all` sobre essa emissão para incluir fontes
  não carregadas, remapeia o relatório para os arquivos originais e conclui antes
  da limpeza. Declarações `.d.ts`, testes, dependências, builds do Next.js e
  outros arquivos gerados ficam fora do relatório.
- **Limites no frontend.** Páginas, componentes, hooks e protótipos em `src`
  entram na medição. A suíte Node exercita principalmente lógica e clientes HTTP
  com respostas simuladas. Ela não mede a execução dos Server Components no Next.js
  nem os fluxos no navegador. As linhas de módulos não carregados entram com zero
  acertos. Nesses arquivos, os registros sintéticos do c8 para funções e ramificações
  não enumeram todos os caminhos reais. Por isso, o percentual de ramificações do
  c8 deve ser lido junto com a cobertura de linhas e com o relatório por arquivo.

## Artefatos no GitHub Actions

Na aba **Checks** do PR para `develop` ou `main`, abra a execução do workflow
**Pull request checks**. Os jobs **Backend** e **Frontend** mostram os resumos
no log. Na página **Summary** da execução, baixe e extraia `backend-coverage`
ou `frontend-coverage` em **Artifacts**. Abra `html/index.html` no primeiro e
`index.html` no segundo. Os mesmos pacotes incluem `coverage.xml` e `lcov.info`,
respectivamente.

Falhas de teste continuam falhando o job. O workflow tenta publicar os relatórios
gerados em execuções com falhas. A porcentagem é informativa e não há limiar de
cobertura nem comparação obrigatória com execuções anteriores.

## Linha de base local

Código de aplicação e suítes iniciais do commit
`af61ba072394fb66c2b82c933d74a0efa2051e03` de `develop`, medidos com a instrumentação
desta entrega em 05/11/2026. A coluna final mede o mesmo código de aplicação com os
quatro testes adicionados nesta issue. Os comandos são os da seção de execução local.

Ambiente local Windows com Python 3.14.6, coverage.py 7.12.0 e SQLite no backend,
e Node.js 22.23.4, TypeScript 5.9.3 e c8 12.0.0 no frontend.

| Medição | Suítes do commit-base | Com os testes da #190 |
| --- | ---: | ---: |
| Backend, testes aprovados | 159 | 161 |
| Backend, linhas | 1.696/1.930 (87,88%) | 1.714/1.930 (88,81%) |
| Backend, ramificações | 245/324 (75,62%) | 249/324 (76,85%) |
| Frontend, testes aprovados | 61 | 63 |
| Frontend, linhas | 931/3.995 (23,30%) | 933/3.995 (23,35%) |
| Frontend, ramificações observadas pelo c8 | 256/318 (80,50%) | 258/319 (80,87%) |
| Frontend, funções observadas pelo c8 | 68/128 (53,12%) | 68/128 (53,12%) |

O XML contém os 67 arquivos Python de `app`. O LCOV aponta para os 65 arquivos
TypeScript e TSX originais em `src`, incluindo fontes zeradas como `src/app/layout.tsx`
e `src/lib/hooks/useDebouncedValue.ts`.

### Lacunas medidas e testes acrescentados

| Lacuna na linha de base | Verificação acrescentada | Fonte |
| --- | --- | --- |
| Detalhe e histórico de moderação fora da suíte determinística | `test_moderacao.py` verifica acesso à identidade interna e ao histórico por moderadores, rejeição de visitantes e contas comuns e resposta para versão inexistente. | [AC22-04 e AC22-05](../requisitos.md), [contrato das APIs](alinhamento-denuncias-issues-160-161.md) |
| Validação de itens inválidos na consulta pública de comentários | `comentarios.test.mjs` verifica que a consulta remove campos privados e rejeita uma lista com item sem texto publicável. | [AC20-03](../requisitos.md) |

Entre as lacunas restantes estão os comandos de administração e descarte de moderação,
partes do cliente de e-mail e do acesso ao SIGAA no backend, e a execução de páginas,
componentes e hooks no frontend.
