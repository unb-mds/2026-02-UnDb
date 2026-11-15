# Fotos da equipe

Coloque aqui as fotos escolhidas pelos integrantes (ex.: nicolas.jpg).
Em src/app/sobre/equipe.ts, configure foto: "/equipe/nicolas.jpg".
A apresentação opcional e o nome também podem ser editados nesse arquivo.
Use fotos com autorização dos integrantes. O enquadramento usa object-cover;
prefira retratos com o rosto centralizado. Sem foto, o cartão mostra a inicial.

Em 15/11/2026, por solicitação explícita do PO, a foto de Tiago Vieira foi
atualizada a partir do avatar público de `TiagoVieira-596` no GitHub
(`https://avatars.githubusercontent.com/u/158865980?v=4&s=460`), preservando os
bytes JPEG em `TiagoVieira-596.jpg`. Os seis nomes de exibição em `equipe.ts`
seguem os nomes e sobrenomes fornecidos pelo solicitante nesta conversa.
O LinkedIn de Tiago é o endereço fornecido pelo próprio solicitante:
`https://www.linkedin.com/in/tiago-vieira-85a721325/`.

Verificação desta alteração: `BROWSER_PATH=... node tests/equipe-browser.mjs`, após
build. Confere os seis nomes no HTML, bytes/Content-Type da foto e as larguras
320/768/1280 px. `PREVIEW_DIR` opcional salva capturas locais.
