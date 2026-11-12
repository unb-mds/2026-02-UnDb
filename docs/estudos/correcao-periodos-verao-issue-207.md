# Diagnóstico de períodos de verão — #207

Em 12/11/2026, após o piloto de Física 2026.2 (204 ofertas processadas),
consultas públicas sem banco reproduziram duas causas distintas de pendências.

- O perfil de Rendisley foi encontrado, mas o período `2025.4` fez o parser
  rejeitar todo o histórico. O usuário confirmou que `.4` representa verão.
  A correção preserva esse período literalmente e mantém comparação exata
  de período, código e identificador do componente para associar identidades.
- A busca por Vinicius Ricardo Marques de Souza respondeu explicitamente
  que nenhum docente foi encontrado. A ausência de um contador numérico era
  tratada como erro. A mensagem explícita agora representa zero resultados;
  resposta desconhecida ou contagem divergente continua inconclusiva.

Com a correção do período, nove perfis foram consultados e lidos com sucesso:
Rendisley Aristoteles dos Santos Paiva, Vinicius de Carvalho Rispoli,
Luiz Antonio Ribeiro Junior, Alessandra Ferreira Albernaz, Eberth de Almeida
Correa, Marcello Ferreira, Vanessa Carvalho de Andrade, Alexandre Cavalheiro
Dias e Andre Luis Miranda de Barcellos Coelho. Sete desses perfis continham
linhas de período `.4`. Vinicius Ricardo foi o décimo nome consultado e teve
zero resultados na busca global por esse nome.

Isso comprova leitura dos perfis naquele momento, não associação de todas as
ofertas nem ausência de homônimos. Não explica retrospectivamente toda falha
de rede do piloto, pois o coletor não preservou a causa original das exceções.
Nenhuma conexão ou escrita no banco foi realizada nesta verificação.

Validação local: 35 testes de identidade e importação, 34 aprovados e um
dependente de PostgreSQL ignorado; Ruff e `git diff --check`. Os testes cobrem
histórico misto, preservação de `.4`, ausência de equivalência com `.1`/`.2`,
ano isolado e classificação de busca explicitamente vazia.

Após integrar/publicar a correção, reprocessar o piloto para atualizar as
pendências não decididas. Não é necessário apagar o catálogo por essas causas.
União de UUIDs antigos continua sujeita ao procedimento administrativo próprio.
