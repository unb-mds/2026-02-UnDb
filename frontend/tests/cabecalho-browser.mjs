// Regressão #211: usa a infraestrutura de navegador existente e HTTP controlado.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { comNavegador } from "./browser-session.mjs";

let autenticado = false;
let moderador = false;
let statusSessao = 200;
let segurarProxima = false;
let respostaRetida = null;
const fixture = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Content-Type", "application/json");
  if (req.method === "OPTIONS") { res.writeHead(204).end(); return; }
  if (req.url.startsWith("/api/moderacao/comentarios")) { res.writeHead(autenticado && moderador ? 200 : 403).end(autenticado && moderador ? "[]" : "{}"); return; }
  if (req.url === "/api/auth/sessao") {
    const corpo = { autenticado };
    if (segurarProxima) {
      segurarProxima = false;
      respostaRetida = () => res.end(JSON.stringify(corpo));
      return;
    }
    res.writeHead(statusSessao).end(JSON.stringify(statusSessao === 200 ? corpo : { detail: "Indisponível" }));
    return;
  }
  if (req.url === "/api/auth/login") {
    req.resume();
    autenticado = true;
    res.end(JSON.stringify({ message: "Autenticação realizada." }));
    return;
  }
  if (req.url === "/api/auth/logout") {
    autenticado = false;
    res.end(JSON.stringify({ message: "Sessão encerrada." }));
    return;
  }
  if (req.url.startsWith("/api/professores") || req.url.startsWith("/api/disciplinas")) {
    res.end("[]"); return;
  }
  res.writeHead(401).end("{}");
});

