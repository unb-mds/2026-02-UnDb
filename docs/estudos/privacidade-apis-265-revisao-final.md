# Privacidade das APIs — #265 na revisão final

Data: 20/11/2026. Base: `origin/develop@18179192250b80c4534784697972021cd2e89a64`
mais as alterações locais de `codex/revisao-geral-final`. Fonte de autorização:
Nicolas solicitou executar nesta revisão o trabalho pendente da Yasmin, revisar o
conjunto e deixar a implementação pronta para posterior decisão sobre main/publicação.

## Escopo confirmado

Consulta ao GitHub em 20/11/2026: nenhuma PR aberta de `ailoiol`; #265 atribuída à
Yasmin e aberta. O trabalho é executado pelo escopo vigente da
[issue #265](https://github.com/unb-mds/2026-02-UnDb/issues/265), sem inventar uma PR,
sem alterar atribuições, comentar/fechar issues ou aprovar trabalho em nome dela.
A atualização das referências confirmou `develop` no mesmo SHA da base local.
As entregas das PRs #277/#279/#280/#283/#285 já estão nessa base e foram reutilizadas.

Esta conferência substitui a espera por implementação externa. Não substitui a
validação hospedada nem o aceite humano final da #168. Estudo aprofundado de
reidentificação e revisão jurídica formal permanecem fora da etapa, conforme a issue.

## Matriz atual de acesso e necessidade dos campos

A necessidade abaixo é técnica e rastreável ao fluxo autorizado, não determinação
jurídica de proporcionalidade. Permissões e retenções aprovadas foram preservadas.

| Superfície / ator | Campos necessários ao fluxo observado | Proteção e limite |
|---|---|---|
| Catálogo / visitante | UUID institucional, nome, unidade, códigos, ofertas; SIAPE no detalhe docente atual | Identifica docente/oferta, não conta avaliadora. Revisão de necessidade pública do SIAPE segue como evolução; nenhum uso indevido novo foi comprovado e não houve remoção por preferência |
| Agregados / visitante | Professor/disciplina, contagem; cinco critérios somente com três ou mais avaliações | O vínculo interno com autor não é serializado; contagem/insuficiência abaixo do mínimo. Mínimo não garante anonimato |
| Comentários publicados / visitante | ID da versão para denúncia/voto, texto publicado e criação | Sem conta, nome/e-mail do autor, `avaliacao_id` ou critérios individuais; texto/data/contexto ainda podem identificar indiretamente |
| Comentários do autor / autor confirmado | ID/estado/texto próprio, vínculo com avaliação/substituição e datas | Consulta filtra usuário no servidor; sem identidade de outros autores ou denunciantes; no-store/no-referrer |
| Minhas avaliações / própria sessão (RF27) | ID próprio, cinco respostas, professor/disciplina e atualização | Usuário exclusivamente da sessão; excluídas omitidas; paginação; sem nome/e-mail/UUID do avaliador, comentários ou moderação; no-store/no-referrer |
| Utilidade / visitante ou sessão | `uteis`, `nao_uteis`, `meu_voto` | Apenas voto da sessão consultante; nenhuma lista/identidade de votantes; não armazena resposta em cache |
| Denúncia / visitante ou sessão | Motivo fechado na entrada; mensagem genérica na saída | Identidade interna serve à unicidade e impedimentos, sem retorná-la ao público; lista só para moderação autorizada |
| Moderação / moderador confirmado | Texto/estado/versão, autor `{id,nome,email}`, denúncias e identidades internas previstas por RF22, decisão/responsável/motivo/data | IDs sustentam autorização/impedimentos/rastreabilidade; nome/e-mail dão contexto ao revisor conforme contrato vigente, não autorização de divulgação pública. Não retornar credenciais, IP ou hash. Mudar poderes/campos aprovados requer decisão própria |
| Reconciliação / reconciliador confirmado | Identificadores institucionais/candidatos/evidência/versão e decisões | Papel distinto de moderação; não concede acesso às identidades de estudantes por ser reconciliador |
| Atendimento / leitor ou atendente configurado | Protocolo/categoria/data; detalhe e eventos internos; UUID responsável | Leitor consulta, atendente escreve. A consulta com protocolo/chave recebe só RESPOSTA/COMPLEMENTO e omite responsável. Segredo armazenado como hash, não em URL |
| Autenticação / usuário ou solicitante de link | Email/senha de entrada, hash interno; token de sessão em cookie; validade/uso de links | Respostas neutras no envio de links, cookie HttpOnly/SameSite e Secure fora de DEBUG. Não retorna hash de senha/token, não usa localStorage para sessão |
| Retenção e registros / processo interno | Vínculo residual, e-mail reservado, prazos; operação/ator/horário/IP em registro privado definido na #266 | Não acessíveis por consulta pública; sem novos campos/prazos. Logs externos e guarda mínima continuam com limites operacionais documentados |

## Verificação e correção

Cinco novos testes em `backend/tests/test_privacidade_revisao_265.py` usam somente
fixtures sintéticas e APIs reais em ASGI:

1. Campos exatos dos comentários públicos e denúncia; ausência de nomes/e-mails/UUIDs
   de contas ao consultar como visitante, autor, outra conta ou moderador; agregados
   com insuficiência sem notas individuais.
2. Detalhe/denúncias/decisões negados a visitante/conta comum/não confirmada; nomes e
   e-mails internos somente no contrato do moderador, sem credenciais e sem cache.
3. Alternância de contas nas respostas individuais; tentativa de selecionar outro
   usuário pela query não ultrapassa a sessão; mutações alheias são negadas.
4. Votos retornam só contagens e estado do próprio usuário, inclusive ao alternar
   contas; cabeçalhos privados preservados.
5. Exclusão lógica remove a avaliação das consultas públicas/privadas e torna a
   utilidade indisponível, sem reexpor o texto.

Resultado: cinco aprovados. Regresões existentes de papéis, origens, cookies, logs,
422/500 seguros, retenção, votos e atendimento foram reutilizadas na suíte completa.
Nenhuma exposição de identidade de conta foi confirmada nas respostas exercitadas.
Isso não comprova anonimização de texto, de pequenos grupos ou de diferenças temporais.

**Finding confirmado de interface — dados antigos no atendimento:**
`frontend/src/app/atendimento/fila.tsx` consultava permissão só na montagem/paginação;
voltar à aba após expiração/revogação podia manter um pedido já aberto no DOM até
outra ação. A API continuava autorizando cada operação, sem bypass confirmado.
Foi adicionada revalidação em foco/pageshow/visibilidade/evento de sessão, limpeza
imediata dos dados ao ocultar/revalidar e invalidação de respostas atrasadas de
consulta/escrita. Nenhuma permissão de leitura/escrita foi ampliada.

O runner `solicitacoes-browser.mjs` agora verifica perda de permissão com pedido
aberto, recuperação, troca de sessão e resposta antiga retida que não pode reexibir
conteúdo após revogação. Cenário aprovado com HTTP sintético.

## Comunicação e limites

Home manteve as alterações editoriais pedidas por Nicolas em 18/11: frase antiga,
sem o parágrafo adicional e indicador resumido. Sobre/metodologia, Termos e
Privacidade continuam explicando vínculo interno, mínimo de três, comentários
abaixo desse mínimo e risco de identificação contextual. A política foi complementada
para refletir a consulta privada das próprias avaliações já autorizada em RF27.
Não houve promessa de anonimato absoluto ou alteração da ciência dos Termos.

Reutilizado o inventário da PR #277 como histórico; essa matriz atualiza os fluxos
#266/#278/#263 e RF27 sem sobrescrever evidências antigas. SIAPE, fornecedores,
conta mínima, logs externos e retenção operacional continuam com suas ressalvas.
Nenhum teste com usuário real, produção, provedor de email ou IA foi executado.

## Handoff para #168

Parte local de implementação/verificação da #265 incorporada à revisão geral.
Após decisão sobre main/publicação: identificar SHA hospedado e conferir TLS,
CORS/cookies, cache/CDN, versões e cabeçalhos na borda; permissões de banco e
operadores reais; jobs/purgas; logs/fornecedores e os limites da matriz da #266.
Não fechar #265/#168 por esta entrega local, não duplicar suítes já aprovadas sem
mudança, e manter o que depender de operação/aceite explicitamente pendente.

## Resultados da continuidade

Backend completo no Docker/Python 3.12 com novo PostgreSQL 16 migrado:
461 testes, dois ignorados; Ruff check/format e compileall aprovados. Frontend:
99 testes, ESLint sem avisos e build Docker/TypeScript aprovados. Auditoria npm
de runtime em 20/11 retornou zero avisos; não cobre ferramentas dev ou produção.
MkDocs strict aprovado. A regressão ampla de navegador é consolidada no
[relatório da implementação](revisao-geral-implementacao-2026-11-20.md).
