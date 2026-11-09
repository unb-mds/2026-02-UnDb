import { contextoEmTransicao, lerTextoPagina } from "./browser-navigation.mjs";
import { contrasteTexto } from "./browser-contrast.mjs";
import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { existsSync, mkdtempSync, readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const frontend = fileURLToPath(new URL("../", import.meta.url));
const navegador =
  process.env.BROWSER_PATH ??
  (existsSync("/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe")
    ? "/mnt/c/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
    : "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe");
assert.ok(existsSync(navegador), "Defina BROWSER_PATH para Edge/Chromium.");

const real = process.env.DENUNCIA_FIXTURE_FILE
  ? JSON.parse(readFileSync(process.env.DENUNCIA_FIXTURE_FILE, "utf8"))
  : null;

for (const porta of real ? [3100, 9227] : [8000, 3100, 9227]) {
  const reserva = createServer();
  await new Promise((resolve, reject) => {
    reserva.once("error", reject);
    reserva.listen(porta, "127.0.0.1", resolve);
  });
  await new Promise((resolve) => reserva.close(resolve));
}

const professorId = real?.professorId ?? "11111111-1111-4111-8111-111111111111";
const disciplinaId = real?.disciplinaId ?? "22222222-2222-4222-8222-222222222222";
const versaoId = real?.versaoId ?? "33333333-3333-4333-8333-333333333333";
const mensagemId = real?.mensagemId ?? "44444444-4444-4444-8444-444444444444";

let statusDenuncia = 201;
let statusAgradecimento = 401;
let comentariosStatus = 200;
let contaAtual = null;
let denunciaAutenticada = false;
const denunciante = real?.denunciante ?? { email: "denunciante@aluno.unb.br", senha: "Senha-fixture-123!" };
const outraConta = real?.outraConta ?? { email: "outra@aluno.unb.br", senha: "Senha-fixture-123!" };
let agradecimentoConsumido = false;
let agradecimentoPendente = false;
const enviosDenuncia = [];
const exibicoesConfirmadas = [];

const fixture = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Content-Type", "application/json");

  if (req.method === "OPTIONS") {
    res.writeHead(204).end();
    return;
  }

  const url = new URL(req.url, "http://localhost:8000");
  const responder = (status, corpo) => {
    if (!res.destroyed) res.writeHead(status).end(JSON.stringify(corpo));
  };

  if (url.pathname === "/api/auth/sessao") { responder(200, {autenticado: !!contaAtual}); return; }
  if (url.pathname === "/api/auth/login") {
    let body = ""; for await (const parte of req) body += parte;
    contaAtual = JSON.parse(body).email;
    statusAgradecimento = contaAtual === denunciante.email ? 200 : 401;
    res.setHeader("Set-Cookie", "fixture=conta; Path=/; HttpOnly; SameSite=Lax");
    responder(200, {message:"Login realizado."}); return;
  }
  if (url.pathname === "/api/auth/logout") {
    contaAtual = null; statusAgradecimento = 401;
    res.setHeader("Set-Cookie", "fixture=; Path=/; Max-Age=0");
    responder(200, {message:"Sessão encerrada."}); return;
  }
  // Avaliação agregada da disciplina
  if (url.pathname === `/api/professores/${professorId}/disciplinas/${disciplinaId}`) {
    responder(200, {
      professor: { id: professorId, nome: "Prof. Teste Denúncia", departamento: "Dep. Informática" },
      disciplina: { id: disciplinaId, codigo: "CIC0099", nome: "MDS Teste", departamento: "Dep. Informática" },
      professor_id: professorId, disciplina_id: disciplinaId, total_avaliacoes: 5,
      dados_suficientes: true,
      didatica: 4.2,
      dificuldade: "MEDIO",
      chamada: false,
      disponibiliza_material: true,
      qualidade_material: "BOM",
      recomenda: 85,
    });
    return;
  }

  // Comentários publicados
  if (url.pathname === `/api/professores/${professorId}/disciplinas/${disciplinaId}/comentarios`) {
    if (comentariosStatus !== 200) { responder(comentariosStatus, {}); return; }
    responder(200, [
      {
        id: versaoId,
        texto: "Comentário publicado para verificação de denúncia RF21.",
        created_at: "2026-11-01T12:00:00Z",
      },
    ]);
    return;
  }

  // Denúncia de comentário
  const matchDenuncia = url.pathname.match(/^\/api\/comentarios\/([^/]+)\/denuncias$/);
  if (matchDenuncia) {
    const id = matchDenuncia[1];
    let corpo = "";
    for await (const parte of req) corpo += parte;
    const entrada = JSON.parse(corpo);
    enviosDenuncia.push({ id, ...entrada, cookie: req.headers.cookie });

    if (statusDenuncia === 201 && contaAtual) {
      if (denunciaAutenticada) { responder(409, {}); return; }
      denunciaAutenticada = true;
    }
    if (statusDenuncia === 201) {
      responder(201, { mensagem: "Denuncia registrada. Obrigado por contribuir." });
    } else if (statusDenuncia === 409) {
      responder(409, { detail: "ja existe denuncia aberta desta conta para a versao" });
    } else if (statusDenuncia === 404) {
      responder(404, { detail: "versao indisponivel para denuncia" });
    } else {
      responder(statusDenuncia, { detail: "erro simulado" });
    }
    return;
  }

  // Agradecimentos
  if (url.pathname === "/api/agradecimentos") {
    if (statusAgradecimento !== 200) {
      responder(statusAgradecimento, { detail: "Não autenticado" });
      return;
    }
    if (agradecimentoConsumido || !agradecimentoPendente) {
      responder(200, []);
    } else {
      responder(200, [
        { id: mensagemId, mensagem: "Obrigado por contribuir com a moderacao do conteudo." },
      ]);
    }
    return;
  }

  // Confirmação de exibição
  const matchExibido = url.pathname.match(/^\/api\/agradecimentos\/([^/]+)\/exibido$/);
  if (matchExibido) {
    const id = matchExibido[1];
    exibicoesConfirmadas.push(id);
    agradecimentoConsumido = true;
    res.writeHead(204).end();
    return;
  }

  responder(404, { detail: "não encontrado" });
});

