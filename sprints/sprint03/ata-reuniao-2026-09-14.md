# Ata de reunião — acompanhamento da Sprint 03

## Informações gerais

- **Data:** 14 de setembro de 2026
- **Horário:** 13h
- **Participantes:** não registrados individualmente
- **Local ou formato:** não registrado
- **Objetivo:** revisar e confirmar as pendências da semana referentes à Sprint 03 — Persistência e APIs Base

## Pauta

1. Conferência das atividades ainda abertas na Sprint 03.
2. Consulta dos responsáveis registrados nas Issues.
3. Registro das dependências existentes entre as atividades.

## Pendências confirmadas

### Integração com o SIGAA

- **#25 — Integrar importação e disponibilizar dados no backend:** Gabriel e Warlley.

### Frontend

- **#29 — Criar estrutura inicial do projeto:** Vinicius.
- **#30 — Implementar tela de exemplo consumindo API real:** Vinicius, após a estrutura da #29.
- **#31 — Definir padrão visual básico:** Vinicius; pode avançar em paralelo à estrutura inicial.
- **#36 — Definir execução e containerização do frontend:** Vinicius e Tiago, após o avanço das Issues #29 e #34.

### Infraestrutura e Docker

- **#34 — Criar Docker Compose para backend e PostgreSQL:** Tiago.
- **#37 — Testar a subida completa do ambiente:** Tiago, Gabriel e `ailoiol`, após a conclusão das configurações anteriores da infraestrutura, especialmente #34 e #36.

### Avaliações

- **#38 — Definir o modelo de dados dos cinco critérios:** Nicolas.
- **#40 — Implementar endpoint de consulta agregada:** Nicolas, após a validação da #38.

## Dependências e sequência de trabalho registrada

A reunião confirmou as pendências. A sequência abaixo consolida as dependências atualmente documentadas nas Issues e não representa uma nova decisão de processo:

1. Avançar em paralelo com as Issues #25, #29, #31, #34 e #38.
2. Iniciar #30 após #29; #40 após #38; e #36 após #29 e #34.
3. Executar #37 por último, como validação integrada do ambiente.

O caminho de maior dependência ficou registrado como `#29 + #34 → #36 → #37`. As frentes `#38 → #40` e #25 podem avançar paralelamente.

## Encaminhamentos

- Cada responsável deve acompanhar os critérios de aceite e registrar progresso, bloqueios e evidências na respectiva Issue.
- Dependências ou impedimentos identificados durante a execução devem ser comunicados à equipe antes de ampliar ou alterar o escopo.
- A situação das pendências será verificada novamente até o encerramento da Sprint 03, previsto para 18 de setembro de 2026.

## Observações

Esta reunião confirmou as pendências da semana. Os responsáveis e as dependências foram transcritos do estado das Issues consultado em 14 de setembro de 2026; não foi registrada confirmação individual de presença ou aceite de cada responsável. Não foram registradas nesta ata novas decisões de produto, requisitos, arquitetura, processo ou alterações de escopo.
