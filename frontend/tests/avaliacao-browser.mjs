// Teste de interface com respostas controladas, NÃO é integração com FastAPI.
// Requer build padrão (API localhost:8000), Node 22+ e Edge/Chromium headless.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, rmSync } from "node:fs";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const navegador = process.env.BROWSER_PATH ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
assert.ok(existsSync(navegador), "Informe BROWSER_PATH com o executável Edge/Chromium.");
assert.ok(globalThis.WebSocket, "O teste de navegador requer Node 22+ (WebSocket nativo).");
// Não se conectar a servidores ou navegadores já em uso na máquina.
for (const porta of [8000, 3100, 9223]) {
  const reserva = createServer();
  await new Promise((resolve, reject) => {
    reserva.once("error", () => reject(new Error(`A porta ${porta} precisa estar livre para este teste.`)));
    reserva.listen(porta, resolve);
  });
  await new Promise((resolve) => reserva.close(resolve));
}
const frontend = fileURLToPath(new URL("../", import.meta.url));
const perfil = mkdtempSync(join(tmpdir(), "undb-avaliacao-browser-"));
const professorId = "11111111-1111-4111-8111-111111111111";
const disciplinaId = "22222222-2222-4222-8222-222222222222";
const caminho = `/professores/${professorId}/disciplinas/${disciplinaId}`;
let consultasSessao = 0;
const envios = [];
const fixture = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Content-Type", "application/json");
  if (req.method === "OPTIONS") { res.writeHead(204).end(); return; }
  if (req.url === `/api${caminho}`) {
    res.end(JSON.stringify({
      professor_id: professorId, disciplina_id: disciplinaId,
      professor: { id: professorId, nome: "Professor de teste", departamento: "CIC" },
      disciplina: { id: disciplinaId, codigo: "CIC0001", nome: "Disciplina de teste", departamento: "CIC" },
      total_avaliacoes: 0, dados_suficientes: false,
    }));
  } else if (req.url === "/api/auth/sessao") {
    consultasSessao += 1; res.end(JSON.stringify({ autenticado: true }));
  } else if (req.method === "POST" && req.url === "/avaliacoes") {
    let body = "";
    for await (const chunk of req) body += chunk;
    envios.push({ body: JSON.parse(body), cookie: req.headers.cookie });

    res.writeHead(405).end(JSON.stringify({ detail: "Envio indisponível" }));
  } else { res.writeHead(404).end(JSON.stringify({ detail: "Not Found" })); }
});

