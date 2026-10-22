# Observação de uso — busca, acesso e avaliação

**Estado:** relato de uso organizado a partir das observações encaminhadas por Nicolas. As melhorias abaixo são propostas para avaliação da equipe; não representam alterações já implementadas ou novos requisitos aprovados.

**Vínculo principal:** [Issue #148 — Observar a jornada com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/148). O registro também subsidia a preparação da [#153](https://github.com/unb-mds/2026-02-UnDb/issues/153) e o planejamento de #155, #157 e #158.

## 1. Síntese

O participante relatado conseguiu iniciar a navegação e realizar uma busca por professor, mas teve dificuldade para compreender a organização dos resultados e o caminho até a avaliação. Os principais pontos foram a percepção de nomes repetidos, a falta de contexto de disciplina nos resultados, a perda da pesquisa ao voltar e a quantidade percebida de etapas para avaliar.

Também foram relatadas dúvidas na tela de login e nos rótulos de Chamada e Recomendação. As sugestões se concentram em tornar professor, disciplina e unidade mais reconhecíveis, apresentar ações mais claras e melhorar a hierarquia visual.

O relato permite identificar obstáculos concretos para investigação. Não permite afirmar que todos os usuários enfrentam esses problemas, que o envio de uma avaliação foi concluído ou que o protótipo resolve as dificuldades.

## 2. Origem e condições do registro

| Campo | Informação disponível |
|---|---|
| Participante | `ALUNO-01`, aluno externo à equipe, conforme informado por Nicolas. |
| Identificação pública | Nome pessoal omitido, seguindo o protocolo de anonimização da #148. |
| Fonte | Relato escrito de Nicolas nesta conversa, após o uso pelo colega. A redação deste documento é uma organização desse relato, sem transcrição literal da sessão. |
| Quantidade de participantes | Um participante identificado no relato. O uso de expressões no plural não foi convertido em participantes adicionais. |
| Data da sessão | Não informada. |
| Ambiente | O contexto anterior previa execução local no computador do colega; sistema operacional, navegador, largura de tela e configuração efetivamente usados não foram confirmados no relato. |
| Versão testada | Branch e commit não informados. A orientação anterior era testar as páginas normais do sistema; o relato não confirma acesso a `/prototipo`. |
| Tarefas mencionadas | Abrir a página inicial, buscar professor, consultar informações, voltar à busca, acessar login e procurar o caminho de avaliação. |
| Resultado das tarefas | Há relato de busca e de dificuldades de navegação. Sucesso do login, confirmação de e-mail e envio/persistência da avaliação não foram informados. |
| Medições e anexos | Sem contagem de cliques, tempos, capturas, gravação ou medidas de frequência fornecidas. |

## 3. Dificuldades relatadas e propostas de encaminhamento

Os identificadores `OBS-01` a `OBS-10` são referências locais deste registro, não novos requisitos funcionais. Cada proposta deve ser confrontada com a versão testada e com os requisitos vigentes antes da implementação.

### OBS-01 — Professor aparentemente repetido nos resultados

**Relato:** ao pesquisar um professor, o participante estranhou encontrar o mesmo nome mais de uma vez.

**Impacto percebido:** dificuldade para distinguir qual resultado selecionar e compreender se os registros representam a mesma pessoa.

**Proposta:** investigar os registros correspondentes e apresentar contexto suficiente para distinguir os resultados. Não unir nem excluir professores apenas pelo nome: o projeto preserva identidades provisórias e evita unir homônimos automaticamente, conforme ADR 07.

**Verificação necessária:** registrar o termo pesquisado, os resultados exibidos, seus identificadores e as unidades/disciplinas associadas. A repetição visual não comprova duplicidade indevida no banco.

### OBS-02 — Falta de contexto da disciplina junto ao professor

**Relato:** o participante sentiu falta da matéria abaixo do nome do professor e sugeriu colocar a matéria em destaque acima do conteúdo relacionado.

**Impacto percebido:** dificuldade para reconhecer a relação entre professor e disciplina e saber qual combinação está sendo consultada ou avaliada.

**Proposta:** tornar explícitos professor e disciplina nos cabeçalhos da consulta e da avaliação; avaliar uma prévia das disciplinas nos resultados de professor. Um professor pode ter várias disciplinas: a interface não deve apresentar uma única matéria como se fosse a única associação existente.

**Verificação necessária:** identificar as telas exatas em que o contexto faltou ou passou despercebido. No código inspecionado, o formulário real já apresenta professor e disciplina; o achado pode envolver destaque visual, outra tela ou diferença de versão.

### OBS-03 — Pesquisa perdida ao voltar

**Relato:** ao voltar à página anterior, a pesquisa em andamento não foi preservada.

**Impacto percebido:** necessidade de refazer a busca e sensação de navegação desorganizada.

**Proposta:** preservar o termo e o contexto da busca ao abrir um resultado e retornar. Avaliar o uso de parâmetros de URL para permitir recuperação pelo histórico e por recarga, sem definir aqui uma nova arquitetura.

**Verificação sugerida:** pesquisar um nome, abrir um resultado, usar o botão Voltar do navegador e o link de retorno da interface, separadamente, e conferir se o termo e a lista correspondente são recuperados. O relato não informa qual mecanismo de retorno foi usado.

### OBS-04 — Unidade e localização pouco compreensíveis

**Relato:** foi sugerido destacar departamento ou localização na parte superior, com exemplos escritos como “fcte” e “bsaa”.

**Impacto percebido:** dificuldade para situar o professor ou a disciplina no contexto institucional.

**Proposta:** apresentar o nome legível da unidade/departamento com rótulo explícito e hierarquia visual clara. Confirmar com o participante o significado dos exemplos antes de definir textos ou campos.

**Limite:** departamento, faculdade, campus, prédio e sala não são equivalentes. Os contratos institucionais inspecionados oferecem `departamento`, mas não sala física. Não inferir localização a partir de nome, sigla ou código; inclusão de novos dados exige verificar a fonte e o escopo.

### OBS-05 — Tela de login pouco intuitiva

**Relato:** o participante considerou a página de login pouco intuitiva.

**Impacto percebido:** dificuldade na compreensão da etapa de acesso. O elemento específico que gerou dúvida não foi informado.

**Proposta:** revisar a apresentação das ações de entrar e cadastrar, a explicação do e-mail institucional e a continuidade até a avaliação. Preservar a consulta pública e a exigência de conta com e-mail confirmado para registrar avaliações.

**Verificação necessária:** identificar se a dúvida ocorreu antes do cadastro, na confirmação do e-mail, na entrada ou no retorno à avaliação. O modo local de confirmação por log pode influenciar a experiência, mas não foi confirmado como causa nesta sessão.

### OBS-06 — Caminho até avaliar percebido como longo

**Relato:** foi considerado difícil chegar à avaliação do professor, com muitos cliques.

**Impacto percebido:** esforço para encontrar a ação principal de contribuição.

**Proposta:** destacar uma ação de avaliação nas telas em que professor e disciplina já estejam definidos e preservar esse destino durante o acesso à conta. Se a disciplina ainda não estiver selecionada, deixar clara essa escolha, sem avaliar um professor fora do contexto de uma matéria.

**Verificação necessária:** registrar o percurso efetivamente feito e em qual etapa a ação deixou de ser encontrada. Não há contagem de cliques para estabelecer uma meta numérica de redução.

### OBS-07 — Respostas de Chamada e Recomendação genéricas

**Relato:** as respostas “Sim” e “Não” para chamada foram consideradas genéricas; houve sugestão de textos como “Faz chamada” e “Não faz chamada”. Também foi relatada falta de clareza na apresentação de recomendar ou não a matéria.

**Impacto percebido:** dificuldade para interpretar o que cada resposta comunica no formulário.

**Proposta:** testar rótulos completos, como “Faz chamada” / “Não faz chamada” e “Recomenda a matéria” / “Não recomenda a matéria”, mantendo visível a disciplina correspondente. Esses textos são exemplos para validação, não redação final aprovada.

**Limites:** preservar os valores booleanos, as escalas e as regras de agregação existentes; Chamada continua neutra. Na consulta agregada, Recomendação continua sendo percentual, não uma resposta individual exposta publicamente. Confirmar em qual tela a ambiguidade ocorreu.

### OBS-08 — Mostrar e ocultar senha

**Relato:** foi sugerido um botão para revelar e ocultar a senha digitada.

**Proposta:** avaliar a inclusão do controle na tela de acesso, e no cadastro caso a equipe confirme esse alcance. O botão deve comunicar seu estado e poder ser acionado pelo teclado, sem enviar o formulário ou alterar o valor digitado.

**Limite:** trata-se de uma sugestão de melhoria; o relato não identifica erro de autenticação causado pela ausência desse controle.

### OBS-09 — Ordenação por departamento ou nome da disciplina

**Relato:** foi sugerida a possibilidade de alternar a ordenação por departamento e por nome da disciplina.

**Proposta:** esclarecer em qual listagem a pessoa espera usar cada opção e submeter o comportamento ao PO. Distinguir ordenação de resultados de busca da comparação de professores de uma mesma disciplina.

**Limites:** a regra vigente de comparação é ordenação por percentual de recomendação, com os desempates definidos nos requisitos. Esta sugestão não autoriza substituir essa regra nem restringir a busca ao departamento do usuário. Novas opções de ordenação devem ter escopo e comportamento definidos antes de implementação.

### OBS-10 — Código ou número sem significado claro

**Relato:** o participante não compreendeu um número exibido junto às matérias e sugeriu mostrar o nome do departamento em seu lugar. Mencionou um código no formato “cic001”, um nome de disciplina e outro número, sem identificar exatamente a tela ou o campo.

**Impacto percebido:** informação vista como aleatória, dificultando a leitura dos resultados.

**Proposta:** identificar o elemento antes de modificá-lo; avaliar rótulos como “Código da disciplina” e “Departamento”, priorizando visualmente nome e contexto institucional.

**Limites:** não há evidência suficiente para afirmar que o valor era código da disciplina, identificador interno ou outro dado. Não remover o código institucional sem avaliação: RF06 mantém a busca por código. O departamento pode ser destacado sem eliminar essa informação.

## 4. Priorização proposta

Esta ordem é uma recomendação editorial baseada no impacto descrito sobre a jornada. Não é uma frequência medida nem uma decisão de sprint. Uma sessão relatada não permite estimar a prevalência dos problemas entre alunos.

| Ordem sugerida | Achados | Justificativa |
|---|---|---|
| Investigar primeiro | OBS-01, OBS-02 e OBS-10 | Reconhecer professor, disciplina e unidade é necessário para selecionar o destino correto da consulta e da avaliação. |
| Ajustar a continuidade da jornada | OBS-03, OBS-05 e OBS-06 | Perda da busca, dúvidas de acesso e dificuldade de encontrar a avaliação aumentam o esforço para concluir o percurso. |
| Refinar clareza e interação | OBS-04, OBS-07 e OBS-08 | Hierarquia visual, respostas compreensíveis e controle da senha apoiam a compreensão e o preenchimento. |
| Decidir escopo antes de implementar | OBS-09 e inclusão de localização em OBS-04 | Novas ordenações e dados de sala/localização dependem de esclarecimento, fonte e decisão de produto. |

O pedido geral de tornar o site mais intuitivo e visualmente agradável foi desdobrado nesses pontos concretos. Não constitui autorização para um redesenho integral ou para mudanças nas regras do produto.

## 5. Rastreabilidade e orientação às próximas entregas

As referências a requisitos indicam o comportamento que deve ser preservado, não que todo pedido do participante já seja exigência aprovada. As rotas abaixo são candidatas para investigação; a rota efetivamente usada na sessão não foi registrada.

| Achados | Telas candidatas | Fontes e limites | Encaminhamento sugerido |
|---|---|---|---|
| OBS-01, OBS-02, OBS-04 | `/professores`, `/professores/[id]` | RF05–RF07; ADR 07; manter identidade e vínculos institucionais. | #155: contexto dos resultados e navegação; investigar dados antes de unir registros. |
| OBS-03 | `/professores`, `/disciplinas` e links de retorno | RF05/RF06; preservação da busca é proposta de UX. | #155: continuidade da pesquisa ao navegar e voltar. |
| OBS-05, OBS-06, OBS-08 | `/login`, `/cadastro`, consulta professor/disciplina e formulário | RF01/RF02/RF04/RF14; manter acesso público à consulta e autorização no envio. | #155/#158: revisar acesso e percurso; explicitar o alcance das alterações de login/cadastro no planejamento. |
| OBS-02, OBS-07 | `/professores/[id]/disciplinas/[disciplinaId]` e `/avaliar` sob essa rota | RF08/RF14/RF15 e RNF02; preservar escalas, neutralidade e privacidade. | #157/#158: contexto visual e rótulos do formulário e da consulta. |
| OBS-09, OBS-10 | `/disciplinas`, `/disciplinas/[id]` e listas de disciplinas | RF06/RF07/RF12/RF13; não substituir silenciosamente a ordenação da comparação. | #155/#157: identificar campos e propor ordenações com escopo explícito ao PO. |

Para implementar, partir de `develop`, consultar as instruções do frontend e as skills aplicáveis, reproduzir o achado na versão registrada e associar a mudança ao identificador deste documento. Não é necessário criar uma issue para cada observação se o trabalho couber nas entregas existentes; o planejamento deve explicitar o alcance escolhido.

## 6. O que este registro comprova e o que permanece aberto

- **Registrado:** um relato humano de uso, suas dificuldades, propostas associadas e relação com telas/requisitos.
- **A completar:** data, versão, ambiente, percurso de retorno, elemento numérico e distinção dos resultados com nomes repetidos.
- **Não medido:** frequência por tarefa, quantidade de cliques, tempo e taxa de sucesso.
- **Não demonstrado:** sucesso de autenticação/envio, teste do protótipo e redução dos obstáculos em comparação com o sistema atual.
- **A decidir:** propostas de ordenação e eventual inclusão de localização; textos e prioridades finais de implementação.

Para a #148, este documento acrescenta evidência ao diagnóstico, mas não marca automaticamente seus critérios como concluídos. A equipe deve avaliar a suficiência do registro e complementar as lacunas relevantes. Para a #153, ainda é necessário registrar o uso do protótipo e confrontar os resultados com estes obstáculos; não há resultado desse teste neste relato. Nenhuma issue é encerrada por este documento.

## 7. Próxima verificação com o participante

1. Confirmar data, branch/commit, dispositivo e navegador usados, se disponíveis.
2. Repetir a busca que mostrou nomes aparentemente repetidos e identificar os resultados, sem publicar dados pessoais do participante.
3. Identificar a tela e o valor que pareceram um número aleatório, e o significado esperado de “fcte”/“bsaa”.
4. Registrar o percurso até avaliar e o ponto de dúvida no login; conferir se houve conclusão ou abandono.
5. Usar o protótipo nas tarefas correspondentes e registrar o que melhorou, permaneceu difícil ou não pôde ser comparado. Se for a mesma pessoa, registrar que já conhecia a tarefa.

Esses itens complementam o roteiro existente; não exigem refazer toda a sessão nem autorizam preencher informações ausentes por suposição.

## 8. Referências

- [Segundo relato e consolidação — ALUNO-02](relato-usabilidade-aluno-02-issue-148.md).
- [Protocolo e diagnóstico preliminar da #148](observacao-jornada-busca-comparacao.md).
- [Preparação da validação da #153](https://github.com/unb-mds/2026-02-UnDb/blob/661c7cb68c27ca730b53632b6851a61bc8057d46/docs/estudos/validacao-prototipo-jornada-issue-153.md).
- [Protótipo e limitações da #152](verificacao-prototipo-jornada-issue-152.md).
- [Requisitos do produto](../requisitos.md), fonte de verdade para regras e escalas.
- [Arquitetura — ADR 07](../arquitetura.md#adr-07-identidade-institucional-e-sincronizacao-do-sigaa).

A inspeção de apoio consultou a `develop` no commit `661c7cb68c27ca730b53632b6851a61bc8057d46`: páginas de busca de professor/disciplina, detalhe do professor, formulário de avaliação, login, `frontend/src/lib/avaliacao-formulario.ts` e `backend/app/schemas/institucional.py`. Essa é a versão de referência da análise, não uma confirmação da versão utilizada pelo participante. Não houve reprodução da sessão ou teste de navegação durante a redação.
