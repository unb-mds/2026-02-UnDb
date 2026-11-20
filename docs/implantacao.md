# Implantação e operação do UnDb

Este roteiro organiza a documentação existente da implantação. Fonte: [hospedagem](hospedagem.md),
[inicialização no Render](inicializacao-render.md), [arquitetura](arquitetura.md) e contratos
atuais na base `df854bf`. Não é evidência de novo deploy ou revalidação dos painéis.

## Componentes documentados

| Componente | Implantação registrada | Documento de referência |
|---|---|---|
| Site Next.js | Vercel, domínio `undb.app.br` | [Hospedagem](hospedagem.md) |
| API FastAPI | Render, domínio `api.undb.app.br` | [Inicialização](inicializacao-render.md) |
| Banco PostgreSQL | Neon | [Papel da API e migrations](acesso-postgresql-api.md) |
| E-mail transacional | Resend | [Hospedagem](hospedagem.md) |
| Domínio e DNS | Registro.br | [Hospedagem](hospedagem.md) e [continuidade](continuidade-operacional.md) |
| Importação SIGAA | Processo Python / rotina conforme configuração do operador | [Operação da importação](operacao-importacao-sigaa.md) |

## Sequência para o operador autorizado

1. Identificar a versão e a branch que serão publicadas. Distinguir PR, prévia de hospedagem,
   merge, tag e deploy; nenhum deles comprova os demais por si só.
2. Conferir acessos e variáveis privadas nos mecanismos dos provedores. Valores secretos
   não devem ir para README, screenshots ou issues. URLs públicas e configuração estão
   no guia de hospedagem.
3. Preparar o PostgreSQL e os papéis conforme o documento de acesso. A conexão da API
   tem privilégios diferentes da conexão administrativa de migrations. Não executar
   migration contra banco real sem verificar o destino e a autorização operacional.
4. No fluxo hospedado documentado, o inicializador executa `alembic upgrade head` antes
   de iniciar Uvicorn. Falha de migration impede subir a API; `/health` não certifica
   toda a jornada nem, isoladamente, acesso ao banco.
5. Configurar o frontend com URL pública da API, origens autorizadas e variáveis indicadas.
   Variáveis `NEXT_PUBLIC_*` são incorporadas ao build e não podem conter segredos.
6. Validar a versão publicada, navegação, acesso, confirmação de e-mail e um percurso
   principal em ambiente apropriado. Usar dados sintéticos e distinguir console de
   entrega externa de e-mail.
7. Conferir workers/rotinas de descarte e atualização, flags e permissões realmente
   ativados. A execução local do Compose não comprova a execução contínua hospedada.
8. Registrar resultados e limitações e manter plano de reversão/recuperação correspondente
   à infraestrutura disponível. Não prometer backups ou recuperação ainda não verificados.

## Operações com controles próprios

- [Canal de solicitações](canal-titulares.md): ativação, retenção e permissões específicas.
- [Moderação com IA](moderacao-ia.md): flags, envio de texto e revisão humana.
- [Sessões, abuso e logs](seguranca/revisao-sessoes-abuso-logs-issue-266.md): controles e limites da revisão.
- [Continuidade operacional](continuidade-operacional.md): responsáveis, acessos e lacunas.
- [#267 — recuperação](https://github.com/unb-mds/2026-02-UnDb/issues/267): roteiro e teste isolado de restauração.

Planos, regiões, contratos, permissões e disponibilidade devem ser conferidos pelo
operador; registros históricos não provam a configuração atual. Esta entrega documental
não mudou infraestrutura, conta, permissão, custo ou flag de produção.
