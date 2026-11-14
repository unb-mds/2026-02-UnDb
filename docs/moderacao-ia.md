# Apoio à revisão de comentários — Issue #239

O apoio usa a **Moderation API gratuita da OpenAI**, com `omni-moderation-latest`,
conforme escolha do PO em 14/11/2026. É preciso configurar uma chave de API no
backend; não há chamada à Responses API ou a modelo de geração pago, nem fallback
pago. O acesso e as cotas disponíveis dependem da conta.

A direção aprovada pelo PO em 14/11/2026 publica automaticamente textos sem sinais
e encaminha os demais à revisão humana. Migração 20261114_01 permite auditoria com
ator sistema; não há armazenamento adicional de textos/pareceres nem alteração de notas.

## Funcionamento

Quando MODERACAO_AUTOMATICA_ATIVA estiver habilitada, o envio salva critérios e
texto pendente, aplica filtro local/privacidade e consulta a API sem locks no banco.
Somente sinalizado=false e nenhuma categoria retornada permitem publicação, após
nova conferência e bloqueio da versão. Qualquer sinal local ou externo, falha,
limite ou configuração incompleta mantém pendência. Não há rejeição automática.
Edição passa pela mesma regra. Suspensão/remoção/denúncia anterior exige humano.

Na fila privada, “Consultar apoio à revisão” continua disponível para moderadores,
sem decidir por eles. Abrir a fila não chama a API. O payload externo contém apenas
modelo e texto, sem IDs/identidades como metadados. A resposta do envio distingue
publicado de pendente; logout não retira uma avaliação já confirmada.

Não há prompt, instruções, ferramentas, geração de justificativa ou tokens de saída
configurados. A resposta validada fornece `flagged` e as categorias nativas:
assédio, assédio com ameaça, ódio, ódio com ameaça, atividade ilícita, atividade
ilícita violenta, autolesão/intenção/instruções, conteúdo sexual/envolvendo menores
e violência/gráfica. Os rótulos descrevem indícios, não julgamento definitivo.

**A API não oferece categorias de spam, exposição de dados pessoais ou palavrões em
geral.** Elas continuam exigindo revisão humana e, para os termos previstos, o filtro
local. Violência não é automaticamente ameaça, e assédio não equivale a qualquer
crítica negativa. Categorias nativas não são convertidas silenciosamente em motivos
de denúncia do UnDb nem adicionadas como proibições de produto.

A interface não preenche ação ou motivo. `flagged=false` não aprova o texto.
A API não fornece o campo de incerteza do classificador personalizado anterior;
nenhum valor é inventado a partir de scores. Todas as substituições são versões
independentes; análise de uma não dispensa revisão de outra. Resultados de versões
alteradas/retiradas durante a chamada são descartados.

## Lista de termos

`backend/app/data/termos_moderacao.json` é a proposta inicial `239-proposta-2`,
com categorias e justificativas. Revisar com o PO antes de habilitar
`MODERACAO_FILTRO_ATIVO`. Palavras/expressões completas, sem distinção de maiúsculas
ou acentos, com espaços consecutivos aceitos entre palavras.

Não inclui palavras como "ruim", "difícil" ou "reprovei". Não detecta todo disfarce
nem toda discriminação e pode sinalizar citações/negações legítimas. Incrementar
versão e reavaliar casos ao alterar o conteúdo. É sinalização para revisão, não veto.

## Configuração e ativação

Variáveis somente no backend, nunca em `NEXT_PUBLIC_*`, código ou chat:

```dotenv
MODERACAO_AUTOMATICA_ATIVA=False
MODERACAO_FILTRO_ATIVO=False
MODERACAO_IA_ATIVA=False
MODERACAO_IA_DADOS_APROVADOS=False
OPENAI_API_KEY=
OPENAI_MODERACAO_MODEL=omni-moderation-latest
MODERACAO_IA_TIMEOUT=10
MODERACAO_IA_POR_MINUTO=5
MODERACAO_IA_POR_DIA=100
```

1. Criar uma chave de projeto na plataforma OpenAI e configurá-la no ambiente privado
   do backend. Não usar chave do navegador nem reutilizar segredos institucionais.
