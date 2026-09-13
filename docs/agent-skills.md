# Como usar as Agent Skills do projeto

Este tutorial explica como integrantes e agentes de IA podem trabalhar com as mesmas responsabilidades e regras do G7, independentemente da ferramenta utilizada. Você não precisa instalar uma integração de skills para começar: um agente que consiga ler os arquivos Markdown já pode seguir o procedimento manual.

**Base da investigação:** checkout local do repositório `unb-mds/G7-2026-2`, em 13/09/2026, commit `a934dcee12c770356741b3e0a42ce66a2618d7c8`. Foram inspecionados os nove `SKILL.md`, suas referências, arquivos de entrada, estrutura e documentação relacionada. O estado remoto de Issues, PRs e configurações do GitHub não foi consultado; este inventário descreve o checkout, sem afirmar que corresponde à versão mais recente da `main` remota. Os exemplos não representam execuções de implementação, testes ou review realizadas para este tutorial.

Este documento é explicativo. As regras oficiais do sistema de skills permanecem em [`skills/`](../skills/). Na classificação de `skill-authoring`, esta entrega é **NO-SKILL**: documentação de uso, sem criar ou alterar skills, adapters ou governança.

## 1. O que são as skills

Uma skill representa uma **responsabilidade reutilizável do projeto**. Por exemplo, implementar uma mudança e revisar essa mudança são atividades diferentes, com procedimentos e limites próprios.

Conforme [`skill-authoring`](../skills/governance/skill-authoring/SKILL.md), uma skill deve explicar:

- quando utilizar e quando não utilizar;
- entradas esperadas e pré-condições;
- procedimento e saída esperada;
- restrições e fronteiras de aprovação humana;
- verificações necessárias;
- interação com outras skills;
- tratamento de incerteza, conflitos e falhas.

O `SKILL.md` começa com metadados, incluindo `name`, `description`, versão, categoria e status. A `description` ajuda a selecionar a skill; o arquivo integral orienta sua execução. Ler apenas o nome ou o resumo não equivale a carregar o procedimento.

Uma skill não é um agente separado, não concede acesso a ferramentas e não aprova decisões. O mesmo agente pode atuar em responsabilidades diferentes durante uma conversa, desde que respeite os respectivos limites. Pessoas também podem usar os procedimentos como roteiro de trabalho.

### Estados: o que já vale e o que ainda é proposta

O vocabulário canônico está em `skill-authoring`, seção 3:

| Estado | Significado prático |
|---|---|
| `Defined` | Aprovado e autoritativo no respectivo escopo. |
| `Proposed` | Preparado, mas ainda não autoritativo. |
| `Pending Decision` | Exige decisão humana. |
| `Not Currently Applicable` | Conhecido, mas desnecessário no contexto atual. |

Nos metadados das skills existentes, os status aparecem como `defined` e `proposed`. Consulte `metadata.project-status` antes de usar o procedimento como regra.

**Ler uma proposta não significa adotá-la.** Ela pode ajudar a compreender uma responsabilidade ou preparar uma discussão, mas não pode impor novas obrigações. Se uma ação depender exclusivamente de uma regra proposta, identifique a lacuna e a decisão necessária; continue as partes sustentadas por autoridade existente.

Também separe o estado da skill do estado das decisões que ela menciona. `fastapi`, por exemplo, continua `proposed`, embora registre decisões pontuais de persistência como aprovadas. Verifique a fonte e o alcance dessa aprovação; ela não promove a skill inteira. Da mesma forma, `requirements` ser proposta não invalida requisitos aprovados em outros documentos.

## 2. Onde ficam as skills

### Fonte canônica e estrutura atual

```text
skills/
├── governance/
│   ├── project-governance/
│   │   ├── SKILL.md
│   │   └── references/HUMAN_APPROVAL_BOUNDARIES.md
│   └── skill-authoring/
│       ├── SKILL.md
│       └── references/
│           ├── LIFECYCLE.md
│           ├── SKILL_TEMPLATE.md
│           └── VALIDATION_CHECKLIST.md
├── process/
│   └── requirements/SKILL.md
├── engineering/
│   ├── architecture/SKILL.md
│   ├── code-review/SKILL.md
│   ├── implementation/SKILL.md
│   └── testing/SKILL.md
└── technology/
    ├── docker/SKILL.md
    └── fastapi/SKILL.md
```

O padrão é `skills/<category>/<skill-name>/SKILL.md`. `references/` guarda material de apoio; a estrutura também permite `scripts/` e `assets/`, mas esses diretórios não estão presentes nas skills deste inventário.

### Inventário completo

Os links abaixo abrem a fonte de cada responsabilidade. Todos os nove arquivos declaram `agent-agnostic: "true"`.

