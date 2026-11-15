// RF24: UI com HTTP controlado; persistência é verificada nos testes do backend.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import { comNavegador } from './browser-session.mjs';
let modo='ok';const envios=[];
const fixture=createServer(async(req,res)=>{
 res.setHeader('Access-Control-Allow-Origin','http://localhost:3100');res.setHeader('Access-Control-Allow-Credentials','true');res.setHeader('Access-Control-Allow-Headers','Content-Type');res.setHeader('Access-Control-Allow-Methods','GET, POST, OPTIONS');res.setHeader('Content-Type','application/json');
 if(req.method==='OPTIONS'){res.writeHead(204).end();return;}
 if(req.url==='/api/auth/sessao'){res.end(JSON.stringify({autenticado:false}));return;}
 if(req.url==='/api/agradecimentos'){res.end('[]');return;}
 if(!['/api/auth/recuperar-senha','/api/auth/redefinir-senha'].includes(req.url)){res.writeHead(404).end('{}');return;}
 let body='';for await(const chunk of req)body+=chunk;envios.push({path:req.url,body:JSON.parse(body)});
 await new Promise(r=>setTimeout(r,200));
 if(modo==='rede'){res.destroy();return;}
 if(modo==='invalido'){res.writeHead(400).end(JSON.stringify({detail:'Link inválido ou expirado.'}));return;}
 res.writeHead(req.url.endsWith('/recuperar-senha')?202:200).end(JSON.stringify({message:req.url.endsWith('/recuperar-senha')?'Se o endereço informado possuir uma conta, enviaremos um link para redefinir a senha.':'Senha redefinida. Entre novamente com sua nova senha.'}));
});
await comNavegador({fixture,executar:async({cdp,avaliar,aguardar})=>{
 const navegar=async path=>{await cdp('Page.navigate',{url:'http://localhost:3100'+path});await aguardar(()=>avaliar(`location.pathname===${JSON.stringify(path.split('?')[0])} && !!document.querySelector('main h1')`),'página');await avaliar('document.fonts.ready');await avaliar('new Promise(r=>setTimeout(r,150))');};
 const texto=()=>avaliar('document.querySelector("main")?.innerText??""');
 const esperar=trecho=>aguardar(async()=>(await texto()).includes(trecho),trecho);
 const fill=valores=>avaliar(`Object.entries(${JSON.stringify(valores)}).forEach(([name,value])=>{const i=document.querySelector('[name='+name+']');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,value);i.dispatchEvent(new Event('input',{bubbles:true}));})`);
 const submit=()=>avaliar('document.querySelector("main form").requestSubmit()');
 for(const tema of ['light','dark'])for(const width of [320,768,1280]){
  await cdp('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});await cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:tema}]});
  for(const [nome,path]of [['solicitar','/esqueci-senha'],['redefinir','/redefinir-senha?token='+'x'.repeat(43)],['invalido','/redefinir-senha']]){
   await navegar(path);assert.equal(await avaliar('document.querySelectorAll("main h1").length'),1);assert.equal(await avaliar('document.documentElement.scrollWidth<=innerWidth'),true);assert.equal(await avaliar('!!document.querySelector(".auth-card img")'),true,'moldura atual com logo');
   assert.equal(await avaliar('[...document.querySelectorAll("main input")].every(i=>!!i.labels?.length)'),true);
   await cdp('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await cdp('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});assert.equal(await avaliar('document.activeElement!==document.body'),true);
   if(process.env.PREVIEW_DIR){await mkdir(process.env.PREVIEW_DIR,{recursive:true});const shot=await cdp('Page.captureScreenshot',{format:'png'});await writeFile(`${process.env.PREVIEW_DIR}/senha-${nome}-${tema}-${width}.png`,Buffer.from(shot.data,'base64'));}
  }
 }
 await navegar('/login');await esperar('Esqueci minha senha');
 await navegar('/esqueci-senha');modo='rede';await fill({email:'teste@aluno.unb.br'});await submit();await esperar('Não foi possível solicitar');assert.equal(await avaliar('document.querySelector("[name=email]").value'),'teste@aluno.unb.br');
 modo='ok';await submit();await esperar('Solicitando…');await esperar('Confira também');assert.deepEqual(envios.at(-1),{path:'/api/auth/recuperar-senha',body:{email:'teste@aluno.unb.br'}});
 const path='/redefinir-senha?token='+'x'.repeat(43);await navegar(path);const inicio=envios.length;await fill({senha:'nova senha segura',confirmacao:'senha diferente'});await submit();await esperar('não coincidem');assert.equal(envios.length,inicio);
 await fill({confirmacao:'nova senha segura'});modo='rede';await submit();await esperar('Não foi possível redefinir');assert.equal(await avaliar('document.querySelector("[name=senha]").value'),'nova senha segura');
 modo='ok';await submit();await esperar('Senha redefinida.');assert.equal(await avaliar('location.search'),'');assert.equal(await avaliar('document.querySelector("main form")===null'),true);assert.deepEqual(envios.at(-1).body,{token:'x'.repeat(43),senha:'nova senha segura'});
 await navegar(path);modo='invalido';await fill({senha:'nova senha segura',confirmacao:'nova senha segura'});await submit();await esperar('inválido ou expirado');assert.equal(await avaliar('!!document.querySelector("main a[href=\\"/esqueci-senha\\"]")'),true);
 console.log('RF24: 18 combinações com moldura atual, teclado/rótulos, link de login, carregamento, respostas genéricas, falha/retry, confirmação divergente, sucesso e token inválido aprovados.');
}});