2. Revisar lista, rótulos sintéticos e critérios de qualidade com o PO/moderadores.
3. Avaliar retenção externa, dados enviados e comunicação de privacidade. A flag de
   dados é uma trava operacional, não consentimento do aluno ou aprovação jurídica.
4. Habilitar as duas flags de IA no ambiente de teste para avaliação sintética; lista
   pode ser habilitada separadamente. Reiniciar o backend para carregar configuração.
5. Validar acesso/cotas da conta e resultados reais antes de ativar com comentários reais.

O cliente aceita somente a família `omni-moderation-*` e sempre usa o endpoint fixo
`/v1/moderations`. Configurar modelo de geração causa indisponibilidade, sem chamada
externa. O alias pode evoluir; a resposta inclui o modelo efetivamente informado
pelo provedor. Revalidar preços e disponibilidade no momento da ativação.

Uma tentativa HTTP, HTTPS, sem redirecionamentos, resposta limitada a 32 KiB e
timeout de socket entre 1 e 30 segundos. Não é prazo absoluto contra resposta lenta
em fragmentos. Falhas, resposta inválida e falta de chave preservam a fila humana,
sem expor mensagens brutas do provedor.

Limites em memória **por processo**, janela móvel de minuto e 24h, contando também
tentativas que falham. Não armazenam texto ou ID. Reinícios zeram contadores e
workers/réplicas multiplicam a cota; tetos defensivos de 30/minuto e 1.000/24h por
processo. Servem para limitar uso/abuso, mesmo com endpoint gratuito. Antes de
escalar, planejar limitação compartilhada e conferir cotas da conta.

Desligar: `MODERACAO_IA_ATIVA=False` e reiniciar/republicar pelo procedimento vigente.
Impede novas chamadas; chamadas em curso podem terminar. Não há parecer persistido
para limpar. O filtro pode ser desligado à parte.

## Dados e limites de privacidade

Uma barreira local impede envio ao reconhecer e-mail, sequências numéricas longas,
links, referências comuns a documentos/credenciais ou partes do nome do autor no
texto. **Não é anonimização completa**: dados disfarçados e nomes de terceiros podem
escapar. Moderador deve conferir o texto antes da consulta; a ativação com dados
reais depende da avaliação explícita dessa limitação.

O backend não registra texto/parecer em logs ou banco. O endpoint de moderação não
usa o parâmetro `store` da Responses API: não se deve prometer que `store=false`
controla retenção nessa integração. Avaliar controles e condições aplicáveis à conta
OpenAI; descarte local em sete dias não significa descarte externo. Não enviar
material conhecido/suspeito de abuso sexual infantil a essa API, conforme orientação
do provedor. Não usar comentários reais em fixtures.

## Contrato privado

`POST /api/moderacao/comentarios/{versao_id}/triagem`, sem texto vindo do cliente.
Requer moderador confirmado e elegível, sem autoria/denúncia própria ou impedimento
ligado à versão substituída. Apenas versões pendentes/publicadas/suspensas com texto.
Não altera permissão de decidir nem verifica se o aluno cursou a disciplina.

Retorna `comentario_versao_id`, `status`, `filtro_ativo`, `versao_lista`,
`categorias_locais` (sete motivos do UnDb), `categorias_ia` (categorias nativas da
OpenAI), `sinalizado` (booleano ou null se não analisado), `modelo` e
`versao_integracao`. Não há `incerto` ou `versao_prompt`.

Status: `CONCLUIDA`, `DESATIVADA`, `DADOS_SENSIVEIS`, `LIMITE`, `INDISPONIVEL`.
Erros 401/403/404/409 preservam autorização, existência e estado. Resposta de sucesso
usa `Cache-Control: no-store`. Não retorna texto livre da OpenAI ou scores usados
como suposta probabilidade de culpa.

## Avaliação reproduzível

No checkout de desenvolvimento, dentro de `backend`, com dependências instaladas:

```bash
python -m unittest tests.test_triagem -v
python -m app.commands.avaliar_triagem
```

