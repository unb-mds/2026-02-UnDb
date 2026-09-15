# Integridade e constraints

Escolha a garantia estrutural mais próxima da regra autorizada. API e serviço não substituem constraints para invariantes que o banco consegue garantir.

| Mecanismo | Use quando | Atenção |
| --- | --- | --- |
| `PRIMARY KEY` | identifica uma linha estavelmente | chave composta é válida quando representa identidade; não esconda chave candidata relevante. |
| `FOREIGN KEY` | referência exige linha existente | `ON DELETE`/`ON UPDATE` só com regra autorizada; FK não cria automaticamente índice na coluna referenciante. |
| `UNIQUE` | valor ou combinação não se repete | use composição para unicidade de vários atributos. |
| `NOT NULL` | ausência é inválida | não confunda desconhecido com vazio ou zero. |
| `CHECK` | domínio é predicado por linha | não o use para estado de outras linhas sem suporte analisado. |
| `DEFAULT` | há valor de ausência autorizado | não substitui requisito nem validação de entrada. |

## Avaliação

O requisito `(usuario_id, professor_id, disciplina_id)` pede FKs e `UNIQUE` composta, uma vez que nomes e relações estejam alinhados ao modelo aprovado. A constraint é barreira de concorrência; “novo envio substitui anterior” é comportamento de escrita. Após autorização, repository/service atualiza a linha encontrada ou aplica upsert com semântica explícita; migration introduz a constraint tratando dados existentes; testes demonstram integridade e reenvio.

No G7, use o RF03 de `docs/requisitos.md` e o modelo aprovado em `docs/arquitetura.md` como fontes da regra. Compare essas fontes com SQLAlchemy e Alembic; se os artefatos divergirem, registre o conflito sem eleger silenciosamente uma fonte ou editar o modelo.
