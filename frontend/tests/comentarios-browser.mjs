let publicacaoAutomatica = false;
import { lerTextoPagina } from "./browser-navigation.mjs";
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { readFileSync } from 'node:fs';
import { comNavegador } from './browser-session.mjs';

const real = process.env.COMENTARIOS_FIXTURE_FILE ? JSON.parse(readFileSync(process.env.COMENTARIOS_FIXTURE_FILE, 'utf8')) : null;
const uuid = i => `${String(i).padStart(8,'0')}-1111-4111-8111-111111111111`;
const professorId = real?.professorId ?? uuid(1), disciplinaId = real?.disciplinaId ?? uuid(2);
const versaoId = real?.versaoId ?? uuid(3), avaliacaoId = uuid(4);
let conta = null, statusConsulta = 200, atraso = 0, statusRetirada = 200;
const data = '2026-11-03T12:00:00Z';
const criar = (i, estado, texto = `Texto ${estado} <script>window.injecao=true</script> ${'L'.repeat(430)}`) => ({ id: uuid(i), avaliacao_id:avaliacaoId, texto, estado, substitui_id:null, created_at:data, updated_at:data });
let itens = [criar(3,'PUBLICADO'), criar(5,'PENDENTE'), criar(6,'SUSPENSO'), criar(7,'REMOVIDO',null), criar(8,'RETIRADO',null), criar(9,'SUBSTITUIDO',null), criar(10,'REJEITADO',null)];
itens[1].substitui_id = versaoId;
const autor = real?.outraConta ?? { email:'autor@aluno.unb.br', senha:'Fixture-123!' };
const naoConfirmado = real?.denunciante ?? { email:'nao-confirmado@aluno.unb.br', senha:'Fixture-123!' };
const envios = [];
const fixture = createServer(async (req,res) => {
  res.setHeader('Access-Control-Allow-Origin','http://localhost:3100');
  res.setHeader('Access-Control-Allow-Credentials','true');
  res.setHeader('Access-Control-Allow-Headers','Content-Type');
  res.setHeader('Access-Control-Allow-Methods','GET,POST,PATCH,OPTIONS');
  res.setHeader('Content-Type','application/json');
  const responder = (s, b) => { if (!res.destroyed) res.writeHead(s).end(JSON.stringify(b)); };
  if (req.method === 'OPTIONS') { res.writeHead(204).end(); return; }
  const url = new URL(req.url,'http://localhost:8000');
  if (url.pathname === '/api/agradecimentos') { responder(401,{}); return; }
  if (url.pathname === '/api/auth/sessao') { responder(200,{ autenticado:!!conta }); return; }
  let body=''; for await (const parte of req) body+=parte;
  const dados = body ? JSON.parse(body) : null;
  if (url.pathname === '/api/auth/login') {
    conta = dados.email;
    res.setHeader('Set-Cookie','fixture=conta; Path=/; HttpOnly; SameSite=Lax');
    responder(200,{message:'Autenticação realizada.'}); return;
  }
  if (url.pathname === '/api/auth/logout') { conta=null; responder(200,{message:'Sessão encerrada.'}); return; }
  if (url.pathname === `/api/professores/${professorId}/disciplinas/${disciplinaId}`) {
    responder(200,{ professor_id:professorId, disciplina_id:disciplinaId, professor:{id:professorId,nome:'Professor RF20',departamento:'CIC'}, disciplina:{id:disciplinaId,nome:'Disciplina RF20',codigo:'CIC0099',departamento:'CIC'},total_avaliacoes:1,dados_suficientes:false }); return;
  }
  if (url.pathname === `/api/professores/${professorId}/disciplinas/${disciplinaId}/comentarios`) { responder(200,itens.filter(v=>v.estado==='PUBLICADO')); return; }
  const status = !conta ? 401 : conta === naoConfirmado.email ? 403 : 200;
  if (status !== 200) { responder(status,{detail:'Não autorizado'}); return; }
  if (url.pathname === '/api/comentarios/meu') {
    assert.equal(url.searchParams.get('professor_id'),professorId);
    assert.equal(url.searchParams.get('disciplina_id'),disciplinaId);
    const resposta=structuredClone(itens), codigo=statusConsulta;
    setTimeout(()=>responder(codigo,codigo===200?resposta:{detail:'Falha privada: não exibir'}),atraso); return;
  }
  if (url.pathname === '/api/avaliacoes') {
    envios.push(dados);
    let comentario_erro=null;
    if (dados.comentario !== undefined) {
      const texto = dados.comentario.trim();
      if (!texto || [...texto].length>500) comentario_erro='invalido';
      else { itens=itens.filter(v=>v.estado!=='PENDENTE'); itens.push({...criar(11,publicacaoAutomatica?'PUBLICADO':'PENDENTE',texto),substitui_id:versaoId}); }
    }
    responder(200,{id:avaliacaoId,comentario_erro,comentario_estado:dados.comentario&&!comentario_erro?(publicacaoAutomatica?'PUBLICADO':'PENDENTE'):null}); return;
  }
  if (url.pathname.endsWith('/retirar') && req.method==='PATCH') {
    if(statusRetirada!==200){responder(statusRetirada,{});return;}
    const id=url.pathname.split('/')[3],item=itens.find(v=>v.id===id);
    itens=itens.filter(v=>v.estado!=='PENDENTE'||v.id===id).map(v=>['PUBLICADO','SUSPENSO','PENDENTE'].includes(v.estado)?{...v,estado:'RETIRADO'}:v);
    responder(200,{...item,estado:'RETIRADO'});return;
  }
  responder(404,{});
});

