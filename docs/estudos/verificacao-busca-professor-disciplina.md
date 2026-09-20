# Verificação da busca de professor e disciplina — Issues #44/#45

**Executado em:** 17/09/2026, com backend e frontend reais rodando (não mock, não teste
unitário isolado) contra o PostgreSQL populado pela importação real do SIGAA (CIC/2026.2:
119 professores, 57 disciplinas, 108 turmas).

**Objetivo:** confirmar que a busca por nome de professor (#44) e por nome/código de
disciplina (#45) devolve os dados certos do banco, incluindo o caso que motivou a #25
(turmas com mais de um docente), e que o frontend consome esse contrato corretamente.

## Ambiente

- Backend: `uvicorn app.main:app`, `DATABASE_URL` apontando para o Postgres local já
  migrado (`alembic upgrade head`, revisão `20260917_02`), `CORS_ORIGINS` liberando a
  origem do frontend.
- Frontend: `next dev`, `NEXT_PUBLIC_API_URL` apontando para o backend acima.
- Evidência coletada via `curl` direto nos dois servidores — sem navegador gráfico
  disponível neste ambiente de verificação (falta lib de sistema para o Chromium headless,
  sem acesso a `sudo` para instalar). Onde a checagem depende de execução de JavaScript no
  navegador (a busca em si, que roda client-side), o teste cobre o contrato HTTP completo
  — incluindo os headers de CORS que o navegador exigiria — mas não uma captura de tela
  real. Isso é uma lacuna explícita, não escondida: ver seção "O que ainda falta".

## 1. Busca de professor por nome (#44)

| Caso | Termo | Resultado |
|---|---|---|
| Nome completo | `MARIA EMILIA MACHADO TELLES WALTER` | 3 registros — mesma pessoa, 3 identidades provisórias (ver nota sobre homônimos) |
| Nome parcial, minúsculo | `emilia` | Mesmos 3 registros |
| Termo **com acento**, nome guardado **sem acento** | `emília` | Mesmos 3 registros — confirma que a normalização (`normalizar_busca`) ignora acento nos dois lados da comparação |
| Termo sem correspondência | `zzznaoexiste` | `[]` — lista vazia, sem erro |

Requisição de exemplo (nome parcial, minúsculo):

```
GET /api/professores?nome=emilia
```
```json
[
  {"id":"2c171339-f5d0-4342-8968-e26599f21799","nome":"MARIA EMILIA MACHADO TELLES WALTER","departamento":"CIC","siape":null,"identidade_confirmada":false},
  {"id":"50950e64-e8bf-467e-ab1f-6f756365d139","nome":"MARIA EMILIA MACHADO TELLES WALTER","departamento":"CIC","siape":null,"identidade_confirmada":false},
  {"id":"c40d384b-b988-4802-834a-2e9d5b5ef26f","nome":"MARIA EMILIA MACHADO TELLES WALTER","departamento":"CIC","siape":null,"identidade_confirmada":false}
]
```

**Sobre os 3 registros para a mesma pessoa:** não é duplicação por bug — é o comportamento
deliberado da ADR 07 (`docs/arquitetura.md`). A fonte pública do SIGAA não expõe SIAPE, então
cada ocorrência sem identificador externo vira uma identidade provisória própria, e homônimos
nunca são unidos automaticamente. Um professor que aparece em turmas de semestres/coletas
diferentes pode gerar mais de uma identidade até uma reconciliação explícita (fora do escopo
das #44/#45).

## 2. Busca de disciplina por nome ou código (#45)

| Caso | Termo | Resultado |
|---|---|---|
| Código exato | `CIC0002` | 1 registro: `FUNDAMENTOS TEÓRICOS DA COMPUTAÇÃO` |
| Código parcial | `CIC000` | 5 registros (`CIC0002`, `CIC0003`, `CIC0004`, `CIC0005`, `CIC0007`) |
| Nome parcial, sem acento no termo | `programacao` | 6 registros, todos com "programação"/"programacao" no nome real (com e sem acento na fonte) |
| Termo sem correspondência | `zzznaoexiste` | `[]` |

O frontend busca nome e código em paralelo e mescla o resultado (`buscarDisciplinas`, em
`frontend/src/lib/services/disciplinas.ts`), porque o backend trata os dois filtros como E
lógico, não OU — decisão registrada no commit que introduziu a função.

## 3. Buscar professor a partir da disciplina (o outro sentido da busca)

Fluxo: busca a disciplina `CIC0004`, pega as turmas, confere que os professores batem com
uma busca direta por nome de um deles — e o caminho inverso também.

```
GET /api/disciplinas/3703661c-c330-412a-ab92-ac2b3f2b7dda/turmas
```

12 turmas, incluindo duas com mais de um docente — exatamente o cenário que a #25 corrigiu:

| Turma | Semestre | Docente(s) |
|---|---|---|
| 02 | 2026.2 | JOAO GABRIEL ROSSI DE BORBA, YURI COSSICH LAVINAS |
| 12 | 2026.2 | NILTON CORREIA DA SILVA, FABRICIO ATAIDES BRAZ |
| (demais 10 turmas) | 2026.2 | 1 docente cada |

Conferência cruzada com `JOAO GABRIEL ROSSI DE BORBA` (id `2253672e-bcdc-46ca-ba3e-b4fe24f68d74`):

```
GET /api/professores/2253672e-bcdc-46ca-ba3e-b4fe24f68d74/disciplinas
```
```json
[{"id":"3703661c-...","codigo":"CIC0004","nome":"ALGORITMOS E PROGRAMAÇÃO DE COMPUTADORES", ...}]
```

`CIC0004` aparece — os dois sentidos da busca (disciplina → professores, professor →
disciplinas) concordam sobre o mesmo vínculo.

## 4. Frontend consumindo o mesmo dado

As páginas de detalhe (`/professores/[id]`, `/disciplinas/[id]`, componentes de servidor)
foram checadas direto pelo HTML renderizado:

- `/professores/2253672e-bcdc-46ca-ba3e-b4fe24f68d74` → `<h1>JOAO GABRIEL ROSSI DE BORBA</h1>`,
  lista `CIC0004 — ALGORITMOS E PROGRAMAÇÃO DE COMPUTADORES`.
- `/disciplinas/3703661c-c330-412a-ab92-ac2b3f2b7dda` → `<h1>ALGORITMOS E PROGRAMAÇÃO DE
  COMPUTADORES</h1>`, lista os 14 vínculos de professor das 12 turmas, incluindo as duas
  multidocentes.

Nenhum erro nos logs do backend nem do frontend durante toda a bateria de testes acima.

## 5. O que ainda falta

- **Sem navegador real testado.** Tudo acima prova o contrato HTTP e a renderização
  server-side; a interação client-side (digitar e ver a lista atualizar) não foi vista
  visualmente. O comportamento é inferido com alta confiança (a lógica de fetch, os estados
  de carregamento/erro e o CORS já confirmado por header foram todos verificados
  separadamente), mas "inferido com confiança" não é a mesma coisa que "visto rodando".
- **Paginação.** Nenhum dos endpoints de listagem pagina resultado — `specs.md §11` já
  registra isso como decisão em aberto, não inventar limite sem issue própria. Com 119
  professores reais e uma busca ampla o suficiente, a lista pode ficar grande.
- **Debounce sem teste automatizado.** O comportamento de esperar 300ms antes de buscar
  está implementado e foi validado manualmente contra a API real, mas não há teste de
  frontend (unitário ou e2e) cobrindo isso — não existe suíte de teste de frontend no
  projeto ainda.