let next, browser, socket, contador = 0;
const pendentes = new Map();

function caminhoParaNavegador(caminho) {
  if (caminho.startsWith("/mnt/c/")) {
    return caminho.replace("/mnt/c/", "C:/").replace(/\//g, "\\");
  }
  return caminho;
}

const baseDir = existsSync("/mnt/c/Users/wmede/AppData/Local/Temp")
  ? "/mnt/c/Users/wmede/AppData/Local/Temp"
  : tmpdir();
const perfil = mkdtempSync(join(baseDir, "undb-denuncia-browser-"));
const perfilNavegador = caminhoParaNavegador(perfil);

const cdp = (method, params = {}) =>
  new Promise((resolve, reject) => {
    const id = ++contador;
    const timer = setTimeout(() => {
      pendentes.delete(id);
      reject(new Error(`Timeout CDP ${method}`));
    }, 20000);
    pendentes.set(id, { resolve, reject, timer });
    socket.send(JSON.stringify({ id, method, params }));
  });

async function avaliar(expression) {
  if (expression.trimStart().startsWith("const ")) expression = `{ ${expression} }`;
  const resultado = await cdp("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (resultado.exceptionDetails) {
    throw new Error(JSON.stringify(resultado.exceptionDetails));
  }
  return resultado.result.value;
}

async function aguardar(consulta, nome) {
  for (let i = 0; i < 400; i++) {
    try {
      if (await consulta()) return;
    } catch (erro) {
      if (!contextoEmTransicao(erro)) throw erro;
    }
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`Não encontrado: ${nome}`);
}

const texto = () => lerTextoPagina(avaliar);
const esperarTexto = (valor) => aguardar(async () => (await texto()).includes(valor), valor);

async function navegar() {
  await cdp("Page.navigate", {
    url: `http://localhost:3100/professores/${professorId}/disciplinas/${disciplinaId}`,
  });
  await esperarTexto("Prof. Teste Denúncia");
  await esperarTexto("Comentários");
}

async function captura(nome) {
  if (!process.env.PREVIEW_DIR) return;
  mkdirSync(process.env.PREVIEW_DIR, { recursive: true });
  const imagem = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
  writeFileSync(join(process.env.PREVIEW_DIR, `${nome}.png`), Buffer.from(imagem.data, "base64"));
}

try {
  if (!real) await new Promise((resolve) => fixture.listen(8000, resolve));

  next = spawn(process.execPath, ["node_modules/next/dist/bin/next", "start", "-p", "3100"], {
    cwd: frontend,
    stdio: "inherit",
    windowsHide: true,
  });
  await aguardar(
    async () => {
      try {
        return (await fetch("http://127.0.0.1:3100/", { signal: AbortSignal.timeout(2000) })).ok;
      } catch {
        return false;
      }
    },
    "Next.js",
  );

  browser = spawn(
    navegador,
    [
      "--headless=new",
      "--edge-skip-compat-layer-relaunch",
      "--disable-gpu",
      "--no-first-run",
      "--remote-debugging-port=9227",
      `--user-data-dir=${perfilNavegador}`,
      "about:blank",
    ],
    { stdio: "ignore", windowsHide: true },
  );

  await aguardar(
    async () => {
      try {
        return (await fetch("http://127.0.0.1:9227/json", { signal: AbortSignal.timeout(2000) })).ok;
      } catch {
        return false;
      }
    },
    "Edge/Chromium",
  );

  const paginas = await (await fetch("http://127.0.0.1:9227/json", { signal: AbortSignal.timeout(2000) })).json();
  socket = new WebSocket(paginas.find((item) => item.type === "page").webSocketDebuggerUrl);
  await new Promise((resolve) => socket.addEventListener("open", resolve, { once: true }));

  socket.addEventListener("message", ({ data }) => {
    const mensagem = JSON.parse(data);
    const atual = pendentes.get(mensagem.id);
    if (!atual) return;
    clearTimeout(atual.timer);
    pendentes.delete(mensagem.id);
    if (mensagem.error) atual.reject(new Error(JSON.stringify(mensagem.error)));
    else atual.resolve(mensagem.result);
  });

  await cdp("Page.enable");
  await cdp("Network.enable");
  await cdp("Network.setCacheDisabled", { cacheDisabled: true });

  const clicar = (rotulo) => avaliar(`Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === ${JSON.stringify(rotulo)})?.click()`);
  async function abrir() {
    // O HTML pode chegar antes da hidratação. Abrir o modal é idempotente e
    // não envia denúncia; repetir somente esse clique até o React responder.
    await aguardar(async () => {
      await avaliar(`document.querySelector('[data-testid="botao-denunciar-${versaoId}"]')?.click()`);
      return (await texto()).includes("Denunciar comentário");
    }, "modal de denúncia interativo");
    assert.equal(await avaliar(`document.querySelectorAll('input[name="motivoDenuncia"]').length`), 7);
    assert.equal(await avaliar(`!!document.querySelector('textarea, input[type="text"]')`), false);
    assert.equal(await avaliar(`document.querySelector('dialog button[type="submit"]').disabled`), true);
    await avaliar(`document.querySelector('#motivo-SPAM').click()`);
    assert.equal(await avaliar(`document.querySelector('dialog button[type="submit"]').disabled`), false);
  }
  async function enviar(mensagem) {
    await clicar("Confirmar denúncia");
    await esperarTexto(mensagem);
    if (!real && mensagem === "registrada") {
      assert.equal(enviosDenuncia.at(-1)?.motivo, "SPAM");
      assert.equal(enviosDenuncia.at(-1)?.id, versaoId);
    }
    if (mensagem !== "registrada") {
      assert.ok(!(await texto()).includes("Denuncia registrada"));
      assert.ok(!(await texto()).includes("limiar"));
    }
  }
  async function login(conta) {
    await aguardar(async () => await avaliar(`!!document.querySelector('input[name="email"]')`), "formulário de login");
    await avaliar(`{
      const preencher = (nome, valor) => {
        const input = document.querySelector('input[name="' + nome + '"]');
        Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(input, valor);
        input.dispatchEvent(new Event('input', {bubbles:true}));
      };
      preencher('email', ${JSON.stringify(conta.email)}); preencher('senha', ${JSON.stringify(conta.senha)});
    }`);
    await clicar("Entrar"); await esperarTexto("Sua sessão está ativa");
  }
  const mensagensServidor = () => avaliar(`fetch('http://localhost:8000/api/agradecimentos', {credentials:'include'}).then(r => r.json())`);

  // Cada viewport testa leitura e denúncia, sem reutilizar um agradecimento consumido.
  for (const tema of ["light", "dark"]) {
    for (const largura of [1280, 320]) {
      await cdp("Emulation.setDeviceMetricsOverride", {width:largura, height:800, deviceScaleFactor:1, mobile:largura === 320});
      await cdp("Emulation.setEmulatedMedia", {features:[{name:"prefers-color-scheme", value:tema}]});
      await navegar(); await esperarTexto("Comentário publicado para verificação de denúncia RF21.");
      const contrasteBotao = await contrasteTexto(avaliar, `[data-testid="botao-denunciar-${versaoId}"]`);
      assert.ok(contrasteBotao >= 4.5, `Denunciar, sistema ${tema}, ${largura}px: ${contrasteBotao}`);
      await abrir();
      assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true);
      await captura(`denuncia-modal-${tema}-${largura}`);
      await enviar("registrada");
      const contrasteSucesso = await contrasteTexto(avaliar, 'dialog [role="status"] p');
      assert.ok(contrasteSucesso >= 4.5, `Sucesso da denúncia, sistema ${tema}, ${largura}px: ${contrasteSucesso}`);
      await clicar("Fechar");
    }
  }
  await cdp("Page.navigate", {url:"http://localhost:3100/login"});
  await login(denunciante);
  await navegar(); await abrir(); await enviar("registrada"); await clicar("Fechar");
  await abrir(); await enviar("Você já possui uma denúncia aberta"); await clicar("Cancelar");
  await abrir();
  if (real) {
    const sessao = await fetch("http://localhost:8000/api/auth/login", {
      method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(real.moderador),
    });
    assert.equal(sessao.status, 200);
    const cookie = sessao.headers.getSetCookie().map(v => v.split(";")[0]).join("; ");
    const acao = await fetch(`http://localhost:8000/api/moderacao/comentarios/${versaoId}/acoes`, {
      method:"POST", headers:{"Content-Type":"application/json", Cookie:cookie},
      body:JSON.stringify({acao:"REMOVER", motivo:"Verificar primeira exibição"}),
    });
    assert.equal(acao.status, 200, await acao.text());
  } else { statusDenuncia = 404; agradecimentoPendente = true; }
  await enviar("Este comentário não está mais disponível"); await clicar("Cancelar");
  assert.equal((await mensagensServidor()).length, 1, "GET não consome agradecimento");

  // Aba oculta: mensagem no DOM ainda não representa primeira exibição.
  const gate = await cdp("Page.addScriptToEvaluateOnNewDocument", {source:
    `Object.defineProperty(document, 'visibilityState', {configurable:true, get:() => 'hidden'});`});
  await cdp("Page.navigate", {url:"http://localhost:3100/login"});
  await esperarTexto("Sua sessão está ativa"); await esperarTexto("Obrigado por contribuir");
  assert.equal((await mensagensServidor()).length, 1);
  await clicar("Sair");
  await aguardar(async () => !(await texto()).includes("Obrigado por contribuir"), "limpeza no logout");
  await login(denunciante); await esperarTexto("Obrigado por contribuir");
  assert.equal((await mensagensServidor()).length, 1, "Login não consome antes da exibição");
  await avaliar(`Object.defineProperty(document, 'visibilityState', {configurable:true, get:() => 'visible'}); document.dispatchEvent(new Event('visibilitychange'));`);
  await aguardar(async () => (await mensagensServidor()).length === 0, "consumo após exibição");
  await clicar("Sair");
  await aguardar(async () => !(await texto()).includes("Obrigado por contribuir"), "limpeza de mensagem exibida");
  await login(outraConta);
  assert.ok(!(await texto()).includes("Obrigado por contribuir"));
  await cdp("Page.removeScriptToEvaluateOnNewDocument", {identifier:gate.identifier});
  if (!real) {
    comentariosStatus = 503;
    await navegar(); await esperarTexto("Não foi possível carregar os comentários");
    assert.ok(!(await texto()).includes("Ainda não há comentários publicados"));
    comentariosStatus = 200;
  }
  console.log(`Denúncia/agradecimentos aprovados: ${real ? "API/PostgreSQL reais" : "HTTP controlado"}, quatro viewports, visitante, conta não confirmada, duplicidade, 404, login/logout e consumo após visibilidade.`);

} finally {
  if (socket?.readyState === WebSocket.OPEN) {
    await cdp("Browser.close").catch(() => {});
  }
  socket?.close();
  for (const atual of pendentes.values()) {
    clearTimeout(atual.timer);
    atual.reject(new Error("Teste encerrado"));
  }
  browser?.kill();
  next?.kill();
  if (!real) {
    await new Promise((resolve) => {
      fixture.closeAllConnections();
      fixture.close(resolve);
    });
  }
  await new Promise((resolve) => setTimeout(resolve, 500));
  try {
    await rm(perfil, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
  } catch {
    // Arquivo de lock liberado assincronamente pelo Edge
  }
}
