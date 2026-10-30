// #157: rotas reais → FastAPI → PostgreSQL. Sem interceptação de respostas.
// Preparar banco isolado com backend/tests/seed_resultados.py e API em :8000.
// RESULTADOS_FIXTURE_FILE aponta para o JSON da preparação; PREVIEW_DIR recebe evidências.
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { existsSync, mkdtempSync, readFileSync } from "node:fs";
import { mkdir, rm, writeFile } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

assert.ok(process.env.RESULTADOS_FIXTURE_FILE, "Informe RESULTADOS_FIXTURE_FILE, gerado em PostgreSQL isolado.");
assert.ok(process.env.PREVIEW_DIR, "Informe PREVIEW_DIR para salvar evidências.");
const fixture = JSON.parse(readFileSync(process.env.RESULTADOS_FIXTURE_FILE, "utf8").replace(/^\uFEFF/, ""));
const navegador = process.env.BROWSER_PATH ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
assert.ok(existsSync(navegador), "Informe BROWSER_PATH com Edge/Chromium.");
const frontend = fileURLToPath(new URL("../", import.meta.url));
const destino = resolve(process.env.PREVIEW_DIR);
const perfil = mkdtempSync(join(tmpdir(), "undb-resultados-"));
const [p0, p1, p2, p3, p4, p5, p6] = fixture.professores;
const [d0, d1] = fixture.disciplinas;
const base = "http://localhost:3100";
let next, browser, socket;
let sequencia = 0;
const pendentes = new Map();
const evidencias = [];
const errosPagina = [];

async function aguardar(condicao, descricao) {
  const inicio = Date.now();
  while (Date.now() - inicio < 25000) {
    if (await condicao()) return;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`Timeout: ${descricao}`);
}
function cdp(method, params = {}) {
  return new Promise((resolve, reject) => {
    const id = ++sequencia;
    const timer = setTimeout(() => { pendentes.delete(id); reject(new Error(`Timeout: ${method}`)); }, 15000);
    pendentes.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });
}
async function avaliar(expression) {
  const resultado = await cdp("Runtime.evaluate", { expression, returnByValue: true, awaitPromise: true });
  if (resultado.exceptionDetails) throw new Error(JSON.stringify(resultado.exceptionDetails));
  return resultado.result.value;
}
const texto = () => avaliar("document.querySelector('main')?.innerText ?? ''");
const esperarTexto = (trecho) => aguardar(async () => (await texto()).includes(trecho), trecho);
async function navegar(rota, trecho) {
  await cdp("Page.navigate", { url: base + rota });
  await aguardar(async () => await avaliar(`location.pathname === ${JSON.stringify(rota)} && document.readyState === 'complete'`), rota);
  await esperarTexto(trecho);
}
async function buscar(rota, termo, trecho) {
  await navegar(rota, rota === "/professores" ? "Buscar professor" : "Buscar disciplina");
  await aguardar(async () => await avaliar(`!!document.querySelector('input[type=search]') && Object.keys(document.querySelector('input[type=search]')).some(k => k.startsWith('__reactProps'))`), "hidratação da busca");
  await avaliar("document.querySelector('input[type=search]').focus()");
  await cdp("Input.insertText", { text: termo });
  await esperarTexto(trecho);
  await aguardar(async () => !(await texto()).includes("Carregando disciplinas"), "disciplinas carregadas");
}
function seletorRota(caminho) {
  return `a[href="${caminho}"], a[href^="${caminho}?"]`;
}

async function api(path) {
  const resposta = await fetch("http://localhost:8000" + path);
  assert.equal(resposta.status, 200, path);
  return resposta.json();
}
async function encerrar(processo) {
  if (!processo || processo.exitCode !== null) return;
  const fim = new Promise((r) => processo.once("exit", r));
  processo.kill();
  await fim;
}

