---
name: gerador-paginas-next-tailwind
description: Gera e adapta páginas do UnDb com Next.js App Router, TypeScript estrito e classes utilitárias Tailwind, respeitando layout, temas, serviços e requisitos existentes. Use ao solicitar uma nova tela ou adaptar uma rota do frontend, inclusive pelo nome Gerador_Paginas_Next_Tailwind; não para configurar a própria skill ou redesenhar a arquitetura.
metadata:
  project-version: "0.1.0"
  project-status: "proposed"
  project-category: "technology"
  project-scope: "frontend-page-generation"
  agent-agnostic: "true"
---

# Gerador_Paginas_Next_Tailwind

## 1. Objetivo

Transformar uma solicitação de tela autorizada em páginas funcionais, fortemente tipadas, consistentes com o UnDb e preparadas para verificação. Adaptação seletiva de orientações Next.js externas; origem e limites em [Pesquisa](references/pesquisa.md).

## 2. Escopo

Rotas em `frontend/src/app/`, componentes funcionais necessários à tela e integração com tipos, hooks e serviços existentes em `frontend/src/lib/`. Esta skill fornece o procedimento tecnológico; não substitui implementação, testes ou decisões de produto.

## 3. Quando utilizar

Quando o usuário pedir criação ou adaptação de página Next.js/Tailwind do projeto e informar comportamento e escopo suficientes. O nome de exibição acima corresponde ao identificador portátil `gerador-paginas-next-tailwind`.

## 4. Quando não utilizar

Não executar geração durante investigação, instalação, configuração ou revisão da própria skill, exceto em teste descartável explicitamente autorizado. Nesse caso, respeitar o formato solicitado (código na resposta ou arquivos temporários), sem integrar o exemplo ao produto. Não usar para construir outro aplicativo, migrar stack, definir design system, backend, banco ou infraestrutura de testes.

## 5. Entradas esperadas

Objetivo da tela, rota pretendida, requisito/critério autorizado, conteúdo, interação e dados necessários. Consultar referências visuais fornecidas quando acessíveis; não presumir conteúdo de um board apenas por existir um link.

## 6. Pré-condições

1. Ler `AGENTS.md`, `frontend/AGENTS.md` e a skill de [implementation](../../engineering/implementation/SKILL.md) antes de implementar.
2. Ler [Contexto do repositório](references/contexto-repositorio.md) e conferir suas fontes atuais: `frontend/README.md`, requisitos e ADRs pertinentes, rota semelhante, layout, estilos globais, serviços, tipos e configurações.
3. Conferir versões em `frontend/package.json` e lockfile. Antes de escrever código Next.js, ler os guias pertinentes em `frontend/node_modules/next/dist/docs/`, conforme o bootstrap do frontend. Se ausentes, consultar documentação oficial compatível e declarar a limitação; não atualizar dependências para contorná-la.
4. Distinguir uso autorizado do procedimento e adoção como regra oficial: o estado desta skill é `proposed`, não uma promoção implícita da governança.

## 7. Procedimento

1. **Mapear a tela.** Relacionar rota, fonte do comportamento, serviços/tipos reutilizáveis e estados de interface. Identificar somente lacunas que afetem a implementação. Preservar alterações já presentes no checkout.
2. **Definir a fronteira de execução.** Usar Server Component para composição e leitura no servidor; isolar estado, eventos e APIs do navegador em Client Components com `"use client"`. Nunca criar Client Component `async`; passar props serializáveis pela fronteira. Usar `params`/`searchParams` assíncronos conforme a versão instalada e os exemplos locais, sem APIs do Pages Router.
3. **Integrar contratos existentes.** Reutilizar `@/lib/services`, `@/lib/types` e hooks, mantendo transporte e adaptação de resposta fora do JSX. Tipar props, eventos, estados e resultados sem `any`, `@ts-ignore` ou coerções para ocultar incompatibilidades. Usar `unknown` e refinamento em erros. Não confundir uma asserção TypeScript com validação de resposta em runtime.
4. **Compor a interface.** Herdar o header e fontes do layout raiz. Estilizar o novo código exclusivamente com utilitários Tailwind e tokens existentes: sem `style`, CSS Modules, styled-jsx, CSS-in-JS ou nova folha CSS. Reusar componentes existentes quando aplicáveis; extrair apenas unidades com responsabilidade concreta, sem criar biblioteca de UI ou dependências por conveniência. Preferir classes completas e estaticamente detectáveis em variantes tipadas.
5. **Preservar comportamento e acessibilidade.** Usar `next/link`, HTML semântico, um `h1`, rótulos associados, foco visível e mensagens em português. Tratar carregamento, sucesso, vazio, erro e não encontrado quando pertinentes. Em busca assíncrona, impedir resposta obsoleta de sobrescrever a atual. Mapear 404 real a `notFound()`; não converter indisponibilidade da API em ausência de registro. Preservar a sequência documentada de consulta do professor antes de suas disciplinas.
6. **Preparar para testes.** Manter apresentação separável dos serviços e efeitos; usar props tipadas, chaves estáveis e controles selecionáveis por papel/rótulo. Não buscar dados durante importação de módulo. Descrever cenários verificáveis ligados ao requisito, incluindo estados e interações. Implementar testes somente no escopo autorizado e com mecanismos estabelecidos, seguindo [testing](../../engineering/testing/SKILL.md).
7. **Verificar e entregar.** Executar as verificações da seção 11 aplicáveis à mudança, relatar resultados reais e limitações. Não executar commit, push, PR ou merge sem autorização explícita.

