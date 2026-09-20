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
- `erros`, incluindo divergência de contagem, falha de coleta, falha de banco ou oferta que
  o modelo atual não representa.

O código de saída é `0` para sucesso integral e `1` quando existe qualquer falha. A rotina
da #26 pode armazenar o JSON e usar o código de saída para monitoramento, sem precisar
interpretar texto livre.

## Limitações explícitas

- Ofertas sem docente ou com múltiplos docentes são registradas como falha e não são
  persistidas. Alterar essa regra exige a decisão de modelo ainda pendente.
- Professores são reconhecidos por nome e departamento; homônimos permanecem uma limitação
  conhecida da fonte pública.
- A reimportação reutiliza disciplina por código, professor por nome/departamento e turma
  por disciplina/professor/semestre. O modelo atual não mantém um identificador público
  estável da turma.
- Falhas da importação não derrubam a API, pois o processo não é executado por endpoints.

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

A consulta pública real do CIC em 2026.2 reportou e extraiu 108 ofertas. Dessas, 98 tinham
exatamente um docente e foram processadas; nove tinham dois docentes e uma tinha três, totalizando
dez falhas isoladas conforme a limitação de modelo já registrada.

Para verificar o encadeamento sem alterar um banco do projeto, os dados reais foram gravados
em um banco temporário em memória e consultados pela mesma camada de serviço usada pela API:

- 46 professores, 51 disciplinas e 83 relações de turma distintas foram gravadas;
- a consulta pública retornou a professora `MARIA EMILIA MACHADO TELLES WALTER` e a disciplina
  `CIC0002` a partir dos registros persistidos;
- as 98 ofertas aceitas resultaram em 83 relações porque o modelo validado identifica turma por
  disciplina, professor e semestre, sem armazenar o código textual da turma do SIGAA.

Essa verificação confirma coleta, gravação e consulta com dados reais, mas não substitui a
execução em PostgreSQL. A máquina usada não tinha uma instância PostgreSQL configurada; as
migrações e a consistência do modelo devem ser verificadas no check `Backend` do Pull Request.

## Limitação atual

A importação registra falhas individuais quando uma oferta possui mais
de um docente. O modelo atual exige exatamente um docente por turma.

Essas ofertas não interrompem o processamento das demais. A quantidade
extraída, a quantidade processada e as mensagens de erro ficam registradas
na tabela `importacao_execucoes`.

## Execução periódica

**Mecanismo definido:** cron do sistema operacional, com periodicidade diária.

Script: `scripts/importar-sigaa-cron.sh`. Ele ativa o venv do projeto, entra em
`backend/` e chama o comando de importação já documentado acima.

Entrada de crontab utilizada:0 3 * * * /caminho/absoluto/para/2026-02-UnDb/scripts/importar-sigaa-cron.sh >> /tmp/importacao-sigaa.log 2>&1


Para configurar: `crontab -e` e adicionar a linha acima, ajustando o caminho absoluto
do repositório. O log fica disponível em `/tmp/importacao-sigaa.log` (ou outro caminho
definido no redirecionamento).

**Nota:** a frequência diária (03:00) foi escolhida para evitar sobrecarga
desnecessária na fonte pública do SIGAA. Uma frequência de produção definitiva pode
ser revisada pelo time; ver pendência na Issue #26.

### Evidência de execução repetida em 20/09/2026

Duas execuções manuais do script, simulando o disparo do cron, foram realizadas em
sequência para validar repetibilidade e idempotência:

| Execução | Início (UTC) | Fim (UTC) | Ofertas processadas | Falhas |
|---|---|---|---|---|
| 1 | 15:41:08 | 15:41:13 | 98 | 10 (múltiplos docentes) |
| 2 | 15:45:07 | 15:45:11 | 98 | 10 (múltiplos docentes) |

Após as duas execuções, a contagem de registros persistidos permaneceu estável:
46 professores, 51 disciplinas, 83 turmas — confirmando que a reimportação reaproveita
registros existentes em vez de duplicá-los. As 10 falhas por execução são a limitação
já conhecida de turmas com múltiplos docentes (ver seção "Limitações explícitas").