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
    reserva.listen(porta, resolve);
  });
  await new Promise((resolve) => reserva.close(resolve));
}

const professorId = real?.professorId ?? "11111111-1111-4111-8111-111111111111";
const disciplinaId = real?.disciplinaId ?? "22222222-2222-4222-8222-222222222222";
const versaoId = real?.versaoId ?? "33333333-3333-4333-8333-333333333333";
const mensagemId = real?.mensagemId ?? "44444444-4444-4444-8444-444444444444";

let statusDenuncia = 201;
let statusAgradecimento = 200;
let agradecimentoConsumido = false;
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

  // Avaliação agregada da disciplina
  if (url.pathname === `/api/professores/${professorId}/disciplinas/${disciplinaId}`) {
    responder(200, {
      professor: { id: professorId, nome: "Prof. Teste Denúncia", departamento: "Dep. Informática" },
      disciplina: { id: disciplinaId, codigo: "CIC0099", nome: "MDS Teste", departamento: "Dep. Informática" },
      totalAvaliacoes: 5,
      dadosSuficientes: true,
      didatica: 4.2,
      dificuldade: "MEDIO",
      chamada: "NAO",
      disponibilizaMaterial: "SIM",
      qualidadeMaterial: "BOM",
      recomenda: 85,
    });
    return;
  }

  // Comentários publicados
  if (url.pathname === `/api/professores/${professorId}/disciplinas/${disciplinaId}/comentarios`) {
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
    if (agradecimentoConsumido) {
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
    if (await consulta()) return;
    await new Promise((r) => setTimeout(r, 100));
  }
  throw new Error(`Não encontrado: ${nome}`);
}

const texto = () => avaliar("document.body.innerText");
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
    stdio: "ignore",
    windowsHide: true,
  });
  await aguardar(
    async () => {
      try {
        return (await fetch("http://localhost:3100/")).ok;
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
        return (await fetch("http://localhost:9227/json")).ok;
      } catch {
        return false;
      }
    },
    "Edge/Chromium",
  );

  const paginas = await (await fetch("http://localhost:9227/json")).json();
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

  // 1. Navegação e verificação visual em desktop (1280px) e smartphone (320px)
  for (const tema of ["light", "dark"]) {
    for (const largura of [1280, 320]) {
      await cdp("Emulation.setDeviceMetricsOverride", {
        width: largura,
        height: 800,
        deviceScaleFactor: 1,
        mobile: largura === 320,
      });
      await cdp("Emulation.setEmulatedMedia", {
        features: [{ name: "prefers-color-scheme", value: tema }],
      });

      await navegar();
      await esperarTexto("Comentário publicado para verificação de denúncia RF21.");
      assert.equal(
        await avaliar("document.documentElement.scrollWidth <= innerWidth"),
        true,
        `Sem rolagem horizontal em ${tema}/${largura}px`,
      );

      // Verifica exibição do agradecimento no topo da tela
      await esperarTexto("Obrigado por contribuir com a moderacao do conteudo.");
      assert.ok(exibicoesConfirmadas.includes(mensagemId), "Confirma exibição pelo POST exibido");

      await captura(`denuncia-pagina-${tema}-${largura}`);
    }
  }

  // 2. Fluxo de denúncia com sucesso (201)
  await navegar();
  const temBotao = await avaliar(`!!document.querySelector('[data-testid="botao-denunciar-${versaoId}"]')`);
  assert.ok(temBotao, "Botão denunciar deve estar presente no comentário");

  await avaliar(`document.querySelector('[data-testid="botao-denunciar-${versaoId}"]').click()`);
  await esperarTexto("Denunciar comentário");
  await esperarTexto(versaoId);

  // Verifica que não há campo de justificativa livre
  const temCampoTexto = await avaliar(`!!document.querySelector('textarea, input[type="text"]')`);
  assert.equal(temCampoTexto, false, "Não deve haver campo de justificativa livre");

  // Verifica que os sete motivos estão presentes
  const totalRadios = await avaliar(`document.querySelectorAll('input[name="motivoDenuncia"]').length`);
  assert.equal(totalRadios, 7, "Devem existir exatamente os 7 motivos fechados de RF21");

  // Botão confirmar deve estar desabilitado sem seleção
  const botaoDesabilitado = await avaliar(`document.querySelector('button[type="submit"]').disabled`);
  assert.equal(botaoDesabilitado, true, "Confirmar deve estar desabilitado sem seleção");

  // Seleciona motivo SPAM
  await avaliar(`document.querySelector('#motivo-SPAM').click()`);
  assert.equal(await avaliar(`document.querySelector('button[type="submit"]').disabled`), false);

  // Submete
  await avaliar(`document.querySelector('button[type="submit"]').click()`);
  await esperarTexto("Denuncia registrada. Obrigado por contribuir.");
  assert.equal(enviosDenuncia.at(-1)?.motivo, "SPAM");
  assert.equal(enviosDenuncia.at(-1)?.id, versaoId);

  // Fecha o modal
  await avaliar(`Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === 'Fechar')?.click()`);
  await aguardar(async () => !(await texto()).includes("Denunciar comentário"), "modal fechado");

  // 3. Fluxo de duplicidade (409)
  statusDenuncia = 409;
  await avaliar(`document.querySelector('[data-testid="botao-denunciar-${versaoId}"]').click()`);
  await esperarTexto("Denunciar comentário");
  await avaliar(`document.querySelector('#motivo-OFENSA_PESSOAL').click()`);
  await avaliar(`document.querySelector('button[type="submit"]').click()`);
  await esperarTexto("Você já possui uma denúncia aberta para este comentário.");
  assert.ok(!(await texto()).includes("Denuncia registrada"));
  assert.ok(!(await texto()).includes("limiar"));
  await avaliar(`Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === 'Cancelar')?.click()`);

  // 4. Fluxo de versão indisponível (404)
  statusDenuncia = 404;
  await avaliar(`document.querySelector('[data-testid="botao-denunciar-${versaoId}"]').click()`);
  await esperarTexto("Denunciar comentário");
  await avaliar(`document.querySelector('#motivo-AMEACA').click()`);
  await avaliar(`document.querySelector('button[type="submit"]').click()`);
  await esperarTexto("Este comentário não está mais disponível para denúncia.");

  console.log("Teste de navegador de denúncias e agradecimentos aprovado com sucesso!");
} finally {
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
