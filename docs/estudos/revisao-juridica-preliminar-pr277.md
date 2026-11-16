# Análise jurídica preliminar — PR #277

Data de corte: **16/11/2026, America/Sao_Paulo**. Versão examinada: `3708fdc`.
Origem: solicitação de Gabriel para preparar todos os pontos jurídicos pendentes da
[PR #277](https://github.com/unb-mds/2026-02-UnDb/pull/277), com fontes oficiais e casos
de borda. Os aceites A1–A8 estão no [registro de revisão](revisao-pr277.md).

**Estado:** análise documental preparada; não é parecer de advogado, certificação de
conformidade, aprovação de políticas ou autorização de publicação/merge. As conclusões
abaixo são recomendações e inferências identificadas, não novos requisitos aprovados.
Nenhum painel, produção, segredo ou dado privado foi acessado. Nenhum caso concreto de
ilícito ou incidente foi investigado. A cobertura é delimitada, sem garantia de exaustividade.

## 1. Resultado para esta PR

Recomendo preservar os textos aprovados sobre independência, autoria, amostras,
confirmação de e-mail, mínimo e moderação. Eles descrevem limites observáveis e não
precisam ganhar cláusulas de exoneração de responsabilidade. Não identifiquei fundamento
para apresentar a equipe como representante da UnB, órgão de pesquisa ou serviço
certificado. A PR melhora a transparência, mas não entrega sozinha a conformidade da operação.

A preparação desta análise fica concluída. Permanecem verificações materiais sobre
agentes de tratamento, bases legais, operação do canal, retenção, contratos e público
menor de idade. Esses pontos têm destinos na seção 5. Recomendo não ativar ou anunciar
de controles ainda não homologados. FGA permanece fora da entrega atual, conforme A7.

## 2. Fontes e limites de consulta

Todas as referências são públicas e oficiais. Leis e decisões prevalecem sobre guias,
notícias institucionais e esta análise. A legislação deve ser reconferida na data da decisão.

| ID | Fonte consultada | Uso e limite |
|---|---|---|
| S1 | [Constituição, texto da Câmara](https://www2.camara.leg.br/atividade-legislativa/legislacao/constituicao1988/arquivos/ConstituicaoTextoAtualizado_EC%20141.html), art. 5º, IV, V, IX, X e LXXIX | Expressão, resposta, personalidade e proteção de dados |
| S2 | [LGPD, Câmara](https://www2.camara.leg.br/legin/fed/lei/2018/lei-13709-14-agosto-2018-787077-normaatualizada-pl.html) e [cópia oficial no MME](https://www.gov.br/mme/pt-br/acesso-a-informacao/acoes-e-programas/governanca/programa-de-integridade/normativos/l13709_lgpd.pdf) | O HTML retornou 429; a cópia PDF é de 04/11/2025, não comprova todas as alterações posteriores. Artigos materiais citados foram lidos; atualização integral em 2026 ainda requer conferência |
| S3 | [ANPD: fins acadêmicos, guia](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/web-guia-anpd-tratamento-de-dados-para-fins-academicos.pdf/@@display-file/file), pp. 18–25 e 30–41 | Limites da exceção acadêmica, base e identificação; orientação, não dispensa geral |
| S4 | [Código Civil, Câmara](https://www2.camara.leg.br/legin/fed/lei/2002/lei-10406-10-janeiro-2002-432893-normaatualizada-pl.html), arts. 18–21 | Consulta por trechos indexados; abertura retornou 429. Não se presume ilicitude pela mera crítica |
| S5 | [Marco Civil, Câmara, publicação original](https://www2.camara.leg.br/legin/fed/lei/2014/lei-12965-23-abril-2014-778630-publicacaooriginal-143980-pl.html) | Lido junto a STF e decretos; link de versão atualizada retornou 404 |
| S6 | [STF, Tema 533: tese e andamento](https://portal.stf.jus.br/jurisprudenciaRepercussao/verAndamentoProcesso.asp?classeProcesso=RE&incidente=5217273&numeroTema=533) e [Tema 987](https://portal.stf.jus.br/processos/detalhe.asp?incidente=5160549) | A página 533 expõe tese e embargos de 2026, inclusive suspensão para proclamação; não afirmar trânsito ou usar voto isolado como tese final. A página 987 não expôs integralmente a aba de andamentos |
| S7 | [Decreto 12.975/2026, texto no MJ](https://bibliotecadigital.mj.gov.br/bitstream/1/17151/1/DEC_PR_2026_12975.html) | Deveres gerais, notificação, honra, devido processo, representação e transparência |
| S8 | [Decreto 12.976/2026, texto no MJ](https://bibliotecadigital.mj.gov.br/bitstream/1/17152/1/DEC_PR_2026_12976.html) | Violência contra mulheres, atendimento prioritário e hipóteses específicas |
| S9 | [ANPD: Marco Civil e FAQ](https://www.gov.br/anpd/pt-br/assuntos/marco-civil-da-internet) | Explica novos deveres e fiscalização; cronograma regulatório não equivale a dispensa de lei |
| S10 | [Lei 15.211/2025, Câmara](https://www2.camara.leg.br/legin/fed/lei/2025/lei-15211-17-setembro-2025-797997-normaatualizada-pl.pdf), arts. 1º–3º, 7º, 16 e 27–33 | ECA Digital e acesso provável; não pressupor que universitário é maior |
| S11 | [ANPD, Enunciado 1/2023](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/tratamento_de_dados_de_criancas_e_adolescentes.pdf) | Hipóteses legais e melhor interesse de crianças/adolescentes |
| S12 | [ANPD, Resolução 19/2024](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/resolucao-cd-anpd-no-19-de-23-de-agosto-de-2024) | Transferência internacional: base e mecanismo próprios; página indica retificação de 2025 |
| S13 | [ANPD, Resolução 2/2022](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd/resolucao-cd-anpd-no-2-de-27-de-janeiro-de-2022) | Pequeno porte não significa isenção; enquadramento e alto risco precisam ser avaliados |
| S14 | [UnB: gestão e uso da marca](https://marca.unb.br/index.php) | Não autoriza uso de marca por esta análise; não foi feita busca de anterioridade no INPI |
| S15 | [ANPD: agentes de tratamento](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-orientativo-para-definicoes-dos-agentes-de-tratamento-de-dados-pessoais-e-do-encarregado) | Referência para qualificar papéis pelas decisões reais, não por título de responsável de issue |

O Planalto apresentou desafio automatizado nas tentativas de LGPD, MCI e decretos;
não foi contornado. Foram usadas as alternativas oficiais acima. Não foi concluída
pesquisa exaustiva de todos os processos, portarias ou atos infralegais posteriores.
Em particular, prazos, alcance das teses e regulamentação de 2026 precisam ser
reconferidos antes de assumir obrigação operacional ou publicar condição contratual.

Na reconferência, o índice da Câmara indicou alterações de 2026 na LGPD; o
[catálogo do Senado](https://www2.senado.leg.br/bdsf/handle/id/962304) indicou edição
atualizada até julho de 2026. As tentativas de abrir esses textos integrais não
concluíram. Assim, a cópia de 2025 não foi apresentada como consolidação vigente.

## 3. Evidência do projeto

Foram lidos arquivos locais em `3708fdc`; os caminhos abaixo são referências de código,
não prova de configuração em produção:

| Evidência | Constatação |
|---|---|
| `frontend/src/app/page.tsx` e `sobre/page.tsx` | Independência, critérios separados, limites e triagem condicional. Não há alegação FGA no texto público |
| `backend/app/models/avaliacao.py` | Avaliação mantém `usuario_id`, professor e disciplina; unicidade por conta/par |
| `backend/app/schemas/comentario.py` | Resposta pública tem ID do comentário, texto e data; resposta do autor tem campos adicionais |
| `backend/app/schemas/auth.py` e `models/usuario.py` | Cadastro não pede idade e não registra versão/ciência de Termos; e-mail institucional não prova idade, matrícula ou experiência |
| `backend/app/services/openai_triagem.py` | Integração pode enviar o texto original à API externa de moderação; isso não prova anonimização, retenção ou região do fornecedor |
| `backend/app/services/solicitacao_titular_service.py` | Recebimento condicionado a flags e atendentes; protocolo/chave, allowlists e histórico separado; nenhum cumprimento automático de direitos |
| `docs/canal-titulares.md` e `continuidade-operacional.md` | Contrato e papéis operacionais, com retenção/ativação/qualificação jurídica ainda a conciliar |
| `frontend/src/components/rodape.tsx` e árvore de rotas | Links de contato; não há `/privacidade` ou `/termos-de-uso` nesta base |

Não foi auditada a aplicação inteira, o histórico Git, o comportamento de provedores,
CDN ou cookies de terceiros. Segurança de sessão/logs continua em #266 e incidentes
em #267. A análise não expõe credenciais nem reproduz identidade de avaliadores.

## 4. Avaliação dos quatro temas

### 4.1 Independência e ausência de endosso

**Conclusão proposta:** manter A1. A descrição reduz confusão institucional, mas não
define pessoa jurídica, controlador ou representante. A ANPD orienta analisar a
finalidade de cada tratamento: chamar o projeto de acadêmico não exclui todas as
obrigações nem demonstra qualificação como órgão de pesquisa (S3).

**Aplicação ao UnDb:** não atribuir responsabilidades à UnB por nomes, domínio de
e-mail ou origem SIGAA. Conferir também identidade visual, metadados e imagens de
compartilhamento; a frase de independência não substitui exame de marca (S14).
Se o serviço mudar de operador, receber patrocínio ou ganhar publicidade, reavaliar
descrição, papéis e contratos. As pessoas responsáveis por issues não se tornam
controladores, encarregados ou representantes legais apenas por essa designação (S15).

### 4.2 Opiniões, amostras, honra e responsabilidade

**Conclusão proposta:** manter A3/A4/A6. Recomendo ler ausência de garantia de veracidade
como limite metodológico, sem excluir responsabilidade por atos da plataforma. A
Constituição protege expressão e personalidade; o Código Civil protege nome/imagem e
vida privada (S1/S4). Não classificar toda nota baixa como ataque, nem toda acusação
como opinião protegida.

O STF distingue hipóteses de responsabilização, inclusive honra, e prevê mecanismos
de atendimento e transparência; o andamento exige cuidado com os embargos (S6).
Não usar a antiga leitura de que só se age após ordem judicial para todos os casos.
O Decreto 12.975 detalha identificação da notificação, motivação, contestação,
preservação da crítica contextual e outras obrigações (S7). Aplicabilidade concreta,
representação e procedimentos precisam de validação, sem inventar enquadramento.

**Aplicação:** denúncia simples e notificação jurídica são percursos distintos. Uma
denúncia de visitante continua útil mesmo sem cumprir formalidades de notificação.
O limiar de 50 da suspensão automática não pode virar requisito de atendimento.
Reter ou remover texto não deve invalidar notas pelo mesmo comando; fraude numérica
segue #270. Reclamação do docente não autoriza revelar o aluno nem remover crítica
automaticamente. Homônimos e associação errada de docente exigem #263/RF23.

Há situações especiais que não cabem em prazo genérico: S8 prevê, para suas hipóteses,
duas horas para conteúdo íntimo, seis/24 horas em disposições transitórias e tratamento
de contestação. Não aplicar esses valores como SLA universal nem prometer cumprimento
sem operação. Não oferecer uploads íntimos como forma de prova; links/textos também
podem carregar esse risco. A política atual de sete dias precisa ser conciliada com
preservação legal e comunicação às autoridades, sem alteração silenciosa (S8, #262/#267).

### 4.3 Autoria, identificação e dados pessoais

**Conclusão proposta:** manter A2 e o aviso de que três não garante anonimato. Ocultar
nome publicamente não remove o vínculo interno. Texto, data e comparações temporais
podem tornar alguém identificável; docentes também são titulares. A LGPD trata de
necessidade, transparência, direitos e segurança e limita a alegação de anonimização
(S2). Dados públicos não são autorização irrestrita de reutilização.

**Aplicação:** #261 deve justificar por operação cadastro/sessão, catálogo docente,
avaliação, texto, moderação, atendimento, logs e antifraude. Não presumir consentimento
de docentes dado pelos alunos, nem usar ciência dos Termos como base para tudo.
Saúde, religião, sexualidade e outros dados sensíveis em texto exigem avaliação própria.
Pedidos de acesso, correção, eliminação, oposição e revisão precisam de identidade
proporcional, sem expor dados de terceiros; nem todo pedido autoriza eliminação imediata.

O payload da IA pode conter dados pessoais mesmo depois do filtro. Identificar países,
suboperadores, contratos, usos adicionais e mecanismo de transferência, caso exista
transferência internacional, além da hipótese legal (S12). Esta análise não afirma
qual contrato/retenção/região está em uso. Pequeno porte não afasta automaticamente
deveres ou o exame de risco (S13).

Menores podem ler o site, denunciar ou ter conta universitária. O ECA Digital abrange
serviços de acesso provável, e a ANPD exige melhor interesse na escolha de hipótese
legal (S10/S11). Não concluir que confirmação de e-mail resolve isso; não adicionar
coleta de documentos, idade ou dados parentais sem análise e aprovação do requisito.

### 4.4 Política de Privacidade e Termos

**Conclusão proposta:** preparar #268/#269 usando somente práticas confirmadas. O Sobre
não é substituto desses documentos. Não publicar placeholders de controlador, canal,
fornecedores ou retenção. Não prometer resposta por e-mail, recurso, exclusão total ou
suporte permanente que ainda não tenham sido implementados/homologados.

Recomendo que a Política cubra agentes/contato, dados/finalidades, bases por operação,
origem, acesso interno, fornecedores/transferências, retenção, direitos, menores e
versão. Os Termos devem tratar finalidade, participação, crítica legítima, condutas
proibidas, regras reais de moderação, notificação, contestação, limites metodológicos,
conteúdo dos usuários, mudanças e encerramento. Evitar renúncia geral a direitos,
licença irrestrita para outras finalidades e exoneração absoluta da equipe.

O registro de ciência deve ser separado de consentimentos específicos, guardar versão
e permitir leitura prévia. Contas anteriores, recusa de nova versão e mudanças
materiais precisam de decisão antes da implementação. Se houver relação de consumo,
remuneração direta/indireta, anúncios ou patrocínio, validar também o regime aplicável;
gratuidade não é conclusão suficiente. Não copiar foro ou imunidade de plataforma estrangeira.

## 5. Lacunas, responsáveis e condições de conclusão

| ID | Constatação ou hipótese | Próxima ação / destino |
|---|---|---|
| J1 | Qualificação jurídica da equipe/representação não comprovada | #261 com #260: identificar decisores e agente/representante, base e contato. Nicolas opera; isso não decide qualificação jurídica |
| J2 | Canal existe no código, operação atual não verificada | #263 com #262/#264: homologar atendimento acessível a não usuários, inclusive urgências, e registrar versão/capacidade real |
| J3 | Revisão/escalonamento e comunicações completos ainda pendentes | Warlley, #264: procedimentos motivados, impedimentos, contestação e reconciliação dos prazos especiais |
| J4 | Contratos, bases e transferências não validados | #261; refletir em #268. Conferir IA/hospedagem/e-mail e proibir promessas sem evidência |
| J5 | Identificação indireta e acesso interno precisam de avaliação | Yasmin, #265: matriz de campos/atores, pequenas amostras e tempo, revisão de permissões sem removê-las por suposição |
| J6 | Retenção geral, exclusão e preservação precisam de conciliação | #262 com #267: categorias, eventos, backups e exceções legais delimitadas; sete dias não são prazo universal |
| J7 | Público menor e obrigações de 2026 não avaliados no produto | #261/#265/#269, PO e validação jurídica: enquadramento, riscos, capacidade e medidas proporcionais antes de mudar cadastro |
| J8 | Política e Termos ausentes nesta base | Gabriel, #268/#269: redigir, validar práticas e aprovar versões antes de publicar; retomar Home/Sobre conforme A8 |
| J9 | Uso de marca não foi examinado integralmente | #271/PO: verificar ativos e uso institucional; consultar UnB quando necessário, sem presumir endosso |

Essas lacunas não são todas bugs introduzidos pela PR e não significam encerramento
obrigatório de todas as issues para cada correção editorial. São condições relevantes
de operação, publicação de políticas e interpretação jurídica. Não declarar a PR ou o
serviço juridicamente homologados apenas por testes, merge ou esta análise.

## 6. Pacote de validação e aprovação futura

Usar os [casos de mesa](casos-juridicos-pr277.md), sem dados reais. Para cada conclusão,
registrar versão, responsável, fonte, evidência e limitações. Recomendo esta ordem:

1. Qualificar agentes e contato; inventariar tratamentos e público efetivo.
2. Conciliar canal, urgências, contestação, retenção e preservação com fontes atuais.
3. Avaliar acesso/identificação, menores e fornecedores; documentar decisões.
4. Finalizar Política/Termos, versões e ciência; confrontar cada afirmação com evidência.
5. Obter validação jurídica identificada e aceite humano do pacote, com exceções explícitas.

Nenhuma aprovação foi presumida. Até lá, estado correto: análise preliminar preparada,
textos com aceites editoriais, pendências jurídicas/operacionais identificadas.

### Verificação documental desta preparação

Build estrito do MkDocs concluído em 16/11/2026. Foram conferidos os links locais
dos três documentos e a presença, sem repetição, de J1–J9 e C01–C36. A matriz não
foi executada contra a aplicação. Não foram repetidas as suítes de software, pois
esta preparação altera apenas documentação e navegação documental.
