import { test } from "node:test";
import assert from "node:assert/strict";
import { join } from "node:path";
import { pathToFileURL } from "node:url";
const service = await import(pathToFileURL(join(process.env.AVALIACAO_TEST_BUILD, "services/identidades.js")));
const id = "11111111-1111-4111-8111-111111111111";
const item = { id, professor_id: id, nome: "Docente de teste", unidade: "524", periodo: "2027.1", disciplina: "IFD0004", turma: "01", motivo: "HOMONIMOS", estado: "PENDENTE", versao: 1, identificador_destino: null, candidatos: [{ identificador: "123", nome: "Docente de teste", perfil_url: "https://sigaa.unb.br", compativel: true }] };
test("fila de identidades usa paginação, credenciais, no-store e cancelamento", async t => {
  const c = new AbortController();
  t.mock.method(globalThis,"fetch",async (url,init) => {
    assert.equal(new URL(url).pathname,"/api/moderacao/identidades");
    assert.equal(new URL(url).searchParams.get("offset"),"50");
    assert.equal(init.cache,"no-store"); assert.equal(init.credentials,"include"); assert.equal(init.signal,c.signal);
    return Response.json([item]);
  });
  assert.deepEqual(await service.listarIdentidades("PENDENTE",50,c.signal),[item]);
});
test("decisão transmite a versão, o perfil e a justificativa sem papel fornecido pelo cliente",async t => {
  t.mock.method(globalThis,"fetch",async (url,init) => {
    assert.equal(init.method,"POST");
    assert.deepEqual(JSON.parse(init.body),{acao:"CONFIRMAR",versao:1,justificativa:"Perfil conferido",identificador:"123"});
    return Response.json({...item,estado:"CONFIRMADA",versao:2});
  });
  assert.equal((await service.decidirIdentidade(item,"CONFIRMAR","Perfil conferido","123")).estado,"CONFIRMADA");
});
test("contrato inválido não vira fila vazia nem decisão aceita",async t => {
  t.mock.method(globalThis,"fetch",async () => Response.json([{...item,candidatos:[{...item.candidatos[0],identificador:"javascript:alert(1)"}]}]));
  await assert.rejects(service.listarIdentidades("PENDENTE",0));
});
test("prévia sem união aceita as contagens nulas serializadas pela API", async t => {
  const previa = { colisoes: 0, uniao_necessaria: false, bloqueada: false, turmas: null, avaliacoes: null };
  t.mock.method(globalThis, "fetch", async () => Response.json(previa));
  assert.deepEqual(await service.consultarPrevia(id, "123"), previa);
});
test("prévia com união recusa contagens ausentes ou inválidas", async t => {
  for (const valor of [null, -1, "1", undefined]) {
    t.mock.method(globalThis, "fetch", async () => Response.json({ colisoes: 0, uniao_necessaria: true, bloqueada: false, turmas: valor, avaliacoes: 1 }));
    await assert.rejects(service.consultarPrevia(id, "123"), /Prévia incompatível/);
  }
});
test("403 e 409 preservam o status sem simular sucesso",async t => {
  for (const status of [403,409]) {
    t.mock.method(globalThis,"fetch",async () => Response.json({detail:"Solicitação recusada"},{status}));
    await assert.rejects(service.decidirIdentidade(item,"SEPARAR","Pessoas distintas"), e=>e.status===status);
  }
});
