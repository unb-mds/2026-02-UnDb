# Orientações documentais relatadas em 17/11/2026

**Fonte:** relato de Nicolas nesta sessão em 17/11/2026 sobre comentários da professora
em aula. É uma síntese indireta, sem fala literal, lista de presentes, gravação ou ata
formal da aula. Não é a reunião de equipe de 16/11. A #241 organiza estes registros e
as melhorias documentais solicitadas pelo PO.

## Orientações e tratamento nesta entrega

| Orientação relatada | Encaminhamento / localização |
|---|---|
| Documentar o design system do projeto; usar Material Design como referência | [Catálogo do design system existente](design-system.md): tokens, tipografia, componentes e estados; sem mudança de stack ou redesign |
| Melhorar o README, tendo Flutter como referência | README com entradas por público, resumo de uso, badges de workflows reais, imagem de funcionamento e gráfico da arquitetura |
| Mostrar CI e outros badges úteis | Workflows `pull-request.yml`/`pages.yml` e versões do próprio repositório; sem badge de licença ainda não definida ou cobertura sem medição |
| Incluir imagem de como o software funciona | Diagrama visual da jornada, com descrição textual; não apresenta mock como dados ou opiniões reais |
| Incluir gráfico de arquitetura | Diagrama Mermaid derivado de arquitetura/hospedagem já documentadas |
| Separar documentação para usar da documentação para desenvolver | [Tutorial acessível](tutorial-uso.md), [índice técnico](para-desenvolvedores.md) e navegação por público |
| Explicar como subir ambiente e como contribuir | [Desenvolvimento local](desenvolvimento.md) e `CONTRIBUTING.md` existentes, agora acessíveis pela entrada técnica/README |
| Documentar implantação | [Roteiro de implantação](implantacao.md) aponta à configuração e inicialização existentes, com limites reais e sem executar deploy |
| Criar “Implementando com IA”, explicando skills/specs | [Implementando com IA](implementando-com-ia.md) e [registro de uso](uso-ia.md) |
| Buscar referências em projetos de software livre | Flutter, catálogo definitive-opensource e exemplos adicionais FastAPI/Django abaixo; padrões editoriais são adaptados ao UnDb |
| Próxima aula terá IA como tema | Informação relatada, sem data específica ou conteúdo antecipado |

A orientação para simplificar as pendências jurídicas da R2 já foi relatada por Nicolas
em 16/11 e consta da [ata de alinhamento](atas/2026-11-16.md) e da #272. Não se presume
que todos os tópicos desta lista de 17/11 foram discutidos naquela reunião.

## Referências indicadas e consultadas

- [Material Design 3](https://m3.material.io/): referência indicada para design system. A página exige JavaScript; não foi atestada conformidade do UnDb com o padrão.
- [Flutter](https://github.com/flutter/flutter): referência indicada de README; apresentação inicial e caminhos para documentação/instalação/contribuição inspiram a organização, sem copiar conteúdo ou identidade.
- [definitive-opensource](https://github.com/mustbeperfect/definitive-opensource): catálogo indicado para descobrir referências, não uma norma ou garantia de adequação ao projeto.
- [FastAPI](https://github.com/fastapi/fastapi): exemplo adicional de entrada com documentação, recursos e contribuição.
- [Django](https://github.com/django/django): exemplo adicional de separação entre documentação, desenvolvimento e contribuição; não implica retorno do backend a Django.
- [AI-USAGE.md do Cerradinho](https://github.com/unb-mds/2026-2-Cerradinho-API/blob/13b071aa7afa3e085ab05ea362f1370ee5eb1131/AI-USAGE.md): exemplo fornecido por Nicolas para formato do registro. Não é apresentado como documento original de autoria da professora.

## Limites

Esta consolidação registra o que foi relatado e documenta o estado do UnDb. Não altera
requisitos de avaliação individual, processo Scrum, critérios de aceite, licença,
restrições de acesso, design do produto ou tecnologia estrutural. Uma orientação de
referência não equivale à adoção automática de um framework ou política de outro projeto.
