// #266: cabeçalhos e metadados de páginas sensíveis, somente API/dados sintéticos.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { comNavegador } from "./browser-session.mjs";

const fixture = createServer((req, res) => {
  res.setHeader("Content-Type", "application/json");
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.writeHead(204).end();
  if (req.url === "/api/auth/sessao") return res.end(JSON.stringify({ autenticado: false }));
  if (req.url === "/api/auth/confirmar") return res.end(JSON.stringify({ message: "E-mail confirmado." }));
  return res.end("[]");
});

await comNavegador({ fixture, executar: async ({ cdp, avaliar, aguardar }) => {
  for (const caminho of ["/confirmar-email", "/redefinir-senha"]) {
    const resposta = await fetch(`http://localhost:3100${caminho}?token=${"x".repeat(43)}`);
    assert.equal(resposta.status, 200);
    assert.equal(resposta.headers.get("referrer-policy"), "no-referrer");
    assert.ok(resposta.headers.get("cache-control")?.includes("no-store"));
    await cdp("Page.navigate", { url: `http://localhost:3100${caminho}?token=${"x".repeat(43)}` });
    await aguardar(async () => await avaliar('document.querySelector("meta[name=referrer]")?.content === "no-referrer"'));
    assert.equal(await avaliar('document.querySelector("meta[name=robots]")?.content.includes("noindex")'), true);
  }
  console.log("#266: confirmação e recuperação com no-store, no-referrer e noindex aprovadas.");
}});
