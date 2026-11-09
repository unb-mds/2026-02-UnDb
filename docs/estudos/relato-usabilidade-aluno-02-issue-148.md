# Observação de uso — aluno da UnB externo à equipe

**Estado:** segundo relato de uso organizado a partir das observações encaminhadas por Nicolas. As propostas abaixo não são mudanças implementadas nem novos requisitos aprovados.

**Vínculo:** [Issue #148 — Observar a jornada com alunos](https://github.com/unb-mds/2026-02-UnDb/issues/148), com encaminhamentos para #155, #157 e #158. A avaliação do protótipo continua sendo acompanhada separadamente na #153.

## 1. Síntese

Um segundo colega, aluno da UnB e externo à equipe do projeto, acompanhou o processo e relatou confusão na busca por professor e dificuldade para encontrar o caminho até a avaliação. Segundo Nicolas, conseguiu usar o sistema normalmente depois de alguns cliques, embora o funcionamento inicial não estivesse claro.

Sugeriu agrupar as disciplinas na página do professor e, se possível, apresentar a foto do professor disponibilizada no SIGAA. A primeira sugestão se relaciona à organização e ao contexto da navegação; a segunda é uma possibilidade adicional cuja viabilidade ainda precisa ser verificada.

## 2. Origem e condições do registro

| Campo | Informação disponível |
|---|---|
| Participante | `ALUNO-02`, aluno da UnB que não participa da equipe do projeto. |
| Fonte | Relato escrito de Nicolas nesta conversa. O texto é uma organização das informações recebidas, sem transcrição literal da sessão. |
| Relação com o primeiro relato | Nicolas informou que o segundo colega também acompanhou o processo. Não foi esclarecido se navegou sozinho, observou o primeiro participante ou recebeu orientação. Não se presume independência entre as observações. |
| Data, versão e ambiente | Data da sessão, branch/commit, dispositivo, navegador e largura da tela não informados. |
| Atividades mencionadas | Busca por professor, compreensão da organização das informações e percurso até a avaliação. |
| Resultado relatado | Conseguiu usar normalmente após alguns cliques. O relato não especifica o último passo concluído nem confirma autenticação, envio ou persistência de uma avaliação. |
| Medições e anexos | Não foram fornecidos tempos, contagem de cliques, capturas ou gravação. |
| Protótipo | Não foi informado acesso a `/prototipo` nem comparação entre versões. |

## 3. Achados e sugestões

Os identificadores `A02-01` a `A02-04` pertencem a este registro. Não são novos requisitos funcionais.

### A02-01 — Confusão na busca por professor

**Relato:** o participante também citou confusão ao pesquisar professor e falta de clareza inicial sobre o funcionamento do sistema.

**Impacto percebido:** necessidade de explorar a navegação antes de compreender o percurso.

**Relação com o primeiro relato:** reforça a dificuldade geral de compreender a busca e seus resultados. Não confirma, por si só, a repetição indevida de professores, o desaparecimento da pesquisa ou o problema com códigos/números mencionados por `ALUNO-01`.

**Encaminhamento proposto:** revisar o contexto dos resultados, a apresentação da relação professor/disciplina e a indicação do próximo passo na #155. Registrar o termo buscado e a tela específica antes de atribuir a causa a dados ou componentes.

### A02-02 — Caminho até a avaliação pouco evidente

**Relato:** houve dificuldade para chegar à etapa de avaliação, mas o participante conseguiu usar o sistema depois de alguns cliques.

**Impacto percebido:** esforço inicial de descoberta, sem bloqueio total de uso relatado. Não há medição para definir quantos cliques foram excessivos ou afirmar sucesso do envio.

**Relação com o primeiro relato:** converge com OBS-06 de `ALUNO-01`, que também descreveu dificuldade para encontrar o caminho de avaliação.

**Encaminhamento proposto:** destacar a ação de avaliar quando professor e disciplina estiverem definidos, tornar os próximos passos reconhecíveis e conferir a continuidade entre consulta, acesso e formulário em #155/#158. Preservar autenticação e e-mail confirmado para envio, conforme RF14.

### A02-03 — Agrupar as disciplinas na página do professor

**Sugestão:** apresentar as disciplinas do professor agrupadas na própria página/aba do professor.

**Objetivo percebido:** facilitar a compreensão do vínculo entre professor e matéria e a escolha do contexto de avaliação. A redução de cliques por essa solução ainda não foi demonstrada.

**Contexto técnico já inspecionado:** a página `/professores/[id]` na `develop` de referência possui a seção “Disciplinas lecionadas”. A sugestão pode indicar que a seção passou despercebida, que o acesso aos resultados exige outra organização ou que a versão utilizada era diferente. Não se deve documentar a funcionalidade como inexistente sem reproduzir a navegação.

**Encaminhamento proposto:** identificar em qual tela o agrupamento era esperado; avaliar hierarquia, rótulos e acesso às disciplinas já existentes antes de criar uma estrutura adicional. Cada avaliação continua vinculada a um professor e uma disciplina; não juntar identidades de professores apenas por nome. Relaciona-se a RF05–RF07, RF14 e ADR 07, com trabalho candidato em #155/#157/#158.

### A02-04 — Foto do professor, se viável

**Sugestão:** mostrar a foto do professor disponível no SIGAA, caso seja possível.

**Classificação:** proposta opcional a investigar. A ausência de foto não foi descrita como impedimento de uso, e seu benefício ainda não foi validado.

**Verificações antes de decidir:**

- Confirmar se a fonte pública oferece a imagem e se é possível associá-la com segurança à identidade correta do docente.
- Conferir as condições de acesso e uso da imagem e o impacto de obtê-la/exibi-la na aplicação.
- Avaliar o impacto nos contratos e na importação: os contratos institucionais inspecionados não incluem campo de foto.
- Prever apresentação sem foto quando o dado não existir ou não puder ser obtido; a imagem não deve ser condição para buscar, consultar ou avaliar.

Não houve consulta ao SIGAA para verificar imagens nesta redação. A viabilidade permanece em aberto; a proposta deve ser avaliada pelo PO antes de ampliar o escopo das entregas. Não utilizar semelhança visual ou nome para unir registros de docentes.

## 4. Consolidação com o primeiro relato

| Tema | ALUNO-01 | ALUNO-02 | Leitura para planejamento |
|---|---|---|---|
| Clareza da busca por professor | Estranhou resultados com nomes repetidos e sentiu falta de contexto de matéria. | Citou confusão na busca, sem detalhar o elemento. | Dificuldade geral mencionada nos dois relatos; investigar causas sem assumir que são idênticas. |
| Acesso à avaliação | Considerou difícil chegar à avaliação, com muitos cliques. | Encontrou dificuldade inicial, mas conseguiu usar após alguns cliques. | Tema recorrente nos dois relatos; priorizar a investigação do percurso e da ação de avaliar. |
| Relação professor/disciplina | Pediu matéria mais visível junto ao professor e ao conteúdo. | Sugeriu disciplinas agrupadas na página do professor. | Propostas convergem na necessidade de contexto mais reconhecível; a solução final ainda precisa ser validada. |
| Foto do professor | Não mencionada. | Sugestão condicionada à viabilidade. | Investigar separadamente; não tratar como causa comprovada de dificuldade. |

A tabela registra presença nos relatos, não frequência de eventos por tarefa nem estimativa da população. Há dois participantes relatados, com possível observação compartilhada. O fato de conseguirem explorar a interface não elimina a dificuldade inicial; também não comprova que todas as tarefas foram concluídas.

Como proposta de prioridade, investigar primeiro a clareza dos resultados e o caminho para avaliar, por aparecerem nos dois relatos e afetarem diretamente a jornada central. Avaliar a organização das disciplinas como hipótese de solução. Manter a foto como estudo opcional, sem bloquear essas melhorias.

## 5. Complementação e próximo teste

1. Confirmar versão/ambiente e se o uso foi individual, acompanhado ou apenas observado.
2. Registrar o que exatamente ocorreu entre buscar o professor e encontrar a avaliação; distinguir conclusão da navegação de envio confirmado.
3. Identificar onde o participante esperava encontrar as disciplinas e conferir a seção já existente na página do professor.
4. Na #153, realizar e registrar o teste do protótipo nas tarefas correspondentes, indicando contato prévio com a interface e eventual ajuda recebida.

Este relato complementa a evidência da #148, sem encerrar a issue automaticamente. Não comprova validação do protótipo ou redução dos obstáculos, e não substitui os critérios da #153.

## 6. Referências

- [Primeiro relato — ALUNO-01](relato-usabilidade-aluno-01-issue-148.md).
- [Protocolo e diagnóstico da #148](observacao-jornada-busca-comparacao.md).
- [Preparação da validação da #153](https://github.com/unb-mds/2026-02-UnDb/blob/661c7cb68c27ca730b53632b6851a61bc8057d46/docs/estudos/validacao-prototipo-jornada-issue-153.md).
- [Requisitos](../requisitos.md), fonte de verdade para regras e escalas.
- [Arquitetura — ADR 07](../arquitetura.md#adr-07-identidade-institucional-e-sincronizacao-do-sigaa).

O contexto técnico remete à inspeção já registrada no primeiro relato, na `develop` de referência `661c7cb68c27ca730b53632b6851a61bc8057d46`, especialmente à página do professor e aos contratos institucionais. Não confirma que essa foi a versão usada pelo participante e não representa reprodução da sessão.
