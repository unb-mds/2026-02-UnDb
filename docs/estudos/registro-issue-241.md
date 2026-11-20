# Entrega documental — Issue #241

Consolidada em 17/11/2026, branch `docs/241-atas-uso-ia`, sobre `develop` `df854bf`
(após integração da #269/PR #281). Fonte: relato de Nicolas nesta sessão, escopo da
[#241](https://github.com/unb-mds/2026-02-UnDb/issues/241), orientações documentais
relatadas por ele e exemplo AI-USAGE do Cerradinho indicado por ele.

## Entregas

- Duas atas anteriores preservadas; a de 14/09 foi centralizada em `docs/atas/`, com
  ponte no caminho antigo de `sprints/sprint03/`.
- Cinco novas atas retrospectivas: semanas 2, 3, 5, 6 e reunião de 16/11 da semana 8.
  Presenças e ausências seguem o relato, não os assignees. Dias desconhecidos ficam
  como intervalos; segundas/quartas e feriados não foram usados para escolher datas.
- Índice de cobertura das semanas: ausência de reunião na semana 4 explicitamente
  informada; semanas sem relato não são convertidas em “não houve reunião”.
- `AI_USAGE.md` na raiz, com formato adaptado do exemplo indicado, fontes e saída
  aceita/ajustada/pendente; histórico da R1 e usos pessoais não conhecidos seguem ausentes.
- Orientação de simplificação da R2 de 16/11 registrada como relato do PO com contexto
  da #272, separada das orientações documentais relatadas em 17/11.
- README reorganizado com badges dos workflows reais, imagem SVG de funcionamento,
  gráfico Mermaid da arquitetura e entradas para usar/desenvolver.
- Tutorial de uso acessível; entrada técnica com links para ambiente/contribuição;
  roteiro de implantação e catálogo do design system existente.
- Documento “Implementando com IA”, explicando requisitos, specs, skills, evidências e
  o exemplo rastreável da #269, sem criar governança nova.

Conteúdo documental permanece no repositório/GitHub Pages, conforme esclarecimento
explícito de Nicolas. Nenhum arquivo de frontend/backend, serviço, dependência ou regra
de produto foi alterado pela #241.

## Critérios da issue

| Critério | Evidência |
|---|---|
| Conferir atas existentes e completar relatos fornecidos, sem inventar | [Índice de atas](../atas/README.md), cinco registros retrospectivos e preservação das duas atas anteriores |
| Registrar orientação de simplificação relatada em 16/11 | [Ata de 16/11](../atas/2026-11-16.md), distinguindo o encontro do estado posterior das issues |
| Registro simples de IA com fonte, finalidade e limites | [Índice do registro canônico](../uso-ia.md) e [Implementando com IA](../implementando-com-ia.md) |
| Links/navegação e fidelidade | Verificações abaixo; lacunas explícitas e nenhuma transcrição privada publicada |

## Verificações executadas

- `mkdocs build --strict`: aprovado.
- Conferência de 113 links/imagens locais no README, AI_USAGE, guias, atas, relatório e
  caminho antigo: nenhum destino ausente.
- Navegador Brave/Chromium: 15 combinações de 5 páginas com 320/768/1280 px,
  título principal único e ausência de rolagem horizontal; imagem SVG sem texto cortado.
- Inspeção visual das capturas da entrada da documentação em desktop e da ata de
  realinhamento do frontend em 320 px: leitura e navegação adequadas.
- `git diff --check`: aprovado.
- Fontes dos badges conferidas em `.github/workflows/pull-request.yml` e `pages.yml`;
  não foi anunciado percentual de cobertura, licença ou disponibilidade não comprovados.

Não foram repetidas suítes da aplicação para uma mudança apenas documental. As verificações
não representam nova observação com alunos ou auditoria dos serviços hospedados.

## Limitações e revisão

Dia/horário/local/duração ou compromissos individuais ausentes continuam explícitos.
O exemplo do Cerradinho é referenciado em commit fixo e não tratado como prova de autoria
da professora ou como política oficial copiada. Não se inventou uso de IA por outros
integrantes, ferramentas/modelos desconhecidos ou aceite individual de uma reunião.

O design system é documentação dos tokens/componentes existentes, não implementação
nova ou declaração de conformidade Material 3. Arquitetura/implantação descrevem fontes
já registradas, sem decisão estrutural ou nova operação em produção.
