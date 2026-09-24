// Interface controlada por padrão; E2E_FIXTURE ativa FastAPI/PostgreSQL reais (runner Python).
// Requer build padrão (API localhost:8000), Node 22+ e Edge/Chromium headless.
import assert from "node:assert/strict";
import { spawn, spawnSync } from "node:child_process";
import { existsSync, mkdtempSync } from "node:fs";
import { rm } from "node:fs/promises";
import { createServer } from "node:http";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const navegador = process.env.BROWSER_PATH ?? "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe";
assert.ok(existsSync(navegador), "Informe BROWSER_PATH com o executável Edge/Chromium.");
assert.ok(globalThis.WebSocket, "O teste de navegador requer Node 22+ (WebSocket nativo).");
// Não se conectar a servidores ou navegadores já em uso na máquina.
const real = process.env.E2E_FIXTURE ? JSON.parse(process.env.E2E_FIXTURE) : null;
for (const porta of (real ? [3100, 9223] : [8000, 3100, 9223])) {
  const reserva = createServer();
  await new Promise((resolve, reject) => {
    reserva.once("error", () => reject(new Error(`A porta ${porta} precisa estar livre para este teste.`)));
    reserva.listen(porta, resolve);
  });
  await new Promise((resolve) => reserva.close(resolve));
}
const frontend = fileURLToPath(new URL("../", import.meta.url));
const perfil = mkdtempSync(join(tmpdir(), "undb-avaliacao-browser-"));
const professorId = real?.professorId ?? "11111111-1111-4111-8111-111111111111";
const disciplinaId = real?.disciplinaId ?? "22222222-2222-4222-8222-222222222222";
const caminho = `/professores/${professorId}/disciplinas/${disciplinaId}`;
let consultasSessao = 0;
let autenticado = true;
let statusEnvio = 200;
let statusConsulta = 200;
let statusConfirmacao = 400;
let statusCadastro = 202;
let falhaComplementar = false;
let consultaInterrompida = false;
const professor = { id: professorId, nome: "Professor de teste", departamento: "CIC", siape: null, identidade_confirmada: true };
const disciplina = { id: disciplinaId, codigo: "CIC0001", nome: "Disciplina de teste", departamento: "CIC", creditos: null, identificador_externo: null };
const envios = [];
const fixture = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Content-Type", "application/json");
  if (req.method === "OPTIONS") { res.writeHead(204).end(); return; }
  const institucional = req.url.startsWith("/api/professores/") || req.url.startsWith("/api/disciplinas/");
  if (institucional && consultaInterrompida) { req.socket.destroy(); return; }
  if (institucional && statusConsulta !== 200) { res.writeHead(statusConsulta).end(JSON.stringify({detail:"Serviço indisponível"})); return; }
  if (req.url === `/api${caminho}`) {
    res.end(JSON.stringify({
      professor_id: professorId, disciplina_id: disciplinaId,
      professor: { id: professorId, nome: "Professor de teste", departamento: "CIC" },
      disciplina: { id: disciplinaId, codigo: "CIC0001", nome: "Disciplina de teste", departamento: "CIC" },
      total_avaliacoes: 0, dados_suficientes: false,
    }));
  } else if (req.url === `/api/professores/${professorId}`) {
    res.end(JSON.stringify(professor));
  } else if (req.url === `/api/disciplinas/${disciplinaId}`) {
    res.end(JSON.stringify(disciplina));
  } else if (req.url === `/api/professores/${professorId}/disciplinas` || req.url === `/api/disciplinas/${disciplinaId}/turmas`) {
    res.writeHead(falhaComplementar ? 503 : 200).end(JSON.stringify(falhaComplementar ? {detail:"Falha complementar"} : []));
  } else if (req.url.startsWith(`/api/disciplinas/${disciplinaId}/professores`)) {
    res.end(JSON.stringify({disciplina, professores:[]}));
  } else if (req.url === "/api/auth/sessao") {
    consultasSessao += 1; res.end(JSON.stringify({ autenticado }));
  } else if (req.method === "POST" && req.url === "/api/avaliacoes") {
    let body = "";
    for await (const chunk of req) body += chunk;
    envios.push({ body: JSON.parse(body), cookie: req.headers.cookie });

    res.writeHead(statusEnvio).end(JSON.stringify(statusEnvio === 200 ? {} : {detail:"Rejeição de teste"}));
  } else if (req.url === "/api/auth/confirmar") {
    res.writeHead(statusConfirmacao).end(JSON.stringify(statusConfirmacao === 200 ? {message:"E-mail confirmado."} : {detail:"Falha de confirmação"}));
  } else if (req.url === "/api/auth/cadastro") {
    res.writeHead(statusCadastro).end(JSON.stringify(statusCadastro === 202 ? {message:"Se o endereço informado estiver disponível, enviaremos um link de confirmação."} : {detail:[{loc:["body","nome"],msg:"Nome inválido"}]}));
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
function aguardarSaida(processo, timeout = 5000) {
  if (!processo || processo.exitCode !== null || processo.signalCode !== null) {
    return Promise.resolve(true);
  }
  return new Promise((resolve) => {
    const concluir = (encerrou) => {
      clearTimeout(timer);
      processo.off("exit", aoSair);
      resolve(encerrou);
    };
    const aoSair = () => concluir(true);
    const timer = setTimeout(() => concluir(false), timeout);
    processo.once("exit", aoSair);
  });
}
async function encerrarProcesso(processo, descricao) {
  if (!processo || processo.exitCode !== null || processo.signalCode !== null) return;
  processo.kill();
  if (await aguardarSaida(processo)) return;
  processo.kill("SIGKILL");
  if (!(await aguardarSaida(processo))) {
    throw new Error(`Timeout ao encerrar ${descricao}.`);
  }
}
async function removerPerfilTemporario() {
  const codigosRetentaveis = new Set(["EBUSY", "ENOTEMPTY", "EPERM"]);
  for (let tentativa = 1; tentativa <= 20; tentativa += 1) {
    try {
      await rm(perfil, { recursive: true, force: true });
      return;
    } catch (erro) {
      if (!codigosRetentaveis.has(erro?.code) || tentativa === 20) throw erro;
      await new Promise((resolve) => setTimeout(resolve, 250));
    }
  }
}
const texto = () => avaliar("document.body.innerText");
const enviar = () => avaliar('document.querySelector("button[type=submit]").click()');
const aguardarTexto = (trecho) => aguardar(async () => (await texto()).includes(trecho), trecho);

try {
  if (!real) await new Promise((resolve, reject) => { fixture.once("error", reject); fixture.listen(8000, resolve); });
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
  if (!real) await cdp("Network.setCookie", { name: "undb_session", value: "cookie-apenas-de-teste", url: "http://localhost:8000", httpOnly: true, sameSite: "Lax" });
  await cdp("Page.navigate", { url: `http://localhost:3100${caminho}` });
  await aguardarTexto("Avaliar este professor na disciplina");
  await avaliar('Array.from(document.querySelectorAll("a")).find(a => a.textContent.includes("Avaliar este professor")).click()');
  await aguardar(async () => await avaliar('document.querySelectorAll("select").length === 5'), "formulário");
  assert.match(await texto(), /Professor de teste/);
  assert.match(await texto(), /Disciplina de teste/);
  // Confirma hidratação antes de testar a validação local.
  await avaliar('document.querySelector("form").dispatchEvent(new Event("submit", {bubbles:true, cancelable:true}))');
  await aguardarTexto("Selecione uma opção válida para Didática.");
  await enviar();
  assert.equal(await avaliar('document.querySelector("form").checkValidity()'), false);
  assert.equal(envios.length, 0);
  await avaliar(`Object.entries({didatica:"5", dificuldade:"DIFICIL", chamada:"false", material:"NAO_DISPONIBILIZA", recomenda:"false"}).forEach(([nome, valor]) => { const campo = document.querySelector('[name="'+nome+'"]'); campo.value = valor; campo.dispatchEvent(new Event("change", {bubbles:true})); })`);
  assert.equal(await avaliar('document.querySelector("form").checkValidity()'), true);
  assert.equal(await avaliar('document.querySelector("button[type=submit]").disabled'), false);
  const respostas = () => avaliar('Object.fromEntries(new FormData(document.querySelector("form")))');
  const preenchidas = await respostas();
  if (real) {
    const banco = () => JSON.parse(executarPython("--inspect"));
    for (const token of [null, "sessao-invalida", real.expiredToken]) {
      await cdp("Network.clearBrowserCookies");
      if (token) await cdp("Network.setCookie", { name:"undb_session", value:token, url:"http://localhost:8000", httpOnly:true, sameSite:"Lax" });
      await enviar();
      await aguardarTexto("Entre na sua conta");
      assert.deepEqual(await respostas(), preenchidas);
      assert.deepEqual(banco(), []);
    }
    // Login HTTP real preserva as respostas no formulário original.
    const login = await avaliar(`fetch("http://localhost:8000/api/auth/login", {method:"POST", credentials:"include", headers:{"Content-Type":"application/json"}, body:JSON.stringify(${JSON.stringify({email:real.email, senha:real.senha})})}).then(r=>r.status)`);
    assert.equal(login, 200);
    await enviar();
    await aguardarTexto("link recebido");
    assert.deepEqual(banco(), []);
    assert.deepEqual(await respostas(), preenchidas);
    const confirmacao = await avaliar(`fetch("http://localhost:8000/api/auth/confirmar", {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({token:${JSON.stringify(real.confirmationToken)}})}).then(r=>r.status)`);
    assert.equal(confirmacao, 200);
    // Altera só o corpo da requisição: a rejeição 422 vem da API real.
    await avaliar(`window.fetchOriginal = window.fetch; window.fetch = (url, init) => {
      if (String(url).endsWith("/api/avaliacoes")) init = {...init, body:JSON.stringify({...JSON.parse(init.body), didatica:6})};
      return window.fetchOriginal(url, init);
    }`);
    await enviar();
    await aguardarTexto("Revise os campos: Didática");
    await avaliar('window.fetch = window.fetchOriginal');
    assert.deepEqual(banco(), []);
    assert.deepEqual(await respostas(), preenchidas);
    await enviar();
    await aguardarTexto("Avaliação registrada com sucesso");
    const primeira = banco();
    assert.equal(primeira.length, 1);
    assert.equal(primeira[0].usuario_id, real.usuarioId);
    assert.equal(primeira[0].didatica, 5);
    assert.equal(primeira[0].qualidade_material, null);
    await avaliar('document.querySelector("[name=didatica]").value="2"; document.querySelector("[name=material]").value="BOM"');
    await enviar();
    await aguardarTexto("Avaliação registrada com sucesso");
    const segunda = banco();
    assert.equal(segunda.length, 1);
    assert.equal(segunda[0].id, primeira[0].id);
    assert.equal(segunda[0].created_at, primeira[0].created_at);
    assert.equal(segunda[0].didatica, 2);
    assert.equal(segunda[0].qualidade_material, "BOM");
    assert.equal(segunda[0].disponibiliza_material, true);
    assert.ok(segunda[0].updated_at >= primeira[0].updated_at);
    await cdp("Network.setBlockedURLs", {urls:["*api/avaliacoes*"]});
    await enviar();
    await aguardarTexto("Verifique sua conexão");
    assert.equal((await respostas()).material, "BOM");
    assert.deepEqual(banco(), segunda);
    await cdp("Network.setBlockedURLs", {urls:[]});
    console.log("Integração real: formulário → FastAPI → PostgreSQL; criação, substituição com mesmo ID/linha, sessões ausente/inválida/expirada, e-mail não confirmado, 422 e falha de rede sem perda das respostas.");
  } else {
    autenticado = false;
    await enviar();
    await aguardarTexto("Entre na sua conta");
    assert.equal(envios.length, 0);
    autenticado = true;
    for (const [status, mensagem] of [[401,"Entre na sua conta"], [403,"link recebido"], [422,"Revise as opções"], [503,"não conseguiu confirmar"]]) {
      statusEnvio = status;
      await enviar();
      await aguardarTexto(mensagem);
      assert.deepEqual(await respostas(), preenchidas);
      assert.ok(!(await texto()).includes("Avaliação registrada com sucesso"));
    }
    statusEnvio = 200;
    await enviar();
    await aguardarTexto("Avaliação registrada com sucesso");
    assert.ok(envios.at(-1).cookie.includes("undb_session="));
    assert.ok(!("usuario_id" in envios.at(-1).body));
    assert.ok(consultasSessao > 0);
  }
  // Acesso direto não predefine respostas e mantém os cinco campos obrigatórios.
  await cdp("Page.navigate", { url: `http://localhost:3100${caminho}/avaliar` });
  await aguardar(async () => await avaliar('document.querySelectorAll("select").length === 5'), "formulário direto");
  assert.equal(await avaliar('document.querySelector("form").reportValidity()'), false);
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
  assert.equal(await avaliar('document.querySelectorAll("textarea, [name=historico], [name=comentario]").length'), 0);
  if (!real) await verificarCorrecoesInterface();
  console.log("Interface aprovada: cinco critérios, escalas, validação local, respostas preservadas, teclado, acesso direto e 6 combinações de tema/largura.");
} finally {
  if (socket?.readyState === WebSocket.OPEN) {
    await cdp("Browser.close").catch(() => {});
    socket.close();
  }
  if (!(await aguardarSaida(browser))) await encerrarProcesso(browser, "o navegador");
  await encerrarProcesso(next, "o Next.js");
  fixture.closeAllConnections();
  if (fixture.listening) await new Promise((resolve) => fixture.close(resolve));
  // Somente o perfil temporário exclusivo criado por este teste.
  await removerPerfilTemporario();
}

function executarPython(acao) {
  const result = spawnSync(process.env.E2E_PYTHON, ["-m", "tests.integration_avaliacao", acao], {
    cwd: join(frontend, "../backend"), encoding:"utf8", windowsHide:true, env:process.env,
  });
  assert.equal(result.status, 0, result.stderr);
  return result.stdout;
}

async function verificarCorrecoesInterface() {
  for (const rota of ["/professores/abc", "/disciplinas/abc", `/professores/${professorId}/disciplinas/abc`, `/professores/abc/disciplinas/${disciplinaId}/avaliar`]) {
    await cdp("Page.navigate", {url:`http://localhost:3100${rota}`});
    await aguardarTexto("Não encontramos isso");
    assert.equal(await avaliar('!!document.querySelector("header")'), true);
  }
  for (const modo of ["503", "conexao", "complementar"]) {
    statusConsulta = modo === "503" ? 503 : 200;
    consultaInterrompida = modo === "conexao";
    falhaComplementar = modo === "complementar";
    const rotas = [`/professores/${professorId}`, `/disciplinas/${disciplinaId}`];
    if (modo !== "complementar") rotas.push(caminho);
    for (const rota of rotas) {
      await cdp("Page.navigate", {url:`http://localhost:3100${rota}`});
      await aguardarTexto("Não foi possível carregar esta página");
      assert.equal(await avaliar('!!document.querySelector("header")'), true);
    }
  }
  falhaComplementar = false;
  consultaInterrompida = false;
  statusConsulta = 200;
  await avaliar('document.querySelector("main button").click()');
  await aguardarTexto("Comparação de professores");
  await cdp("Page.navigate", {url:`http://localhost:3100${caminho}`});
  await aguardarTexto("Avaliar este professor na disciplina");
  await cdp("Page.navigate", {url:"http://localhost:3100/cadastro"});
  await aguardar(async () => await avaliar('!!document.querySelector("[name=nome]")'), "cadastro");
  await avaliar(`document.querySelector('[name=nome]').value='   '; document.querySelector('[name=email]').value='TESTE@ALUNO.UNB.BR'; document.querySelector('[name=senha]').value='senha-teste-local'`);
  assert.equal(await avaliar('document.querySelector("form").checkValidity()'), true);
  await enviar();
  await aguardarTexto("Informe seu nome");
  assert.equal(await avaliar('document.activeElement.name'), "nome");
  await avaliar('document.querySelector("[name=nome]").value="Estudante"');
  statusCadastro = 422;
  await enviar();
  await aguardarTexto("Revise os dados do cadastro");
  assert.equal(await avaliar('document.querySelector("[name=email]").value'), "TESTE@ALUNO.UNB.BR");
  statusCadastro = 202;
  await enviar();
  await aguardarTexto("Se o endereço informado estiver disponível");
  for (const tema of ["light", "dark"]) {
    await cdp("Emulation.setEmulatedMedia", {features:[{name:"prefers-color-scheme", value:tema}]});
    const contraste = await avaliar(`(() => {
      const style = getComputedStyle(document.querySelector('button[type=submit]'));
      const lum = rgb => { const c = rgb.match(/[\\d.]+/g).slice(0,3).map(Number).map(x => {x/=255; return x<=0.04045 ? x/12.92 : ((x+0.055)/1.055)**2.4}); return c[0]*0.2126+c[1]*0.7152+c[2]*0.0722; };
      const a=lum(style.color), b=lum(style.backgroundColor); return (Math.max(a,b)+0.05)/(Math.min(a,b)+0.05);
    })()`);
    assert.ok(contraste >= 4.5, `${tema}: ${contraste}`);
  }
  statusConfirmacao = 503;
  await cdp("Page.navigate", {url:"http://localhost:3100/confirmar-email?token=teste"});
  await aguardarTexto("Verifique sua conexão");
  assert.ok(!(await texto()).includes("Este link é inválido"));
  statusConfirmacao = 200;
  await avaliar('document.querySelector("main button").click()');
  await aguardarTexto("E-mail confirmado.");
  statusConfirmacao = 400;
  await cdp("Page.navigate", {url:"http://localhost:3100/confirmar-email?token=invalido"});
  await aguardarTexto("Este link é inválido ou expirou");
  console.log("Regressões de interface: IDs malformados, indisponibilidade e recuperação, domínio maiúsculo, nome em branco, 422, confirmação transitória/token inválido e contraste claro/escuro.");
}
