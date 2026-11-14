// #237: apresentação sobre os contratos existentes, usando o driver CDP do projeto.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { comNavegador } from "./browser-session.mjs";

const antes = process.env.UI237_ANTES === "1";
const professor = "11111111-1111-4111-8111-111111111111";
const disciplina = "22222222-2222-4222-8222-222222222222";
const caminho = `/professores/${professor}/disciplinas/${disciplina}/avaliar`;
let autenticado = true, confirmado = true, statusSessao = 200, statusComentarios = 200;
let reterSessao = false;
const retidas = [], escritas = [];
const fixture = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Content-Type", "application/json");
  if (req.method === "OPTIONS") { res.writeHead(204).end(); return; }
  const url = new URL(req.url, "http://localhost:8000");
  const responder = (status, corpo) => { if (!res.destroyed) res.writeHead(status).end(JSON.stringify(corpo)); };
  if (url.pathname === "/api/auth/sessao") {
    const corpo = { autenticado };
    const responderSessao = () => responder(statusSessao, statusSessao === 200 ? corpo : { detail: "Indisponível" });
    if (reterSessao) retidas.push(responderSessao); else responderSessao();
  } else if (url.pathname === "/api/auth/logout") {
    autenticado = false; responder(200, { message: "Sessão encerrada." });
  } else if (url.pathname === "/api/auth/login") {
    req.resume(); autenticado = true; confirmado = true;
    responder(200, { message: "Autenticação realizada com sucesso." });
  } else if (url.pathname === "/api/comentarios/meu") {
    responder(!autenticado ? 401 : !confirmado ? 403 : statusComentarios, []);
  } else if (url.pathname === "/api/agradecimentos") {
    responder(200, []);
  } else if (url.pathname === "/api/avaliacoes") {
    let corpo = ""; for await (const parte of req) corpo += parte;
    const status = !autenticado ? 401 : !confirmado ? 403 : 200;
    escritas.push({ status, corpo: JSON.parse(corpo) });
    responder(status, status === 200
      ? { id: "33333333-3333-4333-8333-333333333333", comentario_erro: null }
      : { detail: "Confirme seu e-mail antes de avaliar." });
  } else if (url.pathname === `/api/professores/${professor}/disciplinas/${disciplina}`) {
    responder(200, {
      professor_id: professor, disciplina_id: disciplina, total_avaliacoes: 0, dados_suficientes: false,
      professor: { id: professor, nome: "Professor de teste — dados sintéticos", departamento: "CIC" },
      disciplina: { id: disciplina, nome: "Disciplina de teste", codigo: "CIC0001", departamento: "CIC" },
    });
  } else if (url.pathname.startsWith("/api/professores") || url.pathname.startsWith("/api/disciplinas")) {
    responder(200, []);
  } else { responder(404, {}); }
});

