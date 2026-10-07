# Auditoria de Clareza e Rastreabilidade dos Requisitos — Issue #149

**Data:** 07/10/2026  
**Sprint:** 05 — Diagnóstico da jornada e requisitos (Release 2)  
**Issue de referência:** [#149 — [R2][DOCS] Auditar clareza e rastreabilidade dos requisitos](https://github.com/unb-mds/2026-02-UnDb/issues/149)  
**Epic:** [#146 — [EPIC][R2] Clareza dos requisitos e da arquitetura SIGAA](https://github.com/unb-mds/2026-02-UnDb/issues/146)  
**Governança aplicável:** `skills/process/ambiguity-removal/SKILL.md`, `skills/process/requirements/SKILL.md` e `skills/governance/project-governance/SKILL.md`.

---

## 1. Escopo e Fontes Auditadas

A presente auditoria foi executada com o objetivo de identificar lacunas, termos vagos, conflitos, critérios de aceite não verificáveis e estados desatualizados nos documentos de engenharia de software do projeto após a conclusão e entrega da **Release 1.0.0**.

Foram auditados os seguintes artefatos:
1. **Fonte de verdade canônica dos requisitos:** [`docs/requisitos.md`](../requisitos.md);
2. **Especificação técnica de implementação (derivada):** [`specs.md`](../../specs.md);
3. **Documento de Visão do Produto (derivado):** [`docs/visao.md`](../visao.md);
4. **Documento de Arquitetura (consumidor de requisitos):** [`docs/arquitetura.md`](../arquitetura.md);
5. **Notas da Release 1.0.0 (evidência de entrega):** [`docs/releases/1.0.0.md`](../releases/1.0.0.md).

---

## 2. Relatório de Ambiguidade (Ambiguity Report)

**Veredito:** `CONCERNS`  
*(Os requisitos essenciais da Release 1 estão validados e operacionais no código da v1.0.0. Contudo, os requisitos do escopo da Release 2 apresentam lacunas críticas de atores, regras de negócio e limites de domínio, e a matriz de rastreabilidade e certas notas de pendências permanecem defasadas em relação à entrega realizada).*

### Tabela Resumo dos Achados

| ID | Localização | Tipo de Ambiguidade | Categoria | Estado de Decisão |
|---|---|---|---|---|
| **AMB-001** | `docs/requisitos.md` § 5 (RF18) | Termo vago / Requisito incompleto | Nova Decisão (Produto/Engenharia) | `Pending Decision` |
| **AMB-002** | `docs/requisitos.md` § 5 (RF20) | Escopo ambíguo / Regras omitidas | Nova Decisão (Produto) | `Pending Decision` |
| **AMB-003** | `docs/requisitos.md` § 5 (RF21) | Atores ausentes / Comportamento omitido | Nova Decisão (Produto) | `Pending Decision` |
| **AMB-004** | `docs/requisitos.md` § 4, § 5 (RF22) | Permissões / Modelo de autorização omitido | Nova Decisão (Produto/Arquitetura) | `Pending Decision` |
| **AMB-005** | `docs/requisitos.md` § 11 (Tabela pendências) | Conflito interno / Estado desatualizado | Correção Documental | `Proposed` |
| **AMB-006** | `docs/requisitos.md` § 9 (Matriz rastreabilidade) | Estado desatualizado pós-Release 1 | Correção Documental | `Proposed` |
| **AMB-007** | `docs/requisitos.md` § 2 e `docs/visao.md` § 2 | Conflito documental entre branches | Correção Documental | `Defined` (PR #140) |
| **AMB-008** | `docs/requisitos.md` § 5 (RF11) | Termo vago ("maioria clara") vs decisão aprovada | Correção Documental | `Proposed` |
| **AMB-009** | `docs/requisitos.md` § 7 (RNF01, RNF03–08) | Lacuna de homologação formal de RNFs | Decisão Pendente de Governança | `Pending Decision` |
| **AMB-010** | `docs/requisitos.md` § 7 | Lacuna de requisito não-funcional de desempenho | Proposta de Novo RNF | `Proposed` |
| **AMB-011** | `docs/requisitos.md` § 11 e `specs.md` § 7 | Dependência operacional do Resend na R2 | Decisão de Engenharia/Produto | `Pending Decision` |
| **AMB-012** | `docs/visao.md` § 11 e `docs/requisitos.md` § 13 | Referência externa frágil (link absoluto GitHub) | Correção Documental | `Proposed` |

---

## 3. Detalhamento dos Achados (Findings)

### AMB-001: Vagueza e incompletude no RF18 (Rotina de atualização periódica do SIGAA)
- **Localização:** `docs/requisitos.md`, Seção 5 (Módulo 7 — Release 2), linha 136–137.
- **Trecho:**  
  > `[RF18] Rotina de atualização: o sistema deve atualizar os dados importados periodicamente.`
- **Tipo de ambiguidade:** Termo vago / Quantificador sem limite / Requisito incompleto / Critério não verificável.
- **Problema:** O termo "periodicamente" não determina cadência (diária, semanal, mensal), horário preferencial de execução, gatilho (cron do sistema operacional, worker em background ou disparo manual administrativo), tolerância a falhas parciais nem o comportamento em caso de sobreposição de execuções.
- **Interpretações possíveis:**
  1. *Interpretação A:* Cron job diário em nível de container/SO chamando `sigaa-import.sh` fora do horário de pico acadêmico.
  2. *Interpretação B:* Agendador interno na aplicação backend (ex: APScheduler/Celery).
  3. *Interpretação C:* Rotina disparada por endpoint restrito acionado por moderador/administrador.
- **Evidências:** `docs/requisitos.md` seção 9 ("agendamento local ainda não configurado"); `docs/releases/1.0.0.md` linha 31 ("A atualização periódica automática (RF18) fica para a Release 2"); Issue pai #146 e Issue #164.
- **Fonte potencialmente autoritativa:** `docs/requisitos.md` (a definir em conjunto com PO e Time em #164).
- **Impacto:** Impossibilita implementar testes de aceitação automatizados e dimensionar a infraestrutura de execução agendada.
- **Recomendação:** Definir no planejamento da Issue #164 a periodicidade exata (ex.: semanal aos domingos ou diária de madrugada), janela de timeout e tratamento de notificações em caso de falha.
- **Estado:** `Pending Decision`.

---

### AMB-002: Escopo, ator e regras omitidas no RF20 (Comentários em texto livre)
- **Localização:** `docs/requisitos.md`, Seção 5 (Módulo 7 — Release 2), linha 138.
- **Trecho:**  
  > `[RF20] Comentários em texto livre: permitir comentário textual sobre a disciplina.`
- **Tipo de ambiguidade:** Escopo ambíguo / Requisito incompleto / Casos de borda omitidos.
- **Problema:** A redação restringe o comentário a "sobre a disciplina", enquanto o núcleo do produto e a avaliação são centrados no par `(professor, disciplina)`. Além disso, omite regras contratuais fundamentais: limite de caracteres (tamanho mínimo e máximo), multiplicidade (um comentário por usuário substituível como no RF03?), obrigatoriedade (opcional junto com os 5 critérios ou avulso?), anonimato perante o público (RNF01) e ciclo de vida do texto (publicação imediata versus aprovação prévia).
- **Interpretações possíveis:**
  1. *Interpretação A:* O comentário é um campo opcional adicional da avaliação do par `(professor, disciplina)`, compartilhado na mesma submissão e sujeito à regra de substituição única (RF03).
  2. *Interpretação B:* O comentário é uma entidade independente vinculada apenas à `disciplina`, permitindo múltiplos relatos desacoplados de docentes.
- **Evidências:** `specs.md` § 3 (`avaliacoes` não possui campo de comentário); `docs/requisitos.md` § 8 ("Sem campo livre no Release 1"); Issue #154 e #156.
- **Fonte potencialmente autoritativa:** PO (Product Owner).
- **Impacto:** Bloqueia a modelagem relacional de banco de dados (Issue #156), schemas da API e os fluxos de interface do frontend (#159).
- **Recomendação:** Submeter ao PO para decisão antes do início da Issue #156, no âmbito da Issue #154.
- **Estado:** `Pending Decision`.

---

### AMB-003: Atores, gatilhos e regras de negócio omitidos no RF21 (Denúncia de conteúdo)
- **Localização:** `docs/requisitos.md`, Seção 5 (Módulo 7 — Release 2), linha 139.
- **Trecho:**  
  > `[RF21] Denúncia de conteúdo: permitir sinalizar avaliação abusiva.`
- **Tipo de ambiguidade:** Atores ausentes / Requisito incompleto / Comportamento não especificado.
- **Problema:** Não define: quem possui permissão para denunciar (visitante anônimo ou apenas estudante autenticado com e-mail confirmado?); o que exatamente pode ser denunciado (apenas comentários textuais livres do RF20 ou também avaliações numéricas estruturadas?); quais motivos/categorias prévias de denúncia são aceitos; se um usuário pode denunciar o mesmo item múltiplas vezes; e se a denúncia altera imediatamente a visibilidade do conteúdo (auto-ocultação preventiva por limiar de denúncias).
- **Interpretações possíveis:**
  1. *Interpretação A:* Apenas estudantes autenticados denunciam comentários textuais, escolhendo categorias fechadas (ofensa, assédio, spam) e justificativa opcional; o conteúdo permanece público até decisão de um moderador.
  2. *Interpretação B:* Qualquer visitante pode denunciar qualquer elemento; após N denúncias, o comentário fica temporariamente oculto.
- **Evidências:** `docs/requisitos.md` § 4 (não lista ação de denúncia nos perfis); Issue #154 e #160.
- **Fonte potencialmente autoritativa:** PO (Product Owner).
- **Impacto:** Bloqueia a criação da tabela de denúncias, endpoints de registro de denúncia e componentes visuais de sinalização.
- **Recomendação:** Submeter ao PO as opções de permissão e regras de auto-ocultação na Issue #154.
- **Estado:** `Pending Decision`.

---

### AMB-004: Modelo de autorização, perfil e ações no RF22 (Fila de moderação)
- **Localização:** `docs/requisitos.md`, Seção 4 (linha 68) e Seção 5 (Módulo 7), linha 140.
- **Trecho:**  
  > `Moderador: Membro da equipe com privilégio de curadoria | Tudo do estudante + fila de moderação (Release 2)`  
  > `[RF22] Fila de moderação: interface para aprovar ou remover conteúdo denunciado.`
- **Tipo de ambiguidade:** Atores e permissões incompletas / Modelo de dados não especificado.
- **Problema:** Não especifica como um usuário se torna moderador (campo de perfil/role `is_moderator` na tabela `usuarios` ou credencial administrativa específica), quais ações compõem o ciclo de decisão (ignorar denúncia / manter conteúdo; remover comentário mantendo as notas numéricas da avaliação; banir usuário?) e se as decisões geram log de auditoria permanente.
- **Interpretações possíveis:**
  1. *Interpretação A:* Papel `moderador` atribuído via banco/admin a contas institucionais específicas; a tela exibe denúncias pendentes com botões "Acatar denúncia (remover comentário)" ou "Rejeitar denúncia (manter comentário)".
  2. *Interpretação B:* Painel de administração desacoplado com credenciais estáticas de ambiente.
- **Evidências:** `specs.md` § 3 (tabela `usuarios` possui apenas dados básicos sem campo de papel/perfil); Issue #154, #161 e #162.
- **Fonte potencialmente autoritativa:** PO e Arquiteto de Software.
- **Impacto:** Bloqueia o contrato de autenticação/autorização da API e a implementação da interface administrativa da moderação.
- **Recomendação:** Definir o modelo de atribuição de papel e as ações permitidas na Issue #154.
- **Estado:** `Pending Decision`.

---

### AMB-005: Conflito interno sobre o estado de conclusão do RF17 (Cobertura de unidades)
- **Localização:** `docs/requisitos.md`, Seção 11, Tabela de pendências (linha 308) versus Subseção "Escopo de cobertura..." (linhas 312–317).
- **Trecho:**  
  > Linha 308: `| Execução e operação da coleta em todas as unidades | RF17–RF19; escopo de graduação definido abaixo | Time |`  
  > Linhas 312–317: `Em 24/09/2026, ficou definido que RF17 abrange todas as opções da página pública de turmas do SIGAA que tenham ofertas no nível GRADUAÇÃO... A evidência de execução está em estudos/validacao-release-1-sigaa-2026-09-24.md.`
- **Tipo de ambiguidade:** Conflito interno no documento / Estado desatualizado.
- **Problema:** A tabela de decisões pendentes da seção 11 ainda lista a execução da coleta de todas as unidades como pendência bloqueante, embora a subseção logo abaixo e as notas da Release 1.0.0 declarem explicitamente que a decisão foi tomada em 24/09/2026, implementada e validada em PostgreSQL isolado para 211 unidades (PR #130).
- **Interpretações possíveis:**
  1. Trata-se de resíduo textual mantido na tabela de pendências após a resolução ocorrida no final da Release 1.
- **Evidências:** `docs/releases/1.0.0.md`, PR #130, `docs/estudos/validacao-release-1-sigaa-2026-09-24.md`.
- **Fonte potencialmente autoritativa:** `docs/releases/1.0.0.md` e subseção aprovada de `docs/requisitos.md`.
- **Impacto:** Cria incerteza para novos colaboradores e avaliadores sobre se a cobertura do SIGAA foi ou não entregue e homologada.
- **Recomendação:** Remover o item da tabela de decisões pendentes ou registrá-lo explicitamente como "Definido e entregue na Release 1.0.0".
- **Estado:** `Proposed` (para sincronização na Issue #167).

---

### AMB-006: Matriz de rastreabilidade (Seção 9) desatualizada em relação à Release 1.0.0
- **Localização:** `docs/requisitos.md`, Seção 9, linhas 210–222.
- **Trecho:**  
  > `| RF01–RF04 | ... | R1 | Planejado — modelo de acesso validado; envio de e-mail ainda depende das decisões da seção 11 |`  
  > `| RF05–RF07 | ... | R1 | Planejado |`  
  > `| RF08–RF11 | ... | R1 | Planejado |`  
  > `| RF12–RF13 | ... | R1 | Planejado |`  
  > `| RF14–RF15 | ... | R1 | Planejado |`  
  > `| RNF02 | ... | R1 | Validado pelo PO; implementação planejada |`
- **Tipo de ambiguidade:** Estado desatualizado / Divergência de rastreabilidade com o produto entregue.
- **Problema:** A versão 1.0.0 do sistema foi lançada e tagueada em 24/09/2026 com os requisitos RF01 a RF17 e RF19 concluídos e testados. A matriz de requisitos continua classificando esses itens como "Planejado", deixando o documento descompassado da realidade do projeto.
- **Interpretações possíveis:**
  1. A matriz não foi atualizada ao final da Sprint 4 / Release 1.
- **Evidências:** `docs/releases/1.0.0.md`, tag `v1.0.0`, suíte de testes passando.
- **Fonte potencialmente autoritativa:** `docs/releases/1.0.0.md`.
- **Impacto:** Prejudica a rastreabilidade do projeto perante avaliadores e auditores de software.
- **Recomendação:** Atualizar a coluna "Estado" na matriz de rastreabilidade para refletir a conclusão e validação da Release 1.0.0.
- **Estado:** `Proposed` (para sincronização na Issue #167).

---

### AMB-007: Conflito documental entre branches sobre a origem dos requisitos
- **Localização:** `docs/requisitos.md` § 2 (linha 24) e `docs/visao.md` § 2 (linhas 20–22) na branch de auditoria versus branch `develop`.
- **Trecho:**  
  > `Conversas abertas com 20 a 30 alunos da UnB, de diferentes semestres, conduzidas antes da definição de escopo.`
- **Tipo de ambiguidade:** Conflito de versão entre branches / Divergência textual da fonte de verdade.
- **Problema:** A Issue #139 determinou a remoção da menção à pesquisa com 20 a 30 alunos e substituição pela motivação real da equipe: *"Nós percebemos a necessidade de tornar esse conhecimento acessível sem depender de contatos pessoais. Essa motivação guiou o desenvolvimento do produto."* Essa alteração foi aprovada e integrada na branch `develop` (PR #140). Contudo, branches ramificadas a partir de `main` (como `docs/149-clareza-requisitos`) mantêm o texto antigo caso não estejam sincronizadas com `develop`.
- **Interpretações possíveis:**
  1. A branch de trabalho deve incorporar o commit da PR #140 para manter a integridade documental.
- **Evidências:** Commit `069b276` em `origin/develop`, Issue #139, PR #140.
- **Fonte potencialmente autoritativa:** PR #140 aprovada em `develop`.
- **Impacto:** Risco de reintrodução de texto revogado se os branches de documentação da Release 2 não integrarem a alteração canônica de #139.
- **Recomendação:** Garantir que o texto aprovado pela PR #140 permaneça unificado em `requisitos.md` e `visao.md`.
- **Estado:** `Defined` (aprovado na PR #140).

---

### AMB-008: Vagueza na redação do RF11 ("maioria clara") versus regra de empate aprovada
- **Localização:** `docs/requisitos.md`, Seção 5 (Módulo 3), linha 107–108.
- **Trecho:**  
  > `[RF11] Estado conflitante: para os critérios de natureza factual, quando não houver maioria clara entre as respostas, o sistema deve exibir estado "conflitante".`
- **Tipo de ambiguidade:** Termo vago ("maioria clara") / Inconsistência textual com decisão posterior.
- **Problema:** "Maioria clara" é uma expressão imprecisa e não verificável. O PO já resolveu essa ambiguidade na decisão de 13/09/2026 (registrada na Seção 11, linha 276 e em `specs.md` § 4, linha 147), definindo: *"maioria simples; empate exato gera 'conflitante'"*. O texto principal do RF11 na Seção 5 não foi alinhado a essa formulação exata.
- **Interpretações possíveis:**
  1. O RF11 deve ser alinhado textualmente à decisão aprovada: *"quando houver empate exato entre as respostas, o sistema deve exibir estado 'conflitante'"*.
- **Evidências:** `docs/requisitos.md` linha 276; `specs.md` tabela § 4.
- **Fonte potencialmente autoritativa:** Decisão do PO em 13/09/2026.
- **Impacto:** Ambiguidade de interpretação para quem lê apenas o catálogo de RFs sem consultar a Seção 11.
- **Recomendação:** Ajustar a redação do RF11 na fonte de verdade para espelhar a regra de empate exato aprovada.
- **Estado:** `Proposed` (para sincronização na Issue #167).

---

### AMB-009: Lacuna de homologação formal dos Requisitos Não-Funcionais (RNF01, RNF03–RNF08)
- **Localização:** `docs/requisitos.md`, Seção 7, linhas 167–190 e Seção 9, linha 221.
- **Trecho:**  
  > `RNF02 validado pelo PO nesta revisão. Os demais RNFs continuam propostos.`
- **Tipo de ambiguidade:** Estado pendente de governança / Lacuna de validação formal.
- **Problema:** Requisitos técnicos como RNF03 (Argon2id, HTTPS, proteção contra SQLi), RNF04 (Docker Compose reprodutível), RNF05 (migrações Alembic versionadas), RNF06 (arquitetura em camadas) e RNF07 (resiliência na importação por savepoints) foram comprovadamente implementados e testados na Release 1. No entanto, permanecem com estado formal `proposto`. Pela regra de governança do projeto (`skills/governance/project-governance/SKILL.md`), a implementação não valida automaticamente o requisito sem manifestação humana explícita.
- **Interpretações possíveis:**
  1. O PO deve ser consultado formalmente para validar os RNFs já atendidos pela arquitetura entregue na v1.0.0.
- **Evidências:** Código-fonte em `backend/app/`, migrações em `backend/alembic/`, `docs/releases/1.0.0.md`.
- **Fonte potencialmente autoritativa:** PO (Product Owner).
- **Impacto:** Manter requisitos já atendidos como "propostos" transmite a impressão incorreta de escopo não acordado.
- **Recomendação:** Encaminhar solicitação de validação dos RNFs 01 e 03–08 ao PO.
- **Estado:** `Pending Decision`.

---

### AMB-010: Lacuna de Requisito Não-Funcional de Desempenho e Tempo de Resposta
- **Localização:** `docs/requisitos.md`, Seção 7 (Requisitos Não-Funcionais).
- **Trecho:** Ausência de RNF estipulando tempos máximos de resposta para consultas e agregação.
- **Tipo de ambiguidade:** Lacuna em requisitos não-funcionais (Performance e Escalabilidade).
- **Problema:** A agregação dos critérios é calculada dinamicamente em tempo de consulta (`specs.md` § 4, linha 160: *"Agregação é calculada na consulta, não materializada"*). Com a entrada de turmas e avaliações em maior escala na Release 2, operações de comparação e agregação podem sofrer degradação. O documento não estabelece tempos-limite (ex: p95 < 500ms) nem obrigatoriedade de índices de cobertura no PostgreSQL.
- **Interpretações possíveis:**
  1. Criar um RNF09 (Desempenho da consulta e agregação) estipulando teto de tempo de resposta sob carga nominal e exigência de índices relacionais.
- **Evidências:** `specs.md` § 4; `docs/arquitetura.md` § 3.
- **Fonte potencialmente autoritativa:** PO e Arquiteto de Software.
- **Impacto:** Risco de degradação assintótica de performance sem critério formal de aceite para refatoração ou criação de views/índices.
- **Recomendação:** Propor a redação do RNF09 para análise do PO e time de engenharia.
- **Estado:** `Proposed`.

---

### AMB-011: Dependência operacional de envio de e-mail na Release 2
- **Localização:** `docs/requisitos.md`, Seção 11 (linhas 291–297) e `specs.md`, Seção 7 (linhas 234–236).
- **Trecho:**  
  > `Na Release 1, EMAIL_BACKEND=console escreve o link no terminal e é o único modo previsto. A ativação de EMAIL_BACKEND=resend, com chave e remetente configurados externamente, fica planejada para a Release 2.`
- **Tipo de ambiguidade:** Dependência operacional de infraestrutura sem contingência.
- **Problema:** O envio externo pelo Resend depende de credenciais e domínio institucional remetente verificado. Caso o envio falhe em produção (rejeição, timeout ou esgotamento de quota), os documentos não especificam política de reenvio do link, rate limit para evitar abusos nem tratamento da falha na interface do estudante.
- **Interpretações possíveis:**
  1. A Issue #165 deve especificar limites de tentativas, timeouts e fallback de exibição amigável de erro.
- **Evidências:** Issue #165 (`[R2][ACESSO] Verificar prontidão do envio real de confirmação de e-mail`).
- **Fonte potencialmente autoritativa:** Arquiteto de Software e PO.
- **Impacto:** Risco de bloqueio do onboarding de usuários reais em ambiente público caso o serviço de e-mail apresente instabilidade.
- **Recomendação:** Endereçar requisitos de resiliência e rate limit de cadastro na Issue #165.
- **Estado:** `Pending Decision`.

---

### AMB-012: Inconsistência de hiperlinks nos documentos derivados
- **Localização:** `docs/visao.md` § 11 (linha 147).
- **Trecho:**  
  > `[Especificação de implementação](https://github.com/unb-mds/2026-02-UnDb/blob/develop/specs.md)`
- **Tipo de ambiguidade:** Referência absoluta frágil.
- **Problema:** O documento de visão referencia `specs.md` por uma URL absoluta apontando para a branch `develop` no GitHub, enquanto os demais artefatos utilizam caminhos relativos de repositório. Em builds locais do MkDocs ou forks, o link direciona externamente em vez de navegar no próprio workspace.
- **Interpretações possíveis:**
  1. Substituir pelo link relativo adequado ou referência uniforme.
- **Evidências:** `docs/visao.md` linha 147.
- **Fonte potencialmente autoritativa:** Padrão de documentação MkDocs do repositório.
- **Impacto:** Fragilidade de navegação na documentação estática e em revisões offline.
- **Recomendação:** Uniformizar as referências cruzadas entre os documentos de documentação.
- **Estado:** `Proposed` (para sincronização na Issue #167).

---

## 4. Distinção entre Correções Documentais e Novas Decisões de Produto

Em estrita conformidade com os critérios de aceite da Issue #149 e com as regras canônicas de governança (`skills/governance/project-governance/SKILL.md`), os achados foram categorizados em dois grupos disjuntos:

### Grupo A — Correções Documentais (Aptas para Aplicação em #167)
Correções que **não alteram** o escopo, não criam regras de negócio novas e não modificam decisões previamente homologadas. Tratam apenas de sincronização, remoção de inconsistências internas e atualização de estados já verificados:
1. **AMB-005:** Remoção da pendência de coleta de todas as unidades da tabela da Seção 11 de `requisitos.md`, dado que o escopo de `GRADUAÇÃO` foi homologado e entregue na R1.
2. **AMB-006:** Atualização da matriz de rastreabilidade (Seção 9 de `requisitos.md`), marcando RF01–RF17 e RF19 como "Entregues na Release 1.0.0".
3. **AMB-007:** Garantia de persistência do texto aprovado na Issue #139 / PR #140 sobre a motivação da origem dos requisitos em todas as derivações.
4. **AMB-008:** Alinhamento da redação do RF11 de "maioria clara" para "empate exato gera conflitante", espelhando a decisão tomada pelo PO em 13/09/2026.
5. **AMB-012:** Padronização de hiperlinks relativos em `docs/visao.md`.

### Grupo B — Novas Decisões de Produto / Engenharia (Encaminhar ao PO)
Mudanças substantivas que **exigem aprovação humana explícita** do Product Owner antes de qualquer edição na fonte de verdade dos requisitos:
1. **AMB-001 (RF18):** Definição da periodicidade e estratégia de agendamento da reimportação periódica do SIGAA.
2. **AMB-002 (RF20):** Detalhamento do domínio de comentários em texto livre (objeto do comentário, limites de caracteres, multiplicidade e moderação prévia vs reativa).
3. **AMB-003 (RF21):** Definição dos atores com permissão para denunciar, categorias de denúncia e regras de auto-ocultação.
4. **AMB-004 (RF22):** Definição do modelo de moderador, permissões de curadoria e ações cabíveis sobre conteúdo denunciado.
5. **AMB-009:** Homologação formal dos requisitos não-funcionais (RNF01, RNF03–08) já cumpridos na arquitetura da Release 1.
6. **AMB-010:** Deliberação sobre a inclusão de um RNF de Desempenho e Latência de consulta/agregação.
7. **AMB-011:** Definição da política de contingência e rate limit do envio de e-mail institucional na Release 2.

---

## 5. Encaminhamentos Estruturados ao Product Owner (PO)

Abaixo constam as questões objetivas preparadas para deliberação do PO, conforme exigido pelo critério de conclusão da Issue #149:

```markdown
### Pauta de Decisões de Produto para a Release 2

1. Decisão sobre RF20 (Comentários):
   - Questão: O comentário em texto livre deve pertencer exclusivamente ao par (professor, disciplina) como campo opcional da avaliação já existente, ou ser um comentário avulso da disciplina?
   - Proposta da Engenharia: Vincular ao par (professor, disciplina) na tabela de avaliações, limitado a 500 caracteres, opcional, e substituível juntamente com a reavaliação (RF03).

2. Decisão sobre RF21 (Denúncia):
   - Questão: Quem pode denunciar e o que acontece quando uma denúncia é registrada?
   - Proposta da Engenharia: Apenas estudantes autenticados com e-mail confirmado podem denunciar. O comentário permanece visível até julgamento na moderação, exceto se atingir um limiar de 5 denúncias distintas (auto-ocultação preventiva).

3. Decisão sobre RF22 (Moderação):
   - Questão: Como os moderadores são credenciados e quais ações podem tomar?
   - Proposta da Engenharia: Atribuição de perfil 'moderador' via flag no banco de dados. Ações possíveis: 'Acatar denúncia' (remove o comentário textual, mantendo as notas dos 5 critérios) ou 'Rejeitar denúncia' (reabilita o comentário e arquiva a denúncia).

4. Decisão sobre RF18 (Atualização SIGAA):
   - Questão: Qual deve ser a frequência da rotina de atualização de turmas?
   - Proposta da Engenharia: Execução semanal aos domingos às 03:00 UTC via cron containerizado, com log estruturado e notificação em caso de falha.

5. Homologação formal dos RNFs:
   - Questão: O PO aprova a promoção dos RNFs 01, 03, 04, 05, 06, 07 e 08 de 'Propostos' para 'Validados' com base na evidência entregue na Release 1.0.0?
```

---

## 6. Rastreabilidade com as Próximas Issues do Planejamento

| Issue | Papel no Ciclo da Release 2 | Relação com esta Auditoria |
|---|---|---|
| **#149** *(Esta Issue)* | Diagnóstico de ambiguidades e separação de decisões | Produz este relatório e formaliza as pendências |
| **#154** | Detalhar regras de comentário, denúncia e moderação | Consome os achados AMB-002, AMB-003 e AMB-004 e as respostas do PO |
| **#156 / #160 / #161** | Implementação de dados e API (comentários, denúncias, moderação) | Bloqueadas até o fechamento das decisões de #154 |
| **#164** | Operação e agendamento da importação periódica | Consome a resolução do achado AMB-001 (RF18) |
| **#165** | Prontidão do envio real de e-mails | Consome a análise do achado AMB-011 |
| **#167** | Sincronizar requisitos e documentos derivados | Aplica as correções documentais (Grupo A) e as decisões aprovadas na fonte de verdade |

---

*Relatório elaborado conforme as diretrizes do MDS 2026/2 e as regras de governança do Grupo 7.*
