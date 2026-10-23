# Resultados do reteste e encaminhamentos — issue #153

**Registro:** 22/10/2026. **Fonte:** retorno do participante encaminhado por Nicolas na conversa de trabalho, seguido de sua escolha por notas em botões e autorização para publicar a entrega na [PR #182](https://github.com/unb-mds/2026-02-UnDb/pull/182).

**Estado:** avaliação qualitativa registrada para revisão da [#153](https://github.com/unb-mds/2026-02-UnDb/issues/153). Há melhora percebida e dificuldades remanescentes; os ajustes feitos após esse relato ainda não foram retestados pelo participante.

## 1. Participante, artefato e limites

O retorno se refere a um usuário do protótipo. Seu vínculo com a UnB, identidade e correspondência com ALUNO-01/ALUNO-02 não foram informados nesta rodada. Não se presume um terceiro participante nem sessões independentes. O relato foi mediado por Nicolas; não houve observação direta pelo agente.

O artefato disponibilizado foi `/prototipo`, na branch `feature/153-ajustes-prototipo`, PR #182, com a versão publicada `60e63246831533f7c27ac93031bd5828ff37b5bf`. Esse SHA é uma referência de distribuição, não confirmação da versão efetivamente executada pelo participante. Data e duração da sessão, dispositivo, navegador, largura, roteiro exato, intervenções e contagem de cliques não foram informados.

Os dados são fictícios e locais, a conta é demonstrativa e a avaliação não é enviada ou salva. Não há evidência de envio real, comparação de notas, confirmação real de e-mail ou conclusão autônoma de todas as tarefas do roteiro. Não foram coletados indicadores quantitativos; o retorno não comprova representatividade nem eliminação de todos os obstáculos.

## 2. Atividades e observações informadas

As atividades abaixo foram identificadas pelos elementos mencionados no relato; não equivalem à confirmação de execução integral do roteiro preparado.

| Código | Atividade/elemento mencionado | Resultado informado | Limite |
|---|---|---|---|
| RT-01 | Retornar na jornada | Gostou do botão de retorno e achou a experiência mais organizada e melhor que antes. | Não foi informado se também testou o histórico do navegador ou a preservação do termo. |
| RT-02 | Interpretar a organização dos resultados | Não entendeu exatamente as opções “departamento” e “nome”; sugeriu escolher a ordenação na própria listagem, sem defini-la previamente. | Não se presume falha da busca nem equivalência entre departamento e localização física. |
| RT-03 | Página de avaliação | Pediu um layout mais visual; estrelas foram um exemplo de apresentação de nota. | Não foi relatado envio ou preenchimento completo dos cinco critérios. |
| RT-04 | Login e criar conta | Notou itens de pesquisa ainda aparecendo acima da área de conta, descrevendo a apresentação como bugada. | Não há relato de falha de autenticação real; o acesso utilizado é simulado. |
| RT-05 | Impressão geral | Relatou melhora expressiva da experiência em relação à anterior. | Percepção qualitativa; não há medida de tempo, cliques ou taxa de sucesso. |

## 3. Comparação com o diagnóstico da #148

Base: [observação consolidada](observacao-jornada-busca-comparacao.md) e relatos de [ALUNO-01](relato-usabilidade-aluno-01-issue-148.md) e [ALUNO-02](relato-usabilidade-aluno-02-issue-148.md).

| Obstáculo anterior | Evidência do reteste | Conclusão possível |
|---|---|---|
| Retorno e perda da busca (OBS-03) | RT-01 elogia o botão de retorno. | Retorno percebido como melhor; preservação da pesquisa não confirmada pelo relato. |
| Organização e compreensão da busca/professor/disciplina (OBS-01/02/04/10; A02-01/03) | RT-01/05 apontam organização melhor; RT-02 mantém dúvida sobre nome/departamento. | Melhora geral percebida, com vocabulário e localização do controle ainda a ajustar. Distinção de homônimos e códigos não foi confirmada. |
| Acesso à avaliação e excesso de cliques (OBS-06; A02-02) | RT-03 comenta a página de avaliação. | A tela foi mencionada, mas não há percurso ou contagem para afirmar redução de cliques. |
| Clareza de acesso e conta (OBS-05/08) | RT-04 identifica sobreposição visual com itens de pesquisa. | Dificuldade de apresentação permanece; compreensão de confirmação de e-mail e controle de senha não foi avaliada neste retorno. |
| Compreensão de Chamada/Recomendação e aparência do formulário (OBS-07; A02-03) | RT-03 pede controles mais visuais. | Há pedido de apresentação; não há confirmação de compreensão das escalas ou dos rótulos. |

O resultado é favorável à direção da proposta, mas parcial: melhor organização e retorno convivem com problemas de clareza e apresentação. Os itens sem evidência ficam explícitos, sem serem classificados como resolvidos.

## 4. Ajustes posteriores ao relato

Implementados nesta entrega do protótipo, sujeitos à revisão e a eventual novo reteste:

- **RT-02:** ordenação na própria lista, com atualização ao trocar a opção, mantendo termo e tipo de busca. Rótulos “Nome do professor/da disciplina (A–Z)” e “Unidade acadêmica (A–Z)”, acompanhados de explicação de departamento/instituto/faculdade. Não altera a ordenação da comparação por recomendação.
- **RT-03:** Didática em botões de 1 a 5, sem nota pré-selecionada, com texto da escolha, seleção por teclado e foco visível. Nicolas preferiu botões às estrelas. A escala continua exatamente 1–5, sem nova nota composta ou descrições qualitativas aprovadas para cada número.
- **RT-03:** formulário em bloco com mais espaçamento, didática destacada e seção para os demais critérios; professor e disciplina continuam em destaque acima.
- **RT-04:** login/cadastro sem a navegação das etapas de pesquisa. Quando houver avaliação selecionada, o contexto fica recolhido em uma seção expansível, preservando o destino de retorno.

Essas alterações não são resultados já aprovados pelo participante. A autenticação, persistência e telas reais continuam fora do alcance desta proposta.

## 5. Ideias registradas para continuidade

Nicolas considerou boas as sugestões abaixo e pediu seu registro. A tabela distingue o que existe daquilo que ainda precisa de refinamento, evitando ampliar silenciosamente esta entrega.

| Ideia | Situação e próximo passo |
|---|---|
| Professor e disciplina em destaque no topo | Já representado no protótipo; transportar para a implementação real em #158. |
| Separar “Sobre as aulas” e “Sua recomendação” em blocos com mais espaço | Agrupamento inicial aplicado; refinar a separação dos blocos na #158 sem alongar desnecessariamente o formulário. |
| Didática em botões numerados e descrição da escolha | Botões e texto “Nota selecionada: X de 5” implementados. Adjetivos como “Regular” não foram adicionados: significado de cada nota precisa de alinhamento ao produto. |
| Dificuldade em opções escritas | Preservar Fácil/Médio/Difícil. A sugestão anterior de cinco níveis (“Muito fácil” a “Muito difícil”) alteraria o contrato de três níveis; encaminhar ao PO, sem implementar nesta PR. |
| Chamada e Recomendação em botões maiores com respostas específicas | Rótulos explícitos já existem nos seletores. Botões para esses critérios ficam como refinamento para #158, mantendo booleanos e neutralidade. |
| Confirmação bem visível ao concluir | A prévia já informa que nada foi enviado/salvo; melhorar sua hierarquia visual na #158. Na rota real, confirmar sucesso somente após resposta do serviço. |

Para #155/#157: levar a ordenação para a listagem, explicar unidade acadêmica, preservar pesquisa/retorno e manter disciplinas agrupadas por professor. A aplicação às rotas reais deve ser verificada com API/dados reais; esta PR não a comprova.

## 6. Encaminhamentos de produto e critérios da issue

O [encaminhamento anterior ao PO](https://github.com/unb-mds/2026-02-UnDb/issues/153#issuecomment-6307276687) sobre ordenação da comparação permanece sem resposta presumida. A nova organização alfabética só demonstra resultados de busca; não substitui RF13. Eventual ampliação de Dificuldade para cinco níveis e rótulos qualitativos novos para Didática exigem decisão do PO e atualização dos contratos antes de implementar. As questões históricas de semestre/oferta permanecem no [roteiro anterior](validacao-prototipo-jornada-issue-153.md).

- [x] **Registrar tarefas, observações e limitações da avaliação:** atividades mencionadas, resultados mediados e informações ausentes nas seções 1–2.
- [x] **Comparar os principais obstáculos com o diagnóstico anterior:** comparação qualitativa e limites na seção 3; não há alegação de melhora em itens não observados.
- [x] **Encaminhar mudanças que impliquem regra de produto ao PO:** encaminhamento anterior e pontos desta seção registrados para revisão na #153/PR #182; sem pressupor resposta ou aprovação do PO.

Os critérios possuem evidência documental para revisão humana. A publicação da PR não equivale a merge nem fecha a issue por si só: a conclusão deve acompanhar a revisão e integração da entrega conforme `CONTRIBUTING.md`. Um novo teste dos ajustes desta rodada pode aprofundar a validação, sem reescrever o relato recebido como se fosse avaliação dessa versão nova.

## 7. Verificação técnica

As evidências técnicas estão na seção 6 de [ajustes do protótipo](ajustes-prototipo-jornada-issue-153.md). Testes automatizados verificam controles e regressões, não substituem a percepção do participante descrita acima.
