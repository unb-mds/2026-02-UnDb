// #204/#217: rotas oficiais com API sintética; não valida integração PostgreSQL.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { mkdtempSync } from "node:fs";
import { rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { contextoEmTransicao } from "./browser-navigation.mjs";

const frontend = fileURLToPath(new URL("../", import.meta.url));
const base = "http://localhost:3100";
const apiPort = 8109;
const browserPort = 9231;
const id = (n) => `00000000-0000-4000-8000-${String(n).padStart(12, "0")}`;
const disciplina = { id: id(20), codigo: "TEST204", nome: "Disciplina sintética #204", departamento: "TEST", departamento_nome: "Unidade de teste" };
const nomes = ["Zélia", "Álvaro", "Álvaro", "Sem dados", "Sem avaliações"];
const professores = nomes.map((nome, i) => ({
  professor_id: id(i + 1), disciplina_id: disciplina.id,
  professor: { id: id(i + 1), nome, departamento: "TEST" }, disciplina,
  total_avaliacoes: [4, 4, 3, 2, 0][i], dados_suficientes: i < 3,
  ...(i < 3 ? { didatica: 4.2, dificuldade: "MEDIO", chamada: "CONFLITANTE", disponibiliza_material: "CONFLITANTE", qualidade_material: null, recomenda: i === 2 ? 50 : 100 } : {}),
}));
let falharComparacao = false;
let somenteAtual = false;
const fixture = createServer((req, res) => {
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", base);
  res.setHeader("Access-Control-Allow-Credentials", "true");
  const path = new URL(req.url, `http://localhost:${apiPort}`).pathname;
  const responder = (status, body) => res.writeHead(status).end(JSON.stringify(body));
  if (path === `/api/disciplinas/${disciplina.id}`) return responder(200, { ...disciplina, identificador_externo: null, creditos: 4 });
  if (path === `/api/disciplinas/${disciplina.id}/professores`) return responder(falharComparacao ? 503 : 200, { disciplina, professores: somenteAtual ? professores.slice(0, 1) : professores });
  if (path === `/api/disciplinas/${disciplina.id}/turmas`) return responder(200, professores.slice(1, 3).map((p, i) => ({
    id: id(30 + i), fonte: "TEST", codigo: String(i + 1), semestre: "2026.2", ativa: true,
    professores: [{ ...p.professor, siape: null, identidade_confirmada: false }],
  })));
  const agregado = professores.find((p) => path === `/api/professores/${p.professor_id}/disciplinas/${disciplina.id}`);
  if (agregado) return responder(200, agregado);
  if (path.endsWith("/comentarios")) return responder(200, []);
  if (path === "/api/auth/sessao") return responder(200, { autenticado: false });
  if (path === "/api/agradecimentos") return responder(401, {});
  responder(404, {});
});

async function aguardar(condicao, descricao) {
  const inicio = Date.now();
  while (Date.now() - inicio < 30000) {
    if (await condicao()) return;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`Timeout: ${descricao}`);
}
let next, browser, socket, perfil;
let seq = 0;
const pendentes = new Map();
const erros = [];
function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++seq;
    const timer = setTimeout(() => { pendentes.delete(id); reject(new Error(method)); }, 15000);
    pendentes.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function avaliar(expression) {
  const r = await cdp("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
  return r.result.value;
}
async function navegar(path, trecho) {
  await cdp("Page.navigate", { url: base + path });
  await aguardar(async () => {
    try { return await avaliar(`document.readyState === 'complete' && !!document.querySelector('main') && document.querySelector('main').innerText.includes(${JSON.stringify(trecho)})`); }
    catch (e) { if (contextoEmTransicao(e)) return false; throw e; }
  }, trecho);
}
async function encerrar(p) {
  if (!p || p.exitCode !== null) return;
  const fim = new Promise((r) => p.once("exit", r));
  p.kill();
  await fim;
}
try {
  for (const port of [apiPort, 3100, browserPort]) {
    const reserva = createServer();
    await new Promise((r, reject) => { reserva.once("error", reject); reserva.listen(port, r); });
    await new Promise((r) => reserva.close(r));
  }
  await new Promise((r) => fixture.listen(apiPort, r));
  next = spawn(process.execPath, ["node_modules/next/dist/bin/next", "start", "-p", "3100"], {
    cwd: frontend, stdio: "ignore", windowsHide: true,
    env: { ...process.env, API_INTERNAL_URL: `http://localhost:${apiPort}` },
  });
  await aguardar(async () => { try { return (await fetch(base)).ok; } catch { return false; } }, "Next.js");
  perfil = mkdtempSync(join(tmpdir(), "undb-perfil-"));
  browser = spawn(process.env.BROWSER_PATH ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", [
    "--headless=new", "--disable-gpu", "--no-first-run", `--remote-debugging-port=${browserPort}`, `--user-data-dir=${perfil}`, "about:blank",
  ], { stdio: "ignore", windowsHide: true });
  await aguardar(async () => { try { return (await fetch(`http://localhost:${browserPort}/json`)).ok; } catch { return false; } }, "Edge");
  const tabs = await (await fetch(`http://localhost:${browserPort}/json`)).json();
  socket = new WebSocket(tabs.find((t) => t.type === "page").webSocketDebuggerUrl);
  await new Promise((r, reject) => { socket.addEventListener("open", r, { once: true }); socket.addEventListener("error", reject, { once: true }); });
  socket.addEventListener("message", ({ data }) => {
    const m = JSON.parse(data);
    if (m.method === "Runtime.exceptionThrown") erros.push(m.params);
    const p = pendentes.get(m.id);
    if (!p) return;
    clearTimeout(p.timer); pendentes.delete(m.id);
    if (m.error) p.reject(new Error(JSON.stringify(m.error))); else p.resolve(m.result);
  });
  await cdp("Page.enable");
  await cdp("Runtime.enable");
  const contexto = "?busca=disciplinas&q=TEST&ordem=nome";
  const ordem = () => avaliar("Array.from(document.querySelectorAll('tbody tr')).map(r => r.querySelector('a').pathname.split('/').at(-1))");
  for (const width of [320, 390, 768, 1440]) {
    await cdp("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 768 });
    await navegar(`/disciplinas/${disciplina.id}${contexto}`, "Comparação de professores");
    assert.deepEqual(await ordem(), professores.map((p) => p.professor_id), "Preserva desempates da API, inclusive acentos");
    assert.equal(await avaliar("Array.from(document.querySelectorAll('tbody tr')).every(r => Array.from(r.cells).reduce((n,c) => n+c.colSpan,0) === 8)"), true, "Oito colunas em todas as linhas");
    assert.ok((await avaliar("document.querySelector('tbody').innerText")).includes("Conflitante"));
    assert.ok((await avaliar("document.querySelector('tbody').innerText")).includes("Turma 1"));
    assert.ok((await avaliar("document.querySelector('tbody').innerText")).includes("Turma 2"));
    assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, "Tabela rola dentro da página");
    await aguardar(() => avaliar("Object.keys(document.querySelector('.sort')).some(k => k.startsWith('__reactProps'))"), "Hidratação");
    await avaliar("document.querySelector('.sort').focus()");
    await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", text: "\r", windowsVirtualKeyCode: 13 });
    await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
    await aguardar(async () => (await ordem())[0] === id(3), "Recomendação crescente via teclado");
    assert.deepEqual(await ordem(), [3, 1, 2, 4, 5].map(id));
    assert.equal(await avaliar("getComputedStyle(document.activeElement).outlineStyle !== 'none'"), true);
    const href = await avaliar("document.querySelector('.table-actions a').getAttribute('href')");
    assert.ok(href.includes("busca=disciplinas") && href.includes("q=TEST"));
    await navegar(href, "Os cinco critérios");
    assert.equal(await avaliar("document.querySelectorAll('.metrics dt').length"), 5);
    assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, "Perfil responsivo");
    for (const n of [4, 5]) {
      await navegar(`/professores/${id(n)}/disciplinas/${disciplina.id}`, n === 4 ? "Faltam 1" : "Ainda não há avaliações");
      assert.equal(await avaliar("document.querySelectorAll('.metrics').length"), 0, "Não exibe critérios abaixo do mínimo");
    }
    console.log(`Perfil/comparação: ${width}px aprovado`);
  }
  falharComparacao = true;
  await navegar(`/professores/${id(1)}/disciplinas/${disciplina.id}`, "Não foi possível carregar os outros professores");
  assert.equal(await avaliar("document.querySelector('main').innerText.includes('Nenhum outro professor cadastrado')"), false);
  assert.equal(await avaliar("document.querySelectorAll('.metrics dt').length"), 5, "Falha complementar preserva critérios");
  falharComparacao = false; somenteAtual = true;
  await navegar(`/professores/${id(1)}/disciplinas/${disciplina.id}`, "Nenhum outro professor cadastrado");
  assert.deepEqual(erros, [], "Sem exceções no navegador");
  console.log("Falha complementar e vazio confirmado: aprovados. API sintética; sem validação PostgreSQL.");
} finally {
  if (socket?.readyState === WebSocket.OPEN) { await cdp("Browser.close").catch(() => {}); socket.close(); }
  await encerrar(browser);
  await encerrar(next);
  await new Promise((r) => fixture.close(r));
  if (perfil) {
    assert.ok(resolve(perfil).startsWith(resolve(tmpdir()) + "/") || resolve(perfil).startsWith(resolve(tmpdir()) + "\\"));
    await rm(perfil, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 });
  }
}
