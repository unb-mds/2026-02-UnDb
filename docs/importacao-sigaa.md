# Importação persistida do SIGAA

Este procedimento integra a coleta HTTP validada na Issue #23 à persistência da Issue #25.
A importação roda fora da API: nenhum endpoint consulta o SIGAA em tempo real.

## Pré-requisitos

1. Configure `backend/.env` a partir de `backend/.env.example`.
2. Garanta que o PostgreSQL indicado por `DATABASE_URL` esteja acessível.
3. Aplique as migrações com `alembic upgrade head`.
4. Execute os comandos abaixo a partir de `backend/`.

## Executar

Cada `--departamento` usa o formato `CODIGO=ROTULO_SIGAA`. A opção pode ser repetida;
uma falha de coleta ou persistência em uma unidade não impede a execução das seguintes.

```bash
python -m app.commands.importar_sigaa \
  --departamento "CIC=DEPTO CIÊNCIAS DA COMPUTAÇÃO" \
  --ano 2026 \
  --periodo 2
```

Exemplo com mais de uma unidade:

```bash
python -m app.commands.importar_sigaa \
  --departamento "CIC=DEPTO CIÊNCIAS DA COMPUTAÇÃO" \
  --departamento "MAT=DEPTO MATEMÁTICA" \
  --ano 2026 \
  --periodo 2
```

O rótulo deve identificar uma opção atual do formulário público do SIGAA. A enumeração e
a cobertura de todas as unidades permanecem nas Issues #26/#27.

## Contrato de resultado para a Issue #26

Depois que a configuração é carregada e a execução iniciada, o comando imprime JSON. O campo
de execução `sucesso` é `true` somente quando todas
as unidades terminam sem erro. Cada item de `departamentos` contém:

- `sucesso` da unidade;
- `total_reportado` pelo SIGAA;
- `ofertas_extraidas` e `ofertas_processadas` (inclui registros já existentes que foram
  reutilizados na reimportação);
- `estado` (`sucesso`, `parcial` ou `falha`);
- `erros`, incluindo divergência de contagem, falha de coleta ou falha de banco.

O código de saída é `0` para sucesso integral e `1` quando existe qualquer falha. A rotina
da #26 pode armazenar o JSON e usar o código de saída para monitoramento, sem precisar
interpretar texto livre.

## Semântica da sincronização

- ofertas sem docente são persistidas com zero vínculos; ofertas com múltiplos docentes
  preservam todos os vínculos;
- como a página pública não fornece SIAPE, cada docente recebe identidade provisória por
  ocorrência de turma. Homônimos não são unidos silenciosamente e uma reconciliação futura
  pode confirmar a identidade;
- turma é identificada por fonte, unidade, período, componente e código textual. Uma troca
  de docente atualiza os vínculos sem duplicar a turma;
- somente uma coleta completa, com a contagem validada e sem erro de oferta, marca como
  inativas as turmas ausentes. Execução parcial preserva todos os registros anteriores;
- falhas da importação não derrubam a API, pois o processo não é executado por endpoints.

## Verificações

Testes determinísticos, incluindo o fluxo extração → persistência → consulta com o exemplo
real capturado na POC:

```bash
python -m unittest discover -s tests -v
```

Consulta manual à fonte pública, sem persistência:

```bash
python -m app.scrapers.sigaa_poc --real
```

A execução persistida real usa o primeiro comando deste documento e depende da
disponibilidade do SIGAA e do PostgreSQL configurado.

### Evidências executadas em 17 e 18/09/2026

A consulta pública real do CIC em 2026.2 reportou e extraiu 108 ofertas. A composição observada
foi de 98 ofertas com exatamente um docente, nove com dois e uma com três, totalizando 119
vínculos, 57 disciplinas e 119 identidades docentes provisórias. O modelo atual identifica a
turma pela origem, unidade, período, disciplina e código textual da turma, preservando todos os
docentes associados às dez ofertas multidocentes.

Em 17/09/2026, a validação de conclusão da Issue #25 executou duas importações consecutivas dos
dados reais no mesmo PostgreSQL 16. As duas execuções retornaram 108 ofertas e mantiveram as
contagens estáveis em uma unidade, 57 disciplinas, 108 turmas, 119 docentes provisórios e 119
vínculos, sem duplicatas. A migração dos dados legados e uma consulta pela API também foram
validadas nessa execução.

Em 18/09/2026, a fonte e o comportamento determinístico foram revalidados sem alterar o banco
do projeto:

Essa verificação confirma coleta, gravação e consulta com dados reais, mas não substitui a
execução em PostgreSQL. A máquina usada não tinha uma instância PostgreSQL configurada; as
migrações e a consistência do modelo devem ser verificadas no check `Backend` do Pull Request.

## Limitação atual

A importação registra falhas individuais quando uma oferta possui mais
de um docente. O modelo atual exige exatamente um docente por turma.

Essas ofertas não interrompem o processamento das demais. A quantidade
extraída, a quantidade processada e as mensagens de erro ficam registradas
na tabela `importacao_execucoes`.
- a POC consultou novamente o SIGAA público e obteve `total_reportado=108` e
  `ofertas_extraidas=108` para CIC em 2026.2;
- a suíte backend completa passou com 51 testes;
- a primeira oferta extraída continuou sendo o componente `CIC0002`.

A checagem de 18/09 é somente leitura e complementa, sem substituir, a evidência de
persistência e idempotência em PostgreSQL registrada em 17/09 na Issue #25.
