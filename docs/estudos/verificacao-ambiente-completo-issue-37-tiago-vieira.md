# Validação adicional do ambiente completo — Issue #37

## Proveniência

| Campo | Registro |
| --- | --- |
| Executor e autor do relatório | Tiago Vieira (`@TiagoVieira-596`) |
| Publicador no repositório | Gabriel (`@gabrielrdaraujo`) |
| Papel do publicador | Preservação do arquivo original, registro da proveniência e envio ao GitHub |
| Autorização informada | “Pode ser, acho que assim fica bem indicado” |
| Data do registro | 22/09/2026 |
| Natureza da evidência | Validação adicional independente |
| Arquivo original | [`Relatorio_Issue_37_Validacao_Ambiente_Completo_TiagoVieira.docx`](./evidencias/issue-37/Relatorio_Issue_37_Validacao_Ambiente_Completo_TiagoVieira.docx) |
| SHA-256 do arquivo recebido | `CA15E817306B7AEECB54215A6DBD33074D8EB7FFF1D74A39EC4DF0A88A0BCD6E` |

O arquivo DOCX foi recebido pronto e incluído sem alterações. O hash acima permite
confirmar que o documento versionado corresponde exatamente ao arquivo entregue por
Tiago. Gabriel realizou somente a publicação e este registro de proveniência.

## Escopo declarado no relatório

O relatório registra uma execução local da stack composta por PostgreSQL 16, backend
FastAPI e frontend Next.js. Segundo o documento, os serviços foram iniciados em conjunto
por Docker Compose e funcionaram sem erros impeditivos observados durante a execução.

O teste informado utilizou o comando:

```text
docker compose up --build
```

O documento também registra a consulta do estado dos serviços com:

```text
docker compose ps
```

## Resultados declarados por Tiago

- PostgreSQL, backend e frontend iniciaram corretamente;
- o backend utilizou o serviço `db` para acessar o PostgreSQL;
- o frontend utilizou o serviço `backend` para acessar a API;
- o healthcheck do PostgreSQL foi utilizado como condição de inicialização do backend;
- as migrações Alembic foram executadas na inicialização do backend;
- o volume `postgres_data` estava configurado para persistência;
- o ambiente integrado funcionou localmente sem erro impeditivo observado.

Esses itens reproduzem as conclusões do relatório entregue. O publicador não refez essa
execução em nome de Tiago e não amplia as afirmações além do conteúdo do arquivo original.

## Limitações registradas

O relatório original não informa o commit exato testado, a data da execução, o sistema
operacional nem as versões locais do Docker. A persistência é fundamentada na configuração
do volume e na execução da stack, mas o documento recomenda como evidência adicional um
reinício sem remover o volume.

Os metadados internos do DOCX registram o gerador `python-docx`, sem nome de autor. Assim,
a atribuição a Tiago se apoia na entrega do arquivo, na identificação do nome no arquivo e
na autorização de publicação reproduzida neste registro, e não nos metadados internos.

A Issue #37 já possuía duas validações independentes registradas antes desta publicação.
Por isso, este documento é classificado como evidência adicional e não substitui ou altera
a autoria dos registros anteriores.
