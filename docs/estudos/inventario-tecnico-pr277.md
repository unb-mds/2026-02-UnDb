# Inventário técnico de tratamentos — PR #277

Data: 16/11/2026 (America/Sao_Paulo). Fonte: código de `794be68` e correção de cache
descrita na [verificação](verificacao-pendencias-pr277.md). Escopo: insumos de J1–J8
para #261/#262/#264/#265/#268/#269; não é inventário jurídico aprovado ou auditoria
de produção. Nenhuma consulta a banco real, painel ou segredo foi feita.

Gabriel informou que Nicolas responde pelos fatos operacionais e pediu deixá-los
pendentes enquanto avançamos nas partes independentes. As perguntas estão
[na PR](https://github.com/unb-mds/2026-02-UnDb/pull/277#issuecomment-6917996624).
Atribuição de acompanhamento não define controlador, operador ou encarregado.

## 1. Operações e necessidade técnica observada

Em todas as linhas, **base legal, prazo geral de guarda, configuração em produção e
qualificação dos agentes permanecem pendentes**. A necessidade descrita é técnica,
não conclusão de proporcionalidade jurídica. Não se usa consentimento genérico nem
dispensa acadêmica como justificativa automática. Para direitos e fornecedores,
conferir também a [análise preliminar e fontes](revisao-juridica-preliminar-pr277.md).

| ID | Titular, origem e dados | Finalidade / necessidade observada | Armazenamento, acesso e destinatários previstos no código |
|---|---|---|---|
| T01 | Pessoa cadastrada: nome, e-mail institucional, hash de senha, UUID, confirmação, papéis, criação | Cadastro/login; nome é exibição e e-mail é identificador da conta. Necessidade do nome em cada uso privado requer validação | `usuarios`; autor vê a própria sessão; moderação acessa identidades conforme RF22; infraestrutura acessa banco conforme permissões reais, ainda a conferir |
| T02 | Pessoa cadastrada: token de confirmação, hash, validade, uso e vínculo com conta | Comprovar controle do endereço, sem provar matrícula ou experiência | `email_confirmation_tokens`; token aberto segue no link ao e-mail/Resend e ao frontend; não é publicado na consulta de avaliações |
| T03 | Usuário autenticado: token de sessão, hash, UUID e datas | Autenticação e renovação; hash persistido permite validar/revogar sem guardar token aberto no banco | `sessoes_usuario`; cookie `undb_session`, HttpOnly, SameSite=Lax e Secure quando DEBUG=False. Configuração hospedada não verificada |
| T04 | Pessoa que recupera conta: e-mail, token/link, hash, validade e uso | Recuperação e revogação de sessões/links; resposta neutra reduz enumeração | `password_reset_tokens`; link ao frontend e provedor de e-mail; não confundir validade com eliminação de registros expirados |
| T05 | Docentes: nome, nome normalizado, unidade, SIAPE quando disponível, origem e confirmação | Catálogo e reconciliação entre ofertas; nome isolado não prova identidade. SIAPE distingue identidades, mas necessidade de sua divulgação exige revisão | `professores`; detalhe/listagem pública têm `siape` e `identidade_confirmada`. Fonte declarada: SIGAA público; isso não dispensa análise de finalidade/base |
| T06 | Docentes/ofertas: unidades, disciplinas, códigos, turma, semestre, vínculos e situação | Contextualizar professor–disciplina e preservar histórico de ofertas | `unidades`, `disciplinas`, `turmas` e `turmas_professores`; catálogo público. Não contém matrícula ou histórico individual do estudante nesses modelos |
| T07 | Docentes e revisores: candidatos, identificadores/perfis, pendência, justificativa, autor/data/versão e correspondências | Resolver homônimos e manter rastreabilidade, sem fusão por nome somente | `identidades_docentes`, `identidades_locais`, `pendencias_identidade`, `decisoes_identidade`, `professor_correspondencias`; revisão exige papel reconciliador confirmado, distinto da moderação de texto |
| T08 | Docentes/operadores: execução, período, unidades, contagens, resultado JSON e erro de importação | Acompanhar extração e reconciliação; mensagens/JSON podem reproduzir dados de origem | `importacao_execucoes` e saídas do importador; destinatários efetivos dos logs/artefatos precisam de inventário operacional; não publicar erros brutos sem revisão |
| T09 | Avaliador e docente: vínculo `usuario_id`, professor/disciplina, cinco critérios e datas | Unicidade/substituição e agregação; vínculo interno permite autoria. Removê-lo exigiria nova decisão de integridade/direitos | `avaliacoes`; resposta de criação é do autor. Consulta pública usa agregado/contagem, com critérios omitidos abaixo de três; não publica notas individuais |
| T10 | Autor, docente e terceiros eventualmente citados: texto, versão, estado, avaliação, substituição e datas | Comentários opcionais, publicação, revisão e retirada; texto pode identificar pessoas e conter dados sensíveis | `comentario_versoes`; público recebe ID da versão/texto/data somente se publicado; autor tem seus estados e vínculos. Texto pendente não vira público por existir no banco |
| T11 | Denunciante e docente/autor: motivo, versão, conta opcional e data | Denunciar e impedir duplicidade por conta; visitante não tem identidade cadastrada | `denuncias`; detalhe restrito a moderador autorizado. Denúncia simples não identifica formalmente todo visitante e não comprova ilicitude |
| T12 | Autor, denunciante e moderador: ação, motivo, estados, versão, moderador opcional e datas | Justificar decisões e impedir atuação em caso próprio conforme RF22 | `decisoes_moderacao`; autor e denunciantes identificados aparecem internamente conforme schemas aprovados. Decisão automática tem moderador nulo e motivo do sistema |
| T13 | Denunciante autenticado: mensagem de agradecimento, usuário, versão, evento e data | Informar suspensão/remoção; não revela lista de denunciantes ao público | `agradecimentos`; consulta e confirmação por usuário autenticado; encerramento de denúncia e exibição da mensagem seguem fluxos distintos |
| T14 | Autor/terceiros: texto integral elegível à IA e resultado categórico | Apoio à triagem; filtro não comprova anonimização. Envio depende das flags, aprovação de dados, configuração e cotas | `openai_triagem.py`: Moderations API; sem geração ou fallback pago. Países, contrato, usos adicionais, retenção e suboperadores não confirmados; não afirmar ausência de dados pessoais |
| T15 | Solicitante, pessoas citadas e atendentes: categoria, alvo, descrição, evidência textual, protocolo, hash de chave, complementos, triagem, providências, resposta e datas | Atendimento sem conta e acompanhamento com segredo; separar resposta pública ao portador da chave de notas internas | `solicitacoes_titulares`, `eventos_solicitacoes`; sem e-mail obrigatório/upload/IA. Portador da chave vê RESPOSTA/COMPLEMENTO; allowlists separam leitura e atendimento; responsáveis por UUID, não nome |
| T16 | Cliente do canal: endereço do cliente transformado em HMAC e orçamento temporário | Limitar tentativas por processo sem persistir o endereço no orçamento | `limite_atendimento.py`: memória, janela de 60 segundos, até 4096 entradas; sem interpretar X-Forwarded-For. Isso não descreve logs do servidor/proxy nem proteção distribuída |
| T17 | Visitantes/contas: IP, URL, cabeçalhos, eventos HTTP e possíveis dados de erro | Operação e segurança; coleta efetiva, necessidade e destinos dependem do ambiente | Console, Uvicorn, hospedagem, CDN e monitoramento precisam de conferência. Em `EMAIL_BACKEND=console`, o código registra e-mail/link: não declarar logs livres de dados pessoais |
| T18 | Todas as categorias eventualmente copiadas em backup/exportação | Recuperação operacional; cópias não são apagadas pela mera retirada de texto | Arquivos, restaurações e backups dos provedores não foram inspecionados. Locais, leitores, expiração, reexecução de exclusões e preservação dependem de #262/#267 e Nicolas |

## 2. Validade, retenção e descarte: diferenças comprovadas

| Categoria | Comportamento do código | Lacuna a resolver antes de afirmar prazo geral |
|---|---|---|
| Confirmação de e-mail | Link vence em 24 horas; marca `used_at` | Expirar não comprova descarte periódico do registro, conta não confirmada ou logs |
| Sessão | Sete dias após última atividade válida; renovação; logout remove sessão; sessão expirada consultada é removida | Não equivale a rotina global de limpeza nem ao prazo de logs/backups |
| Recuperação | Uma hora e uso único; redefinição invalida links e sessões conforme serviço | Não comprova eliminação de todos os registros expirados ou e-mails já entregues |
| Texto retirado/removido e decisão | Serviço usa sete dias; rotina elimina decisões vencidas e limpa texto de estados RETIRADO/REMOVIDO; pendentes/suspensos são preservados | O prazo não abrange todo o banco; execução contínua hospedada, exceções de preservação, dados residuais e backups precisam de conciliação |
| Denúncias/agradecimentos | Encerramento elimina denúncias; agradecimento tem ciclo próprio | Não são arquivo jurídico permanente; não prolongar guarda para recurso por conveniência |
| Canal | Não há prazo geral de descarte implementado; ativação exige retenção aprovada e atendentes configurados | Definir categorias, evento inicial/final, histórico, chave, solicitações em curso e exceções antes da ativação |
| Catálogo, avaliações, identidades, importações | Persistência sem prazo geral de eliminação definido nesses modelos | Delimitar atualização, direitos, integridade, necessidade histórica e eventual preservação |
| HMAC do canal | Expiração em memória após 60 segundos; reinício perde orçamento | Não generalizar esse valor a IPs/logs de borda ou múltiplas instâncias |

Nenhum prazo novo foi escolhido. Decisão de retenção deve definir categoria, finalidade,
evento, prazo/condição, responsável, rotina, evidência, exceção e fim da exceção. Para
restauração, reaplicar exclusões antes de reexpor os dados e registrar prova sintética;
esse procedimento continua dependente de aprovação e capacidade operacional reais.

## 3. Fornecedores: fato documental e confirmação pendente

| Serviço | Evidência disponível | O que Nicolas precisa confirmar |
|---|---|---|
| Vercel | `docs/hospedagem.md`: frontend no Hobby, branch pública observada `main` | Titular/contrato/plano atual, países e subprocessamento, logs/cache, retenção e acessos |
| Render | Documento registra API Free/Docker; `/health` não consulta banco | Região/plano/contrato atual, disponibilidade, logs/proxy, descarte, acessos e continuidade |
| Neon | Documento registra PostgreSQL Free e conexão da API/importador | Região/branch real, papéis, backups/restore, expiração, contrato e acessos |
| Resend | Documento registra envio transacional; código envia destinatário e link | Contrato, região de processamento além do painel, suboperadores, e-mails/logs e retenção |
| OpenAI | Endpoint de moderação e payload estão no código; ativação foi registrada na #239 | Projeto/contrato/configuração atual, retenção, usos, países/suboperadores e transferência |
| Registro.br | Documento registra domínio/DNS e titularidade declarada | Titularidade, renovação, recuperação e contato público aprovado; sem publicar dados privados da conta |

Não inferir contrato aplicável apenas de página comercial. Eventual transferência
internacional exige identificar a operação concreta e o mecanismo pertinente; nenhum
contrato foi aceito ou provedor reconfigurado por esta revisão.

## 4. Decisões jurídicas a derivar do inventário

Conferir separadamente base para conta/autenticação, catálogo, avaliações, publicação,
moderação, IA, atendimento e segurança. A base escolhida deve atender à finalidade
real, ao titular e à categoria; dado sensível exige análise própria. Aceite de Termos
não é consentimento de docentes ou autorização para qualquer finalidade.

Se for considerada a hipótese de legítimo interesse, registrar finalidade concreta,
necessidade e alternativas, expectativa/impacto, balanceamento e salvaguardas, por
operação. A [ANPD oferece modelo orientativo](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/copy_of_guia_legitimo_interesse.pdf/@@download/file).
Este inventário não conclui esse teste nem autoriza a base para dados sensíveis.

## 5. Entrega e pendências

Mapeamento técnico preparado com evidência local e sem dados reais. Yasmin mantém o
destino #261/#265; Warlley, #262/#264; Gabriel, #268/#269, conforme atribuições do
GitHub e A8, sem presumir aceite novo. Nicolas fornece os fatos que Gabriel decidiu
deixar pendentes. Os responsáveis pelos insumos retomam também #263 e #271.

Não marcar #261, #262 ou uma política como concluída apenas por este documento:
faltam confirmação operacional, fundamentos/decisões jurídicas e a aprovação do
inventário. A [verificação de pendências](verificacao-pendencias-pr277.md) separa
o que foi testado, analisado, corrigido e adiado.