try {
  // Recusa servidores/navegadores preexistentes nas portas do teste.
  for (const porta of [3100, 9224]) {
    const reserva = createServer();
    await new Promise((resolve, reject) => { reserva.once("error", reject); reserva.listen(porta, resolve); });
    await new Promise((r) => reserva.close(r));
  }
  await mkdir(destino, { recursive: true });
  await aguardar(async () => { try { return (await fetch("http://localhost:8000/health")).ok; } catch { return false; } }, "API pronta");
  const comparacao = await api(`/api/disciplinas/${d0.id}/professores?ordenar_por=recomendacao`);
  assert.deepEqual(comparacao.professores.map((p) => p.professor_id), [p0, p1, p2, p3, p4, p5]);
  assert.deepEqual(comparacao.professores.map((p) => p.total_avaliacoes), [4, 3, 3, 4, 2, 0]);
  assert.equal(comparacao.professores[3].chamada, "CONFLITANTE");
  for (const p of comparacao.professores.slice(4)) {
    assert.equal(p.dados_suficientes, false);
    assert.equal("didatica" in p, false);
    assert.equal("recomenda" in p, false);
  }
  assert.deepEqual((await api(`/api/professores/${p0}/disciplinas`)).map((d) => d.id), [d0.id, d1.id]);
  assert.deepEqual((await api(`/api/professores/${p1}/disciplinas`)).map((d) => d.id), [d0.id]);
  next = spawn(process.execPath, ["node_modules/next/dist/bin/next", "start", "-p", "3100"], {
    cwd: frontend, stdio: "ignore", windowsHide: true,
    env: { ...process.env, API_INTERNAL_URL: "http://localhost:8000" },
  });
  await aguardar(async () => { try { return (await fetch(base)).ok; } catch { return false; } }, "Next.js");
  browser = spawn(navegador, ["--headless=new", "--disable-gpu", "--no-first-run", "--remote-debugging-port=9224", `--user-data-dir=${perfil}`, "about:blank"], { stdio: "ignore", windowsHide: true });
  await aguardar(async () => { try { return (await fetch("http://localhost:9224/json")).ok; } catch { return false; } }, "Edge");
  const tabs = await (await fetch("http://localhost:9224/json")).json();
  socket = new WebSocket(tabs.find((t) => t.type === "page").webSocketDebuggerUrl);
  await new Promise((r, reject) => { socket.addEventListener("open", r, { once: true }); socket.addEventListener("error", reject, { once: true }); });
  socket.addEventListener("message", ({ data }) => {
    const mensagem = JSON.parse(data);
    if (mensagem.method === "Runtime.exceptionThrown") errosPagina.push(mensagem.params);
    const pendente = pendentes.get(mensagem.id);
    if (!pendente) return;
    clearTimeout(pendente.timer);
    pendentes.delete(mensagem.id);
    if (mensagem.error) pendente.reject(new Error(JSON.stringify(mensagem.error)));
    else pendente.resolve(mensagem.result);
  });
  await cdp("Page.enable");
  await cdp("Runtime.enable");
  await cdp("Network.enable");
  const telas = [
    { nome: "busca-inicial", abrir: () => navegar("/professores", "Digite ao menos 2 letras") },
    { nome: "busca-vazia", abrir: () => buscar("/professores", "Professor inexistente PR183", "Nenhum resultado") },
    { nome: "busca-erro", abrir: async () => {
      await cdp("Network.setBlockedURLs", { urls: ["*localhost:8000/api/professores*"] });
      await buscar("/professores", fixture.termo, "Não foi possível buscar");
    }, verificar: async () => {
      assert.doesNotMatch(await texto(), /Nenhum resultado/);
      assert.ok((await texto()).includes("Tentar novamente"));
    } },
    { nome: "busca-carregando", abrir: async () => {
      await navegar("/professores", "Digite ao menos 2 letras");
      await aguardar(async () => await avaliar("!!document.querySelector('input[type=search]') && Object.keys(document.querySelector('input[type=search]')).some(k => k.startsWith('__reactProps'))"), "busca hidratada");
      // Latência induzida, sem substituir a resposta da API real.
      await cdp("Network.emulateNetworkConditions", { offline: false, latency: 2000, downloadThroughput: -1, uploadThroughput: -1 });
      await avaliar("document.querySelector('input[type=search]').focus()");
      await cdp("Input.insertText", { text: fixture.termo });
      await esperarTexto("Buscando…");
    } },
    { nome: "busca-professores", abrir: () => buscar("/professores", fixture.termo, "Sem turma"), verificar: async () => {
      assert.equal(await avaliar("document.querySelectorAll('main h2').length"), 7, "Homônimos não são unidos");
      assert.equal(await avaliar(`document.querySelector(${JSON.stringify(seletorRota(`/professores/${p0}`))}).closest('li').querySelectorAll('ul > li').length`), 2);
      assert.equal(await avaliar(`document.querySelector(${JSON.stringify(seletorRota(`/professores/${p1}`))}).closest('li').querySelectorAll('ul > li').length`), 1);
      assert.ok((await texto()).includes("Nenhuma turma ativa registrada"));
      for (const id of [p0, p1]) assert.ok(await avaliar(`!!document.querySelector(${JSON.stringify(seletorRota(`/professores/${id}/disciplinas/${d0.id}/avaliar`))})`));
    } },
    { nome: "busca-disciplinas", abrir: () => buscar("/disciplinas", "REV183", d1.nome), verificar: async () => {
      assert.equal(await avaliar("document.querySelectorAll('main ul > li').length"), 2);
      assert.ok((await texto()).includes("Código da disciplina: REV1831"));
    } },
    { nome: "detalhe-professor", abrir: () => navegar(`/professores/${p0}`, d1.nome) },
    { nome: "comparacao", abrir: () => navegar(`/disciplinas/${d0.id}`, "Comparação de professores"), verificar: async () => {
      assert.deepEqual(await avaliar("Array.from(document.querySelectorAll('main h3 a')).map(a => a.pathname.split('/').at(-1))"), [p0, p1, p2, p3, p4, p5]);
      for (const id of [p4, p5]) {
        const card = await avaliar(`document.querySelector('h3 a[href="/professores/${id}"]').closest('li').innerText`);
        assert.doesNotMatch(card, /%|Didática|Dificuldade|Faz chamada/);
      }
      assert.ok((await texto()).includes("Conflitante"));
    } },
    { nome: "agregado", abrir: () => navegar(`/professores/${p0}/disciplinas/${d0.id}`, "Baseado em 4 avaliações.") },
    { nome: "insuficiente", abrir: () => navegar(`/professores/${p4}/disciplinas/${d0.id}`, "Dados insuficientes"), verificar: async () => assert.doesNotMatch(await texto(), /%|Didática|Faz chamada/) },
    { nome: "sem-avaliacoes", abrir: () => navegar(`/professores/${p5}/disciplinas/${d0.id}`, "Ainda não há avaliações"), verificar: async () => assert.doesNotMatch(await texto(), /%|Didática|Faz chamada/) },
    { nome: "sem-turmas", abrir: () => navegar(`/professores/${p6}`, "Nenhuma turma ativa registrada") },
  ];
  for (const tema of ["light", "dark"]) {
    await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
    for (const largura of [320, 768, 1280]) {
      await cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura === 320 });
      for (const tela of telas) {
        await cdp("Network.setBlockedURLs", { urls: [] });
        await cdp("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
        await tela.abrir();
        await tela.verificar?.();
        await avaliar("document.fonts.ready.then(() => true)");
        assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `${tela.nome}/${tema}/${largura}: rolagem horizontal`);
        assert.equal(await avaliar("document.querySelectorAll('main h1').length"), 1);
        if (tela.nome === "comparacao") assert.equal(await avaliar("getComputedStyle(document.querySelector('main ul')).gridTemplateColumns.split(' ').length"), largura < 640 ? 1 : 2);
        // Tab real deve chegar aos atalhos e produzir foco visível.
        const alvo = tela.nome === "busca-professores" || tela.nome === "detalhe-professor"
          ? `/professores/${p0}/disciplinas/${d0.id}/avaliar` : null;
        if (alvo) {
          const seletor = seletorRota(alvo);
          await avaliar(`document.querySelector(${JSON.stringify(seletor)}).closest('li').querySelector('a').focus()`);
          await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
          await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
          assert.equal(await avaliar(`document.activeElement.pathname === ${JSON.stringify(alvo)} && document.activeElement.matches(':focus-visible') && getComputedStyle(document.activeElement).outlineStyle !== 'none'`), true, "Foco de Avaliar");
          await avaliar("document.activeElement.blur(); window.scrollTo(0, 0)");
        }
        let captura;
        if ((largura === 320 && tema === "dark") || (largura === 1280 && tema === "light")) {
          captura = `${tela.nome}-${tema}-${largura}.png`;
          const layout = await cdp("Page.getLayoutMetrics");
          const screenshot = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width: largura, height: layout.cssContentSize.height, scale: 1 } });
          await writeFile(join(destino, captura), Buffer.from(screenshot.data, "base64"));
        }
        evidencias.push({ tela: tela.nome, tema, largura, aprovado: true, captura });
      }
    }
  }
  await cdp("Network.emulateNetworkConditions", { offline: false, latency: 0, downloadThroughput: -1, uploadThroughput: -1 });
  // A falha de transporte não é sucesso; recuperar refaz a consulta real.
  await cdp("Network.setBlockedURLs", { urls: ["*localhost:8000/api/professores*"] });
  await buscar("/professores", fixture.termo, "Não foi possível buscar");
  await cdp("Network.setBlockedURLs", { urls: [] });
  await avaliar("Array.from(document.querySelectorAll('main button')).find(b => b.textContent.includes('Tentar novamente')).click()");
  await esperarTexto("7 resultado(s)");
  // Falha real de transporte em uma consulta complementar: preserva o professor
  // e não transforma indisponibilidade em lista vazia nem afeta os outros cartões.
  await cdp("Network.setBlockedURLs", { urls: [`*api/professores/${p0}/disciplinas`] });
  await buscar("/professores", fixture.termo, "Não foi possível carregar as disciplinas");
  assert.ok(await avaliar(`!!document.querySelector(${JSON.stringify(seletorRota(`/professores/${p0}`))})`));
  assert.ok(await avaliar(`!!document.querySelector(${JSON.stringify(seletorRota(`/professores/${p1}/disciplinas/${d0.id}/avaliar`))})`));
  await cdp("Network.setBlockedURLs", { urls: [] });
  await buscar("/professores", "Professor inexistente PR183", "Nenhum resultado");
  // Navega pelos atalhos reais com identidade professor/disciplina.
  await buscar("/professores", fixture.termo, "Sem turma");
  await avaliar(`document.querySelector(${JSON.stringify(seletorRota(`/professores/${p1}/disciplinas/${d0.id}/avaliar`))}).click()`);
  await esperarTexto("Avaliar professor na disciplina");
  assert.equal(await avaliar("location.pathname"), `/professores/${p1}/disciplinas/${d0.id}/avaliar`);
  assert.ok((await texto()).includes("Ana " + fixture.termo));
  assert.ok((await texto()).includes(d0.nome));
  await buscar("/professores", fixture.termo, "Sem turma");
  await avaliar(`document.querySelector(${JSON.stringify(seletorRota(`/disciplinas/${d0.id}`))}).click()`);
  await esperarTexto("Comparação de professores");
  assert.equal(await avaliar("location.pathname"), `/disciplinas/${d0.id}`);
  assert.deepEqual(errosPagina, [], "Exceções do navegador");
  const resumo = { origem: "FastAPI e PostgreSQL reais; dados sintéticos em banco isolado", combinacoes: evidencias.length,
    cenarios: ["homônimos por ID", "disciplinas agrupadas sem duplicatas", "atalhos", "ordenação e desempates", "conflito", "insuficiência", "zero avaliações", "zero turmas", "falha complementar", "busca vazia de resultados", "teclado e foco", "quebra de textos"], evidencias };
  await writeFile(join(destino, "resultado.json"), JSON.stringify(resumo, null, 2) + "\n");
  console.log(`Resultados/API/PostgreSQL: ${evidencias.length} combinações aprovadas; capturas e resultado.json em ${destino}`);
} finally {
  if (socket?.readyState === WebSocket.OPEN) {
    await cdp("Browser.close").catch(() => {});
    socket.close();
  }
  await encerrar(browser);
  await encerrar(next);
  // Exclusivamente o perfil temporário criado por este runner.
  const raizTemporaria = resolve(tmpdir());
  assert.equal(resolve(perfil).startsWith(raizTemporaria + "\\") || resolve(perfil).startsWith(raizTemporaria + "/"), true);
  await rm(perfil, { recursive: true, force: true, maxRetries: 20, retryDelay: 250 });
}
