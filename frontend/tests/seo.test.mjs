import { test } from 'node:test';
import assert from 'node:assert/strict';
import { join } from 'node:path';
import { pathToFileURL } from 'node:url';
const { metadadosPagina, urlPublica, xmlUrls, URLS_PUBLICAS, TAMANHO_SITEMAP } = await import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, 'seo.js')));

test('metadados públicos compartilham identidade real e canonical absoluto por página', () => {
  const m = metadadosPagina('Professor de teste', 'Disciplinas lecionadas.', '/professores/teste');
  assert.equal(m.alternates.canonical, 'https://undb.app.br/professores/teste');
  assert.equal(m.openGraph.url, m.alternates.canonical);
  assert.equal(m.twitter.title, m.title);
  assert.equal(m.openGraph.images[0].url, 'https://undb.app.br/undb-preview.png');
  assert.deepEqual(m.robots, {index:true, follow:true});
  assert.equal(metadadosPagina('Busca', 'Busca filtrada.', '/professores', false).robots.index, false);
});
test('URLs técnicas, tokens e destinos externos não viram URLs canônicas', () => {
  for (const caminho of ['https://outro.example', '//outro.example', '/login?token=segredo', '/#fragmento', '/\\outro.example']) assert.throws(() => urlPublica(caminho));
  assert.equal(URLS_PUBLICAS.includes('/login'), false);
  assert.ok(TAMANHO_SITEMAP < 50000);
});
test('sitemap omite datas inventadas e escapa XML tanto em URL set como índice', () => {
  assert.match(xmlUrls(['https://example.com/?a=1&b=2']), /a=1&amp;b=2/);
  assert.match(xmlUrls(['https://undb.app.br/']), /<urlset[^>]+><url><loc>/);
  assert.match(xmlUrls(['https://undb.app.br/sitemaps/professores/0.xml'], true), /<sitemapindex[^>]+><sitemap><loc>/);
  assert.doesNotMatch(xmlUrls(['https://undb.app.br/']), /lastmod/);
});
