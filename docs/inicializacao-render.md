# Inicialização da API no Render

A [PR #209](https://github.com/unb-mds/2026-02-UnDb/pull/209) incluiu o módulo
`app.commands.iniciar_servidor` para resolver os deploys que falhavam com status
127 ao interpretar uma sequência de shell inteira como nome de programa.

No painel, **Docker Command** deve conter exatamente:

```text
python -m app.commands.iniciar_servidor
```

O comando aplica `alembic upgrade head` antes do Uvicorn, valida `PORT` e não
inicia o servidor se a migração falhar. Usa `os.execv` para entregar sinais ao
processo HTTP. O CMD original do Dockerfile continua preservado para uso local;
o override é configuração explícita do serviço hospedado.

Configuração de caminhos, variáveis, driver Neon e diagnóstico estão no
[guia de hospedagem](hospedagem.md#api-no-render-e-conexao-neon).
Health `/health` verifica apenas o processo, e não o banco. Os três testes de
inicialização conferem ordem, falha de migração e porta inválida; o sucesso real
do deploy e das migrações foi observado posteriormente na v1.1.0 pelo PO.

Antes de atualizar uma base com dados, obter backup privado e verificar sua
recuperação. Reverter deploy não reverte schema; não fazer downgrade automático.
