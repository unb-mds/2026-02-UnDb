import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const carregar = (arquivo) =>
  import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));

const servicoDenuncias = await carregar("services/denuncias.js");
const servicoComentarios = await carregar("services/comentarios.js");
const tiposDenuncia = await carregar("types/denuncia.js");

const versaoId = "11111111-1111-4111-8111-111111111111";
const professorId = "22222222-2222-4222-8222-222222222222";
const disciplinaId = "33333333-3333-4333-8333-333333333333";
const mensagemId = "44444444-4444-4444-8444-444444444444";

test("aceita exatamente os sete motivos fechados de RF21", () => {
  const motivosEsperados = [
    "OFENSA_PESSOAL",
    "XINGAMENTO",
    "PALAVRAO",
    "AMEACA",
    "DISCRIMINACAO",
    "EXPOSICAO_DADOS_PESSOAIS",
    "SPAM",
  ];
  assert.deepEqual([...tiposDenuncia.motivosDenuncia], motivosEsperados);
  for (const motivo of motivosEsperados) {
    assert.ok(tiposDenuncia.ROTULOS_MOTIVOS_DENUNCIA[motivo], `rótulo para ${motivo} deve existir`);
  }
});

test("envia POST /api/comentarios/{versao_id}/denuncias com cookie e somente motivo", async (t) => {
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, `/api/comentarios/${versaoId}/denuncias`);
    assert.equal(init.method, "POST");
    assert.equal(init.credentials, "include");
    assert.deepEqual(JSON.parse(init.body), { motivo: "SPAM" });
    return Response.json(
      { mensagem: "Denuncia registrada. Obrigado por contribuir." },
      { status: 201 },
    );
  });

  const resposta = await servicoDenuncias.registrarDenuncia(versaoId, {
    motivo: "SPAM",
    campoExtra: "ignorado",
  });
  assert.equal(resposta.mensagem, "Denuncia registrada. Obrigado por contribuir.");
});

test("motivo inválido ou versão com UUID inválido não disparam requisição", async (t) => {
  t.mock.method(globalThis, "fetch", () => {
    assert.fail("não deve realizar fetch com parâmetros inválidos");
  });

  await assert.rejects(
    servicoDenuncias.registrarDenuncia(versaoId, { motivo: "MOTIVO_INEXISTENTE" }),
    /Motivo de denúncia inválido/,
  );
  await assert.rejects(
    servicoDenuncias.registrarDenuncia("uuid-invalido", { motivo: "SPAM" }),
    /Identificador de versão inválido/,
  );
});

test("preserva status HTTP 404, 409 e 422 na denúncia", async (t) => {
  for (const status of [404, 409, 422]) {
    t.mock.method(globalThis, "fetch", async () =>
      Response.json({ detail: `erro de teste ${status}` }, { status }),
    );

    await assert.rejects(
      servicoDenuncias.registrarDenuncia(versaoId, { motivo: "PALAVRAO" }),
      (erro) => {
        assert.equal(erro.status, status);
        return true;
      },
    );
  }
});

test("respostas incompatíveis de denúncia falham em vez de produzir sucesso", async (t) => {
  t.mock.method(globalThis, "fetch", async () =>
    Response.json({ respostaInvalida: true }, { status: 201 }),
  );

  await assert.rejects(
    servicoDenuncias.registrarDenuncia(versaoId, { motivo: "XINGAMENTO" }),
    /Resposta de denúncia incompatível/,
  );
});

test("listarAgradecimentos consulta GET /api/agradecimentos com credentials e no-store", async (t) => {
  const mensagensMock = [
    { id: mensagemId, mensagem: "Obrigado por contribuir com a moderacao do conteudo." },
  ];

  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, "/api/agradecimentos");
    assert.equal(init.credentials, "include");
    assert.equal(init.cache, "no-store");
    return Response.json(mensagensMock);
  });

  const resultado = await servicoDenuncias.listarAgradecimentos();
  assert.deepEqual(resultado, mensagensMock);
});

test("listarAgradecimentos retorna array vazio em 401 (visitante não autenticado)", async (t) => {
  t.mock.method(globalThis, "fetch", async () =>
    Response.json({ detail: "Não autenticado" }, { status: 401 }),
  );

  const resultado = await servicoDenuncias.listarAgradecimentos();
  assert.deepEqual(resultado, []);
});

test("confirmarAgradecimentoExibido envia POST /api/agradecimentos/{id}/exibido e trata 204", async (t) => {
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, `/api/agradecimentos/${mensagemId}/exibido`);
    assert.equal(init.method, "POST");
    assert.equal(init.credentials, "include");
    return new Response(null, { status: 204 });
  });

  await servicoDenuncias.confirmarAgradecimentoExibido(mensagemId);
});

test("confirmarAgradecimentoExibido rejeita mensagemId com UUID inválido antes do fetch", async (t) => {
  t.mock.method(globalThis, "fetch", () => {
    assert.fail("não deve realizar fetch com id inválido");
  });

  await assert.rejects(
    servicoDenuncias.confirmarAgradecimentoExibido("id-invalido"),
    /Identificador de mensagem inválido/,
  );
});

test("listarComentariosPublicados consulta GET /api/professores/{id}/disciplinas/{id}/comentarios", async (t) => {
  const comentariosMock = [
    {
      id: versaoId,
      texto: "Excelente didática e aulas práticas.",
      created_at: "2026-11-01T10:00:00Z",
    },
  ];

  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(
      new URL(url).pathname,
      `/api/professores/${professorId}/disciplinas/${disciplinaId}/comentarios`,
    );
    assert.equal(init.credentials, "include");
    return Response.json(comentariosMock);
  });

  const resultado = await servicoComentarios.listarComentariosPublicados(
    professorId,
    disciplinaId,
  );
  assert.deepEqual(resultado, comentariosMock);
});

test("listarComentariosPublicados rejeita IDs inválidos antes de requisitar", async (t) => {
  t.mock.method(globalThis, "fetch", () => {
    assert.fail("não deve requisitar");
  });

  await assert.rejects(
    servicoComentarios.listarComentariosPublicados("invalido", disciplinaId),
    /Identificadores inválidos/,
  );
});
