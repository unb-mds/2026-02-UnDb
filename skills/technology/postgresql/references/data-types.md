# Tipos de dados PostgreSQL

Escolha pelo significado e pelos valores autorizados, não por convenção. Registre qualquer escolha que mude semântica, interoperabilidade ou migração como proposta até a aprovação aplicável.

| Tipo | Use quando | Evite quando |
| --- | --- | --- |
| `INTEGER` | faixa inteira cabe em 32 bits e esse é o significado | usar para identificador universal apenas por hábito. |
| `BIGINT` | o domínio inteiro exige faixa maior | “prever escala” sem estimativa ou requisito. |
| `UUID` | identidade distribuída/externa ou modelo autorizado pede UUID | substituir PK existente sem decisão/migration. |
| `TEXT` | texto sem limite de domínio conhecido | impor `VARCHAR(n)` arbitrário. |
| `VARCHAR(n)` | limite de negócio é conhecido, como código ou tamanho documentado | usar `VARCHAR(255)` como padrão sem razão. |
| `BOOLEAN` | estado binário definido | codificar três estados quando `NULL` é ambíguo. |
| `DATE` | apenas data importa | armazenar data como texto. |
| `TIMESTAMP` | data/hora local sem instante global | registrar evento/auditoria que precisa de instante absoluto. |
| `TIMESTAMPTZ` | eventos e auditoria entre zonas; PostgreSQL armazena o instante em UTC | esperar que a zona original seja preservada. |
| `NUMERIC(p,s)` | precisão decimal exata é requisito | usar para métricas inteiras ou sem domínio de precisão. |
| `JSON`/`JSONB` | estrutura variável autorizada e o acesso/índice justifica | ocultar entidades relacionais, constraints ou consultas centrais. |

No G7, UUID, `VARCHAR` com limites documentados, `SMALLINT` para didática, `BOOLEAN`, enums e `TIMESTAMPTZ` são escolhas especificadas. `JSONB` não deve ser introduzido para dados de avaliação ou SIGAA sem modelo e acesso autorizados. Em SQLAlchemy, mapeie o tipo e sua nulidade de modo consistente com a migration; tipos PostgreSQL nativos, como `UUID`, `JSONB` e `ENUM`, exigem revisão manual da migration.
