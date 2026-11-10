# Conta e avaliação no tema dark — Issue #205

**Base:** `develop` em `ea7c39c`, incluindo #202/PR #208 e verde aceito da
#212/PR #214. **Escopo:** apresentação da conta e do formulário de avaliação.
Não representa validação com usuários da #166.

## Fontes e coordenação

- [Issue #205](https://github.com/unb-mds/2026-02-UnDb/issues/205): critérios da integração.
- [Guia e índice da referência](../../docs/referencias/ui-dark/issues/205.md),
  consultados também no commit imutável `0b1ee93dfab29627af3927b36ebdcc3efd399c59`
  após buscar esse objeto do remoto. O material serve apenas para consulta.
- [Contrato de tokens e componentes](ui-dark.md): a aplicação usa as classes
  `.container`, `.panel`, `.button` e os tokens existentes. A cor vigente foi
  conferida em `globals.css`: `--primary: #00822e`. Não foi editado o CSS global;
  a atualização histórica do guia da #212 permanece na entrega documental própria.
- Consulta anterior às edições: PR #208 integrado; #204 e #206 abertas; #212
  encerrada pela aceitação do PO. A busca de PRs abertos retornou apenas #213,
  documental. Não foram alterados perfil/comparação ou componentes de comentários.

## Apresentação integrada

- Login/cadastro: contêiner limitado, painel dark com padding responsivo, campos
  sobre `raised`, bordas de controle, texto auxiliar `muted` e ações compartilhadas.
  A navegação entre as duas opções usa duas colunas e mantém `aria-current`.
- Senha: input com largura mínima flexível e botão de mostrar/ocultar com área de
  toque da classe `.button`. Labels, `aria-controls`, `aria-pressed`, autocomplete
  e limites da senha permanecem os existentes.
- Confirmação: painel consistente com a conta, mensagens existentes e `aria-busy`
  durante a consulta. Token inválido, falha transitória, nova tentativa e retorno
  para login/avaliação mantêm o mesmo comportamento.
- Destino: contexto público recolhível em painel; falha de detalhes continua sem
  bloquear autenticação nem perder o destino seguro. O sumário preserva seu
  comportamento nativo de teclado.
- Avaliação: contexto professor/disciplina/código/unidade em painel com duas colunas
  a partir de `sm`; formulário com campos e critérios nas superfícies dark. Os
  cinco botões de Didática continuam quebrando linha quando necessário, sem nota
  inicial; Dificuldade/Chamada permanecem neutras e os rótulos não foram alterados.
- Comentário opcional permanece dentro do formulário. Acompanhamento, retirada,
  estados e dados privados continuam nos componentes e serviços já existentes da
  #206; não foram redesenhados. Sucesso só decorre da confirmação HTTP existente.

Não se alteraram endpoints, helpers de retorno, permissões, estado de sessão,
validações, handlers, escalas, valores negativos ou a proteção de envio repetido.
As mudanças de produção são de classes e duas melhorias semânticas: status de
verificação de sessão e estado ocupado da confirmação. Nenhuma etapa de pesquisa,
conta simulada, dado de demonstração ou infraestrutura paralela foi acrescentada.

## Verificações e limites

Ambiente local: Node 24.14.1 e npm 11.11.0.

| Verificação | Resultado observado |
|---|---|
| `npm run lint` | Aprovado |
| `npm run typecheck` | Aprovado; geração de rotas e TypeScript |
| `npm run test:coverage` | 68 testes aprovados; relatório gerado |
| `npm run build` | Aprovado |
| `git diff --check` | Aprovado |
| `npm run test:browser` | Interrompido antes dos cenários: falta executável Edge/Chromium em `BROWSER_PATH` |

A suíte existente cobre retorno seguro, escalas, 401/403/404/409/422/429/503,
falha de rede e respostas preservadas. O runner de avaliação mantém os testes
de visitante, conta não confirmada, criação/substituição com a mesma linha quando
usado com API/PostgreSQL reais e validação do formulário por teclado.

O cenário controlado passa a testar duas submissões consecutivas com apenas um
envio. A matriz de avaliação acrescenta 390/1440 px, preservando 320/768/1280 e
as asserções existentes. `conta-dark-browser.mjs` acrescenta login/cadastro e
confirmação incompleta em 320/390/768/1440 px, senha, Tab/foco, contraste de texto,
campo com altura mínima e ausência de overflow/etapas antigas. Sua execução local
não foi possível; os resultados remotos devem ser consultados no PR desta entrega.

### Reprodução de capturas com o método existente

Após build, com Edge/Chromium instalado e as portas usadas pelo runner livres:

```sh
BROWSER_PATH=/caminho/para/chrome PREVIEW_DIR=/tmp/undb-conta-205 npm run test:browser
```

É exemplo de reprodução, não comando executado nesta sessão. Usa o navegador CDP
e o servidor HTTP controlado do próprio projeto, com dados sintéticos de teste.
`PREVIEW_DIR` recebe capturas prefixadas `205-` para as quatro larguras solicitadas
e para a avaliação nos dois temas de sistema; não são dados de produção. Os
outros cenários existentes também podem gerar suas capturas nesse diretório.

**Pendência:** capturas e inspeção visual humana das telas/estados em 320, 390,
768 e 1440 px não foram realizadas localmente. A captura da referência consultada
não é evidência da implementação. Não se instalaram dependências novas, não se
afrouxaram asserções e não se declara aceite da #205; usar `Refs #205` enquanto
essa evidência faltar. As verificações técnicas não substituem o reteste #166.