await comNavegador({ fixture:real?null:fixture, executar:async ({cdp,avaliar,aguardar}) => {
  const texto=()=>lerTextoPagina(avaliar);
  const esperar=t=>aguardar(async()=>(await texto()).includes(t),t);
  const clicar=async t=>{await avaliar(`Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()===${JSON.stringify(t)})?.click()`);};
  const navegar=async path=>{await cdp('Page.navigate',{url:`http://localhost:3100${path}`});};
  const caminho=`/professores/${professorId}/disciplinas/${disciplinaId}`;
  const getComentarios=()=>avaliar(`fetch('http://localhost:8000/api/comentarios/meu?professor_id=${professorId}&disciplina_id=${disciplinaId}',{credentials:'include',cache:'no-store'}).then(r=>r.json())`);
  async function login(dados){
    // Conta ativa mostra Minha conta; aguardar o estado verificado antes de trocar a sessão.
    await navegar('/login');
    await aguardar(async()=>await avaliar(`!!document.querySelector('input[name="email"]') || document.body?.innerText.includes('Sua sessão está ativa')`),'sessão de login');
    if ((await texto()).includes('Sua sessão está ativa')) await clicar('Sair');
    await aguardar(async()=>await avaliar(`!!document.querySelector('input[name="email"]')`),'login pronto');
    await avaliar(`for(const [nome,valor] of Object.entries(${JSON.stringify(dados)})){const i=document.querySelector('input[name="'+nome+'"]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(i,valor);i.dispatchEvent(new Event('input',{bubbles:true}));}`);
    await clicar('Entrar'); await esperar('Sua sessão está ativa');
  }
  async function preencher(comentario=''){
    await avaliar(`document.querySelector('input[name="didatica"][value="4"]').click();for(const [nome,valor] of Object.entries({dificuldade:'MEDIO',chamada:'true',material:'BOM',recomenda:'true'})){document.querySelector('input[name="'+nome+'"][value="'+valor+'"]').click();}const t=document.querySelector('textarea');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(t,${JSON.stringify(comentario)});t.dispatchEvent(new Event('input',{bubbles:true}));`);
  }
  await navegar(caminho+'/avaliar'); await esperar('Enviar avaliação');
  await aguardar(async()=>!(await texto()).includes('Carregando seus comentários'),'consulta visitante');
  assert.ok(!(await texto()).includes('Meus comentários'));
  await login(naoConfirmado); await navegar(caminho+'/avaliar'); await esperar('Enviar avaliação');
  await aguardar(async()=>!(await texto()).includes('Carregando seus comentários'),'consulta não confirmada');
  assert.ok(!(await texto()).includes('Meus comentários'));
  await preencher('Tentativa não confirmada'); await clicar('Enviar avaliação'); await esperar('O envio não foi autorizado');
  await login(autor); await navegar(caminho+'/avaliar'); await esperar('Meus comentários');
  if(!real){for(const t of ['Em análise','Publicado','Temporariamente indisponível','Removido','Retirado','Substituído','Rejeitado','O texto desta versão não está mais disponível'])await esperar(t);}
  for(const tema of ['light','dark'])for(const largura of [320,390,768,1440]){
    await cdp('Emulation.setDeviceMetricsOverride',{width:largura,height:900,deviceScaleFactor:1,mobile:largura===320});
    await cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:tema}]});
    assert.equal(await avaliar('document.documentElement.scrollWidth<=innerWidth'),true,`${tema}/${largura}`);
  }
  assert.equal(await avaliar('window.injecao'),undefined);
  // Reenvio sem texto preserva a versão pública. Texto inválido não bloqueia critérios.
  const antes=await getComentarios();
  await preencher(); await clicar('Enviar avaliação'); await esperar('Avaliação registrada com sucesso');
  assert.deepEqual((await getComentarios()).map(v=>[v.id,v.estado]),antes.map(v=>[v.id,v.estado]));
  await preencher(' '.repeat(3)); await clicar('Enviar avaliação'); await esperar('Seus critérios foram salvos, mas o comentário não foi enviado');
  for (const [limite, invalido] of [[500,false],[501,true],[1,false]]) {
    await preencher('x'.repeat(limite)); await clicar('Enviar avaliação');
    await esperar(invalido ? 'Seus critérios foram salvos, mas o comentário não foi enviado' : 'Seu novo texto foi enviado');
    const pendenteLimite = (await getComentarios()).find(v=>v.estado==='PENDENTE');
    assert.equal(pendenteLimite.texto.length, invalido ? 500 : limite);
  }
  const novo='Texto novo da interface RF20';
  await preencher(novo); await clicar('Enviar avaliação'); await esperar('Seu novo texto foi enviado para aprovação humana'); await esperar(novo);
  let versoes=await getComentarios();
  assert.ok(versoes.some(v=>v.estado==='PUBLICADO'&&v.id===versaoId));
  let pendente=versoes.find(v=>v.estado==='PENDENTE'); assert.equal(pendente.texto,novo); assert.equal(pendente.substitui_id,versaoId);
  if(real){
    const sessao=await fetch('http://127.0.0.1:8000/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(real.moderador)});
    const cookie=sessao.headers.getSetCookie().map(v=>v.split(';')[0]).join('; ');
    const rejeitar=await fetch(`http://127.0.0.1:8000/api/moderacao/comentarios/${pendente.id}/acoes`,{method:'POST',headers:{'Content-Type':'application/json',Cookie:cookie},body:JSON.stringify({acao:'REJEITAR',motivo:'Fixture de rejeição RF20'})});
    assert.equal(rejeitar.status,200);
    await navegar(caminho+'/avaliar'); await esperar('Rejeitado'); await esperar('O texto desta versão não está mais disponível');
    versoes=await getComentarios(); assert.ok(versoes.some(v=>v.id===versaoId&&v.estado==='PUBLICADO'));
    await preencher('Segundo substituto'); await clicar('Enviar avaliação'); await esperar('Seu novo texto foi enviado');
  }
  await aguardar(async()=>await avaliar(`!!document.querySelector('[aria-label="Retirar comentário ${versaoId}"]:not(:disabled)')`),'retirada disponível');
  await avaliar(`document.querySelector('[aria-label="Retirar comentário ${versaoId}"]').click()`); await esperar('Deseja continuar?');
  if(!real){statusRetirada=503;await clicar('Confirmar retirada');await esperar('Não foi possível confirmar a retirada');statusRetirada=200;}
  await clicar('Confirmar retirada'); await esperar('Comentário retirado.');
  versoes=await getComentarios(); assert.ok(!versoes.some(v=>['PUBLICADO','PENDENTE','SUSPENSO'].includes(v.estado)));
  if(!real){
    statusConsulta=503;
    await avaliar(`window.dispatchEvent(new Event('undb:sessao-alterada'))`); await esperar('Não foi possível carregar seus comentários');
    assert.ok(!(await texto()).includes('Texto PUBLICADO')); statusConsulta=200;
    await clicar('Tentar novamente'); await esperar('Meus comentários');
    atraso=400; await avaliar(`window.dispatchEvent(new Event('undb:sessao-alterada'))`);
    conta=null; atraso=0; await avaliar(`window.dispatchEvent(new Event('undb:sessao-alterada'))`);
    await aguardar(async()=>!(await texto()).includes('Carregando seus comentários'),'sessão encerrada');
    await new Promise(r=>setTimeout(r,600)); assert.ok(!(await texto()).includes('Meus comentários'),'resposta antiga não reaparece');
    conta=autor.email; itens=[]; await avaliar(`window.dispatchEvent(new Event('undb:sessao-alterada'))`); await esperar('Você ainda não possui comentários');
  }
  if(!real){publicacaoAutomatica=true;await preencher('Texto adequado para publicação automática.');await clicar('Enviar avaliação');await esperar('Seu comentário foi publicado após a triagem automática.');}
  console.log(`RF20 aprovado (${real?'API/PostgreSQL reais':'HTTP controlado'}): permissões, estados, texto descartado, envio/substituição/retirada, critérios preservados, erros e oito combinações de tema/largura.`);
}});
