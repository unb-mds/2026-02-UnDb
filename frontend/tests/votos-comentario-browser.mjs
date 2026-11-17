// RF20/#278: CDP existente e HTTP sintético; não acessa dados reais.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import { comNavegador } from './browser-session.mjs';

const id = n => `${String(n).padStart(8, '0')}-1111-4111-8111-111111111111`;
const professor = id(1), disciplina = id(2), versao = id(3);
const disciplinaWire = { id:disciplina, nome:'Disciplina sintética', codigo:'CIC0001', departamento:'CIC' };
let voto = null, status = 200, atraso = 0, statusConsulta = 200, atrasoConsulta = 0;
const envios = [];
const resumo = () => ({ uteis:voto==='UTIL'?1:0, nao_uteis:voto==='NAO_UTIL'?1:0, meu_voto:voto });
const fixture = createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3100');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Headers', req.headers['access-control-request-headers'] ?? 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  if (req.method === 'OPTIONS') { res.writeHead(204).end(); return; }
  const responder = (codigo, dados) => {
    if (!res.destroyed) res.writeHead(codigo, {'Content-Type':'application/json'}).end(JSON.stringify(dados));
  };
  const path = req.url.split('?')[0];
  if (path === '/api/auth/sessao') return responder(200, {autenticado:false});
  if (path === '/api/agradecimentos' || path === '/api/comentarios/meu' || path === '/api/moderacao/comentarios') return responder(401, {});
  if (path.endsWith('/utilidade')) {
    const codigo = statusConsulta, dados = resumo();
    setTimeout(()=>responder(codigo, codigo===200?dados:{detail:'Detalhe interno sintético'}), atrasoConsulta);
    return;
  }
  if (path.endsWith('/voto')) {
    let corpo=''; for await (const parte of req) corpo+=parte;
    const dados=JSON.parse(corpo); envios.push(dados);
    const codigo=status;
    if (codigo===200) voto=dados.voto;
    const resposta = resumo();
    setTimeout(()=>responder(codigo, codigo===200?resposta:{detail:'Detalhe interno sintético'}), atraso);
    return;
  }
  if (path.endsWith('/comentarios')) return responder(200,[{id:versao,texto:'Crítica acadêmica legítima, mesmo quando impopular.',created_at:'2026-11-16T12:00:00Z'}]);
  if (path===`/api/disciplinas/${disciplina}/professores`) return responder(200,{disciplina:disciplinaWire,professores:[]});
  if (path===`/api/disciplinas/${disciplina}`) return responder(200, disciplinaWire);
  if (path===`/api/professores/${professor}`) return responder(200, {id:professor,nome:'Professor sintético',departamento:'CIC'});
  if (path===`/api/professores/${professor}/disciplinas/${disciplina}`) return responder(200,{professor_id:professor,disciplina_id:disciplina,professor:{id:professor,nome:'Professor sintético',departamento:'CIC'},disciplina:disciplinaWire,total_avaliacoes:1,dados_suficientes:false});
  responder(404,{});
});