await comNavegador({ fixture, executar: async ({ cdp, avaliar, aguardar }) => {
  const conta = 'header nav[aria-label="Conta"]';
  const texto = () => avaliar(`document.querySelector('${conta}')?.innerText ?? ''`);
  const esperar = valor => aguardar(async () => (await texto()).includes(valor), `cabeçalho: ${valor}`);
  const navegar = rota => cdp("Page.navigate", { url: `http://localhost:3100${rota}` });
  const evento = nome => avaliar(`window.dispatchEvent(new Event(${JSON.stringify(nome)}))`);
  const visitante = async () => {
    await esperar("Entrar");
    assert.equal(await avaliar(`document.querySelectorAll('${conta} a').length`), 1);
    assert.doesNotMatch(await texto(), /Minha conta/);
  };
  const conectado = async () => {
    await esperar("Minha conta");
    assert.doesNotMatch(await texto(), /Entrar|criar conta/i);
    assert.equal(await avaliar(`document.querySelector('${conta} a').getAttribute('href')`), "/login");
  };
  const neutro = async () => {
    await esperar("Verificar conta");
    assert.doesNotMatch(await texto(), /Entrar|Minha conta/);
    assert.equal(await avaliar(`document.querySelectorAll('${conta} a').length`), 1);
  };

  await navegar("/login");
  await visitante();
  await aguardar(() => avaliar("!!document.querySelector('main input[name=senha]')"), "formulário de login");
  await avaliar("document.querySelector('[name=email]').value='fixture@aluno.unb.br'; document.querySelector('[name=senha]').value='Fixture-local-211!'; document.querySelector('main form').requestSubmit()");
  await conectado();
  await avaliar(`document.querySelector('${conta} a').click()`);
  await aguardar(() => avaliar("location.pathname === '/login' && !location.search && document.querySelector('main')?.innerText.includes('Sua sessão está ativa')"), "Minha conta abre a sessão existente");
  await avaliar("Array.from(document.querySelectorAll('main button')).find(b => b.textContent === 'Sair').click()");
  await visitante();

  autenticado = true;
  await navegar("/");
  await conectado();
  await cdp("Page.reload");
  await conectado();
  await avaliar("document.querySelector('header a[href=\"/professores\"]').click()");
  await aguardar(() => avaliar("location.pathname === '/professores'"), "navegação de cliente");
  await conectado();

  autenticado = false;
  await evento("focus");
  await visitante();
  autenticado = true;
  await evento("pageshow");
  await conectado();

  // Depois de perder a sessão, não manter Minha conta enquanto a consulta aguarda.
  autenticado = false;
  segurarProxima = true;
  await evento("undb:sessao-alterada");
  await aguardar(async () => !!respostaRetida, "revalidação após logout retida");
  await aguardar(() => avaliar(`document.querySelector('${conta} [role=status]')?.textContent === 'Verificando sessão…'`), "carregamento neutro após perder a sessão");
  await neutro();
  respostaRetida();
  respostaRetida = null;
  await aguardar(() => avaliar(`!document.querySelector('${conta} [role=status]')`), "logout revalidado");
  autenticado = true;
  await evento("undb:sessao-alterada");
  await conectado();

  // Uma resposta visitante antiga não pode desfazer o login já validado.
  autenticado = false;
  segurarProxima = true;
  await evento("undb:sessao-alterada");
  await aguardar(async () => !!respostaRetida, "consulta antiga retida");
  autenticado = true;
  await evento("undb:sessao-alterada");
  await conectado();
  respostaRetida();
  respostaRetida = null;
  await new Promise(resolve => setTimeout(resolve, 250));
  await conectado();

  statusSessao = 503;
  await evento("focus");
  await aguardar(() => avaliar(`document.querySelector('${conta} [role=status]')?.textContent.includes('Não foi possível')`), "erro de sessão sem assumir visitante");
  await neutro();
  statusSessao = 200;
  await evento("focus");
  await conectado();

  // A chamada de acesso permanece clara enquanto a sessão é validada.
  segurarProxima = true;
  await navegar("/");
  await aguardar(async () => !!respostaRetida, "sessão inicial retida");
  await neutro();
  respostaRetida();
  respostaRetida = null;
  await conectado();

  for (const autenticacao of [false, true]) {
    autenticado = autenticacao;
    await evento("undb:sessao-alterada");
    if (autenticacao) await conectado(); else await visitante();
    for (const width of [320, 768, 1280]) {
      await cdp("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: false });
      if (width < 1024) {
        await avaliar("document.querySelector('header .menu-toggle').click()");
        await aguardar(() => avaliar("document.querySelector('header .menu-toggle').getAttribute('aria-expanded') === 'true'"), "menu aberto");
        assert.equal(await avaliar(`document.querySelector('${conta} a').getBoundingClientRect().height >= 44`), true, "conta acessível no menu");
      }
      for (const tema of ["light", "dark"]) {
        await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
        assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `overflow ${width}/${tema}/${autenticacao}`);
        await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
        await avaliar(`document.querySelector('${conta} a').focus()`);
        assert.equal(await avaliar("getComputedStyle(document.activeElement).outlineStyle"), "solid");
        if (process.env.PREVIEW_DIR) {
          await mkdir(process.env.PREVIEW_DIR, { recursive: true });
          const { data } = await cdp("Page.captureScreenshot", { format: "png" });
          await writeFile(join(process.env.PREVIEW_DIR, `cabecalho-${autenticacao ? "conta" : "visitante"}-${width}-${tema}.png`), Buffer.from(data, "base64"));
        }
      }
      if (width < 1024) {
        await avaliar("document.querySelector('header .menu-toggle').click()");
        await aguardar(() => avaliar("document.querySelector('header .menu-toggle').getAttribute('aria-expanded') === 'false'"), "menu fechado");
      }
    }
  }

  const linkModeracao = () => avaliar("!!document.querySelector('footer a[href=\"/moderacao\"]')");
  autenticado = true; moderador = false;
  await evento("undb:sessao-alterada");
  await conectado();
  assert.equal(await linkModeracao(), false, "Estudante não vê moderação");
  moderador = true;
  await evento("undb:sessao-alterada");
  await aguardar(linkModeracao, "Moderador vê o link após confirmação do servidor");
  autenticado = false;
  await evento("undb:sessao-alterada");
  await aguardar(async () => !(await linkModeracao()), "Logout oculta moderação");

  autenticado = false;
  const destino = "/professores/11111111-1111-4111-8111-111111111111/disciplinas/22222222-2222-4222-8222-222222222222/avaliar?busca=professores&q=LINDOMAR&ordem=nome";
  await navegar(`/login?returnTo=${encodeURIComponent(destino)}`);
  await visitante();
  assert.equal(await avaliar(`new URL(document.querySelector('${conta} a').href).searchParams.get('returnTo')`), destino);
  console.log("Cabeçalho: login/logout, recarga, navegação, foco/pageshow, resposta obsoleta, erro/recuperação, carregamento neutro, retorno à avaliação e 320/768/1280 px nos dois temas aprovados.");
} });