O segundo comando avalia a lista proposta sem rede/ativação. A fixture sintética em
`tests/fixtures/triagem_sintetica.json` tem rótulos **propostos**, separados para lista
e categorias OpenAI; revisar com humanos antes de homologar. Não converter ausência
de categoria da API em garantia de que não houve spam ou exposição de dados.

Após configurar chave/flags e autorizar o envio desses casos sintéticos:

```bash
python -m app.commands.avaliar_triagem --openai
```

Consulta somente a Moderation API gratuita. Respeita limites e bloqueio de dados;
com 5/minuto nem todos os 12 casos são enviados numa execução. Para avaliar os casos
não sensíveis de uma vez, ajustar conscientemente a cota para 12 e depois restaurar.
Relata FP/FN por categoria e casos não analisados, sem imprimir textos/segredos ou
resposta bruta. A fixture está no checkout, não na imagem de produção.

## Fontes oficiais

Consultadas em 14/11/2026:

- [Endpoint gratuito, categorias e exemplos](https://developers.openai.com/api/docs/guides/moderation).
- [Controles de dados da plataforma](https://developers.openai.com/api/docs/guides/your-data).

A implementação anterior com Responses API paga foi substituída antes de qualquer
chamada externa. Testes determinísticos verificam o contrato e o fluxo humano,
**não a qualidade do modelo real**. Chave, avaliação real, revisão da lista e metas
de qualidade ainda são necessárias antes da ativação.

## Verificações da troca para Moderation API

Em 14/11/2026: 259 testes backend aprovados (dois opcionais ignorados), 78 testes
frontend aprovados, TypeScript, lint dos arquivos alterados, build Next.js com
Webpack e MkDocs estrito aprovados. Teste em Brave isolado com API fictícia aprovou
os cinco estados da triagem e a regressão das ações humanas, incluindo 24 combinações
de estado/largura/tema. O teste de transporte confirma o endpoint `/v1/moderations`,
payload apenas com modelo/texto e bloqueio de configuração de geração paga.
Não foi feita chamada real à OpenAI, nem configurada chave ou ativado envio de dados.


## Habilitar o novo fluxo

Depois de aplicar a migração e revisar a lista, habilitar explicitamente no ambiente
de teste MODERACAO_AUTOMATICA_ATIVA=True e MODERACAO_FILTRO_ATIVO=True, além das
flags/chave da IA. Não foram ativadas automaticamente nem houve deploy nesta tarefa.
Todos os controles são necessários: desligar qualquer um mantém os envios pendentes.
No Docker Compose as variáveis do backend são repassadas sem gravar a chave na imagem.

Uma publicação registra APROVAR com moderador_id nulo (sistema), data, transição,
versões da lista/integração e modelo, sem copiar o texto; descarte após sete dias.
Não são armazenados pareceres para pendências, que permanecem na fila existente.
O downgrade da migração é bloqueado enquanto houver auditoria automática retida,
em vez de excluí-la ou atribuí-la a uma pessoa. O fluxo pode demorar o timeout da
API; critérios já foram salvos mesmo se a conexão do navegador for interrompida.

Limitações mantidas: sem classificação nativa de spam/dados pessoais/palavrões;
barreira local e lista não cobrem todos os disfarces. Não se afirma que um texto
sem sinais seja seguro ou que a API identifique toda ambiguidade.


## Verificações do fluxo automático — 14/11/2026

269 testes backend aprovados (dois opcionais ignorados) e 79 frontend aprovados.
Os dez novos cenários também passaram em PostgreSQL 16 descartável, com schema
criado apenas por Alembic e API simulada. Upgrade e comparação de schema aprovados;
downgrade recusou perda de auditoria e passou após descarte de fixtures vencidas,
seguido de novo upgrade/check. Banco descartável removido ao final.
Build Next.js/Webpack, lint dos arquivos alterados, MkDocs estrito e composição
Docker aprovados. Imagem backend construída sem .env e com a lista incluída.
Navegador com API fictícia validou envio pendente/publicado, substituição e retirada.
Não foi aplicado schema no banco real nem habilitado modo automático no .env
privado, realizado deploy ou criados commits/PRs. A conectividade com a OpenAI foi
validada anteriormente pelo PO com os exemplos sintéticos; os testes deste novo
fluxo não enviaram comentários reais.
