// Issue #242: HTTP controlado somente no teste; nenhum dado de demonstração no produto.
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { comNavegador } from "./browser-session.mjs";

const uuid = i => `${String(i).padStart(8, "0")}-1111-4111-8111-111111111111`;
const disciplinas = [
  "Fundamentos de Sistemas Distribuídos e Aplicações Concorrentes em Ambientes Heterogêneos",
  "Cálculo 1", "Introdução à Ciência da Computação", "Álgebra Linear",
  "Probabilidade e Estatística", "Laboratório de Métodos Experimentais",
].map((nome, i) => ({ id: uuid(i + 1), codigo: `TESTE${100 + i}`, nome, departamento: "TESTE", total_avaliacoes: i === 5 ? 1 : 125 - i }));
let modo = "sucesso";
let destaquesRespondidos = 0;
const consultas = [];
const fixture = createServer((req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "http://localhost:3100");
  res.setHeader("Access-Control-Allow-Credentials", "true");
  res.setHeader("Content-Type", "application/json");
  const enviar = (valor, status = 200) => res.writeHead(status).end(JSON.stringify(valor));
  const path = new URL(req.url, "http://localhost:8000").pathname;
  consultas.push(path);
  if (path === "/api/disciplinas/destaques") {
    destaquesRespondidos += 1;
    return enviar(modo === "sucesso" ? disciplinas : modo === "vazio" ? [] : {}, modo === "erro" ? 503 : 200);
  }
  if (path === "/api/disciplinas") return enviar(disciplinas);
  if (path === "/api/auth/sessao") return enviar({ autenticado: false });
  const d = disciplinas.find(d => path === `/api/disciplinas/${d.id}/professores`);
  if (d) return enviar({ disciplina: d, professores: [
    { professor_id: uuid(10), disciplina_id: d.id, professor: { id: uuid(10), nome: "Docente com dados suficientes", departamento: "TESTE" }, disciplina: d, total_avaliacoes: 3, dados_suficientes: true, didatica: 4.2, dificuldade: "MEDIO", chamada: true, disponibiliza_material: true, qualidade_material: "BOM", recomenda: 80 },
    { professor_id: uuid(11), disciplina_id: d.id, professor: { id: uuid(11), nome: "Docente com poucos dados", departamento: "TESTE" }, disciplina: d, total_avaliacoes: 2, dados_suficientes: false },
  ].filter(p => d.total_avaliacoes > 1 || !p.dados_suficientes).map(p => d.total_avaliacoes === 1 ? { ...p, total_avaliacoes: 1 } : p) });
  return enviar({}, 404);
});

await comNavegador({ fixture, executar: async ({ cdp, avaliar, aguardar }) => {
  const seletor = '[aria-label="Disciplinas mais avaliadas"]';
  const resultados = [];
  for (const width of [320, 768, 1280]) {
    await cdp("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: false });
    for (const tema of ["light", "dark"]) {
      await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }, { name: "prefers-reduced-motion", value: "reduce" }] });
      await cdp("Page.navigate", { url: "http://localhost:3100/" });
      await aguardar(() => avaliar(`document.querySelectorAll('${seletor} > li').length === 6`), "seis destaques da API");
      await avaliar("document.fonts.ready");
      const conteudos = await avaliar(`Array.from(document.querySelectorAll('${seletor} > li')).map(li => ({ titulo: li.querySelector('h3').textContent, texto: li.textContent, href: li.querySelector('a').getAttribute('href') }))`);
      conteudos.forEach((c, i) => {
        assert.equal(c.titulo, disciplinas[i].nome);
        assert.ok(c.texto.includes(disciplinas[i].codigo));
        assert.ok(c.texto.includes(`${disciplinas[i].total_avaliacoes} ${i === 5 ? "avaliação" : "avaliações"}`));
        assert.equal(c.texto.includes("4,2/5 didática · 80% recomendam"), i !== 5);
        assert.ok(c.texto.includes("Dados insuficientes"));
        assert.equal(c.href, `/disciplinas/${disciplinas[i].id}`);
      });
      const medidas = await avaliar(`(() => { const ul = document.querySelector('${seletor}'); return { pagina: document.documentElement.scrollWidth, viewport: innerWidth, colunas: getComputedStyle(ul).gridTemplateColumns.split(' ').length, titulos: Array.from(ul.querySelectorAll('h3')).every(h => h.scrollHeight <= h.clientHeight + 1 && h.scrollWidth <= h.clientWidth + 1 && getComputedStyle(h).webkitLineClamp === 'none'), cartoes: Array.from(ul.querySelectorAll('li > a')).every(a => a.scrollWidth <= a.clientWidth + 1), altura: ul.getBoundingClientRect().height }; })()`);
      assert.ok(medidas.pagina <= width, `overflow da página em ${width}`);
      assert.ok(medidas.titulos && medidas.cartoes, `conteúdo cortado em ${width}`);
      assert.equal(medidas.colunas, width < 640 ? 1 : width < 1024 ? 2 : 3);
      await avaliar("document.querySelector('a[href=\"/disciplinas\"].link').focus()");
      await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      assert.ok(await avaliar(`document.activeElement === document.querySelector('${seletor} a') && getComputedStyle(document.activeElement).outlineStyle !== 'none'`), "primeiro cartão acessível por Tab e foco visível");
      if (process.env.PREVIEW_DIR && tema === "dark") {
        await avaliar("document.activeElement.blur(); window.scrollTo(0, 0)");
        const clip = await avaliar(`(() => { const r = document.querySelector('${seletor}').closest('section').getBoundingClientRect(); return { x: r.x + scrollX - 6, y: r.y + scrollY - 6, width: r.width + 12, height: r.height + 12, scale: 1 }; })()`);
        const foto = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip });
        await mkdir(process.env.PREVIEW_DIR, { recursive: true });
        await writeFile(join(process.env.PREVIEW_DIR, `destaques-${width}.png`), Buffer.from(foto.data, "base64"));
      }
      resultados.push({ width, tema, ...medidas });
    }
  }
  // Enter no link nativo preserva o destino de comparação.
  await avaliar(`document.querySelector('${seletor} a').focus()`);
  await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", text: "\r", windowsVirtualKeyCode: 13 });
  await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
  await aguardar(() => avaliar(`location.pathname === '/disciplinas/${disciplinas[0].id}'`), "destino por Enter");
  for (modo of ["vazio", "erro"]) {
    const antes = destaquesRespondidos;
    await cdp("Page.navigate", { url: "http://localhost:3100/" });
    await aguardar(() => avaliar("document.querySelector('#catalogo-unidades') !== null"), "home hidratada");
    await aguardar(() => Promise.resolve(destaquesRespondidos > antes), "resposta real da fixture de destaques");
    assert.equal(await avaliar(`document.querySelector('${seletor}') === null`), true);
  }
  assert.ok(consultas.includes("/api/disciplinas/destaques"));
  assert.ok(disciplinas.every(d => consultas.includes(`/api/disciplinas/${d.id}/professores`)));
  console.log(JSON.stringify({ resultados, dados: "HTTP controlado, sintético, exclusivo do teste", teclado: "Tab, foco e Enter", estados: "sucesso, vazio, erro" }));
} });
