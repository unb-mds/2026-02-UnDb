import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
const carregar = (arquivo) => import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, arquivo)));
const { lerContextoBusca, comContextoBusca, urlBusca, ordenarResultados } = await carregar("contexto-busca.js");
const { buscarDisciplinas } = await carregar("services/disciplinas.js");
const { listarProfessores } = await carregar("services/professores.js");
const { retornoAvaliacaoSeguro } = await carregar("retorno-avaliacao.js");

test("retorno autenticado permite apenas rota da avaliação e contexto autorizado, até 2048 caracteres", () => {
  const destino = "/professores/11111111-1111-4111-8111-111111111111/disciplinas/22222222-2222-4222-8222-222222222222/avaliar";
  assert.equal(retornoAvaliacaoSeguro(destino), destino);
  for (const tipo of ["professores", "disciplinas"]) {
    for (const termo of ["", "Cálculo & Álgebra + CIC", "?next=externo/#fragmento"]) {
      const retorno = comContextoBusca(destino, { tipo, termo, ordem: "unidade" });
      assert.equal(retornoAvaliacaoSeguro(retorno), retorno);
    }
  }
  for (const valor of [
    `https://externo.test${destino}`, `//externo.test${destino}`, `${destino}/`, `${destino}\n`, `${destino}#fim`, `${destino}?`,
    `${destino}?busca=professores&q=x&ordem=nome&token=segredo`, `${destino}?busca=professores&q=x&ordem=nome&q=y`,
    `${destino}?busca=professores&q=x&ordem=recomendacao`, `${destino}?busca=outro&q=x&ordem=nome`,
    `${destino}?busca=professores&q=%00&ordem=nome`, `${destino}?busca=professores&q=%GG&ordem=nome`, `${destino}?busca=professores&q=x`,
  ]) assert.equal(retornoAvaliacaoSeguro(valor), null, valor);
  const prefixo = `${destino}?busca=professores&ordem=nome&q=`;
  assert.equal(retornoAvaliacaoSeguro(prefixo + "a".repeat(2048 - prefixo.length))?.length, 2048);
  assert.equal(retornoAvaliacaoSeguro(prefixo + "a".repeat(2049 - prefixo.length)), null);
  // Python/Pydantic contam pontos de código, inclusive fora do plano básico Unicode.
  const unicode = prefixo + "😀".repeat(2048 - prefixo.length);
  assert.equal(retornoAvaliacaoSeguro(unicode), unicode);
  assert.equal(retornoAvaliacaoSeguro(unicode + "😀"), null);
});

test("contexto preserva modalidade, termo e ordem por todas as etapas sem destino arbitrário", () => {
  for (const tipo of ["professores", "disciplinas"]) {
    const contexto = { tipo, termo: "Cálculo & Álgebra + CIC", ordem: "unidade" };
    const lista = new URL(urlBusca(contexto), "http://local");
    assert.equal(lista.pathname, `/${tipo}`);
    assert.equal(lista.searchParams.get("q"), contexto.termo);
    for (const rota of ["/professores/id", "/disciplinas/id", "/professores/id/disciplinas/d", "/professores/id/disciplinas/d/avaliar"]) {
      const url = new URL(comContextoBusca(rota, contexto), "http://local");
      assert.deepEqual(lerContextoBusca(Object.fromEntries(url.searchParams)), contexto);
      assert.equal(url.pathname, rota);
    }
  }
  assert.equal(lerContextoBusca({ busca: "https://externo.test" }), null);
  assert.equal(lerContextoBusca({ busca: ["professores", "disciplinas"] }), null);
  assert.deepEqual(lerContextoBusca({ busca: "professores", q: ["a", "b"], ordem: "invalida" }), { tipo: "professores", termo: "", ordem: "nome" });
  assert.equal(comContextoBusca("/professores/id", null), "/professores/id");
});

test("ordena o conjunto inteiro com acentos e homônimos, sem unir IDs nem modificar a resposta", () => {
  const dados = [
    { id: "4", nome: "Zélia", departamento: "Administração" },
    { id: "3", nome: "Ana", departamento: "Matemática" },
    { id: "2", nome: "Álvaro", departamento: "Computação" },
    { id: "1", nome: "Ana", departamento: "Computação" },
  ];
  assert.deepEqual(ordenarResultados(dados, "nome").map(x => x.id), ["2", "1", "3", "4"]);
  assert.deepEqual(ordenarResultados(dados, "unidade").map(x => x.id), ["4", "2", "1", "3"]);
  assert.deepEqual(dados.map(x => x.id), ["4", "3", "2", "1"]);
  const muitos = Array.from({ length: 155 }, (_, i) => ({ id: String(i), nome: `Nome ${String(154 - i).padStart(3, "0")}`, departamento: "CIC" }));
  assert.equal(ordenarResultados(muitos, "nome")[0].id, "154");
  assert.equal(ordenarResultados(muitos, "nome").at(-1).id, "0");
  assert.deepEqual(ordenarResultados([dados[1], { ...dados[1], id: "0" }], "nome").map(x => x.id), ["0", "3"]);
});

test("busca por código OU nome une listas completas por ID antes de ordenar", async (t) => {
  const chamadas = [];
  const item = (id, nome) => ({ id, nome, codigo: id, departamento: "CIC", creditos: null, identificador_externo: null });
  t.mock.method(globalThis, "fetch", async (url) => {
    chamadas.push(new URL(url));
    return Response.json(new URL(url).searchParams.has("codigo") ? [item("1", "Zoologia"), item("2", "Álgebra")] : [item("2", "Álgebra"), item("3", "Biologia")]);
  });
  const resultados = await buscarDisciplinas("CIC & teste");
  assert.equal(chamadas.length, 2);
  assert.ok(chamadas.every(url => url.pathname === "/api/disciplinas"));
  assert.equal(chamadas.find(url => url.searchParams.has("codigo")).searchParams.get("codigo"), "CIC & teste");
  assert.equal(chamadas.find(url => url.searchParams.has("nome")).searchParams.get("nome"), "CIC & teste");
  assert.deepEqual(ordenarResultados(resultados, "nome").map(x => x.id), ["2", "3", "1"]);
});

test("falha em uma consulta da união não vira lista vazia ou sucesso parcial", async (t) => {
  t.mock.method(globalThis, "fetch", async (url) => new URL(url).searchParams.has("codigo") ? Response.json([]) : Response.json({ detail: "indisponível" }, { status: 503 }));
  await assert.rejects(buscarDisciplinas("CIC"), { status: 503 });
});

test("professores usam contrato público existente, sem filtros por unidade nem paginação inventada", async (t) => {
  t.mock.method(globalThis, "fetch", async (url, init) => {
    assert.equal(new URL(url).pathname, "/api/professores");
    assert.deepEqual([...new URL(url).searchParams.entries()], [["nome", "Ána"]]);
    assert.equal(init.credentials, "include");
    return Response.json([]);
  });
  assert.deepEqual(await listarProfessores("Ána"), []);
});
