# Retenção, exclusão e purga — #266, Bloco 5

Estado: implementado. Fonte: seção B e EXECUTAR: BLOCO 5 do PO. Não representa
validação jurídica nem comprovação em produção. Continuidade na PR #280.

## Conta e recadastro

`DELETE /api/auth/conta` exige sessão e proteção de origem, sem limitador. Na mesma
transação, bloqueia a conta, marca `excluido_em`, zera nome e papéis, apaga hash de
senha, sessões, tokens e avisos de agradecimento da conta, e oculta suas avaliações
e todas as versões de comentários. A resposta 204 remove o cookie. O estado
EXCLUIDA deriva de `excluido_em`; os booleanos restantes ficam falsos e o nome
vazio é marcador constante, não o nome anterior.

Permanece o mínimo na conta: ID, e-mail, criação e exclusão, com estado derivado.
E-mail continua reservado pela constraint única: recadastro retorna a resposta
neutra existente sem enviar e-mail nem reativar conta. Login usa hash fictício e
recusa conta excluída; recuperação, reenvio, confirmação, redefinição e sessão
também não reativam a conta. Base legal, prazo de guarda e data de revisão são
**pendentes de validação humana**. Não há job que invente prazo para essa guarda.

## Conteúdo

`DELETE /api/avaliacoes/{id}` exige autoria; outra conta recebe 404.
`DELETE /api/moderacao/avaliacoes/{id}` exige moderador confirmado. Ambas preservam
autorização e origem e ficam fora do limitador. Não foi criado fluxo de frontend
de exclusão neste bloco; os contratos HTTP estão implementados.

Avaliação excluída permanece oculta até `purgar_em`: não participa dos agregados,
destaques por disciplina ou comentários públicos. A janela padrão aprovada é
sete dias, configurável em `RETENCAO_CONTEUDO_DIAS`. Repetir exclusão não estende a
janela. Reenvio de avaliação em descarte retorna 409 até a purga, preservando
unicidade e impedindo ressurreição. Depois da purga, conta ativa pode avaliar
novamente. Bloqueio da conta serializa escrita com exclusão; operações de conteúdo
preservam seus bloqueios e constraints existentes.

Retirada própria e remoção por moderação de comentário continuam ocultando-o
imediatamente. Após a janela, o registro é removido definitivamente, junto de
denúncias, agradecimentos e decisões vinculadas. Referências `substitui_id` são
desligadas antes da remoção. Exclusão da avaliação remove todas as suas versões.
A cascata é explícita, transacional e protegida pelas FKs existentes; não depende
de cascade de ORM ou de FKs desabilitadas. Não há cópia do texto em outra tabela.
Se uma versão removida for substituída por outra aprovada, o prazo de descarte
original é preservado: a purga também remove versões SUBSTITUIDO com prazo vencido
e seus registros vinculados. Substituições sem descarte agendado continuam sem prazo.

Comentário é entidade separada dos critérios estruturados da avaliação. Rejeitar
comentário PENDENTE apaga seu texto, mantém apenas seus metadados e a decisão e
preserva os critérios da avaliação. Nenhum critério passa a ser rejeitado por
causa do texto. Metadados de rejeição não são apagados pelo prazo antigo de sete
dias; seu prazo e finalidade permanecem pendentes de validação. A decisão não
copia automaticamente o texto rejeitado. Motivo humano deve evitar dados pessoais
ou transcrição do conteúdo; permanece um campo de decisão interno já existente.

Denúncias encerradas recebem `encerrada_em`, permanecem até purga do comentário e
não participam de fila, contagem ativa, impedimento ou agradecimento ativo. Índice
único parcial mantém uma denúncia aberta por conta/versão, permitindo novo relato
após encerramento. Denúncias já apagadas pelo comportamento anterior não podem ser
recuperadas. Não há alteração de limiar de suspensão automática neste bloco.

## Job automático e configuração

O processo já versionado `descarte-moderacao` no Compose usa
`python -m app.commands.descartar_moderacao --continuo` e agora executa a purga de
conteúdo, sessões/tokens expirados e contadores expirados, além do descarte de
decisões não relacionadas a rejeição. Não exige Redis, fila ou serviço contratado.
Uma execução isolada usa o mesmo módulo sem `--continuo`.

`PURGA_INTERVALO_SEGUNDOS=60` e `PURGA_LOTE=1000` são padrões técnicos configuráveis;
a unidade de lote é avaliação/comentário/credencial e uma avaliação leva suas
versões relacionadas na mesma transação. Falha gera evento técnico sem payload e
o modo contínuo tenta novamente no próximo ciclo. Índice `purgar_em` atende a busca
de avaliações vencidas; índice de comentários e de contadores já existiam.
Intervalo, duração real, disponibilidade e supervisão em hospedagem permanecem
pendentes de validação operacional. API e job usam SQLAlchemy síncrono/psycopg2.

## Migração e rollback

Migração `20261117_02` acrescenta datas de exclusão, nulidade da senha, prazo de
purga e encerramento de denúncia, com índice parcial. Aplicar antes da API/job.
Downgrade não recupera credenciais, conteúdo purgado ou denúncias encerradas. Ele
remove avaliações ocultas e dependentes para não reexpor conteúdo ao retirar as
colunas; por isso o rollback é reversível no esquema, sem prometer reversibilidade
dos dados. Contas usam senha vazia inválida na revisão antiga.

Parar API e job durante rollback/reaplicação: a aplicação antiga não conhece os
estados novos. O downgrade guarda somente IDs/datas de contas excluídas em
`retencao_rollback_contas`; upgrade restaura essas datas, mantém senha NULL e remove
o marcador. Não executar aplicação antiga como se implementasse as regras novas.
Isso não é backup nem registro de acesso do Bloco 6.

## Backups e pendências

Nenhum backup criado ou produção acessada. A retenção de backups precisa ser
compatível com exclusões; uma restauração precisa reaplicá-las usando registro
mínimo de IDs e datas. Responsável operacional deve definir local protegido,
exportação/guarda desse registro, procedimento de reaplicação e comprovação. Esse
fluxo de restauração permanece **pendente de validação**, não implementado por
este bloco. O marcador de rollback não substitui esse registro operacional.

Base legal da conta mínima e vínculo residual autor/conteúdo, prazo dos metadados
de rejeição, retenção de backups e execução contínua do job permanecem pendentes
de validação. A #266 não está concluída. Blocos 6–8 continuam planejados.

## Verificações

`tests.test_retencao` cobre SQLite com FKs e PostgreSQL descartável, relógio
simulado na fronteira da janela, cascatas, idempotência, rollback transacional,
recadastro neutro, credenciais removidas, rejeição, tokens/sessões/contadores
expirados, denúncias encerradas e contratos HTTP/autorização/origem.
`tests.integration_retencao_migracao` ensaia downgrade/reaplicação com conta
excluída sintética. Evidências finais em
`evidencias/issue-266/bloco-5/resultados.json`; resultados de CI na PR.


## Integracao com a ciencia dos Termos (#269)

Contas ativas preservam a versao e data de ciencia explicita; conta excluida
apaga ambos os campos para manter a guarda minima aprovada. A migracao de retencao
usa agora o ID unico 20261117_02_retencao; o ID 20261117_02 permanece reservado
para a migracao da develop de ciencia dos Termos. A revisao 20261117_04 une os
grafos e reconcilia bancos do historico anterior da #266 sem apagar ciencia real.
Rollback e reaplicacao devem manter API/jobs parados conforme o procedimento.
