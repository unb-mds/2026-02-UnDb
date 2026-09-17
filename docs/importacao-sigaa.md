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

### Evidência executada em 17/09/2026

A consulta pública real do CIC em 2026.2 reportou e extraiu 108 ofertas. Em 17/09/2026, o
modelo N:N atual persistiu em memória as 108: 98 tinham exatamente um docente, nove tinham
dois e uma tinha três. Foram preservados 119 vínculos, 57 disciplinas e 119 identidades
docentes provisórias, sem perda das dez ofertas multidocentes.

Para verificar o encadeamento sem alterar um banco do projeto, os dados reais foram gravados
em um banco temporário em memória e consultados pela mesma camada de serviço usada pela API:

- o modelo anterior havia gravado apenas 46 professores, 51 disciplinas e 83 relações de
  turma, pois descartava ofertas multidocentes e não preservava o código textual da turma;
- a consulta pública retornou a professora `MARIA EMILIA MACHADO TELLES WALTER` e a disciplina
  `CIC0002` a partir dos registros persistidos;
- as 98 ofertas aceitas resultaram em 83 relações porque o modelo validado identifica turma por
  disciplina, professor e semestre, sem armazenar o código textual da turma do SIGAA.

A execução real em memória valida a fonte e a representação, mas não substitui PostgreSQL.
Antes de fechar a #25, executar a importação real nesse banco, repeti-la para verificar
ausência de duplicatas e validar a migração `upgrade/downgrade/upgrade`. As consultas do
contrato OpenAPI, a idempotência e os casos de falha são cobertos pela suíte determinística.
