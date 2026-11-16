# Continuidade operacional e responsáveis

> **Estado: proposta parcial para validação humana.** Este documento registra indicações
> e aceites reportados por Nicolas nesta conversa, além de procedimentos para revisão.
> Não determina qualificação jurídica, não confirma acessos reais e não altera contas,
> permissões ou serviços.

Esta proposta prepara a entrega documental da [issue #260](https://github.com/unb-mds/2026-02-UnDb/issues/260), vinculada ao épico [#272](https://github.com/unb-mds/2026-02-UnDb/issues/272). A auditoria e este documento não certificam segurança ou conformidade jurídica.

## 1. Identidade e limites do projeto

O UnDb é um projeto estudantil independente. Não há, neste registro, evidência de
endosso institucional da Universidade de Brasília, nem fundamento para atribuir à UnB
responsabilidade pelo serviço. O projeto não representa a avaliação oficial da UnB,
de seus cursos ou docentes.

Esta descrição deve ser revisada pelas pessoas responsáveis antes de ser publicada em
políticas ou apresentada como posição institucional. A qualificação jurídica de
controlador, operador, representante ou encarregado permanece sujeita a revisão
especializada.

## 2. Papéis e contatos a designar

As pessoas devem aceitar expressamente cada designação antes que o papel seja tratado
como vigente. Ser autor de código, responsável por uma issue ou administrador de uma
conta não constitui, por si só, designação jurídica ou operacional.

| Papel a definir | Titular e contato | Substituto e contato | Escopo / limites | Aceite e data | Estado |
|---|---|---|---|---|---|
| Decisão sobre finalidades e meios do tratamento (qualificação jurídica pendente) | Equipe do UnDb, em conjunto | Decisão coletiva; sem substituto individual designado | Decidir dados coletados, finalidades, acesso e descarte; respeitar requisitos e retenção aprovados | Decisão confirmada por Nicolas nesta conversa em 15/11/2026 | Definição operacional aprovada; qualificação jurídica não validada |
| Operação técnica da aplicação e infraestrutura | Nicolas Zanin (titular declarado; contato de trabalho pendente) | Tiago Vieira (contato de trabalho pendente) | Nicolas conduz a operação; equipe apoia conforme disponibilidade e acessos aprovados | Nicolas aceitou; confirmou o aceite de Tiago em 15/11/2026 | `Proposed` até registrar limites do apoio e verificar acessos |
| Recebimento de solicitações de privacidade | Vinicius Gavaldao (contato de trabalho pendente) | Gabriel (sobrenome e contato pendentes) | Receber, protocolar e encaminhar; qualificação jurídica dos papéis permanece pendente | Nicolas confirmou em 15/11/2026 os aceites de Vinicius e Gabriel | `Proposed` até definição do canal |
| Recebimento de notificações jurídicas | Vinicius Gavaldao (contato de trabalho pendente) | Gabriel (sobrenome e contato pendentes) | Receber e encaminhar pelo canal aprovado; qualificação jurídica dos papéis permanece pendente | Nicolas confirmou em 15/11/2026 os aceites de Vinicius e Gabriel | `Proposed` até definição do canal |
| Renovação do domínio e dos serviços | Nicolas Zanin (titular declarado; contato de trabalho pendente) | Tiago Vieira (contato de trabalho pendente) | Acompanhar vencimentos e titularidade administrativa; equipe pode apoiar | Nicolas aceitou e confirmou o aceite de Tiago em 15/11/2026 | `Proposed` até conferência dos vencimentos e verificação de acesso |
| Moderação e reconciliação de identidades | Pendente | Pendente | Executar somente os procedimentos aprovados para cada função | Pendente | `Pending Decision` |

Não preencher contatos pessoais ou dados sensíveis em documentação pública. Publicar
somente um canal institucional ou endereço de contato aprovado para essa finalidade.

## 3. Inventário administrativo a confirmar

O guia de [hospedagem de demonstração](hospedagem.md) documenta os provedores previstos
ou usados na preparação. Ele não comprova titularidade, configuração atual, recuperação
de conta, nem quem tem acesso administrativo. Os itens abaixo precisam ser confirmados
por responsáveis autorizados, diretamente nos painéis e registros pertinentes.

As entregas anteriores de hospedagem foram consultadas: [#169](https://github.com/unb-mds/2026-02-UnDb/issues/169)
registrou a estratégia; [#170](https://github.com/unb-mds/2026-02-UnDb/issues/170), a preparação do
PostgreSQL; [#171](https://github.com/unb-mds/2026-02-UnDb/issues/171), a publicação e validação
operacional. Elas documentam Vercel, Render, Neon, Resend e Registro.br, mas não substituem
a confirmação de titularidade administrativa, recuperação de contas e aceite dos
responsáveis nesta entrega. Este trabalho não repetiu testes em produção nem alterou os
serviços.

Nicolas confirmou ser titular dos painéis citados e informou que a recuperação de acesso
ocorre por e-mail sob seu controle. Não foram registrados endereços, códigos ou segredos,
nem foram inspecionadas as configurações dos painéis.

| Recurso | Referência documental | Conta institucional/organizacional disponível? | Titular administrativo | Operador(es) autorizado(s) | Renovação / vencimento | Recuperação institucional | Estado |
|---|---|---|---|---|---|---|---|
| Domínio `undb.app.br` / Registro.br | `docs/hospedagem.md` informa aquisição por um ano | Não informado | Nicolas Zanin (titularidade declarada em 15/11/2026; painel não inspecionado) | Nicolas; inclusão de equipe planejada onde suportada | Nicolas responsável; vencimento não informado | E-mail sob controle de Nicolas (informado por ele) | `Proposed` |
| Frontend / Vercel | `docs/hospedagem.md` | Membresia organizacional planejada; convite pendente | Nicolas Zanin (titularidade declarada em 15/11/2026; painel não inspecionado) | Nicolas; Tiago, Vinicius e Gabriel planejados como membros | Nicolas responsável | E-mail sob controle de Nicolas (informado por ele) | `Proposed` |
| API / Render | `docs/hospedagem.md` | Membresia organizacional planejada; convite pendente | Nicolas Zanin (titularidade declarada em 15/11/2026; painel não inspecionado) | Nicolas; Tiago, Vinicius e Gabriel planejados como membros | Nicolas responsável | E-mail sob controle de Nicolas (informado por ele) | `Proposed` |
| Banco / Neon | `docs/hospedagem.md` | Membresia organizacional planejada; convite pendente | Nicolas Zanin (titularidade declarada em 15/11/2026; painel não inspecionado) | Nicolas; Tiago, Vinicius e Gabriel planejados como membros | Nicolas responsável | E-mail sob controle de Nicolas (informado por ele) | `Proposed` |
| E-mail / Resend | `docs/hospedagem.md` | Membresia organizacional planejada; convite pendente | Nicolas Zanin (titularidade declarada em 15/11/2026; painel não inspecionado) | Nicolas; Tiago, Vinicius e Gabriel planejados como membros | Nicolas responsável | E-mail sob controle de Nicolas (informado por ele) | `Proposed` |
| Repositório GitHub e organização | Repositório `unb-mds/2026-02-UnDb` | Organização existente; papel administrativo individual não verificado | Nicolas Zanin (titularidade declarada em 15/11/2026; papel na organização não inspecionado) | Nicolas; inclusão de equipe planejada | Nicolas responsável | E-mail sob controle de Nicolas (informado por ele) | `Proposed` |

Guardar identificadores de conta, e-mails de recuperação, códigos de recuperação,
tokens, senhas, URLs privadas e segredos em cofre privado aprovado. Este repositório,
issues públicas, commits e capturas públicas não são locais para esses dados. Registrar
a localização do cofre e o procedimento de acesso sem copiar seus segredos para cá:

- Cofre institucional aprovado: **pendente de definição**.
- Procedimento para solicitar acesso emergencial ao cofre: **pendente de definição**.
- Evidência da confirmação por responsáveis autorizados: **pendente**.

## 4. Procedimentos de acesso e transição

Os passos abaixo são um fluxo proposto para validação. Não autorizam qualquer alteração
em contas reais.

### Conceder ou revisar acesso

1. Registrar a necessidade, o recurso, o papel requerido e quem aprovou a solicitação.
2. Confirmar a identidade da pessoa por canal previamente aprovado.
3. Conceder somente o nível de acesso necessário para a função e pelo período necessário.
4. Registrar responsável, escopo, data da concessão e data ou condição de revisão.
5. Fazer revisão periódica por pessoa designada; frequência e registro oficial aguardam
   aprovação dos responsáveis.

### Transferir ou revogar acesso

1. Confirmar a pessoa substituta e o aceite da responsabilidade antes da transferência.
2. Transferir a titularidade administrativa usando os mecanismos oficiais de cada serviço,
   sem compartilhar credenciais pessoais.
3. Verificar recuperação de conta, fatores de autenticação e meios institucionais
   disponíveis, sem publicar valores ou códigos.
4. Revogar acessos que deixaram de ser necessários e revisar sessões, tokens e integrações
   segundo o procedimento aprovado para cada serviço.
5. Registrar data, recursos afetados, responsáveis e evidência não sensível da conclusão.

Mudanças de titularidade, permissões ou configuração em provedores exigem autorização
específica e execução por responsáveis humanos. Nenhuma foi realizada na preparação
deste documento.

**Plano informado por Nicolas:** adicionar Tiago, Vinicius e Gabriel como membros das
organizações dos serviços que suportarem esse modelo. As inclusões ainda não foram feitas.
Nicolas informou que alguns planos gratuitos limitam a inclusão de membros. A viabilidade
será verificada por serviço; não se presume acesso dos substitutos nem contratação paga.
Antes de conceder cada acesso, registrar o serviço e o nível necessário para a função,
evitando conceder administração ampla por padrão. Nicolas executará as alterações; esta
proposta não altera nem autoriza mudanças nos painéis.

## 5. Continuidade após o encerramento da disciplina

**Decisão informada por Nicolas:** a intenção é manter o serviço após a MDS. Nicolas
conduzirá a operação e renovação; o restante da equipe dará apoio conforme disponibilidade
e acessos que forem efetivamente concedidos. Isso registra a intenção e o responsável
principal, sem garantir disponibilidade permanente nem presumir que toda a equipe tenha
acesso às contas.

Permanecem necessários: registrar quais integrantes aceitaram apoiar, delimitar quais
atividades podem executar, manter o substituto operacional habilitado e decidir o que
ocorre se Nicolas e o substituto estiverem indisponíveis. As decisões de deploy,
manutenção, restauração e comunicação devem respeitar os acessos concedidos em cada
serviço.

### Critérios para suspender novas contribuições

Condições aprovadas por Nicolas em 15/11/2026: suspender novos cadastros,
avaliações ou comentários se não houver responsável operacional disponível, canal de
contato funcional, capacidade de encaminhar incidentes ou condição de operar os controles
aprovados. O alcance da suspensão e a mensagem aos usuários devem ser
registrados antes de uso.

## 6. Encerramento do serviço

O encerramento precisa ser aprovado pelos responsáveis designados e coordenado com as
políticas e entregas de retenção, direitos dos titulares, canal de atendimento, backup e
resposta a incidentes. Este documento não cria prazo de retenção nem promete eliminação
instantânea de dados ou backups.

Checklist proposto para um plano de encerramento aprovado:

- [ ] Decisão, data efetiva, autoridade decisora e motivo registrados.
- [ ] Aviso público preparado, com data, impacto e canal ainda acessível para solicitações.
- [ ] Canal de direitos e notificações encaminhado a uma pessoa que aceitou recebê-los.
- [ ] Novas contribuições suspensas conforme a decisão registrada.
- [ ] Dados ativos, backups e obrigações de retenção tratados conforme política validada;
      registrar o que será mantido, por qual fundamento e como será encerrado, sem expor dados.
- [ ] Provedores, domínio e custos revisados antes de cancelamento ou transferência.
- [ ] Acessos, sessões, tokens e integrações revogados pelos responsáveis, com evidência
      não sensível.
- [ ] Registro final preservado sem credenciais, dados pessoais desnecessários ou segredos.

Os critérios detalhados de retenção e exclusão dependem das decisões e revisões jurídicas
das issues relacionadas, em especial #261 e #262. O canal de direitos depende do contrato
e dos responsáveis definidos nas issues #262 e #263; resposta a incidente e recuperação
devem ser alinhadas com #267. A lista de dependências do épico #272 indica revisão de
impacto, não aprovação automática nem obrigação de mudar entregas compatíveis.

## 7. Exercício de mesa: saída do administrador principal

Este roteiro descreve a validação sem alterar contas, permissões, DNS, serviços, backups
ou dados reais. Nicolas informou que os exercícios de mesa já foram realizados.

**Registro informado:** em 15/11/2026, participaram Nicolas Zanin e Gabriel. Tiago Vieira
sugeriu os cenários, gerados com apoio do GPT. Nicolas informou que as lacunas estão
registradas nas issues relacionadas ao épico #272.

1. Simular que o administrador principal ficou indisponível imediatamente.
2. Pedir ao substituto que localize este procedimento, os responsáveis aceitos, o canal de
   solicitação de acesso ao cofre e as instruções de recuperação sem usar credenciais
   publicadas ou depender de contato privado com o administrador ausente.
3. Simular uma falha de serviço e uma solicitação de titular recebida durante a ausência.
4. Verificar se o substituto sabe quem pode decidir suspender contribuições, comunicar a
   indisponibilidade e encaminhar a solicitação sem prometer prazo ou resultado não aprovado.
5. Simular a decisão de manter ou encerrar o serviço e apontar quais documentos, políticas
   e aprovações ainda faltariam.
6. Confirmar que o substituto consegue localizar os procedimentos e canais sem ajuda
   privada do administrador ausente; verificar que nenhum passo depende de credenciais,
   tokens ou identificadores secretos publicados no repositório.
7. Registrar lacunas, impacto, responsável por resolver, prazo acordado e issue relacionada.
   Não encerrar pendência sem conferir a correção.

| Verificação no exercício | Resultado esperado | Resultado / evidência |
|---|---|---|
| Substituto encontra este procedimento e localiza os papéis vigentes | Documento acessível sem ajuda privada do administrador ausente | Exercício realizado; lacunas referenciadas nas issues relacionadas, conforme Nicolas |
| Substituto identifica canal privado para solicitar recuperação de acesso | Canal aprovado, acessível e sem segredo neste repositório | Canal permanece pendente; lacunas referenciadas nas issues relacionadas |
| Substituto explica como encaminhar solicitação de titular e notificação jurídica | Contatos aceitos e instrução de encaminhamento disponíveis | Exercício realizado; lacunas referenciadas nas issues relacionadas, conforme Nicolas |
| Substituto sabe quem pode decidir suspender contribuições ou encerrar o serviço | Autoridade decisora e procedimento registrados | Exercício realizado; lacunas referenciadas nas issues relacionadas, conforme Nicolas |
| Participantes concluem o cenário sem depender de credencial publicada | Nenhum segredo ou identificador privado precisa ser exposto | Exercício realizado; lacunas referenciadas nas issues relacionadas, conforme Nicolas |

**Resultado reportado por Nicolas:** exercícios de mesa realizados em 15/11/2026 com
Nicolas Zanin e Gabriel; Tiago Vieira sugeriu cenários, gerados com apoio do GPT. As
lacunas estão rastreadas nas issues relacionadas ao épico #272, conforme relato de
Nicolas. Não foi fornecida ata separada nem resultado por item neste documento.

**Registro da execução:** data 15/11/2026; participantes Nicolas Zanin e Gabriel;
contribuição de cenários por Tiago Vieira e GPT; lacunas referenciadas às issues do épico
#272; ata/evidência não sensível separada não fornecida.

## 8. Revisão, aceite e pendências

### Rastreabilidade dos critérios da issue #260

| Critério | Evidência neste documento | Estado para aceite |
|---|---|---|
| Designar papéis de tratamento, operação, privacidade e notificações; indicar substitutos e aceite | Matriz de papéis da seção 2 | Parcial: Nicolas, Tiago, Vinicius e Gabriel registrados com aceites reportados por Nicolas; contatos de trabalho e canais pendentes |
| Inventariar titularidade, contas institucionais/organizacionais, renovação e recuperação | Nicolas declarou ser titular e responder por renovação de todos os serviços; recuperação pelo e-mail sob seu controle | Parcial; disponibilidade organizacional, confirmação de e-mail em cada serviço e vencimento do domínio pendentes; painéis não inspecionados |
| Definir concessão, revisão, transferência e revogação com menor privilégio | Fluxo da seção 4; plano de incluir Tiago, Vinicius e Gabriel onde houver organizações | Procedimento registrado; inclusões ainda não feitas e permissões por serviço ainda a conferir |
| Registrar continuidade após MDS, disponibilidade, suspensão de contribuições e decisão sobre manter/encerrar | Seção 5 registra manutenção por Nicolas com apoio da equipe e condições de suspensão aprovadas por ele | Acessos de substitutos sujeitos às limitações dos planos; cobertura deve ser conferida por serviço |
| Definir encerramento com aviso, canal acessível, dados/backups e revogação de acessos | Checklist da seção 6 | Parcial; depende de canal e política de retenção/exclusão aprovados |
| Explicitar independência estudantil, ausência de endosso comprovado e distinção da avaliação oficial da UnB | Declaração da seção 1 | Texto preparado; revisão humana antes de publicação |
| Validar em exercício de mesa, registrar lacunas, responsáveis e aceite | Seção 7 registra exercícios em 15/11/2026 com Nicolas Zanin e Gabriel; Tiago sugeriu e GPT gerou cenários | Realizado conforme relato de Nicolas; lacunas remetidas às issues do épico #272; sem ata separada |

| Revisão necessária | Responsável | Evidência / data | Estado |
|---|---|---|---|
| Confirmar pessoas, substitutos, contatos de trabalho e aceite de cada papel | Nicolas Zanin aceitou operação/renovação; Tiago Vieira, Vinicius Gavaldao e Gabriel aceites conforme confirmação de Nicolas | Sobrenome de Gabriel, contatos de trabalho e canais pendentes | `Pending Decision` |
| Registrar titularidade administrativa, acessos efetivos, vencimentos e recuperação de cada conta | Nicolas declarou titularidade/renovação; recuperação pelo e-mail sob seu controle | Confirmar e-mail em cada serviço, disponibilidade de conta organizacional, acessos e vencimento do domínio | `Pending Decision` |
| Qualificação jurídica de controlador, operadores, representação e eventual encarregado | Sem especialista disponível; não inferir qualificação nesta proposta | Pendência registrada; não bloqueia a preparação operacional, mas não equivale a validação jurídica | `Pending Decision` |
| Revisar consistência com inventário de tratamentos e fornecedores (#261) | Responsável da entrega a designar | Pendente | `Pending Decision` |
| Alinhar canal, retenção, exclusão e encerramento (#262, #263, #267) | Responsáveis dessas entregas | Pendente | `Pending Decision` |
| Registrar resultado do exercício de mesa, sem alterar contas reais | Nicolas relata exercícios de 15/11/2026 com Gabriel; Tiago sugeriu e GPT gerou cenários | Lacunas referenciadas nas issues relacionadas ao épico #272; sem ata separada | `Proposed` |
| Aprovar e publicar a versão final | Autoridade humana a confirmar | Pendente | `Pending Decision` |

## Histórico de revisão

### Encaminhamento das pendências

As issues abaixo são destinos de conciliação documental; sua abertura não significa que
os insumos já tenham sido aprovados ou entregues. Nicolas acompanha a retomada das
pendências operacionais desta entrega. Responsáveis e datas das demais entregas devem
ser confirmados no acompanhamento do épico.

| Pendência | Destino | Retomada necessária |
|---|---|---|
| Canal público e encaminhamento restrito a Vinicius/Gabriel | [#263](https://github.com/unb-mds/2026-02-UnDb/issues/263) | Incluir o canal aprovado e conferir acesso dos responsáveis |
| Papéis de tratamento e inventário de fornecedores | [#261](https://github.com/unb-mds/2026-02-UnDb/issues/261) | Conciliar quem decide finalidades/meios; manter qualificação jurídica não validada explícita |
| Retenção, direitos e destino dos dados no encerramento | [#262](https://github.com/unb-mds/2026-02-UnDb/issues/262) | Incorporar a matriz aprovada ao procedimento de encerramento |
| Incidentes, recuperação e backups | [#267](https://github.com/unb-mds/2026-02-UnDb/issues/267) | Conciliar canais privados, substituição e recuperação com o plano desta entrega |
| Inclusão dos membros nos provedores e recuperação independente de Nicolas | #260 / Nicolas Zanin | Registrar convites aceitos e permissões mínimas por serviço, sem publicar identificadores privados |

O exercício relatado por Nicolas identifica as lacunas por referência ao backlog; não
comprova, por si só, que um substituto recuperou acesso sem Nicolas ou que todos os passos
do roteiro acima foram executados. Os resultados individuais permanecem não verificados.

### Alterações registradas

| Data | Alteração | Estado |
|---|---|---|
| 15/11/2026 | Proposta documental para a issue #260; Nicolas Zanin declarou titularidade e aceitou operação/renovação, com apoio da equipe. Confirmou os aceites de Tiago Vieira (substituto operacional), Vinicius Gavaldao (contato de privacidade/notificações) e Gabriel (substituto de Vinicius). Registrou exercícios com Gabriel; Tiago sugeriu e GPT gerou os cenários. Lacunas remetidas às issues relacionadas ao épico #272. Canais ficam pendentes para alinhamento com #263. | Parcial; conferência das contas e demais validações pendentes |
