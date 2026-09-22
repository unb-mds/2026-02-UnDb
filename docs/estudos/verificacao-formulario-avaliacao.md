# Verificação do formulário de avaliação — Issue #42

## Escopo autorizado após o review do PR #117

Em 22/09/2026, o responsável autorizou a divisão de escopo para resolver o P1 do review.
As issues [#42](https://github.com/unb-mds/2026-02-UnDb/issues/42) e
[#116](https://github.com/unb-mds/2026-02-UnDb/issues/116) foram atualizadas no GitHub
antes das mudanças locais, e os corpos publicados foram conferidos por leitura da API.

- #42: interface, cinco critérios, validações locais e feature gate.
- #116: sessão, POST /avaliacoes real, persistência, substituição sem duplicata e remoção
  do gate após a validação integrada, coordenando #39/#47/#48/#49/#50.
- As regras de produto de docs/requisitos.md e specs.md não foram alteradas.
- Branch: `feature/42-formulario-avaliacao`; base desta correção: `1c498a5`.
- A descrição substituta do PR fica apenas em arquivo local, com `Relacionado a #42`.
  Esta etapa não autoriza push, alteração remota do PR, merge ou fechamento de issue.

## Feature gate

`avaliacao-form.tsx` define `envioHabilitado = false`, sem configuração pública para
ativação. O botão fica desabilitado e associado ao aviso de indisponibilidade. O handler
preserva a validação local e retorna antes de consultar sessão ou enviar POST. Assim,
clique, submissão por teclado/requestSubmit e acesso direto à rota não liberam o envio.
Os cinco campos continuam disponíveis e a tela informa que as respostas não serão
salvas. A consulta institucional de professor/disciplina já existente continua funcionando.

O cliente HTTP e o tratamento de respostas permanecem preparados para #116, mas o fluxo
de envio está bloqueado. Remover o gate exige concluir e verificar a integração real.

## CI e testes

O job Frontend usa Node 22 e `windows-latest`, com `BROWSER_PATH` apontando para Edge.
Executa `npm ci`, lint, testes unitários, build e então `npm run test:browser`.
A imagem Windows inclui Edge conforme o
[inventário oficial](https://github.com/actions/runner-images/blob/main/images/windows/Windows2025-Readme.md).
Os jobs de backend e Docker Compose continuam no Ubuntu.

A suíte de navegador verifica navegação, acesso direto, cinco campos obrigatórios,
validação local, bloqueio no botão e no handler, nenhuma chamada de sessão/POST,
preservação das respostas, teclado e larguras 320/768/1280 nos temas claro/escuro.
Confirma a hidratação por um erro de validação gerado pelo handler React antes de
exercitar submissões válidas. O servidor controlado devolveria 405 se recebesse um POST.
Os cenários de sucesso/erro HTTP preparados continuam cobertos na suíte unitária;
testes de navegador do fluxo liberado deverão acompanhar a remoção do gate na #116.

O runner requer build padrão, Node 22+, Edge/Chromium e portas 8000/3100/9223 livres.
Usa perfil temporário exclusivo e encerra os processos que inicia.

## Verificação local desta correção

Ambiente: Windows, Node v24.21.0 e Edge headless.

- `npm test`: 18 testes aprovados, incluindo 240 combinações válidas.
- `npm run lint`: aprovado.
- `npm run build`: aprovado.
- `npm run test:browser`: aprovado no Edge fora do sandbox; no sandbox houve timeout em Page.enable.
- `git diff --check`: aprovado.

O CI remoto não foi executado para esta correção porque não houve push. Backend e
Docker Compose não foram reexecutados; a alteração não modifica esses componentes.

## Limites e handoff para #116

Respostas controladas não comprovam integração com FastAPI, persistência ou substituição.
O router atual não implementa POST. #116 deve consolidar o contrato com #39, aplicar
sessão/e-mail confirmado de #49, garantir unicidade/substituição conforme #50 e validar
formulário → API real → banco (criação, segundo envio sem nova linha, concorrência,
sessão ausente/inválida/expirada, e-mail não confirmado e entrada inválida).
Somente depois deverá remover o gate e atualizar os testes para o fluxo liberado.
A #42 não depende desse aceite integrado; seu fechamento não é solicitado nesta etapa.
