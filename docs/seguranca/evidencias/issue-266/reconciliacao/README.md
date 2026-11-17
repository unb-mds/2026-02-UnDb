# Reconciliação da branch com develop

Estado: implementado. Revisão independente e validações operacionais/jurídicas permanecem pendentes de validação.

Integração de `origin/develop` em `8a2bb75` à branch `fix/266-sessoes-abuso-logs`, antes em `0423191`, preservando o histórico de ambas. A PR de continuação é a #280; a #279 já foi integrada. A retirada do rascunho foi solicitada pelo PO para revisão por outra pessoa, sem aceite final da #266.

## Resolução

- Modelo e schema de usuário: preservados exclusão lógica, senha removível, normalização de e-mail e ciência obrigatória/versionada dos Termos da #269. A data de ciência continua sendo atribuída no servidor; contas legadas não recebem ciência retroativa.
- Cadastro: preservados checkbox, links públicos e payload da #269, juntamente com mensagens acessíveis de 429/503 e manutenção do preenchimento da #266.
- Exclusão de conta: os campos de ciência também são apagados, mantendo somente o registro mínimo aprovado. Cadastro ativo continua persistindo versão/data.
- Requisitos: preservadas as duas entregas. Documentação, páginas públicas, atas e orientações recebidas de develop foram mantidas. A política recebeu somente correções factuais sobre limitador, retenção e alcance do ensaio sintético de backup; revisão humana continua pendente.
- Alembic: as duas branches usavam `20261117_02` para mudanças diferentes. Preservado o identificador de develop para ciência dos Termos; retenção passou a `20261117_02_retencao`, e `20261117_04` une os ramos. Guardas de existência permitem migrar o antigo banco #266 carimbado com o identificador ambíguo, sem recriar contadores nem inventar ciência. A operação exige API/jobs parados; rollback não recupera dados já apagados.

## Verificações executadas

Ambiente local Windows, Python 3.12 e PostgreSQL local descartável; dados e adaptadores de e-mail sintéticos. Nenhum ambiente de produção acessado. Não se trata de execução Linux/CI ou de containers.

| Verificação | Comando ou ensaio | Resultado |
| --- | --- | --- |
| Backend completo com PostgreSQL | `python -m unittest discover -s tests -q` | 428 testes, sem falhas, 2 skips |
| Backend selecionado | Seleção de segurança/autenticação/retenção/acesso pelo harness local | 87 testes, sem falhas |
| Migrações | `alembic upgrade head`, `check`, downgrade até base e reaplicação; rollback com dados sintéticos | Sem falhas; sem diferença pendente no schema |
| Compatibilidade de históricos | `python -m tests.integration_conflito_migracoes` | Origens develop `_02`, retenção antiga `_02` e acesso `_03` chegaram ao head único `_04` |
| Ciência dos Termos | `python -m tests.integration_termos` em banco exclusivo vazio | Persistência, conta legada, constraint e downgrade/reaplicação sem falhas |
| Integrações reais locais | Moderação HTTP, avaliação e acesso pelo navegador | Sem falhas; acesso com 54 combinações |
| Limpeza e purga | CLIs existentes e rollback com dados | Retorno zero |
| Frontend | `npm run lint`, `npm run typecheck`, `npm test`, `npm run build` | Sem falhas; 91 testes |
| Cadastro e documentos públicos | `node tests/termos-browser.mjs` | 18 combinações, sem falhas |
| Análise estática e documentos | Ruff check/format, compileall, `mkdocs build --strict`, `git diff --check` | Sem falhas |

Os ensaios removem bancos/papéis descartáveis ao terminar. O teste de Termos foi ajustado para aceitar também a porta local reservada usada pelo harness, preservando autorização explícita, banco exclusivo vazio, destino loopback e igualdade entre URLs de aplicação/migração. Uma primeira execução foi interrompida pela guarda de ambiente; após isolar o banco correto, a execução final passou. A injeção de limitador permitido nesse teste isola o contrato de Termos; as regressões do limitador são executadas separadamente.

## Handoff

Revisar especialmente a colisão de identificadores Alembic e os três percursos de atualização, a composição das regras de cadastro e a remoção da ciência na exclusão de conta. Executar ensaios somente em bancos descartáveis. Não interpretar esta evidência como validação jurídica, de produção ou aceite final. Pendências e riscos residuais continuam em [validações pendentes](../../../validacoes-pendentes-266.md). O resultado remoto de CI é registrado na descrição da PR, associado ao SHA publicado.
