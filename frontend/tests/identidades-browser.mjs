// RF23: contrato real da prévia e decisões que terminam após trocar a seleção.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { comNavegador } from "./browser-session.mjs";

const uuid = i => `${String(i).padStart(8, "0")}-1111-4111-8111-111111111111`;
const criar = (i, nome) => ({
  id: uuid(i), professor_id: uuid(i + 10), nome, unidade: "524", periodo: "2027.1",
  disciplina: "IFD0004", turma: "01", motivo: "HOMONIMOS", estado: "PENDENTE",
  versao: 1, identificador_destino: null,
  candidatos: [{ identificador: String(i), nome, perfil_url: "https://sigaa.unb.br", compativel: true }],
});
let itens = [criar(1, "Docente Alfa"), criar(2, "Docente Beta")];
let acesso = 200;
let liberar = null;
let envio = null;
const fixture = createServer(async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Access-Control-Allow-Methods", "GET,POST,OPTIONS");
  res.setHeader("Content-Type", "application/json");
  const responder = (status, valor) => res.writeHead(status).end(JSON.stringify(valor));
  if (req.method === "OPTIONS") { responder(204); return; }
  const url = new URL(req.url, "http://localhost:8000");
  if (url.pathname === "/api/auth/sessao") { responder(200, { autenticado: true }); return; }
  if (url.pathname === "/api/agradecimentos") { responder(200, []); return; }
  if (acesso !== 200) { responder(acesso, { detail: "Permissão necessária." }); return; }
  if (url.pathname === "/api/moderacao/identidades") {
    responder(200, itens.filter(i => i.estado === url.searchParams.get("estado"))); return;
  }
  const match = url.pathname.match(/^\/api\/moderacao\/identidades\/([^/]+)\/(previa|decisoes)$/);
  if (!match) { responder(404, {}); return; }
  const item = itens.find(i => i.id === match[1]);
  if (!item) { responder(404, {}); return; }
  if (match[2] === "previa") {
    // PreviaResponse serializa campos opcionais como null.
    responder(200, { colisoes: 0, uniao_necessaria: false, bloqueada: false, turmas: null, avaliacoes: null }); return;
  }
  if (req.method === "GET") { responder(200, []); return; }
  let corpo = "";
  for await (const parte of req) corpo += parte;
  envio = JSON.parse(corpo);
  item.estado = "CONFIRMADA";
  item.versao += 1;
  item.identificador_destino = envio.identificador;
  liberar = () => responder(200, item);
});

await comNavegador({ fixture, executar: async ({ cdp, avaliar, aguardar }) => {
  const texto = () => avaliar("document.body?.innerText ?? ''");
  const esperar = valor => aguardar(async () => (await texto()).includes(valor), valor);
  const clicar = valor => avaliar(`Array.from(document.querySelectorAll('button')).find(b => b.textContent.trim() === ${JSON.stringify(valor)})?.click()`);
  const selecionar = nome => avaliar(`Array.from(document.querySelectorAll('li button')).find(b => b.textContent.startsWith(${JSON.stringify(nome)}))?.click()`);
  await cdp("Page.navigate", { url: "http://localhost:3100/moderacao/identidades" });
  await esperar("Docente Alfa");
  await selecionar("Docente Alfa");
  await esperar("Histórico de decisões");
  await avaliar("document.querySelector('input[type=radio]').click()");
  await esperar("Não há união com outro registro neste momento.");
  await avaliar(`const campo = document.querySelector('textarea'); Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set.call(campo, 'Perfil conferido'); campo.dispatchEvent(new Event('input', { bubbles: true }));`);
  await aguardar(() => avaliar("!Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Confirmar associação').disabled"), "confirmação habilitada");
  await clicar("Confirmar associação");
  await aguardar(async () => envio !== null, "envio da decisão");
  assert.deepEqual(envio, { acao: "CONFIRMAR", versao: 1, justificativa: "Perfil conferido", identificador: "1" });

  // Trocar a fila desmonta o formulário anterior enquanto o POST ainda responde.
  await clicar("Atualizar fila");
  await esperar("Docente Beta");
  await selecionar("Docente Beta");
  await esperar("Histórico de decisões");
  liberar();
  await new Promise(resolve => setTimeout(resolve, 500));
  assert.equal(await avaliar("document.querySelector('section h2')?.textContent"), "Docente Beta", "resposta antiga não deve limpar a seleção atual");
  assert.doesNotMatch(await texto(), /Associação confirmada e aguardando/);

  for (const tema of ["light", "dark"]) {
    await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
    for (const largura of [320, 768, 1280]) {
      await cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: false });
      assert.ok(await avaliar("document.documentElement.scrollWidth <= innerWidth"), `sem overflow: ${tema}/${largura}`);
    }
  }
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
  assert.ok(await avaliar("document.activeElement !== document.body"), "teclado alcança os controles");
  acesso = 403;
  await clicar("Atualizar fila");
  await esperar("permissão específica de identidades");
  assert.doesNotMatch(await texto(), /Docente Alfa|Docente Beta|Histórico de decisões/);
  console.log("Identidades: prévia nula, POST obsoleto, permissão, teclado e 320/768/1280 nos dois temas aprovados.");
} });