## 8. Saída esperada

- **Implementação no repositório:** arquivos da tela autorizada, justificativa breve da divisão servidor/cliente, contratos reutilizados, estados cobertos e evidências de verificação.
- **Exemplo somente na resposta:** código no formato solicitado, com indicação de dependências do layout existente, interações simuladas e limites da verificação. Não criar arquivos para executar esse exemplo sem autorização.
- **Teste descartável em arquivos:** criar somente os artefatos temporários autorizados e respeitar o momento de remoção ou espera por feedback solicitado. Não incluir esses artefatos em staging, commit ou integração ao produto.
- **Análise/configuração sem teste autorizado:** documentação da skill, sem páginas, componentes ou arquivos `.tsx`.

Dados fictícios de exemplos autorizados não estabelecem requisitos, contratos ou permissão para coletar dados reais no produto.

## 9. Restrições

Não inventar endpoints, dados de produção, critérios de avaliação ou autorização de acesso. Não adicionar cache compartilhado a dados de sessão. Manter o FastAPI responsável por negócio e persistência, sem acesso direto ao banco ou substituição por Server Actions/Route Handlers. Preservar requisitos de neutralidade, insuficiência e privacidade indicados na referência local. Não copiar desativações de lint de outra tela sem demonstrar a necessidade específica.

## 10. Aprovação humana

Aplicar [project-governance](../../governance/project-governance/SKILL.md) e suas [fronteiras de aprovação](../../governance/project-governance/references/HUMAN_APPROVAL_BOUNDARIES.md). A solicitação de configurar esta skill não autoriza seu primeiro uso. Não promover `proposed` para `defined` sem aprovação humana explícita, conforme o bootstrap e [skill-authoring](../../governance/skill-authoring/SKILL.md). Não exigir nova confirmação para trabalho já autorizado dentro do mesmo escopo.

## 11. Verificação

- Conferir aderência à rota solicitada, contratos, separação servidor/cliente, tipos e utilitários Tailwind.
- Para implementação de telas no repositório, executar `npm run lint` e `npm run build` em `frontend/`, como no CI. O build verifica também TypeScript; não inventar scripts `test` ou `typecheck`.
- Para telas executáveis no ambiente autorizado, verificar em navegador larguras **320, 768 e 1280 px**, temas claro/escuro, quebra de textos e ausência de rolagem horizontal; testar Tab, foco, rótulos e estados relevantes. Incluir transição de grade em `sm` quando usada.
- Para código somente na resposta, revisar estrutura e aderência às fontes e declarar que lint, build e navegador não foram executados sobre o exemplo. Em testes temporários, executar apenas verificações compatíveis com o ambiente e escopo autorizados; não tratar checks da aplicação que excluam o exemplo como validação dele.
- Reportar separadamente análise estática, build, inspeção visual e testes de comportamento. Se faltar navegador/backend/rede, indicar exatamente os cenários não verificados.
- Ao alterar somente a skill, usar o checklist de `skill-authoring` e um validador Agent Skills disponível. Não gerar páginas para testar a skill sem autorização.

## 12. Interação com outras skills

- [implementation](../../engineering/implementation/SKILL.md): conduz alterações autorizadas; esta skill acrescenta as decisões tecnológicas da tela.
- [testing](../../engineering/testing/SKILL.md): planeja/executa testes no escopo autorizado; prontidão para testes não implica adotar framework.
- [architecture](../../engineering/architecture/SKILL.md): recebe propostas que alterem fronteiras ou tecnologias.
- [project-governance](../../governance/project-governance/SKILL.md): autoridade e evidências.
- [skill-authoring](../../governance/skill-authoring/SKILL.md): manutenção e promoção desta skill.

Consultar apenas as dependências pertinentes, respeitando seu estado e sem duplicar seus procedimentos.

## 13. Incerteza e falhas

Revalidar o contexto quando código/documentação evoluírem. Se faltar requisito, contrato ou decisão estrutural indispensável, registrar `Pending Decision`, identificar a fonte e interromper somente a parte dependente. Não escolher silenciosamente entre fontes conflitantes nem transformar proposta em regra. Distinguir falha de código, ambiente e informação; não declarar verificação inexistente como aprovada.
