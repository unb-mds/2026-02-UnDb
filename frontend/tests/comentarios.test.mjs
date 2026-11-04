import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const carregar = (arquivo) => import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));
const servico = await carregar("services/comentarios.js");
const { ApiError } = await carregar("services/http-error.js");

const versaoId = "11111111-1111-4111-8111-111111111111";
const outraVersao = "22222222-2222-4222-8222-222222222222";
const avaliacaoId = "33333333-3333-4333-8333-333333333333";
const outraAvaliacao = "44444444-4444-4444-8444-444444444444";

const comentarioPublicado = {
  id: versaoId,
  texto: "Didática excelente e aulas práticas.",
  created_at: "2026-11-01T10:00:00Z",
  updated_at: "2026-11-01T10:00:00Z",
  estado: "PUBLICADO",
  avaliacao_id: avaliacaoId,
  substitui_id: null,
};

const comentarioDescartado = {
  ...comentarioPublicado,
  id: outraVersao,
  texto: null,
  estado: "RETIRADO",
  avaliacao_id: outraAvaliacao,
};

const substitutoPendente = {
  ...comentarioPublicado,
  id: outraVersao,
  texto: "Revisado: didática excelente e aulas práticas.",
  estado: "PENDENTE",
  avaliacao_id: avaliacaoId,
};

test("consulta GET /api/comentarios/meu com cookie e mapeia versões do autor", async (t) => {
  const respostas = [comentarioPublicado, comentarioDescartado, substitutoPendente];
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, "/api/comentarios/meu");
    assert.equal(init.credentials, "include");
    return Response.json(respostas);
  });

  const resultado = await servico.consultarMeusComentarios();
  assert.deepEqual(resultado, respostas);
  // Texto nulo após descarte é preservado; substituto pendente distingue versão publicada.
  assert.equal(resultado[1].texto, null);
  assert.equal(resultado[1].estado, "RETIRADO");
  assert.equal(resultado[2].estado, "PENDENTE");
  assert.equal(resultado[2].texto, "Revisado: didática excelente e aulas práticas.");
});

test("texto nulo, estado e IDs são validados contra o contrato antes de retornar", async (t) => {
  const invalidos = [
    { ...comentarioPublicado, estado: "INVENTADO" },
    { ...comentarioPublicado, id: "uuid-invalido" },
    { ...comentarioPublicado, avaliacao_id: "uuid-invalido" },
    { ...comentarioPublicado, substitui_id: "uuid-invalido" },
    { ...comentarioPublicado, texto: 123 },
    { ...comentarioPublicado, estado: undefined },
    { ...comentarioPublicado, created_at: undefined },
  ];
  for (const corpo of invalidos) {
    t.mock.method(globalThis, "fetch", async () => Response.json([corpo]));
    await assert.rejects(servico.consultarMeusComentarios(), /incompatível/);
  }
});

test("resposta que não é array falha em vez de produzir lista vazia", async (t) => {
  for (const corpo of [null, { comentarios: [] }, ""]) {
    t.mock.method(globalThis, "fetch", async () => Response.json(corpo));
    await assert.rejects(servico.consultarMeusComentarios(), /incompatível/);
  }
});

test("401 e 404 do serviço de comentários do autor propagam o status", async (t) => {
  for (const status of [401, 404]) {
    t.mock.method(
      globalThis,
      "fetch",
      async () => Response.json({ detail: "Sessão inválida ou expirada." }, { status }),
    );
    await assert.rejects(servico.consultarMeusComentarios(), (erro) => {
      assert.ok(erro instanceof ApiError);
      assert.equal(erro.status, status);
      return true;
    });
  }
});

test("falha de rede não é sucesso e explica que a consulta não foi confirmada", async (t) => {
  t.mock.method(globalThis, "fetch", async () => {
    throw new TypeError("Failed to fetch");
  });
  await assert.rejects(servico.consultarMeusComentarios(), (erro) => {
    assert.ok(erro instanceof TypeError);
    return true;
  });
});
