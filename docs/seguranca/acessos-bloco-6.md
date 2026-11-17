# Registros de acesso — Bloco 6

Estado: implementado. Fonte: decisão C do PO. Premissa de não aplicação do art. 15
do Marco Civil por ausência de fins econômicos: pendente de validação jurídica.
Não é evidência de produção. Nenhum ambiente de produção foi acessado.

Migração reversível 20261117_03 cria registros_acesso, sem endpoint/painel ou FK
que impeça exclusão de conta. Usuário é ID interno, sem nome/e-mail. Middleware
ASGI registra sucesso/falha das mutações de autenticação (inclusive falhas e
reenvio), avaliações, comentários, denúncias, moderação, identidade, exclusões e
canal público/interno de titulares. Publicação/edição no mesmo POST de avaliação
usa operação avaliacoes.escrever; nenhuma leitura pública é registrada.

Campos: UUID do registro e da requisição gerados no servidor, UTC, operação fixa,
usuário quando resolvido pela autenticação da rota (inclusive login bem sucedido),
peer ASGI, valores brutos de Forwarded/X-Forwarded-For, resultado. Não persiste
corpo, query string, cookie, senha, token, texto, e-mail ou nome. Falhas anônimas
ficam sem ID de usuário. Não se identifica conta por e-mail no registro.

Encaminhamento é NÃO confiável. Compose usa --no-proxy-headers para preservar o
peer de conexão; na hospedagem é necessário conferir essa opção e a topologia
com Nicolas (item 8). Sem essa evidência, não interpretar o peer ASGI como IP
original do visitante. Nenhuma chave de limitação usa IP.

ACESSO_RETENCAO_MESES=6 determina expiração em meses corridos, ajustando dias ao
fim do mês (inclui bissextos). O job de purga existente remove vencidos em lotes;
nenhum prazo de conta/metadados é inferido desse prazo. Downgrade remove a tabela
e seus dados: esquema reversível não recupera registros apagados.

Escrita ocorre fora da transação de negócio e fora do event loop. Se o banco de
registro falhar, gera somente acesso.gravacao_falhou, sem exceção/dados pessoais;
não desfaz ação já confirmada nem impede ação urgente. Isso pode deixar lacuna
de evidência e exige monitoramento operacional, pendente de validação. Filtros
de console aceitam apenas esse evento constante; campos de acesso não são
impressos. O job/API usam as permissões existentes, sem alterar produção.

Sigilo: acesso direto por operador autorizado de banco, com aprovação da pessoa
responsável pelo controlador (identidade pendente de validação), escopo e período
definidos. Registrar justificativa, autorização, executor e destinatário em canal
privado; consultar somente período/IDs pertinentes, exportar por meio protegido,
restringir cópia e acesso e comprovar descarte segundo política aprovada. Não
copiar registros para PR, issue, console ou artefato público. Papéis efetivos e
acesso da equipe permanecem pendentes de validação operacional.

Ordem judicial: encaminhar para responsável e validação jurídica da autenticidade,
alcance e forma de atendimento; preservar apenas o escopo autorizado sem alterar
prazos por iniciativa técnica; entregar pelo canal aprovado com registro mínimo
de cadeia de custódia. Nenhum prazo legal ou obrigação é declarado validado.

Testes: tests.test_registros_acesso cobre meses corridos, eventos, minimização,
encaminhamento não confiável e persistência/purga. Migração/modelo e job também
foram exercitados no PostgreSQL descartável. Bloco 8 não iniciado.