| Nome | Categoria | Versão | Status | Responsabilidade |
|---|---|---|---|---|
| [project-governance](../skills/governance/project-governance/SKILL.md) | governance | 1.0.0 | **defined** | Autoridade, decisões, evidências, escopo e aprovação humana. |
| [skill-authoring](../skills/governance/skill-authoring/SKILL.md) | governance | 1.0.0 | **defined** | Criação, manutenção, validação e ciclo de vida das skills; independência de agente e fonte única. |
| [architecture](../skills/engineering/architecture/SKILL.md) | engineering | 1.0.0 | **defined** | Análise de questões estruturais e propostas arquiteturais rastreáveis, sem efetivar decisões. |
| [implementation](../skills/engineering/implementation/SKILL.md) | engineering | 1.0.0 | **defined** | Execução de mudanças de código autorizadas, preservando requisitos, arquitetura e tecnologia. |
| [testing](../skills/engineering/testing/SKILL.md) | engineering | 1.0.0 | **defined** | Planejamento, preparação, execução e avaliação de verificações contra fontes autorizadas. |
| [code-review](../skills/engineering/code-review/SKILL.md) | engineering | 1.0.0 | **defined** | Inspeção de mudanças e comunicação de problemas verificáveis, riscos e lacunas. |
| [requirements](../skills/process/requirements/SKILL.md) | process | 0.1.0 | **proposed** | Proposta para estruturar e manter requisitos rastreáveis e documentos derivados. |
| [docker](../skills/technology/docker/SKILL.md) | technology | 0.1.0 | **proposed** | Proposta para containerização, ambiente local e investigação de falhas de containers. |
| [fastapi](../skills/technology/fastapi/SKILL.md) | technology | 0.4.0 | **proposed** | Proposta de orientação do backend: estrutura, routers, schemas, configurações, domínio e persistência. |

### Arquivos de entrada e adapters: como funciona hoje

Um **bootstrap** é um arquivo de entrada que encaminha o agente às fontes. Um **adapter** adapta a descoberta ou invocação à ferramenta. Nenhum deles deve manter uma versão independente das regras universais.

| Mecanismo | Estado observado no checkout |
|---|---|
| [`AGENTS.md`](../AGENTS.md) | Existe. Declara-se bootstrap, lista as quatro categorias, manda comparar a tarefa com as descriptions e ler integralmente as skills aplicáveis e referências necessárias. Reconhece a precedência das skills canônicas. |
| [`CLAUDE.md`](../CLAUDE.md) | Existe. A seção “Como este projeto usa Skills” encaminha à árvore canônica. Também contém contexto, convenções e restrições de produto; portanto, hoje não é apenas um adapter mínimo. |
| `.agents/skills/` para descoberta nativa | **Ainda não implementado no repositório.** O diretório `.agents/` não foi encontrado neste checkout. |
| `.claude/skills/` para descoberta nativa | **Ainda não implementado no repositório.** O diretório `.claude/` não foi encontrado neste checkout. |
| Configuração `.codex/`, regras Cursor ou instruções Copilot | Não encontradas no checkout inspecionado. Integração específica por esses arquivos: **Ainda não implementado no repositório.** |
| Geração, sincronização ou links de adapters para a árvore canônica | **Ainda não implementado no repositório.** Não foi encontrado mecanismo desse tipo. |

Há, portanto, **descoberta orientada por arquivos de entrada**. Isso não demonstra registro automático das nove skills no catálogo nativo de cada ferramenta. Configurações pessoais e plugins instalados na máquina de um integrante também não demonstram uma integração compartilhada pelo projeto.

### Ressalvas encontradas nas fontes

- `CLAUDE.md` ainda contém regras e resumos além da descoberta. Trate-o como entrada e confira as fontes apontadas; sua presença não cria uma governança exclusiva de Claude. Não mova nem ignore regras silenciosamente: conflitos materiais seguem `project-governance`.
- `fastapi` atribui “estratégia” a `testing`, mas a skill `testing` definida exclui a definição de estratégia global. Para o procedimento de testing, consulte sua própria fonte autoritativa; a referência da proposta não amplia essa autoridade.
- `docker` menciona uma skill de framework ainda não criada, embora `fastapi` já exista como proposta. Uma referência pode estar desatualizada; confira o inventário real.
- A afirmação de autoridade dentro de `requirements` deve ser lida junto de seu status `proposed`. Ela não torna seu procedimento oficialmente adotado.

Essas observações não alteram os arquivos. Se for necessário corrigir o sistema de skills ou a estratégia de adapters, o trabalho retorna a `skill-authoring`, com as aprovações pertinentes.

**Possível evolução futura:** o projeto pode definir adapters mínimos para descoberta nativa. A estratégia não está definida em `skill-authoring`, que a remete a uma definição separada. Este tutorial não escolhe entre links, geração ou outra configuração e não fornece uma instalação futura como se já existisse.

## 3. Como escolher uma skill

Comece pela natureza da tarefa, independentemente de usar Codex, Claude ou um chat.

1. Leia a solicitação e identifique a atividade atual: analisar, implementar, verificar ou revisar, por exemplo.
2. Compare essa atividade com `description`, escopo e exclusões das candidatas.
3. Confira o status da skill.
4. Leia integralmente a skill aplicável e as referências necessárias.
5. Reúna as entradas e verifique pré-condições antes de agir.

| Tarefa | Responsabilidade principal | Limite importante |
|---|---|---|
| Implementar uma Issue autorizada | `implementation` | A Issue precisa fornecer ou apontar comportamento esperado e decisões suficientes. |
| Criar ou executar verificações | `testing` | Criar/alterar testes precisa estar autorizado; a skill não inventa critérios nem ferramentas estruturais. |
| Revisar um diff ou PR | `code-review` | A atividade termina na avaliação e comunicação, sem correção implícita. |
| Analisar uma decisão estrutural | `architecture` | Produz análise e proposta; não aprova nem implementa a decisão. |
| Determinar se algo está autorizado | `project-governance` | Governa limites; não substitui procedimentos de domínio. |
| Criar, alterar ou auditar skills | `skill-authoring` | Consulte também `project-governance` e referências relevantes. |
| Refinar ou desambiguar requisitos | Responsabilidade descrita em `requirements` | A skill está **proposed**; busque fontes aprovadas e decisão humana necessária. |
| Trabalhar em FastAPI ou containers | `implementation`, quando houver mudança autorizada; consulta tecnológica pertinente | `fastapi` e `docker` estão **proposed**; não adote seus procedimentos integralmente como regras aprovadas. |

