# Lint e verificação de tipos — Issue #189

**Data:** 04/11/2026. **Origem:** [issue #189](https://github.com/unb-mds/2026-02-UnDb/issues/189).
**Base:** `origin/develop`, commit `af61ba072394fb66c2b82c933d74a0efa2051e03`.
**Branch local:** `chore/189-lint-verificacao-tipos`.

## Alteração e escopo

- Backend: Ruff `0.17.3`, fixado em `backend/requirements-dev.txt` e exigido por
  `backend/pyproject.toml`. Alvo Python 3.12, largura de 100 caracteres e regras
  `E4`, `E7`, `E9`, `F`. Os defaults de exclusão de ambientes, caches, dependências
  e builds foram preservados, com exclusão adicional explícita de `__pycache__`.
  Todo o Python do backend é elegível, incluindo `app`, `tests`, migrações Alembic
  e os scripts na raiz. Não há exclusão de código para contornar apontamentos.
- Frontend: ESLint/configuração existentes preservados; script `npm run typecheck`
  executa `next typegen && tsc --noEmit`, com o `tsconfig.json` estrito existente.
  Nenhuma biblioteca nova ou alteração de lockfile é necessária para esse script.
- CI: o job `Backend` instala também `requirements-dev.txt`, considera os dois
  arquivos de dependências no cache e executa lint/formatação antes dos testes.
  O job `Frontend` executa `typecheck` depois de ESLint e antes dos testes/build.
  Os eventos existentes de PR para `develop` e `main` foram preservados.
  Os comandos retornam falha e não corrigem arquivos no CI.
- Documentação: comandos de instalação, verificação e correção no guia de
  contribuição; entradas nos README principal/frontend e na navegação do MkDocs.

A imagem de execução permanece instalando apenas `backend/requirements.txt`.
Não foram alterados Rulesets, requisitos, política de cobertura ou frameworks de teste.
A medição de cobertura pertence à #190 e é independente desta entrega.

## Apontamentos existentes e preservação de comportamento

A inspeção inicial encontrou três apontamentos do Ruff:

| Apontamento | Tratamento |
|---|---|
| `E731`, atribuição de lambda em `app/commands/importar_sigaa_agendado.py` | Função local equivalente mantém a coleta adiada e a sessão usada pela importação |
| `F401`, import de `listar_unidades` em `pegar_id.py` | Exportação pública tornada explícita com `as listar_unidades`; preserva os consumidores e testes do parser |
| `E702`, duas instruções em uma linha em `tests/integration_avaliacao.py` | Instruções separadas, mantendo o mesmo fluxo |

Também foi aplicada a formatação necessária para adoção do check, incluindo
migrações e testes. A comparação de AST com a base confirmou equivalência de todos
os arquivos Python modificados, exceto os dois ajustes explícitos de função/import
descritos acima. Não houve mudança de SQL, modelo de dados ou regras de negócio.

A primeira execução da suíte identificou que remover o import considerado não usado
quebrava `test_sigaa_poc_unittest`, que importa o parser de `pegar_id`. A exportação
foi restaurada explicitamente e a suíte completa foi reexecutada com sucesso.

## Evidências locais

Backend verificado em container descartável `python:3.12-slim`, com o diretório
`backend` montado somente para leitura, dependências instaladas pelos dois arquivos
de requirements e variáveis de teste: SQLite em memória, segredo fictício,
`DEBUG=False` e `EMAIL_BACKEND=console`. Nenhum banco real foi alterado.

Frontend verificado no Windows com Node.js `24.18.0` e npm `11.16.0`; o CI usa
Node.js 22. As versões instaladas de Next.js `16.3.5`, ESLint `9.39.5` e TypeScript
`5.9.3` foram conferidas contra o lockfile. O venv local usa Python `3.14.6`;
os checks Ruff também foram executados nesse ambiente.

| Verificação | Resultado |
|---|---|
| `python -m ruff check .`, dentro de `backend/`, Python 3.12 | Aprovado |
| `python -m ruff format --check .`, dentro de `backend/`, Python 3.12 | Aprovado |
| `python -m unittest discover -s tests -q`, Python 3.12 | 159 testes aprovados |
| `python -m compileall -q app alembic tests`, no backend local | Aprovado |
| `npm run lint`, no frontend | Aprovado, sem mudança de configuração ESLint |
| `npm run typecheck`, no frontend | Aprovado |
| `npm test`, no frontend | 61 testes aprovados |
| `npm run typecheck` em cópia temporária dos arquivos versionados, sem `.next` nem `next-env.d.ts` prévios | Aprovado; tipos gerados antes da checagem, usando as dependências existentes por junction |
| Erro TypeScript intencional apenas nessa cópia temporária | `TS2322` rejeitado com status não zero; arquivo de sondagem removido |
| Import não usado e formatação inválida fornecidos ao Ruff por stdin, sem criar arquivos no projeto | Ambos rejeitados com status 1 |
| `venv/Scripts/python.exe -m mkdocs build --strict --site-dir site` | Aprovado; páginas antigas fora do `nav` listadas apenas como informação |
| `git diff --check` | Aprovado |

Os comandos do container usaram `--no-cache` no Ruff por causa da montagem somente
para leitura e `--quiet` no formatter para reduzir a saída; essas opções não
enfraquecem os checks. O CI preserva a saída padrão e o unittest verboso.

Comandos locais reproduzíveis estão no
[guia de contribuição](https://github.com/unb-mds/2026-02-UnDb/blob/develop/CONTRIBUTING.md#verificações-de-qualidade-locais).
O script TypeScript segue a geração de tipos descrita no guia incluído no pacote
Next.js instalado (`node_modules/next/dist/docs/01-app/03-api-reference/06-cli/next.md`).
Referências externas: [configuração do Ruff](https://docs.astral.sh/ruff/configuration/)
e [next typegen](https://nextjs.org/docs/app/api-reference/cli/next#next-typegen-options).

## Limites e continuidade

Os checks remotos de PR ainda não foram executados por esta entrega local. Os jobs
existentes de migração/PostgreSQL, Docker e navegador foram preservados; suas
integrações reais não foram reexecutadas localmente nesta atividade. Os testes
determinísticos e a comparação de AST não substituem essas verificações.

A configuração não torna novos checks obrigatórios em Rulesets nem promove uma
proposta de ADR. Na publicação autorizada do PR, vincular #189 e acrescentar os
resultados dos checks remotos. A #188 pode ser integrada separadamente.
