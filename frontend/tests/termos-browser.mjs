// RF26: interface com HTTP controlado; contratos/persistência reais em test_termos.py.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import { comNavegador } from './browser-session.mjs';

const envios = [];
let status = 202;
const fixture = createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3100');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Content-Type', 'application/json');
  if (req.method === 'OPTIONS') { res.writeHead(204).end(); return; }
  if (req.url === '/api/auth/sessao') { res.end('{"autenticado":false}'); return; }
  if (req.url === '/api/agradecimentos') { res.end('[]'); return; }
  if (req.url === '/api/auth/cadastro') {
    let body = ''; for await (const chunk of req) body += chunk;
    envios.push(JSON.parse(body));
    await new Promise(resolve => setTimeout(resolve, 250));
    res.writeHead(status).end(JSON.stringify(status === 202
      ? { message: 'Se o endereço informado estiver disponível, enviaremos um link de confirmação.' }
      : { detail: 'Reabra os Termos de Uso e confirme a versão vigente.' }));
    return;
  }
  res.writeHead(404).end('{}');
});

await comNavegador({ fixture, executar: async ({ cdp, avaliar, aguardar }) => {
  const navegar = async path => {
    await cdp('Page.navigate', { url: 'http://localhost:3100' + path });
    await aguardar(() => avaliar(`location.pathname === ${JSON.stringify(path)} && !!document.querySelector('main h1')`), path);
    await avaliar('document.fonts.ready');
    await avaliar('new Promise(r=>setTimeout(r,200))');
  };
  const esperar = texto => aguardar(() => avaliar(`document.querySelector('main').innerText.includes(${JSON.stringify(texto)})`), texto);
  const tecla = async (key, code, windowsVirtualKeyCode) => {
    await cdp('Input.dispatchKeyEvent', { type: 'keyDown', key, code, windowsVirtualKeyCode });
    await cdp('Input.dispatchKeyEvent', { type: 'keyUp', key, code, windowsVirtualKeyCode });
  };
  for (const tema of ['light', 'dark']) for (const width of [320, 768, 1280]) {
    await cdp('Emulation.setDeviceMetricsOverride', { width, height: 950, deviceScaleFactor: 1, mobile: false });
    await cdp('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-color-scheme', value: tema }] });
    for (const path of ['/privacidade', '/termos-de-uso', '/cadastro']) {
      await navegar(path);
      assert.equal(await avaliar('document.querySelectorAll("main h1").length'), 1);
      assert.equal(await avaliar('document.documentElement.scrollWidth <= innerWidth'), true, `${path} ${width}`);
      assert.equal(await avaliar('[...document.querySelectorAll("footer a")].some(a=>a.pathname==="/privacidade") && [...document.querySelectorAll("footer a")].some(a=>a.pathname==="/termos-de-uso")'), true);
      if (path === '/cadastro') {
        assert.equal(await avaliar('document.querySelector("[name=ciencia_termos]").checked'), false);
        assert.equal(await avaliar('[...document.querySelectorAll("main input")].every(i=>i.labels?.length>0)'), true);
        assert.equal(await avaliar('[...document.querySelectorAll("main a")].filter(a=>["/privacidade","/termos-de-uso"].includes(a.pathname)).every(a=>a.target==="_blank")'), true);
        await avaliar('document.querySelector("[name=ciencia_termos]").focus()');
        await tecla(' ', 'Space', 32);
        assert.equal(await avaliar('document.querySelector("[name=ciencia_termos]").checked'), true);
        await tecla('Tab', 'Tab', 9);
        assert.equal(await avaliar('document.activeElement.pathname'), '/termos-de-uso');
      } else {
        await esperar('2026-11-17'); await esperar('sem fins lucrativos');
        assert.equal(await avaliar("document.querySelector('link[rel=canonical]').href"), 'https://undb.app.br' + path);
        assert.equal(await avaliar("document.querySelector('meta[property=\"og:url\"]').content"), 'https://undb.app.br' + path);
        assert.equal(await avaliar('[...document.querySelectorAll("main a[href^=\\"#\\"]")].every(a=>!!document.getElementById(a.hash.slice(1)))'), true);
        await avaliar('document.querySelector("main nav a").focus()');
        await tecla('Enter', 'Enter', 13);
        await aguardar(() => avaliar('location.hash.length > 1'), 'navegação por seção');
        await tecla('Tab', 'Tab', 9);
        assert.equal(await avaliar('document.activeElement !== document.body'), true);
        await avaliar('scrollTo(0,0)');
      }
      if (process.env.PREVIEW_DIR) {
        await mkdir(process.env.PREVIEW_DIR, { recursive: true });
        const shot = await cdp('Page.captureScreenshot', { format: 'png' });
        await writeFile(`${process.env.PREVIEW_DIR}/${path.slice(1)}-${tema}-${width}.png`, Buffer.from(shot.data, 'base64'));
      }
    }
  }
  await navegar('/cadastro');
  await avaliar(`for (const [name,value] of Object.entries({nome:'Pessoa sintética', email:'teste@aluno.unb.br', senha:'Senha-sintetica-269!'})) {
    const input=document.querySelector('[name='+name+']'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input,value); input.dispatchEvent(new Event('input',{bubbles:true}));
  }`);
  await avaliar('document.querySelector("main form").requestSubmit()');
  assert.equal(envios.length, 0, 'HTML bloqueia ciência ausente');
  await avaliar('document.querySelector("main form").dispatchEvent(new Event("submit",{bubbles:true,cancelable:true}))');
  await esperar('Confirme a ciência');
  assert.equal(envios.length, 0, 'React bloqueia envio sem ciência');
  assert.equal(await avaliar('document.activeElement.name'), 'ciencia_termos');
  await tecla(' ', 'Space', 32);
  status = 422;
  await avaliar('document.querySelector("main form").requestSubmit()');
  await esperar('Enviando…');
  await esperar('Reabra os Termos');
  assert.equal(await avaliar('document.querySelector("[name=ciencia_termos]").checked'), true);
  status = 202;
  await aguardar(() => avaliar('!document.querySelector("main button[type=submit]").disabled'), 'botão liberado');
  await avaliar('document.querySelector("main form").requestSubmit()');
  await esperar('Se o endereço informado estiver disponível');
  assert.equal(envios.length, 2);
  assert.deepEqual(envios.at(-1), { nome: 'Pessoa sintética', email: 'teste@aluno.unb.br', senha: 'Senha-sintetica-269!', ciencia_termos: true, termos_versao: '2026-11-17' });
  assert.equal(await avaliar('document.querySelector("[name=ciencia_termos]").checked'), false, 'sucesso limpa ciência');
  console.log('RF26: 18 combinações, links públicos/âncoras, teclado, rótulos, ciência desmarcada, bloqueios HTML/React, 422/retry, payload e reset aprovados.');
} });