Não carregue todas as skills por padrão. Descobrir candidatas pelos metadados é diferente de executar todos os procedimentos. Uma pergunta sobre autoridade pode precisar apenas de governança e da fonte da decisão; uma alteração local determinada por decisões existentes não exige análise arquitetural nova.

### Onde procurar os fatos do produto

As skills explicam procedimentos e responsabilidades. O comportamento concreto precisa de fontes autorizadas, como a tarefa humana, requisitos e decisões registradas.

- [`docs/requisitos.md`](requisitos.md) declara-se fonte de verdade dos requisitos. Seu cabeçalho distingue requisitos funcionais e escopo R1 validados de requisitos não funcionais propostos.
- [`docs/arquitetura.md`](arquitetura.md) contém registros arquiteturais; confira o estado da decisão aplicável.
- [`specs.md`](../specs.md) declara-se derivado desses dois documentos e reconhece a precedência deles em divergências.
- Código, configuração, Issues e resultados de execução ajudam a verificar o estado e a intenção, mas sua mera existência não prova aprovação de uma decisão.

Não use “está no repositório” como sinônimo de “está aprovado”. Se houver conflito, aplique somente precedência já definida; quando ela não resolver o caso, exponha as fontes e solicite resolução para a parte afetada.

## 4. Como várias skills trabalham juntas

| Papel na tarefa | O que significa | Exemplo |
|---|---|---|
| Skill principal | Governa o procedimento da atividade atual. | `implementation` durante uma alteração de código autorizada. |
| Dependência consultada | Fornece limites ou contexto necessário, sem assumir toda a atividade. | Consultar governança para avaliar escopo e decisões arquiteturais existentes para implementar. |
| Handoff | Transferência explícita quando muda a responsabilidade. | Encaminhar uma falha encontrada por `testing` à implementação. |
| Governança transversal | Mantém autoridade, evidência e aprovação válidas em todas as atividades pertinentes. | Uma proposta arquitetural continua proposta mesmo depois de tecnicamente recomendada. |

Um percurso conceitual possível é:

```text
requisitos autorizados
  → architecture, se houver questão estrutural
  → implementation
  → testing
  → code-review
  → fluxo de Git/GitHub aplicável e autorizado
```

**Isso não é um pipeline obrigatório definido pelo repositório.** `requirements` continua proposta; uma Issue já suficientemente definida pode começar pela implementação. Uma falha pode exigir voltar da verificação à implementação. A análise arquitetural só entra quando existe questão dessa responsabilidade.

### Referências entre as skills

O mapa abaixo resume encaminhamentos presentes nas seções de interação, sem transformar cada referência em carregamento obrigatório:

| Fonte | Relações relevantes |
|---|---|
| `skill-authoring` | Consulta governança; recebe mudanças do sistema identificadas pelas skills de domínio; menciona `project-audit`. |
| `project-governance` | Remete o ciclo de vida a `skill-authoring`; fornece limites transversais às responsabilidades de domínio. |
| `implementation` | Consome requisitos e decisões estruturais/tecnológicas; encaminha testes, revisão, documentação e operações Git/GitHub. |
| `testing` | Consome comportamento autorizado; encaminha correções a `implementation`, questões estruturais a `architecture` e evidências a `code-review`. |
| `code-review` | Confronta requisitos, arquitetura e diretrizes autorizadas; encaminha correções e verificações às respectivas skills. |
| `architecture` | Consome requisitos e evidências técnicas; encaminha implementação, testes, revisão, tecnologia e registros após as decisões pertinentes. |
| `requirements` — proposta | Relaciona requisitos com governança, arquitetura, implementação, testing, review, tecnologia e processo. |
| `fastapi` — proposta | Referencia requirements, architecture, implementation, testing, docker e skill-authoring. |
| `docker` — proposta | Referencia skill-authoring, orientação de framework e futura responsabilidade de CI/CD. |

`technology-guidelines`, `documentation`, `scrum-github`, `project-audit` e `integracao-sigaa` são nomes referenciados, mas não há `SKILL.md` correspondente no inventário. Skills específicas de Scrum, GitHub e CI/CD: **Ainda não implementado no repositório.** Uma referência não cria a skill nem autoriza o agente a inventar seu procedimento.

### Como fazer um handoff útil

Entregue à próxima atividade o contexto suficiente: objetivo autorizado, fontes, arquivos/diff, decisões vigentes, pendências, verificações efetivamente executadas, resultados e próximo trabalho necessário. Esse é um exemplo de organização, não um formulário novo obrigatório.

O handoff pode ocorrer na mesma conversa, em outra conversa, com outro agente ou com uma pessoa. Trocar de skill não exige trocar de ferramenta. Se abrir outro chat, envie também os arquivos canônicos necessários: um resumo anterior não substitui as fontes.

### Git/GitHub e aprovação humana

