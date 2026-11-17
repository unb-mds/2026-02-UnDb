# Incidentes e recuperação — R2 / #267

Fonte: [escopo vigente da #267](https://github.com/unb-mds/2026-02-UnDb/issues/267),
[requisitos](../requisitos.md#recuperacao-isolada-e-roteiro-de-incidentes-267) e
confirmação de Nicolas em 17/11/2026 nesta sessão. Entrega proporcional à R2:
roteiro curto e recuperação sintética isolada. Revisão jurídica formal e estrutura
empresarial não são critérios desta etapa. Este roteiro não autoriza produção.

## Aviso e acompanhamento

Nicolas informou, de memória, que **Gabriel e Vinicius recebem os avisos**; precisa
confirmar o canal privado utilizado e como acompanha. Não há canal operacional
privado confirmado nas fontes consultadas. `/contato` e `/atendimento` são o fluxo
de titulares, desligado por padrão, e não substituem esse canal. `no-reply` é
remetente transacional, não caixa de recebimento. Não inventar grupo, e-mail,
plantão, substituto habilitado, SLA ou prazo legal.

Quem detectar prepara o aviso abaixo sem dados pessoais. **Antes de encaminhar,
confirmar com Nicolas o meio privado e seus participantes**, pelos contatos de
trabalho já conhecidos do time; este documento não fornece um endereço alternativo.
Gabriel executa a entrega técnica #267; isso não lhe concede acesso aos provedores.
Nicolas acompanha a operação; Tiago tem indicação histórica de apoio/substituição,
com acesso e disponibilidade ainda não comprovados. Ver [continuidade](../continuidade-operacional.md).

```text
Detecção: data/hora e fuso (preferir UTC); início conhecido ou desconhecido.
Versão: SHA de frontend/API e revisão de schema, ou “a conferir”.
Impacto observado: fluxo afetado, alcance agregado e se persiste.
Fatos: status/classe de erro e referência restrita; separar hipóteses.
Ação: proposta ou executada, executor/autorização, resultado e reversão.
Encaminhamento: responsável que aceitou; próxima atualização a combinar.
```

Não anexar corpo, texto de avaliador, IP, e-mail, dump, URL privada, token, chave,
cookie ou traceback bruto em issues/PRs. Preservar apenas o necessário sob acesso
autorizado e descarte vigente; falta de canal não autoriza publicar evidência bruta.

## Interromper, diagnosticar, reverter, conferir

1. Separar indisponibilidade, possível exposição e abuso. Crítica acadêmica legítima
   segue moderação; volume de denúncias não comprova violação. Registrar fatos e
   hipóteses; não investigar autores nem realizar ataques para reproduzir o sinal.
2. Nicolas/operação define e autoriza a intervenção e seu alcance. Antes de agir,
   registrar estado anterior sem segredos, impacto e reversão. A continuidade já
   prevê suspensão de novas contribuições se faltarem condições de operação; **não
   há interruptor global implementado para isso**. Não inventar endpoint/comando:
   operador deve confirmar mecanismo e autorizar eventual parada de API/jobs no
   ambiente afetado. Essa parada pode interromper leituras e atendimento também.
3. Usar [atualização/diagnóstico/reversão](../hospedagem.md#atualizar-diagnosticar-e-reverter):
   identificar versão/variáveis, logs mínimos de build/migration/inicialização e
   consulta real ao catálogo. `/health` não consulta banco. Falhas de limitador,
   registro ou purga exigem conferir os eventos e a [matriz #266](../seguranca/validacoes-pendentes-266.md),
   sem desativar autorização para contornar o erro. Logs de provedores têm acesso
   e retenção próprios, ainda não verificados.
4. Reverter código somente para versão compatível com schema. Deploy anterior não
   desfaz migration. Para migração/rollback, manter API e jobs parados conforme
   [retenção](../seguranca/retencao-bloco-5.md#migracao-e-rollback); dados apagados
   não voltam por downgrade. Não restaurar sobre produção automaticamente.
5. Se restauração for necessária, operador confirma autorização, ponto de recuperação,
   origem, destino vazio distinto, cobertura e proteção da cópia. Seguir o procedimento
   de [backup/restauração da hospedagem](../hospedagem.md#backup-e-restauracao-roteiro-ainda-nao-executado).
   Manter destino inacessível ao público durante validação e reaplicação abaixo.
6. Conferir revisão Alembic/schema/vínculos, jornada de leitura e escrita, sessão,
   autorização, ocultação e purgas. Só registrar recuperação após evidência;
   Nicolas/operação decide retorno autorizado, comunicação e revisão posterior.
   Registrar causa confirmada ou hipótese, ações, resultado e encaminhamentos.

Os cinco [cenários documentais existentes](https://github.com/unb-mds/2026-02-UnDb/blob/develop/skills/engineering/security-review/references/scenarios.md)
foram confrontados com este roteiro: acesso negado é controle; possível segredo
exige referência sem valor; instrução em comentário é dado não confiável; denúncia
coordenada não elimina crítica; falha de catálogo exige consulta real e reversão
compatível. Percurso documental, sem ataques, nova campanha de moderação ou operação.

## Backup realmente conhecido em 17/11/2026

| Fonte / recurso | Cobertura e acesso | Período e limites | Estado |
|---|---|---|---|
| Nicolas: “faço os backups manualmente no Docker, quando necessário” | Nicolas é o executor informado; conteúdo, origem, formato e outros acessos não detalhados | Histórico recuperável, local/cifra e descarte não informados | **Relato operacional**, sem inspeção de cópia nem restauração dessas cópias |
| Compose: `postgres_data` | Persistência do PostgreSQL local | Não fornece histórico independente nem proteção contra perda/exclusão do volume | **Observado no código; não é backup** |
| Bloco 7 da #266 | Dump custom/restore em dois bancos sintéticos; contagens iguais nas 25 tabelas daquele schema | Arquivo/bancos/papéis removidos; sem jornada, backup automático ou RPO/RTO comprovados | **Evidência histórica parcial**, [resultado](../seguranca/evidencias/issue-266/bloco-7/resultados.json) |
| Ensaio #267 | Todas as tabelas descobertas no schema migrado; fixtures de catálogo, conta/Termos, avaliações/comentários, votos, credenciais, acesso e pedidos/eventos/hash | Cópia temporária de um instante sintético; sem usuários reais, painel de provedor ou garantia de recuperação hospedada | Ver [evidência e reprodução](../seguranca/evidencias/issue-267/README.md) |
| Manutenção: diário após primeiro dado real e arquivo semestral | Escopo e instalação a validar por operação | Agenda, histórico, retenção, alertas, acessos e destino não comprovados | **Plano documentado**, não rotina instalada |
| Neon/Vercel/Render/Resend | Somente arquitetura/hospedagem documentadas; não houve acesso nesta tarefa | Não presume janela do plano, snapshot/PITR, logs ou cópia de serviços externos | **Capacidade não comprovada** |

Dump lógico não inclui automaticamente papéis/grants de cluster (`--no-owner --no-acl`),
configurações dos provedores, DNS, segredos, e-mails e logs externos. O ensaio usa
papel de laboratório; não homologa permissões API/migração reais. Contadores
`UNLOGGED` são efêmeros e não devem sustentar garantia de recuperação de orçamento.

## Exclusões e revogações antes de liberar uma cópia

O backup pode trazer conta, conteúdo, sessão, token ou permissão que já deixou de
ser válido. O marcador `retencao_rollback_contas` não é diário de exclusões e o
dump antigo não sabe o que aconteceu depois dele.

1. Manter API/jobs do destino sem acesso público. Obter de fonte operacional
   autorizada os eventos posteriores ao ponto de recuperação: operação, ID mínimo,
   data UTC original e vínculo necessário para reaplicar. Não copiar texto, e-mail,
   token ou senha ao registro de reaplicação. IDs também exigem acesso protegido.
2. Reconciliar exclusão de conta/avaliação, retirada/remoção de texto e revogação de
   sessões/tokens/papéis com os serviços/transações vigentes. Usar a data original
   para não reiniciar janelas; respeitar remoção de ciência dos Termos, votos e
   cascatas. Uma retirada de texto não apaga as notas da avaliação.
3. Executar purga vigente até tratar os lotes vencidos, incluindo acessos e
   credenciais expiradas. Conferir inatividade da conta, sessão/token/papel
   revogados, conteúdo ausente de consultas/agregados e integridade dos dependentes.
   Não criar prazo para pedidos/eventos ou conta mínima sem decisão autorizada.
4. Registrar ponto de corte, cobertura e resultado sem valores sensíveis; repetir
   de modo idempotente se necessário e obter decisão do operador antes de liberar.

**Limitação essencial:** Nicolas não sabe se existe registro protegido dessas
ações; responsável e procedimento de acesso permanecem pendentes. Sem uma fonte
completa não é possível garantir que uma cópia antiga não reexponha exclusões ou
reative revogações. **Não liberar a restauração com essa garantia presumida**:
encaminhar a lacuna a Nicolas/operação para decidir o tratamento antes do retorno.
O ensaio exercita um diário artificial descartável e sete eventos conhecidos;
não instala exportação, política de guarda ou ferramenta de replay em produção.

## Pendências e proposta para o time

| Insumo específico | Quem acompanha / efeito |
|---|---|
| Confirmar Gabriel/Vinicius, canal privado, participantes e forma de Nicolas acompanhar | Nicolas; impede declarar aviso/escalonamento operacional concluído |
| Descrever uma cópia manual real: origem/formato, cobertura, histórico disponível, destino protegido, acesso autorizado, passos e resultado de recuperação | Nicolas/operação; impede comprovar recuperação e janela reais. Não enviar dump ou credencial |
| Definir/verificar registro protegido de exclusões/revogações, cobertura, responsável, acesso e descarte | Nicolas/operação com responsáveis pela retenção; impede garantir reaplicação completa de uma restauração real |
| Publicar/confirmar documentos e versão efetivamente demonstrada | Commit/push/PR/merge e encerramento técnico autorizados na continuação; conferir resultado na PR. Deploy e versão demonstrada seguem na revisão geral #168 |

**Proposta, não adotada:** um único canal privado com Gabriel, Vinicius e Nicolas,
para aviso e acompanhamento com o modelo mínimo acima; confirmar ferramenta e
participantes antes de usar. Primeiro inventariar e validar as cópias manuais
existentes, depois decidir a instalação do plano de backup. Separadamente, definir
um registro mínimo protegido das exclusões/revogações com cobertura e acesso
comprovados, sem inventar prazo de guarda ou prometer recuperação por plano gratuito.

Resumo factual destinado à #168 e matriz dos critérios estão na
[evidência técnica](../seguranca/evidencias/issue-267/README.md). A validação local
não operou produção. Na continuação, o usuário autorizou um único commit, push,
PR para develop, merge e encerramento da #267 com as ressalvas acima. Esse aceite
da entrega técnica não comprova resolução dos fatos operacionais pendentes.
