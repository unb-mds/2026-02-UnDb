// Captura somente a referência histórica, com fixtures explicitamente demonstrativas.
// Exige git archive do SHA abaixo em PROTOTIPO_REFERENCE_DIR e build prévio.
import assert from "node:assert/strict";
import { spawn, execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { mkdtempSync, readFileSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const sha = "91ecb79efc1c473624e0adeb358d57eab835da98";
assert.ok(process.env.PROTOTIPO_REFERENCE_DIR && process.env.PREVIEW_DIR);
const fonte = resolve(process.env.PROTOTIPO_REFERENCE_DIR);
const repo = fileURLToPath(new URL("../../", import.meta.url));
const git = (...args) => execFileSync("git", args, { cwd: repo, windowsHide: true });
// Conferir todos os fontes, não apenas a pasta /prototipo: critérios são compartilhados.
for (const registro of git("ls-tree", "-rz", sha, "frontend/src").toString().split("\0").filter(Boolean)) {
  const [cabecalho, caminho] = registro.split("\t");
  const esperado = cabecalho.split(" ")[2];
  const origem = readFileSync(join(fonte, caminho.slice("frontend/".length)));
  // git archive respeita core.autocrlf no Windows; binários permanecem intactos.
  const bytes = /\.(tsx?|css)$/.test(caminho) ? Buffer.from(origem.toString("utf8").replace(/\r\n/g, "\n")) : origem;
  const atual = createHash("sha1").update(`blob ${bytes.length}\0`).update(bytes).digest("hex");
  assert.equal(atual, esperado, `Fonte histórica alterada: ${caminho}`);
}
const destino = resolve(process.env.PREVIEW_DIR);
const perfil = mkdtempSync(join(tmpdir(), "undb-referencia-186-"));
let next, browser, socket, sequencia = 0;
const pendentes = new Map();
const evidencias = [];
async function aguardar(condicao, descricao) {
  const inicio = Date.now();
  while (Date.now() - inicio < 25000) {
    if (await condicao()) return;
    await new Promise(r => setTimeout(r, 100));
  }
  throw new Error(`Timeout: ${descricao}`);
}
function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequencia;
    const timer = setTimeout(() => { pendentes.delete(id); reject(new Error(method)); }, 20000);
    pendentes.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function avaliar(expression) {
  const r = await cdp("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  assert.equal(r.exceptionDetails, undefined);
  return r.result.value;
}
async function encerrar(p) {
  if (!p || p.exitCode !== null || p.signalCode !== null) return;
  const fim = new Promise(r => p.once("exit", r));
  p.kill();
  await fim;
}
try {
  for (const porta of [3102, 9226]) {
    const reserva = createServer();
    await new Promise((resolve, reject) => { reserva.once("error", reject); reserva.listen(porta, resolve); });
    await new Promise(r => reserva.close(r));
  }
  await mkdir(destino, { recursive: true });
  next = spawn(process.execPath, [join(fonte, "node_modules/next/dist/bin/next"), "start", "-p", "3102"], { cwd: fonte, stdio: "ignore", windowsHide: true });
  await aguardar(async () => { try { return (await fetch("http://localhost:3102/prototipo")).ok; } catch { return false; } }, "referência compilada");
  browser = spawn(process.env.BROWSER_PATH ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe", ["--headless=new", "--disable-gpu", "--no-first-run", "--remote-debugging-port=9226", `--user-data-dir=${perfil}`, "about:blank"], { stdio: "ignore", windowsHide: true });
  await aguardar(async () => { try { return (await fetch("http://localhost:9226/json")).ok; } catch { return false; } }, "navegador");
  const tabs = await (await fetch("http://localhost:9226/json")).json();
  socket = new WebSocket(tabs.find(t => t.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve, reject) => { socket.addEventListener("open", resolve, { once: true }); socket.addEventListener("error", reject, { once: true }); });
  socket.addEventListener("message", ({ data }) => {
    const m = JSON.parse(data), p = pendentes.get(m.id);
    if (!p) return;
    clearTimeout(p.timer); pendentes.delete(m.id);
    if (m.error) p.reject(new Error(JSON.stringify(m.error))); else p.resolve(m.result);
  });
  await cdp("Page.enable");
  const telas = [
    ["entrada", "", "Encontre professores e disciplinas"],
    ["busca", "etapa=busca&tipo=professor", "O que você quer encontrar?"],
    ["resultados-professores", "etapa=resultados&tipo=professor&q=Ana", "Resultados da busca"],
    ["resultados-disciplinas", "etapa=resultados&tipo=disciplina&q=Algoritmos", "Resultados da busca"],
    ["escolha", "etapa=resultados&tipo=professor&q=Ana&professor=ana-demo", "Disciplinas de Ana"],
    ["comparacao", "etapa=comparacao&disciplina=algoritmos-demo&ordem=recomendacao", "Comparação de professores"],
    ["formulario", "etapa=avaliacao&professor=ana-demo&disciplina=algoritmos-demo", "Avaliar professor na disciplina"],
    ["acesso", "etapa=acesso&professor=ana-demo&disciplina=algoritmos-demo&retornoEtapa=avaliacao", "Minha conta"],
  ];
  for (const tema of ["light", "dark"]) for (const largura of [320, 768, 1280]) {
    await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
    await cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura === 320 });
    for (const [tela, query, titulo] of telas) {
      await cdp("Page.navigate", { url: `http://localhost:3102/prototipo?${query}` });
      await aguardar(() => avaliar(`document.readyState === 'complete' && !!document.querySelector('h1') && document.querySelector('main').innerText.includes(${JSON.stringify(titulo)})`), tela);
      await avaliar("document.fonts.ready.then(() => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(() => r(true)))))");
      assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `${tela}/${largura}/${tema}`);
      let captura;
      if ((largura === 320 && tema === "dark") || (largura === 1280 && tema === "light")) {
        captura = `${tela}-${tema}-${largura}.png`;
        const layout = await cdp("Page.getLayoutMetrics");
        const shot = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: largura, height: layout.cssContentSize.height, scale: 1 } });
        await writeFile(join(destino, captura), Buffer.from(shot.data, "base64"));
      }
      evidencias.push({ tela, tema, largura, captura });
    }
  }
  await writeFile(join(destino, "resultado.json"), JSON.stringify({ commit: sha, origem: "Protótipo histórico; fixtures demonstrativas, sem persistência", fontesConferidos: true, combinacoes: evidencias.length, evidencias }, null, 2) + "\n");
  console.log(`Referência ${sha}: ${evidencias.length} combinações capturadas/conferidas.`);
} finally {
  if (socket?.readyState === WebSocket.OPEN) await cdp("Browser.close").catch(() => {});
  socket?.close();
  await encerrar(browser); await encerrar(next);
  assert.ok(resolve(perfil).startsWith(resolve(tmpdir()) + "/") || resolve(perfil).startsWith(resolve(tmpdir()) + "\\"));
  await rm(perfil, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 });
}
