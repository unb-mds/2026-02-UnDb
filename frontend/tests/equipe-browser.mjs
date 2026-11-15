import assert from 'node:assert/strict';
import { readFile, mkdir, writeFile } from 'node:fs/promises';
import { comNavegador } from './browser-session.mjs';
const nomes=['Nicolas Zanin','Gabriel Araujo','Yasmin Loiola','Tiago Vieira','Warlley Medeiros','Vinicius Gavaldao'];
await comNavegador({executar:async({cdp,avaliar,aguardar})=>{
 const resposta=await fetch('http://localhost:3100/sobre');assert.equal(resposta.status,200);const html=await resposta.text();for(const nome of nomes)assert.ok(html.includes(nome));assert.ok(html.includes('https://www.linkedin.com/in/tiago-vieira-85a721325/'));
 const imagem=await fetch('http://localhost:3100/equipe/TiagoVieira-596.jpg');assert.equal(imagem.status,200);assert.match(imagem.headers.get('content-type'),/image\/jpeg/);assert.deepEqual(Buffer.from(await imagem.arrayBuffer()),await readFile(new URL('../public/equipe/TiagoVieira-596.jpg',import.meta.url)));
 for(const width of [320,768,1280]){
  await cdp('Emulation.setDeviceMetricsOverride',{width,height:900,deviceScaleFactor:1,mobile:false});await cdp('Page.navigate',{url:'http://localhost:3100/sobre#equipe'});await aguardar(()=>avaliar('!!document.querySelector("#equipe")'),'equipe');await avaliar('document.fonts.ready');
  await avaliar('document.querySelectorAll("#equipe img").forEach(i=>{i.loading="eager";})');await aguardar(()=>avaliar('[...document.querySelectorAll("#equipe img")].every(i=>i.complete&&i.naturalWidth>0)'),'fotos');assert.equal(await avaliar('document.documentElement.scrollWidth<=innerWidth'),true);
  if(process.env.PREVIEW_DIR){await mkdir(process.env.PREVIEW_DIR,{recursive:true});const s=await cdp('Page.captureScreenshot',{format:'png'});await writeFile(`${process.env.PREVIEW_DIR}/equipe-${width}.png`,Buffer.from(s.data,'base64'));}
 }
 console.log('Equipe: seis nomes completos no HTML, foto JPEG pública idêntica ao arquivo e layout sem overflow em 320/768/1280 px.');
}});