A ausência de `scrum-github` não significa ausência de toda orientação. O [`README.md`](../README.md) descreve branch `feature/nome-curto-da-tarefa` a partir da `main`, commits pequenos, PR relacionado à Issue e revisão de pelo menos outro integrante antes do merge. Isso é documentação existente, não uma skill de processo implementada.

O [`AGENTS.md`](../AGENTS.md) exige solicitação ou autorização explícita para commit, push, PR e merge, além de confirmação para operações Git destrutivas. A lista canônica de [fronteiras de aprovação humana](../skills/governance/project-governance/references/HUMAN_APPROVAL_BOUNDARIES.md) inclui merge e fechamento relevante de Issue quando representar aceite ou conclusão oficial. Concluir implementação, testes ou review não concede essas aprovações; referências que provoquem fechamento automático também precisam respeitar esse limite.

Consulte essa referência para a lista completa, incluindo decisões arquiteturais permanentes, alterações de requisito aprovado, tecnologia estrutural, modelo de dados substancial, produto, Scrum, DoD/DoR e governança. O mecanismo operacional exato de registro das aprovações no GitHub permanece `Pending Decision`. Não invente um rito obrigatório para preencher essa lacuna. Quando a autorização explícita já cobrir a ação, prossiga dentro desse escopo; silêncio ou aprovação de outro assunto não bastam.

## 5. Usando com Codex

### Como funciona hoje

O projeto fornece `AGENTS.md` como entrada. A documentação oficial do Codex descreve o carregamento de instruções `AGENTS.md` conforme o diretório de trabalho e a hierarquia de arquivos. Esse mecanismo é da ferramenta; o encaminhamento para `skills/` é do projeto. [Documentação oficial de AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).

