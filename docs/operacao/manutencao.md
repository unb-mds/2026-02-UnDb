# Manutenção do UnDb

Fonte: decisões A–F do PO, Bloco 8 da #266. O projeto será mantido após o release.
Estados: **implementado** descreve código/documentação; **planejado** descreve
rotina a instalar; **pendente de validação** exige evidência ou decisão humana.
Nenhuma rotina é apresentada como comprovada em produção. Acompanhamento central
das pendências em [validações #266](../seguranca/validacoes-pendentes-266.md).

## Responsáveis e passagem de serviço

Nicolas acompanha a operação e a topologia (item 8). O registro histórico em
`continuidade-operacional.md` indica Tiago como apoio/substituto, com escopo,
contatos e acessos ainda pendentes de validação. Confirmar aceite e cobertura
antes de atribuir execução; não inferir papel jurídico de permissão técnica.
Manutenção/dependências e moderação: equipe UnDb, com executor e revisor designados
por rotina. Canal de titulares: toda a equipe, escala semanal planejada; publicar
internamente responsável e substituto aceitos antes de qualquer ativação.

Na troca de membros: conferir contas de serviço/domínio, responsáveis/substitutos,
vencimentos, acessos mínimos, pendências, versão implantada, jobs, procedimento de
restauração e último ensaio. Transferir segredos somente por meio privado aprovado,
revogar acessos antigos e rotacionar credenciais afetadas, testar continuidade e
registrar aceite de quem recebe. Estado: planejado; comprovação em registro privado
sem valores de segredo, dump ou dados de avaliadores.

## Calendário de rotinas

| Cadência | Rotina e executor | Estado | Comprovação sem dados pessoais |
| --- | --- | --- | --- |
| Contínua | Processo `descarte-moderacao`: purgar conteúdo, credenciais e registros vencidos; operação supervisiona | Implementado no código/Compose; hospedagem pendente de validação | Ciclos, contagens e alerta de falha, SHA/configuração; não publicar linhas do banco |
| Diária | Operação: saúde da API/banco, falhas de registro, job, cota de e-mail e fila | Planejado | Checklist privado com data, executor, versão e resultado agregado |
| Diária após primeiro dado real | Operação: backup automático | Planejado | Execução, tamanho, destino protegido, acesso e resultado sem conteúdo do dump |
| Semanal | Equipe: rodízio do canal quando ativado, fila de moderação e passagem ao substituto | Planejado; ativação pendente de validação | Escala aceita e pendências agregadas em canal privado |
| Semanal | Manutenção: verificar falhas de CI e avisos de segurança aplicáveis | Planejado | SHA, advisory, alcance e encaminhamento no registro autorizado |
| Mensal | Manutenção/operação: auditoria de dependências, acesso mínimo, logs de provedores, custos/cotas e validade de segredos | Planejado | Relatório sanitizado e aprovações de mudanças; sem rotação arbitrária ou segredos |
| Periódica, calendário a definir | Operação/revisor: restauração isolada e reaplicação de exclusões | Pendente de validação da periodicidade | Schema, vínculos e jornada sintética, descarte e limitações do ensaio |
| Início de cada semestre | Operação/equipe: checklist abaixo e cópia de arquivo | Planejado | Relatório de importação, backup de arquivo e revisão das cotas/limites |
| Anual e antes do vencimento registrado | Nicolas/substituto aceito: domínio, hospedagem, contatos e passagem de bastão | Planejado; datas pendentes de validação | Comprovante privado de renovação/aceite; não inventar vencimentos |
| Após incidente ou mudança relevante | Operação/manutenção: reavaliar acesso, segredos, restauração e dependências | Planejado | Decisão, responsáveis e resultado sanitizado |

## Backups e recuperação

Não criar cópia de dados reais por este plano antes do primeiro dado real.
Planejado: automáticos diários a partir desse marco, mais cópia de arquivo no
início de cada semestre e testes periódicos de restauração. Retenção, local,
região, criptografia, acesso, orçamento e alertas: pendentes de validação pelo
responsável operacional; não há promessa de capacidade de provedor gratuito.

O ensaio implementado do Bloco 7 usou `pg_dump -Fc --no-owner --no-privileges` e
`pg_restore --exit-on-error` em dois bancos sintéticos locais distintos. Retornos
zero e contagens iguais nas 25 tabelas; arquivo e recursos removidos. Isso não
prova backup automático, RPO/RTO, igualdade byte a byte ou jornada no restaurado.
Roteiro reproduzível: criar bancos novos isolados com papéis de ensaio; migrar a
fonte e povoar somente dados sintéticos; passar conexão por ambiente privado;
exportar arquivo protegido temporário; restaurar em destino novo, conferir schema,
contagens, FKs e jornada; remover arquivo/bancos/papéis e registrar o resultado.
Nunca usar produção como destino ou incluir dump no GitHub.

Antes de tornar restauração acessível, reaplicar exclusões por registro mínimo
protegido de IDs/datas; conferir sessões/tokens revogados, ocultação, purgas e
versão de schema. Exportação/guarda desse registro e procedimento de reaplicação
são pendentes de validação. Backups precisam de retenção compatível com exclusões.
Não confundir volume persistente ou marcador de rollback com backup operacional.

## Purga, banco e logs

Comando implementado: `python -m app.commands.descartar_moderacao --continuo`;
sem a opção, executa uma vez. Compose mantém processo separado. Padrões em
`backend/.env.example`: conteúdo sete dias, acesso seis meses corridos,
`PURGA_INTERVALO_SEGUNDOS` e `PURGA_LOTE`. Supervisão e retomada em hospedagem
permanecem pendentes de validação, especialmente se a API suspender por inatividade.
Conta mínima e metadados de rejeição não recebem prazo inventado.

API usa papel limitado, migrações papel próprio; permissões reais devem ser
conferidas por operação. Rollback deve parar API/job e seguir a migração: dados
apagados não voltam. Ver [retenção](../seguranca/retencao-bloco-5.md).

Console tem eventos mínimos sem corpo, token, senha, e-mail ou texto. A tabela
privada de acesso contém IP/encaminhamento bruto não confiável, sob acesso restrito;
não há painel/endpoint. Falha de gravação exige alerta e análise de lacuna.
Procedimento de consulta/ordem judicial em [registros](../seguranca/acessos-bloco-6.md).
Logs de Render/Vercel/Neon/Resend/OpenAI/GitHub precisam de inventário próprio;
filtro da aplicação não comprova sanitização ou retenção desses provedores.

## Dependências e segredos

Implementado: patches dirigidos de source-map-js e zod. Planejado: executar
`npm audit`, `npm audit --omit=dev` e `npm ls`, analisar alcance, atualizar com
mudança mínima, validar lockfile e executar lint/tipagem/testes/build. Auditoria
não equivale a explorabilidade comprovada. Glob/minimatch: major somente após
aprovação item 9; Next/sharp ainda exigem investigação. Fontes e proposta em
[evidências do Bloco 7](../seguranca/evidencias/issue-266/bloco-7/resultados.json).

Rotacionar segredos em incidente, transferência/revogação de acesso e conforme
política de validade aprovada, ainda pendente de validação. Registrar somente
identificador/versão/data, nunca valor. Trocar HMAC reinicia chaves de orçamento;
planejar efeito sobre cota de e-mail e múltiplas instâncias. Não desativar
autenticação/autorização para contornar falha do limitador.

## Início de semestre

Equipe/operação: confirmar oferta/período SIGAA, usar o procedimento existente de
[importação](../operacao-importacao-sigaa.md), conferir origem e vínculos sem
credenciais estudantis; preparar cópia de arquivo protegida; revisar fila de
moderação, equipe/acessos, reserva real da cota de e-mail, carga/falsos positivos
e números PROVISÓRIOS do limitador. Conferir jobs, restauração, vencimentos e
pendências da passagem anterior. Estado: planejado; medição/aceite dos limites
continua pendente de validação (item 4).

## Incidentes e canal de titulares

Planejado: quem detecta avisa Nicolas e substituto aceito por canal privado da
equipe, ainda a confirmar; não usar issue/PR para dados, credenciais ou evidências
brutas. Registrar horário UTC, versão, impacto mínimo observado e responsável.
Nicolas coordena decisão de contenção com operação: restringir acesso/fluxo
afetado, revogar credencial comprometida e preservar evidência mínima protegida;
não executar restauração/produção automaticamente a partir deste documento.
Validar causa e correção em ambiente isolado, decidir retorno, registrar limites
e revisão posterior. Preservação tem escopo, acesso e destino aprovados, não prazo
ilimitado inventado. Controlador, porte, comunicação externa e prazos legais são
pendentes de validação jurídica apropriada; roteiro não os define.

Canal permanece DESATIVADO por padrão. Antes de ativar: equipe/escala com responsável
e substituto, acessos por UUID, retenção/minimização/backups aprovados, integração
de contato (e-mail preferencial ou WhatsApp), confirmação proporcional do
solicitante, respostas e revisão testadas com dados sintéticos. Sem IA no atendimento.
Não prometer exclusão integral instantânea: explicar conta mínima, janela de
conteúdo, logs e limites de cópias. Procedimento em [canal](../canal-titulares.md).
