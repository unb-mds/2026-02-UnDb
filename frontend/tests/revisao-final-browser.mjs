// Revisão final: cenários sintéticos de interface; persistência e autoria têm testes HTTP próprios.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import { comNavegador } from './browser-session.mjs';
const uuid = i => `${String(i).padStart(8,'0')}-1111-4111-8111-111111111111`;
const disciplinas = Array.from({length:12},(_,i)=>({id:uuid(i+1),codigo:`CIC${i}`,nome:i===0?'Fundamentos de Sistemas Distribuídos e Aplicações Concorrentes em Ambientes Heterogêneos':'Disciplina de teste '+i,departamento:'CIC',departamento_nome:'Departamento de Ciência da Computação'}));
const professores = [{id:uuid(50),nome:'Professora de teste com nome completo',departamento:'CIC',departamento_nome:'Departamento de Ciência da Computação'}];
const itens = disciplinas.map((d,i)=>({id:uuid(100+i),professor_id:professores[0].id,disciplina_id:d.id,professor:professores[0],disciplina:d,didatica:4,dificuldade:'MEDIO',chamada:false,disponibiliza_material:i!==0,qualidade_material:i===0?null:'BOM',recomenda:true,updated_at:'2026-11-18T00:00:00Z'}));
let autenticado=true, modo='ok';const envios=[];
const fixture=createServer(async(req,res)=>{
 const url=new URL(req.url,'http://localhost');
 res.setHeader('Content-Type','application/json');res.setHeader('Access-Control-Allow-Origin','http://localhost:3100');res.setHeader('Access-Control-Allow-Credentials','true');res.setHeader('Access-Control-Allow-Headers','Content-Type');res.setHeader('Access-Control-Allow-Methods','GET, POST, OPTIONS');
 if(req.method==='OPTIONS')return res.writeHead(204).end();
 const send=(body,status=200)=>res.writeHead(status).end(JSON.stringify(body));
 if(url.pathname==='/api/auth/sessao')return send({autenticado});
 if(url.pathname==='/api/auth/logout'){autenticado=false;return send({message:'Sessão encerrada.'});}
 if(url.pathname==='/api/avaliacoes/minhas'){
  if(modo==='expirada'){autenticado=false;return send({detail:'Sessão expirada'},401);}
  if(modo==='erro-lista')return send({detail:'Indisponível'},503);
  const pagina=Number(url.searchParams.get('pagina')??1);return send({itens:modo==='vazia'?[]:itens.slice((pagina-1)*10,pagina*10),total:modo==='vazia'?0:12,pagina,tamanho:10});
 }
 if(url.pathname==='/api/auth/reenviar-confirmacao'){
  let body='';for await(const chunk of req)body+=chunk;envios.push(JSON.parse(body));
  if(modo==='rede'){res.destroy();return;}
  if(['429','503'].includes(modo)){res.setHeader('Retry-After','37');res.setHeader('Access-Control-Expose-Headers','Retry-After');return send({detail:'INTERNO'},Number(modo));}
  return send({message:'Se o endereço informado possuir uma conta pendente, enviaremos um novo link de confirmação.'},202);
 }
 if(url.pathname==='/api/auth/confirmar')return send({detail:'Token inválido'},400);
 if(url.pathname==='/api/professores')return send(professores);
 if(url.pathname==='/api/disciplinas')return send(disciplinas);
 if(url.pathname==='/api/agradecimentos')return send([]);
 return send({},404);
});
await comNavegador({fixture,executar:async({cdp,avaliar,aguardar})=>{
 const navegar=async path=>{await cdp('Page.navigate',{url:'http://localhost:3100'+path});await aguardar(()=>avaliar('!!document.querySelector("main h1")'),'página');await avaliar('document.fonts.ready');};
 const esperar=texto=>aguardar(()=>avaliar(`document.querySelector('main').innerText.includes(${JSON.stringify(texto)})`),texto);
 const clicar=texto=>avaliar(`Array.from(document.querySelectorAll('main button')).find(b=>b.textContent.trim()===${JSON.stringify(texto)}).click()`);
 for(const width of [320,768,1280])for(const tema of ['light','dark']){
  await cdp('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});await cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:tema}]});
  for(const path of ['/login','/reenviar-confirmacao','/professores','/disciplinas']){
   await navegar(path);
   if(path==='/login')await esperar('12 avaliações enviadas');
   if(['/professores','/disciplinas'].includes(path))await aguardar(()=>avaliar('!!document.querySelector("section[aria-label^=\\"Catálogo de\\"] h3")'),'cartões do catálogo');
   assert.equal(await avaliar('document.documentElement.scrollWidth<=innerWidth'),true,`${path} ${width} ${tema}`);
   assert.equal(await avaliar('document.querySelectorAll("main h1").length'),1);
   assert.equal(await avaliar('[...document.querySelectorAll("input")].every(i=>!!i.labels?.length)'),true);
   if(process.env.PREVIEW_DIR){await mkdir(process.env.PREVIEW_DIR,{recursive:true});const shot=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});await writeFile(`${process.env.PREVIEW_DIR}/${path.slice(1)}-${tema}-${width}.png`,Buffer.from(shot.data,'base64'));}
  }
 }
 await navegar('/login');await esperar('12 avaliações enviadas');assert.equal(await avaliar('document.querySelectorAll("#minhas-avaliacoes-titulo").length'),1);
 assert.ok(await avaliar('document.querySelector("main").innerText.includes("Não disponibiliza")'));
 await clicar('Próxima');await esperar('Página 2 de 2');assert.equal(await avaliar('document.querySelectorAll("main li").length'),2);
 await clicar('Anterior');await esperar('Página 1 de 2');
 modo='erro-lista';await navegar('/login');await esperar('Serviço temporariamente indisponível.');modo='ok';await clicar('Tentar novamente');await esperar('12 avaliações enviadas');
 modo='vazia';await navegar('/login');await esperar('Você ainda não enviou avaliações.');modo='ok';
 modo='expirada';await navegar('/login');await esperar('Esqueci minha senha');modo='ok';autenticado=true;await navegar('/login');await esperar('12 avaliações enviadas');
 await clicar('Sair');await esperar('Esqueci minha senha');assert.equal(await avaliar('!!document.querySelector("#minhas-avaliacoes-titulo")'),false);
 const retorno=`/professores/${uuid(50)}/disciplinas/${uuid(1)}/avaliar`;
 await navegar('/reenviar-confirmacao?returnTo='+encodeURIComponent(retorno));
 await avaliar(`const i=document.querySelector('[name=email]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,'teste@aluno.unb.br');i.dispatchEvent(new Event('input',{bubbles:true}));`);
 for(const falha of ['rede','429','503']){modo=falha;await avaliar('document.querySelector("main form").requestSubmit()');await esperar(falha==='rede'?'Não foi possível solicitar':'Aguarde 37 segundos');assert.equal(await avaliar('document.querySelector("[name=email]").value'),'teste@aluno.unb.br');assert.equal(await avaliar('document.querySelector("main").innerText.includes("INTERNO")'),false);}
 modo='ok';await avaliar('document.querySelector("main form").requestSubmit()');await esperar('Confira também a pasta de spam');assert.deepEqual(envios.at(-1),{email:'teste@aluno.unb.br',return_to:retorno});
 assert.equal(await avaliar('document.querySelector("a[href^=\\"/login?\\"]").getAttribute("href")'),'/login?returnTo='+encodeURIComponent(retorno));
 await navegar('/reenviar-confirmacao?returnTo=https://outro.example');await avaliar(`document.querySelector('[name=email]').value='teste@aluno.unb.br';document.querySelector('main form').requestSubmit()`);await esperar('Confira também');assert.deepEqual(envios.at(-1),{email:'teste@aluno.unb.br'});
 await navegar('/confirmar-email?token='+'x'.repeat(43));await esperar('Solicitar novo link de confirmação');
 assert.equal(await avaliar('document.querySelector("a[href=\\"/reenviar-confirmacao\\"]").textContent'),'Solicitar novo link de confirmação');
 console.log('Revisão final: 24 combinações de tela/largura/tema, catálogo em cartões, conta privada, paginação, vazio, erro/retry, saída, reenvio e retorno seguro aprovados.');
}});
