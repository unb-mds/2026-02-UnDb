# Hospedagem pública e operação

Registro de 09–10/11/2026, consolidado na [PR #213](https://github.com/unb-mds/2026-02-UnDb/pull/213)
por solicitação de Nicolas, PO e operador desta configuração. Relaciona #169,
#170, #171 e a validação de e-mail #165. Registra a escolha feita na conversa e
o ambiente observado; não declara homologação operacional de toda a Release 2.

## Componentes e escolha inicial

| Componente | Serviço usado | Papel |
|---|---|---|
| Frontend Next.js | Vercel Hobby | Aplicação em [undb.app.br](https://undb.app.br) |
| API FastAPI | Render Free, Web Service Docker | [api.undb.app.br](https://api.undb.app.br/health) |
| PostgreSQL | Neon Free | Persistência compartilhada pela API e pelo importador |
| E-mail transacional | Resend | Confirmação enviada por `no-reply@undb.app.br` |
| Registro e DNS | Registro.br | Zona de `undb.app.br`; não houve delegação para a Vercel |
| Importador SIGAA | Processo Python local independente | Povoamento manual de graduação 2026.2 no Neon |

O objetivo autorizado foi começar com serviços gratuitos para demonstração à
professora, aproveitando Next.js, Docker e PostgreSQL existentes. O domínio foi
comprado separadamente: infraestrutura no plano gratuito não significa domínio
gratuito. Nicolas criou/configurou as contas, variáveis, DNS e importação; revisão
e continuidade da operação devem ser acompanhadas pelo time nas issues citadas.

| Alternativa discutida | Vantagem considerada | Escolha e limite |
|---|---|---|
| Vercel + Render + Neon | Aproveita frontend e API atuais e separa a persistência do ciclo do container | Usada na demonstração; exige coordenar URLs, CORS, certificados e serviços distintos |
| Supabase como PostgreSQL hospedado | Alternativa discutida para o banco | Não adotada; não houve migração para Supabase Auth ou Storage |
| VM com o Compose existente | Reúne processos, inclusive tarefas contínuas | Alternativa futura se necessária; não contratada nem configurada nesta sessão |
| Neon em São Paulo ou EUA | Proximidade entre API e banco reduz o percurso de consultas | A recomendação foi aproximar as regiões de API/banco; a região final de ambos não foi auditada nesta revisão. Resend mostrou São Paulo no painel |

O Render Free pode suspender o serviço por inatividade, demora a retomar e não
oferece disco persistente. O PostgreSQL fica no Neon, não no filesystem da API.
Conferir consumo e limites nos painéis antes de uma apresentação; não se assume
disponibilidade contínua ou SLA. [Limites oficiais do Render](https://render.com/docs/free).
Não foram comprados planos pagos durante esta configuração.

## Frontend na Vercel

Importar `unb-mds/2026-02-UnDb`, selecionar **Root Directory `frontend`** e preset
**Next.js**. A detecção de `backend`/FastAPI na primeira tela não serve para esse
projeto frontend. O serviço da API continua no Render. A branch pública observada
é `main`; uma prévia de PR não comprova promoção para produção.

| Variável | Valor público / orientação |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://api.undb.app.br` |
| `API_INTERNAL_URL` | Opcional fora do Compose; se definido, usar URL acessível ao servidor Vercel. Sem ele, o cliente de servidor usa a URL pública |

`NEXT_PUBLIC_API_URL` é pública e incorporada ao build; alteração exige novo
deploy. Não colocar `DATABASE_URL`, `SECRET_KEY` ou chave Resend em variáveis
`NEXT_PUBLIC_*`. No Compose, `API_INTERNAL_URL=http://backend:8000` tem outro
contexto e não deve ser copiado para a Vercel.
[Configuração de variáveis da Vercel](https://vercel.com/docs/environment-variables).

## API no Render e conexão Neon

Usar **Web Service**, repositório autorizado na integração GitHub, linguagem
Docker e plano **Free**. Se só alguns repositórios aparecerem, revisar o acesso da
integração à organização/repositório. Configuração com caminhos relativos à raiz:

| Campo | Valor |
|---|---|
| Root Directory | Vazio |
| Docker Build Context Directory | `backend` |
| Dockerfile Path | `backend/Dockerfile` |
| Docker Command | `python -m app.commands.iniciar_servidor` |
| Pre-Deploy Command | Vazio |
| Health Check Path | `/health` |

Alternativa equivalente: Root Directory `backend`, contexto `.`, Dockerfile
`./Dockerfile`. Não misturar os dois conjuntos de caminhos. O Dockerfile local
mantém seu CMD Uvicorn na porta 8000; o **override no painel** é necessário para
o fluxo hospedado desta versão. Não existe Blueprint `render.yaml` versionado
nesta base; a configuração foi feita manualmente.

O inicializador valida `PORT`, executa `alembic upgrade head` e só então substitui
o processo por Uvicorn em `0.0.0.0:$PORT` (padrão 10000). Se a migração falha,
o servidor não inicia. Não colocar aspas envolvendo o comando inteiro nem uma
sequência `alembic ... && uvicorn ...` no campo: isso causou status 127 no deploy.

| Variável do Render | Configuração |
|---|---|
| `DATABASE_URL` | Conexão direta Neon, `postgresql+psycopg2://`, com `sslmode=require`; valor secreto |
| `SECRET_KEY` | Valor aleatório privado, mantido no painel |
| `DEBUG` | `False` |
| `CORS_ORIGINS` | Lista separada por vírgulas; origem principal `https://undb.app.br`. Incluir outras origens apenas quando usadas e verificadas |
| `FRONTEND_URL` | `https://undb.app.br` |
| `EMAIL_BACKEND` | `resend` |
| `EMAIL_FROM` | `UnDb <no-reply@undb.app.br>` |
| `RESEND_API_KEY` | Chave privada de envio, restrita ao domínio verificado |

Editar variáveis já existentes: o painel rejeita chaves duplicadas. A primeira
configuração usava `EMAIL_BACKEND=console`, que só registra o link nos logs; ela
foi substituída por `resend` antes da validação de entrega externa.

Copiar do Neon somente a URI, sem `psql`, aspas ou instruções adicionais. Nesta
base o driver instalado é `psycopg2-binary`: preservar usuário, senha, host, banco
e parâmetros da URI, ajustando o prefixo para `postgresql+psycopg2://`. O erro
`ModuleNotFoundError: No module named 'psycopg'` foi resolvido assim. Nenhuma senha
ou chave pertence a esta documentação. A conexão direta foi usada para migração
e importação; conexão pooled é distinta e deve ser avaliada antes de trocar o
endpoint. [Pooling no Neon](https://neon.com/docs/connect/connection-pooling).

`pool_pre_ping=True` testa conexões antes de reutilizá-las, mas não recupera uma
transação interrompida. O sucesso de `/health` comprova o processo HTTP: esse
endpoint retorna `{"status":"ok"}` sem consultar o banco.

## DNS, domínio e HTTPS

No Registro.br, manter seus servidores DNS e usar **Configurar zona DNS**, em
modo avançado. Cadastrar os nomes relativos (`api`, `www`; nome vazio para raiz)
conforme a interface, sem repetir `.undb.app.br`. A tabela final deve mostrar os
nomes completos abaixo. Valores públicos observados em 09/11:

| Tipo | Nome completo | Destino observado |
|---|---|---|
| A | `undb.app.br` | `216.198.79.1` |
| CNAME | `www.undb.app.br` | `561f642ad75552f8.vercel-dns-017.com.` |
| CNAME | `api.undb.app.br` | `undb-api.onrender.com` |

Copiar sempre o destino **do painel do projeto** ao recriar a configuração;
endereços recomendados pelo provedor podem mudar. Na Vercel, raiz conectada a
Production e `www` redirecionando por **308** para a raiz. No Render, adicionar
`api.undb.app.br`, salvar o CNAME no Registro.br e verificar o domínio.

A transição do modo DNS no Registro.br e a propagação atrasaram as verificações.
`Invalid Configuration` logo após salvar não provou erro na entrada. Ao fim,
Vercel mostrou raiz/www válidos e Render mostrou **Verified / Certificate Issued**;
o responsável confirmou acesso aos dois endereços. Não é necessário trocar
nameservers para fazer esses apontamentos.

## Resend e confirmação institucional

Adicionar `undb.app.br`, copiar os registros **inteiros** do painel para o
Registro.br e aguardar `Verified`. A tela usada nesta sessão apresentou TXT DKIM
`resend._domainkey` e CNAMEs de envio `rsend` e `send`. Os destinos/valor DKIM
ficaram truncados nas imagens: não são reconstruídos aqui. Usar os registros
atuais do painel; não substituir por uma receita de outra região/produto.
Não há evidência suficiente nesta revisão para afirmar que DMARC ou recebimento
de e-mail foram configurados. [Domínios verificados no Resend](https://resend.com/docs/dashboard/domains/introduction).

Após a verificação, criar chave de envio restrita a esse domínio e guardá-la no
Render. `no-reply@undb.app.br` é o remetente transacional; isso não cria uma caixa
postal. O domínio de cadastro aceito continua `@aluno.unb.br`.

**Evidência #165, 09/11:** o PO cadastrou conta institucional no ambiente público,
recebeu a mensagem na caixa institucional, confirmou o link e autenticou com
sucesso. Preservar tokens e dados pessoais fora de issues/capturas públicas.
Esse fluxo não comprova envio de toda mensagem futura nem o restante da #171.

## Atualizar, diagnosticar e reverter

1. Integrar por PR, promover pelo fluxo `release/*`/`hotfix/*` para `main` e
   retornar os ajustes da release a `develop`, conforme o guia de contribuição.
   Esta PR documental não promove #214/#215 nem altera versões do pacote.
2. Antes de migração com dados, obter cópia privada e validar recuperação em
   ambiente isolado. Conferir revisão/variáveis dos dois serviços.
3. Acompanhar logs de build, migração e inicialização no Render; depois conferir
   health, consulta real ao catálogo e fluxo navegador/API. Atualizar frontend e
   API juntos quando a tela depender de um campo novo.
4. Conferir HTTPS, redirecionamento `www`, requisições/CORS e cookies seguros;
   conferir cadastro, confirmação, login, logout e avaliação com conta de teste.
   Nesta sessão foram demonstrados cadastro/confirmação/login e leitura pública;
   não se declara todo esse roteiro executado em produção.
5. Para reverter código, selecionar revisão anterior compatível com o schema
   atual e refazer as verificações. **Reverter deploy não desfaz migrações**;
   não executar downgrade ou restaurar sobre o banco público automaticamente.

| Sintoma | Verificação útil |
|---|---|
| Status 127 / comando inteiro “not found” | Docker Command sem aspas externas, módulo Python disponível na revisão publicada |
| Falta de `psycopg` | Driver/prefixo da URI e dependências da imagem |
| Health OK, catálogo falha | URL usada pelo frontend, CORS, banco e logs; health não testa persistência |
| Primeira requisição lenta | Partida após inatividade do Render; distinguir de erro persistente |
| E-mail não chega | `EMAIL_BACKEND`, domínio/chave/remetente e eventos do Resend; não publicar o link/token |
| `ClientRead` / `idle` no PostgreSQL | Servidor aguardando cliente; isoladamente não prova importação travada |

## Backup e restauração — roteiro ainda não executado

A #170 exige verificação de recuperação. Não foi obtida evidência de dump,
restauração ou política periódica instalada nesta sessão. Limites/janela de
restauração do plano Neon devem ser conferidos no projeto, sem pressupor retenção
ou backup externo automático. Roteiro para o operador, em ambiente isolado:

1. Com cliente PostgreSQL compatível, configurar conexão direta/TLS via mecanismo
   privado (por exemplo, serviço libpq + arquivo de senha protegido). Não colocar
   a URI real em histórico, argumentos, repositório ou relatório.
2. Executar `pg_dump --format=custom --no-owner --no-acl --file=<arquivo-privado>`
   usando a conexão de origem configurada pelo operador. Guardar fora do repo e
   validar o arquivo com `pg_restore --list <arquivo-privado>`.
3. Apontar explicitamente para **outro banco vazio**, verificar host/banco antes
   de executar `pg_restore --no-owner --no-acl --exit-on-error --dbname=<destino-isolado> <arquivo-privado>`.
   Não usar o banco público como destino do ensaio.
4. Conferir `alembic_version`, contagens/vínculos, leitura e escrita com dados de
   teste na cópia. Preservar privacidade e os prazos de descarte também nas cópias.
5. Registrar data, versão das ferramentas, origem/destino sem credenciais,
   resultado e responsável; só então considerar o procedimento validado.

## Tarefas fora do servidor HTTP

O povoamento manual terminou com sucesso: ver [relatório da importação](estudos/importacao-neon-2026-11-10.md).
O agendamento por GitHub Actions foi discutido, mas **não existe workflow SIGAA
versionado nesta base** nem evidência de instalação de cron remoto. O guia
[Operação SIGAA](operacao-importacao-sigaa.md) descreve o comando e os perfis
previstos; #164 ainda exige demonstrar execução periódica e histórico.

A retenção de moderação tem prazo aprovado de sete dias. O comando existente é
`python -m app.commands.descartar_moderacao --continuo`, com ciclo de 60 segundos,
e o Compose local possui processo próprio. Não houve evidência de processo
contínuo equivalente instalado no ambiente gratuito. Limpeza durante acesso ou
uma importação ocasional não substitui essa obrigação. A escolha/implantação de
operação contínua segue em #169/#171; não se declara atendida pela API no Render.

Responsabilidades de acompanhamento: Nicolas nas #164/#169/#170/#171; time na
revisão e definição da continuidade; aceite e fechamento de issues permanecem
manuais com o PO. O registro não cria novo serviço pago, requisito ou SLA.
