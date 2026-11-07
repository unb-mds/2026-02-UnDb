# Referência de implementação UnDb dark — 06/11/2026

Material preparado por Nicolas para a integração das issues #202–#206. O time pode adaptar o visual durante a implementação. Os arquivos são um ponto de partida concreto, acompanhado de capturas, sem obrigação de reproduzir cada pixel.

## Divisão e ordem

| Issue | Área | Responsável / dependência |
| --- | --- | --- |
| [#202](issues/202.md) | Tokens, layout, cabeçalho, busca compacta e breadcrumbs | Nicolas; primeira integração |
| [#203](issues/203.md) | Home, busca, disciplinas e unidades | Depois da base #202 |
| [#204](issues/204.md) | Perfil, critérios e comparação | Depois de #202 e contratos de #203 |
| [#205](issues/205.md) | Cadastro, login, confirmação e avaliação | Depois de #202; coordenar comentários com #206 |
| [#206](issues/206.md) | Comentários, denúncias e moderação | Depois de #202; coordenar formulário com #205 |
| [#207](issues/207.md) | Reconciliação de professores duplicados | Vinicius; backend independente da UI |

Cada guia lista os arquivos e inclui uma instrução pronta para IA. O responsável deve ler os critérios atualizados da issue e as regras do repositório. O conteúdo desta pasta é referência de implementação, não altera a autoridade de AGENTS.md ou das skills canônicas.

## Acessar sem repassar arquivos manualmente

É possível ler os arquivos e capturas diretamente no GitHub. Em um checkout do projeto, traga só a referência para sua branch:

```sh
git fetch origin feature/202-referencia-ui-dark
git restore --source=origin/feature/202-referencia-ui-dark -- docs/referencias/ui-dark
```

O comando atualiza apenas esse caminho. Confira antes se não há alterações próprias nessa pasta. Para resultado imutável, use o SHA informado nas issues no lugar de `origin/feature/202-referencia-ui-dark`. Não comite cópias da referência em cada PR; adapte apenas a área funcional correspondente em `frontend/`. Quem usa IA deve indicar o guia de sua issue e pedir que ela leia os arquivos relacionados, não depender apenas de screenshots.

## Integração no aplicativo oficial

- Partir de `develop` atualizado, preservando entregas recentes de ADRs, lint, tipos e, quando integrada, cobertura. A referência veio de uma cópia anterior à integração dessas entregas e não as substitui.
- O código de referência está em `src/`; o destino funcional é `frontend/src/`. Não substituir o frontend inteiro ou o `package.json` pelo material da demonstração.
- Usar API, cookies, variáveis, autenticação e infraestrutura oficiais. `src/lib/services/` e tipos mostram o contrato usado na demonstração, mas devem ser comparados com os serviços vigentes. O fallback local 8107 foi removido desta referência; configure a API segundo o projeto oficial.
- Remover ou condicionar à demonstração os avisos `simulation-banner`, `demo-label`, badges simulados e exemplos fixos. Não levar notas fictícias ao banco oficial. A área de contas fictícias foi retirada da home distribuída.
- As capturas têm catálogo institucional e avaliações/comentários simulados; não são opiniões reais dos docentes. Algumas capturas funcionais são anteriores à importação FCTE e servem para visualizar os fluxos, não para definir dados oficiais.
- Não recriar `/prototipo` nem a barra numerada de etapas. Busca na home leva diretamente aos resultados novos; cabeçalho interno mantém busca compacta e contexto. Preservar retorno seguro à avaliação após login/confirmação.
- Resultados abaixo de três avaliações não exibem critérios; falta de avaliação não equivale a nota baixa. Dificuldade e chamada são informativas, sem nota geral. Permissões e decisões de moderação continuam no servidor.
- A fonte contém o CSS completo da experiência para consulta; #202 deve organizar o contrato compartilhado e as demais issues adaptar só suas áreas para evitar disputas em `globals.css`.

## Validação

Na cópia isolada foram executados lint, build e verificações funcionais de navegação, acesso, avaliação e moderação. Isso não certifica a futura integração: cada PR deve executar os checks atuais do repositório e verificar erros, carregamento, vazio, teclado e larguras 320/390/768/1440 px. O reteste com alunos continua na #166 após a integração; capturas e checks técnicos não o substituem.

## Escopo da publicação

Inclui fontes de UI, guias por issue, capturas e inventário SHA-256. Não inclui backend duplicado, banco, .env, credenciais, dependências instaladas, builds ou volumes. A branch apenas disponibiliza a referência; a aplicação oficial deve evoluir nas PRs das issues. Não executar esta pasta como aplicativo independente.
