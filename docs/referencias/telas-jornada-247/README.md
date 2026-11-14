# Implementação das seis telas da jornada — #247

## Objetivo e continuidade

[Issue #247](https://github.com/unb-mds/2026-02-UnDb/issues/247), atribuída a
@nicolaszanin06 e @ViniGvdo. Fonte: pedido e seis capturas fornecidas pelo PO em
14/11/2026. Vinícius continuará a implementação nesta mesma branch e PR.

**Este primeiro commit contém apenas documentação e referências visuais.** A PR é de
implementação, permanece em rascunho e não deve ser integrada apenas pelo guia.
A issue só estará concluída após implementar, verificar e obter aceite das telas.

Base inspecionada: `develop` em `18c04c445bed813948a6ed64f0fbcdc8a33c4bb7`.
Antes de continuar, atualizar com a `develop` vigente e reavaliar os arquivos abaixo.
A #237 / PR #243 já corrigiu os estados de sessão e o aviso de senha; preservar.
A #242 / PR #246 trata dos destaques da home; não duplicar essa mudança aqui.

## Referências disponíveis

[Figma — Protótipo + site atual](https://www.figma.com/design/5ydNmYipNHOVfG1oME5j7l/UnDb---Design-atual?node-id=11-2).
As capturas abaixo foram fornecidas pelo PO e estão versionadas para o implementador
não depender do acesso ao Figma. Não representam capturas da implementação atual.
Não foram consultadas propriedades internas do Figma nesta preparação.

| Tela | Referência fornecida | Situação na base inspecionada |
| --- | --- | --- |
| Login | [Captura](capturas/login.png) | Formulário e retorno existentes; moldura com fundo líquido |
| Cadastro | [Captura](capturas/cadastro.png) | Campos, validações e aviso de senha existentes; apresentação parcial |
| Confirmar e-mail | [Captura](capturas/confirmacao-email.png) | Painel de resultado simples; falta a composição central da referência |
| Sucesso da avaliação | [Captura](capturas/sucesso-avaliacao.png) | Mensagem no formulário; falta o cartão de conclusão contextual |
| Página 404 | [Captura](capturas/pagina-404.png) | Texto e links simples; faltam indicador e hierarquia visual |
| Moderação | [Captura](capturas/moderacao.png) | Lista/detalhe funcionais; composição visual ainda diferente |

As capturas são referência de composição, não novos contratos de negócio. Usar a
logo oficial do repositório, não a marca simplificada do protótipo. Não transportar
nomes, códigos, comentários, horários ou avaliações ilustrativos para produção.

## Arquivos e sequência sugerida

Todos os caminhos abaixo são relativos à raiz do repositório.

| Etapa | Arquivos de entrada |
| --- | --- |
| Moldura e abas de conta | `frontend/src/components/moldura-conta.tsx`, `opcoes-acesso.tsx`, `campo-senha.tsx` |
| Login | `frontend/src/app/login/login-form.tsx`, `page.tsx` |
| Cadastro | `frontend/src/app/cadastro/cadastro-form.tsx`, `page.tsx` |
| Confirmação | `frontend/src/app/confirmar-email/confirmation-client.tsx`, `page.tsx` |
| Resultado da avaliação | `frontend/src/app/professores/[id]/disciplinas/[disciplinaId]/avaliar/avaliacao-form.tsx`, `page.tsx` |
| 404 | `frontend/src/app/not-found.tsx` |
| Moderação | `frontend/src/app/moderacao/page.tsx`, `fila-moderacao.tsx`, `detalhe-moderacao.tsx` |
| Contratos e retorno seguro | `frontend/src/lib/services/auth.ts`, `avaliacoes.ts`, `moderacao.ts`; `frontend/src/lib/retorno-avaliacao.ts`, `contexto-busca.ts` |

Ler `AGENTS.md`, as skills aplicáveis e os contratos em [specs.md](../../../specs.md)
e [requisitos](../../requisitos.md). Reutilizar componentes, ícones e tokens atuais;
não substituir o frontend nem copiar uma segunda folha global de estilos.

1. Confrontar cada referência com a tela atual, registrando antes/depois.
2. Ajustar moldura, login e cadastro juntos; conferir efeitos nas rotas que a reutilizam.
3. Implementar apresentação da confirmação e resultado da avaliação.
4. Ajustar 404 e fila/detalhe de moderação sem reduzir funcionalidades.
5. Executar as verificações pertinentes, atualizar esta matriz e pedir revisão do PO.

## 1. Login

- Composição compacta, logo oficial, título, explicação, abas de acesso, campos,
  mostrar/ocultar senha, botão principal e retorno contextual conforme referência.
- Preservar os estados da #237: visitante, carregando, erro de consulta e sessão ativa.
  Sessão ativa mostra Minha conta e Sair, sem convite para entrar/cadastrar novamente.
- Conservar foco, valores, validações, erros e retorno seguro na revalidação da sessão.
- O botão entra e retorna ao formulário; não envia avaliação. Usar texto como
  “Entrar e continuar” quando houver retorno, sem copiar “Entrar e enviar avaliação”.
- “Esqueci minha senha” na captura não autoriza criar link sem destino ou novo fluxo
  de recuperação. Se não existir contrato implementado, registrar pendência com o PO.

## 2. Cadastro

- Mesma família visual do login, abas, nome, e-mail institucional, senha e orientação
  de confirmação. Ajustar tamanhos e espaçamentos para desktop e mobile.
- Manter a orientação de senha exclusiva da #237, limites atuais, acessibilidade e
  validações de nome/domínio. Não coletar senha do SIGAA.
- Mensagem de retorno somente quando houver destino validado. Sem retorno, apresentar
  fluxo genérico, sem prometer voltar a uma avaliação inexistente.
- Botão cria conta e solicita confirmação; não autentica nem envia avaliação por si só.
  Preservar resposta de cadastro, carregamento, falha e prevenção de envio duplicado.

## 3. Confirmação de e-mail

- Cartão central com ícone de estado, identificação da etapa, título de sucesso,
  explicação e ações de continuidade/início conforme a captura.
- Separar carregamento, sucesso, token ausente, inválido/expirado e indisponibilidade
  recuperável. Só mostrar confirmação depois de resposta de sucesso da API.
- Não dizer que a sessão está ativa só porque o e-mail foi confirmado. O fluxo atual
  usa login com `returnTo` quando existe avaliação de origem; preservar essa proteção.
- Sem retorno válido, oferecer início/acesso genérico. Reaproveitar
  `retornoAvaliacaoSeguro`; não aceitar URL externa por parâmetro.
- Preservar tentativa novamente para falhas transitórias, sem converter erro de rede
  em token inválido ou repetir indefinidamente a confirmação.

## 4. Sucesso da avaliação

- Exibir composição central de conclusão com ícone, agradecimento, disciplina/código,
  professor real e ações de retorno/início, usando o contexto já consultado.
- Mostrar somente após confirmação efetiva do envio. URL ou parâmetro arbitrário não
  pode afirmar que uma avaliação foi gravada; preferir estado do resultado existente.
- Forma sugerida: componente de resultado no fluxo atual, sem exigir nova rota/API.
  Caso outra solução seja escolhida, manter refresh/acesso direto honestos e revisar
  retorno/histórico; não guardar senha, token ou texto privado em URL/localStorage.
- Diferenciar critérios gravados de comentário pendente, substituto ou falha parcial.
  Nunca afirmar que comentário foi publicado se depende de revisão humana.
- Preservar acesso a Meus comentários/retirada e à substituição de avaliação; um novo
  cartão não pode esconder permanentemente essas ações já existentes.
- Voltar aos resultados conserva contexto válido de busca/ordem; sem ele, voltar à
  consulta pertinente. Não inventar nomes/códigos nem deixar links sem destino.

## 5. Página não encontrada

- Aplicar indicador 404, título e explicação, com ações Buscar professor e Buscar
  disciplina na hierarquia visual da captura; manter logo/cabeçalho/rodapé oficiais.
- Usar o mecanismo `not-found` existente. Falha de rede/503 não deve virar 404.
- Validar caminhos desconhecidos e IDs inválidos/inexistentes, sem quebrar os estados
  de indisponibilidade das rotas reais nem expor detalhes internos.

## 6. Moderação

- Reorganizar visualmente a fila e o detalhe: identidade da página, navegação entre
  comentários/identidades, filtros, atualizar fila, item selecionado e painel de análise.
- Em desktop, lista e análise lado a lado; no mobile, empilhar com leitura e foco claros.
  O foco do painel e a seleção devem funcionar também por teclado.
- Reaproveitar filtros/ações por estado e serviço existente. A captura mostra um recorte:
  não remover estados, denúncias, histórico, justificativas, anterior/substituto,
  impedimentos por autoria ou confirmação de decisões já exigidos pelo fluxo real.
- Não exibir aprovar/rejeitar/suspender indiscriminadamente; disponibilidade segue
  contratos, estado e permissões. Manter erros, corrida de respostas e envio único.
- Acesso restrito continua na API; ocultar navegação não substitui autorização.
  Sem sessão/moderador, nunca mostrar dados privados da fila.
- Não expor autor/e-mail privado para preencher elementos decorativos da referência.
  Dados indisponíveis não autorizam novos campos no backend sem decisão própria.
- Preservar triagem de IA já integrada: apoio não decide publicação/rejeição sozinho.

## Segurança: aprovação das skills ainda pendente

Na base inspecionada, as duas propostas da #240 / PR #244 permanecem `proposed`:

- [Security Review](../../../skills/engineering/security-review/SKILL.md), seção 10:
  “adoção da skill e alterações derivadas dependem de aprovação pertinente. Não promover a defined.”
- [Incident Response](../../../skills/process/incident-response/SKILL.md), seção 10:
  “Promoção a defined exige aprovação humana explícita.”

**Encaminhamento:** registrar na #240 a revisão/aprovação humana explícita para adotar
cada skill antes de tratá-la como regra oficial. A promoção em si segue
[skill-authoring](../../../skills/governance/skill-authoring/SKILL.md) e
[project-governance](../../../skills/governance/project-governance/SKILL.md).
Este guia não altera metadados, aprova skills nem concede acesso operacional.
A pendência não bloqueia esta documentação ou trabalho independente autorizado.
Se uma etapa depender de autoridade ainda não definida, interromper apenas essa etapa.

Na implementação visual, preservar sessão, cookies, autorização no servidor, retorno
seguro, renderização de comentários como texto e anonimato. Nenhum teste desta entrega
precisa de conta real, senha institucional, base de produção ou alteração da importação.

## Verificação e aceite da implementação

Comandos já existentes em `frontend/`: `npm run lint`, `npm run typecheck`,
`npm run test:coverage`, `npm run build`, `npm run test:browser`.
Seguir também o CI aplicável e os runners integrados definidos pelo projeto; não
substituir evidência de API/banco por fixture HTTP controlada sem registrar a limitação.

Revisar principalmente `tests/conta-avaliacao-sessao-browser.mjs`,
`conta-dark-browser.mjs`, `avaliacao-browser.mjs`, `comentarios-browser.mjs`,
`moderacao-browser.mjs`, `cabecalho-browser.mjs` e `transicao-browser.mjs`.
Manter a sincronização por resultado do envio introduzida nas correções da #243;
não voltar a aguardar textos genéricos que também existem no aviso de acesso.

- [ ] Capturas antes/depois das seis telas em 320, 768 e 1280 px, aguardando fontes/imagens.
- [ ] Sem overflow/corte; rótulos e textos longos legíveis; teclado, foco e contraste.
- [ ] Conta: visitante/ativa/pendente/confirmada, logout/expiração, loading/erro/recuperação.
- [ ] Cadastro/retorno/confirmar: sucesso, erros de validação, token ausente/inválido e rede.
- [ ] Avaliação: sucesso, rejeições 401/403/422, rede, substituição, comentário e falha parcial.
- [ ] 404 real distinto de erro temporário, com ambos os destinos funcionando.
- [ ] Moderação: permissão, filas vazias/erro, seleção, filtros, decisões e impedimentos.
- [ ] Sem dados fictícios no produto; sem regressão na home, animações ou telas da #237.
- [ ] Checks remotos aprovados e evidências identificando versão/limites de cada teste.
- [ ] Aceite visual do PO e revisão técnica; tirar de rascunho somente com implementação pronta.

Esta validação técnica não encerra automaticamente o reteste com alunos da #166.

## Como continuar na mesma PR

```sh
git fetch origin
git switch feature/247-telas-conta-confirmacao-moderacao
# Se a branch ainda não existir localmente:
# git switch --track origin/feature/247-telas-conta-confirmacao-moderacao
```

Trazer a `develop` vigente conforme o fluxo do projeto, implementar na mesma branch,
enviar commits adicionais e atualizar a descrição/checklist da PR com o resultado final.
Não abrir PR concorrente nem integrar esta PR enquanto contiver apenas documentação.
A PR de implementação referencia `Closes #247`; seu futuro merge representa a entrega
completa, não aprovação automática deste plano ou das skills propostas.
