import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const carregar = (arquivo) => import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));
const servico = await carregar("services/comentarios.js");
const { ApiError } = await carregar("services/http-error.js");
const apresentacao = await carregar("apresentacao-comentario.js");

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

test("AC20-03: a consulta pública retorna apenas os campos do comentário publicado", async (t) => {
  const publico = {
    id: versaoId,
    texto: comentarioPublicado.texto,
    created_at: comentarioPublicado.created_at,
  };
  t.mock.method(globalThis, "fetch", async () => Response.json([{
    ...comentarioPublicado,
    nome_autor: "Identidade interna",
    email: "privado@example.test",
    didatica: 5,
  }]));

  assert.deepEqual(await servico.listarComentariosPublicados(avaliacaoId, outraAvaliacao), [publico]);
});

test("AC20-03: a consulta pública rejeita uma lista com comentário sem texto", async (t) => {
  t.mock.method(globalThis, "fetch", async () => Response.json([
    comentarioPublicado,
    { ...comentarioPublicado, id: outraVersao, texto: null },
  ]));

  await assert.rejects(
    servico.listarComentariosPublicados(avaliacaoId, outraAvaliacao),
    /Resposta de comentários incompatível/,
  );
});

test("consulta GET /api/comentarios/meu com cookie e mapeia versões do autor", async (t) => {
  const respostas = [comentarioPublicado, comentarioDescartado, substitutoPendente];
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, "/api/comentarios/meu");
    assert.equal(init.credentials, "include");
    assert.equal(init.cache, "no-store");
    assert.ok(init.signal);
    return Response.json(respostas);
  });

  const resultado = await servico.consultarMeusComentarios(new AbortController().signal);
  assert.deepEqual(resultado, respostas);
  // Texto nulo após descarte é preservado; substituto pendente distingue versão publicada.
  assert.equal(resultado[1].texto, null);
  assert.equal(resultado[1].estado, "RETIRADO");
  assert.equal(resultado[2].estado, "PENDENTE");
  assert.equal(resultado[2].texto, "Revisado: didática excelente e aulas práticas.");
});

test("respostas do autor são reduzidas aos campos privados autorizados", async (t) => {
  t.mock.method(globalThis, "fetch", async () => Response.json([{
    ...comentarioPublicado,
    nome_autor: "Pessoa não autorizada",
    email: "privado@example.test",
    usuario_id: "55555555-5555-4555-8555-555555555555",
  }]));

  const [comentario] = await servico.consultarMeusComentarios();
  assert.deepEqual(comentario, comentarioPublicado);
  assert.equal("nome_autor" in comentario, false);
  assert.equal("email" in comentario, false);
  assert.equal("usuario_id" in comentario, false);
});

test("respostas públicas retêm somente os campos permitidos pelo contrato", async (t) => {
  t.mock.method(globalThis, "fetch", async () => Response.json([{
    id: versaoId,
    texto: "Comentário público.",
    created_at: "2026-11-01T10:00:00Z",
    email: "privado@example.test",
    usuario_id: "55555555-5555-4555-8555-555555555555",
  }]));

  const [comentario] = await servico.listarComentariosPublicados(avaliacaoId, outraAvaliacao);
  assert.deepEqual(comentario, {
    id: versaoId,
    texto: "Comentário público.",
    created_at: "2026-11-01T10:00:00Z",
  });
  assert.equal("email" in comentario, false);
  assert.equal("usuario_id" in comentario, false);
});

test("apresentação cobre os estados RF20 sem publicar versões pendentes", () => {
  const esperado = {
    PENDENTE: "Em análise",
    PUBLICADO: "Publicado",
    SUSPENSO: "Temporariamente indisponível",
    REMOVIDO: "Removido",
    RETIRADO: "Retirado",
    SUBSTITUIDO: "Substituído",
    REJEITADO: "Rejeitado",
  };
  for (const [estado, rotulo] of Object.entries(esperado)) {
    const comentario = { ...comentarioPublicado, estado };
    assert.equal(apresentacao.rotulosEstadoComentario[estado], rotulo);
    const descricao = apresentacao.descricaoEstadoComentario(comentario);
    if (estado === "PUBLICADO") {
      assert.match(descricao, /visível publicamente/);
    } else {
      assert.match(descricao, /não .*visível|ainda não.*público/);
    }
  }

  assert.match(
    apresentacao.descricaoEstadoComentario({ ...substitutoPendente, substitui_id: versaoId }),
    /substituto aguarda aprovação/,
  );
  assert.equal(
    apresentacao.textoExibivelComentario(comentarioDescartado),
    "O texto desta versão não está mais disponível.",
  );
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
  for (const status of [401, 403, 404]) {
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

test("consulta privada envia apenas o contexto da tela, com cancelamento e sem cache", async (t) => {
  const signal = new AbortController().signal;
  t.mock.method(globalThis, "fetch", async (url, init) => {
    const query = new URL(url).searchParams;
    assert.equal(query.get("professor_id"), avaliacaoId);
    assert.equal(query.get("disciplina_id"), outraAvaliacao);
    assert.equal(query.size, 2);
    assert.equal(init.cache, "no-store");
    assert.equal(init.signal, signal);
    return Response.json([]);
  });
  assert.deepEqual(await servico.consultarMeusComentarios(signal, {professorId:avaliacaoId,disciplinaId:outraAvaliacao}), []);
  await assert.rejects(servico.consultarMeusComentarios(signal, {professorId:"invalido",disciplinaId:outraAvaliacao}));
});

test("retirada é PATCH sem critérios, valida confirmação e remove campos extras", async (t) => {
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, `/api/comentarios/${versaoId}/retirar`);
    assert.equal(init.method, "PATCH");
    assert.equal(init.body, undefined);
    assert.equal(init.credentials, "include");
    return Response.json({...comentarioPublicado,estado:"RETIRADO",email:"privado"});
  });
  const retirada = await servico.retirarComentario(versaoId);
  assert.equal(retirada.estado,"RETIRADO");
  assert.equal("email" in retirada,false);
});

