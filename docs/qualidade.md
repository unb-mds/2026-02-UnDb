# Qualidade e verificações

## Frontend

Com as dependências instaladas, execute em `frontend/`:

```bash
npm ci
npm run lint
npm run typecheck
npm test
npm run build
npm run test:browser
npm run test:perfil
```

Os testes de navegador exigem build pronto e Edge/Chrome disponível; `BROWSER_PATH`
permite apontar o executável. As suítes com respostas controladas verificam estados
da interface; não substituem os jobs com API e PostgreSQL reais.

## Backend

Com Python 3.12 e ambiente virtual próprio, execute em `backend/`:

```bash
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
ruff format --check .
python -m unittest discover -s tests -v
```

Configure `DATABASE_URL` e `SECRET_KEY` no ambiente de testes. Integrações PostgreSQL
precisam de banco descartável migrado e `UNDB_INTEGRATION_TEST=1`; não aponte os runners
para produção ou para o banco de uma importação em andamento. Procedimentos adicionais
estão no [guia do frontend](https://github.com/unb-mds/2026-02-UnDb/blob/release/1.4.0/frontend/README.md) e nos módulos `tests.integration_*` do backend.

## Documentação

Na raiz:

```bash
pip install -r requirements-docs.txt
mkdocs build --strict
mkdocs serve
```

O GitHub Actions verifica a documentação nas PRs e publica o site ao integrar em `main`.
Confira também destinos dos links e imagens no README, que fica fora do build do MkDocs.

## Evidências e limites

- [Integração visual da 1.4](https://github.com/unb-mds/2026-02-UnDb/blob/release/1.4.0/frontend/docs/integracao-visual-211.md).
- [Linha de base de cobertura](estudos/cobertura-testes-issue-190.md).
- [Jornada integrada de comentários e moderação](estudos/validacao-integrada-issue-163.md).

Registros de estudos preservam o contexto e a data da execução. Um teste antigo aprovado
não certifica automaticamente outra versão, disponibilidade pública ou carga do SIGAA.
