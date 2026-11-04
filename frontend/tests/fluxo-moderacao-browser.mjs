// Percurso integrado de RF20–RF22: três interfaces reais, sem mock de HTTP ou autorização.
import assert from 'node:assert/strict';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { comNavegador } from './browser-session.mjs';
import { lerTextoPagina } from './browser-navigation.mjs';

assert.ok(process.env.FLUXO_MODERACAO_FIXTURE_FILE, 'Use fixture sintética e API/PostgreSQL descartáveis.');
const fixture = JSON.parse(readFileSync(process.env.FLUXO_MODERACAO_FIXTURE_FILE, 'utf8'));
const { professorId, disciplinaId } = fixture;
const caminho = `/professores/${professorId}/disciplinas/${disciplinaId}`;
const critica = 'A explicação foi confusa e faltaram exemplos. Sugiro exercícios resolvidos em aula.';
const segundoTexto = 'Nova observação acadêmica, novamente sujeita à aprovação humana.';

await comNavegador({ executar: async ({ cdp, avaliar, aguardar }) => {
  const texto = () => lerTextoPagina(avaliar);
  const esperar = valor => aguardar(async () => (await texto()).includes(valor), valor);
  const navegar = path => cdp('Page.navigate', {url:`http://localhost:3100${path}`});
  const clicar = rotulo => avaliar(`Array.from(document.querySelectorAll('button')).find(b=>b.textContent.trim()===${JSON.stringify(rotulo)})?.click()`);
  const get = path => avaliar(`fetch('http://localhost:8000'+${JSON.stringify(path)},{credentials:'include',cache:'no-store'}).then(async r=>({status:r.status,body:await r.json()}))`);
  const meus = async () => {
    const r = await get(`/api/comentarios/meu?professor_id=${professorId}&disciplina_id=${disciplinaId}`);
    assert.equal(r.status,200); return r.body;
  };
  const publicos = async () => {
    const r = await get(`/api/professores/${professorId}/disciplinas/${disciplinaId}/comentarios`);
    assert.equal(r.status,200);
    for (const item of r.body) assert.deepEqual(Object.keys(item).sort(),['created_at','id','texto']);
    return r.body;
  };
  async function login(conta) {
    await navegar('/login');
    await aguardar(async()=>await avaliar(`!!document.querySelector('input[name="email"]') || !!document.body?.innerText.includes('Sua sessão está ativa')`),'sessão carregada');
    if ((await texto()).includes('Sua sessão está ativa')) await clicar('Sair');
    await aguardar(async()=>await avaliar(`!!document.querySelector('input[name="email"]')`),'formulário de login');
    await avaliar(`for(const [nome,valor] of Object.entries(${JSON.stringify(conta)})){const input=document.querySelector('input[name="'+nome+'"]');Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(input,valor);input.dispatchEvent(new Event('input',{bubbles:true}));}`);
    await clicar('Entrar'); await esperar('Sua sessão está ativa');
  }
  async function sair() {
    await navegar('/login'); await esperar('Sua sessão está ativa'); await clicar('Sair');
    await aguardar(async()=>await avaliar(`!!document.querySelector('input[name="email"]')`),'logout');
  }
  async function enviar(textoNovo) {
    await navegar(caminho+'/avaliar'); await esperar('Meus comentários');
    await avaliar(`document.querySelector('input[name="didatica"][value="4"]').click();for(const [nome,valor] of Object.entries({dificuldade:'MEDIO',chamada:'true',material:'BOM',recomenda:'true'})){const select=document.querySelector('select[name="'+nome+'"]');select.value=valor;select.dispatchEvent(new Event('change',{bubbles:true}));}const campo=document.querySelector('textarea[name="comentario"]');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(campo,${JSON.stringify(textoNovo)});campo.dispatchEvent(new Event('input',{bubbles:true}));`);
    await clicar('Enviar avaliação'); await esperar('Seu novo texto foi enviado para aprovação humana');
    await esperar(textoNovo);
    const pendente=(await meus()).find(v=>v.estado==='PENDENTE');
    assert.equal(pendente.texto,textoNovo); return pendente;
  }
  async function analisar(id) {
    await navegar('/moderacao'); await esperar('Fila de moderação');
    await aguardar(async()=>{
      if (await avaliar(`Array.from(document.querySelectorAll('[aria-label="Comentários na fila"] button')).some(b=>b.textContent.includes(${JSON.stringify(id)}) && b.getAttribute('aria-pressed')==='true')`)) return true;
      await avaliar(`Array.from(document.querySelectorAll('[aria-label="Comentários na fila"] button')).find(b=>b.textContent.includes(${JSON.stringify(id)}))?.click()`);
      return false;
    },'comentário selecionado');
    await aguardar(async()=>await avaliar(`!!document.querySelector('#acao-moderacao') && !!document.querySelector('[aria-label="Análise do comentário"]')?.innerText.includes(${JSON.stringify(id)})`),'análise interativa');
  }
  async function decidir(acao, estadoEsperado) {
    assert.equal(await avaliar(`document.querySelector('button[type="submit"]').disabled`),true,'motivo obrigatório');
    await avaliar(`const select=document.querySelector('#acao-moderacao');select.value=${JSON.stringify(acao)};select.dispatchEvent(new Event('change',{bubbles:true}));const motivo=document.querySelector('#motivo-moderacao');Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,'value').set.call(motivo,'Revisão humana de fixture: conteúdo acadêmico analisado conforme política.');motivo.dispatchEvent(new Event('input',{bubbles:true}));`);
    await aguardar(async()=>!(await avaliar(`document.querySelector('button[type="submit"]').disabled`)),'decisão disponível');
    await clicar('Confirmar decisão');
    await esperar(`Decisão registrada. Estado retornado: ${estadoEsperado}.`);
  }
  async function denunciar(id, esperado='registrada') {
    await navegar(caminho); await esperar('Comentários');
    await aguardar(async()=>{
      await avaliar(`document.querySelector('[data-testid="botao-denunciar-${id}"]')?.click()`);
      return (await texto()).includes('Denunciar comentário');
    },'denúncia interativa');
    await avaliar(`document.querySelector('#motivo-SPAM').click()`);
    await clicar('Confirmar denúncia'); await esperar(esperado);
    await clicar(esperado==='registrada'?'Fechar':'Cancelar');
  }
  async function layout(etapa) {
    for (const tema of ['light','dark']) for (const largura of [320,768,1280]) {
      await cdp('Emulation.setDeviceMetricsOverride',{width:largura,height:900,deviceScaleFactor:1,mobile:largura===320});
      await cdp('Emulation.setEmulatedMedia',{features:[{name:'prefers-color-scheme',value:tema}]});
      assert.equal(await avaliar('document.documentElement.scrollWidth<=innerWidth'),true,`${etapa}/${tema}/${largura}`);
      if (process.env.PREVIEW_DIR && largura===320 && tema==='dark') {
        mkdirSync(process.env.PREVIEW_DIR,{recursive:true});
        const captura=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
        writeFileSync(join(process.env.PREVIEW_DIR,`${etapa}-${largura}-${tema}.png`),Buffer.from(captura.data,'base64'));
      }
    }
  }

  await login(fixture.outraConta);
  const pendente = await enviar(critica);
  assert.ok(!(await publicos()).some(v=>v.id===pendente.id),'pendente não é público');
  await layout('autor-pendente');
  await navegar('/moderacao'); await esperar('Acesso não permitido');
  assert.equal((await get(`/api/moderacao/comentarios/${pendente.id}/denuncias`)).status,403);

  await login(fixture.moderador); await analisar(pendente.id);
  await esperar('Críticas acadêmicas negativas são permitidas');
  await layout('moderacao-pendente'); await decidir('APROVAR','Publicado');
  assert.deepEqual((await publicos()).map(v=>v.id),[pendente.id]);
  assert.ok(!(await publicos()).some(v=>v.id===fixture.versaoId),'substituição não conserva anterior público');

  await sair();
  await navegar('/moderacao'); await esperar('Entre na sua conta');
  await navegar(caminho); await esperar(critica); await layout('publico');
  for (const conta of [fixture.outraConta,fixture.denunciante,fixture.moderador]) assert.ok(!(await texto()).includes(conta.email),'identidade não pública');
  await denunciar(pendente.id); await denunciar(pendente.id);

  await login(fixture.denunciante);
  await navegar('/moderacao'); await esperar('Acesso não permitido');
  await denunciar(pendente.id); await denunciar(pendente.id,'Você já possui uma denúncia aberta');
  assert.equal((await get(`/api/moderacao/comentarios/${pendente.id}/denuncias`)).status,403);

  await login(fixture.moderador); await analisar(pendente.id);
  await esperar('Contas distintas: 1 · Relatos de visitantes: 2');
  const relatos=await get(`/api/moderacao/comentarios/${pendente.id}/denuncias`);
  assert.equal(relatos.body.autenticadas[0].denunciante.email,fixture.denunciante.email);
  await layout('moderacao-denunciado'); await decidir('MANTER','Publicado');
  assert.equal((await get(`/api/moderacao/comentarios/${pendente.id}/denuncias`)).body.contas_distintas,0);

  await login(fixture.denunciante); assert.deepEqual((await get('/api/agradecimentos')).body,[]);
  await denunciar(pendente.id);
  await login(fixture.moderador); await analisar(pendente.id); await decidir('REMOVER','Removido');
  assert.deepEqual(await publicos(),[]);
  // Confirmar exibição exige documento montado e visível; entrar não consome sozinho.
  const gate=await cdp('Page.addScriptToEvaluateOnNewDocument',{source:`Object.defineProperty(document,'visibilityState',{configurable:true,get:()=> 'hidden'});`});
  await login(fixture.denunciante); await esperar('Obrigado por contribuir');
  const avisos=(await get('/api/agradecimentos')).body;
  assert.equal(avisos.length,1); assert.deepEqual(Object.keys(avisos[0]).sort(),['id','mensagem']);
  await layout('agradecimento');
  await avaliar(`Object.defineProperty(document,'visibilityState',{configurable:true,get:()=> 'visible'});document.dispatchEvent(new Event('visibilitychange'));`);
  await aguardar(async()=>((await get('/api/agradecimentos')).body.length===0),'agradecimento consumido após exibição');
  await cdp('Page.removeScriptToEvaluateOnNewDocument',{identifier:gate.identifier});

  await login(fixture.outraConta);
  const novo=await enviar(segundoTexto);
  assert.deepEqual(await publicos(),[],'edição não restaura removido');
  await login(fixture.moderador); await analisar(novo.id); await decidir('APROVAR','Publicado');
  await login(fixture.outraConta); await enviar('Outro substituto que será cancelado pela retirada.');
  await aguardar(async()=>await avaliar(`!!document.querySelector('[aria-label="Retirar comentário ${novo.id}"]:not(:disabled)')`),'retirada disponível');
  await avaliar(`document.querySelector('[aria-label="Retirar comentário ${novo.id}"]').click()`);
  await clicar('Confirmar retirada'); await esperar('Comentário retirado.');
  assert.ok(!(await meus()).some(v=>['PUBLICADO','PENDENTE','SUSPENSO'].includes(v.estado)));
  assert.deepEqual(await publicos(),[]);
  await login(fixture.moderador); await navegar('/moderacao'); await esperar('Nenhum comentário aguardando moderação');
  console.log('Issue #163: autor → aprovação humana → leitura pública → denúncias visitante/conta não confirmada → manter/remover → agradecimento → nova aprovação → retirada. API/PostgreSQL reais, três interfaces integradas, privacidade e 30 combinações de etapa/largura/tema aprovadas.');
}});