let next;
let browser;
let socket;
let sequence = 0;
const pendentes = new Map();
function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => { pendentes.delete(id); reject(new Error(`Timeout: ${method}`)); }, 15000);
    pendentes.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function avaliar(expression) {
  const result = await cdp("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
  return result.result.value;
}
async function aguardar(condicao, descricao) {
  const inicio = Date.now();
  while (Date.now() - inicio < 20000) {
    try { if (await condicao()) return; } catch { /* serviço ainda iniciando */ }
    await new Promise((resolve) => setTimeout(resolve, 100));
  }
  throw new Error(`Timeout: ${descricao}`);
}
const texto = () => avaliar("document.body.innerText");
const enviar = () => avaliar('document.querySelector("button[type=submit]").click()');
const aguardarTexto = (trecho) => aguardar(async () => (await texto()).includes(trecho), trecho);

try {
  await new Promise((resolve, reject) => { fixture.once("error", reject); fixture.listen(8000, resolve); });
  next = spawn(process.execPath, ["node_modules/next/dist/bin/next", "start", "-p", "3100"], {
    cwd: frontend, stdio: "ignore", windowsHide: true,
    env: { ...process.env, API_INTERNAL_URL: "http://localhost:8000" },
  });
  next.on("error", (erro) => console.error(erro));
  await aguardar(async () => (await fetch("http://localhost:3100")).ok, "Next.js");
  browser = spawn(navegador, ["--headless=new", "--disable-gpu", "--no-first-run", "--remote-debugging-port=9223", `--user-data-dir=${perfil}`, "about:blank"], { stdio: "ignore", windowsHide: true });
  browser.on("error", (erro) => console.error(erro));
  await aguardar(async () => (await fetch("http://localhost:9223/json")).ok, "navegador");
  const paginas = await (await fetch("http://localhost:9223/json")).json();
  socket = new WebSocket(paginas.find((pagina) => pagina.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener("open", resolve, { once: true }); socket.addEventListener("error", reject, { once: true }); });
  socket.addEventListener("message", ({ data }) => {
    const mensagem = JSON.parse(data);
    const pendente = pendentes.get(mensagem.id);
    if (!pendente) return;
    clearTimeout(pendente.timer);
    pendentes.delete(mensagem.id);
    if (mensagem.error) pendente.reject(new Error(JSON.stringify(mensagem.error)));
    else pendente.resolve(mensagem.result);
  });
  await cdp("Page.enable");
  await cdp("Network.enable");
  await cdp("Network.setCookie", { name: "undb_session", value: "cookie-apenas-de-teste", url: "http://localhost:8000", httpOnly: true, sameSite: "Lax" });
  await cdp("Page.navigate", { url: `http://localhost:3100${caminho}` });
  await aguardarTexto("Avaliar este professor na disciplina");
  await avaliar('Array.from(document.querySelectorAll("a")).find(a => a.textContent.includes("Avaliar este professor")).click()');
  await aguardar(async () => await avaliar('document.querySelectorAll("select").length === 5'), "formulário");
  assert.match(await texto(), /Professor de teste/);
  assert.match(await texto(), /CIC0001 — Disciplina de teste/);
  // Confirma que o handler React está ativo antes de testar o bloqueio de envio.
  await avaliar('document.querySelector("form").dispatchEvent(new Event("submit", {bubbles:true, cancelable:true}))');
  await aguardarTexto("Selecione uma opção válida para Didática.");
  await enviar();
  assert.equal(await avaliar('document.querySelector("form").checkValidity()'), false);
  assert.equal(envios.length, 0);
  await avaliar(`Object.entries({didatica:"5", dificuldade:"DIFICIL", chamada:"false", material:"NAO_DISPONIBILIZA", recomenda:"false"}).forEach(([nome, valor]) => { const campo = document.querySelector('[name="'+nome+'"]'); campo.value = valor; campo.dispatchEvent(new Event("change", {bubbles:true})); })`);
  assert.equal(await avaliar('document.querySelector("form").checkValidity()'), true);
  assert.equal(await avaliar('document.querySelector("button[type=submit]").disabled'), true);
  await aguardarTexto("suas respostas não serão enviadas nem salvas");
  await enviar();
  // Exercita o handler mesmo sem o botão: Enter/requestSubmit não pode contornar o gate.
  await avaliar('document.querySelector("form").requestSubmit()');
  await avaliar('document.querySelector("form").dispatchEvent(new Event("submit", {bubbles:true, cancelable:true}))');
  await new Promise((resolve) => setTimeout(resolve, 500));
  assert.equal(consultasSessao, 0);
  assert.equal(envios.length, 0);
  assert.ok(!(await texto()).includes("Avaliação registrada com sucesso"));
  assert.equal(await avaliar('document.querySelector("[name=material]").value'), "NAO_DISPONIBILIZA");
  // Acesso direto à rota mantém o gate e permite validar campos localmente.
  await cdp("Page.navigate", { url: `http://localhost:3100${caminho}/avaliar` });
  await aguardar(async () => await avaliar('document.querySelectorAll("select").length === 5'), "formulário direto");
  assert.equal(await avaliar('document.querySelector("button[type=submit]").disabled'), true);
  assert.equal(await avaliar('document.querySelector("form").reportValidity()'), false);
  // Aguarda hidratação por uma mudança observável no handler React.
  await avaliar('document.querySelector("form").dispatchEvent(new Event("submit", {bubbles:true, cancelable:true}))');
  await aguardarTexto("Selecione uma opção válida para Didática.");
  await avaliar('document.querySelector("[name=didatica]").focus()');
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  assert.equal(await avaliar("document.activeElement.name"), "dificuldade");
  for (const tema of ["light", "dark"]) {
    await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
    for (const width of [320, 768, 1280]) {
      await cdp("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: false });
      assert.equal(await avaliar("document.documentElement.scrollWidth <= window.innerWidth"), true, `${tema}, ${width}px`);
    }
  }
  assert.equal(consultasSessao, 0);
  assert.equal(envios.length, 0);
  console.log("Interface aprovada: navegação, acesso direto, cinco critérios obrigatórios, validação local, gate no botão e handler, ausência de sessão/POST, preservação das respostas, teclado e 6 combinações de tema/largura.");
  console.log("Limite: respostas controladas de teste; persistência real e substituição no banco NÃO verificadas.");
} finally {
  if (socket?.readyState === WebSocket.OPEN) {
    await cdp("Browser.close").catch(() => {});
    socket.close();
  }
  browser?.kill();
  next?.kill();
  fixture.closeAllConnections();
  await new Promise((resolve) => fixture.close(resolve));
  // Somente o perfil temporário exclusivo criado por este teste.
  rmSync(perfil, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
}
