import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
const carregar = (arquivo) => import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));
const { interpretarRetryAfter, ApiError } = await carregar("services/http-error.js");
const { apiClient } = await carregar("services/api-client.js");
const { mensagemModeracao } = await carregar("moderacao.js");

test("Retry-After aceita segundos e data HTTP sem aceitar conteúdo livre", () => {
  const agora = Date.parse("Tue, 17 Nov 2026 12:00:00 GMT");
  assert.equal(interpretarRetryAfter("37", agora), 37);
  assert.equal(interpretarRetryAfter("Tue, 17 Nov 2026 12:00:37 GMT", agora), 37);
  assert.equal(interpretarRetryAfter("Tue, 17 Nov 2026 11:00:00 GMT", agora), 1);
  for (const valor of [null, "", "-3", "1.5", "texto interno", "Infinity", "9999999999999999999999"]) {
    assert.equal(interpretarRetryAfter(valor, agora), null);
  }
});

for (const metodo of ["request", "post", "patch"]) {
  for (const status of [429, 503]) {
    test(`${metodo} ${status} informa espera sem detalhes internos`, async (t) => {
      const corpo = { campo: "preenchimento sintético" };
      t.mock.method(globalThis, "fetch", async () => Response.json({ detail: "DETALHE_INTERNO" }, { status, headers: { "Retry-After": "37" } }));
      await assert.rejects(apiClient[metodo]("/ensaio", corpo), (erro) => {
        assert.ok(erro instanceof ApiError);
        assert.equal(erro.status, status);
        assert.equal(erro.retryAfter, 37);
        assert.equal(erro.detalhes, undefined);
        assert.match(erro.message, /Aguarde 37 segundos/);
        assert.ok(!erro.message.includes("DETALHE_INTERNO"));
        assert.equal(mensagemModeracao(erro, "acao"), erro.message);
        return true;
      });
      assert.equal(corpo.campo, "preenchimento sintético");
    });
  }
}

test("503 sem Retry-After e corpo HTML mantém orientação genérica", async (t) => {
  t.mock.method(globalThis, "fetch", async () => new Response("<html>INTERNO</html>", { status: 503 }));
  await assert.rejects(apiClient.post("/ensaio", {}), (erro) => {
    assert.equal(erro.retryAfter, null);
    assert.match(erro.message, /Tente novamente em instantes/);
    assert.ok(!erro.message.includes("INTERNO"));
    return true;
  });
});
