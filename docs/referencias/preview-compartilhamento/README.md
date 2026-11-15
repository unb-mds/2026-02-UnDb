# Preview de compartilhamento do UnDb

Complemento solicitado pelo PO para a PR #248, continuidade de @ViniGvdo.
A arte e o roteiro originais de `51a7317` foram preservados. Os metadados foram
implementados localmente na auditoria de continuidade; publicação e validação real
no WhatsApp permanecem pendentes. Veja a [auditoria e os limites da validação](../../estudos/auditoria-pr248.md).

## Arte final
- Arquivo: [undb-preview-final.png](./undb-preview-final.png).
- PNG, 1200 × 630 px. Logo original fornecida pelo PO aplicada diretamente, com redimensionamento proporcional e remoção apenas das margens externas; sem regenerar símbolo ou tipografia.
- Fundo branco, marca completa, frase “Sua próxima matéria começa aqui.”, descrição, domínio e rodapé azul/verde.
- Esta é a arte final selecionada; descartar as versões exploratórias geradas anteriormente.

## Implementação
1. Disponibilizar uma cópia do PNG em `frontend/public/undb-preview.png`, preservando bytes e dimensões.
2. Ajustar `frontend/src/app/layout.tsx` ou a fonte vigente dos metadados, conciliando com os valores existentes:
   - `metadataBase`: `new URL("https://undb.app.br")`.
   - Título da home e `openGraph.title`: “UnDb | Avaliações de professores da UnB”.
   - Descrição e `openGraph.description`: “Veja o que outros estudantes acharam dos professores e disciplinas da UnB e escolha suas próximas matérias.”
   - `openGraph.type`: `website`; `siteName`: `UnDb`; `locale`: `pt_BR`.
   - `openGraph.images`: URL pública absoluta `https://undb.app.br/undb-preview.png`, largura 1200, altura 630, tipo `image/png`, alt “UnDb — avaliações de professores e disciplinas da UnB”.
   - `openGraph.url` da home: `https://undb.app.br/`. Evitar herdar a URL da home em páginas que tenham sua própria URL de compartilhamento.
   - `twitter.card`: `summary_large_image`, com mesmo título, descrição, imagem e alt.
3. Preservar metadados específicos de rotas, títulos existentes quando necessários, logo e favicon oficiais. Não criar conta social fictícia nem substituir a logo por imagem gerada.
4. Não criar arquivo `opengraph-image.*` ou `twitter-image.*` que sobreponha a configuração por acidente; conferir a precedência dos arquivos já existentes.

## Aceite e validação
- [ ] PNG público responde 200 por HTTPS, sem autenticação, com Content-Type image/png e 1200 × 630 px.
- [x] PNG servido localmente com HTTP 200, Content-Type image/png, dimensões corretas e bytes idênticos à arte original; HTTPS de produção ainda depende de deploy.
- [x] HTML inicial local entregue ao crawler contém og:title, og:description, og:image absoluto, dimensões, alt, og:url e twitter:card coerentes, sem duplicatas conflitantes.
- [x] Conferir tags locais na home e em rotas internas; Sobre preserva título/descrição próprios e moderação preserva títulos/robots. A URL da home não é herdada por outras rotas.
- [x] Executar os checks pertinentes já definidos no frontend (lint, tipos e build).
- [ ] Depois do deploy, compartilhar o endereço público em uma nova mensagem do WhatsApp e registrar captura do resultado. O aplicativo escolhe o formato/corte final; a arte não garante cartão grande em todos os clientes.
- [ ] Se aparecer a imagem antiga, investigar cache do crawler antes de alterar a marca; quando necessário, publicar nova URL versionada da imagem e atualizar os metadados.
- [ ] Revisão visual do PO e revisão técnica antes do merge.

## Estado
O commit original entregou referência e arte, sem metadados. A continuidade acrescenta
`frontend/public/undb-preview.png`, metadados compartilhados reutilizados por layout,
home e Sobre, e `frontend/tests/preview-compartilhamento-browser.mjs` ao `test:browser`.
Para verificar localmente, depois de `npm run build`, execute em `frontend/`:
`node tests/preview-compartilhamento-browser.mjs`.
Nenhum deploy ou compartilhamento externo foi realizado. Os novos commits desta
auditoria aguardam autorização de push; isso não representa aceite visual ou revisão da PR.
