// #247: apresentação e contratos HTTP controlados; não comprova persistência real.
import assert from 'node:assert/strict';
import { createServer } from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { comNavegador } from './browser-session.mjs';
import { contrasteTexto } from './browser-contrast.mjs';

const antes = process.env.UI247_ANTES === '1';
const pid = '11111111-1111-4111-8111-111111111111';
const did = '22222222-2222-4222-8222-222222222222';
const cid = '33333333-3333-4333-8333-333333333333';
const caminho = `/professores/${pid}/disciplinas/${did}`;
const retorno = `${caminho}/avaliar?busca=disciplinas&q=CIC0001&ordem=nome`;
const query = `?returnTo=${encodeURIComponent(retorno)}`;
let autenticado = false, loginStatus = 200, cadastroStatus = 202, confirmarStatus = 200;
let moderacaoStatus = 200, envioStatus = 200, comentarioErro = null, comentarioEstado = 'PENDENTE';
let envios = 0, cadastros = 0, confirmacoes = 0, reterEnvio = false, liberarEnvio;
const filtrosConsultados = [];
const comentario = { id: cid, texto: 'Relato acadêmico sintético para testar a interface.', estado: 'PENDENTE',
  autor: { id: pid, nome: 'Autor sintético', email: 'autor.teste@aluno.unb.br' },
  substitui_id: null, created_at: '2026-11-14T12:00:00Z' };
const fixture = createServer(async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', 'http://localhost:3100');
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  res.setHeader('Content-Type', 'application/json');
  if (req.method === 'OPTIONS') { res.writeHead(204).end(); return; }
  const url = new URL(req.url, 'http://localhost:8000');
  const responder = (status, corpo) => { if (!res.destroyed) res.writeHead(status).end(JSON.stringify(corpo)); };
  if (url.pathname === '/api/auth/sessao') responder(200, { autenticado });
  else if (url.pathname === '/api/auth/login') {
    req.resume(); autenticado = loginStatus === 200;
    responder(loginStatus, autenticado ? { message: 'Autenticação realizada com sucesso.' } : { detail: 'Credenciais inválidas' });
  } else if (url.pathname === '/api/auth/cadastro') {
    req.resume(); cadastros++;
    responder(cadastroStatus, cadastroStatus === 202 ? { message: 'Se o endereço informado estiver disponível, enviaremos um link de confirmação.' } : { detail: 'Dados inválidos' });
  } else if (url.pathname === '/api/auth/confirmar') {
    req.resume(); confirmacoes++;
    responder(confirmarStatus, confirmarStatus === 200 ? { message: 'E-mail confirmado.' } : { detail: 'Falha de confirmação' });
  } else if (url.pathname === '/api/agradecimentos') responder(200, []);
  else if (url.pathname === '/api/comentarios/meu') responder(autenticado ? 200 : 401, []);
  else if (url.pathname === `/api${caminho}`) responder(200, {
    professor_id: pid, disciplina_id: did, total_avaliacoes: 0, dados_suficientes: false,
    professor: { id: pid, nome: 'Professor de teste', departamento: 'CIC' },
    disciplina: { id: did, nome: 'Disciplina de teste', codigo: 'CIC0001', departamento: 'CIC' },
  });
  else if (url.pathname === '/api/avaliacoes') {
    req.resume(); envios++;
    const concluir = () => responder(envioStatus, envioStatus === 200 ? { id: cid, comentario_erro: comentarioErro, comentario_estado: comentarioEstado } : { detail: 'Envio rejeitado' });
    if (reterEnvio) liberarEnvio = concluir; else concluir();
  } else if (url.pathname.startsWith('/api/moderacao/comentarios')) {
    if (url.pathname === '/api/moderacao/comentarios') filtrosConsultados.push(url.searchParams.get('estado'));
    if (moderacaoStatus !== 200) responder(moderacaoStatus, { detail: 'Restrito' });
    else if (url.pathname.endsWith('/decisoes')) responder(200, []);
    else if (url.pathname.endsWith(cid)) responder(200, comentario);
    else responder(200, [comentario]);
  } else responder(404, { detail: 'Not Found' });
});

