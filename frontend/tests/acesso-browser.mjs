// #158: telas → FastAPI → e-mail console → PostgreSQL, sem respostas HTTP simuladas.
// CI: python -m tests.integration_acesso. Docker local: E2E_ACESSO_CONTAINER e
// E2E_ACESSO_FIXTURE_FILE. PREVIEW_DIR é opcional e não recebe tokens ou senhas.
import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const fixture = JSON.parse(process.env.E2E_ACESSO_FIXTURE ?? readFileSync(process.env.E2E_ACESSO_FIXTURE_FILE, "utf8").replace(/^\uFEFF/, ""));
const frontend = fileURLToPath(new URL("../", import.meta.url));
const navegador = process.env.BROWSER_PATH ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
assert.ok(existsSync(navegador), "Informe BROWSER_PATH com Edge/Chromium.");
assert.ok(process.env.E2E_ACESSO_CONTAINER || process.env.E2E_EMAIL_LOG_FILE, "Informe o log do adaptador console real.");
const base = "http://localhost:3100";
const destinos = fixture.professores.map((p) => `/professores/${p}/disciplinas/${fixture.disciplinaId}/avaliar`);
const perfil = mkdtempSync(join(tmpdir(), "undb-acesso-browser-"));
const evidencias = [];
const clientes = [];
let next, browser;

