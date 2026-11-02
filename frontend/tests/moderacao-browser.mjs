// Mesmo mecanismo das suítes existentes: Node, CDP e Edge/Chromium isolado.
// MODERACAO_FIXTURE_FILE seleciona API/PostgreSQL reais; padrão usa HTTP controlado.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { existsSync, mkdtempSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const frontend = fileURLToPath(new URL("../", import.meta.url));
const navegador = process.env.BROWSER_PATH ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
assert.ok(existsSync(navegador), "Defina BROWSER_PATH para Edge/Chromium.");
const real = process.env.MODERACAO_FIXTURE_FILE ? JSON.parse(readFileSync(process.env.MODERACAO_FIXTURE_FILE, "utf8")) : null;
for (const porta of (real ? [3100, 9226] : [8000, 3100, 9226])) {
  const reserva = createServer();
  await new Promise((resolve, reject) => { reserva.once("error", reject); reserva.listen(porta, resolve); });
  await new Promise((resolve) => reserva.close(resolve));
}
const uuid = (i) => `${String(i).padStart(8, "0")}-1111-4111-8111-111111111111`;
const autor = { id: uuid(90), nome: "Autor de teste", email: "autor.privado@aluno.unb.br" };
const data = "2026-11-01T12:00:00Z";
const criar = (i, estado) => ({ id: uuid(i), estado, texto: `${i}: Texto acadêmico de teste. ${"Texto longo ".repeat(40)}<script>window.injecao=true</script>`, autor, created_at: data, substitui_id: i === 1 ? uuid(4) : null });
let itens, acesso, statusAcao, atrasoFila, atrasos, falhaDenuncias, falhaDecisoes, mudarNoConflito, falharAtualizacao;
const envios = [];
function reiniciar() {
  itens = [criar(1, "PENDENTE"), criar(2, "PUBLICADO"), criar(3, "SUSPENSO")];
  acesso = 200; statusAcao = 200; atrasoFila = 0; atrasos = {}; falhaDenuncias = false; falhaDecisoes = false; mudarNoConflito = false; falharAtualizacao = false;
}
reiniciar();
const consultas = [];
const fixture = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Content-Type", "application/json");
  if (req.method === "OPTIONS") { res.writeHead(204).end(); return; }
  const url = new URL(req.url, "http://localhost:8000");
  const responder = (status, corpo) => { if (!res.destroyed) res.writeHead(status).end(JSON.stringify(corpo)); };
  if (acesso !== 200) { responder(acesso, { detail: "Rejeição privada: não exibir" }); return; }
  if (url.pathname === "/api/moderacao/comentarios") {
    const resposta = structuredClone(itens.filter((item) => !url.searchParams.has("estado") || item.estado === url.searchParams.get("estado")));
    setTimeout(() => responder(200, resposta), atrasoFila); return;
  }
  const match = url.pathname.match(/^\/api\/moderacao\/comentarios\/([^/]+)(?:\/(denuncias|decisoes|acoes))?$/);
  if (!match) { responder(404, {}); return; }
  const [, id, recurso] = match;
  const item = itens.find((valor) => valor.id === id) ?? (id === uuid(4) ? criar(4, "SUSPENSO") : null);
  if (!item) { responder(404, { detail: "indisponivel" }); return; }
  if (!recurso) { setTimeout(() => responder(200, item), atrasos[id] ?? 0); return; }
  if (recurso === "denuncias") {
    if (falhaDenuncias) { responder(503, {}); return; }
    const relato = { id: uuid(50), comentario_versao_id: id, estado: "EM_ABERTO", motivo: "SPAM", created_at: data, denunciante: autor };
    responder(200, { autenticadas: [relato], visitantes: [{ ...relato, id: uuid(51), denunciante: null }], contas_distintas: 1, total_visitantes: 1 }); return;
  }
  if (recurso === "decisoes") { responder(falhaDecisoes ? 503 : 200, falhaDecisoes ? {} : []); return; }
  let corpo = "";
  for await (const parte of req) corpo += parte;
  const entrada = JSON.parse(corpo);
  envios.push({ id, ...entrada, cookie: req.headers.cookie });
  if (statusAcao !== 200) {
    if (mudarNoConflito) itens = itens.filter((valor) => valor.id !== id);
    responder(statusAcao, { detail: "Rejeição privada: não exibir" }); return;
  }
  const destino = { APROVAR: "PUBLICADO", REJEITAR: "REJEITADO", MANTER: "PUBLICADO", RESTAURAR: "PUBLICADO", REMOVER: "REMOVIDO" }[entrada.acao];
  itens = itens.filter((valor) => valor.id !== id);
  if (falharAtualizacao) acesso = 503;
  responder(200, { id: uuid(70), comentario_versao_id: id, moderador_id: uuid(80), acao: entrada.acao, motivo: entrada.motivo,
    estado_anterior: item.estado, estado_posterior: destino, created_at: data });
});

