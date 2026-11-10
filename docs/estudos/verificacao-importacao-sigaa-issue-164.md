# Preparação da auditoria e agenda SIGAA — #164

Registro de 10/11/2026, por solicitação do PO para incluir a preparação da #164
na mesma PR da #170. Base `develop` em `976d93b`. Esta entrega não declara
agendamento ativo nem auditoria da carga real de novembro concluída.

## Código preparado

- Workflow GitHub Actions com os perfis já documentados, às 03:00 de Brasília:
  diário na matrícula, semanal aos domingos fora dela. Um único perfil seleciona
  a coleta; variável ausente mantém a agenda sem executar importação.
- Disparo manual e execução agendada restritos a `main`, com concorrência sem
  cancelar a execução ativa. Não executa migrations nem recebe credenciais da API.
- Lista esperada comitada antes da coleta e origem da enumeração preservada em
  JSON, sem alteração de schema. Resultado por unidade continua no histórico.
- Relatório com a comparação integral de unidades, incluindo lacunas,
  duplicidades, falhas, zero ofertas válido, totais e período. Não usa o número
  de cartões do catálogo como denominador e não fixa 211 no código.
- Comando de auditoria de um ID explícito do histórico sem nova coleta ou escrita.
  Histórico antigo sem origem da enumeração não é promovido a comprovação da
  cobertura integral do formulário.
- Artefato de auditoria separado de logs brutos e mensagens de exceção privadas.
  Timeout, cancelamento ou falha de conexão podem impedir relatório final; nesse
  caso o job não demonstra sucesso. Um histórico `em_andamento` exige diagnóstico.
- GRANTs do papel `undb_importador` independentes dos papéis da API e do Alembic.

## Evidências locais

Python 3.12, PostgreSQL 16 descartável e coleta SIGAA simulada. Nenhum acesso ao
Neon ou coleta real de unidades foi executado nesta verificação.

- Suíte determinística: **186 testes aprovados**, incluindo 15 novos testes de
  cobertura, CLI de auditoria, propagação de falha e preservação da lista esperada
  após interrupção. Lint, formatação e build estrito do MkDocs aprovados.
- Migrações completas com conexão administrativa e execução do importador com
  `undb_importador`: primeira coleta, reimportação e substituição de vínculo
  docente aprovadas; unidade sem ofertas preservada no denominador da auditoria.
- Falha de coleta simulada persistiu histórico de falha e lista esperada, gerou
  auditoria incompleta e código de saída 1. A mensagem de erro permaneceu no
  histórico privado e não apareceu no relatório exportado.
- Auditoria posterior do ID com falha retornou código 1 sem modificar o histórico.
- O papel do importador teve acesso a contas/avaliações, DELETE em professores e
  CREATE TABLE recusados com SQLSTATE `42501`.

As verificações locais validam os mecanismos. Não substituem a execução agendada
no GitHub nem a comparação das listas reais do formulário e do Neon.

## Pendências operacionais

1. Revisão humana e promoção do workflow para `main` pelo fluxo do projeto.
2. Criar/configurar o papel limitado do importador e os secrets/variables descritos
   no [guia de operação](../operacao-importacao-sigaa.md); não usar `undb_api`.
3. Auditar o ID exato da carga manual anterior com o histórico completo e preservar
   a lista esperada. Caso a origem não esteja registrada, apresentar a evidência
   externa da enumeração; não inventar que o comando antigo tinha essa marcação.
4. Validar um disparo manual e depois uma execução automática, preservando run,
   ID do histórico e relatório. Configurar notificações de falha do Actions para
   o responsável pela operação. Conferir logs privados quando faltar artefato.
5. Resolver somente falhas concretas, sem confundir unidades sem ofertas com
   unidades não consultadas. Reconciliação de docentes continua na #207.
