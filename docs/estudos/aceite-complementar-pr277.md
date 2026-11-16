# Aceite editorial complementar — PR #277

Data: 16/11/2026 (America/Sao_Paulo). Textos conferidos em `c69e660`.
**Estado: preparado para decisão humana; não aprovado.** Origem: solicitação de Gabriel
para resolver pendências que não dependam de Nicolas. Não foi encontrado novo defeito
técnico nesta conferência. Este pacote delimita o aceite editorial que continuava
descrito genericamente como “demais trechos”.

## 1. O que já está aprovado

[A1–A6](revisao-pr277.md) registram os aceites de Gabriel para independência, autoria,
limites/e-mail, mínimo, moderação e fórmulas/comparação no Sobre. A7 mantém FGA fora do
texto público e em entrega futura. A8 confirma os responsáveis pela retomada.
Esses aceites permanecem válidos nos seus escopos e não estão sendo solicitados novamente.

## 2. Trechos complementares já presentes na branch

### E1 — Título da Home

> Escolha seus professores com experiências compartilhadas por estudantes.

Substitui a afirmação de que as opiniões necessariamente vêm de quem já cursou.
Fonte: RF01/RF14 e A3; não muda o cadastro nem verifica experiência.

### E2 — Cartão de indicadores na Home

> Indicadores com contexto
>
> Indicadores agregados a partir de três avaliações por professor e disciplina;
> abaixo disso, contagem e insuficiência.

Fonte: RNF02 e A4. Não altera o mínimo ou a publicação de comentários.

### E3 — Apresentação e acesso à metodologia na Home

> Projeto acadêmico estudantil independente, complementar aos processos oficiais da UnB.
> Conta institucional confirmada não comprova experiência na disciplina.
> Conheça a metodologia e os limites.

O último trecho é link para `/sobre#metodologia`. Fontes: A1/A3 e a seção de metodologia
já aprovada. Não apresenta a equipe como representante da UnB.

### E4 — Moderação no passo Contribua e na chamada final da Home

No passo Contribua:

> Avalie com sua conta institucional confirmada. Comentários são opcionais. Com a triagem
> habilitada, textos sem sinais locais e da IA podem ser publicados automaticamente;
> os demais aguardam revisão humana.

Na chamada final, a primeira frase é “Avalie em cinco critérios com sua conta
institucional confirmada.”; o restante é igual. Fontes: RF20.4, decisão #239 e A5.
O uso de “podem” e a condição de habilitação não anunciam ativação ou detecção integral.

### E5 — Cartão Comentários com responsabilidade no Sobre

> Comentários são opcionais e podem ser denunciados. Com a triagem automática habilitada,
> textos sem sinais locais e da IA podem ser publicados automaticamente; os demais
> aguardam revisão humana.

Fontes: RF20–RF22 e A5. A metodologia da mesma página detalha falhas, limites,
configuração incompleta e ausência de garantia integral.

### E6 — Rastreabilidade e documentos derivados

Conferência técnica concluída: os acréscimos em [Visão](../visao.md) e `specs.md`
descrevem regras existentes, com fonte em `docs/requisitos.md`. Não houve decisão
nova a propagar à fonte de requisitos. O aceite editorial complementar abrange:

- Visão: motivação independente/complementar; resultados por professor–disciplina;
  mínimo e contagem; ausência de nota geral; volume não indica qualidade; limites de
  opiniões/e-mail/autoria; triagem condicional e revisão humana por exceção.
- Specs: chamada como controle de presença, neutralidade e desempates, limites do
  mínimo, confirmação sem prova de matrícula/experiência e vínculo interno preservado.
- Registro de revisão: distinção entre aceites, análise preliminar, testes sintéticos,
  operação não comprovada e retomadas registradas no épico/destinos.

Para conferir as alterações exatas em relação à base da PR:

- [Home, Sobre e documentos no diff da PR #277](https://github.com/unb-mds/2026-02-UnDb/pull/277/files).
- [Visão no commit examinado](https://github.com/unb-mds/2026-02-UnDb/blob/c69e660/docs/visao.md).
- [Specs no commit examinado](https://github.com/unb-mds/2026-02-UnDb/blob/c69e660/specs.md).
- [Registro dos aceites e evidências](revisao-pr277.md).

## 3. Alcance de uma eventual aprovação

Uma aprovação explícita de **E1–E6** encerra somente o aceite editorial complementar
desses textos/derivações. Não é aprovação formal no GitHub, parecer jurídico, aceite
de políticas futuras, escolha de base legal, autorização de ativação, fechamento de
issue ou merge. A manifestação humana precisa ser registrada com seu alcance real.

A necessidade de aceite vem do critério da [#271](https://github.com/unb-mds/2026-02-UnDb/issues/271):
“revisão humana confere rastreabilidade e aprova a comunicação”. Preparar o pacote e
conferir tecnicamente os textos não substitui essa manifestação.

## 4. Pendências que não são exclusivas de Nicolas

| Ponto | Quem precisa agir | Parte independente disponível | Limite |
|---|---|---|---|
| Aceite editorial complementar | Gabriel | E1–E6 acima, prontos para decisão conjunta | Não inferir aceite da ordem para preparar/resolver |
| Política/revisão/escalonamento, #264 | Warlley, com revisão pertinente | Regras vigentes e roteiro já conferidos na [verificação](verificacao-pendencias-pr277.md) | Novas regras e enquadramento jurídico precisam de decisão; operação/urgências dependem também de Nicolas |
| Necessidade de campos/acesso, #265 | Yasmin, com decisão competente | Matriz de campos/atores, inventário e correção de cache entregues | RF22 aprova nome/e-mail internamente; remover campos ou mudar permissões exige decisão própria |
| Revisão jurídica | Pessoa habilitada/designada pela equipe | Análise preliminar, fontes/limites, inventário e 36 casos disponíveis | Não há revisor jurídico designado/aceite identificado neste registro; dados operacionais ainda faltam |
| Aprovação formal da PR | Revisor humano conforme CONTRIBUTING | Sem threads de revisão abertas; CI do head examinado aprovado | Não há revisão submetida no GitHub; essa ausência não é aprovação |

Os pontos de #264/#265/#268/#269 já têm retomada no épico e nos destinos. Este pacote
não converte toda evolução futura em bug ou bloqueio genérico da PR, nem declara essas
issues concluídas. Os fatos adiados com Nicolas permanecem no
[pedido de confirmação](https://github.com/unb-mds/2026-02-UnDb/pull/277#issuecomment-6917996624).
