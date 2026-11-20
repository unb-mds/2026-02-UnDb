# Revisão de sessões, abuso e logs — #266

## Estado e escopo

Revisão técnica local de 16/11/2026. **Entrega parcial para revisão; não constitui aceite
integral da issue nem validação jurídica.** Não houve acesso a contas, logs, credenciais ou banco de
produção, testes ofensivos, carga ou envio à IA. Todos os ensaios usam dados sintéticos.

Base: `develop@d99916e93186864c2769ae95ea577bba477b4e17`, obtida após `git fetch origin`.
A cópia principal estava em `5e07337`, com arquivos não rastreados da #251, preservados.
Trabalho isolado em `fix/266-sessoes-abuso-logs`, worktree `.worktrees/issue-266`.
`7b0bd73` é referência histórica, não a base desta implementação.

## Diagnóstico anterior às alterações de código

Registro preparado antes da implementação, a partir da leitura do código, requisitos,
ADRs, documentação operacional e discussões relacionadas. Evidência estática ainda não
é evidência de teste. As seções seguintes serão completadas com os resultados observados.

| Categoria | Diagnóstico e evidência inicial | Encaminhamento |
|---|---|---|
| Já existente; revalidar em testes | RF02/#47/#49: sessão aleatória com hash no banco, cookie HttpOnly/Lax/Secure fora de DEBUG, renovação de sete dias, logout no servidor | Preservar; não reimplementar |
| Já existente; revalidar em testes | RF24/PR #255: uma hora, uso único, troca transacional, revogação de todos os links de recuperação e sessões; login e troca bloqueiam usuário no PostgreSQL | Preservar; SQLite não comprova concorrência PostgreSQL |
| Confirmado por inspeção | Handler padrão de validação pode devolver `input` e contexto de exceção; não existe sanitização central das respostas | Reproduzir localmente; remover valores recebidos mantendo HTTP 422 e mensagens úteis |
| Confirmado por inspeção | Engine SQLAlchemy não oculta parâmetros; worker usa `logging.exception`; Uvicorn usa access log padrão com caminho/query e cliente | Testar com dados sintéticos; minimizar nas fronteiras de gravação |
| Confirmado por inspeção | Adaptador console registra destinatário e link completo; esse comportamento local é explicitamente aprovado no ADR03/RF24 | Preservar o uso local deliberado; impedir exposição acidental fora de DEBUG, sujeito à conciliação do contrato |
| Confirmado como lacuna de controle | Não há verificação explícita de origem nos endpoints mutáveis; CORS e SameSite não substituem CSRF | Proposta de comportamento deve receber aprovação antes de entrar em vigor |
| Confirmado como limitação | PEND-263-ABUSO: orçamento 30/minuto configurável, comum a criação/consulta/complemento, HMAC do cliente, 60 segundos, teto de 4.096 entradas, apenas memória/processo | Não declarar distribuído; testar janela/reinício/instâncias e manter pendência operacional |
| Dependente de infraestrutura | Proxy confiável, peers do Render, tratamento de cabeçalhos, número de workers, logs de borda, permissões novas de RF24/RF25 | Solicitar evidência sanitizada ao operador; não confiar em cabeçalhos por suposição |
| Dependente de decisão humana/jurídica | Novos limites HTTP/conta/origem, comportamento em falha, retenção/acesso/descarte de logs, bases e enquadramento de guarda | Equipe/PO e revisão jurídica; #261/#262/#267, sem prazo ou base inventados |
| Apenas proposta | Skills de segurança/incidentes da #240/PR #244 continuam `proposed`; referências históricas sobre IA assistiva estão superadas pela autorização da #239 | Não promover skills nem mudar política de publicação |

## Fontes internas consultadas

Issues #47, #49, #170, #171, #239, #240, #261, #263, #265, #266, #267, #268,
#269, #271 e épico #272, incluindo comentários disponíveis. Também foram conferidas
#260, #262 e #264 para confirmar papéis e limites dos encaminhamentos. #255 é uma **PR**, embora
referida como issue no pedido. PRs #244, #245, #255 e #275: metadados, discussão e
implementação integrada na base. Comentários automáticos de preview não são homologação.

Fontes de produto: `docs/requisitos.md` (RF01–RF04/RF14/RF20–RF25 e estados dos RNFs),
`specs.md` (derivado), `docs/arquitetura.md` e `docs/adrs/index.md`. Operação:
`docs/hospedagem.md`, `docs/acesso-postgresql-api.md`, `docs/inicializacao-render.md`,
`docs/continuidade-operacional.md`, `docs/canal-titulares.md`, `docs/moderacao-ia.md`,
`frontend/docs/recuperacao-senha.md`, `CONTRIBUTING.md`, CI, Dockerfiles, Compose,
Alembic e exemplos de ambiente. Documentos antigos de infraestrutura têm ressalvas
superadas pelas consolidações datadas das #170/#171; o histórico não foi tomado como
estado atual de produção.

## Decisões e propostas de comportamento

### Origens e CSRF — proposta apresentada e posteriormente aprovada

Aplicar a POST/PUT/PATCH/DELETE em `/api` validação da origem exata contra a lista
configurada, sem derivá-la de Host ou X-Forwarded-Host. Origem explícita externa,
`null`, malformada ou duplicada: negar antes de autenticação/efeitos. Sem Origin:
validar a origem de Referer quando presente; sem ambos, negar operações com cookie de
sessão e login, preservando clientes sem cookie nas demais operações. Frontend atual
usa fetch JSON com credenciais e envia Origin pelo navegador. Não acrescentar origem
por curinga, não aceitar subdomínios automaticamente. A origem da API só pode ser
incluída por configuração explícita. GET continua público conforme seus contratos;
renovação de sessão e limpeza oportunista de moderação via GET merecem avaliação própria.

Essa proposta evita um token CSRF adicional e uma mudança de schema; restringe clientes
com cookie que hoje não enviam metadados. Exige aprovação e atualização da fonte de
requisitos **antes** de ser aplicada. Alternativa: token CSRF vinculado à sessão e header
obrigatório, com alteração do frontend; maior custo de integração e mesma necessidade
de aprovação. Nenhum dos mecanismos elimina XSS ou abuso por clientes HTTP.

**Decisão em 16/11/2026:** o solicitante respondeu explicitamente “Aprovar a proposta de
CSRF” à pergunta que descrevia o comportamento acima. A restrição foi registrada primeiro
em `docs/requisitos.md`, depois em `specs.md` e implementada em `core/origins.py`.
Não houve promoção de skill ou aprovação implícita de rate limit/retenção.