await comNavegador({fixture, timeoutMs:60000, executar:async ({cdp,avaliar,aguardar}) => {
  const grupo = '[role="group"][aria-label="Este comentário foi útil?"]';
  const botao = i => `${grupo} button:nth-child(${i})`;
  const selecionar = seletor => `document.querySelector(${JSON.stringify(seletor)})`;
  const pronto = () => aguardar(()=>avaliar(`${selecionar(botao(1))} && ${selecionar(botao(1))}.getAttribute('aria-disabled')==='false' && ${selecionar(grupo)}.getAttribute('aria-busy')==='false'`),'contagens prontas');
  const pressionado = (i, valor) => aguardar(()=>avaliar(`${selecionar(botao(i))}?.getAttribute('aria-pressed')===${JSON.stringify(String(valor))}`),'estado do voto');
  const tecla = async (key, code, windowsVirtualKeyCode) => {
    const texto = key==='Enter'?{text:'\r',unmodifiedText:'\r'}:{};
    await cdp('Input.dispatchKeyEvent',{type:'keyDown',key,code,windowsVirtualKeyCode,...texto});
    await cdp('Input.dispatchKeyEvent',{type:'keyUp',key,code,windowsVirtualKeyCode});
  };
  const foto = async nome => {
    if (!process.env.PREVIEW_DIR) return;
    await mkdir(process.env.PREVIEW_DIR,{recursive:true});
    const shot = await cdp('Page.captureScreenshot',{format:'png'});
    await writeFile(`${process.env.PREVIEW_DIR}/${nome}.png`,Buffer.from(shot.data,'base64'));
  };
  const caminho = `http://localhost:3100/professores/${professor}/disciplinas/${disciplina}`;
  await cdp('Page.navigate',{url:caminho});
  await cdp('Page.bringToFront');
  await cdp('Emulation.setFocusEmulationEnabled',{enabled:true});
  await pronto();
  await avaliar('document.fonts.ready');
  const evidencias = {dados:'HTTP sintético exclusivo; não comprova produção',viewports:[],estados:[]};
  for (const largura of [320,390,768,1440]) {
    await cdp('Emulation.setDeviceMetricsOverride',{width:largura,height:900,deviceScaleFactor:1,mobile:largura<768});
    await avaliar(`${selecionar(grupo)}.scrollIntoView({block:'center',behavior:'instant'})`);
    assert.equal(await avaliar('document.documentElement.scrollWidth <= innerWidth'),true,`overflow ${largura}`);
    const medidas = await avaliar(`Array.from(${selecionar(grupo)}.querySelectorAll('button')).map(b=>({altura:b.getBoundingClientRect().height,largura:b.getBoundingClientRect().width,esquerda:b.getBoundingClientRect().left,direita:b.getBoundingClientRect().right}))`);
    assert.equal(medidas.every(b=>b.altura>=44 && b.largura>=44 && b.esquerda>=0 && b.direita<=largura),true,`alvos ${largura}`);
    await foto(`votos-${largura}-inicial`);
    // A sequência começa em Denunciar e usa Tab, Enter e Space nativos.
    await avaliar(`document.querySelector('[data-testid="botao-denunciar-${versao}"]').focus()`);
    await tecla('Tab','Tab',9);
    assert.equal(await avaliar(`document.activeElement===${selecionar(botao(1))}`),true,'Tab chega a Útil');
    const foco = await avaliar(`({visivel:document.activeElement.matches(':focus-visible'),outline:getComputedStyle(document.activeElement).outlineStyle,espessura:parseFloat(getComputedStyle(document.activeElement).outlineWidth)})`);
    assert.equal(foco.visivel && foco.outline!=='none' && foco.espessura>=2,true,'foco visível');
    await tecla('Enter','Enter',13);
    await pressionado(1,true); await pronto();
    assert.equal(await avaliar(`document.activeElement===${selecionar(botao(1))}`),true,'foco preservado após voto');
    await foto(`votos-${largura}-selecionado-foco`);
    await tecla('Tab','Tab',9);
    assert.equal(await avaliar(`document.activeElement===${selecionar(botao(2))}`),true,'Tab chega a Não útil');
    await tecla(' ','Space',32);
    await pressionado(2,true); await pronto();
    await tecla(' ','Space',32);
    await pressionado(2,false); await pronto();
    evidencias.viewports.push({largura,semOverflow:true,alvos:medidas,teclado:'Tab/Enter/Space',foco});
  }
  assert.deepEqual(envios.slice(0,3),[{voto:'UTIL'},{voto:'NAO_UTIL'},{voto:null}]);
  // Contraste de texto calculado a partir das cores realmente renderizadas.
  const medirContraste = () => avaliar(`(()=>{
    const grupo=${selecionar(grupo)};
    const rgb=cor=>cor.match(/[\\d.]+/g).slice(0,3).map(Number);
    const lum=cor=>rgb(cor).map(c=>c/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4).reduce((s,c,i)=>s+c*[.2126,.7152,.0722][i],0);
    const razao=(a,b)=>(Math.max(lum(a),lum(b))+.05)/(Math.min(lum(a),lum(b))+.05);
    const bg=el=>{while(el){const c=getComputedStyle(el).backgroundColor;if(c!=='rgba(0, 0, 0, 0)'&&c!=='transparent')return c;el=el.parentElement;}return 'rgb(0,0,0)';};
    return Array.from(grupo.querySelectorAll('button,p')).filter(el=>el.textContent.trim()).map(el=>({texto:el.textContent,razao:razao(getComputedStyle(el).color,bg(el))}));
  })()`);
  const contraste = await medirContraste();
  assert.equal(contraste.every(c=>c.razao>=4.5),true,'contraste de texto AA');
  evidencias.contraste=contraste;
  // Estados de erro, bloqueio de duplicatas e ausência de sucesso fictício.
  for (const codigo of [401,403,404,503]) {
    status=codigo; atraso=700;
    const antes=envios.length;
    await avaliar(`${selecionar(botao(1))}.click()`);
    await aguardar(()=>avaliar(`${selecionar(grupo)}.getAttribute('aria-busy')==='true'`),'carregamento');
    assert.equal(await avaliar(`${selecionar(botao(1))}.getAttribute('aria-disabled')`),'true','carregamento anunciado');
    const contrasteCarregando = await medirContraste();
    assert.equal(contrasteCarregando.every(c=>c.razao>=4.5),true,'contraste durante carregamento');
    await avaliar(`${selecionar(botao(1))}.click()`);
    assert.equal(envios.length,antes+1,'não duplica escrita durante carregamento');
    await foto(`votos-carregando-${codigo}`);
    await pronto();
    assert.equal(await avaliar(`!!${selecionar(grupo+' [role="alert"]')}`),true,'erro acessível');
    assert.equal(await avaliar("document.body.innerText.includes('Detalhe interno')"),false);
    assert.equal(await avaliar(`${selecionar(botao(1))}.getAttribute('aria-pressed')`),'false');
    const contrasteErro = await medirContraste();
    assert.equal(contrasteErro.every(c=>c.razao>=4.5),true,'contraste do erro');
    await foto(`votos-erro-${codigo}`);
    evidencias.estados.push({codigo,carregamento:true,erroAcessivel:true,semDuplicata:true,contrasteCarregando,contrasteErro});
  }
  status=200; atraso=0;
  // Leitura indisponível, retry e carregamento inicial.
  statusConsulta=503; atrasoConsulta=300;
  await avaliar("window.dispatchEvent(new Event('undb:sessao-alterada'))");
  await aguardar(()=>avaliar(`${selecionar(grupo)}.getAttribute('aria-busy')==='true'`),'reconsulta');
  await aguardar(()=>avaliar(`${selecionar(grupo)}.innerText.includes('Tentar novamente')`),'retry disponível');
  assert.equal(await avaliar(`${selecionar(grupo)}.querySelectorAll('[aria-pressed]').length`),0,'não inventa contagens na falha');
  await foto('votos-falha-leitura');
  statusConsulta=200;
  await avaliar(`${selecionar(grupo)}.querySelector('button').click()`);
  await pronto();
  // Uma resposta antiga não devolve estado privado depois de troca de sessão.
  atraso=700;
  await avaliar(`${selecionar(botao(1))}.click()`);
  await aguardar(()=>avaliar(`${selecionar(grupo)}.getAttribute('aria-busy')==='true'`),'escrita em andamento');
  voto=null;
  await avaliar("window.dispatchEvent(new Event('undb:sessao-alterada'))");
  await pronto();
  await avaliar('new Promise(r=>setTimeout(r,800))');
  await pressionado(1,false);
  assert.equal(await avaliar(`${selecionar(grupo)}.innerText.includes('Útil (0)')`),true,'não reaparece estado da sessão anterior');
  evidencias.retry=true; evidencias.respostaObsoletaIgnorada=true;
  if (process.env.PREVIEW_DIR) await writeFile(`${process.env.PREVIEW_DIR}/resultados.json`,JSON.stringify(evidencias,null,2)+'\n');
  console.log('Votos: 320/390/768/1440 px, Tab/Enter/Space, foco, contraste AA, erros/carregamento/retry, unicidade de envio e troca de sessão passaram (HTTP sintético).');
}});
