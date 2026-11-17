// RF20/#278: infraestrutura CDP existente, HTTP sintético, sem dependências novas.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { comNavegador } from './browser-session.mjs';

const id = n => `${String(n).padStart(8,'0')}-1111-4111-8111-111111111111`;
const professor = id(1), disciplina = id(2), versao = id(3);
let voto = null, status = 200, atraso = 0;
const envios = [];
const fixture = createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3100');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  if (req.method === 'OPTIONS') { res.writeHead(204).end(); return; }
  const responder = (codigo, dados) => { res.writeHead(codigo, {'Content-Type':'application/json'}).end(JSON.stringify(dados)); };
  const path = req.url.split('?')[0];
  if (path === '/api/auth/sessao') return responder(200, {autenticado:false});
  if (path === '/api/agradecimentos' || path === '/api/comentarios/meu') return responder(401, {});
  if (path.endsWith('/utilidade')) return responder(200, {uteis:voto==='UTIL'?1:0, nao_uteis:voto==='NAO_UTIL'?1:0, meu_voto:voto});
  if (path.endsWith('/voto')) {
    let corpo=''; for await (const parte of req) corpo+=parte;
    const dados=JSON.parse(corpo); envios.push(dados);
    const codigo=status;
    if (codigo===200) voto=dados.voto;
    setTimeout(()=>responder(codigo,codigo===200?{uteis:voto==='UTIL'?1:0,nao_uteis:voto==='NAO_UTIL'?1:0,meu_voto:voto}:{detail:'Detalhe interno que não deve aparecer'}),atraso);
    return;
  }
  if (path.endsWith('/comentarios')) return responder(200,[{id:versao,texto:'Crítica acadêmica legítima, mesmo quando impopular.',created_at:'2026-11-16T12:00:00Z'}]);
  if (path===`/api/professores/${professor}/disciplinas/${disciplina}`) return responder(200,{professor_id:professor,disciplina_id:disciplina,professor:{id:professor,nome:'Professor sintético',departamento:'CIC'},disciplina:{id:disciplina,nome:'Disciplina sintética',codigo:'CIC0001',departamento:'CIC'},total_avaliacoes:1,dados_suficientes:false});
  responder(404,{});
});

await comNavegador({fixture, executar:async ({cdp,avaliar,aguardar}) => {
  await cdp('Page.navigate',{url:`http://localhost:3100/professores/${professor}/disciplinas/${disciplina}`});
  const grupo = `[role="group"][aria-label="Este comentário foi útil?"]`;
  const botao = i => `${grupo} button:nth-child(${i})`;
  await aguardar(()=>avaliar(`!!document.querySelector('${botao(1)}')`),'contagens');
  for (const largura of [320,390,768,1440]) {
    await cdp('Emulation.setDeviceMetricsOverride',{width:largura,height:900,deviceScaleFactor:1,mobile:largura<768});
    assert.equal(await avaliar('document.documentElement.scrollWidth <= innerWidth'),true,`overflow ${largura}`);
    assert.equal(await avaliar(`Array.from(document.querySelectorAll('${grupo} button')).every(b=>b.getBoundingClientRect().height>=44)`),true);
  }
  await avaliar(`document.querySelector('${botao(1)}').focus()`);
  await cdp('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  await cdp('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
  await aguardar(()=>avaliar(`document.querySelector('${botao(1)}').getAttribute('aria-pressed')==='true'`),'voto útil por teclado');
  await avaliar(`document.querySelector('${botao(2)}').click()`);
  await aguardar(()=>avaliar(`document.querySelector('${botao(2)}').getAttribute('aria-pressed')==='true'`),'troca');
  await avaliar(`document.querySelector('${botao(2)}').click()`);
  await aguardar(()=>avaliar(`document.querySelector('${botao(2)}').getAttribute('aria-pressed')==='false'`),'retirada');
  for (const codigo of [401,403,404,503]) {
    status=codigo; atraso=350;
    await avaliar(`document.querySelector('${botao(1)}').click()`);
    assert.equal(await avaliar(`document.querySelector('${botao(1)}').disabled`),true);
    await aguardar(()=>avaliar(`!document.querySelector('${botao(1)}').disabled`),'fim carregamento');
    assert.equal(await avaliar(`!!document.querySelector('${grupo} [role="alert"]')`),true);
    assert.equal(await avaliar(`document.body.innerText.includes('Detalhe interno')`),false);
    assert.equal(await avaliar(`document.querySelector('${botao(1)}').getAttribute('aria-pressed')`),'false');
  }
  assert.deepEqual(envios.slice(0,3),[{voto:'UTIL'},{voto:'NAO_UTIL'},{voto:null}]);
  console.log('Votos: teclado, troca, retirada, erros, carregamento e 320/390/768/1440 px passaram (HTTP sintético).');
}});
