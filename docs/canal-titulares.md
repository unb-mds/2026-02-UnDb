# Canal de solicitações — #263

## Contrato aprovado em 15/11/2026

Nicolas aprovou formulário e acompanhamento no UnDb sem login estudantil. O solicitante
recebe protocolo aleatório e chave secreta; somente o hash da chave é persistido.
Vinicius e Gabriel podem atender e responder; Nicolas e Tiago têm leitura restrita.
Contas são identificadas por UUID configurado pelo operador, nunca por nome exibido.

O contrato autoriza tabelas próprias para solicitações e histórico: categoria, alvo,
descrição, evidência textual, responsável, datas e respostas. Não há upload de arquivos,
documentos pessoais obrigatórios ou envio a IA. Respostas são consultadas pelo mesmo
canal; não existe promessa de entrega por e-mail ou prazo/SLA não aprovado.

## Configuração e operação

Configurar `CANAL_TITULARES_LEITORES` com UUIDs das contas confirmadas de Nicolas/Tiago
e `CANAL_TITULARES_ATENDENTES` com UUIDs de Vinicius/Gabriel, separados por vírgula.
Não usar UUIDs de exemplo em produção nem publicar identificadores privados. A configuração
não concede moderação ou reconciliação; cada função preserva suas próprias permissões.
No banco hospedado, conceder ao papel da API SELECT/INSERT em `solicitacoes_titulares`
e `eventos_solicitacoes` somente após revisão do operador. Migração usa papel administrativo.

`CANAL_TITULARES_ATIVO` e `CANAL_TITULARES_RETENCAO_APROVADA` são falsos por padrão.
O operador deve ativar ambos somente após validação dos insumos. Suspender recebimento
não impede acompanhar/complementar pedidos existentes nem responder pela área restrita.
Não incluir corpos de requisições ou chaves em logs, métricas ou ferramentas de analytics.

As rotas públicas de criação, consulta e complemento compartilham orçamento técnico
temporário por cliente e processo (`CANAL_TITULARES_LIMITE_MINUTO`, padrão 30/minuto).
Os identificadores são HMAC em memória, com expiração de 60 segundos e limite de entradas;
não são persistidos. Reinícios zeram o orçamento; múltiplas instâncias não o compartilham.
O endereço usado é o cliente fornecido pelo servidor, sem interpretar X-Forwarded-For
diretamente. Validar a configuração de proxy do provedor para não agrupar visitantes.
Isso complementa, mas não substitui, os controles de abuso da #266.

Retomada de PEND-263-ABUSO: a [revisão #266](seguranca/revisao-sessoes-abuso-logs-issue-266.md)
verificou autorização, janela, HMAC e isolamento do orçamento com dados sintéticos, e
sanitizou validação/erros/logs da aplicação. O limite continua por processo; proxies,
instâncias e logs de borda exigem homologação do operador. A pendência não está encerrada.
Mutações seguem a restrição de origens aprovada na #266; leitura/consulta por chave mantém
o contrato do canal. Nenhuma flag de recebimento foi ativada.

Pedidos repetidos geram protocolos independentes, sem revelar se outra pessoa já pediu
algo sobre o mesmo alvo. Referência indisponível ou evidência insuficiente deve receber
triagem motivada; o servidor não acessa links fornecidos pelo solicitante.

Atendimento em `/atendimento`: registrar triagem e providências internamente, incluindo
encaminhamento e prioridade segundo regras aprovadas; registrar resposta motivada pelo
tipo RESPOSTA, com orientação para revisão por complemento. O solicitante consulta em
`/contato`, com protocolo e chave. Aguardar identidade/legitimidade proporcional antes
de executar direitos; não pedir documentos excessivos por padrão. Evidências além do
texto exigem canal seguro específico aprovado, não links de upload improvisados.

## Limites de ativação

Recebimento desativado por padrão. Ativar em produção somente após aprovar retenção na
#262, conferir inventário/minimização na #261, configurar os responsáveis e validar o
percurso com dados sintéticos. Não há prazo de descarte inventado nesta entrega.
A política deve contemplar dados ativos, histórico, chave de consulta, logs e backups.

Um pedido já basta para triagem humana; não depende do volume de denúncias. Discordância
ou nota negativa não gera remoção automática. O atendimento não altera notas, comentários,
identidades ou contas: encaminha ao fluxo específico. Identidade/legitimidade deve ser
verificada proporcionalmente antes de executar direitos ou transmitir dados privados.
Respostas nunca devem identificar avaliadores. Revisão pode ser solicitada pelo canal.

## Dependências e retomada

| Origem | Insumo pendente | Destino / ajuste esperado |
|---|---|---|
| #263 | Retenção e descarte aprovados | #262 deve revisar tabelas/campos/histórico e implementar descarte verificável |
| #263 | Inventário, bases e minimização | #261 deve conferir campos, evidências e acesso do canal |
| #263 | Escalonamento urgente e revisão | #264/#267 devem conciliar procedimento com fila de atendimento |
| #260 | Canal acessível a titulares | Atualizar continuidade com /contato após ativação validada; nomes não comprovam acesso |

Os destinos são referências de integração, não confirmação de aceite ou resolução.

## Verificação local — 15/11/2026

- Sete testes de API passaram: sessão/allowlist, leitura sem escrita, hash da chave,
  isolamento entre protocolos, registros internos ocultos, complemento/revisão, ativação
  bloqueada, orçamento temporário e criação das tabelas/índice em banco SQLite sintético.
- Teste de navegador com API fictícia passou: criação/recibo, consulta, complemento,
  formulário restrito a atendente, leitor sem formulário e recebimento suspenso.
- TypeScript, ESLint do canal e Ruff passaram; build Next.js com Webpack passou.
- Build padrão com Turbopack falhou no processamento de CSS por erro do processo local;
  a primeira tentativa também teve bloqueio de download das fontes Google no sandbox.
- Suíte geral: 314 testes na execução inicial, com duas falhas no corpus de ofensas,
  dois erros de limpeza de arquivos SQLite no Windows e dois testes pulados. As falhas
  de ofensas se repetiram isoladamente; esses arquivos não foram alterados nesta entrega.
  Isso não equivale a aprovação da suíte geral nem de produção.

Nenhuma solicitação real, conta, permissão de produção, painel ou dado de avaliador foi
usado na validação. A migração PostgreSQL completa e o percurso com os responsáveis reais
ainda precisam ser homologados. Registros de integração no GitHub ainda não foram publicados.
