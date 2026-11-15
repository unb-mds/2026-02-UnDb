// PR #248: valida o HTML inicial entregue ao crawler, sem executar scripts da página.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { comNavegador } from './browser-session.mjs';

const tituloHome = 'UnDb | Avaliações de professores da UnB';
const descricaoHome = 'Veja o que outros estudantes acharam dos professores e disciplinas da UnB e escolha suas próximas matérias.';
const imagemUrl = 'https://undb.app.br/undb-preview.png';
const alt = 'UnDb — avaliações de professores e disciplinas da UnB';
const imagem = await readFile(new URL('../public/undb-preview.png', import.meta.url));
const original = await readFile(new URL('../../docs/referencias/preview-compartilhamento/undb-preview-final.png', import.meta.url));
assert.deepEqual(imagem, original, 'arte pública preserva exatamente os bytes fornecidos por Nicolas');
assert.equal(imagem.subarray(0, 8).toString('hex'), '89504e470d0a1a0a');
assert.deepEqual([imagem.readUInt32BE(16), imagem.readUInt32BE(20)], [1200, 630]);

await comNavegador({ executar: async ({ avaliar }) => {
  for (const [rota, titulo, descricao, url] of [
    ['/', tituloHome, descricaoHome, 'https://undb.app.br/'],
    ['/sobre', 'Sobre o UnDb', 'Conheça a proposta do UnDb e a equipe que constrói a plataforma.', 'https://undb.app.br/sobre'],
    ['/professores', tituloHome, descricaoHome, null],
  ]) {
    const response = await fetch(`http://localhost:3100${rota}`, { headers: { 'User-Agent': 'WhatsApp/2.24' } });
    assert.equal(response.status, 200);
    const html = await response.text();
    // DOMParser trata escapes HTML e ordem de atributos sem executar JavaScript ou buscar recursos.
    const documento = await avaliar(`const pagina = new DOMParser().parseFromString(${JSON.stringify(html)}, 'text/html');
      ({ titulo: pagina.title,
         metas: Array.from(pagina.head.querySelectorAll('meta')).map(m => [m.getAttribute('property') ?? m.getAttribute('name'), m.content]),
         icones: Array.from(pagina.head.querySelectorAll('link[rel~=icon]')).map(l => l.getAttribute('href')) })`);
    assert.equal(documento.titulo, titulo, `${rota}: título específico preservado`);
    const valor = (chave, esperado) => assert.deepEqual(documento.metas.filter(([nome]) => nome === chave).map(([, conteudo]) => conteudo), [esperado], `${rota}: ${chave} único no head inicial`);
    valor('description', descricao);
    valor('og:title', titulo);
    valor('og:description', descricao);
    valor('og:type', 'website');
    valor('og:site_name', 'UnDb');
    valor('og:locale', 'pt_BR');
    valor('og:image', imagemUrl);
    valor('og:image:width', '1200');
    valor('og:image:height', '630');
    valor('og:image:type', 'image/png');
    valor('og:image:alt', alt);
    valor('twitter:card', 'summary_large_image');
    valor('twitter:title', titulo);
    valor('twitter:description', descricao);
    valor('twitter:image', imagemUrl);
    valor('twitter:image:alt', alt);
    if (url) {
      const urls = documento.metas.filter(([nome]) => nome === 'og:url').map(([, conteudo]) => conteudo);
      assert.equal(urls.length, 1, `${rota}: og:url único`);
      // O Next normaliza a barra final da origem; comparar a URL sem perder caminho/query.
      assert.equal(new URL(urls[0]).href, new URL(url).href);
    } else assert.equal(documento.metas.some(([nome]) => nome === 'og:url'), false, 'URL da home não vaza para outra rota');
    assert.ok(documento.icones.some(icone => icone.split('?')[0] === '/favicon.ico'));
    assert.ok(documento.icones.some(icone => icone.split('?')[0] === '/icon.png'));
  }
  for (const [rota, titulo] of [['/moderacao', 'Fila de moderação — UnDb'], ['/moderacao/identidades', 'Identidades de professores — UnDb']]) {
    const html = await (await fetch(`http://localhost:3100${rota}`)).text();
    const documento = await avaliar(`const pagina = new DOMParser().parseFromString(${JSON.stringify(html)}, 'text/html');
      ({ titulo: pagina.title, robots: pagina.head.querySelector('meta[name=robots]')?.content, url: pagina.head.querySelector('meta[property="og:url"]')?.content ?? null })`);
    assert.equal(documento.titulo, titulo);
    assert.equal(documento.robots, 'noindex, nofollow');
    assert.equal(documento.url, null, 'área privada não herda a URL da home');
  }
  const png = await fetch('http://localhost:3100/undb-preview.png');
  assert.equal(png.status, 200);
  assert.match(png.headers.get('content-type'), /^image\/png\b/);
  assert.deepEqual(Buffer.from(await png.arrayBuffer()), original, 'HTTP entrega a arte original sem autenticação');
  for (const arquivo of ['favicon.ico', 'icon.png']) {
    const resposta = await fetch(`http://localhost:3100/${arquivo}`);
    assert.equal(resposta.status, 200);
    assert.deepEqual(Buffer.from(await resposta.arrayBuffer()), await readFile(new URL(`../src/app/${arquivo}`, import.meta.url)));
  }
  console.log('Preview #248: PNG original 1200x630 servido com HTTP 200/image/png; metadados únicos no HTML inicial, títulos/descrições de home e Sobre, URLs por rota, robots e ícones preservados. HTTPS público/WhatsApp após deploy permanecem pendentes.');
} });
