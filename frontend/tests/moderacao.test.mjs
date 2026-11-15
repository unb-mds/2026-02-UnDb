import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const carregar = (arquivo) => import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));
const servico = await carregar("services/moderacao.js");
const { acoesParaEstado, mensagemModeracao } = await carregar("moderacao.js");
const { ApiError } = await carregar("services/http-error.js");
const id = "11111111-1111-4111-8111-111111111111";
const outro = "22222222-2222-4222-8222-222222222222";
const autor = { id: outro, nome: "Nome privado", email: "privado@aluno.unb.br" };
const comentario = { id, texto: "Crítica acadêmica", estado: "PENDENTE", autor, substitui_id: null, created_at: "2026-11-01T12:00:00Z" };
const decisao = { id: outro, comentario_versao_id: id, moderador_id: outro, acao: "APROVAR", motivo: "Revisão humana", estado_anterior: "PENDENTE", estado_posterior: "PUBLICADO", created_at: comentario.created_at };

test("fila usa cookie, no-store, cancelamento e apenas o filtro de estado contratado", async (t) => {
  const controlador = new AbortController();
  const chamadas = [];
  t.mock.method(globalThis, "fetch", async (url, init) => {
    chamadas.push(new URL(url));
    assert.equal(init.credentials, "include");
    assert.equal(init.cache, "no-store");
    assert.equal(init.signal, controlador.signal);
    return Response.json([comentario]);
  });
  for (const estado of [undefined, "PENDENTE", "PUBLICADO", "SUSPENSO"]) {
    assert.deepEqual(await servico.listarFila(estado, controlador.signal), [comentario]);
  }
  assert.ok(chamadas.every((url) => url.pathname === "/api/moderacao/comentarios"));
  assert.equal(chamadas[0].search, "");
  assert.equal(chamadas[2].search, "?estado=PUBLICADO");
});

test("consulta detalhes, denúncias e decisões da versão sem misturar registros", async (t) => {
  const denuncia = { id: outro, comentario_versao_id: id, motivo: "SPAM", estado: "EM_ABERTO", created_at: comentario.created_at, denunciante: autor };
  const corpo = { autenticadas: [denuncia], visitantes: [{ ...denuncia, denunciante: null }], contas_distintas: 42, total_visitantes: 77 };
  t.mock.method(globalThis, "fetch", async (url) => Response.json(String(url).endsWith("/denuncias") ? corpo : String(url).endsWith("/decisoes") ? [decisao] : comentario));
  assert.deepEqual(await servico.consultarComentario(id), comentario);
  assert.deepEqual(await servico.consultarDecisoes(id), [decisao]);
  assert.equal((await servico.consultarDenuncias(id)).contas_distintas, 42, "não recalcula contagens do backend");
  corpo.autenticadas[0] = { ...denuncia, comentario_versao_id: outro };
  await assert.rejects(servico.consultarDenuncias(id), /outra versão/);
});

test("envia somente ação e motivo, sem identidade ou autorização fornecida pelo cliente", async (t) => {
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, `/api/moderacao/comentarios/${id}/acoes`);
    assert.equal(init.method, "POST");
    assert.equal(init.credentials, "include");
    assert.deepEqual(JSON.parse(init.body), { acao: "APROVAR", motivo: "Revisão humana" });
    return Response.json(decisao);
  });
  assert.deepEqual(await servico.executarAcao(id, { acao: "APROVAR", motivo: "  Revisão humana  ", moderador_id: "não enviar" }), decisao);
});

test("motivo vazio ou versão inválida não disparam requisição", async (t) => {
  t.mock.method(globalThis, "fetch", () => { assert.fail("não deve enviar"); });
  await assert.rejects(servico.executarAcao(id, { acao: "REJEITAR", motivo: "  " }));
  await assert.rejects(servico.consultarComentario("../../outro"));
});

test("respostas incompatíveis falham em vez de produzir fila vazia ou sucesso", async (t) => {
  let resposta = { registros: [] };
  t.mock.method(globalThis, "fetch", async () => Response.json(resposta));
  await assert.rejects(servico.listarFila());
  resposta = [{ ...comentario, estado: "INVENTADO" }];
  await assert.rejects(servico.listarFila());
  resposta = { ...decisao, comentario_versao_id: outro };
  await assert.rejects(servico.executarAcao(id, { acao: "APROVAR", motivo: "Revisão humana" }));
});

test("ações exibidas correspondem ao estado contratado, sem restauração de estados finais", () => {
  assert.deepEqual(acoesParaEstado("PENDENTE", false), ["APROVAR", "REJEITAR"]);
  assert.deepEqual(acoesParaEstado("PUBLICADO", true), ["MANTER", "REMOVER"]);
  assert.deepEqual(acoesParaEstado("PUBLICADO", false), []);
  assert.deepEqual(acoesParaEstado("SUSPENSO", true), ["RESTAURAR", "REMOVER"]);
  for (const estado of ["RETIRADO", "REMOVIDO", "REJEITADO", "SUBSTITUIDO"]) assert.deepEqual(acoesParaEstado(estado, true), []);
});

test("403 e 409 preservam status e não revelam mensagens internas", async (t) => {
  let status = 403;
  t.mock.method(globalThis, "fetch", async () => Response.json({ detail: "nome/e-mail ou detalhe interno" }, { status }));
  for (status of [401, 403, 409, 422, 503]) {
    await assert.rejects(servico.listarFila(), (erro) => {
      assert.equal(erro.status, status);
      assert.ok(!mensagemModeracao(erro, "acao").includes("detalhe interno"));
      return true;
    });
  }
  assert.match(mensagemModeracao(new ApiError("interno", 403), "acao"), /outro moderador/);
  assert.match(mensagemModeracao(new ApiError("interno", 409), "acao"), /estado.*mudou/);
  assert.match(mensagemModeracao(new TypeError("offline"), "consulta"), /conexão/);
});

test("triagem é explícita, usa apenas versão e valida categorias e vínculo", async (t) => {
  const corpo = { comentario_versao_id: id, status: "CONCLUIDA", filtro_ativo: false,
    versao_lista: "teste", versao_integracao: "teste", categorias_locais: [], categorias_ia: [], sinalizado: false, modelo: "teste" };
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, `/api/moderacao/comentarios/${id}/triagem`);
    assert.equal(init.method, "POST");
    assert.equal(init.credentials, "include");
    assert.equal(init.cache, "no-store");
    assert.deepEqual(JSON.parse(init.body), {});
    return Response.json(corpo);
  });
  assert.deepEqual(await servico.analisarComentario(id), corpo);
  corpo.categorias_ia = ["DESCONHECIDA"];
  await assert.rejects(servico.analisarComentario(id), /incompatível/);
  corpo.categorias_ia = [];
  corpo.comentario_versao_id = outro;
  await assert.rejects(servico.analisarComentario(id), /outra versão/);
});


test("histórico distingue ator sistema de moderador humano", async (t) => {
  t.mock.method(globalThis, "fetch", async () => Response.json([{ ...decisao, moderador_id: null }]));
  assert.equal((await servico.consultarDecisoes(id))[0].moderador_id, null);
});
