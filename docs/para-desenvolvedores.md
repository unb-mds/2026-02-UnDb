# Para desenvolver e contribuir

Esta é a entrada técnica para quem quer executar, entender, modificar ou operar o UnDb.
Para pesquisar ou avaliar professores, use o [tutorial de uso](tutorial-uso.md).

## 1. Subir o ambiente

Siga o [guia de desenvolvimento local](desenvolvimento.md): pré-requisitos, cópia dos
arquivos de exemplo, credenciais locais, Docker Compose, API, frontend e catálogo.
O banco começa sem opiniões reais; a importação do SIGAA traz dados institucionais,
não avaliações de estudantes. Não reutilize credenciais de produção.

## 2. Entender antes de alterar

| Objetivo | Fonte |
|---|---|
| Problema, público e escopo | [Visão](visao.md) |
| Comportamento autorizado e critérios | [Requisitos](requisitos.md) |
| Camadas e decisões técnicas | [Arquitetura](arquitetura.md) e [ADRs](adrs/index.md) |
| Contratos e especificação derivada | `specs.md`, na raiz do repositório |
| Tokens e componentes existentes | [Design system](design-system.md) e guia do frontend |
| Dados públicos e atualização | [Importação](importacao-sigaa.md), [operação](operacao-importacao-sigaa.md) e [identidades](identidades-docentes.md) |

## 3. Contribuir pelo fluxo do projeto

O [CONTRIBUTING.md](https://github.com/unb-mds/2026-02-UnDb/blob/develop/CONTRIBUTING.md)
descreve Gitflow, tipos de branch, destino da PR, revisão humana e checks obrigatórios.
Para uma tarefa da próxima versão, partir de `develop`, criar a branch apropriada,
implementar o escopo da issue, verificar e abrir PR para `develop`. `main` recebe
releases/hotfixes conforme o fluxo aprovado. Não há novo processo definido nesta página.

Antes de mudanças, consultar `AGENTS.md` e skills aplicáveis. [Implementando com IA](implementando-com-ia.md)
explica como requisitos, specs, skills e evidências se relacionam. Declarar o apoio usado
no [registro de IA](uso-ia.md).

## 4. Verificar e entregar

Os comandos atuais estão em [Qualidade](qualidade.md). Executar verificações adequadas
aos arquivos e comportamentos alterados; distinguir teste com HTTP controlado, integração
PostgreSQL e observação com participantes. Documentar resultado real e limites na PR.

A documentação usa MkDocs Material. `mkdocs build --strict` verifica sua construção;
`mkdocs serve` permite conferir navegação e leitura. README, arquivos fora de `docs/`
e destinos externos precisam de conferência complementar.

## 5. Implantar e operar

O [roteiro de implantação](implantacao.md) organiza os documentos de hospedagem,
inicialização, permissões, importação, moderação, continuidade e recuperação. Ler esses
documentos não concede acesso ou autorização para executar comandos em produção.