let next, browser, socket, contador = 0;
const pendentes = new Map();
const perfil = mkdtempSync(join(tmpdir(), "undb-moderacao-"));
const cdp = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++contador;
  const timer = setTimeout(() => { pendentes.delete(id); reject(new Error(`Timeout CDP ${method}`)); }, 20000);
  pendentes.set(id, { resolve, reject, timer });
  socket.send(JSON.stringify({ id, method, params }));
});
async function avaliar(expression) {
  if (expression.trimStart().startsWith("const ")) expression = `{ ${expression} }`;
  const resultado = await cdp("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (resultado.exceptionDetails) throw new Error(JSON.stringify(resultado.exceptionDetails));
  return resultado.result.value;
}
async function aguardar(consulta, nome) {
  for (let i = 0; i < 200; i++) { if (await consulta()) return; await new Promise((r) => setTimeout(r, 100)); }
  throw new Error(`Não encontrado: ${nome}`);
}
const texto = () => avaliar("document.body.innerText");
const esperarTexto = (valor) => aguardar(async () => (await texto()).includes(valor), valor);
const clicar = (valor) => avaliar(`Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === ${JSON.stringify(valor)})?.click()`);
async function navegar() { await cdp("Page.navigate", { url: "http://localhost:3100/moderacao" }); await esperarTexto("Fila de moderação"); }
async function selecionar(id) {
  await avaliar(`Array.from(document.querySelectorAll('[aria-label="Comentários na fila"] button')).find(b => b.textContent.includes(${JSON.stringify(id)}))?.click()`);
  await aguardar(async () => await avaliar(`document.querySelector('[aria-label="Análise do comentário"]')?.innerText.includes(${JSON.stringify(id)}) && !!document.querySelector('#acao-moderacao')`), `análise ${id}`);
}
async function preencher(acao, motivo = "Decisão humana de teste") {
  await avaliar(`const seletor = document.querySelector('#acao-moderacao'); seletor.value = ${JSON.stringify(acao)}; seletor.dispatchEvent(new Event('change', {bubbles:true}));
    const campo = document.querySelector('#motivo-moderacao'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(campo, ${JSON.stringify(motivo)}); campo.dispatchEvent(new Event('input', {bubbles:true}));`);
}
async function cookie(valor) {
  await cdp("Network.clearBrowserCookies");
  if (valor) await cdp("Network.setCookie", { name: "undb_session", value: valor, url: "http://localhost:8000", httpOnly: true, sameSite: "Lax" });
}
async function captura(nome) {
  if (!process.env.PREVIEW_DIR) return;
  mkdirSync(process.env.PREVIEW_DIR, { recursive: true });
  const imagem = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  writeFileSync(join(process.env.PREVIEW_DIR, `${nome}.png`), Buffer.from(imagem.data, "base64"));
}

try {
  if (!real) await new Promise((resolve) => fixture.listen(8000, resolve));
  next = spawn(process.execPath, ["node_modules/next/dist/bin/next", "start", "-p", "3100"], { cwd: frontend, stdio: "ignore", windowsHide: true });
  await aguardar(async () => { try { return (await fetch("http://localhost:3100/moderacao")).ok; } catch { return false; } }, "Next.js");
  browser = spawn(navegador, ["--headless=new", "--disable-gpu", "--no-first-run", "--remote-debugging-port=9226", `--user-data-dir=${perfil}`, "about:blank"], { stdio: "ignore", windowsHide: true });
  await aguardar(async () => { try { return (await fetch("http://localhost:9226/json")).ok; } catch { return false; } }, "Edge/Chromium");
  const paginas = await (await fetch("http://localhost:9226/json")).json();
  socket = new WebSocket(paginas.find((item) => item.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve) => socket.addEventListener("open", resolve, { once: true }));
  socket.addEventListener("message", ({ data }) => {
    const mensagem = JSON.parse(data);
    if (mensagem.method === "Network.requestWillBeSent") consultas.push(mensagem.params.request.url);
    const atual = pendentes.get(mensagem.id);
    if (!atual) return;
    clearTimeout(atual.timer); pendentes.delete(mensagem.id);
    if (mensagem.error) atual.reject(new Error(JSON.stringify(mensagem.error))); else atual.resolve(mensagem.result);
  });
  await cdp("Page.enable"); await cdp("Network.enable"); await cdp("Network.setCacheDisabled", { cacheDisabled: true });
  await cookie(real?.moderador ?? "cookie-de-teste");
  if (!real) {
    atrasoFila = 600;
    await navegar(); await esperarTexto("Carregando fila de moderação"); await esperarTexto("Selecione um comentário para analisar");
    for (const [status, esperado] of [[401, "Entre na sua conta"], [403, "Acesso não permitido"], [503, "Não foi possível carregar"]]) {
      acesso = status; await clicar("Atualizar fila"); await esperarTexto(esperado);
      assert.ok(!(await texto()).includes("Autor de teste"));
      assert.equal(await avaliar("document.querySelectorAll('[aria-label=\"Comentários na fila\"] button').length"), 0);
    }
    acesso = 200; atrasoFila = 0; itens = []; await clicar("Atualizar fila"); await esperarTexto("Nenhum comentário aguardando");
    reiniciar(); await clicar("Atualizar fila"); await esperarTexto("Selecione um comentário");
    await avaliar("const filtro=document.querySelector('#estado-fila'); filtro.value='SUSPENSO'; filtro.dispatchEvent(new Event('change',{bubbles:true}));");
    await aguardar(async () => await avaliar("document.querySelectorAll('[aria-label=\"Comentários na fila\"] button').length === 1"), "filtro suspenso");
    await avaliar("const filtro=document.querySelector('#estado-fila'); filtro.value=''; filtro.dispatchEvent(new Event('change',{bubbles:true}));");
    await aguardar(async () => await avaliar("document.querySelectorAll('[aria-label=\"Comentários na fila\"] button').length === 3"), "fila completa");
    atrasos[uuid(1)] = 600;
    await avaliar(`Array.from(document.querySelectorAll('[aria-label="Comentários na fila"] button'))[0].click()`);
    await selecionar(uuid(2));
    await new Promise((resolve) => setTimeout(resolve, 700));
    assert.ok((await avaliar("document.querySelector('[aria-label=\"Análise do comentário\"]').innerText")).includes(uuid(2)), "resposta antiga não substitui seleção");
    atrasos = {};
    for (const tema of ["light", "dark"]) for (const largura of [320, 768, 1280]) {
      await cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura === 320 });
      await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
      for (const [id, opcoes] of [[uuid(1), ["APROVAR", "REJEITAR"]], [uuid(2), ["MANTER", "REMOVER"]], [uuid(3), ["RESTAURAR", "REMOVER"]]]) {
        await selecionar(id);
        assert.deepEqual(await avaliar("Array.from(document.querySelector('#acao-moderacao').options).map(o=>o.value).filter(Boolean)"), opcoes);
        assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `${tema}/${largura}`);
        assert.equal(await avaliar("Array.from(document.querySelectorAll('.line-clamp-3')).every(el => el.getBoundingClientRect().height <= 3 * parseFloat(getComputedStyle(el).lineHeight) + 1)"), true, "prévias de até três linhas");
        assert.equal(await avaliar("window.injecao"), undefined);
      }
      await avaliar("document.querySelector('[aria-label=\"Denúncias da versão\"] details').open=true");
      await captura(`moderacao-${tema}-${largura}`);
      await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      assert.ok(await avaliar("document.activeElement !== document.body"));
    }
    for (const [i, acao] of [[1, "APROVAR"], [1, "REJEITAR"], [2, "MANTER"], [2, "REMOVER"], [3, "RESTAURAR"], [3, "REMOVER"]]) {
      reiniciar(); await clicar("Atualizar fila"); await esperarTexto("Selecione um comentário"); await selecionar(uuid(i));
      assert.equal(await avaliar("document.querySelector('button[type=submit]').disabled"), true);
      await preencher(acao, "   "); assert.equal(await avaliar("document.querySelector('button[type=submit]').disabled"), true);
      await preencher(acao); await clicar("Confirmar decisão"); await esperarTexto("Decisão registrada");
      await esperarTexto("Selecione um comentário");
      assert.ok(!await avaliar(`Array.from(document.querySelectorAll('[aria-label="Comentários na fila"] button')).some(b=>b.textContent.includes(${JSON.stringify(uuid(i))}))`));
      assert.equal(envios.at(-1).acao, acao); assert.ok(envios.at(-1).motivo.trim()); assert.ok(envios.at(-1).cookie?.includes("undb_session"));
      assert.ok(!(await texto()).includes("Autor de teste"), "painel antigo removido após ação");
    }
    for (const [status, esperado] of [[403, "outro moderador"], [409, "estado do conteúdo mudou"], [503, "Não foi possível confirmar"], [422, "Revise a ação"]]) {
      reiniciar(); statusAcao = status; mudarNoConflito = status === 409;
      await navegar(); await esperarTexto("Selecione um comentário"); await selecionar(uuid(1));
      await preencher("APROVAR"); await clicar("Confirmar decisão"); await esperarTexto(esperado);
      assert.ok(!(await texto()).includes("Decisão registrada")); assert.ok(!(await texto()).includes("Rejeição privada"));
      if (status === 403) {
        await esperarTexto("Selecione um comentário");
        await avaliar("document.querySelector('[aria-label=\"Comentários na fila\"] button').click()");
        await esperarTexto("Este caso requer outro moderador");
        assert.equal(await avaliar("document.querySelector('#acao-moderacao') === null"), true);
      }
    }
    reiniciar(); await clicar("Atualizar fila"); await esperarTexto("Selecione um comentário"); await selecionar(uuid(2));
    acesso = 403; await preencher("REMOVER"); await clicar("Confirmar decisão"); await esperarTexto("Acesso não permitido");
    assert.ok(!(await texto()).includes(autor.email));
    reiniciar(); falhaDenuncias = true; falhaDecisoes = true;
    await clicar("Atualizar fila"); await esperarTexto("Selecione um comentário"); await selecionar(uuid(1));
    await esperarTexto("Não foi possível consultar as decisões");
    assert.equal(await avaliar("document.querySelector('#acao-moderacao').options.length"), 3, "aprovação inicial independe de denúncias e histórico");
    reiniciar(); falharAtualizacao = true;
    await clicar("Atualizar fila"); await esperarTexto("Selecione um comentário"); await selecionar(uuid(1));
    await preencher("APROVAR"); await clicar("Confirmar decisão");
    await esperarTexto("Decisão registrada"); await esperarTexto("Não foi possível carregar");
    assert.equal(await avaliar("document.querySelectorAll('[aria-label=\"Comentários na fila\"] button').length"), 0, "não mantém fila obsoleta quando a atualização falha");
    assert.equal(await avaliar("localStorage.length + sessionStorage.length"), 0);
    console.log("Fila controlada: acesso, três estados, filtros, seis ações, motivo, 403/409/422/503, concorrência de consultas, teclado e 18 combinações de estado/largura/tema aprovados.");
  } else {
    for (const [token, esperado] of [[null, "Entre na sua conta"], [real.comum, "Acesso não permitido"], [real.naoConfirmado, "Acesso não permitido"]]) {
      await cookie(token); await navegar(); await esperarTexto(esperado);
      assert.ok(!(await texto()).includes("Autor real de teste"));
    }
    await cookie(real.moderador); await navegar(); await esperarTexto("Selecione um comentário");
    for (const tema of ["light", "dark"]) for (const largura of [320, 768, 1280]) {
      await cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura === 320 });
      await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
      await selecionar(real.casos[0].id);
      assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true);
      await captura(`moderacao-real-${tema}-${largura}`);
    }
    for (const caso of real.casos) {
      await selecionar(caso.id); await preencher(caso.acao); await clicar("Confirmar decisão"); await esperarTexto("Decisão registrada");
      await esperarTexto("Selecione um comentário");
      const resultado = await avaliar(`fetch('http://localhost:8000/api/moderacao/comentarios/${caso.id}',{credentials:'include',cache:'no-store'}).then(r=>r.json())`);
      assert.equal(resultado.estado, caso.destino);
    }
    await selecionar(real.proprio); await preencher("APROVAR"); await clicar("Confirmar decisão"); await esperarTexto("outro moderador");
    await esperarTexto("Selecione um comentário");
    const estado = await avaliar(`fetch('http://localhost:8000/api/moderacao/comentarios/${real.proprio}',{credentials:'include'}).then(r=>r.json())`);
    assert.equal(estado.estado, "PENDENTE");
    await selecionar(real.denunciaPropria); await preencher("MANTER"); await clicar("Confirmar decisão"); await esperarTexto("outro moderador");
    await esperarTexto("Selecione um comentário");
    console.log("Fila real: navegador → FastAPI/PostgreSQL, visitante/conta comum/não confirmada, seis ações, impedimento próprio e seis combinações de largura/tema aprovados.");
  }
  assert.ok(!consultas.some((url) => url.includes("/api/agradecimentos") || /\/api\/comentarios\/[^/]+\/denuncias/.test(url)), "não consome a interface da #193");
} finally {
  socket?.close();
  for (const atual of pendentes.values()) { clearTimeout(atual.timer); atual.reject(new Error("Teste encerrado")); }
  browser?.kill(); next?.kill();
  if (!real) await new Promise((resolve) => { fixture.closeAllConnections(); fixture.close(resolve); });
  await rm(perfil, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
}