A descoberta nativa de skills do Codex contempla `.agents/skills/`. Esse adapter não existe neste checkout; portanto, este tutorial usa leitura explícita dos caminhos canônicos. Não presuma que escrever `$implementation` invoca a skill deste projeto: ela precisa estar disponível no catálogo correspondente. [Documentação oficial de skills](https://learn.chatgpt.com/docs/build-skills).

Nesta investigação, o Codex teve acesso ao checkout local, às instruções `AGENTS.md` fornecidas na sessão e à leitura dos arquivos. Isso permite verificar o uso por arquivos, mas não demonstra que as nove skills estejam registradas nativamente. A disponibilidade de catálogos pessoais em outra instalação deve ser verificada separadamente.

### Passo a passo local

1. Abra a pasta clonada `G7-2026-2` como diretório de trabalho do Codex. Se ainda não tiver o checkout, siga a clonagem no README.
2. Forneça a Issue: número/link, descrição, critérios autorizados, referências e escopo pedido. Um link sozinho não garante acesso ao conteúdo; cole o texto se necessário.
3. Peça a identificação das fontes e a leitura explícita das skills aplicáveis.
4. Autorize claramente a atividade desejada: analisar, implementar, criar testes ou apenas revisar.
5. Ao mudar de responsabilidade, use um dos prompts de handoff abaixo.
6. Confira o diff local e o relato de verificações. Ler uma skill não executa seus comandos automaticamente.

Comandos de inspeção que uma pessoa pode usar na raiz, no PowerShell:

```powershell
git status --short
rg --files skills
Get-Content -Encoding UTF8 skills/engineering/implementation/SKILL.md
```

São exemplos de inspeção, não comandos oficiais de teste. Se `rg` não estiver instalado, use o explorador de arquivos. Para preparar a aplicação, consulte o README atual; não execute exemplos de Compose de uma skill proposta como se já houvesse um arquivo Compose implementado.

### Prompt para iniciar e implementar

```text
Trabalhe no checkout local de G7-2026-2. A tarefa é implementar a Issue #XX.
Contexto da Issue: [cole descrição, critérios autorizados e referências].
Escopo autorizado: [descreva a mudança]. Fora do escopo: [limites relevantes].

Leia AGENTS.md. Antes de alterar código, leia integralmente
skills/governance/project-governance/SKILL.md e as referências necessárias.
Selecione as skills pela description e confira seus status.
Use skills/engineering/implementation/SKILL.md como procedimento principal.
Consulte requisitos, decisões arquiteturais e fontes tecnológicas pertinentes.
Não adote skills proposed como regras aprovadas.

Se faltar acesso à Issue ou a uma fonte essencial, indique a lacuna.
Não redefina requisitos nem arquitetura. Registre decisões ausentes e interrompa
somente o trabalho afetado. Ao entregar, informe diff/arquivos, verificações
realmente executadas, limitações e handoffs. Não execute commit, push ou PR
nesta tarefa.
```

### Handoff para testing e depois review

```text
A implementação da Issue #XX está no diff [identifique arquivos ou referências].
Use skills/engineering/testing/SKILL.md e a governança aplicável.
Fontes do comportamento esperado: [referências].
Autorizo criar ou alterar testes pertinentes à mudança, usando mecanismos
já estabelecidos e sem introduzir decisões estruturais novas.
Execute as verificações disponíveis, classifique os resultados e informe
comandos, contexto, evidências e limitações. Encaminhe defeitos de produção
para implementation; esta etapa não autoriza corrigi-los.
```

```text
Revise o diff [base e versão final, ou patch fornecido] da Issue #XX usando
skills/engineering/code-review/SKILL.md e a governança aplicável.
Considere estas fontes e evidências de testing: [referências/resultados].
Inspecione o contexto necessário, sustente findings e separe sugestões opcionais.
Não altere código ou testes. Informe escopo revisado, limitações e handoffs.
A conclusão técnica não é aprovação formal do PR.
```

## 6. Usando com Claude Code

### Como funciona hoje

Existe [`CLAUDE.md`](../CLAUDE.md) na raiz. Ele encaminha a seleção das skills à árvore `skills/` e manda ler integralmente os arquivos aplicáveis. A ferramenta documenta o carregamento de `CLAUDE.md` pela hierarquia de diretórios. Ela não usa `AGENTS.md` como arquivo nativo equivalente; pedir sua leitura explicitamente é possível. O `CLAUDE.md` atual não contém importação `@AGENTS.md`. [Documentação oficial de memória e instruções](https://code.claude.com/docs/en/memory).

A ferramenta também possui skills nativas em `.claude/skills/`, mas esse diretório não existe no checkout. Registro nativo das skills G7 por esse mecanismo: **Ainda não implementado no repositório.** Um comando `/implementation` não está demonstrado pelo conteúdo deste projeto. [Documentação oficial de skills do Claude Code](https://code.claude.com/docs/en/skills).

O uso abaixo é **leitura explícita/manual das skills canônicas**, apoiada pelo arquivo de entrada existente. Não é instalação nativa de skills e não foi testado em uma sessão Claude Code nesta investigação.

### Passo a passo e prompt equivalente

Abra Claude Code na pasta do repositório, forneça a Issue e peça a leitura pelos caminhos. Confira se o agente identifica as fontes corretas e os status antes de começar. Preserve a distinção entre as orientações do arquivo de entrada e a autoridade das skills e documentos de origem.

```text
Estamos no repositório G7-2026-2. Implemente a Issue #XX:
[cole descrição, critérios autorizados, referências e limites de escopo].

Leia CLAUDE.md como entrada e leia também AGENTS.md.
Para as regras do projeto, localize a fonte canônica em skills/.
Leia integralmente skills/governance/project-governance/SKILL.md,
suas referências necessárias e skills/engineering/implementation/SKILL.md.
Selecione outras skills pela tarefa e preserve seus status.
Consulte os documentos de requisitos e arquitetura aplicáveis; não transforme
as propostas requirements, fastapi ou docker em regras definidas.

Implemente somente o escopo autorizado. Se surgir decisão estrutural ou
requisito indefinido, registre a lacuna e encaminhe a parte afetada.
Entregue arquivos alterados, verificações executadas, limitações e handoffs.
Esta tarefa não autoriza commit, push ou PR.
```

Para testing e review, copie os dois prompts de handoff da seção Codex: eles usam caminhos e responsabilidades do projeto, sem sintaxe exclusiva da ferramenta. Não copie o conteúdo integral das skills para `CLAUDE.md` para conseguir essa portabilidade.

## 7. Usando com ChatGPT/GPT

O caminho depende do acesso disponível na conversa. Não presuma descoberta automática nem execução de comandos a partir do nome “ChatGPT” ou “GPT”.

### Situação 1: o agente possui acesso ao repositório

Indique qual versão deve ser consultada e peça leitura real dos arquivos. Acesso de leitura permite análise; alterações e execuções dependem das ferramentas efetivamente disponíveis.

```text
Use o repositório G7-2026-2 na versão [commit/branch identificada].
Minha Issue é #XX: [contexto e escopo autorizado].
Localize e leia skills/engineering/implementation/SKILL.md como procedimento
principal e skills/governance/project-governance/SKILL.md para as fronteiras
de decisão, incluindo referências necessárias.
Selecione dependências pertinentes pelos metadados e confirme seus status.
Informe quais fontes conseguiu acessar e quais ações consegue executar.
Se não puder editar ou testar, entregue a proposta correspondente e declare
essa limitação, sem apresentar a implementação ou a verificação como executada.
```

### Situação 2: os arquivos já foram fornecidos como contexto

Informe o caminho original de cada arquivo, o commit ou data da cópia e qual tarefa está autorizada. Peça que o agente confirme quais arquivos recebeu integralmente. Se faltar uma referência necessária, forneça-a antes da ação que depende dela.

Enviar uma cópia ao chat é transporte de contexto. Ela não vira fonte independente para futuras alterações: mantenha a origem identificada e atualize a cópia quando a fonte mudar.

### Situação 3: o agente não possui acesso direto

Para uma implementação, disponibilize um pacote proporcional à tarefa:

- `AGENTS.md`, para a orientação de descoberta e os limites ali registrados;
- `skills/engineering/implementation/SKILL.md` integral;
- `skills/governance/project-governance/SKILL.md` e `references/HUMAN_APPROVAL_BOUNDARIES.md`;
- `skills/governance/skill-authoring/SKILL.md`, quando necessário para consultar os estados e a fonte do sistema, ou para trabalho sobre skills; nesse último caso, inclua também suas referências pertinentes;
- descrição da Issue, escopo autorizado e trechos suficientes dos requisitos, arquitetura e especificações, preservando estados e contexto;
- arquivos de código/configuração afetados ou diff com contexto suficiente;
- outras skills selecionadas e referências necessárias; para testar ou revisar, inclua `testing` ou `code-review`, respectivamente;
- comandos documentados, contexto de ambiente e saídas reais, quando disponíveis e relevantes. Não forneça valores de segredos.

Se nem a seleção estiver clara, forneça primeiro os nomes, caminhos, descriptions e status atuais das candidatas. Depois envie integralmente as escolhidas. Isso evita enviar indiscriminadamente toda a árvore.

```text
Você não tem acesso direto ao repositório. Os arquivos fornecidos são cópias
de G7-2026-2 no commit [hash], identificadas pelo caminho original.
Use implementation como procedimento principal e project-governance para
as fronteiras de decisão. A Issue é: [texto e autorização].
Confira o material recebido e solicite referências essenciais ausentes.
Trate skills proposed como propostas. Trabalhe apenas com o contexto fornecido.
Entregue [análise ou patch proposto]. Não alegue leitura de arquivos ausentes,
aplicação de patch ou execução de testes sem evidência de que ocorreram.
```

## 8. Usando com outros agentes

Este é o fallback para qualquer agente capaz de ler Markdown:

1. Forneça acesso ao checkout ou às cópias identificadas dos arquivos.
2. Aponte `skills/` como fonte canônica do sistema.
3. Identifique a responsabilidade pela natureza da tarefa e pelas descriptions.
4. Confira status e carregue integralmente a skill principal aplicável.
5. Carregue apenas dependências e referências relevantes.
6. Reúna entradas, verifique pré-condições e execute o procedimento autorizado.
7. Respeite handoffs, lacunas de evidência e aprovação humana.

Se a ferramenta não puder ler arquivos, cole o texto com seu caminho e origem. Se não puder executar comandos, uma pessoa pode executar as verificações apropriadas e fornecer saídas reais. O agente deve atribuir esses resultados à evidência recebida, sem dizer que os executou.

Não é necessário ensinar uma sintaxe de invocação universal. A forma de descobrir, carregar, referenciar, selecionar ou invocar pode variar; o comportamento do projeto continua na mesma fonte. Uma limitação da ferramenta deve aparecer como limitação, não como alteração silenciosa da skill.

## 9. Exemplos completos

Os cenários abaixo são didáticos. `#XX` e `#YY` são marcadores a substituir, não Issues/PRs consultados. O contexto de produto usado é real: o **RF03** de [`docs/requisitos.md`](requisitos.md) exige impedir avaliações repetidas do mesmo usuário para o mesmo professor na mesma disciplina. O tutorial não afirma que há um defeito atual nessa implementação.

### Cenário A — Implementar uma Issue

**Solicitação ilustrativa:** “Implemente na Issue #XX o comportamento de bloqueio de duplicatas do RF03, dentro das decisões de persistência existentes.”

1. **Recebimento:** leia a Issue, confirme a autorização de implementar e relacione-a ao RF03. Se o contrato de erro não estiver definido nas fontes, não invente um código HTTP para completar a tarefa.
2. **Seleção:** `implementation` governa a mudança; `project-governance` governa autoridade. `testing` e `code-review` entram nas atividades correspondentes. A proposta `requirements` pode ser consultada para entender a responsabilidade, sem virar regra adotada.
3. **Fontes:** leia as skills aplicáveis, o RF03, as partes pertinentes de arquitetura e `specs.md`, além do código e migrações envolvidos. Se consultar `fastapi`, preserve seu status e confira as decisões pontuais nas fontes referenciadas.
4. **Implementação:** faça a menor mudança coerente autorizada. Não acrescente nova identificação do aluno, nova funcionalidade ou troca de persistência por conveniência.
5. **Limites:** se a solução depender de mudança substancial de modelo ou nova decisão permanente, interrompa essa parte e encaminhe a análise/aprovação. Continue trabalho independente quando permitido.
6. **Verificação:** execute verificações de implementação já definidas e disponíveis. Para criação/alteração autorizada de testes, passe a `testing`, relacionando cada caso ao comportamento aprovado.
7. **Handoff:** entregue o diff, as fontes, resultados reais e pendências a `code-review`. Operações de Git/GitHub dependem das orientações e autorizações correspondentes.

Uma passagem de contexto poderia dizer:

```text
Alvo: Issue #XX, bloqueio de duplicatas conforme RF03.
Mudança: [arquivos e comportamento efetivamente alterados].
Fontes: [requisito, contrato e decisão de persistência inspecionados].
Verificações: [comandos executados, resultados e ambiente relevante].
Limitações: [o que não foi verificado e por quê].
Próxima atividade: testing [escopo autorizado], seguido de review do diff.
```

### Cenário B — Testar uma implementação

Suponha que um teste existente bloqueie qualquer segunda avaliação do mesmo usuário para um professor, mesmo em disciplinas diferentes.

| Elemento | Papel na investigação |
|---|---|
| RF03 e decisões autorizadas relacionadas | Fonte para determinar o comportamento esperado. |
| Teste existente | Artefato com uma expectativa a conferir contra a fonte. |
| Resultado da execução | Evidência do que ocorreu naquele contexto. |

Sob `testing`, compare a premissa do teste com o RF03, que inclui a disciplina. Investigue outros contratos autorizados antes de concluir: o teste isolado não cria uma proibição adicional entre disciplinas.

Se houver autorização para alterar testes e fonte suficiente, ajuste a verificação à expectativa autorizada. Não altere o produto apenas para satisfazer o teste antigo. Se a aplicação falhar por banco indisponível, registre falha de ambiente; se a expectativa não puder ser estabelecida, registre resultado inconclusivo. Encaminhe defeitos sustentados a `implementation`, sem corrigi-los implicitamente numa tarefa limitada a testing.

Informe alvo, fonte, teste/comando realmente executado, contexto, saída observada e limitações. Caso nenhum comando tenha sido executado, diga que houve análise ou planejamento, não teste aprovado.

### Cenário C — Code review de uma Pull Request

**Solicitação ilustrativa:** “Revise o diff do PR #YY relacionado à Issue #XX.”

Use `code-review` para identificar base e versão final, ler diff e contexto, confrontar fontes autorizadas e considerar evidências de testing.

Um possível finding, **apenas se confirmado no diff e no contrato aplicável**, seria: “O filtro de duplicidade omite a disciplina e bloqueia uma avaliação permitida pelo comportamento autorizado. Local: [arquivo/trecho]. Evidência: [fluxo e fonte]. Impacto: [caso reproduzível].”

“Eu prefiro outro nome para esta função” é sugestão opcional, salvo padrão autorizado que sustente um problema. Não invente escala de severidade, política de lint ou gate para torná-la obrigatória.

Entregue findings sustentados, sugestões separadas, limitações e handoffs. Não edite código nem testes enquanto atuar exclusivamente em review. Zero findings é resultado possível para o escopo inspecionado; não prova correção global nem aprova formalmente o PR.

### Cenário D — Decisão arquitetural durante a implementação

Durante a tarefa, surge a ideia de introduzir um novo serviço externo para controlar duplicatas.

1. `implementation` identifica que a ideia pode introduzir tecnologia estrutural e alterar responsabilidades do sistema.
2. Registra a dependência como `Pending Decision` e interrompe apenas a parte que a tornaria efetiva.
3. `architecture` analisa se há problema estrutural real, examina as decisões existentes e compara alternativas materialmente relevantes com critérios autorizados. Manter a estrutura atual pode ser a recomendação.
4. Se for necessário escolher tecnologia estrutural, explicita essa decisão e a encaminha à responsabilidade pertinente e à aprovação humana. `technology-guidelines` não existe hoje; não invente a skill nem deixe `architecture` absorver silenciosamente a escolha.
5. A recomendação permanece `Proposed`. Um spike, código experimental ou teste não é execução implícita de `architecture`; precisa do handoff e escopo apropriados.
6. Depois da aprovação necessária, a alteração autorizada volta a `implementation`, com verificações em `testing` e revisão quando aplicáveis.

Enquanto isso, só continue partes independentes que não pressuponham a escolha pendente e atendam aos limites de implementação e governança. Não peça aprovação genérica para “tudo”: descreva a decisão concreta que bloqueia a parte afetada.

### Cenário E — Agente sem integração automática

Uma integrante quer revisar um patch num chat que só recebe texto.

1. Envia o `SKILL.md` integral de `code-review`, governança e referências necessárias, com caminhos originais e commit de origem.
2. Fornece o patch, sua intenção e fontes pertinentes do comportamento esperado.
3. Explica que o pacote é uma cópia para contexto e que a fonte permanece no repositório.
4. Pede confirmação do material recebido e revisão limitada ao que está disponível.
5. Se faltar contexto de uma chamada, fornece o arquivo solicitado ou aceita a limitação explicitamente registrada.
6. Leva o resultado à equipe, sem tratá-lo como aprovação formal e sem alegar execução de testes pelo chat.

O procedimento de review continua o mesmo. Apenas o transporte dos arquivos mudou.

## 10. Prompts reutilizáveis

Substitua os campos entre colchetes. Estes prompts apontam às fontes; não substituem a leitura nem criam autorizações fora do escopo declarado. Os exemplos de testing abaixo explicitam se a criação de testes está autorizada.

### Iniciar uma Issue

```text
Analise a Issue [número/link e conteúdo disponível]. Leia AGENTS.md e
skills/governance/project-governance/SKILL.md, com referências pertinentes.
Selecione as skills aplicáveis por description e status. Localize as fontes
do comportamento esperado, delimite o escopo e identifique decisões pendentes.
Nesta etapa, entregue análise e próximos passos; não altere código.
```

### Implementação

```text
Implemente [mudança autorizada] da Issue [referência]. Leia integralmente
skills/engineering/implementation/SKILL.md e a governança aplicável.
Fontes e limites: [referências e escopo]. Consulte dependências pertinentes
sem promover propostas. Entregue a menor mudança coerente, verificações
realmente executadas e handoffs. Registre lacunas em vez de inventar decisões.
```

### Testing

```text
Verifique [implementação/diff] conforme [fontes autorizadas]. Leia
skills/engineering/testing/SKILL.md e a governança aplicável.
Autorizo criar/alterar testes pertinentes usando mecanismos estabelecidos.
Confira as premissas dos testes existentes; eles não são requisitos por si só.
Informe execuções, resultados, classificação das falhas e limitações.
Encaminhe correções de produção; elas não estão autorizadas nesta etapa.
```

### Code review

```text
Revise [diff/base/versão] com skills/engineering/code-review/SKILL.md e
a governança aplicável. Intenção e fontes: [referências]. Evidências de
testing disponíveis: [resultados, ou ausência]. Sustente cada finding,
separe sugestões opcionais e registre limitações. Não altere código/testes
nem converta a conclusão em aprovação formal de PR.
```

### Investigação arquitetural

```text
Analise [problema e escopo] usando skills/engineering/architecture/SKILL.md
e skills/governance/project-governance/SKILL.md, com referências necessárias.
Confirme se a questão é estrutural. Examine decisões existentes, impactos
e alternativas pertinentes com critérios autorizados. Entregue recomendação,
evidências, incertezas e decisões necessárias. Não efetive a recomendação,
escolha tecnologia silenciosamente ou implemente uma prova de conceito.
```

### Trabalhar com várias skills

```text
Resolva [tarefa e escopo autorizado]. Leia AGENTS.md, identifique a skill
principal de cada atividade e consulte apenas dependências relevantes.
Autorizo implementação e criação/alteração de testes pertinentes usando
decisões já estabelecidas, seguidas de revisão técnica do diff.
Use implementation, testing e code-review nos respectivos procedimentos,
com governança transversal. Faça handoffs explícitos ao mudar a responsabilidade.
Questões estruturais novas devem ser analisadas separadamente; preserve
as aprovações necessárias. Não execute commit, push, PR ou merge nesta tarefa.
```

### Agente que não conhece o projeto

```text
Este é o projeto G7 de MDS/UnB. Leia AGENTS.md e descubra as skills em
skills/<category>/<skill-name>/SKILL.md. A fonte canônica do sistema é skills/;
arquivos específicos de ferramentas são entradas/adapters.
Minha tarefa é [descrição]. Confira descriptions e status, leia integralmente
as skills aplicáveis e referências necessárias. Informe fontes acessíveis
e lacunas essenciais. Se só tiver cópias, preserve caminhos e origem delas.
Não presuma requisitos, aprovações nem verificações não executadas.
```

### Pedir seleção autônoma das skills

```text
Para a tarefa [descrição], determine quais skills do checkout são aplicáveis.
Compare as descriptions, confira status e leia escopo/exclusões das candidatas.
Indique a principal, dependências necessárias e possíveis handoffs, com
justificativa curta. Diferencie proposed de defined e referências a skills
inexistentes. Não carregue todas por padrão. Depois execute somente
[atividade explicitamente autorizada].
```

## 11. Erros comuns

| Erro | Como evitar |
|---|---|
| Copiar a skill inteira para vários arquivos de agentes | Referencie a fonte canônica; cópias transportadas para chat precisam de origem e não são novas fontes de manutenção. |
| Manter versões diferentes da regra em Claude e Codex | Mude a regra em sua skill, seguindo `skill-authoring`; limite adapters à descoberta/invocação. |
| Tratar adapter como fonte canônica | Siga os links até a regra e seu status; exponha conflitos sem criar precedência por preferência. |
| Usar `proposed` como `defined` | Confira metadados e aprovação aplicável; sugestão não se torna obrigação por existir num arquivo. |
| Carregar todas as skills em toda tarefa | Selecione pela responsabilidade e leia dependências pertinentes. |
| Usar `implementation` para redefinir requisito | Registre a lacuna e encaminhe a decisão, preservando a parte independente. |
| Usar `code-review` para alterar diretamente código | Entregue findings; a correção passa a `implementation` dentro do escopo autorizado. |
| Usar `testing` para inventar critérios de aceite | Relacione expectativas às fontes autorizadas; um teste existente não basta. |
| Usar `architecture` para escolher silenciosamente tecnologia | Explicite a dependência tecnológica e a aprovação necessária; análise não efetiva a escolha. |
| Confundir conclusão técnica com aprovação humana | Review, testes e artefatos prontos não aprovam PR, merge, produto ou arquitetura. |
| Assumir verificação não executada | Exija relato fiel de comando/inspeção, contexto e resultado; registre ausência ou inconclusão. |
| Presumir `/implementation` ou `$implementation` como integração G7 | Confira o catálogo e sua origem; no estado atual, use leitura explícita pelo caminho. |
| Executar exemplo de uma proposta como comando oficial | Confira documentação e arquivos reais; exemplos não demonstram ambiente implementado. |
| Supor que skill ausente elimina regras existentes | Consulte documentos e autorizações disponíveis; não invente o workflow faltante. |

### Conferência deste tutorial

A revisão documental comparou estas orientações com `skill-authoring`, suas três referências, `project-governance` e `HUMAN_APPROVAL_BOUNDARIES.md`, além das fronteiras das skills de engenharia. Foram preservados fonte única, status, escopo, evidência, handoffs e aprovação humana. Nenhuma skill ou configuração de agente foi alterada ou promovida. A documentação oficial das ferramentas foi consultada para distinguir capacidade da ferramenta de integração presente no checkout; não foi realizado teste de instalação ou invocação nativa em cada agente.

# Quick Start

1. Leia a Issue/tarefa e identifique o escopo autorizado.
2. Consulte `project-governance` quando houver autoridade, decisão, evidência, escopo ou aprovação envolvidos.
3. Compare a tarefa com as descriptions e escolha a responsabilidade principal.
4. Confira o status e leia integralmente o `SKILL.md` aplicável em `skills/`.
5. Consulte somente dependências, referências e fontes de produto necessárias.
6. Verifique pré-condições e execute a parte autorizada do procedimento.
7. Faça handoff quando a responsabilidade mudar, levando fontes e evidências.
8. Preserve propostas e decisões pendentes; não transforme hipótese em decisão.
9. Relate apenas verificações realmente executadas e explicite limitações.
10. Quando uma decisão humana for necessária, interrompa apenas a parte afetada e apresente a decisão concreta; continue trabalho independente permitido.
