# ADR 09 — Estratégia de qualidade: lint, testes e cobertura

| Campo | Valor |
|---|---|
| Estado | `Proposed` — registro para revisão; não constitui aprovação de política nova |
| Data de preparação | 2026-11-04 |
| Responsável pela entrega | Gabriel (@gabrielrdaraujo), conforme #188 |
| Origem | [#188](https://github.com/unb-mds/2026-02-UnDb/issues/188), [#189](https://github.com/unb-mds/2026-02-UnDb/issues/189) e [#190](https://github.com/unb-mds/2026-02-UnDb/issues/190) |
| Base inspecionada | `develop`, commit `af61ba072394fb66c2b82c933d74a0efa2051e03` |
| Aprovação | Preparação documental solicitada na #188; aprovação deste ADR como decisão permanente ainda não registrada |
| Substitui / substituído por | Nenhum |

## Contexto e origem do escopo

A #188 solicita registrar a estratégia de qualidade discutida pelo PO, aproveitando
o código e o GitHub Actions atuais. As #189 e #190 detalham as entregas de análise
estática e cobertura. As três issues registram autorização de Nicolas em 28/10/2026
para criação, atribuição e escolha da sprint. Essa origem autoriza os trabalhos
descritos; não representa aprovação de percentual mínimo ou mudança adicional de política.

O objetivo é tornar verificações reproduzíveis e expor lacunas de teste sem confundir
quantidade de código executado com correção funcional. Os comportamentos esperados
continuam nos [requisitos](../requisitos.md), e a atividade de verificação segue a
[skill testing](https://github.com/unb-mds/2026-02-UnDb/blob/develop/skills/engineering/testing/SKILL.md).

## Configuração observada na base

Esta inspeção é uma fotografia do commit acima, não evidência de execução das suítes
nem de sucesso dos checks remotos.

| Área | Implementado na base | Entrega ainda prevista |
|---|---|---|
| Backend | Python 3.12 no CI; `unittest`; compilação de `app` e `alembic`; importação da aplicação; migrações, consistência de modelos e dados legados em PostgreSQL 16 descartável; build da imagem | Ruff e dependência de desenvolvimento reproduzível (#189); coverage.py e relatórios (#190) |
| Frontend | ESLint com presets Next.js/TypeScript; `npm test` usa TypeScript instalado e runner nativo Node; build Next.js; testes em Edge/Chromium | Script explícito de `tsc --noEmit` (#189); medição, sourcemaps e relatórios de cobertura (#190) |
| Integração | Jobs de Compose, avaliação/acesso e moderação com PostgreSQL e navegador; testes de navegador com HTTP controlado no job Frontend | Manter essas verificações; cobertura não substitui integração real nem validação funcional |
| Documentação | MkDocs Material e build estrito no workflow de documentação | Template, catálogo e este registro (#188) |

O runner `frontend/tests/run-tests.mjs` compila uma lista explícita de módulos de
`src/lib` (formulário, busca, serviços, comentários, denúncias e moderação) em diretório
temporário, executa seis arquivos de teste Node e remove a compilação em `finally`.
Isso não mede todos os componentes, páginas ou Server Components. Compilação dessa
lista e build Next.js também não equivalem ao script de tipagem explícito da #189.

O workflow `pull-request.yml` executa em PRs para `develop` e `main`, usando Python
3.12 e Node 22. Seus jobs incluem `Gitflow policy`, `Backend`, `Docker Compose`,
`Evaluation end to end (PostgreSQL)`, `Moderation end to end (PostgreSQL)` e `Frontend`.
O workflow `pages.yml` executa `Build documentation` em PRs que alteram seus caminhos
de documentação/configuração e publica o site somente a partir de `main`.
Execução de um job e obrigatoriedade de um status check são coisas distintas:
`CONTRIBUTING.md` descreve `Gitflow policy` e `Backend` como obrigatórios; os Rulesets
remotos não foram inspecionados nesta entrega.

## Alternativas consideradas

| Alternativa | Benefícios | Custos, riscos e limites |
|---|---|---|
| Aproveitar ESLint, unittest e runner Node, acrescentando Ruff, tipagem e cobertura nas #189/#190 | Preserva as suítes e concentra o esforço nas lacunas atuais | Exige definir escopo instrumentável e integrar relatórios antes da limpeza temporária |
| Migrar para pytest, Jest ou Vitest agora | Permitiria adotar outros recursos desses ecossistemas | Migração fora do escopo; não é necessária para medir as suítes existentes |
| Usar SonarQube ou serviço externo de cobertura | Centralizaria análises em outro serviço | Acrescenta infraestrutura e operação; explicitamente fora do escopo solicitado |
| Bloquear PRs por um percentual mínimo desde já | Criaria um critério numérico de integração | Não há linha de base nem meta aprovada; estabeleceria política por suposição |

## Decisão proposta e trabalhos autorizados

Consolidar o escopo solicitado nas issues, preservando as ferramentas existentes:

- **Análise estática (#189):** manter ESLint; acrescentar Ruff para Python 3.12,
  com `ruff check` e `ruff format --check`; disponibilizar script explícito baseado
  em `tsc --noEmit`. Fixar ferramentas de forma reproduzível, documentar escopo e
  exclusões e corrigir os apontamentos necessários sem mudar regras de negócio.
  Falhas de lint, formatação e tipos devem fazer seus checks falharem, sem correção
  automática no CI. Nenhuma dessas adições é implementada pela #188.
- **Testes:** preservar `unittest`, runner Node e verificações de integração existentes.
  Relacionar testes e lacunas selecionadas a requisitos autorizados; respostas HTTP
  controladas e SQLite em testes locais não comprovam integração com PostgreSQL.
  O acesso real ao SIGAA continua sendo verificação manual, sem tornar os testes
  determinísticos dependentes da disponibilidade externa.
- **Cobertura (#190):** usar coverage.py sobre `backend/app`, com linhas e ramificações,
  gerando terminal, HTML e XML. Avaliar c8 como primeira opção no frontend, mantendo
  o runner nativo e gerando terminal, HTML e LCOV com caminhos dos TypeScript originais.
  A adequação do c8 e os ajustes do runner devem ser validados nessa entrega, não
  são resultados já comprovados por este registro.
- **Denominador e limites (#190):** incluir fontes de aplicação elegíveis mesmo não
  executadas; excluir dependências, testes, builds e gerados com justificativa.
  Gerar relatórios antes de apagar a compilação temporária e validar sourcemaps.
  Explicitar limites de UI, navegador e Server Components: cobertura de utilitários
  não deve ser apresentada como cobertura completa da interface.
- **CI e linha de base (#190):** publicar artefatos identificados de backend e frontend
  no GitHub Actions, preservando a falha do check quando testes falharem. Registrar
  commit, versões, comandos, totais e principais lacunas; acrescentar testes de
  comportamento relevantes para lacunas selecionadas. Documentar como localizar
  os artefatos na execução do workflow. Nomes e caminhos finais pertencem à #190.

## Execução local e no CI

**Disponível na base inspecionada**, em ambiente isolado de desenvolvimento/teste:

```bash
# Na raiz; Python 3.12 é a versão de referência do CI.
python -m pip install -r backend/requirements.txt
cd backend
python -m compileall -q app alembic
python -m unittest discover -s tests -v
```

As suítes determinísticas utilizam fixtures e configuração de teste. Não aponte
verificações de integração/migração para banco com dados reais. Para os testes reais
com PostgreSQL, sessões, navegador e respectivas variáveis, consulte os comandos do
workflow e os relatórios de [acesso](../estudos/verificacao-acesso-avaliacao-issue-158.md)
e [moderação](../estudos/validacao-integrada-issue-163.md).

```bash
# A partir da raiz; Node 22 corresponde ao CI.
cd frontend
npm ci
npm run lint
npm test
npm run build
# Após o build, com Edge/Chromium disponível (BROWSER_PATH quando necessário):
npm run test:browser
```

O build requer internet para dependências/fontes. `test:browser` usa HTTP controlado
e não comprova persistência; os jobs de integração real são verificações separadas.
Pré-requisitos de navegador e portas estão no
[README do frontend](https://github.com/unb-mds/2026-02-UnDb/blob/develop/frontend/README.md).

**Planejado nas #189/#190**, ainda sem instalação/scripts de suporte nesta base:

| Entrega | Comandos ou resultado esperado | Local / integração |
|---|---|---|
| Ruff (#189) | `ruff check` e `ruff format --check`, no escopo documentado pela entrega | Backend; acrescentar ao workflow de PR |
| TypeScript (#189) | Script npm baseado em `tsc --noEmit`; nome final a documentar | Frontend; acrescentar ao workflow de PR |
| coverage.py (#190) | `coverage run --branch --source=app -m unittest discover -s tests -v`, `coverage report`, `coverage html`, `coverage xml` | Dentro de `backend/`; publicar relatórios no CI |
| Frontend (#190) | Instrumentação a validar com c8, sourcemaps e fontes elegíveis; resumo, HTML e LCOV | Runner Node existente; comando final e artefatos a documentar |

Não há comando de cobertura frontend validado nem percentual medido a registrar
nesta entrega documental. Após #189/#190, atualizar este ADR com os comandos,
dependências fixadas e evidências efetivas, sem alterar seu estado de aprovação por
consequência automática da implementação.

## Justificativa

ESLint já está integrado ao frontend; preservá-lo evita duplicação. Ruff atende à
lacuna de lint/formatação Python descrita na #189. A verificação explícita de tipos
torna sua reprodução independente de executar o build. coverage.py mede o backend
com o `unittest` atual; c8 é a primeira opção a avaliar para o runner Node sem exigir
migração de framework. Artefatos do Actions mantêm os relatórios junto à execução e
ao commit medido, sem contratar serviço externo.

## Consequências

O time passa a encontrar num único registro o estado observado e as entregas de
qualidade planejadas. #189/#190 precisarão coordenar edições no mesmo workflow,
custos de instalação/execução e caminhos dos relatórios. A linha de base pode revelar
baixa cobertura ou áreas não instrumentáveis; isso é diagnóstico para selecionar
testes relevantes, não autorização para excluir código ou enfraquecer regras.

## Pendências e limites de aprovação

- **`Pending Decision`:** percentual mínimo, bloqueio por queda de cobertura e qualquer
  meta futura dependem de avaliação humana. Nenhum gate numérico é ativado nesta entrega.
- **`Pending Decision`:** alterações adicionais de política, Definition of Done/Ready
  ou obrigatoriedade de novos checks em Rulesets exigem decisão própria. Este ADR não
  altera as regras de contribuição nem configura proteções remotas.
- **`Proposed`:** este registro consolidado aguarda revisão/aprovação como decisão
  permanente, com responsável, data e referência. As autorizações de escopo das
  issues não são uma aprovação presumida de pontos pendentes.
- **Fora do escopo:** SonarQube, serviço externo de cobertura, migração de frameworks,
  hospedagem e garantia de cobertura integral de todos os fluxos.

## Evidências e referências

- Configuração inspecionada: [workflow de PR](https://github.com/unb-mds/2026-02-UnDb/blob/af61ba072394fb66c2b82c933d74a0efa2051e03/.github/workflows/pull-request.yml),
  [workflow de documentação](https://github.com/unb-mds/2026-02-UnDb/blob/af61ba072394fb66c2b82c933d74a0efa2051e03/.github/workflows/pages.yml),
  [dependências Python](https://github.com/unb-mds/2026-02-UnDb/blob/af61ba072394fb66c2b82c933d74a0efa2051e03/backend/requirements.txt),
  [scripts npm](https://github.com/unb-mds/2026-02-UnDb/blob/af61ba072394fb66c2b82c933d74a0efa2051e03/frontend/package.json),
  [runner Node](https://github.com/unb-mds/2026-02-UnDb/blob/af61ba072394fb66c2b82c933d74a0efa2051e03/frontend/tests/run-tests.mjs),
  [ESLint](https://github.com/unb-mds/2026-02-UnDb/blob/af61ba072394fb66c2b82c933d74a0efa2051e03/frontend/eslint.config.mjs)
  e [TypeScript](https://github.com/unb-mds/2026-02-UnDb/blob/af61ba072394fb66c2b82c933d74a0efa2051e03/frontend/tsconfig.json).
- Autoridade e limites: [governança do projeto](https://github.com/unb-mds/2026-02-UnDb/blob/develop/skills/governance/project-governance/SKILL.md)
  e [limites de aprovação humana](https://github.com/unb-mds/2026-02-UnDb/blob/develop/skills/governance/project-governance/references/HUMAN_APPROVAL_BOUNDARIES.md).
- [Guia e catálogo de ADRs](index.md) e [ADRs anteriores](../arquitetura.md#7-decisoes-arquiteturais-adrs).

### Verificação documental da #188

Verificação local em 04/11/2026, sobre a base indicada e as alterações documentais
desta entrega, no Windows, com Python 3.14.6, MkDocs 1.6.1 e Material 9.7.7 do `venv`
existente. O CI usa Python 3.12; esse ambiente remoto não foi executado nesta atividade.

| Verificação | Resultado |
|---|---|
| `venv/Scripts/python.exe -m mkdocs build --strict --site-dir site` | Aprovado; site gerado. As páginas antigas fora do `nav` foram listadas como informação pelo MkDocs |
| Links locais e âncoras no HTML das três páginas de ADRs e de Arquitetura, incluindo a navegação | Destinos existentes e âncoras válidas, conferidos com parser HTML |
| Comparação dos blocos ADR 01–08 com `HEAD:docs/arquitetura.md` da base | Conteúdo integralmente preservado, do título do ADR 01 até a seção de riscos |
| `git diff --check` e verificação de espaços finais nos novos Markdown | Aprovados |

Os comandos de lint, testes e cobertura descritos neste ADR não foram executados
como parte da #188. Não se infere resultado funcional ou cobertura a partir do
build documental. Evidências de CI e vínculo do PR devem ser acrescentados quando
a publicação da entrega for autorizada.

## Histórico

| Data | Alteração | Referência |
|---|---|---|
| 2026-11-04 | Registro inicial proposto, baseado na inspeção do commit indicado; sem execução das suítes de aplicação nem medição de cobertura | #188; implementações de qualidade nas #189/#190 |