async function aguardar(condicao, descricao) {
  const inicio = Date.now();
  while (Date.now() - inicio < 25000) {
    if (await condicao()) return;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`Timeout: ${descricao}`);
}
async function conectar(target) {
  const tabs = await (await fetch("http://localhost:9225/json")).json();
  const socket = new WebSocket(tabs.find((t) => t.id === target).webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener("open", resolve, { once: true }); socket.addEventListener("error", reject, { once: true }); });
  let sequencia = 0;
  const pendentes = new Map();
  const cdp = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequencia;
    const timer = setTimeout(() => { pendentes.delete(id); reject(new Error(`Timeout CDP: ${method}`)); }, method === "Page.captureScreenshot" ? 30000 : 15000);
    pendentes.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
  socket.addEventListener("message", ({ data }) => {
    const mensagem = JSON.parse(data);
    const p = pendentes.get(mensagem.id);
    if (!p) return;
    clearTimeout(p.timer);
    pendentes.delete(mensagem.id);
    if (mensagem.error) p.reject(new Error(`CDP: ${mensagem.error.message}`));
    else p.resolve(mensagem.result);
  });
  const avaliar = async (expression) => {
    const r = await cdp("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error("Falha na avaliação do cenário no navegador.");
    return r.result.value;
  };
  const tab = { cdp, avaliar, socket };
  clientes.push(tab);
  await cdp("Page.enable");
  await cdp("Network.enable");
  return tab;
}
const texto = (tab) => tab.avaliar("document.querySelector('main')?.innerText ?? ''");
const esperarTexto = (tab, trecho) => aguardar(async () => (await texto(tab)).includes(trecho), trecho);
async function navegar(tab, url, trecho) {
  await tab.cdp("Page.bringToFront");
  const destino = url.startsWith("/") ? base + url : url;
  await tab.cdp("Page.navigate", { url: destino });
  await aguardar(async () => await tab.avaliar(`location.href === ${JSON.stringify(destino)} && document.readyState === 'complete'`), "documento carregado");
  await esperarTexto(tab, trecho);
}
async function clicar(tab, seletor, trecho) {
  await aguardar(async () => await tab.avaliar(`!!document.querySelector(${JSON.stringify(seletor)})`), "ação disponível");
  const destino = await tab.avaliar(`document.querySelector(${JSON.stringify(seletor)}).href ?? null`);
  await tab.avaliar(`document.querySelector(${JSON.stringify(seletor)}).click()`);
  if (destino) await aguardar(async () => await tab.avaliar(`location.href === ${JSON.stringify(destino)}`), "destino do link");
  await esperarTexto(tab, trecho);
}
async function preencher(tab, valores) {
  await aguardar(async () => await tab.avaliar("!!document.querySelector('form') && Object.keys(document.querySelector('form')).some(k => k.startsWith('__reactProps'))"), "formulário hidratado");
  await tab.avaliar(`Object.entries(${JSON.stringify(valores)}).forEach(([nome, valor]) => { const e=document.querySelector('[name="'+nome+'"]'); e.value=valor; e.dispatchEvent(new Event('change',{bubbles:true})); })`);
}
async function enviar(tab, mensagem) {
  await tab.avaliar("document.querySelector('form').requestSubmit()");
  await esperarTexto(tab, mensagem);
  await aguardar(async () => !(await tab.avaliar("document.querySelector('button[type=submit]')?.disabled ?? false")), "envio concluído");
}
function banco() {
  const args = process.env.E2E_ACESSO_CONTAINER
    ? ["exec", "-e", "UNDB_INTEGRATION_TEST=1", "-e", `E2E_ACESSO_FIXTURE=${JSON.stringify(fixture)}`, process.env.E2E_ACESSO_CONTAINER, "python", "-m", "tests.integration_acesso", "--inspect"]
    : ["-m", "tests.integration_acesso", "--inspect"];
  const r = spawnSync(process.env.E2E_ACESSO_CONTAINER ? "docker" : process.env.E2E_PYTHON, args, {
    cwd: join(frontend, "../backend"), encoding: "utf8", windowsHide: true,
    env: { ...process.env, E2E_ACESSO_FIXTURE: JSON.stringify(fixture) },
  });
  assert.equal(r.status, 0, "Inspeção do PostgreSQL deve concluir.");
  return JSON.parse(r.stdout);
}
function linkEmail(email) {
  let log;
  if (process.env.E2E_ACESSO_CONTAINER) {
    const r = spawnSync("docker", ["logs", process.env.E2E_ACESSO_CONTAINER], { encoding: "utf8", windowsHide: true });
    assert.equal(r.status, 0);
    log = r.stdout + r.stderr;
  } else log = readFileSync(process.env.E2E_EMAIL_LOG_FILE, "utf8");
  return log.split(/\r?\n/).find((l) => l.includes(`confirmacao para ${email}: `))?.split(`confirmacao para ${email}: `)[1].trim();
}
async function matriz(tab, tela) {
  await tab.cdp("Page.bringToFront");
  for (const tema of ["light", "dark"]) {
    await tab.cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
    for (const largura of [320, 768, 1280]) {
      await tab.cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura === 320 });
      await tab.avaliar("document.fonts.ready.then(() => true)");
      await tab.avaliar("new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve(true))))");
      assert.equal(await tab.avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `${tela}/${tema}/${largura}`);
      assert.equal(await tab.avaliar("document.querySelectorAll('main h1').length"), 1);
      let captura;
      if (process.env.PREVIEW_DIR && ((tema === "dark" && largura === 320) || (tema === "light" && largura === 1280))) {
        captura = `${tela}-${tema}-${largura}.png`;
        const layout = await tab.cdp("Page.getLayoutMetrics");
        const screenshot = await tab.cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: largura, height: layout.cssContentSize.height, scale: 1 } });
        await writeFile(join(process.env.PREVIEW_DIR, captura), Buffer.from(screenshot.data, "base64"));
      }
      evidencias.push({ tela, tema, largura, aprovado: true, captura });
    }
  }
}
async function encerrar(p) {
  if (!p || p.exitCode !== null || p.signalCode !== null) return;
  const fim = new Promise((r) => p.once("exit", r));
  p.kill();
  await fim;
}
async function preencherAvaliacao(tab) {
  assert.equal(await tab.avaliar("document.querySelector('[name=didatica]:checked') === null"), true);
  await preencher(tab, { dificuldade: "MEDIO", chamada: "false", material: "NAO_DISPONIBILIZA", recomenda: "false" });
  await tab.avaliar("document.querySelector('[name=didatica][value=\"1\"]').focus()");
  for (const type of ["keyDown", "keyUp"]) await tab.cdp("Input.dispatchKeyEvent", { type, key: "ArrowRight", code: "ArrowRight", windowsVirtualKeyCode: 39 });
  assert.equal(await tab.avaliar("document.querySelector('[name=didatica]:checked').value"), "2");
  for (const type of ["keyDown", "keyUp"]) await tab.cdp("Input.dispatchKeyEvent", { type, key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  assert.equal(await tab.avaliar("document.activeElement.name === 'dificuldade' && document.activeElement.matches(':focus-visible')"), true);
}

try {
  for (const porta of [3100, 9225]) {
    const reserva = createServer();
    await new Promise((resolve, reject) => { reserva.once("error", reject); reserva.listen(porta, resolve); });
    await new Promise((r) => reserva.close(r));
  }
  if (process.env.PREVIEW_DIR) await mkdir(process.env.PREVIEW_DIR, { recursive: true });
  assert.equal((await fetch("http://localhost:8000/health")).status, 200);
  next = spawn(process.execPath, ["node_modules/next/dist/bin/next", "start", "-p", "3100"], { cwd: frontend, stdio: "ignore", windowsHide: true, env: { ...process.env, API_INTERNAL_URL: "http://localhost:8000" } });
  await aguardar(async () => { try { return (await fetch(base)).ok; } catch { return false; } }, "Next.js");
  browser = spawn(navegador, ["--headless=new", "--disable-gpu", "--no-first-run", "--remote-debugging-port=9225", `--user-data-dir=${perfil}`, "about:blank"], { stdio: "ignore", windowsHide: true });
  await aguardar(async () => { try { return (await fetch("http://localhost:9225/json")).ok; } catch { return false; } }, "navegador");
  const tabs = await (await fetch("http://localhost:9225/json")).json();
  const a = await conectar(tabs.find((t) => t.type === "page").id);
  const { targetId } = await a.cdp("Target.createTarget", { url: "about:blank" });
  const b = await conectar(targetId);
  for (const [i, tab] of [a, b].entries()) {
    await navegar(tab, destinos[i], "Avaliar professor na disciplina");
    await clicar(tab, 'a[href^="/login?returnTo="]', "Entrar");
    await aguardar(async () => await tab.avaliar("!!document.querySelector('[name=email]')"), "login visitante");
    if (i === 0) await matriz(tab, "login");
    await clicar(tab, 'a[href^="/cadastro?returnTo="]', "Criar conta");
    if (i === 0) await matriz(tab, "cadastro");
    await preencher(tab, { nome: `Estudante de acesso ${i + 1}`, email: fixture.emails[i], senha: fixture.senha });
    await enviar(tab, "Se o endereço informado estiver disponível");
    await aguardar(() => !!linkEmail(fixture.emails[i]), "link do adaptador console");
    const url = new URL(linkEmail(fixture.emails[i]));
    assert.equal(url.origin, base);
    assert.equal(url.searchParams.get("returnTo"), destinos[i]);
  }
  let dados = banco();
  assert.equal(dados.usuarios.length, 2);
  assert.ok(dados.usuarios.every((u) => !u.confirmado && u.sessoes === 0 && u.tokensUsados === 0));
  assert.deepEqual(dados.avaliacoes, []);
  // Abrir conta sem contexto em B não pode alterar o link enviado para A.
  await navegar(b, "/login", "Entrar");
  await navegar(a, `/login?returnTo=${encodeURIComponent(destinos[0])}`, "Entrar");
  await aguardar(async () => await a.avaliar("!!document.querySelector('[name=email]')"), "login A");
  await preencher(a, { email: fixture.emails[0], senha: "senha-errada" });
  await enviar(a, "E-mail ou senha inválidos");
  assert.ok(banco().usuarios.every((u) => u.sessoes === 0));
  await preencher(a, { email: fixture.emails[0], senha: fixture.senha });
  await enviar(a, "Avaliar professor na disciplina");
  assert.equal(await a.avaliar("location.pathname"), destinos[0]);
  const cookies = await a.cdp("Network.getCookies", { urls: ["http://localhost:8000"] });
  assert.ok(cookies.cookies.some((c) => c.name === "undb_session" && c.httpOnly && c.sameSite === "Lax"));
  await preencherAvaliacao(a);
  const respostas = await a.avaliar("Object.fromEntries(new FormData(document.querySelector('form')))");
  await enviar(a, "link recebido");
  assert.deepEqual(await a.avaliar("Object.fromEntries(new FormData(document.querySelector('form')))") , respostas);
  assert.deepEqual(banco().avaliacoes, []);
  await matriz(a, "email-pendente");
  await navegar(a, linkEmail(fixture.emails[0]), "E-mail confirmado.");
  assert.equal(await a.avaliar("new URL(document.querySelector('a[href^=\"/login?returnTo=\"]').href).searchParams.get('returnTo')"), destinos[0]);
  await matriz(a, "confirmacao");
  dados = banco();
  assert.equal(dados.usuarios.find((u) => u.email === fixture.emails[0]).confirmado, true);
  assert.equal(dados.usuarios.find((u) => u.email === fixture.emails[1]).confirmado, false);
  await a.avaliar("document.querySelector('a[href^=\"/login?returnTo=\"]').click()");
  await aguardar(async () => await a.avaliar(`location.pathname === ${JSON.stringify(destinos[0])}`), "confirmação retoma A com sessão ativa");
  await esperarTexto(a, "Avaliar professor na disciplina");
  await preencherAvaliacao(a);
  await matriz(a, "formulario");
  await enviar(a, "Avaliação registrada com sucesso");
  await matriz(a, "sucesso");
  // A sessão existente faz o login retornar sem solicitar novamente a senha.
  await a.cdp("Page.navigate", { url: `${base}/login?returnTo=${encodeURIComponent(destinos[0])}` });
  await aguardar(async () => await a.avaliar(`location.pathname === ${JSON.stringify(destinos[0])}`), "retorno com sessão ativa");
  await esperarTexto(a, "Avaliar professor na disciplina");
  await navegar(a, "/login", "Sua sessão está ativa");
  await clicar(a, "main button", "Sessão encerrada");
  await navegar(b, linkEmail(fixture.emails[1]), "E-mail confirmado.");
  assert.equal(await b.avaliar("new URL(document.querySelector('a[href^=\"/login?returnTo=\"]').href).searchParams.get('returnTo')"), destinos[1]);
  await clicar(b, 'a[href^="/login?returnTo="]', "Entrar");
  await aguardar(async () => await b.avaliar("!!document.querySelector('[name=email]')"), "login B");
  await preencher(b, { email: fixture.emails[1], senha: fixture.senha });
  await enviar(b, "Avaliar professor na disciplina");
  assert.equal(await b.avaliar("location.pathname"), destinos[1]);
  await preencherAvaliacao(b);
  await enviar(b, "Avaliação registrada com sucesso");
  dados = banco();
  assert.ok(dados.usuarios.every((u) => u.confirmado && u.tokensUsados === 1));
  assert.equal(dados.avaliacoes.length, 2);
  for (const [i, email] of fixture.emails.entries()) {
    const avaliacao = dados.avaliacoes.find((v) => v.email === email);
    assert.equal(avaliacao.professorId, fixture.professores[i]);
    assert.equal(avaliacao.didatica, 2);
    assert.equal(avaliacao.chamada, false);
    assert.equal(avaliacao.recomenda, false);
    assert.equal(avaliacao.disponibilizaMaterial, false);
  }
  await navegar(a, linkEmail(fixture.emails[0]), "Este link é inválido ou expirou");
  assert.equal(await a.avaliar("!!document.querySelector('a[href^=\"/login?returnTo=\"]')"), false);
  const resumo = { origem: "Telas reais → FastAPI → adaptador console → PostgreSQL", combinacoes: evidencias.length,
    cenarios: ["dois cadastros e confirmações em abas distintas", "login genérico não altera retorno", "credenciais inválidas sem sessão", "e-mail pendente bloqueia escrita e mantém respostas", "cookie HttpOnly/SameSite", "retorno da sessão ativa", "logout", "token de uso único", "duas avaliações nos destinos corretos com respostas negativas", "teclado e foco"], evidencias };
  if (process.env.PREVIEW_DIR) await writeFile(join(process.env.PREVIEW_DIR, "resultado.json"), JSON.stringify(resumo, null, 2) + "\n");
  console.log(`Acesso real aprovado: cadastro, confirmação, login, retorno independente entre abas e persistência; ${evidencias.length} combinações de tela/tema/largura.`);
} finally {
  if (clientes[0]?.socket.readyState === WebSocket.OPEN) await clientes[0].cdp("Browser.close").catch(() => {});
  for (const tab of clientes) tab.socket.close();
  await encerrar(browser);
  await encerrar(next);
  const pastaTemporaria = resolve(tmpdir());
  assert.ok(resolve(perfil).startsWith(pastaTemporaria + "/") || resolve(perfil).startsWith(pastaTemporaria + "\\"));
  await rm(perfil, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 });
}
