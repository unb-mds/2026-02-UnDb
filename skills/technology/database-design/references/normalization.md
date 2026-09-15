# Normalização

Use normalização como análise de integridade e manutenção, não como meta estética: **normalize primeiro; desnormalize somente quando existir uma razão concreta e verificável**. “Performance” sem consulta, medição ou restrição conhecida não basta.

1. Liste atributos por entidade e a chave candidata que determina cada fato.
2. Registre dependências funcionais, por exemplo `codigo_disciplina → nome_disciplina`, somente quando tiverem fonte.
3. Mantenha cada fato em uma única origem e procure duplicação.
4. Se desnormalizar, registre origem autorizada, mecanismo de sincronização, risco aceito e evidência.

- **1FN:** valores atômicos; coleções/grupos repetidos normalmente precisam de outra tabela/linhas.
- **2FN:** em chave composta, atributo não-chave depende da chave inteira, não de parte dela.
- **3FN:** atributo não-chave não depende transitivamente de outro atributo não-chave; mantenha o fato com a entidade que o determina.

Procure anomalias de **inserção** (um fato exige inventar/repetir outro), **atualização** (o mesmo fato pode divergir) e **exclusão** (apagar relação apaga outro fato). Não decomponha mecanicamente: preserve informação, constraints e consultas autorizadas. Dependência ou semântica ausente é `Pending Decision`.
