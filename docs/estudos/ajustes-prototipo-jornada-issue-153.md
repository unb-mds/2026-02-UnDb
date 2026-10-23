# Protótipo adaptado aos relatos de uso — preparação da #153

**Estado:** proposta implementada para nova avaliação com alunos. Não há resultados dessa rodada registrados neste documento; a #153 permanece pendente.

**Data da preparação:** 22/10/2026. **Base:** `develop`, commit `741083cebe7cbb1d5ea0b3c2f4ac83cf362f8fa1`. As alterações estão na branch `feature/153-ajustes-prototipo`; registrar o SHA publicado da PR em cada sessão para identificar a versão efetivamente apresentada.

## 1. Objetivo e alcance

Adaptar `/prototipo` aos obstáculos encaminhados por Nicolas nos relatos de [ALUNO-01](relato-usabilidade-aluno-01-issue-148.md) e [ALUNO-02](relato-usabilidade-aluno-02-issue-148.md), para então verificar se a proposta melhora a compreensão da busca, da relação professor/disciplina e do caminho até avaliar.

A coleta dos relatos foi consolidada na [#148](observacao-jornada-busca-comparacao.md). A criação desta proposta não demonstra redução de obstáculos; esse resultado depende do uso pelos participantes na [#153](https://github.com/unb-mds/2026-02-UnDb/issues/153).

## 2. O que mudou

| Relatos de origem | Proposta no protótipo | O que observar na próxima rodada |
|---|---|---|
| OBS-01/02, A02-01/03 | Resultados de professor mostram departamento e disciplinas agrupadas. Duas Anas fictícias, em departamentos distintos, demonstram a distinção de registros; uma tem duas disciplinas. | A pessoa distingue os resultados e escolhe a matéria correspondente sem assumir que nomes iguais são a mesma pessoa? |
| OBS-02/06, A02-02/03 | Botão de avaliação por disciplina diretamente nos resultados e na página do professor; comparação é uma alternativa disponível. Professor e disciplina aparecem em destaque acima do formulário. | Encontra o caminho para avaliar e identifica quem está avaliando em qual matéria? |
| OBS-03 | Termo, tipo de busca e organização dos resultados são preservados nos parâmetros de URL e nos links de retorno. | Ao voltar pelo navegador ou pela interface, consegue continuar a busca sem redigitá-la? |
| OBS-04/10 | Nome e departamento ganham destaque; códigos aparecem com o rótulo “Código da disciplina”. | Compreende o significado do código e o contexto da unidade? O número relatado anteriormente ainda precisa ser identificado na versão real. |
| OBS-05/08 | Entrada única “Entrar / Criar conta” no cabeçalho, seguida de “Minha conta”; demonstra visitante, e-mail pendente/confirmado, saída e retorno à avaliação. Inclui Mostrar/Ocultar senha. | Distingue consulta pública de envio autenticado, encontra a área de acesso e reconhece a necessidade de confirmar o e-mail? |
| OBS-07 | Rótulos completos para Faz chamada/Não faz chamada e Recomenda/Não recomenda a matéria; a consulta agregada mantém percentuais e conflito. | Interpreta as respostas sem alterar a neutralidade da Chamada ou confundir percentual com avaliação individual? |
| OBS-09 | Organização demonstrativa dos resultados por nome ou departamento/nome, escolhida na busca. | Em qual contexto a opção ajuda? Essa experiência não aprova uma nova regra de ordenação do produto. |

O caminho visual foi resumido a três referências: buscar, escolher a disciplina e consultar/avaliar. A busca já está disponível na entrada. Estados de erro e carregamento ficam em uma seção expansível para não competir com as ações principais.

## 3. Regras preservadas e limites

- A autenticação real, os serviços HTTP e o backend não foram adaptados nesta entrega. O cabeçalho real foi extraído do layout raiz para um componente e conserva seus links nas rotas reais. O layout exclusivo de `/prototipo` recebe a navegação demonstrativa e evita exibir links reais de login/cadastro durante o teste. O componente compartilhado dos critérios recebe uma opção de rótulos explicativos, ativada apenas pelo protótipo; o padrão do formulário real permanece igual.
- Dados são fictícios e locais à rota. Não são feitas chamadas à API, autenticação real, envio de e-mail ou persistência de avaliação.
- A demonstração de acesso usa dados fictícios e não cria conta/sessão real. A simulação de entrada representa conta confirmada e a de cadastro representa e-mail pendente; a confirmação é um botão demonstrativo, sem envio de link. Os controles não permitem envio nativo; não há credenciais em URL ou armazenamento persistente. O estado visual fica em memória no layout do protótipo e reinicia ao recarregar. Sair apaga apenas esse estado demonstrativo. A prévia da avaliação continua disponível sem conta.
- Busca e contexto são preservados por URL; respostas preenchidas na avaliação não são persistidas entre etapas. Mostrar o acesso antes de preencher os critérios evita confundir esse limite com perda de respostas após envio.
- Valores, escalas, agregação e neutralidade de RF14/RF15 são preservados. RNF02 continua ocultando critérios abaixo de três avaliações. RF08/RF09/RF10/RF11 continuam representados nos retratos preparados.
- A comparação permanece entre professores da mesma disciplina, com apresentação por recomendação e desempates já preparados conforme RF12/RF13. A organização alfabética/departamental é restrita aos resultados de busca demonstrativos.
- Nomes iguais não são unidos. Não houve alteração de identidade institucional, importação, banco ou ADR 07.
- Fotos do SIGAA e dados de sala/prédio/campus não foram incluídos: fonte, associação correta ao docente e viabilidade permanecem sem verificação. O departamento mostrado é o da fixture, não uma localização física presumida.
- A prévia cobre os cinco critérios estruturados; comentários, denúncia e moderação da R2 não foram implementados aqui.

## 4. Como apresentar

Em `frontend/`, instalar as dependências do lockfile com `npm ci`, iniciar `npm run dev` e abrir `http://localhost:3000/prototipo`. Também é possível usar `npm run build` e `npm run start`. O protótipo não exige API nem importação do SIGAA.

Para esta rodada, começar pela página inicial do protótipo. Seu cabeçalho mantém busca e conta dentro da demonstração. “Voltar ao sistema”, no aviso do protótipo, muda o artefato avaliado e deve ser anotado no registro.

A área de conta é acessível mesmo sem professor ou matéria selecionados. Nesse caso, o retorno leva ao ponto da navegação de origem; quando aberta a partir da avaliação, mantém o destino escolhido. Não inclui edição de perfil, histórico de avaliações, recuperação de senha ou novas regras de acesso.

| Tarefa proposta ao participante | Preparação do facilitador |
|---|---|
| Encontrar a professora Ana e identificar as matérias associadas. | Selecionar busca por professor. Observar a distinção entre departamentos sem explicá-la antecipadamente. |
| Mostrar como avaliaria Ana em Estruturas de dados. | Registrar o percurso e se o atalho foi encontrado; concluir somente a prévia, sem tratar isso como envio real. |
| Voltar à busca e continuar a consulta. | Usar retorno da interface e histórico do navegador, em momentos separados; registrar se o termo e a organização foram reconhecidos. |
| Encontrar Algoritmos e comparar seus professores. | Observar contagem, dados insuficientes e conflito; verificar interpretação, não pedir uma nota “correta” para o professor. |
| Explicar como entraria para enviar uma avaliação no sistema real. | Abrir a área de conta antes de preencher os critérios; simular entrada e cadastro com dados fictícios, observar confirmação pendente, confirmar na demonstração e conferir o retorno à disciplina escolhida. |
| Preencher a prévia e explicar Chamada e Recomendação. | Não antecipar o significado dos rótulos; observar a compreensão e a identificação da matéria. |

O facilitador pode adaptar a redação ao participante, preservando o objetivo e registrando a ajuda dada. Não há meta nova de cliques, tempo ou taxa de sucesso.

## 5. Registro dos resultados — a preencher após o uso

Não há linhas de resultados preenchidas antecipadamente. Para cada tarefa, registrar:

| Campo | Informação a coletar |
|---|---|
| Participante e contexto | Código anônimo; vínculo com a UnB/equipe; contato anterior com o sistema e eventual acompanhamento de outra pessoa. |
| Sessão e versão | Data, dispositivo, navegador, largura de tela e commit/branch efetivamente apresentados. |
| Tarefa e resultado | O que tentou fazer; conclusão com autonomia, com ajuda ou não conclusão; último passo realmente realizado. |
| Dificuldade | Hesitação, interpretação e percurso observados; distinguir fala do participante de hipótese do facilitador. |
| Comparação | Qual obstáculo da #148 foi retomado; melhorou, permaneceu, apareceu outro ou não foi possível comparar, com evidência. |
| Limites | Diferença entre dados reais e fictícios, ajuda, aprendizado prévio, falta de API e ausência de persistência. |
| Encaminhamento | Ajuste de apresentação para #155/#157/#158 ou decisão de produto a levar ao PO. |

Se forem os mesmos colegas, registrar o aprendizado pela repetição. Dois relatos ou uma melhoria percebida nesta amostra não comprovam representatividade estatística.

## 6. Verificações técnicas

As verificações automatizadas cobrem comportamento da proposta e regressões do formulário; não substituem os resultados de alunos.

| Verificação local | Resultado |
|---|---|
| `npm test` | 19 testes aprovados, incluindo preservação de respostas Não e contratos existentes. |
| `npm run lint` | Aprovado. |
| `npm run build -- --webpack` | Aprovado, com TypeScript e todas as rotas. |
| `npm run test:browser` | Aprovado no Brave/Chromium com perfil temporário; runner existente, respostas controladas e nenhuma chamada à API pelo protótipo. |
| Temas e larguras | 12 telas/estados × 2 temas × 3 larguras (320/768/1280 px): 72 combinações sem rolagem horizontal, incluindo conta com/sem contexto; cenários visitante, pendente e confirmado, saída e retorno à avaliação também aprovados. |
| Inspeção visual | Capturas de entrada, formulário, resultados agrupados em desktop/celular, acesso móvel escuro e conta confirmada/pendente em desktop inspecionadas. |
| Documentação | `mkdocs build --strict` e `git diff --check` aprovados. |

Ambiente: macOS, Node 24.19.0, Next.js 16.3.5 e dependências do lockfile, sem alteração de versões. O npm foi disponibilizado temporariamente a partir do runtime local. A primeira tentativa de build não conseguiu baixar as fontes; a tentativa com acesso de rede encontrou uma restrição de porta/processo no Turbopack. O build foi verificado com a opção Webpack já oferecida pelo Next.js, sem alterar o script ou a configuração do projeto. O build padrão com Turbopack permanece não verificado neste ambiente; não foi declarado como aprovado.

As capturas locais de conferência foram geradas em `/private/tmp/undb-prototipo153-capturas`, fora do conjunto de arquivos para versionamento. A suíte também passou nas regressões do formulário real com respostas controladas; não houve integração com FastAPI/PostgreSQL reais nem teste com alunos nesta preparação.

## 7. Referências

- [Preparação anterior da validação da #153](validacao-prototipo-jornada-issue-153.md).
- [Protótipo original da #152 e evidências históricas](verificacao-prototipo-jornada-issue-152.md).
- [Requisitos](../requisitos.md), especialmente RF04–RF15 e RNF02.
- [Arquitetura](../arquitetura.md), ADRs 02, 07 e 08.