await comNavegador({ fixture, diretorioFrontend: process.env.UI247_FRONTEND, executar: async ({ cdp, avaliar, aguardar }) => {
  const texto = () => avaliar("document.querySelector('main')?.innerText ?? ''");
  const esperar = trecho => aguardar(async () => (await texto()).includes(trecho), trecho);
  const navegar = async rota => {
    await cdp('Page.navigate', { url: `http://localhost:3100${rota}` });
    await aguardar(() => avaliar(`location.pathname === ${JSON.stringify(rota.split('?')[0])} && !!document.querySelector('main')`), rota);
  };
  const clicar = rotulo => avaliar(`Array.from(document.querySelectorAll('main button')).find(b => b.textContent.trim() === ${JSON.stringify(rotulo)})?.click()`);
  const preencher = valores => avaliar(`Object.entries(${JSON.stringify(valores)}).forEach(([nome, valor]) => {
    const e = document.querySelector('main [name='+nome+']');
    Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(e, valor);
    e.dispatchEvent(new Event('input', { bubbles: true }));
  })`);
  const submeter = () => avaliar("document.querySelector('main form').requestSubmit()");
  const criterios = () => avaliar(`Object.entries({didatica:'5',dificuldade:'MEDIO',chamada:'false',material:'BOM',recomenda:'true'}).forEach(([n,v])=>document.querySelector('main [name='+n+'][value="'+v+'"]').click())`);
  const capturar = async (nome, largura) => {
    assert.equal(await avaliar('document.documentElement.scrollWidth <= innerWidth'), true, `${nome}/${largura}: overflow`);
    assert.equal(await avaliar("document.querySelectorAll('main h1').length"), 1);
    await avaliar("document.querySelectorAll('img').forEach(i => { i.loading = 'eager'; })");
    await aguardar(() => avaliar('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)'), 'imagens');
    await avaliar('document.fonts.ready.then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))))');
    await avaliar('window.scrollTo({ top: 0, behavior: "instant" }); new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))');
    if (!process.env.UI247_CAPTURAS) return;
    const pasta = join(process.env.UI247_CAPTURAS, antes ? 'antes' : 'depois');
    await mkdir(pasta, { recursive: true });
    await aguardar(() => avaliar('scrollY === 0'), 'rolagem no topo');
    const layout = await cdp('Page.getLayoutMetrics');
    const { data } = await cdp('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true,
      clip: { x: 0, y: 0, width: largura, height: layout.cssContentSize.height, scale: 1 } });
    await writeFile(join(pasta, `${nome}-${largura}.png`), Buffer.from(data, 'base64'));
  };
  for (const largura of [320, 768, 1280]) {
    await cdp('Emulation.setDeviceMetricsOverride', { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura < 768 });
    autenticado = false;
    for (const rota of ['login', 'cadastro']) {
      await navegar(`/${rota}${query}`); await esperar(rota === 'login' ? 'Mostrar senha' : 'Crie uma senha exclusiva');
      await esperar('Avaliação selecionada');
      await capturar(rota, largura);
      assert.ok(await contrasteTexto(avaliar, 'main input[name=email]') >= 4.5);
      await avaliar("document.querySelector('main input').focus()");
      await cdp('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
      await cdp('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
      assert.equal(await avaliar('document.activeElement instanceof HTMLInputElement'), true);
    }
    await navegar(`/confirmar-email${query}&token=token-sintetico`); await esperar('E-mail confirmado.');
    await capturar('confirmacao-email', largura);
    assert.equal(autenticado, false, 'confirmação não cria sessão');
    autenticado = true;
    await navegar(retorno); await esperar('Já pode enviar sua avaliação.'); await criterios(); await submeter();
    await esperar('Avaliação registrada com sucesso.'); await capturar('sucesso-avaliacao', largura);
    if (!antes) {
      assert.match(await avaliar("document.querySelector('[aria-label=\"Resultado da avaliação\"]').innerText"), /CIC0001[\s\S]*Disciplina de teste[\s\S]*Professor de teste/);
      assert.equal(await avaliar("document.querySelector('[aria-label=\"Resultado da avaliação\"] a').getAttribute('href')"), '/disciplinas?q=CIC0001&ordem=nome');
      await clicar('Revisar ou substituir avaliação'); await esperar('Enviar avaliação');
    }
    await navegar('/rota-inexistente-247'); await esperar('Não encontramos isso'); await capturar('pagina-404', largura);
    await navegar('/moderacao'); await esperar('Selecione um comentário');
    await avaliar("document.querySelector('[aria-label=\"Comentários na fila\"] button').click()");
    await esperar('Analisar comentário'); await esperar('Nenhuma decisão disponível'); await capturar('moderacao', largura);
    assert.equal(await avaliar("document.activeElement.getAttribute('aria-label')"), 'Análise do comentário');
  }
  if (antes) { console.log('#247: 18 capturas da base, sem validar a nova implementação.'); return; }

  await clicar('Pendentes'); await esperar('Selecione um comentário');
  assert.equal(filtrosConsultados.at(-1), 'PENDENTE', 'botão desktop consulta o filtro contratado');
  assert.equal(await avaliar("document.querySelector('#estado-fila').value"), 'PENDENTE');
  await clicar('Todos'); await esperar('Selecione um comentário');
  assert.equal(filtrosConsultados.at(-1), null);

  autenticado = false;
  await navegar('/login?returnTo=https://example.com'); await esperar('Mostrar senha');
  assert.doesNotMatch(await texto(), /Você voltará/);
  loginStatus = 401; await preencher({ email: 'teste@aluno.unb.br', senha: 'senha-sintetica' }); await submeter(); await esperar('E-mail ou senha inválidos.');
  loginStatus = 200; await submeter(); await esperar('Sua sessão está ativa');
  autenticado = false;
  await navegar(`/login${query}`); await esperar('Mostrar senha'); await preencher({ email: 'teste@aluno.unb.br', senha: 'senha-sintetica' });
  const anteriores = envios;
  await submeter(); await esperar('Já pode enviar sua avaliação.'); assert.equal(envios, anteriores, 'login não envia avaliação');
  autenticado = false;
  await navegar(`/cadastro${query}`); await esperar('Crie uma senha exclusiva');
  await preencher({ nome: 'Pessoa sintética', email: 'teste@example.com', senha: 'senha-sintetica' });
  assert.equal(await avaliar("document.querySelector('main [name=email]').validity.patternMismatch"), true);
  await submeter(); assert.equal(cadastros, 0);
  await preencher({ email: 'teste@aluno.unb.br' }); cadastroStatus = 422; await submeter(); await esperar('Revise os dados');
  cadastroStatus = 202;
  await avaliar("const f = document.querySelector('main form'); f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true })); f.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }))");
  await esperar('enviaremos um link de confirmação');
  assert.equal(cadastros, 2, 'submissão duplicada não duplica o cadastro confirmado');
  assert.equal(autenticado, false); assert.equal(envios, anteriores);
  assert.match(await texto(), /confirmação/);

  await navegar('/confirmar-email'); await esperar('O link de confirmação está incompleto.');
  for (const status of [400, 422, 503]) {
    confirmarStatus = status; await navegar('/confirmar-email?token=token-sintetico');
    await esperar(status === 503 ? 'Não foi possível confirmar' : 'Este link é inválido ou expirou.');
  }
  const tentativas = confirmacoes; confirmarStatus = 200; await clicar('Tentar novamente'); await esperar('E-mail confirmado.');
  assert.equal(confirmacoes, tentativas + 1); assert.equal(autenticado, false);

  autenticado = true; await navegar(retorno); await esperar('Já pode enviar sua avaliação.'); await criterios();
  reterEnvio = true; await submeter(); await aguardar(() => !!liberarEnvio, 'requisição retida');
  assert.doesNotMatch(await texto(), /Obrigado por contribuir/);
  await submeter(); assert.equal(envios, anteriores + 1, 'envio duplicado bloqueado');
  liberarEnvio(); reterEnvio = false; await esperar('Avaliação registrada com sucesso.');
  await clicar('Revisar ou substituir avaliação');
  envioStatus = 403; await submeter(); await esperar('O envio não foi autorizado'); assert.doesNotMatch(await texto(), /Obrigado por contribuir/);
  envioStatus = 200;
  for (const parcial of [true, false]) {
    await navegar(retorno); await esperar('Já pode enviar sua avaliação.'); await criterios();
    await avaliar(`const e = document.querySelector('textarea[name=comentario]'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(e, 'Comentário sintético'); e.dispatchEvent(new Event('input', {bubbles:true}))`);
    comentarioErro = parcial ? 'Texto inválido' : null; await submeter();
    await esperar(parcial ? 'o comentário não foi enviado' : 'aprovação humana');
    assert.match(await texto(), /Avaliação registrada com sucesso/);
    await cdp('Page.reload'); await esperar('Enviar avaliação'); assert.doesNotMatch(await texto(), /Obrigado por contribuir/);
  }
  for (const status of [401, 403, 503]) {
    moderacaoStatus = status; await navegar('/moderacao'); await esperar(status === 401 ? 'Entre na sua conta' : status === 403 ? 'Acesso não permitido' : 'Não foi possível carregar');
    assert.equal(await avaliar("document.querySelector('[aria-label=\"Comentários na fila\"]')"), null);
    assert.doesNotMatch(await texto(), /autor.teste@/);
  }
  await navegar('/sobre'); await esperar('Pessoas que constroem');
  const linkedin = 'https://www.linkedin.com/in/vinicius-gavald%C3%A3o-franco-74950a44b/';
  assert.deepEqual(await avaliar(`const a = document.querySelector('a[href="${linkedin}"]'); [a?.target, a?.rel, a?.getAttribute('aria-label')]`), ['_blank', 'noopener noreferrer', 'LinkedIn de Vinicius, abre em outra aba']);
  assert.equal((await fetch('http://localhost:3100/rota-inexistente-247')).status, 404);
  console.log('#247: seis telas em 320/768/1280 px; retorno, login, cadastro, confirmação sem sessão, sucesso contextual, reenvio, falha parcial, 404, autorização e LinkedIn aprovados (HTTP controlado).');
} });
