import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
const carregar = (arquivo) => import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));
const { criteriosAvaliacao, criarEntradaAvaliacao, mensagemErroAvaliacao } = await carregar("avaliacao-formulario.js");
const { enviarAvaliacao } = await carregar("services/avaliacoes.js");
const { consultarSessao } = await carregar("services/auth.js");
const { ApiError } = await carregar("services/http-error.js");

function formulario(alteracoes = {}) {
  const dados = new FormData();
  for (const [campo, valor] of Object.entries({ didatica: "3", dificuldade: "MEDIO", chamada: "false", material: "NAO_DISPONIBILIZA", recomenda: "false", ...alteracoes })) {
    dados.set(campo, valor);
  }
  return dados;
}

test("oferece exatamente as cinco escalas individuais da #38", () => {
  assert.deepEqual(criteriosAvaliacao.map(({ rotulo, opcoes }) => [rotulo, opcoes.map(([, texto]) => texto)]), [
    ["Didática", ["1", "2", "3", "4", "5"]],
    ["Dificuldade", ["Fácil", "Médio", "Difícil"]],
    ["Chamada", ["Sim", "Não"]],
    ["Material", ["Não disponibiliza", "Ruim", "Médio", "Bom"]],
    ["Recomenda a matéria", ["Sim", "Não"]],
  ]);
});

test("não transforma respostas Não em true nem envia identidade ou comentário", () => {
  assert.deepEqual(criarEntradaAvaliacao(formulario(), "professor", "disciplina"), {
    professor_id: "professor", disciplina_id: "disciplina", didatica: 3,
    dificuldade: "MEDIO", chamada: false, recomenda: false,
    disponibiliza_material: false, qualidade_material: null,
  });
});

test("converte todas as combinações válidas para o schema individual", () => {
  for (const didatica of ["1", "2", "3", "4", "5"]) {
    for (const dificuldade of ["FACIL", "MEDIO", "DIFICIL"]) {
      for (const material of ["NAO_DISPONIBILIZA", "RUIM", "MEDIO", "BOM"]) {
        for (const chamada of ["true", "false"]) {
          for (const recomenda of ["true", "false"]) {
            const entrada = criarEntradaAvaliacao(formulario({ didatica, dificuldade, material, chamada, recomenda }), "p", "d");
            assert.equal(entrada.didatica, Number(didatica));
            assert.equal(entrada.dificuldade, dificuldade);
            assert.equal(entrada.chamada, chamada === "true");
            assert.equal(entrada.recomenda, recomenda === "true");
            assert.equal(entrada.disponibiliza_material, material !== "NAO_DISPONIBILIZA");
            assert.equal(entrada.qualidade_material, material === "NAO_DISPONIBILIZA" ? null : material);
          }
        }
      }
    }
  }
});

test("rejeita campos vazios, ausentes ou fora das escalas sem presumir valores", () => {
  for (const { nome } of criteriosAvaliacao) {
    for (const valor of ["", "CONFLITANTE", "invalido"]) {
      assert.throws(() => criarEntradaAvaliacao(formulario({ [nome]: valor }), "p", "d"), /Selecione uma opção válida/);
    }
    const dados = formulario();
    dados.delete(nome);
    assert.throws(() => criarEntradaAvaliacao(dados, "p", "d"));
  }
  for (const didatica of ["0", "6", "1.5", "03"]) {
    assert.throws(() => criarEntradaAvaliacao(formulario({ didatica }), "p", "d"));
  }
});

for (const status of [200, 201]) {
  test(`envia POST /api/avaliacoes com cookie e JSON; aguarda confirmação HTTP ${status}`, async (t) => {
    const entrada = criarEntradaAvaliacao(formulario(), "p", "d");
    const chamadas = [];
    t.mock.method(globalThis, "fetch", async (url, init) => {
      chamadas.push({ url, init });
      return Response.json({}, { status });
    });
    assert.equal(await enviarAvaliacao(entrada), undefined);
    assert.equal(chamadas.length, 1);
    assert.equal(new URL(chamadas[0].url).pathname, "/api/avaliacoes");
    assert.equal(chamadas[0].init.method, "POST");
    assert.equal(chamadas[0].init.credentials, "include");
    assert.equal(chamadas[0].init.headers["Content-Type"], "application/json");
    assert.deepEqual(JSON.parse(chamadas[0].init.body), entrada);
  });
}

test("consulta a sessão existente com credenciais do navegador", async (t) => {
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, "/api/auth/sessao");
    assert.equal(init.credentials, "include");
    return Response.json({ autenticado: false });
  });
  assert.deepEqual(await consultarSessao(), { autenticado: false });
});

for (const [status, detalhe, orientacao] of [
  [401, "Sessão inválida ou expirada.", /Entre na sua conta/],
  [403, "Confirme seu e-mail antes de avaliar.", /link recebido/],
  [404, "Not Found", /ainda não está disponível/],
  [404, "Professor não encontrado.", /localizar o destino/],
  [405, "Method Not Allowed", /ainda não está disponível/],
  [409, "Conflito ao registrar avaliação.", /rejeitada/],
  [429, "Tente novamente depois.", /Aguarde/],
  [503, "Serviço temporariamente indisponível.", /não conseguiu confirmar/],
]) {
  test(`preserva detalhe HTTP ${status} e fornece orientação`, async (t) => {
    t.mock.method(globalThis, "fetch", async () => Response.json({ detail: detalhe }, { status }));
    await assert.rejects(enviarAvaliacao(criarEntradaAvaliacao(formulario(), "p", "d")), (erro) => {
      assert.equal(erro.status, status);
      assert.match(mensagemErroAvaliacao(erro), orientacao);
      assert.ok(mensagemErroAvaliacao(erro).includes(detalhe));
      return true;
    });
  });
}

test("preserva detalhes de validação Pydantic 422 com nomes compreensíveis", async (t) => {
  const detalhes = [
    { loc: ["body", "didatica"], msg: "Input should be less than or equal to 5" },
    { loc: ["body", "qualidade_material"], msg: "Qualidade obrigatória" },
  ];
  t.mock.method(globalThis, "fetch", async () => Response.json({ detail: detalhes }, { status: 422 }));
  await assert.rejects(enviarAvaliacao(criarEntradaAvaliacao(formulario(), "p", "d")), (erro) => {
    assert.deepEqual(erro.detalhes, detalhes);
    assert.match(mensagemErroAvaliacao(erro), /Didática, Material/);
    for (const { msg } of detalhes) assert.ok(mensagemErroAvaliacao(erro).includes(msg));
    return true;
  });
});

test("trata 422 sem lista e resposta de erro não JSON", async (t) => {
  assert.match(mensagemErroAvaliacao(new ApiError("Entrada inválida", 422)), /Entrada inválida/);
  t.mock.method(globalThis, "fetch", async () => new Response("indisponível", { status: 502 }));
  await assert.rejects(enviarAvaliacao(criarEntradaAvaliacao(formulario(), "p", "d")), (erro) => {
    assert.equal(erro.status, 502);
    assert.match(mensagemErroAvaliacao(erro), /não conseguiu confirmar/);
    return true;
  });
});

test("falha de rede não é sucesso e explica que o envio não foi confirmado", async (t) => {
  t.mock.method(globalThis, "fetch", async () => { throw new TypeError("Failed to fetch"); });
  await assert.rejects(enviarAvaliacao(criarEntradaAvaliacao(formulario(), "p", "d")), (erro) => {
    assert.match(mensagemErroAvaliacao(erro), /Verifique sua conexão/);
    return true;
  });
});