await comNavegador({ fixture, diretorioFrontend: process.env.UI237_FRONTEND, executar: async ({ cdp, avaliar, aguardar }) => {
  const texto = () => avaliar("document.querySelector('main')?.innerText ?? ''");
  const esperar = trecho => aguardar(async () => (await texto()).includes(trecho), trecho);
  const navegar = async rota => {
    await cdp("Page.navigate", { url: `http://localhost:3100${rota}` });
    await aguardar(() => avaliar(`location.pathname === ${JSON.stringify(rota.split("?")[0])} && !!document.querySelector('main')`), rota);
  };
  const clicar = rotulo => avaliar(`Array.from(document.querySelectorAll('main button')).find(b => b.textContent.trim() === ${JSON.stringify(rotulo)})?.click()`);
  const evento = () => avaliar("window.dispatchEvent(new Event('focus'))");
  const capturar = async (nome, largura) => {
    if (!antes) assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `${nome}: sem transbordamento horizontal em ${largura}px`);
    if (!process.env.UI237_CAPTURAS) return;
    // A captura de página completa também deve aguardar imagens abaixo da dobra.
    await avaliar("document.querySelectorAll('img').forEach(img => { img.loading = 'eager'; })");
    await aguardar(() => avaliar("Array.from(document.images).every(img => img.complete && img.naturalWidth > 0)"), "imagens da captura");
    await avaliar("document.fonts.ready.then(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))))");
    const pasta = join(process.env.UI237_CAPTURAS, antes ? "antes" : "depois");
    await mkdir(pasta, { recursive: true });
    const { data } = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
    await writeFile(join(pasta, `${nome}-${largura}.png`), Buffer.from(data, "base64"));
  };
  const semConvites = async () => {
    assert.equal(await avaliar("document.querySelector('main nav[aria-label=\"Opções de acesso\"]') === null"), true);
    assert.doesNotMatch(await texto(), /Ainda não possui conta/);
    assert.equal(await avaliar("document.querySelector('main form') === null"), true);
  };
  const aviso = () => avaliar("document.querySelector('[data-testid=acesso-avaliacao]')?.innerText ?? ''");
  const acesso = trecho => aguardar(async () => (await aviso()).includes(trecho), `acesso: ${trecho}`);

  await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "no-preference" }] });
  for (const largura of [1440, 768, 390, 320]) {
    await cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura < 768 });
    autenticado = true; confirmado = true;
    await navegar("/login"); await esperar("Sua sessão está ativa neste navegador.");
    if (!antes) {
      assert.equal(await avaliar("document.querySelector('main h1').textContent"), "Minha conta");
      await semConvites();
    }
    await capturar("minha-conta", largura);
    await navegar("/cadastro"); await esperar("Use entre 8 e 128 caracteres.");
    if (!antes) {
      assert.match(await texto(), /Crie uma senha exclusiva para o UnDb/);
      assert.deepEqual(await avaliar("[document.querySelector('main [name=senha]').minLength, document.querySelector('main [name=senha]').maxLength, document.querySelector('main [name=senha]').getAttribute('pattern')]"), [8, 128, null]);
      assert.match(await avaliar("document.getElementById(document.querySelector('main [name=senha]').getAttribute('aria-describedby')).textContent"), /UnB\/SIGAA/);
    }
    await capturar("senha-cadastro", largura);
    for (const [estado, conectado, email, mensagem] of [
      ["visitante", false, false, "Entre na sua conta"],
      ["pendente", true, false, "precisa confirmar seu e-mail"],
      ["confirmado", true, true, "Já pode enviar sua avaliação"],
    ]) {
      autenticado = conectado; confirmado = email;
      await navegar(caminho);
      if (antes) await esperar("Você pode entrar antes de preencher"); else await acesso(mensagem);
      await aguardar(() => avaliar("!!document.querySelector('main [name=didatica]')"), "critérios");
      if (!antes) {
        assert.equal(await avaliar("document.querySelectorAll('main canvas').length"), 0);
        assert.equal(await avaliar("document.querySelectorAll('[data-testid=acesso-avaliacao] a').length"), estado === "visitante" ? 1 : 0);
        assert.equal(await avaliar("document.querySelector('[name=didatica]:checked')"), null);
        assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true);
        await cdp("Input.dispatchMouseEvent", { type: "mouseMoved", x: 160, y: 180 });
        assert.equal(await avaliar("document.querySelectorAll('main canvas').length"), 0);
      }
      await capturar(`avaliacao-${estado}`, largura);
    }
  }
  if (antes) { console.log("#237: versão anterior capturada; sem alegar aprovação das correções."); return; }

  autenticado = true;
  reterSessao = true;
  await navegar("/login"); await esperar("Verificando sessão…"); await semConvites();
  assert.doesNotMatch(await texto(), /Sua sessão está ativa/);
  reterSessao = false; retidas.splice(0).forEach(liberar => liberar());
  await esperar("Sua sessão está ativa");
  await clicar("Sair");
  await aguardar(() => avaliar("!!document.querySelector('main form') && document.querySelector('main h1').textContent === 'Entrar'"), "acesso após logout");
  await avaliar("document.querySelector('main [name=email]').value='fixture237@aluno.unb.br';document.querySelector('main [name=senha]').value='Fixture-exclusiva-237!';document.querySelector('main button[aria-controls]').focus()");
  await evento();
  await aguardar(() => avaliar("document.querySelector('main h1').textContent === 'Entrar'"), "visitante revalidado");
  assert.equal(await avaliar("document.querySelector('main [name=senha]').value"), "Fixture-exclusiva-237!");
  assert.equal(await avaliar("document.activeElement === document.querySelector('main button[aria-controls]')"), true);
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", text: "\r", windowsVirtualKeyCode: 13 });
  await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
  await aguardar(() => avaliar("document.querySelector('main [name=senha]').type === 'text'"), "senha por teclado após revalidação");
  autenticado = true; await navegar("/login"); await esperar("Sua sessão está ativa");
  autenticado = false; await evento(); await aguardar(() => avaliar("document.querySelector('main h1').textContent === 'Entrar'"), "expiração");

  statusSessao = 503; await navegar("/login"); await esperar("Isso não significa que você saiu da conta."); await semConvites();
  statusSessao = 200; autenticado = true; await clicar("Verificar sessão novamente"); await esperar("Sua sessão está ativa");
  reterSessao = true; await navegar(caminho); await acesso("Verificando seu acesso");
  assert.equal(await avaliar("document.querySelectorAll('[data-testid=acesso-avaliacao] a').length"), 0);
  reterSessao = false; retidas.splice(0).forEach(liberar => liberar()); await acesso("Já pode enviar");
  statusSessao = 503; await evento(); await acesso("Isso não significa que você saiu da conta");
  assert.equal(await avaliar("document.querySelectorAll('[data-testid=acesso-avaliacao] a').length"), 0);
  statusSessao = 200; statusComentarios = 503; await clicar("Verificar acesso novamente"); await acesso("Isso não significa que você saiu da conta");
  statusComentarios = 200; confirmado = false; await clicar("Verificar acesso novamente"); await acesso("precisa confirmar");
  confirmado = true; await clicar("Já confirmei, verificar novamente"); await acesso("Já pode enviar");

  const preencher = () => avaliar("document.querySelector('main [name=didatica][value=\"5\"]').click(); Object.entries({dificuldade:'MEDIO',chamada:'false',material:'BOM',recomenda:'true'}).forEach(([nome,valor])=>document.querySelector('main [name='+nome+'][value=\"'+valor+'\"]').click())");
  const enviar = () => avaliar("document.querySelector('main button[type=submit]').click()");
  autenticado = false; await evento(); await acesso("Entre na sua conta"); await preencher(); await enviar();
  await aguardar(() => avaliar("document.querySelector('main [role=alert]')?.textContent.includes('Entre na sua conta')"), "envio exige sessão");
  assert.equal(escritas.length, 0);
  autenticado = true; confirmado = false; await evento(); await acesso("precisa confirmar"); await enviar(); await esperar("link recebido");
  assert.equal(escritas.at(-1).status, 403); assert.doesNotMatch(await texto(), /Avaliação registrada com sucesso/);
  confirmado = true; await evento(); await acesso("Já pode enviar"); await enviar(); await esperar("Avaliação registrada com sucesso");
  assert.equal(escritas.at(-1).status, 200);

  autenticado = false;
  await navegar(`/login?returnTo=${encodeURIComponent(caminho)}`);
  await aguardar(() => avaliar("!!document.querySelector('main [name=senha]')"), "login com retorno");
  await avaliar("document.querySelector('main [name=email]').value='fixture237@aluno.unb.br';document.querySelector('main [name=senha]').value='Fixture-exclusiva-237!';document.querySelector('main form').requestSubmit()");
  await aguardar(() => avaliar(`location.pathname === ${JSON.stringify(caminho)}`), "retorno à avaliação"); await acesso("Já pode enviar");
  await navegar("/login"); await esperar("Sua sessão está ativa");
  assert.equal(await avaliar("document.querySelectorAll('main .liquid-blob').length"), 5);
  assert.notEqual(await avaliar("getComputedStyle(document.querySelector('main .liquid-blob')).animationName"), "none");
  await navegar("/");
  await aguardar(() => avaliar("!!document.querySelector('main .hero-wind canvas')"), "fundo interativo da home preservado");
  console.log("#237: conta ativa/logout/expiração, cinco estados de acesso, senha exclusiva, retorno e autorização, avaliação estática e fundos das demais páginas aprovados em HTTP controlado.");
} });