test("retirada rejeita confirmação errada, estado incompatível e falha HTTP", async (t) => {
  for (const resposta of [{...comentarioPublicado,estado:"PUBLICADO"},{...comentarioPublicado,id:outraVersao,estado:"RETIRADO"}]) {
    t.mock.method(globalThis,"fetch", async()=>Response.json(resposta));
    await assert.rejects(servico.retirarComentario(versaoId), /incompatível/);
  }
  for (const status of [401,403,404,503]) {
    t.mock.method(globalThis,"fetch",async()=>Response.json({}, {status}));
    await assert.rejects(servico.retirarComentario(versaoId), e=>e.status===status);
  }
});

test("envio de comentário preserva critérios e diferencia texto recusado de falha no envio", async (t) => {
  const {enviarAvaliacaoComComentario} = await carregar("services/avaliacoes.js");
  const entrada = {professor_id:avaliacaoId,disciplina_id:outraAvaliacao,didatica:4,dificuldade:"MEDIO",chamada:false,disponibiliza_material:false,qualidade_material:null,recomenda:true,comentario:"   "};
  t.mock.method(globalThis,"fetch",async(url,init)=>{
    assert.equal(new URL(url).pathname,"/api/avaliacoes");
    assert.deepEqual(JSON.parse(init.body),entrada);
    return Response.json({id:avaliacaoId,comentario_erro:"texto inválido",usuario_id:"privado"});
  });
  assert.deepEqual(await enviarAvaliacaoComComentario(entrada),{id:avaliacaoId,comentario_erro:"texto inválido"});
  t.mock.method(globalThis,"fetch",async()=>Response.json({}));
  await assert.rejects(enviarAvaliacaoComComentario(entrada),/incompatível/);
});

const votos = await carregar("services/votos-comentario.js");
test("#278: consulta privada, troca/retirada e resposta minimizada", async (t) => {
  const chamadas = [];
  t.mock.method(globalThis, "fetch", async (url, opcoes) => {
    chamadas.push({ url, opcoes });
    return new Response(JSON.stringify({ uteis: 2, nao_uteis: 1, meu_voto: "UTIL", usuario_id: "nao-repassar" }), { status: 200 });
  });
  assert.deepEqual(await votos.consultarUtilidade(versaoId), { uteis: 2, nao_uteis: 1, meu_voto: "UTIL" });
  for (const voto of ["UTIL", "NAO_UTIL", null]) await votos.definirVoto(versaoId, voto);
  assert.equal(chamadas[0].opcoes.cache, "no-store");
  for (const chamada of chamadas) assert.equal(chamada.opcoes.credentials, "include");
  assert.deepEqual(chamadas.slice(1).map(c => JSON.parse(c.opcoes.body)), [{ voto: "UTIL" }, { voto: "NAO_UTIL" }, { voto: null }]);
  await assert.rejects(votos.definirVoto("invalido", "UTIL"));
});

test("#278: rejeita contagens/estado inválidos e propaga erros HTTP", async (t) => {
  for (const dados of [{ uteis: -1, nao_uteis: 0, meu_voto: null }, { uteis: 0, nao_uteis: 1.5, meu_voto: null }, { uteis: 0, nao_uteis: 0, meu_voto: "outro" }, null]) {
    t.mock.method(globalThis, "fetch", async () => new Response(JSON.stringify(dados)));
    await assert.rejects(votos.consultarUtilidade(versaoId), /inválida/);
    t.mock.restoreAll();
  }
  for (const status of [401, 403, 404, 503]) {
    t.mock.method(globalThis, "fetch", async () => new Response(JSON.stringify({ detail: "Falha" }), { status }));
    await assert.rejects(votos.definirVoto(versaoId, "UTIL"), e => e instanceof ApiError && e.status === status);
    t.mock.restoreAll();
  }
});
