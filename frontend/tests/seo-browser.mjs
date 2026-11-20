// #254: HTTP/HTML inicial e catálogo controlado, sem alterar produção.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import { comNavegador } from './browser-session.mjs';
const pid='11111111-1111-4111-8111-111111111111', did='22222222-2222-4222-8222-222222222222';
const professor={id:pid,nome:'Professor de teste',departamento:'CIC',siape:null,identidade_confirmada:true};
const disciplina={id:did,nome:'Algoritmos de teste',codigo:'CIC0001',departamento:'CIC',creditos:null,identificador_externo:null};
const professores=Array.from({length:101},(_,i)=>({...professor,id:i===0?pid:`11111111-1111-4111-8111-${String(i).padStart(12,'0')}`}));
const chamadas=[];let falha=false;
const fixture=createServer((req,res)=>{
 const url=new URL(req.url,'http://localhost');chamadas.push(url.pathname);
 res.setHeader('Content-Type','application/json');res.setHeader('Access-Control-Allow-Origin','http://localhost:3100');res.setHeader('Access-Control-Allow-Credentials','true');
 const send=(s,b)=>res.writeHead(s).end(JSON.stringify(b));
 if(falha&&url.pathname.startsWith('/api/professores'))return send(503,{detail:'Indisponível'});
 if(url.pathname==='/api/professores')return send(200,professores);
 if(url.pathname==='/api/disciplinas')return send(200,[disciplina]);
 if(url.pathname===`/api/professores/${pid}`)return send(200,professor);
 if(url.pathname===`/api/professores/${pid}/disciplinas`)return send(200,[disciplina]);
 if(url.pathname===`/api/disciplinas/${did}`)return send(200,disciplina);
 if(url.pathname===`/api/disciplinas/${did}/turmas`)return send(200,[]);
 if(url.pathname===`/api/disciplinas/${did}/professores`)return send(200,{disciplina,professores:[]});
 if(url.pathname===`/api/professores/${pid}/disciplinas/${did}`)return send(200,{professor_id:pid,disciplina_id:did,professor,disciplina,total_avaliacoes:0,dados_suficientes:false});
 if(url.pathname.endsWith('/comentarios')||url.pathname==='/api/agradecimentos')return send(200,[]);
 if(url.pathname==='/api/auth/sessao')return send(200,{autenticado:false});
 return send(404,{detail:'Não encontrado'});
});
await comNavegador({fixture,executar:async({avaliar,cdp,aguardar})=>{
 const request=path=>fetch('http://localhost:3100'+path,{headers:{'User-Agent':'WhatsApp/2.24'}});
 const parse=html=>avaliar(`const p=new DOMParser().parseFromString(${JSON.stringify(html)},'text/html');({title:p.title,canonical:p.head.querySelector('link[rel=canonical]')?.href,og:p.head.querySelector('meta[property="og:url"]')?.content,image:p.head.querySelector('meta[property="og:image"]')?.content,robots:p.head.querySelector('meta[name=robots]')?.content,links:[...p.querySelectorAll('a')].map(a=>a.getAttribute('href'))})`);
 for(const [path,title]of [['/','UnDb | Avaliações'],[`/professores/${pid}?busca=professores&q=teste&ordem=nome`,'Professor de teste'],[`/disciplinas/${did}`,'Algoritmos de teste'],[`/professores/${pid}/disciplinas/${did}`,'Professor de teste em Algoritmos de teste']]){
  chamadas.length=0;const response=await request(path);assert.equal(response.status,200,path);const m=await parse(await response.text());assert.ok(m.title.includes(title));assert.equal(m.canonical,'https://undb.app.br'+path.split('?')[0]);assert.equal(new URL(m.og).href,m.canonical);assert.equal(m.image,'https://undb.app.br/undb-preview.png');
  if(path.startsWith('/professores/'+pid+'?'))assert.equal(chamadas.filter(p=>p===`/api/professores/${pid}`).length,1,'metadados e página compartilham a consulta');
 }
 for(const path of ['/login','/cadastro','/confirmar-email?token=ficticio','/moderacao','/prototipo','/professores?q=teste','/departamentos',`/professores/${pid}/disciplinas/${did}/avaliar`])assert.match((await parse(await(await request(path)).text())).robots,/noindex/,path);
 const lista=await parse(await(await request('/professores')).text());assert.ok(lista.links.some(link=>/^\/professores\/[a-f0-9-]{36}$/.test(link)));assert.ok(lista.links.includes('/catalogo/professores/1'));
 assert.equal((await request('/catalogo/professores/1')).status,200);assert.equal((await request('/catalogo/professores/8')).status,200);assert.equal((await request('/catalogo/professores/9')).status,404);
 const catalogados=[];
 for(let pagina=0;pagina<9;pagina++){
  const m=await parse(await(await request(pagina===0?'/professores':`/catalogo/professores/${pagina}`)).text());
  const links=m.links.filter(link=>/^\/professores\/[a-f0-9-]{36}$/.test(link));
  assert.equal(links.length,pagina===8?5:12,'lotes curtos sem perder o restante do catálogo');catalogados.push(...links);
 }
 assert.equal(new Set(catalogados).size,101,'paginação não duplica nem omite professores');
 assert.equal((await request('/professores/id-invalido')).status,404);assert.equal((await request('/professores/99999999-9999-4999-8999-999999999999')).status,404);
 const robots=await(await request('/robots.txt')).text();assert.match(robots,/Allow: \/\n/);assert.match(robots,/Sitemap: https:\/\/undb.app.br\/sitemap.xml/);assert.doesNotMatch(robots,/Disallow: \/login/);
 const index=await(await request('/sitemap.xml')).text();assert.match(index,/<sitemapindex/);assert.match(index,/sitemaps\/professores\/0.xml/);
 const urls=await(await request('/sitemaps/professores/0.xml')).text();assert.equal((urls.match(/<loc>/g)||[]).length,101);assert.doesNotMatch(urls,/token|login|lastmod|<loc>[^<]*[?#]/);assert.match(urls,new RegExp(pid));
 assert.equal((await request('/sitemaps/professores/999.xml')).status,404);assert.equal((await request('/sitemaps/privado/0.xml')).status,404);
 const png=await request('/undb-preview.png');assert.equal(png.status,200);assert.match(png.headers.get('content-type'),/image\/png/);
 falha=true;assert.equal((await request('/sitemap.xml')).status,503);assert.equal((await request('/sitemaps/professores/0.xml')).status,503);assert.equal((await request(`/professores/${pid}`)).status,500);falha=false;
 // Amostra de laboratório, catálogo sintético e cache frio do navegador; não são CWV reais.
 await cdp('Emulation.setDeviceMetricsOverride',{width:390,height:844,deviceScaleFactor:1,mobile:true});await cdp('Emulation.setCPUThrottlingRate',{rate:4});await cdp('Network.enable');await cdp('Network.setCacheDisabled',{cacheDisabled:true});
 await cdp('Network.emulateNetworkConditions',{offline:false,latency:150,downloadThroughput:200000,uploadThroughput:93750});
 await cdp('Page.addScriptToEvaluateOnNewDocument',{source:`window.__lcp=0;new PerformanceObserver(list=>{window.__lcp=list.getEntries().at(-1)?.startTime??0;}).observe({type:'largest-contentful-paint',buffered:true});`});
 await cdp('Page.navigate',{url:'http://localhost:3100/'});await aguardar(()=>avaliar('document.readyState === "complete" && !!document.querySelector("h1")'),'home mobile');
 await avaliar('new Promise(r=>setTimeout(r,1500))');
 const metricas=await avaliar('const n=performance.getEntriesByType("navigation")[0];({ttfbMs:n.responseStart,domContentLoadedMs:n.domContentLoadedEventEnd,loadMs:n.loadEventEnd,lcpMs:window.__lcp,viewport:[innerWidth,innerHeight]})');
 const pasta=process.env.PREVIEW_DIR;if(pasta){await mkdir(pasta,{recursive:true});await writeFile(pasta+'/seo-mobile-laboratorio.json',JSON.stringify({condicoes:'Brave headless, CPU 4x, 150ms, 1.6Mbps, cache navegador desativado, API sintética local',metricas},null,2));}
 console.log('SEO #254: HTML inicial, canonical, OG/Twitter, noindex, descoberta HTML paginada, sitemap/robots, 404/503/500 e consulta única aprovados. Laboratório:',JSON.stringify(metricas));
}});
