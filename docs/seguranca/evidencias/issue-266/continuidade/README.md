# Evidências da continuidade da #266

Data: 16/11/2026. Originais `5e5ab50` e `dbde820` preservados. Base remota
`757b12c`, integrada apenas localmente em `3a1d46d`; correções em `9a186d2`.
Nada deste pacote foi publicado por push/PR, integrado remotamente ou implantado.

## Resultados observados

| Verificação | Resultado |
|---|---|
| Suíte antes das correções | 334 testes; duas falhas de ofensas por encoding cp1252, dois erros de cleanup SQLite; dois skips opcionais PostgreSQL |
| Corpus antigo com `PYTHONUTF8=1`, antes da correção | 13 testes aprovados; evidência da causa de encoding, sem mudar política |
| Suíte final Python 3.14.7/Windows | 341 testes; sem falha; dois skips PostgreSQL |
| Suíte Python 3.12.16/Windows sem PostgreSQL | 338 testes; sem falha; dois skips; antes dos três testes adicionais do canal |
| Suíte final Python 3.12.16/PostgreSQL 16.16 | **341 testes aprovados, sem skips**; inclui contenção real de reconciliação/identidade em banco exclusivo |
| Cobertura Python 3.12/PostgreSQL | 87% de statements/branches combinados informados por coverage; 3.993 statements, 848 branches; não é novo gate de aprovação |
| Segurança #266 + cache #277 + canal | 30 testes aprovados: 22 de segurança, um de cache herdado e sete do canal |
| HTTP de autenticação com DB migrado e papel sem DDL | Cadastro, confirmação/uso único, login/cookie seguro, CSRF, recuperação, invalidação dos outros links e sessões após troca, logout: aprovado; somente e-mail substituído |
| Migrações e legado | Upgrade/check/downgrade/upgrade; seed legado, upgrade/verificação/check, downgrade/verificação/upgrade: todos aprovados |
| Integrações HTTP avaliação/moderação existentes | Aprovadas; banco real migrado, concorrência e autorizações; sem publicar dados sintéticos em ambiente público |
| Ruff/formatação/compileall | Aprovados; 160 arquivos backend formatados; script de homologação também verificado |
| Frontend | 83 testes, lint, tipos e build Webpack aprovados após integração |
| Navegador | Headers/metadados de confirmação/recuperação aprovados; 18 combinações RF24 aprovadas, API fictícia e perfil temporário |
| Dependências | 35 pacotes runtime Python, zero advisories conhecidos; npm 14 nós afetados/17 advisories, sem alteração de versões |
| Busca limitada de segredos no histórico alcançável | 2.384 blobs, zero correspondências nos padrões selecionados; não certifica ausência de segredos |

## Artefatos e reprodução

- [Comandos e resultados agregados](verificacoes.json).
- [Etapas PostgreSQL e exit codes](postgres-resultados.json).
- [Runtime Python resolvido](python-resolvido.json) e [entrada do scanner](python-resolvido.txt),
  que **não** é um lock aprovado; [resultado PyPI](python-audit.json).
- [Lock npm inventariado](frontend-resolvido.json), [audit npm](npm-audit.json) e
  [metadados oficiais dos 17 advisories](advisories-npm.json), sem instruções de exploração.
- [Hashes dos manifests](hashes-fontes.json), iguais aos do snapshot anterior.
- [Busca limitada de segredos](segredos-resultado.json), sem valores encontrados/expostos.

Use o Python da venv correspondente. Comandos gerais têm cwd `backend`; frontend
tem cwd `frontend`. Lint, build e documentação mantêm os comandos já usados pelo
projeto; o build executado foi `npm run build -- --webpack`. O CI permanece com seu
comando original e **não foi executado para esta branch local**.

O [script de homologação](../homologar_postgres.py) exige um cluster **local
descartável** iniciado pelo operador, senha sintética em arquivo privado e nomes de
banco/roles ainda ausentes. Ele não baixa nem inicia banco, não lê URLs de produção,
substitui as URLs dos subprocessos, cria os bancos exclusivos e remove somente seus
recursos. Não executar contra cluster compartilhado. Exemplo a partir da raiz:

```text
python docs/seguranca/evidencias/issue-266/homologar_postgres.py --confirm-disposable-local --port 55466 --password-file .audit-tools/pg-pass.txt
```

O arquivo de senha gerado fica ignorado pelo Git e não está neste pacote. O cluster
foi PostgreSQL portátil 16.16-1, origem oficial EDB indicada no relatório;
SHA-256 do ZIP: `5c0d06f3d26a929ecb36dd931409f1e51a4181355794a259b90aae8bffc57a9f`.
Não instalado como serviço, não exposto além de loopback. Bancos e roles do ensaio
foram removidos ao final. O cluster foi encerrado após os testes.

Para novos inventários, preserve o diretório histórico usando os argumentos novos:

```text
python docs/seguranca/evidencias/issue-266/inventariar_dependencias.py --output-dir DIRETORIO_NOVO
python docs/seguranca/evidencias/issue-266/verificar_segredos.py --output DIRETORIO_NOVO/segredos-resultado.json
```

Instalações isoladas: runtime 3.12 via uv/python-build-standalone; dependências pelos
requirements já existentes; packaging/pip-audit para auditoria. Nenhuma dependência
de produto, schema, limite, flag de produção ou política jurídica foi alterada.

## Limites

PostgreSQL Windows e Python 3.12 local não homologam o runner Linux do CI nem o Neon.
As fixtures da suíte usam SQLite salvo os testes explicitamente configurados para
PostgreSQL; o fluxo HTTP adicional usa o DB migrado e conexão da aplicação sem DDL.
Os ensaios de avaliação/moderação usam HTTP local real; os testes de frontend citados
usam API fictícia, não comprovam a configuração do ambiente publicado.

Não foram realizados carga, força bruta, exploração pública, envio real a provedores,
restauração de backup, inspeção dos painéis, configuração de CDN/proxy, rotação de
segredos ou teste destrutivo em banco compartilhado. Logs brutos locais de execução
não foram versionados; apenas resultados agregados e inventários sem dados de usuários.

Permanecem pendentes a política de limites/distribuição/falha, atualização dirigida
de dependências com destino/responsável pelo PO, configuração operacional com Nicolas,
validação jurídica de bases/retenção/acessos/descarte e eventual publicação autorizada.
O [relatório](../../../revisao-sessoes-abuso-logs-issue-266.md) contém o roteiro e os
consumidores de cada insumo. A #266 permanece sem aceite integral.
