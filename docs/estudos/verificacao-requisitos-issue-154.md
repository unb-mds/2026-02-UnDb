# Verificação documental de RF20–RF22 — Issue #154

Documento de evidência e entrega, derivado de [`requisitos.md`](../requisitos.md).
Relaciona o detalhamento à [Issue #154](https://github.com/unb-mds/2026-02-UnDb/issues/154)
e à [Epic #145](https://github.com/unb-mds/2026-02-UnDb/issues/145).
Não representa implementação de comentários, denúncias ou moderação na aplicação.

## Origem e sequência do trabalho

Foram consultadas as descrições completas da issue e da epic, as issues dependentes
#156/#159/#160/#161/#162/#163, requisitos, `specs.md`, arquitetura, visão, planejamento
da R2 e os achados AMB-002/003/004 da auditoria #149. O arquivo `docs/specs.md` não
existe neste repositório; o derivado efetivo é `specs.md`, na raiz.

As decisões de produto foram perguntadas em blocos, sem edição permanente dos documentos
durante o esclarecimento. A origem das regras aprovadas são as respostas explícitas do
solicitante às perguntas 1–27 desta sessão. O registro na seção 11 dos requisitos agrupa
essas respostas em R2-DEC-01 a R2-DEC-15, distinguindo aprovação, pendência, sugestão não
adotada e fora de escopo. Não se atribuiu a decisão a um PO nominal não identificado
nesta sessão nem se afirmou publicação das respostas como comentários no GitHub.

O checkout inicial estava limpo na branch da #152. Após atualizar a referência remota,
a branch `docs/154-comentarios-denuncia-moderacao` foi criada a partir de `origin/develop`
no commit `2cdc0aa` (que já incluía a PR #179). Não foram incluídas alterações locais
preexistentes nem modificações de código. Primeiro foi alterado e registrado
`docs/requisitos.md`; só depois foram sincronizados os derivados.

## Resultado do detalhamento

| Requisito | Regras documentadas |
|---|---|
| RF20 | Comentário opcional da avaliação única, 1–500 caracteres, autoria pública anônima, leitura pública, moderação humana prévia e nova revisão de substitutos |
| RF21 | Denúncia apenas do texto por conta confirmada ou não e visitante; motivo fechado; duplicidade de autenticados; origens separadas; suspensão por 50 contas distintas com denúncia aberta da versão |
| RF22 | Moderador designado pelo PO, impedimento de julgar caso próprio, aprovação/rejeição, manutenção/remoção e restauração de suspensos; registros privados e retenção limitada |

Também foram explicitados: estados por versão; preservação do texto aprovado durante a
análise do substituto sem contornar suspensão; retirada pelo autor; encerramento de
denúncias sem transferir para nova versão; confirmação/agradecimento; caminhos de erro;
e 17 critérios de aceitação identificados como AC20-01 a AC22-06. Esses critérios são
cenários para verificação futura, não testes funcionais criados nesta issue.

Os cinco critérios continuam independentes da moderação do texto. Suas escalas,
agregação, transparência e mínimo de três avaliações (RNF02) não foram alterados.
RF14 foi contextualizado por release para permitir o complemento de RF20 na R2 sem
apagar a restrição de texto livre da R1. O schema e os contratos atuais continuam
descritos como R1, sem autorização automática de novas tabelas ou endpoints.

## Esclarecimentos que prevalecem sobre respostas anteriores

- A resposta 7 determina moderação exclusivamente humana enquanto a lista de termos
  não for definida, substituindo a exigência inicial de filtro automático da resposta 4.
- Na resposta 3, a descrição explícita de ausência de identificação pública prevalece
  sobre a numeração da opção; não foi autorizada exibição do nome do autor.
- A resposta 26 esclarece o agradecimento: conservar até primeira exibição e apagar
  depois, permitindo entrega no próximo acesso, em vez de descarte imediato.
- A resposta 27 aplica uma semana de retenção interna tanto à retirada pelo autor
  quanto à remoção pelo moderador. Texto temporariamente suspenso continua disponível
  para revisão, sem ser tratado como removido.
- O esclarecimento final exige nova auditoria/moderação para toda substituição do texto.
  A menção a IA não constitui ativação ou aprovação de um provedor nesta etapa.

## Documentos atualizados

- `docs/requisitos.md`: fonte canônica, atores, RF14 por release, RF20–RF22, estados,
  retenção, erros, aceitação, registro de decisões e rastreabilidade.
- `specs.md`: resumo derivado da R2, pendências técnicas e delimitação do modelo R1.
- `docs/arquitetura.md`: restrições de evolução recebidas dos requisitos, sem novo ADR
  ou modelo físico R2.
- `docs/visao.md`: síntese do escopo aprovado e das evoluções pendentes.
- `docs/estudos/auditoria-requisitos-issue-149.md`: nota de evolução, preservando o
  diagnóstico histórico e distinguindo suas sugestões das decisões posteriores.
- Este relatório: evidências, limites e proposta de PR.

## Validação executada

Foi usado um ambiente virtual temporário, sem alterar dependências do projeto:

```powershell
python -m venv .tmp/issue-154-docs-venv
.tmp/issue-154-docs-venv/Scripts/python.exe -m pip install -r requirements-docs.txt
.tmp/issue-154-docs-venv/Scripts/python.exe -m mkdocs build --strict --site-dir site
git diff --check
```

O build é o mesmo comando do workflow de documentação, executado pelo Python do
ambiente virtual. Ambiente local: Python 3.14.7, MkDocs 1.6.1 e Material 9.7.7,
compatíveis com `requirements-docs.txt`; o CI configura Python 3.12.

- Build MkDocs estrito: aprovado após a fonte e após a sincronização final; sem erro
  de links ou renderização. O site gerado fica em `site/`, excluído pelo Git.
- Verificação documental temporária com Python: 15 decisões e 17 critérios de aceitação
  únicos; todas as referências desses critérios resolvem para decisões existentes; os
  quatro derivados citam a fonte e o registro de decisões.
- Comparação documental com `origin/develop`: seções de escalas, RNFs e restrições
  de produto preservadas, assim como o contrato de API R1 em `specs.md`.
- Diff revisado integralmente contra as respostas e o escopo: apenas Markdown,
  sem alterações de código, migrations, testes funcionais, configuração ou skills.
- `git diff --check`: aprovado.

O primeiro acesso ao PyPI foi bloqueado pelo sandbox; a instalação no ambiente
temporário passou com a execução autorizada fora dele. Não foram executados testes
de aplicação, frontend/backend ou fluxos R2 ainda não implementados.

## Pendências e limitações

- Lista do filtro de termos: solicitante definirá depois; não bloqueia fluxo humano.
  Correspondência futura já definida para palavras/expressões completas, ignorando
  maiúsculas e acentos, sem garantia de detectar todo disfarce.
- IA: objetivo futuro condicionado à viabilidade/validação; não substitui humanos agora.
- Modelo físico, rotas, payloads, códigos HTTP, operação do papel e descarte programado:
  detalhamento técnico das issues dependentes, com suas aprovações próprias.
- Denúncias de visitantes podem repetir e não representam contagem de pessoas distintas.
  Não existe vínculo de conta para detectar automaticamente todo impedimento pessoal
  envolvendo uma denúncia feita sem autenticação; não foi inventada coleta de identidade.
- Textos descartados não ficam disponíveis para reconstituir uma revisão antiga.
  Registros privados de decisão duram sete dias, sem cópias de textos rejeitados ou
  substituídos. Essa limitação decorre da retenção escolhida, não de falha de implementação.
- Não houve promoção dos RNFs propostos, das skills ou de ADRs; a redação documental
  e a publicação da entrega permanecem sujeitas à revisão humana solicitada.

## Organização dos commits

Dois commits locais: primeiro a fonte de requisitos e decisões; depois derivados e
evidência de verificação. A divisão permite revisar a decisão de produto antes de
sua propagação. Não foi feito push, aberta PR ou realizado merge nesta entrega.

## Proposta de Pull Request

**Título:** `docs: detalhar RF20–RF22 e decisões de moderação (#154)`

**Origem:** `docs/154-comentarios-denuncia-moderacao` · **Destino:** `develop`

### Objetivo

Detalha RF20–RF22 a partir das respostas humanas da discussão da #154, tornando
comentários, denúncias e moderação verificáveis antes das implementações dependentes.
Registra atores, permissões, visibilidade, estados por versão, erros, retenção e
17 critérios de aceitação com origem em 15 decisões agrupadas.

Atualiza primeiro `docs/requisitos.md`, depois `specs.md`, visão e referências
arquiteturais/históricas. Preserva critérios, agregação e RNF02; moderação inicial
humana, filtro com lista pendente e IA apenas como objetivo futuro condicionado.
Nenhuma funcionalidade da aplicação, schema ou contrato de API novo foi implementado.

Closes #154

Relacionado à Epic #145. As implementações e verificações da Epic continuam nas
#156/#159/#160/#161/#162/#163; esta PR conclui o detalhamento documental.

### Tipo de mudança

- [x] Documentação

### Validação

Build `mkdocs build --strict --site-dir site` aprovado, revisão documental de
rastreabilidade/consistência e `git diff --check` aprovados. Sem execução de testes
funcionais de fluxos ainda não implementados. Evidências e limitações neste relatório.

### Checklist

- [x] Branch e destino seguem `CONTRIBUTING.md`.
- [x] Escopo limitado à documentação da #154.
- [x] Decisões humanas possuem origem e estado; pendências permanecem explícitas.
- [x] Fonte alterada antes dos derivados.
- [x] Sem segredos, `.env`, artefatos temporários ou alterações de aplicação.
- [x] Nenhuma nova decisão técnica ou promoção de governança.

Esta descrição é uma proposta; publicação depende da confirmação explícita do usuário.
