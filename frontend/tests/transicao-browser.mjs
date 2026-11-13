// Transições progressivas: navegação real do Next, HTTP controlado e movimento reduzido.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { comNavegador } from "./browser-session.mjs";

const fixture = createServer((req, res) => {
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  if (req.url === "/api/auth/sessao") return res.end(JSON.stringify({ autenticado: false }));
  if (req.url.startsWith("/api/moderacao")) return res.writeHead(401).end("{}");
  res.end("[]");
});

await comNavegador({ fixture, executar: async ({ cdp, avaliar, aguardar }) => {
  await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "no-preference" }] });
  await cdp("Page.navigate", { url: "http://localhost:3100/" });
  await aguardar(() => avaliar("!!document.querySelector('#entrada-termo') && Object.keys(document.querySelector('main form')).some(k => k.startsWith('__reactProps'))"), "busca hidratada");
  await avaliar("window.documentoDaBusca = true; document.querySelector('.segmented input[value=professores]').click(); document.querySelector('#entrada-termo').value = 'Clara'; document.querySelector('main form').requestSubmit()");
  await aguardar(() => avaliar("location.pathname === '/professores' && document.querySelector('#conteudo').getAnimations().some(a => a.playState === 'running')"), "chegada animada aos resultados");
  assert.equal(await avaliar("window.documentoDaBusca"), true, "navegação sem recarregar o documento");
  assert.equal(await avaliar("new URL(location.href).searchParams.get('q')"), "Clara");
  await aguardar(() => avaliar("document.querySelector('#conteudo').getAnimations().length === 0"), "transição concluída");
  assert.equal(await avaliar("getComputedStyle(document.querySelector('#conteudo')).opacity"), "1");
  await aguardar(() => avaliar("document.querySelectorAll('main h1').length === 1"), "conteúdo dos resultados carregado");

  await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-reduced-motion", value: "reduce" }] });
  await avaliar("document.querySelector('header a[aria-label=\"UnDb — início\"]').click()");
  await aguardar(() => avaliar("location.pathname === '/' && !!document.querySelector('#entrada-termo')"), "retorno à home");
  assert.equal(await avaliar("document.querySelector('#conteudo').getAnimations().length"), 0, "sem animação com movimento reduzido");
  assert.equal(await avaliar("getComputedStyle(document.querySelector('.segmented'), '::before').transitionDuration"), "0s");
  console.log("Transições: busca preservada, navegação sem recarga, entrada concluída e movimento reduzido aprovados.");
} });
