# Ensaio do modelo híbrido — issue #207

Estado: proposta testada por simulação; sem alteração em produção e sem implementação no importador.

Fonte: solicitação do usuário em 13/11/2026 para testar perfil institucional quando disponível e nome + unidade na ausência de perfil encontrado. A unidade usada é a unidade da oferta, não uma lotação funcional presumida.

## Base e método

Backup de 12/11/2026 às 22:22:10, restaurado no container local `undb-restore-2bfb6de2`, banco `undb_restore`, após o ensaio anterior de reavaliação seletiva e consolidação. Essa base local tem 7.849 ocorrências aplicadas e 428 pendentes; produção estava com 7.674 aplicadas e 603 pendentes na última evidência do usuário. Portanto, os números abaixo não são uma leitura atual de produção.

Leitura das tabelas locais e agrupamento em memória, resolvendo correspondências já existentes. Nenhuma escrita no banco. O fallback considera somente PENDENTE/PERFIL_AUSENTE sem decisão humana; não converte consulta inconclusiva, múltiplos perfis ou disciplina incompatível em ausência de perfil.

## Resultado

- 387 ocorrências sem perfil encontrado: 263 grupos por nome + unidade.
- 69 grupos possuem mais de um registro; redução projetada de 124 registros.
- Zero grupos com mais de uma identidade institucional conhecida e zero colisões entre as avaliações existentes.
- Os outros 41 casos permanecem fora do fallback: 23 com múltiplos perfis, 15 com disciplina não confirmada, 3 com consulta inconclusiva.
- Nome normalizado retira acentos, ajusta caixa e espaços; comparar também a chave literal evita atribuir o ganho exclusivamente à normalização.

Exemplos: Ana Clara Gonçalves da Costa 9 → 1; cada um dos quatro nomes informados de CEM 5 → 1; Cosme Roberto Moreira da Silva 4 → 2 por atuar em duas unidades; Vinicius Ricardo Marques de Souza permanece 1. Essas associações por nome são heurísticas, não comprovação individual de identidade.

Marilucia tem perfil público 404588 com FMD0032, FMD0046 e FMD0052 em 2026.2, confirmado na consulta anterior. Deve seguir pelo caminho institucional, embora não seja encontrada na busca pública por nome. Os seis registros dela estão incluídos no cenário bruto de 387, mas não devem permanecer como fallback após registrar essa evidência.

## Verificações de comportamento

Protótipo em memória verificou: reutilização do cadastro na mesma unidade, idempotência do agrupamento, mesmo perfil entre unidades, preservação de perfis distintos e reprodução da falha com duas pessoas diferentes de mesmo nome na mesma unidade sem perfil. Cinco verificações passaram. Isso valida o comportamento da regra, não uma implementação de produção.

## Limites e implantação futura

Ausência de conflitos observados não demonstra ausência de homônimos. Nome + unidade mantém a mesma pessoa separada entre unidades. Se um perfil surgir depois, a identidade provisória precisa poder ser promovida sem novo cadastro, preservando UUID e avaliações; caso múltiplas identidades conhecidas disputem a mesma chave, encaminhar para moderação. Decisões humanas de manter separados devem prevalecer. Essas condições ainda precisam de implementação e testes de integração antes de publicar.

Artefatos operacionais locais: `/private/tmp/undb-testar-hibrido.py`, `/private/tmp/undb-testar-hibrido-casos.py` e `/private/tmp/undb-hibrido-resultado.json`. Não versionar a exportação de dados locais.

## Implementação autorizada após o ensaio

Depois de receber os resultados acima, o PO aceitou explicitamente o risco residual
e autorizou implementar o híbrido e otimizar a consolidação. A condição inicial
“sem implementação” descreve somente o ensaio anterior. Esta alteração implementa
a chave local persistente, a promoção posterior a perfil e o processamento por grupo.

Verificações da implementação em 13/11/2026:

- Suíte completa sobre a develop atual: 249 testes, 247 aprovados e dois específicos
  de PostgreSQL ignorados no modo SQLite. Os testes dirigidos são executados também
  no PostgreSQL descartável, incluindo contenção real, sem esses skips.
- Migrations de banco vazio até `20261113_01`, downgrade da tabela vazia, nova subida
  e `alembic check` sem divergência. Downgrade com associação local é recusado.
- Lint Python e formatação; lint do arquivo de interface alterado.
- Prévia real do comando com o perfil 404588 da Marilucia: seis ocorrências
  compatíveis em 2026.2, nenhuma ignorada. Apenas leitura do SIGAA e cópia local.

Comparação com o código anterior no mesmo PostgreSQL local, mesmos 25 grupos
iniciais do backup anterior à consolidação, contando statements via SQLAlchemy:

| Implementação | Statements | Tempo local |
|---|---:|---:|
| Anterior (hotfix 1.3.1) | 2.287 | 0,298 s |
| Otimizada | 651 | 0,116 s |

Redução de aproximadamente 72% dos statements. Os números incluem o custo de
validação e escrita; a versão nova confirma cada grupo, enquanto a anterior fazia
um único commit ao final. Não há simulação artificial de latência nesses tempos.

Ensaio completo em outra cópia do backup original, sem a reavaliação seletiva
prévia: 2.084 grupos institucionais / 5.059 ocorrências aplicados em 8,269 s,
54.185 statements, nenhum bloqueio e duas avaliações preservadas. O fallback
subsequente processou 256 grupos em 0,720 s, também sem bloqueios. Fila dessa cópia:
8.049 aplicadas e 228 pendentes. Essa base é diferente da projeção inicial de
7.849/428 após reavaliação seletiva; não misturar denominadores nem apresentar
qualquer desses resultados como nova leitura de produção.

Tempo de rede, recurso do servidor e tamanho dos grupos afetam a duração real.
O ganho medido não permite prometer oito segundos em produção. Nenhuma consolidação
ou migration foi executada em produção nesta implementação.
