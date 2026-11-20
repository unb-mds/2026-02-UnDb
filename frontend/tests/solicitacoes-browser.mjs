// RF25: UI com API sintética; autorização real é testada no backend.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { comNavegador } from './browser-session.mjs';
let ativo=true, escrita=false, permissao=true, segurarDetalhe=false, detalheRetido=null;
const protocolo='11111111-1111-4111-8111-111111111111', chave='x'.repeat(43), envios=[];
const item={protocolo,categoria:'OUTRA',alvo:'Alvo fictício',descricao:'Pedido inteiramente sintético.',evidencia:'Contexto fictício.',recebido_em:'2026-11-15T12:00:00Z',historico:[]};
const fixture=createServer(async(req,res)=>{
  res.setHeader('Access-Control-Allow-Origin','http://localhost:3100');
  res.setHeader('Access-Control-Allow-Credentials','true');
  res.setHeader('Access-Control-Allow-Headers','Content-Type');
  res.setHeader('Access-Control-Allow-Methods','GET,POST,OPTIONS');
  res.setHeader('Content-Type','application/json');
  if(req.method==='OPTIONS'){res.writeHead(204).end();return;}
  let body=''; for await(const c of req)body+=c;
  if(body) envios.push({path:req.url,body:JSON.parse(body)});
  const send=x=>res.end(JSON.stringify(x));
  if(req.url==='/api/auth/sessao')return send({autenticado:false});
  if(req.url==='/api/solicitacoes/disponibilidade')return send({ativo});
  if(req.url==='/api/solicitacoes')return send({protocolo,chave,recebido_em:item.recebido_em});
  if(req.url==='/api/solicitacoes/consultar')return send(item);
  if(req.url==='/api/solicitacoes/complementos')return send({...item,historico:[{tipo:'COMPLEMENTO',texto:JSON.parse(body).texto,data:item.recebido_em}]});
  if(req.url==='/api/atendimento/permissao'){if(!permissao){res.writeHead(403);return send({detail:'Acesso restrito ao atendimento.'});}return send({responder:escrita});}
  if(req.url?.startsWith('/api/atendimento?'))return send([item]);
  if(req.url===`/api/atendimento/${protocolo}`){if(segurarDetalhe){detalheRetido=()=>send(item);return;}return send(item);}
  if(req.url===`/api/atendimento/${protocolo}/eventos`)return send({...item,historico:[{tipo:'RESPOSTA',texto:JSON.parse(body).texto,data:item.recebido_em}]});
  res.writeHead(403).end('{"detail":"Acesso restrito"}');
});
await comNavegador({fixture,executar:async({cdp,avaliar,aguardar})=>{
  const navegar=async path=>{await cdp('Page.navigate',{url:'http://localhost:3100'+path});await aguardar(()=>avaliar(`location.pathname===${JSON.stringify(path)} && !!document.querySelector('main h1')`),'página');};
  const esperar=t=>aguardar(()=>avaliar(`document.querySelector('main')?.innerText.includes(${JSON.stringify(t)})`),t);
  const fill=valores=>avaliar(`Object.entries(${JSON.stringify(valores)}).forEach(([name,value])=>{const i=document.querySelector('[name='+name+']');const proto=i.tagName==='TEXTAREA'?HTMLTextAreaElement.prototype:HTMLInputElement.prototype;Object.getOwnPropertyDescriptor(proto,'value').set.call(i,value);i.dispatchEvent(new Event('input',{bubbles:true}));})`);
  await navegar('/contato');await esperar('Enviar solicitação');
  await fill({alvo:item.alvo,descricao:item.descricao,evidencia:item.evidencia});
  await avaliar('document.querySelector("main form").requestSubmit()');await esperar('Solicitação recebida');
  assert.equal(await avaliar('location.search'),'', 'chave fora da URL');
  assert.equal(await avaliar('localStorage.length'),0,'não persistir chave no navegador');
  await avaliar('document.querySelectorAll("main form")[1].requestSubmit()');await esperar('Aguardando análise');
  await fill({texto:'Solicito revisão com contexto sintético.'});
  await avaliar('document.querySelectorAll("main form")[2].requestSubmit()');await esperar('Solicito revisão');
  assert.equal(envios.at(-1).body.chave,chave);
  await navegar('/atendimento');await esperar('Somente leitura');
  await avaliar('document.querySelector("main button").click()');await esperar('Pedido '+protocolo);
  assert.equal(await avaliar('!!document.querySelector("main form")'),false,'leitor sem formulário de escrita');
  escrita=true;await navegar('/contato');await esperar('Enviar solicitação');await navegar('/atendimento');await esperar('Permissão de atendimento');
  await avaliar('document.querySelector("main button").click()');await esperar('Registrar');
  await fill({texto:'Resposta motivada sintética. Peça revisão por complemento.'});
  await avaliar('document.querySelector("main form").requestSubmit()');await esperar('Resposta motivada sintética.');
  permissao=false;await avaliar('window.dispatchEvent(new Event("focus"))');await esperar('Acesso restrito ao atendimento.');
  assert.equal(await avaliar('!!document.querySelector("main article")'),false,'perda de permissão limpa o pedido aberto');
  assert.equal(await avaliar('!!document.querySelector("main form")'),false,'perda de permissão limpa controles internos');
  permissao=true;await avaliar('window.dispatchEvent(new Event("pageshow"))');await esperar('Permissão de atendimento');
  segurarDetalhe=true;await avaliar('document.querySelector("main button").click()');await aguardar(()=>Promise.resolve(!!detalheRetido),'detalhe retido');
  permissao=false;await avaliar('window.dispatchEvent(new Event("undb:sessao-alterada"))');await esperar('Acesso restrito ao atendimento.');
  detalheRetido();segurarDetalhe=false;await avaliar('new Promise(r=>setTimeout(r,150))');
  assert.equal(await avaliar('!!document.querySelector("main article")'),false,'resposta anterior não reexibe pedido após perder acesso');
  ativo=false;await navegar('/contato');await esperar('recebimento ainda não está disponível');
  assert.equal(await avaliar('document.querySelectorAll("main form").length'),1,'acompanhar continua disponível');
  console.log('RF25 UI: criação, recibo, consulta, complemento, leitor, atendente e recebimento suspenso aprovados.');
}});
