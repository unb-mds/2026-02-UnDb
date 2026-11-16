# Verificação das pendências — PR #277

Data: 16/11/2026 (America/Sao_Paulo). Base: `794be68`; correção técnica em `8ca99fb`.
Origem: Gabriel solicitou resolver as pendências e, depois, informou que Nicolas é
responsável pelos fatos operacionais, orientando deixá-los pendentes e avançar nas
demais partes. [Perguntas a Nicolas, com menção na PR](https://github.com/unb-mds/2026-02-UnDb/pull/277#issuecomment-6917996624).

Escopo realizado: inventário técnico, matriz de acesso, análise documental dos 36
casos, inspeção visual dos dois ativos de marca, testes sintéticos e correção de cache.
Não houve participação de responsáveis em exercício de mesa, dado real, ativação,
alteração de requisito, aprovação de política, conclusão jurídica profissional ou merge.

## 1. Resultado e limites por pendência

| ID | Trabalho concluído neste pacote | O que continua pendente |
|---|---|---|
| J1 | Conferidos os aceites operacionais e a decisão conjunta já registrada na #260 | Qualificação jurídica, representação e contato público: Nicolas; análise pertinente antes das políticas |
| J2 | Canal exercitado sinteticamente: protocolo/chave, permissões, resposta/complemento e indisponibilidade | Disponibilidade, acesso real e capacidade de urgência em produção: Nicolas |
| J3 | Regras de revisão existentes confrontadas com código/testes; roteiro abaixo sem novos prazos ou sanções | Política/revisão/escalonamento completos de #264 e enquadramento jurídico dos casos especiais; capacidade real depende de Nicolas |
| J4 | [Inventário técnico T01–T18](inventario-tecnico-pr277.md), acessos, destinos e diferenças de retenção documentados | Inventário aprovado, bases, contratos, países e transferências; Nicolas confirma fatos dos fornecedores |
| J5 | Matriz abaixo, testes de autorização/privacidade e risco de inferência documentados; CACHE-277-01 corrigido | Necessidade jurídica dos campos aprovados, configurações reais de CDN/logs e eventuais mudanças de produto dependem de validação |
| J6 | Separados validade, retirada, descarte e backups; testes de descarte vigente conferidos | Retenção geral, preservação e exclusão/restauração integrais de #262/#267, com operação confirmada por Nicolas |
| J7 | Confirmado que cadastro não registra idade e que domínio não prova maioridade; cenários C32/C33 analisados | Público real, melhor interesse e medidas/requisitos proporcionais aprovados; não inventar coleta documental ou bloqueio de menores |
| J8 | Insumos técnicos para Política/Termos organizados; ausência de rotas/registro de ciência confirmada | Publicação e registro/transição de versões dependem dos fatos e decisões pendentes; adiado conforme orientação de Gabriel |
| J9 | Logo e prévia local inspecionados, com nome próprio UnDb; páginas/metadados conferidos | Origem/licenciamento dos ativos, pesquisa marcária e eventual autorização necessária não comprovados; não declarar regularidade jurídica por inspeção visual |

Isso resolve a correção comprovada e a conferência técnica descrita. Não equivale a
encerrar as nove pendências jurídicas/operacionais: as partes indicadas continuam
rastreáveis. Não se exige encerrar todas as issues para um ajuste editorial independente.

## 2. Matriz de rotas, atores e dados

| Superfície | Ator / autorização | Dados que pode receber | Limite verificado |
|---|---|---|---|
| `/api/professores`, `/api/disciplinas` e ofertas | Visitante | Catálogo, UUIDs institucionais, nome/unidade, SIAPE no detalhe/listagem e vínculos de turma | São dados de docentes, não a identidade da conta avaliadora; necessidade de SIAPE público ainda a validar |
| Agregado por professor–disciplina / comparação | Visitante | Contagem e contexto; critérios somente a partir de três | Não retorna a linha individual da avaliação nem `usuario_id`; três não garante anonimato |
| Comentários publicados por professor–disciplina | Visitante | ID da versão, texto e criação | Não retorna nome/e-mail/UUID da conta, estado interno ou `avaliacao_id`; texto/data podem identificar indiretamente |
| `/api/avaliacoes` | Conta confirmada | Registro da própria contribuição, critérios e estado/erro do comentário | Conta é obtida da sessão, não escolhida pelo payload; unicidade e substituição preservadas |
| `/api/comentarios/meu` e retirada | Autor confirmado | Seus textos/estados e vínculos de versões | Outro autor não pode retirar; consulta é restrita ao usuário autenticado |
| Registro de denúncia | Visitante ou conta | Confirmação simples | Não divulga outros denunciantes; visitante não conta para 50 contas distintas |
| Moderação de texto/denúncias/decisões | Moderador confirmado | Conteúdo, motivos, atores internos e nome/e-mail conforme RF22 | Não acessível a visitante/conta comum; autoria e denúncia própria impedem decisão. Nome/e-mail aprovado internamente não é autorização de divulgação externa |
| `/api/agradecimentos` | Usuário autenticado | Mensagens destinadas à própria conta | Confirmação de exibição é por objeto/usuário; não é lista pública de denúncias |
| `/api/moderacao/identidades` | Reconciliador confirmado | Candidatos, origem, decisão, justificativa e autor interno | Papel não decorre da permissão de moderador; sem fusão automática por homônimo |
| Consulta/complemento de solicitação | Portador de protocolo e chave | Dados do próprio pedido; RESPOSTA e COMPLEMENTO | Não mostra TRIAGEM/PROVIDENCIA nem responsável interno; chave incorreta/protocolo alheio não abre pedido |
| `/api/atendimento` | Allowlist de leitores/atendentes confirmados | Fila e histórico interno | Leitor não responde; moderador/reconciliador não recebe esse acesso por seu papel; campos não podem ser copiados para respostas públicas |

**Cache:** frontend já pede `no-store` nas consultas privadas inspecionadas. React cache
em `consultas-publicas.ts` é usado para consultas públicas, por renderização. Isso não
substitui cabeçalhos do servidor nem comprova configuração de CDN. Em `8ca99fb`, o
middleware passa a aplicar `Cache-Control: no-store` e `Referrer-Policy: no-referrer`
às famílias privadas, inclusive respostas tratadas de autenticação, autorização,
validação e objeto inexistente. Catálogo e `/health` não recebem essa política por esse
middleware. Não foi feito teste hospedado de duas contas/cache/CDN ou erro interno 500.

## 3. Finding confirmado e correção

**CACHE-277-01 — respostas privadas sem instrução de não armazenamento.** A revisão
ampliada encontrou o middleware restrito a solicitações/atendimento, enquanto respostas
de sessão, comentários do autor e moderação com identidades não tinham a mesma proteção
no servidor. Isso deixava armazenamento de respostas privadas sem a restrição explícita
esperada na revisão de cache da #265. Não foi demonstrado vazamento entre usuários ou
exposição em produção. Não é defeito introduzido pelos cinco arquivos originais da PR.

Reprodução sintética antes da mudança: o novo teste HTTP de cache percorreu 13 cenários;
11 falharam pela ausência dos cabeçalhos esperados. Correção: ampliar o middleware já
existente às famílias privadas, com limite de segmento de rota. Nenhuma permissão,
campo, fórmula, limiar, prazo de retenção ou integração foi alterado.

Regressão em `tests.test_moderacao.ModeracaoTest.test_cache_privado_protege_sucesso_e_erros_sem_alterar_rota_publica`:
fila/detalhe/histórico autorizados, 401/403/404/422, sessão, comentários próprios,
agradecimentos, identidades, canal e atendimento. Confere também `/health` público sem
a política forçada. Após a mudança, aprovado; testes e Ruff aprovados conforme seção 6.

A #266 possui registro de trabalho antecipado sobre sessões/logs; sua implementação
não existe nesta base local e não foi presumida integrada. A correção estreita acima
deve ser conciliada ao integrar aquela entrega, sem duplicar ou regredir a proteção.

## 4. Roteiro apoiado em regras existentes

Este roteiro organiza RF20–RF22/RF25, sem aprovar política jurídica nova:

1. Receber denúncia ou solicitação pelo percurso disponível e autorizado. Um pedido
   fundamentado não precisa aguardar 50 denúncias. Não copiar dados reais ao GitHub.
2. Conferir alvo, contexto e necessidade de informações; classificar o encaminhamento
   como texto, catálogo, critérios numéricos, direitos ou possível incidente. Denúncia
   simples não comprova legitimidade de toda notificação jurídica.
3. Preservar crítica acadêmica; discordância/nota baixa não basta para remover.
   Verificar impedimentos e encaminhar a outro moderador quando necessário. Sem
   elegível, aplica-se a pendência prevista em RF22, sem inventar sanção alternativa.
4. Moderador confirmado usa somente transições permitidas e registra motivo. Atendimento
   não executa automaticamente alteração de nota, identidade ou conta. Apuração de
   fraude numérica segue a #270, separada da remoção de texto.
5. Atendimento registra triagem/providências internamente; resposta motivada e eventual
   pedido de revisão usam RESPOSTA/COMPLEMENTO. Não expor avaliadores, denunciantes ou
   material excessivo. Não afirmar que já existe notificação automática a ambas as partes.
6. Preservar descarte e estados vigentes. Caso exija urgência, preservação excepcional,
   comunicação a autoridade, exercício de direitos ou resposta com prazo legal, encaminhar
   aos responsáveis e à validação pertinente; capacidade e procedimento completos
   continuam pendentes. Não usar o prazo de sete dias para todas essas situações.

Não há nova política pública ou SLA neste pacote. Não se confunde organizar as regras
existentes com implementar todos os mecanismos exigidos por uma norma aplicável.

## 5. Conferência dos 36 casos

Foi feita **análise documental individual pelo agente**, confrontando cada cenário
com código, requisitos e as evidências indicadas. Isso não transforma os casos em 36
testes de software aprovados nem em exercício de mesa com aceite humano. A coluna de
continuação descreve a parte que permanece sem conclusão.

| Caso | Resultado da conferência | Continuação necessária |
|---|---|---|
| C01 | Logo UnDb e prévia inspecionados; texto A1 e metadados não declaram serviço oficial | Origem/licença e exame marcário não verificados, J9 |
| C02 | #260 documenta continuidade e decisão conjunta, sem comprovar acessos | Fatos e qualificação com Nicolas, J1/J8 |
| C03 | Schema de cadastro não recebe matrícula/histórico; confirmação prova o endereço | Apuração de fraude segue #270; não alegar experiência comprovada |
| C04 | Teste HTTP 0/1/2/3/4 confirma contagem/insuficiência e agregação | Operação hospedada não testada; preservar mínimo aprovado |
| C05 | Inferência temporal é possível: três notas 4 geram 4,0; com nota 1, média vira 3,3. Escala inteira restringe a dedução do novo valor | Avaliar risco, sem prometer anonimato ou mudar limiar por suposição, #265 |
| C06 | Schema público deixa texto/data visíveis sem nome da conta; isso não elimina identificação indireta | Avaliação contextual e eventual mudança aprovada, #264/#265 |
| C07 | Reconciliação tem regras/testes de homônimos, origem, colisão e rollback | Atualização real do SIGAA e necessidade dos campos, #261/#263 |
| C08 | Schema público não expõe autor; canal não executa entrega de identidade | Procedimento jurídico para pedido/ordem válido, J1/J2/J5 |
| C09 | Triagem tem regressão de crítica sem sinais; RF22 protege crítica e exige motivo | Não há classificador jurídico infalível; política completa #264 |
| C10 | Moderador exige motivo e decide segundo estado, mas código/IA não comprovam veracidade de acusação criminal | Análise contextual/jurídica de honra e notificação; não remover toda crítica nem validar acusação por ausência de sinal, J2/J3 |
| C11 | Texto livre pode conter dados de terceiros; filtro e contrato não autorizam publicação de todo dado sensível | Base e resposta própria por hipótese, J4/J5 |
| C12 | Canal tem categoria e encaminhamento manual; não há escalonamento automático de urgência comprovado | Operação com Nicolas e procedimentos #264/#267 |
| C13 | Não há upload no canal; links/textos continuam podendo carregar exposição íntima | Legitimidade, prazos e protocolo especializado, J2/J3/J6 |
| C14 | Nenhum material ilícito foi criado, baixado ou reproduzido | Protocolo especializado e comunicação/preservação cabíveis, #267 |
| C15 | Testes conferem visitante, unicidade por conta, limiar 50 e encerramento; pedido fundamentado é independente do limiar | Capacidade real e proteção distribuída contra abuso, J2/#266 |
| C16 | Evidência textual, alvo e validação de tamanho existem; servidor não acessa links | Requisitos de notificação/legitimidade e resposta contextual, J2/J3 |
| C17 | Testes de autoria/denúncia própria e revogação de papel aprovados | Disponibilidade de outro elegível e demais conflitos pessoais, J3 |
| C18 | Canal permite resposta e complemento; notas internas ficam separadas | Comunicação/revisão completas para ambas as partes, J3 |
| C19 | Testes de rejeição/retirada/remoção preservam critérios estruturados | Fraude numérica e direitos com efeitos nos agregados, #262/#270 |
| C20 | Sinais levam à pendência humana; IA sem sinais não garante adequação | Critério jurídico e revisão contextual completos, J3 |
| C21 | Testes conferem flags, limites, falhas e preservação dos critérios | Configuração atual com Nicolas; sem ativação ou fallback novo |
| C22 | Integração envia texto integral elegível ao endpoint de moderação | Contrato, base, países e retenção com Nicolas, J4 |
| C23 | Código não comprova estabilidade de país/suboperadores do fornecedor | Confirmação contratual e processo de revisão, J4 |
| C24 | Testes conferem chave incorreta, sessão/allowlists e separação do histórico | Identidade/legitimidade proporcionais para executar direitos, J2/J5 |
| C25 | Retirada e autenticação existem; não há serviço completo de exclusão da conta comprovado nesta base | Política, efeitos, implementação e validação de #262 |
| C26 | Teste de sete dias confere preservação de pendentes/suspensos; não existe legal hold completo comprovado | Decisão de preservação e descarte conciliados, J6 |
| C27 | Nenhuma restauração de backup real ou exercício isolado de restauração foi feita | Procedimento/cópias/reaplicação de exclusões, J6/Nicolas |
| C28 | Nenhuma entrega de dados a autoridade foi realizada; não há exportação jurídica automática | Validar ordem, legitimidade, escopo e sigilo, J1/J6 |
| C29 | Console de e-mail pode registrar links; CACHE-277-01 foi corrigido | Logs de borda, incidentes e implementação da #266/#267 |
| C30 | Testes conferem indisponibilidade e flags do canal | Operação atual e disponibilidade com Nicolas, J2 |
| C31 | Cookie de sessão e uso de cache público/privado mapeados | CDN/analytics/logs/contratos reais não verificados, J4/J8 |
| C32 | Schema não contém idade; domínio não comprova maioridade | Público provável, análise jurídica e medidas aprovadas, J7 |
| C33 | Ser atendente/solicitante não concede acesso à conta de adolescente | Identidade, legitimidade e medidas aplicáveis, J2/J7 |
| C34 | Usuário não tem ciência/versão de Termos no modelo atual | Contrato de versões, transição e implementação aprovados, J8 |
| C35 | Não foi identificada nesta revisão integração de anúncios; isso não comprova todos os contratos | Reavaliar monetização/patrocínio quando existir, J1/J8/J9 |
| C36 | #260 oferece plano, mas não comprova destino/guarda de cópias nem acesso independente | Continuidade e encerramento com responsáveis, J1/J6/Nicolas |

## 6. Verificações reproduzíveis

Python 3.14.6, FastAPI 0.141.1, Starlette 1.6.0, Windows. O projeto recomenda Python
3.12; não foi substituído. Testes usam SQLite e serviços externos simulados, sem
credenciais reais. Variáveis: DEBUG=False, SECRET_KEY sintética, DATABASE_URL=sqlite://.

Primeira tentativa não iniciou a suíte: faltava `httpx` no ambiente local. A versão
0.28.1, já declarada em `requirements-dev.txt`, foi instalada somente em
`site/review-pr277-test-deps` (ignorado), incluída no PYTHONPATH para a execução. Não
houve atualização de dependências versionadas ou alteração do ambiente compartilhado.
[Starlette aceita essa biblioteca embora prefira httpx2 em versões atuais](https://starlette.dev/testclient/); não foi
introduzida uma migração de biblioteca para contornar a preparação do ambiente.

Comando executado a partir de backend, com sockets locais permitidos:

```powershell
../venv/Scripts/python.exe -m unittest tests.test_solicitacoes_titulares tests.test_comentario tests.test_denuncia tests.test_moderacao tests.test_moderacao_automatica tests.test_consulta_agregada tests.test_agregacao_avaliacoes tests.test_reconciliacao_professores tests.test_recuperacao_senha tests.test_auth -v
```

Resultado antes do teste novo: 135 executados, 134 aprovados e um pulado. Após a
correção/regressão: **136 executados, 135 aprovados e um pulado**. O pulado é
`test_postgres_timeout_de_lock_desfaz_e_permite_nova_tentativa`, que exige PostgreSQL
descartável. Não equivale a homologação PostgreSQL local. Logs sintéticos locais em
`site/review-pr277-pendencias-tests.log`; reprodução da falha em
`site/review-pr277-cache-before.log`, ambos ignorados pelo Git.

Ruff check e format --check dos dois arquivos Python alterados: aprovados. Build
estrito do MkDocs e conferência dos links locais, T01–T18 e C01–C36: aprovados.
`git diff --check`: aprovado. A suíte
completa e integrações PostgreSQL ficam com os checks do novo head. No head anterior
`794be68`, a execução CI 414 concluiu Backend, Frontend, Gitflow, Compose e ambas as
integrações PostgreSQL com sucesso; esse resultado não é atribuído ao novo commit.

## 7. Condições para retomada

### Pendências independentes: conferência de 16/11/2026

O [pacote E1–E6](aceite-complementar-pr277.md) delimita o aceite editorial complementar
da Home, do cartão de moderação do Sobre e dos documentos derivados. Não repete os
aceites A1–A6. A conferência técnica desses textos e da rastreabilidade foi concluída;
o aceite humano complementar, a revisão jurídica e a aprovação formal continuam
dependendo das respectivas pessoas, não exclusivamente de Nicolas.

Não foram encontradas threads de revisão abertas nem revisões submetidas no GitHub.
CI do head `c69e6603760a1fce447ea9ae402f5aa18bd7ca3b` aprovado nas execuções
[416](https://github.com/unb-mds/2026-02-UnDb/actions/runs/43880014295) e
[202 — documentação](https://github.com/unb-mds/2026-02-UnDb/actions/runs/43879798894).
São evidências desse head; cada atualização posterior tem seus próprios checks.

### Insumos e decisões ainda necessários

Nicolas responde às perguntas e fornece evidência sanitizada. A partir desses fatos,
os responsáveis das issues conciliam bases, políticas, retenção, menores e capacidade
de atendimento com a análise jurídica pertinente. Novos comportamentos seguem decisão
humana e atualização de requisitos antes da implementação. Não basta transformar uma
linha pendente em checkbox marcado.

Gabriel autorizou adiar os fatos de Nicolas; não foi inferido aceite de terceiros ou
dispensa de obrigações. As redações A1–A6 e o encaminhamento FGA A7 permanecem preservados.
