# Telas da jornada — #247 / PR #248

## Resultado local

Continuidade de `0ff2591` na branch `feature/247-telas-conta-confirmacao-moderacao`,
com base `develop` em `18c04c4`. O checkout inicial estava limpo em outra branch;
as referências foram atualizadas e a branch da PR foi selecionada sem descartar trabalho.
Ela já continha toda a base remota, portanto não exigiu integração adicional.

Fontes: [guia e seis capturas do PO](../../docs/referencias/telas-jornada-247/README.md),
[issue #247](https://github.com/unb-mds/2026-02-UnDb/issues/247),
[PR #248](https://github.com/unb-mds/2026-02-UnDb/pull/248),
[correções da #237 / PR #243](https://github.com/unb-mds/2026-02-UnDb/pull/243),
RF01–04, RF14 e RF20–23 dos requisitos, ADRs pertinentes e contratos de `specs.md`.
As propriedades internas do Figma não foram consultadas: a comparação usa as capturas fornecidas.

| Tela | Implementação e comportamento |
| --- | --- |
| Login | Logo oficial no cartão, título, abas compactas, campos e retorno contextual. Sessão ativa continua em Minha conta/Sair; consulta incerta não declara logout. Login só redireciona ao destino validado e não envia avaliação. Erros, senha visível e carregamento preservados; bloqueio síncrono de submissão duplicada. |
| Cadastro | Mesma moldura, rótulos, placeholder e orientação de domínio institucional. Validação de nome, `@aluno.unb.br`, senha exclusiva de 8–128 caracteres e erros da API preservados. O sucesso só vem da resposta de cadastro e mantém sua mensagem genérica, sem revelar se a conta existe. O link recebido por e-mail continua sendo o próximo passo; nenhum token é fabricado. |
| Confirmação | Cartão central e ícone para carregamento, sucesso e erro; token ausente, inválido/expirado/usado e indisponibilidade continuam distintos conforme o contrato. Nova tentativa só para falha recuperável. Confirmação não autentica; continuar passa por `/login` com retorno seguro. A mutação inicial é adiada/cancelada na montagem descartada do StrictMode. |
| Sucesso | Cartão no fluxo atual, sem rota pública de sucesso ou armazenamento. Exibe professor, disciplina e código consultados, retorno à busca com termo/ordem (ou à consulta), início e revisão/substituição. Só aparece após resposta válida do envio. Distingue comentário publicado, pendente e falha parcial; mantém acompanhamento e retirada. O formulário permanece montado para conservar respostas durante a revisão. |
| 404 | Indicador 404, hierarquia da referência, ações Buscar professor/Buscar disciplina e início. Usa `app/not-found.tsx`, herdando cabeçalho/logo/rodapé. Rota desconhecida retorna HTTP 404; erros temporários da API continuam sendo indisponibilidade. |
| Moderação | Navegação de filas, filtros em botões no desktop e seletor no celular, cartões selecionáveis e lista/análise lado a lado a partir de 1024 px. Datas reais do contrato, detalhes empilhados no mobile. Preserva todos os estados, motivo, decisões, denúncias, anterior/substituto, apoio de triagem, impedimentos e erros; autorização continua na API. |

O LinkedIn solicitado foi incluído somente no registro de Vinicius em
`src/app/sobre/equipe.ts`, reutilizando o cartão, ícone social e link acessível existentes,
com `target="_blank"` e `rel="noopener noreferrer"`. Não foram acrescentadas informações pessoais.

Commits locais agrupados por responsabilidade, usando a identidade Git configurada:

- `211d982`: login, cadastro e componentes de acesso.
- `ec5aff9`: confirmação e resultado contextual da avaliação.
- `852137a`: página 404 e moderação.
- `24def2b`: LinkedIn na aba Sobre.
- Commit final `test(ui)`: runner, inclusão no script de navegador, documentação e 36 PNGs.

## Dependências e fronteiras

Ambiente: Windows, Node **24.21.0**, npm **11.19.0**, Edge headless/CDP.
`package.json` e `package-lock.json` analisados: Next **16.3.5**, React/React DOM
**19.2.8**, TypeScript **5.9.3**, Tailwind **4.3.3**, ESLint **9.39.5**, c8 **12.0.0**.
Configurações do App Router, Tailwind/PostCSS, TypeScript estrito e guias locais do Next foram consultados.

Sem nova biblioteca, atualização de versão ou alteração no lockfile. Ícones, validações
HTML, estado React, serviços de autenticação/API e tokens já disponíveis foram reutilizados.
`package.json` só acrescenta o runner da #247 ao final de `test:browser`.
O backend, contratos, permissões, cookies e banco não foram alterados.

A instalação inicial estava sem `c8`: a primeira execução de cobertura falhou com
`MODULE_NOT_FOUND`. `npm ci` restaurou exatamente o lockfile, após uma tentativa
restrita falhar por acesso ao registro npm. A execução concluída reportou 14 avisos
de vulnerabilidade (10 moderados, 3 altos, 1 crítico) das dependências fixadas;
nenhum `audit fix` ou upgrade foi aplicado nesta entrega. Isso requer avaliação própria.

## Verificações executadas

| Comando em `frontend/` | Resultado |
| --- | --- |
| `npm run lint` | Aprovado, sem erros/avisos. |
| `npm run typecheck` | Aprovado: geração de rotas e TypeScript estrito. |
| `npm run test:coverage` | 79 testes aprovados, zero falhas, após restaurar dependências. |
| `npm run build` | Produção compilada com Turbopack; rotas estáticas/dinâmicas geradas. |
| `npm run test:browser` (oito runners existentes) | Todos aprovados: avaliação/busca/catálogo/conta/protótipo, moderação, denúncia, comentários, cabeçalho, identidades, transições e #237. |
| `node tests/jornada-247-browser.mjs` | Aprovado; integrado ao final do script acima. |
| `git diff --check` | Sem erros de whitespace. |

Cobertura medida na rodada final da implementação: linhas/statements **18,91%**,
branches **74,51%**, funções **49,15%**. Não representa cobertura completa da interface.
Não existe script de formatação no frontend; não foi introduzido formatador.
Os guias históricos que dizem não existir `test`/`typecheck` foram confrontados com
o `package.json` atual, que os fornece.

O novo runner verifica login válido/inválido e destino externo rejeitado, retorno sem envio
automático, domínio inválido bloqueado antes da API, cadastro 422/202, confirmação sem token,
400/422/503 e recuperação sem criar sessão. Também retém a resposta da avaliação para
comprovar ausência de sucesso antecipado e bloqueio de duplicata, verifica 403, comentário
pendente/falha parcial, refresh sem falso sucesso, 404 direto, acesso à moderação 401/403/503
sem dados privados e endereço/atributos do LinkedIn. Os runners anteriores cobrem decisões,
concorrência, logout/expiração, preservação do preenchimento, retiradas e demais erros.

As primeiras tentativas de navegador restrito não responderam ao CDP; com execução
autorizada do Edge local, os runners passaram. Uma expectativa nova de texto de 403 foi
corrigida para a orientação já existente no produto. Nenhuma asserção anterior foi retirada.

## Responsividade e evidências

**36 PNGs**, antes/depois das seis telas em **320, 768 e 1280 px**, altura inicial 900,
escala 1, página completa. Capturas aguardam fontes e imagens e estabilizam a rolagem
no topo para não deslocar o cabeçalho sticky na imagem. Dados sintéticos existem somente
na fixture de teste; as telas normais usam os serviços reais.
Na conta, a captura também aguarda os detalhes auxiliares de destino. O foco da análise
e do resultado usa rolagem imediata e margem para o cabeçalho, evitando sobreposição
durante a seleção sem perder o indicador de foco.

Em todas as larguras: sem overflow horizontal e com um `h1`; formulários utilizáveis,
foco por teclado, contraste dos campos >= 4,5:1 e seleção/foco do painel de moderação.
As suítes anteriores também validaram os temas preferidos claro/escuro, com a aplicação
mantida em seu tema escuro, e navegação com movimento reduzido. São viewports emulados,
não testes em aparelhos físicos nem homologação completa com leitor de tela.

| Tela | Antes: 320 / 768 / 1280 | Depois: 320 / 768 / 1280 |
| --- | --- | --- |
| Login | [320](capturas/issue-247/antes/login-320.png) · [768](capturas/issue-247/antes/login-768.png) · [1280](capturas/issue-247/antes/login-1280.png) | [320](capturas/issue-247/depois/login-320.png) · [768](capturas/issue-247/depois/login-768.png) · [1280](capturas/issue-247/depois/login-1280.png) |
| Cadastro | [320](capturas/issue-247/antes/cadastro-320.png) · [768](capturas/issue-247/antes/cadastro-768.png) · [1280](capturas/issue-247/antes/cadastro-1280.png) | [320](capturas/issue-247/depois/cadastro-320.png) · [768](capturas/issue-247/depois/cadastro-768.png) · [1280](capturas/issue-247/depois/cadastro-1280.png) |
| Confirmação | [320](capturas/issue-247/antes/confirmacao-email-320.png) · [768](capturas/issue-247/antes/confirmacao-email-768.png) · [1280](capturas/issue-247/antes/confirmacao-email-1280.png) | [320](capturas/issue-247/depois/confirmacao-email-320.png) · [768](capturas/issue-247/depois/confirmacao-email-768.png) · [1280](capturas/issue-247/depois/confirmacao-email-1280.png) |
| Sucesso | [320](capturas/issue-247/antes/sucesso-avaliacao-320.png) · [768](capturas/issue-247/antes/sucesso-avaliacao-768.png) · [1280](capturas/issue-247/antes/sucesso-avaliacao-1280.png) | [320](capturas/issue-247/depois/sucesso-avaliacao-320.png) · [768](capturas/issue-247/depois/sucesso-avaliacao-768.png) · [1280](capturas/issue-247/depois/sucesso-avaliacao-1280.png) |
| 404 | [320](capturas/issue-247/antes/pagina-404-320.png) · [768](capturas/issue-247/antes/pagina-404-768.png) · [1280](capturas/issue-247/antes/pagina-404-1280.png) | [320](capturas/issue-247/depois/pagina-404-320.png) · [768](capturas/issue-247/depois/pagina-404-768.png) · [1280](capturas/issue-247/depois/pagina-404-1280.png) |
| Moderação | [320](capturas/issue-247/antes/moderacao-320.png) · [768](capturas/issue-247/antes/moderacao-768.png) · [1280](capturas/issue-247/antes/moderacao-1280.png) | [320](capturas/issue-247/depois/moderacao-320.png) · [768](capturas/issue-247/depois/moderacao-768.png) · [1280](capturas/issue-247/depois/moderacao-1280.png) |

Reprodução das capturas atuais no PowerShell, após build:

```powershell
$env:UI247_CAPTURAS='docs/capturas/issue-247'
node tests/jornada-247-browser.mjs
```

Para a base, `UI247_ANTES=1` e `UI247_FRONTEND` selecionam uma cópia isolada de
`0ff2591` preparada por `git archive`. A cópia foi compilada com `npm run build -- --webpack`
e as mesmas dependências, sem alterar fontes; foi removida depois das capturas.

## Limites e pendências

- A comparação visual preserva intencionalmente a logo oficial, fundo líquido da conta,
  orientação de senha exclusiva, contexto auxiliar, explicação de substituição e controles
  de acompanhamento. As telas são adaptações funcionais das capturas, sujeitas ao aceite do PO.
- O contrato privado de comentários não informa professor/disciplina para cada item da fila.
  A interface não inventa esses campos. Também não existe ação manual `SUSPENDER`; ficam
  disponíveis as ações contratadas por estado, com motivo e confirmação. Nenhuma nova
  permissão foi criada no frontend.
- Recuperação de senha permanece fora do escopo; não há link sem destino nem fluxo simulado.
- Nova integração com FastAPI/PostgreSQL, envio/recebimento institucional real e persistência
  não foram executados: Docker não estava em execução e não havia PostgreSQL local na porta
  5432. A configuração privada existente não foi usada para gravar em banco remoto. As evidências
  HTTP controladas não substituem `tests.integration_acesso`, `tests.integration_avaliacao`
  e os runners integrados de moderação em banco de testes migrado.
- O link do LinkedIn foi verificado no DOM quanto ao endereço e à abertura segura; não foi
  feita autenticação nem verificação do conteúdo remoto do perfil.
- Revisão técnica humana, aceite visual do PO, integração real e checks remotos da nova
  implementação continuam pendentes. A PR permanece em rascunho; sem push, merge,
  fechamento da issue ou alteração da base. O reteste com alunos da #166 não foi concluído.

Inspeção final do diff orientada por `skills/engineering/code-review/SKILL.md`, limitada
às fontes alteradas, contratos e evidências acima; não equivale à revisão independente exigida
para merge. Skills propostas de segurança/incidentes permanecem com seu estado original.