A confirmação seguiu também [project-governance](https://github.com/unb-mds/2026-02-UnDb/blob/d99916e93186864c2769ae95ea577bba477b4e17/skills/governance/project-governance/SKILL.md):
“O agente não pode tratar uma ação sujeita a aprovação como decidida ou efetivá-la sem
autorização humana explícita.” A própria #266 exigia validação de novos comportamentos;
a autorização específica foi recebida, não presumida do início do trabalho.

### Limites — decisão pendente

Não alterar os valores existentes. Definir por operação finalidade, sujeito (conta ou
origem confiável), janela, cota, recuperação, exceção para redes compartilhadas, impacto
em titulares e comportamento na indisponibilidade. Comparar borda aprovada versus
contador transacional no PostgreSQL existente antes de propor Redis ou fornecedor novo.
Persistência compartilhada exige avaliação de custo, contenção, descarte, permissões e
dados; nenhuma nova tabela/serviço foi autorizada por esta análise.

## Integração inicial e pendências recebidas

Retomada de [PEND-263-ABUSO](https://github.com/unb-mds/2026-02-UnDb/issues/266#issuecomment-6905877881),
com [registro no épico](https://github.com/unb-mds/2026-02-UnDb/issues/272#issuecomment-6905832664).
Leitores/atendentes mantêm as allowlists de contas confirmadas; consulta/complemento
continuam disponíveis mesmo com criação suspensa. PEND-263-RET/INV/ESC/OPS não são
resolvidas pela revisão de segurança. Nicolas acompanha a origem; não se inventa novo
responsável jurídico ou operacional.

#261 deve consumir o inventário técnico de logs e fornecedores; #265 deve revisar os
contratos/caches/erros sem retirar acessos de RF22 por suposição; #267 deve consumir os
eventos seguros e as limitações de diagnóstico/retenção; #268/#269 devem descrever somente
práticas verificadas, sem prometer bloqueios ou anonimização. #271 precisa conferir a
redação sobre identidade e proteção; não requer mudar fórmulas ou limiares. Destinos e
responsáveis adicionais devem ser validados pelo PO no acompanhamento do épico.

## Metodologia e fronteiras de confiança

Leitura de fontes atuais e históricas, inspeção de routers/schemas/services/repositories,
configuração de servidor/CI/containers e destinos de dados. Busca por logging, prints,
tracebacks, corpos, headers, tokens, erros convertidos em strings e clientes externos.
Ensaios determinísticos por serviço, ASGI e navegador local; scanners de dependências
somente para versões/nomes. Busca limitada no histórico sem imprimir correspondências.

Ativos: credenciais, sessões, textos privados, associação interna conta–avaliação,
evidências de titulares, segredos de provedores e disponibilidade. Atores: visitante,
conta sem confirmação, estudante confirmado, autor, moderador, reconciliador, leitor e
atendente do canal, operador e fornecedores. Fronteiras: navegador → API (cookies/JSON),
API → PostgreSQL (papel de runtime), Alembic → PostgreSQL (administração), API →
Resend/OpenAI, processos → stdout/stderr, infraestrutura → logs/backup. Autorização
de moderar não concede reconciliação ou atendimento automaticamente.

As classificações usadas são **Confirmado** (evidência direta), **Hipótese** (condição não
comprovada), **Já satisfatório** (controle validado no recorte), **Dependente de
infraestrutura** e **Dependente de decisão humana/jurídica**. Prioridade da issue não
equivale a incidente. Não foram coletadas evidências privadas nem publicado roteiro
de exploração. As instruções de security-review foram lidas como proposta; a regra
histórica que descreve IA exclusivamente assistiva foi confrontada com a #239 vigente.

## Mapeamento dos fluxos sensíveis

| Fluxo / dados recebidos e persistidos | Autenticação, autorização e controles existentes | Abuso/saídas e limites da evidência |
|---|---|---|
| Cadastro: nome, e-mail institucional, senha, retorno opcional; nome/e-mail/hash Argon2id e hash do token no banco | Domínio aluno.unb.br; campos extras rejeitados; senha 8–128; resposta 202 genérica; retorno interno validado | Automação/envio excessivo sem limitador HTTP geral; tempo de resposta não foi tratado como prova de não enumeração. Resend recebe destinatário e corpo do link. Logs locais console são exceção restrita. |
| Confirmação: token no corpo POST; hash/expires_at/used_at e conta confirmada | Token aleatório, 24h, uso único; repository bloqueia token; GET da página não confirma diretamente no backend | Tentativas e requisições repetidas sem cota geral. Página frontend dispara POST; noindex já existente, no-referrer acrescentado. Concorrência real PostgreSQL não exercitada. |
| Login: e-mail/senha; nova sessão/hash/expiração | Verifica hash; bloqueia linha do usuário; token novo independente da entrada; HttpOnly/Lax/Secure fora de DEBUG | Sem limite de tentativas aprovado. Cada login cria sessão adicional; não há limite simultâneo ou painel de dispositivos aprovado. Resposta contém mensagem e Set-Cookie, sem identidade. |
| Consulta de sessão: cookie; renova expires_at | Sessão opaca no servidor, 7 dias de inatividade; cookie também renovado; inválida não autentica | GET altera apenas o prazo conforme RF02, sem alterar credenciais/conteúdo; consulta pública comum não renova. Cache auth agora no-store. Não prometer expiração absoluta ou rotação periódica inexistente. |
| Logout: cookie; remoção da sessão | Exige sessão válida, remove servidor/cookie | Origem agora conferida antes de renovar/autenticar. Remoção do cookie também preservada na resposta 401, corrigindo descarte perdido ao levantar HTTPException. Não revoga as demais sessões, conforme contrato atual. |
| Recuperação/redefinição: e-mail; depois token e nova senha | 202 genérica inclusive falha de entrega, token separado com hash/1h/uso único; troca atômica invalida links e todas as sessões, sem confirmar e-mail ou autenticar | Sem cota HTTP geral. Falha de envio não invalida link anterior. Regressões cobrem rollback, senha anterior e sessões antigas. Serialização real PostgreSQL depende de homologação; a #255 não foi reimplementada. |
| Avaliação e comentário: critérios, professor/disciplina e texto opcional ≤500 | Sessão confirmada; unicidade/substituição no banco; autoria para retirada; critérios preservados durante triagem; publicação somente conforme RF20 | Unicidade não é limite de frequência. Texto pode identificar indiretamente; payload externo elegível contém texto/modelo. Erros de entrada agora não refletem corpo. Sem mudar limiar, política de publicação ou filtro da #252. |
| Denúncia: versão e motivo fechado; conta opcional | Visitante permitido; conta não confirmada também; duplicata aberta por conta/versão; suspensão em 50 contas distintas; autoria/impedimentos de moderador | Visitantes podem repetir segundo RF21, sem deduplicação por IP aprovada. Limiar de suspensão não é cota HTTP nem prova de procedência. Registros privados, sem justificativa textual livre. |
| Moderação/administração: ação/motivo; versões, decisões e identidades internas | Moderador confirmado, impedimentos de autoria/denúncia; reconciliador separado; decisão de identidade usa versão/locks. Concessões operacionais são CLI, não cadastro público | Texto/nome/e-mail internos são acesso aprovado por RF22, sujeitos à revisão da #265; não foram removidos por suposição. Sem cota HTTP própria. Origens conferidas nas ações e triagem; autorização continua obrigatória. |
| Titulares: categoria/alvo/descrição/evidência; protocolo UUID, hash da chave e eventos | Sem login; chave no corpo; compare_digest; respostas genéricas para protocolo/chave inválidos; histórico público só RESPOSTA/COMPLEMENTO; sem envio à IA/upload | Criação/consulta/complemento compartilham orçamento por cliente/processo; sem equivalência distribuída. Texto de solicitante não é visitado como URL pelo servidor. Suspender criação não impede acompanhamento; risco de rede compartilhada permanece. |
| Atendimento: sessão confirmada/allowlist UUID; tipo/texto, autor e data de eventos | Leitor pode consultar; só atendente registra; nenhum privilégio de moderação implícito; no-store/no-referrer | Sete testes anteriores revalidados; não houve configuração de contas reais ou grants novos. Respostas motivadas e legitimidade operacional continuam dependentes das #261/#262/#264/#267. |

## Achados confirmados e tratamento

| ID / classe | Evidência verificável e impacto | Tratamento / estado |
|---|---|---|
| F266-01 — Confirmado | Ensaio local anterior retornou HTTP 422 com valor sintético de token/senha em `input`. `ctx`, `msg` e até nome de campo extra podem carregar entrada | Handler central mantém 422/estrutura detail e mensagem genérica, sem valores/contexto; regressões em auth/canal. Corrigido localmente. |
| F266-02 — Confirmado | Ausência de verificação explícita de origem; endpoints sem corpo também mutam. CORS deixa servidor processar algumas requisições mesmo sem permitir leitura da resposta | Restrição transversal aprovada, aplicada antes das dependências/efeitos a todos os métodos mutáveis `/api`. Testes de origens, cookie, ausência, duplicatas e preflight. |
| F266-03 — Confirmado | Engine sem hide_parameters; exceções/importador/worker podiam formatar dados de driver; access log padrão incluía caminho/query/cliente | Parâmetros ocultos; erros inesperados genéricos; formatter por allowlist; mensagens de importação sem exceção bruta; worker sem traceback. Não higieniza registros já gravados. |
| F266-04 — Confirmado | Console podia registrar links/destinatário fora de uso local; confirmação sem política de referrer explícita | Console exige DEBUG; comportamento local aprovado preservado. Páginas de confirmação/redefinição recebem no-referrer/no-store. Não elimina URL do primeiro acesso nem logs da borda. |
| F266-05 — Confirmado | A remoção do cookie na Response temporária se perdia em HTTPException 401 | Set-Cookie de remoção propagado na exceção e testado via HTTP; auth recebe no-store. A sessão inválida já era negada antes. |
| F266-06 — Confirmado como limitação | Orçamento do canal e IA é memória/processo; reinício e estado separado recebem nova cota | Limitação documentada/testada com relógio controlado. Nenhum contador distribuído ou nova política foi implantado. PEND-263-ABUSO permanece parcial. |
| F266-07 — Confirmado por versão | Lock frontend corresponde a advisories; Python runtime não possui lock | [Anexo de dependências](dependencias-issue-266.md), correções disponíveis e condições registradas. Atualização dirigida ainda pendente de encaminhamento pelo PO. |

Não houve confirmação de ataque, vazamento ocorrido ou exploração pública. XSS no cliente,
roubo de sessão por extensão, coordenação de contas e inferência por texto/amostra são
ameaças plausíveis, **não incidentes demonstrados**. A formatação segura não é detector de
segredos universal; um novo handler, agente de observabilidade ou print pode contorná-la.

## Análise específica de CSRF, CORS e cookies

CORS regula leitura/preflight entre origens no navegador; SameSite regula contexto de
envio do cookie entre sites. Frontend e API em subdomínios do mesmo domínio são origens
distintas e podem ser do mesmo site. Autenticação identifica sessão, autorização verifica
operação/objeto/papel e CSRF confere contexto da operação. Nenhum desses conceitos foi
usado como sinônimo.

O controle implementado compara esquema/host/porta exatos da configuração, não Host ou
X-Forwarded-Host. Rejeita Origin inválido/null/externo/duplicado, mesmo com Referer válido.
Sem Origin usa a origem de Referer (caminho/query não são registrados); sem ambos rejeita
login ou cookie presente. Clientes sem cookie nas demais operações continuam sujeitos ao
contrato/autorização. GET/HEAD/OPTIONS não recebem bloqueio de mutação. Não há exceção
por DEBUG. CORS fica externo ao middleware para preservar o preflight existente.

Cobertura: cadastro, confirmação, login/logout, recuperação/redefinição, avaliação,
retirada, denúncia, confirmação de agradecimento, ações/triagem de moderação, decisões de
identidade, criação/consulta/complemento e eventos do atendimento. Rotas novas sob `/api`
com POST/PUT/PATCH/DELETE herdam a restrição. GETs de sessão e limpezas oportunistas já
existentes mantêm efeitos definidos; nenhuma decisão de conteúdo é exposta por GET.

A lista CORS agora é também fronteira de origem para escrita: usar origens exatas,
sem caminhos, `*` ou prévias arbitrárias. Swagger no domínio da API não ganha exceção;
requer origem explicitamente autorizada para escrever. Scripts com cookie devem enviar
Origin/Referer autorizado. Requisições HTTP podem forjar esses headers: o mecanismo é
proteção de navegador, não autenticação ou proteção contra bots. Risco de XSS e scripts
na origem autorizada permanece. Referência técnica: [OWASP CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html).

## Inventário e decisão sobre abuso

| Operação | Controle real | Limitação / decisão necessária |
|---|---|---|
| Cadastro/login/confirmação/recuperação | Validação de tamanho/domínio, resposta genérica onde definida, tokens aleatórios/expiração | Sem cota HTTP/conta/origem na aplicação; borda não inspecionada. Limites e reação a falhas dependem dos responsáveis. |
| Avaliação/retirada | Unicidade/upsert, sessão confirmada e autoria | Não limita frequência ou consumo de CPU/banco. Não implantar cota arbitrária. |
| Denúncia | Motivo fechado, deduplicação da conta e limiar de suspensão | Não limita visitantes ou HTTP; mudar repetição/limiar alteraria RF21. |
| IA manual/automática | 5/minuto e 100/dia configuráveis por processo, tetos defensivos 30/1.000; tamanho/timeout/uma tentativa | Orçamento de provedor, não de login/denúncia. Workers/reinícios mudam cota efetiva. Preservado como entregue na #239. |
| Canal público | 30/minuto herdado, configurável; janela fixa 60s compartilhada entre três rotas; HMAC do cliente; máximo 4.096 entradas; lock local | Sem persistência, distribuído ou isenção de rede compartilhada. Saturação do mapa também retorna 429/Retry-After. Valor técnico existente não é homologação geral de proporcionalidade. |
| Atendimento/moderação/reconciliação | Sessão confirmada e papel/allowlist; impedimentos/versão conforme operação | Sem cota HTTP própria; aprovação de eventual limite deve considerar operação legítima. |

O teste mostrou que alterar X-Forwarded-For diretamente não muda o bucket do limitador;
isso **não** prova segurança do proxy: Uvicorn pode transformar `scope.client` antes da
aplicação. Teste do middleware do servidor confirmou essa diferença quando o peer é
confiável. [Uvicorn](https://uvicorn.dev/settings/#http) documenta a confiança configurável;
não configurar confiança global `*` por conveniência. Não foi alterado proxy/HTTPS.

Render é o proxy documentado nas #170/#171. Sua [documentação de Web Services](https://render.com/docs/web-services)
explica terminação TLS e encaminhamento HTTP; isso não comprova cadeia de IP/peers,
limpeza de cabeçalhos ou isolamento do serviço específico do UnDb. É necessário ao operador
confirmar configuração efetiva e número de instâncias/forwarded-allow-ips, com evidências
agregadas/sintéticas. Caso contrário, titulares legítimos podem compartilhar bucket ou
identidade incorreta; falsificação/agrupamento no deploy são **hipóteses dependentes de
infraestrutura**, não falhas demonstradas em público.

Recomendação ainda não efetiva: comparar limitação da borda já contratada com contador
transacional PostgreSQL. Borda reduz tráfego que chega à API, mas pode ter custo e
identidade distinta; PostgreSQL compartilha estado sem fornecedor novo, porém adiciona
escritas/contenção, grants, dados e descarte. Memória é simples, mas reinicia/multiplica.
Redis/serviço externo não foi justificado ou introduzido. Definir primeiro cotas por
operação e propósito, sinais mínimos, recuperação, revisão de falsos bloqueios e decisão
de permitir/rejeitar em falha. Não bloquear conta inteira por IP compartilhado sem decisão.

## Sessões e recuperação — resultado consolidado

**Já satisfatório no recorte local:** geração aleatória de 32 bytes, hash SHA-256 de token
opaco (não de senha), Argon2id para senha, sete dias de inatividade com renovação, expiração
no limite exato, logout/revogação e flags dos cookies. Não se aceita ID de sessão do cliente
como sessão nova. Login cria token novo; não há requisito de rotação periódica durante a
mesma sessão nem revogação de todos os dispositivos no logout.

Confirmação tem 24h/uso único e bloqueio do token; recuperação separada tem 1h/uso único.
Troca bloqueia usuário, altera hash, marca links e apaga todas as sessões numa transação;
login usa o mesmo lock. Falhas desfazem a troca. Sessão anterior e senha antiga não são
aceitas após redefinição nos testes; ausência de confirmação continua impedindo avaliar.
Novo pedido não invalida link anterior quando o envio falha. Não há login automático.
Nenhum desses prazos foi alterado pela #266. SQLite prova regressão sequencial, não MVCC
ou concorrência de PostgreSQL. Não há painel de gerenciamento de múltiplas sessões no
contrato atual; isso não foi inventado como obrigação desta entrega.

## Política técnica de logs e erros

Esta seção define o comportamento técnico entregue; **a matriz operacional de acesso,
retenção e descarte permanece proposta para aprovação**, sem prazo universal.

| Ambiente/finalidade | Conteúdo permitido pela implementação e orientação | Acesso, retenção e descarte |
|---|---|---|
| Local sintético | Eventos de erro, método/status e template de rota; console de e-mail com DEBUG=True é exceção explícita do ADR03/RF24 | Desenvolvedor local; não encaminhar links a coletores ou evidência versionada. Descartar artefatos sintéticos ao encerrar a finalidade de teste, conforme procedimento local. |
| Testes/CI | Dados fictícios, resultados agregados, eventos sanitizados. Usar adaptadores falsos; não habilitar console com conta real | Acesso dos mantenedores conforme configuração real do CI; retenção de artefatos não inspecionada. Não supor que mascaramento de secrets higieniza corpos/URLs. |
| API/worker em produção | UTC, nível, componente, evento; respostas HTTP com método/template/status; classe de exceção sem mensagem/stack/argumentos; bibliotecas com detalhes omitidos | Operadores autorizados a confirmar na #260/#267; log não concede identidade de avaliador. Prazo, exportação, revisão de acesso e exclusão dependem de inventário/decisão e recursos do provedor. |
| Auditoria funcional | Banco mantém versões/denúncias/decisões/eventos conforme requisitos específicos; não duplicar conteúdo em stdout | Sete dias de decisões/moderação não são prazo dos logs operacionais. Canal continua condicionado à #262. Backups também precisam de revisão. |

`FormatoSeguro` trabalha por conteúdo permitido, e não por remoção de algumas palavras
em texto livre. Aplicado aos handlers existentes após configuração do servidor e Alembic;
worker também o instala. Não formata input, args ou traceback brutos. Access log do
Uvicorn preserva status; o evento `app.http` preserva método/template/status sem IDs ou
query. Eventos conhecidos incluem falha interna, falha de recuperação e falha de descarte.
Classe do erro, hora/componente/status permitem diagnóstico inicial sem copiar payload.
Mensagens desconhecidas de bibliotecas são substituídas, preservando nível/componente.
Novos eventos devem ter conteúdo estruturado revisado e testes de não exposição.

Handler 422 não devolve `input`, contexto, mensagem do validador ou chave arbitrária;
500 é genérico/no-store. Erros de domínio conhecidos preservam status e suas mensagens
fixas. Falhas de OpenAI já eram sanitizadas e mantêm revisão humana; Resend não devolve
corpo do provedor ao frontend. `hide_parameters=True` reduz detalhes de SQLAlchemy,
mas isoladamente não impede que um driver inclua valores na própria mensagem; por isso
há fronteira HTTP/formatter e tratamento de exceção do Alembic. Importador conserva
status, fase, tipo e contagens, sem texto da exceção inesperada. O worker continua
tentando a cada 60s no modo contínuo; falha isolada termina com código não zero.

Não foram apagados logs antigos, implementado arquivo permanente, coletados IPs novos
ou criado ID de correlação de pessoa. Não foi instalado Sentry/analytics/APM. Não houve
correspondência nas buscas direcionadas por integração de observabilidade no frontend.
Isso não prova ausência de ferramentas habilitadas nos painéis. Prints operacionais
de catálogo/progresso não são registros de senha; comandos administrativos fora das
fronteiras cobertas precisam de diagnóstico restrito se falharem antes da inicialização.
Não habilitar echo SQL, debug de cliente HTTP ou captura de corpo em produção.

Os filtros locais não controlam Vercel, Render, Neon, Resend, DNS ou coletores adicionais.
[Render](https://render.com/docs/logging) documenta logs de runtime e recursos de logs
HTTP com URL conforme plano; a conta Free histórica não comprova a configuração atual.
[Vercel](https://vercel.com/docs/logs) distingue logs de build e runtime. O primeiro acesso
frontend ao link ainda contém token na URL por contrato: provedor, histórico e observabilidade
precisam ser revisados; no-referrer não limpa registro já gravado. Não incluir URL inteira,
Cookie/Authorization, nome/e-mail, protocolo/chave ou texto em tickets/métricas.

## Configuração, segredos, permissões e fornecedores

`SECRET_KEY` e `DATABASE_URL` são obrigatórias via configuração externa. Cookies Secure
dependem de DEBUG=False; exemplos/Compose são locais e não receita de produção. URLs
públicas do frontend são destinadas ao catálogo/API, sem chave de servidor em NEXT_PUBLIC.
Dockerfiles usam usuário sem privilégios, cópias delimitadas e dockerignore de env/logs;
o backend não copia seus testes/venv/.env para a imagem. Imagens não foram reconstruídas
nesta sessão por indisponibilidade do daemon Docker. Não foram lidos valores de .env real,
variáveis de painéis ou dumps, nem executadas rotações.

[Verificação limitada do histórico](evidencias/issue-266/segredos-resultado.json): 2.296
blobs alcançáveis nas refs locais, nenhum grande omitido e zero correspondências para
padrões de chaves de provedores/GitHub/PEM. O script não imprime valores. Não é scanner
universal/entropia e não verifica commits inalcançáveis, outras contas/branches não
obtidas, credenciais em formatos desconhecidos ou artefatos publicados. O inventário de
arquivos rastreados encontrou exemplos, não .env real ou PEM/chave privada. Não foi
identificado indício de segredo real nesses padrões; não se declara ausência global.
Se houver indício posterior, registrar local/tipo sem valor e encaminhar rotação ao
operador e procedimento de incidentes, sem apagar evidência ou rotacionar automaticamente.

#170 comprova historicamente configuração da API com undb_api e conexão administrativa
separada para Alembic; #171 consolida publicação/HTTPS/CORS/cookies por observação e
confirmação do PO. Reutilizadas essas evidências, sem reabrir entregas ou afirmar auditoria
atual dos painéis. `MIGRATION_DATABASE_URL` tem fallback para DATABASE_URL; a credencial
administrativa permanece no mesmo serviço. Não é isolamento de segredo entre processos.
Grants históricos das 15 tabelas não comprovam privilégios das tabelas posteriores de
recuperação/canal/identidades. Conferir permissões efetivas sem conceder automaticamente
todas as tabelas futuras. Nenhum GRANT/migration foi aplicado ao ambiente compartilhado.

Destinos técnicos para #261: Render recebe tráfego/API e stdout, Neon persiste contas,
hashes, vínculos e textos; Vercel atende páginas/URLs de confirmação/recuperação; Resend
recebe destinatário e HTML contendo link; OpenAI recebe texto elegível/modelo sem IDs de
autoria como metadados. Restrição de dados pessoais do filtro não anonimiza todo texto.
[Resend](https://resend.com/docs/dashboard/emails/introduction) oferece painéis de e-mails
e logs de API; [OpenAI](https://developers.openai.com/api/docs/guides/your-data) documenta
controles por endpoint/conta. Não transportar promessa de store=false de Responses para
Moderations. Retenção/região/contratos/subprocessadores efetivos, transferências e acessos
dependem da #261 e responsáveis; nenhum prazo de fornecedor foi generalizado ao projeto.

## Dependências e lockfiles

O [anexo de dependências](dependencias-issue-266.md) contém inventário completo, comandos,
hashes, classificação por advisory, versões corrigidas e análise de condições. São 35
pacotes de runtime Python resolvidos localmente e 478 entradas do lock npm. PyPI não
retornou avisos conhecidos nesse snapshot; npm retornou 14 nós/16 advisories. Condições
de exploração não foram testadas. Atualização de Next/sharp e ferramentas deve ser
direcionada e validada; não houve audit fix ou novas dependências do produto. Produção
e binários nativos permanecem sem inventário verificado.

## Considerações jurídicas e decisões pendentes

**A análise técnica do Codex não substitui validação jurídica pelos responsáveis.** Não
atribui ao UnDb base legal, enquadramento empresarial/acadêmico ou dispensa de deveres.
Finalidades propostas para registros mínimos: diagnosticar indisponibilidade, identificar
falhas e acompanhar controles de segurança. Necessidade de cada dado e compatibilidade
com essas finalidades devem ser justificadas no inventário da #261; não coletar conteúdo
privado por conveniência de depuração.

Fontes oficiais consultadas em 16/11/2026, com limites de acesso:

- [LGPD no Planalto, texto compilado](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm): acesso retornou desafio/timeout. Foram consultados o [registro de alterações no Senado](https://legis.senado.leg.br/norma/27457334), [texto publicado](https://legis.senado.leg.br/norma/27457334/publicacao/27457731) e orientações ANPD; não se afirma leitura integral consolidada de toda alteração vigente. Finalidade/necessidade/segurança/prevenção (art. 6), término/conservação (15/16), registro (37) e medidas de segurança (46–49) são questões a conciliar com o texto vigente na revisão jurídica; não fixam nesta análise prazo genérico de logs.
- [ANPD — guia de segurança](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/guia-vf.pdf/@@display-file/file): referência para controle de acesso e medidas proporcionais. Uso do guia não comprova enquadramento do UnDb como agente de pequeno porte nem implanta suas recomendações.
- [ANPD — legítimo interesse](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes/copy_of_guia_legitimo_interesse.pdf/@@display-file/file): avaliar finalidade, necessidade, balanceamento/salvaguardas por caso; não adotar essa hipótese genericamente para texto livre/dados sensíveis. Base de segurança/antifraude depende de natureza do tratamento e validação, não do nome do log.
- [Marco Civil, compilação da Câmara disponível no Senado](https://legis.senado.leg.br/norma/584776/publicacao/34619030): art. 15 tem condições de enquadramento e hipóteses específicas de preservação; seis meses não são prazo universal de todo log do projeto. Distinguir registro de acesso, conexão, erro e auditoria funcional. Fins econômicos/pessoa jurídica e determinações específicas não foram verificados no contexto do UnDb.
- [Decreto 12.975/2026 no Senado](https://legis.senado.leg.br/norma/43306825/publicacao/43309287): há atualização regulamentar de guarda/segurança e deveres de provedores, inclusive referência à porta lógica quando necessária. Encaminhar enquadramento, vigência e eventuais efeitos sobre canal/moderação à revisão jurídica; não implementar coleta adicional ou alterar retenção automaticamente com base na leitura técnica.

| Questão pendente | Evidência / alternativas e riscos | Decisão necessária / destino |
|---|---|---|
| Bases, finalidades e responsáveis de logs/antifraude | Há dados de autenticação, texto e provedores; coletar mais pode aumentar exposição, coletar menos pode limitar investigação | Equipe definida na #260 e revisão jurídica na #261; sem designar pessoa como controlador/encarregado por inferência. |
| Matriz de retenção/acesso/descarte | Não há prazo aprovado geral de logs; sete dias de moderação não se aplicam automaticamente. Retenção indefinida aumenta risco; descarte sem avaliar guarda específica também | Conciliar #261/#262/#267, operador e validação jurídica; identificar categoria, justificativa, prazo/condição, cópias, permissões e prova de descarte. |
| Guarda de acesso e preservação específica | Enquadramento MCI/atualização de 2026 não validado; logs mínimos da aplicação não são arquivo de acesso jurídico | Revisão especializada; não declarar cumprimento, dispensa ou coletar IP/porta/histórico por suposição. |
| Novos limites e indisponibilidade | Em memória não cobre replicas; cota por origem pode atingir redes compartilhadas/titulares; indisponibilidade pode aceitar abuso ou negar atendimento legítimo | Responsáveis aprovam política e arquitetura compatível antes de efetivar cota/bloqueio; permanece na #266/épico até encaminhamento. |
| Destino da atualização de dependências | Há versões em intervalos afetados; condições variam e correções existem | PO confirma tarefa/responsável/validação; não encaminhar apenas para a próxima issue numérica. |

## Correções e arquivos

Código: `backend/app/core/origins.py`, `http_errors.py`, `safe_logging.py`, `auth.py`,
`database.py`, `app/main.py`, `routers/auth.py`, `services/email_service.py`,
`sigaa_import_service.py`, `importacao_agendada_service.py`, `commands/descartar_moderacao.py`
e `backend/alembic/env.py`. Nenhuma migration/schema, serviço ou dependência de produto
foi adicionado. Frontend: headers em `next.config.ts` e metadado de confirmação;
componentes de formulário e política de publicação não foram alterados.

Testes: novo `backend/tests/test_seguranca_266.py`; clientes HTTP sintéticos de avaliação,
comentários e integrações passaram a enviar origem legítima. Assertivas de importação
verificam categoria da falha e ausência da mensagem bruta. Console foi testado como
exceção local explícita. Novo `frontend/tests/seguranca-266-browser.mjs` cobre headers e
metadados. Documentação: fonte/derivado, exemplos, desenvolvimento, canal, relatório,
anexo/evidências e navegação MkDocs.

## Testes, resultados e limitações

Ambiente isolado com SQLite em memória/temporário; variáveis sintéticas explícitas,
provedores falsos ou mocks, sem banco compartilhado. Comandos Python executados com
`.venv/Scripts/python.exe`, dentro de backend quando indicado. Resultados observados;
não confundir verificação local com aceite ou deploy.

| Verificação executada | Resultado observado |
|---|---|
| Baseline: `python -m unittest tests.test_auth tests.test_recuperacao_senha tests.test_solicitacoes_titulares tests.test_triagem -q` | 56 testes aprovados antes das mudanças. |
| Reprodução anterior de validação e engine, sem imprimir marcadores | HTTP 422 refletiu input sintético; hide_parameters era False. |
| `python -m unittest tests.test_seguranca_266 -q` | 17 testes novos aprovados: origens, erros/logs, cookie, prazo exato, proxy e orçamento/reinício/estado separado, jornada login/sessão/logout. |
| Regressão selecionada de auth/recuperação/canal/avaliação/comentário/denúncia/moderação/IA/identidade/importação | Execução final: 211 testes, sem falha, um opcional pulado; 209 na execução intermediária. Comando completo no registro de verificações. |
| `python -m unittest discover -s tests -q` | Última execução: 334 testes, 2 falhas no corpus de ofensas e 2 erros de limpeza SQLite no Windows; 2 pulados. Suíte geral **não aprovada**. Esses achados já constam da #275 e não foram corrigidos fora do escopo; arquivos de filtro/corpus e teste de conexão não foram modificados. |
| `python -m ruff check .`; `python -m ruff format --check .`; `python -m compileall -q app alembic` | Aprovados na verificação de código; repetir após qualquer ajuste posterior. |
| `npm ci --ignore-scripts --no-audit --no-fund`; `npm test`; `npm run lint`; `npm run typecheck` | Lock instalado sem alteração; 83 testes aprovados, lint e tipos aprovados antes da adição do teste de headers. |
| `npm run build -- --webpack` | Primeira tentativa bloqueada ao baixar fontes; repetida com rede autorizada, build/TypeScript/geração de páginas aprovados. Comando padrão do projeto preservado. |
| `node tests/seguranca-266-browser.mjs`; `node tests/recuperacao-senha-browser.mjs` | Execução inicial bloqueada por timeout CDP; repetida com permissão adequada em perfil temporário. Headers/metadados das duas páginas e 18 combinações de recuperação aprovados. API fictícia; nenhum token real. |
| `python -m mkdocs build --strict --site-dir site`; `git diff --check` | Aprovados. Páginas históricas fora do nav foram informadas pelo MkDocs como INFO; não houve warning impeditivo. |
| `python -m pip_audit ...`; `npm audit --package-lock-only --ignore-scripts --json` | Resultados e limites no anexo; ausência de advisory Python não é certificação. |
| `verificar_segredos.py` | 2.296 blobs, zero correspondências nos padrões limitados, sem imprimir valores. |

Não executados: carga, força bruta, chamadas reais de e-mail/IA, testes em produção,
PostgreSQL concorrente, concessão de permissões, migração em banco compartilhado ou
restauração. Docker instalado sem daemon disponível; não há ambiente PostgreSQL
descartável operacional nesta sessão. O novo teste de proxy é sintético, não configuração
do Render. A venv usou Python 3.14.7; validar CI Python 3.12 antes de promoção. Warning de
depreciação Starlette/httpx foi registrado, sem adicionar httpx2 para silenciá-lo.

Comandos, versões e resultados agregados estão em
[verificacoes.json](evidencias/issue-266/verificacoes.json). A revisão do diff seguiu a
skill canônica code-review; é autoinspeção do autor, não aprovação humana independente.
Foi corrigida durante a revisão a rejeição indevida de Referer com query percent-encoded;
teste cobre esse caso sem registrar query. O formatter conserva eventos úteis e classe
da falha, sem voltar a formatar mensagens brutas para facilitar diagnóstico.

## Riscos remanescentes, próximos passos e rastreabilidade

| ID / origem | Entrega/insumo da #266 | O que falta / gatilho | Destino e situação |
|---|---|---|---|
| PEND-263-ABUSO / #263/#275 | Revisão local de autorização, chaves, logs/validação e limitações do orçamento | Homologar proxy, identidade, instâncias/borda, proporcionalidade e correção compartilhada autorizada | #266 fornece análise à #263/#272; **parcial, não resolvida**. Nicolas acompanha origem. |
| Integração #266 → #261/#262 | Inventário técnico de sessões, logs, dados de provedores e exceção local | Validar bases, agentes, dados necessários, retenção/cópias/descarte; retomar relatório/canal | Destinos existentes; responsáveis/decisão específica conforme PO. |
| Integração #266 → #265 | Erros sem input, auth no-store, templates sem IDs e avisos de cache/dependências | Revisar demais caches privados, nome/e-mail de RF22 e minimização de contratos por ator | Insumo entregue localmente; não declarar a #265 executada. |
| Integração #266 → #267 | Eventos mínimos, classes de erro e limites do diagnóstico; registros antigos não apagados | Aprovar canal privado, acesso/retenção/preservação, exercício e recuperação isolada | Retomar junto de PEND-263-ESC/OPS; sem novo responsável inventado. |
| Integração #266 → #268/#269 | Descrição real de sessão/fornecedores/abuso/logs | Textos jurídicos devem refletir controles publicados e práticas confirmadas; sem promessa de segurança integral/banimento | Conferência de publicação/revisão, não bloqueio para redação. |
| Integração #266 → #271 | Limites de identidade/segurança; nenhuma alteração de fórmulas | Revisar promessas de anonimato/antifraude e conciliar termos publicados | Branch remota de metodologia existe, mas não integrada na base auditada. Não modificar fórmulas ou atribuir aceite. |
| F266-07 / #266 | Inventário e 16 advisories com condições/correções | Atualização dirigida, binários/produção e regressões | Aguardando encaminhamento e responsável validados pelo PO no épico. |

O registro do épico e checklists das issues devem distinguir implementação local,
integração e homologação. Não encerrar pendência por recomendação ou comentário. Não
foram alteradas PEND-263-RET/INV/ESC/OPS, a #260 já fechada documentalmente ou flags de
recebimento. Critérios ainda pendentes: limites aprovados/distribuição, infraestrutura,
retenção/base jurídica, atualização dirigida de dependências e aceite das regressões
gerais. A #266 **não está integralmente concluída**.

### Registros publicados no acompanhamento

Em 16/11/2026, foram publicados e relidos os comentários abaixo, sem fechar issues,
marcar critérios incompletos ou modificar o registro histórico de outro integrante.
O novo registro do épico complementa a tabela anterior; os checklists permanecem nas
issues de destino. Os IDs PEND-266 organizam esses insumos, sem inventar estado de skill,
aceite jurídico, responsável ou tarefa de atualização de dependências.

| Issue | Referência | Verificação |
|---|---|---|
| #272 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/272#issuecomment-6906902341) | Conferido após publicação |
| #266 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/266#issuecomment-6906911556) | Conferido após publicação |
| #263 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/263#issuecomment-6906912447) | Conferido após publicação |
| #261 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/261#issuecomment-6906923249) | Conferido após publicação |
| #262 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/262#issuecomment-6906924124) | Conferido após publicação |
| #265 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/265#issuecomment-6906924932) | Conferido após publicação |
| #267 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/267#issuecomment-6906925839) | Conferido após publicação |
| #268 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/268#issuecomment-6906926619) | Conferido após publicação |
| #269 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/269#issuecomment-6906927471) | Conferido após publicação |
| #271 | [Comentário e checklist](https://github.com/unb-mds/2026-02-UnDb/issues/271#issuecomment-6906928253) | Conferido após publicação |

Implementação no commit local `5e5ab50bb8d2e1dca4852a962869a7e799f5ff9b`; documentação e
evidências em commit separado. Nenhum push/PR/merge/deploy foi realizado. Os comentários
explicitam que os arquivos/commit ainda não estão disponíveis no remoto; publicação
depende de autorização. A develop remota foi reconferida e permaneceu em `d99916e`.

## Continuidade da implementação — 16/11/2026

### Diagnóstico antes das correções desta retomada

Branch `fix/266-sessoes-abuso-logs`, inicialmente limpa em `dbde820`. Os commits
`5e5ab50` e `dbde820` existem e são ancestrais do HEAD; continuam locais. O fetch
encontrou `origin/develop@757b12cdeaa7d6c061cb40181e346a0bb32063f4`, 31 commits
após a base `d99916e`. Nenhuma branch remota da #266 foi localizada. O trabalho de
outras worktrees e os arquivos locais da #251 foram preservados. O usuário autorizou
expressamente integrar essa develop por merge **apenas local**, preservando ambos os
commits. Não há autorização de push, PR, merge remoto ou deploy.

Foram relidas #266/#272 e os comentários de #261/#262/#263/#265/#267/#268/#269/#271,
além de #275/#277 e seus artefatos. A PR #277 está integrada em `757b12c`: a correção
`8ca99fb`, antes referida pelo head `c69e660`, amplia o middleware de cache privado.
O inventário T01–T18 e a matriz J1–J9/C01–C36 são insumos técnicos/documentais,
sem homologar operação ou validar juridicamente os tratamentos. A #271 está fechada
editorialmente; os acompanhamentos externos continuam nas issues de destino.

| Item recebido | Classificação inicial e evidência | Encaminhamento autorizado |
|---|---|---|
| Sessões, CSRF e sanitização da #266 | Implementados e testados localmente; falta conciliar base e homologar | Preservar comportamento já aprovado e repetir regressões |
| CACHE-277-01 / #265 | Implementado na develop; conflito textual apenas em `app/main.py` | Conciliar um único middleware com o evento HTTP seguro; reutilizar a regressão da #277 |
| PEND-263-ABUSO | Parcial: limite compartilhado entre criar/consultar/complementar, por cliente/processo | Retestar proteções e exposição; não ativar canal, novo limite ou infraestrutura |
| Suíte geral anterior | Reproduzida: 334 testes, duas falhas de corpus e dois erros de cleanup, dois skips | Investigar causa antes de alterar código ou testes |
| Moderação no Windows | Confirmado: sem `PYTHONUTF8`, encoding padrão cp1252; os 13 testes de disfarces passam com `PYTHONUTF8=1` | Corrigir leitura de dados UTF-8, preservando lista, categorias, limiares e publicação |
| Cleanup SQLite | Confirmado: `with sqlite3.connect()` encerra transação, não conexão; arquivo segue aberto | Fechar explicitamente o recurso do teste, sem skip nem supressão de erro |
| Dependências | Inventário anterior disponível; nenhum manifest alterado pela develop recebida | Reconsultar advisories; atualização dirigida ainda depende de destino/responsável pelo PO |
| PostgreSQL / Python 3.12 | Não homologados na entrega anterior; Docker sem daemon nesta retomada | Procurar ambiente descartável local, sem banco compartilhado |
| Proxy, CDN, logs e disponibilidade reais | Dependentes de infraestrutura, com Nicolas conforme orientação de Gabriel na #277 | Preparar roteiro de evidências sanitizadas; sem afirmar proteção da borda |
| Limites e falha do mecanismo | Dependentes de aprovação humana | Manter recomendação e riscos rastreáveis no épico |
| Bases, retenção, acesso, descarte e backups | Dependentes de validação jurídica e fatos operacionais | Conciliar #261/#262/#267; nenhum prazo ou base legal novo |

As duas famílias de arquivos associadas às quatro falhas não foram alteradas pelos
commits originais da #266 nem pela develop posterior. Portanto são problemas
preexistentes, reproduzidos nesta base; os resultados finais e seus limites serão
registrados abaixo. A análise técnica do Codex não substitui validação jurídica.

### Conciliação da PR #277

**Implementado e testado.** Merge local `3a1d46d`, com pais `dbde820` e `757b12c`:
preserva os dois commits originais. O único conflito foi em `backend/app/main.py`.
Conservou-se `proteger_cache_privado` e seu limite de segmento, exatamente com as
famílias de rotas de `8ca99fb`, acrescido do evento sanitizado `http.resposta` da #266.
Não há segundo middleware concorrente. A navegação MkDocs, `specs.md` e alterações
editoriais da develop foram conciliadas automaticamente, preservando a restrição de
origens já aprovada. Nenhum contrato, campo ou permissão foi alterado nessa integração.

Reutilizada a regressão de cache da #277, cobrindo sucesso e erros 401/403/404/422.
Adicionadas verificações em todas as famílias privadas para erro de rota e rejeição
de origem, fronteiras de prefixo público e preservação de Set-Cookie, CORS, Vary e
cabeçalhos de respostas públicas. O handler 500 da #266 conserva ambos os cabeçalhos,
mesmo quando a exceção ocorre fora do retorno normal do middleware. Catálogo e saúde
continuam sem `no-store` forçado por esse mecanismo. Validações 422 têm sua proteção
própria; isso não autoriza remover os cabeçalhos definidos por endpoints.

### PEND-263-ABUSO: resultado e limite da correção

**Parcialmente resolvida; dependente de infraestrutura e aprovação humana.** Foram
preservados hash da chave, credencial somente no corpo, controle por sessão confirmada
e allowlists separadas, separação de histórico público/interno e ativação desligada.
Criar, consultar e complementar compartilham o mesmo contador. Atendimento é protegido
por autorização, mas não tem orçamento HTTP específico; não foi criado um valor novo.

`limitar()` usa `request.client.host` após o middleware do servidor; não interpreta
diretamente X-Forwarded-For. Armazena HMAC do endereço com SECRET_KEY, janela monotônica
de 60s, configuração existente `CANAL_TITULARES_LIMITE_MINUTO` (default 30) e teto de
4.096 clientes por processo. O parâmetro temporário entregue na #263 **não** é aceite
de uma política geral de bloqueio. O lock coordena threads do mesmo processo apenas.

Evidências sintéticas, sem tráfego público: cabeçalho enviado por peer não confiável
não muda a identidade no Uvicorn; peer configurado como confiável permite reescrita.
Contador reiniciado ou estado de outra instância concede orçamento novo. Ao lotar a
capacidade global, cliente novo recebe 429 mesmo sem atingir sua cota; um existente
ainda abaixo do limite continua e os slots expiram pelo relógio controlado. Isso
confirma risco de falso positivo em rede compartilhada ou capacidade global, sem
demonstrar ocorrência no serviço hospedado. A resposta conserva Retry-After e não
expõe IP/chave. Falha sintética do relógio não é convertida em orçamento livre; não
simula indisponibilidade de um armazenamento compartilhado ainda inexistente.

O teste HTTP adicional verifica que consulta/atendimento não põem protocolo, chave
ou corpo nos eventos formatados; erros de contrato continuam genéricos e as rotas
de atendimento preservam o template. Os testes existentes conferem leitor sem poder
de resposta, atendente confirmado, chave incorreta, complementos e histórico privado.
Nenhuma correção adicional no contador foi suficientemente definida/autorizada.

Recomendação para decisão: comparar um controle compartilhado com a infraestrutura
PostgreSQL já aprovada e um controle de borda do provedor, antes de escolher tecnologia.
Avaliar atomicidade/janelas, retenção de identificadores mínimos, custo de consulta,
concorrência e indisponibilidade. Redis não foi introduzido. Definir separadamente
abertura, consulta, complemento e operação interna, considerando redes compartilhadas,
recuperação de acesso e alternativa de atendimento. Falha que permite requisições
mantém acesso legítimo, mas perde proteção; falha que nega pode impedir direitos.
O PO/responsáveis devem aprovar limites, modo de falha e arquitetura; nem a proposta
nem este teste encerram PEND-263-ABUSO.

### Diagnóstico das quatro falhas anteriores

**Implementado e testado.** Antes das mudanças desta retomada, reproduzidos 334 testes
com as duas falhas lexicais e os dois erros de cleanup descritos na entrega parcial.
Os arquivos envolvidos são idênticos entre `d99916e`, os commits originais e a nova
develop. A execução antiga de `tests.test_ofensas_disfarcadas` com `PYTHONUTF8=1`
passou todos os 13 testes, enquanto o padrão local cp1252 reproduziu as duas falhas.
O JSON UTF-8 era lido pela codificação implícita, corrompendo termo acentuado.
Correção: `read_text(encoding="utf-8")` na lista e na fixture do comando de avaliação.
Lista, corpus, categorias, flags, limiares e política de publicação não mudaram.
Resultado reaproveitável por #239/#252: correção de portabilidade, sem novo sinal.

Nos testes de conexão de migração, `with sqlite3.connect()` gerencia transação e não
fecha o recurso: ver [documentação Python](https://docs.python.org/3.12/library/sqlite3.html#how-to-use-the-connection-context-manager).
O Windows recusava excluir o arquivo ainda aberto. `contextlib.closing` encerra a
conexão antes do cleanup. Nenhum skip, espera arbitrária ou supressão foi adicionado.

Também foi corrigido o adaptador HTTP de `integration_avaliacao`: ele enviava origem
3000 enquanto o próprio ensaio inicia API/frontend com origem 3100. O cliente agora
envia a origem legítima do ensaio; o controle CSRF não foi flexibilizado.

### Homologação local e regressões

**Implementado e testado localmente; CI desta branch e produção não homologados.**
Python 3.12.16 foi obtido pelo uv em diretório isolado, sem registro do Windows/PATH;
o projeto não passou a depender de uv. O Docker continua sem daemon disponível.
Foi usado o arquivo portátil oficial PostgreSQL 16.16-1 para Windows, referenciado
pelo [PostgreSQL](https://www.postgresql.org/download/windows/) e fornecido pela
[EDB](https://www.enterprisedb.com/download-postgresql-binaries), sem instalar serviço.
O cluster escutou somente em 127.0.0.1:55466, com senha sintética aleatória não exibida.

O [ensaio reproduzível](evidencias/issue-266/homologar_postgres.py) cria somente bancos
e roles reservados que ainda não existam, recusa reutilização e remove o que criou.
Separa owner de migração e papel da aplicação, ambos sem superuser/createdb/createrole;
o papel de aplicação recebe DML nas tabelas funcionais e USAGE no schema, sem CREATE
ou DML na tabela do Alembic. Cadastro/confirmação/login/recuperação/logout foram
exercitados contra esse DB, substituindo apenas o envio externo de e-mail. Inclui
cookies seguros, CSRF, uso único, revogação das sessões e dos outros links **após a
troca de senha**, conforme RF24. A solicitação de um segundo link não revoga o primeiro.
Esses grants são evidência de compatibilidade em teste, não receita aplicada no Neon.

O ciclo executou upgrade/check/downgrade base/upgrade e o fluxo de dados legados do CI,
com verificação de upgrade/downgrade e schema. A suíte completa foi executada com o
banco `undb_207_test` exclusivo para os testes de contenção real. Não houve migration
nova. Evidências agregadas, comandos, versões e limitações ficam em
[continuidade/README.md](evidencias/issue-266/continuidade/README.md).

| Comando/ambiente desta retomada | Resultado final observado |
|---|---|
| `python -m unittest discover -s tests -q`, Python 3.14.7/Windows | 341 testes sem falhas, dois skips opcionais PostgreSQL |
| `python -m coverage run --branch --source=app -m unittest discover -s tests -q`, Python 3.12.16/PostgreSQL 16.16 | 341 testes aprovados, **zero skips**, 87% de cobertura agregada |
| Segurança #266 + regressão de cache #277 + canal | 30 testes aprovados, incluindo 22 da #266; 500 genérico também confere no-store/no-referrer |
| Script de homologação local | 13 etapas de migrações/legado, jornada HTTP segura e integrações HTTP de avaliação/moderação aprovadas; recursos criados removidos, cluster encerrado |
| `ruff check`, `ruff format --check`, `compileall` | Aprovados; 160 arquivos backend formatados |
| `npm test`, `npm run lint`, `npm run typecheck`, `npm run build -- --webpack` | 83 testes e demais verificações aprovados |
| `node tests/seguranca-266-browser.mjs`, `node tests/recuperacao-senha-browser.mjs` | Headers/metadados e 18 combinações RF24 aprovados em API fictícia |
| `python -m mkdocs build --strict --site-dir site` | Aprovado, sem warning impeditivo; navegação conciliada com #276/#277 |
| Busca limitada de segredos | 2.384 blobs, zero correspondências; resultado histórico preservado e nova evidência separada |

Não foi possível executar o CI remoto desta branch sem publicação autorizada. O CI
aprovado da PR #277 é histórico da sua própria versão, não valida os commits da #266.
Também não foram executados testes de TLS/permissões/observabilidade no Neon ou nos
provedores publicados, nem restauração de backup. As limitações de infraestrutura
e validação humana/jurídica abaixo permanecem mesmo após a homologação local.

### Homologação operacional pendente com Nicolas

**Dependente de infraestrutura.** Conforme [orientação registrada na #277](https://github.com/unb-mds/2026-02-UnDb/pull/277#issuecomment-6917996624),
Nicolas confirma fatos operacionais; a execução local não encerra estas verificações:

| Conferência segura pelo responsável | Evidência sanitizada esperada | Risco se divergir |
|---|---|---|
| Caminho navegador → frontend → API, TLS, cookie e CORS | Diagrama/configuração sem valores de segredo; apenas atributos HttpOnly/Secure/SameSite e origem autorizada; não copiar Cookie/Set-Cookie completo | Sessão legítima indisponível ou confiança incorreta entre origens/sites |
| Peer/proxy e interpretação de headers encaminhados | Comando efetivo e configuração de hosts confiáveis, documentação atual do provedor e teste em staging controlado com endereços sintéticos | Agrupar clientes indevidamente ou aceitar identidade encaminhada não confiável; não habilitar `*` por conveniência |
| Número de workers/réplicas e reinícios | Quantidades, versão implantada e confirmação de que orçamento é por processo | Orçamento aparente divergente; não prometer cota distribuída |
| Cache privado na borda | Com conta de teste autorizada, uma consulta legítima e um erro tratado por família: status + somente Cache-Control:no-store e Referrer-Policy:no-referrer; conferir ausência de reaproveitamento entre duas contas de teste | Conteúdo privado persistido/compartilhado; cache local correto não prova CDN |
| Logs de API/worker/proxy/CDN/build/monitoramento | Lista de fontes, campos habilitados, planos, acesso/exportação, retenção/descarte e amostra somente sintética já sanitizada | URL/token ou corpo registrado fora do formatter, acesso excessivo ou guarda indefinida |
| DB e migração | Privilégios efetivos/roles sem identificadores de conexão ou senhas; TLS e conexões API/migração separadas conforme #170 | Permissão indevida ou migração executada pelo papel da aplicação |
| Canal de titulares | Disponibilidade, allowlists efetivas por papel sem publicar UUIDs, titular/substituto/capacidade de urgência e condição de ativação | Atendimento indisponível ou acesso indevido; flag permanece desligada |

Usar staging e contas sintéticas autorizadas, sem teste de carga, cabeçalhos falsificados
no serviço público ou divulgação de painéis/URLs com dados pessoais. Os registros
operacionais devem referenciar versão/ambiente/data, sem prometer retenção antes da
decisão pertinente. Se o responsável não puder verificar algum ponto, mantê-lo aberto.

### Situação das decisões e consumidores

| Item | Classificação nesta retomada | Destino/resultado |
|---|---|---|
| CACHE-277-01 | Implementado e testado localmente | #265 (Yasmin, conforme A8), #266 e épico recebem evidência da conciliação; não repetir a correção |
| Encoding/cleanup e regressões | Implementado e testado | Corrigidos nesta #266; #252 recebe a evidência de portabilidade; nenhuma política de moderação nova |
| PostgreSQL e Python 3.12 | Implementado e testado em ambiente descartável Windows | CI Linux desta branch depende de publicação autorizada; nenhum run novo foi disparado |
| PEND-263-ABUSO | Recomendado, aguardando aprovação + dependente de infraestrutura | #263/#266/#272 continuam abertos no acompanhamento, sem declarar orçamento distribuído |
| Atualização dirigida de dependências | Recomendado, aguardando aprovação de destino/responsável | Anexo atualizado: 17 advisories npm; Next candidato 16.4.5; nenhuma versão alterada |
| Logs/CDN/proxy/Neon e ativação real | Dependente de infraestrutura | Nicolas conforme orientação de Gabriel; roteiro acima, sem deploy ou ativação |
| Bases, retenção, acessos, descarte/backups e preservação | Dependente de validação jurídica | #261/#262/#267 devem conciliar inventário T01–T18, #266 e J1–J9/C01–C36; nenhum prazo geral aprovado |
| Minimização e textos públicos | Insumo técnico; sem necessidade de alteração adicional nesta #266 | #265 e #268/#269 (Gabriel confirmado em A8) consomem cache/logs/fornecedores; retomar Home/Sobre da #271 somente quando suas definições mudarem |

Nenhuma recomendação foi marcada como resolução de implementação, nenhum responsável
novo foi designado. A revisão não encontrou autorização adicional para limites,
falha do mecanismo, retenção ou atualização de dependências. A integração e validação
em produção permanecem distintas da implementação local. A #266 não está integralmente
concluída enquanto esses critérios relevantes permanecerem sem decisão/evidência.

### Registros desta continuidade e situação final

Comentários publicados e relidos integralmente; conteúdo conferido após gravação:

| Registro | Resultado rastreável |
|---|---|
| [Épico #272](https://github.com/unb-mds/2026-02-UnDb/issues/272#issuecomment-6930694269) | Matriz e checklist da retomada; sete linhas reais acrescentadas à tabela de integração do corpo do épico, preservando modelo e demais registros; leitura posterior conferida |
| [#266](https://github.com/unb-mds/2026-02-UnDb/issues/266#issuecomment-6930716693) | Integração #277, correções, homologação local, advisories e critérios ainda abertos |
| [#263](https://github.com/unb-mds/2026-02-UnDb/issues/263#issuecomment-6930718232) | PEND-263-ABUSO retomada, parcial e aberta; sem ativação/política nova |
| [#265](https://github.com/unb-mds/2026-02-UnDb/issues/265#issuecomment-6930719998) | CACHE-277-01 conciliado; checklist para integração e homologação operacional |
| [#252](https://github.com/unb-mds/2026-02-UnDb/issues/252#issuecomment-6930721909) | Causa de encoding/cleanup e correção local; qualidade/ativação continuam pendentes |

Os checklists já recebidos por #261/#262/#267/#268/#269/#271 foram preservados;
nenhum novo requisito, prazo ou responsável foi inserido nessas entregas. O registro
central e a tabela do épico vinculam seus checklists anteriores e os consumidores.
A #271 permanece fechada editorialmente; não foi reaberta por uma limitação operacional.

Commits locais desta retomada: `3a1d46d` (conciliação com a develop, preservando os
originais) e `9a186d2` (correções e regressões). Documentação/evidências em commit final
separado, identificável no histórico da mesma branch. A autoinspeção de review conferiu
o diff, preservação de controles, escopo, ausência de nova política e rastreabilidade;
não substitui revisão humana independente. Não houve push, PR, merge remoto ou deploy.

**Situação da #266: bloqueada por decisões humanas, jurídicas ou de infraestrutura
para seu aceite integral.** O trabalho técnico atualmente autorizado foi implementado
e testado localmente. Permanecem a decisão de limites/controle compartilhado/falha,
o encaminhamento da atualização de dependências, as evidências operacionais com Nicolas,
a validação jurídica e o CI/integração pelo fluxo de publicação autorizado. Não há
falha geral reproduzida remanescente nesta base, mas isso não certifica segurança
integral nem conformidade à LGPD. As fontes jurídicas e suas limitações do relatório
anterior foram preservadas; nenhuma obrigação ou prazo novo foi inferido nesta retomada.
