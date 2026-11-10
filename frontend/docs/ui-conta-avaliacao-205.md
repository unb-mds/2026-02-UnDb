# Conta, avaliação e catálogo — revisão da PR #215

**Estado em 10/11/2026:** PR #215 integrada em `develop` (`f1f0d00`), incluindo a
revisão adicional `85eab6a`; #205 encerrada pelo PO. A versão pública v1.1.0 é
anterior. Fontes: critérios da #205, solicitação do PO de incluir nomes e
“Mostrar mais”, [tokens](ui-dark.md), [requisitos](../../docs/requisitos.md) e
[referência da #205](../../docs/referencias/ui-dark/issues/205.md).

## Conta e avaliação

- Login/cadastro em painel dark com padding responsivo, labels, autocomplete,
  limites de senha e mensagens preservados. Mostrar/ocultar senha tem área de
  toque, `aria-controls` e `aria-pressed`; opções mantêm `aria-current`.
- Confirmação mantém token, tentativa, erros e retorno seguro; painel informa
  `aria-busy`. Sucesso exige resposta HTTP, sem confirmação simulada.
- Destino professor/disciplina recolhível preserva contexto e `returnTo` seguro.
  Falha ao buscar detalhes não bloqueia autenticação.
- Formulário usa superfícies e ações comuns, sem nota inicial. Os cinco valores
  de Didática cabem em uma linha a 320 px, inclusive com scrollbar clássica,
  mantendo área mínima de 44 px. Dificuldade/Chamada continuam neutras.
- Comentário opcional, retirada e acompanhamento privado mantêm serviços/regras;
  redesenho de comentários/moderação pertence à #206.

Sessão, permissões, escalas, agregações, mínimo de três avaliações, anonimato e
proteção contra envio repetido não foram redefinidos por essa integração visual.

## Nome institucional e identidade preservada

A revisão complementar alterou a API de forma aditiva: respostas de professores,
disciplinas, agregado e comparação admitem `departamento_nome` opcional/nulo.
A origem é `Unidade.nome`, associada ao código e à fonte SIGAA por relacionamento
ORM somente de leitura, carregado junto à entidade. Sem nova coluna, migração,
escrita ou mapa manual de siglas; registros legados sem unidade continuam
retornando. `departamento` permanece como identidade e filtro.

Serviços frontend mapeiam para `departamentoNome`; `src/lib/unidade.ts` prefere
nome não vazio/não numérico, preserva código textual e usa `Unidade <código>`
quando só há código numérico. Home, catálogo, buscas, perfil, disciplina,
comparação e contexto da avaliação usam o helper. A correção não une docentes
homônimos/provisórios: reconciliação de identidade continua na #207.

## Expansão do catálogo

`ListaProgressiva` mostra inicialmente 12 disciplinas e acrescenta 12 por clique.
As opções mostram “Todas” e até oito unidades; “Mostrar mais unidades” acrescenta
oito. A unidade selecionada permanece visível. Trocar filtro reinicia o limite;
os códigos continuam na URL e recarga/histórico preservam a seleção.

A expansão anuncia contagem e move foco ao primeiro link novo, sem exibir botão
após o fim. A API entrega a coleção completa: é apresentação progressiva no
cliente, não paginação de rede ou solução de desempenho do importador.

## Evidências e limites

Na revisão adicional em Windows, Python 3.12, Node 24.22.1 e Edge headless:

| Verificação | Resultado da PR #215 |
|---|---|
| Backend unitário | 168 testes aprovados |
| Frontend unitário/cobertura | 71 testes aprovados |
| Ruff lint/formatação, ESLint, TypeScript | Aprovados |
| Build Next.js | Aprovado |
| Suítes de navegador | Aprovadas; conta, avaliação, catálogo, identidade, foco e overflow |
| CI remoto | Todos os checks passaram, incluindo integração real com PostgreSQL e Compose |

Esses resultados superam a limitação de navegador do ambiente inicial do autor;
não são novas execuções desta PR documental. O catálogo controlado de 27 itens
verifica expansão 12/24/27, nomes, filtros, recarga e histórico. Quatro larguras:
320/390/768/1440 px. Capturas usam dados sintéticos, não contas/avaliações reais.
[Comparações versionadas](../../docs/estudos/identidade-conta-catalogo-2026-11-10.md).

Reproduzir com o runner existente, após instalar dependências e disponibilizar
Edge/Chromium nas portas previstas por ele, a partir de `frontend/`:

```sh
BROWSER_PATH=/caminho/para/chrome PREVIEW_DIR=/tmp/undb-conta-205 npm run test:browser
```

É exemplo, não comando executado por esta PR. Os cenários controlados não
comprovam usabilidade com alunos nem todos os fluxos hospedados. #166 permanece
com reteste qualitativo. API e frontend precisam ser promovidos juntos para
exibir os nomes completos em produção.
