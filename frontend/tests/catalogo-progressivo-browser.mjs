import assert from "node:assert/strict";

export async function verificarCatalogoProgressivo({ cdp, avaliar, aguardar }) {
  const quantidade = () => avaliar(`document.querySelectorAll('[aria-label="Disciplinas da unidade"] > li').length`);
  const links = () => avaliar(`document.querySelectorAll('nav[aria-label="Unidades acadêmicas"] a').length`);
  const clicar = seletor => avaliar(`document.querySelector(${JSON.stringify(seletor)}).click()`);
  for (const width of [320, 390, 768, 1440]) {
    await cdp("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: false });
    await cdp("Page.navigate", { url: "http://localhost:3100/departamentos" });
    try {
      await aguardar(async () => await quantidade() === 12 && await links() === 9, "catálogo inicial limitado");
    } catch (erro) {
      const estado = await avaliar('({caminho:location.pathname, disciplinas:document.querySelectorAll("#disciplinas-unidade > li").length, opcoes:document.querySelectorAll("nav[aria-label=\\"Unidades acadêmicas\\"] a").length, texto:document.body.innerText.slice(0,1200)})');
      throw new Error(`${erro.message}: ${JSON.stringify(estado)}`, { cause: erro });
    }
    assert.equal(await avaliar(`document.querySelector('nav[aria-label="Unidades acadêmicas"]').innerText.includes("Unidade Acadêmica Teste 00")`), true);
    assert.equal(await avaliar(`Array.from(document.querySelectorAll('nav[aria-label="Unidades acadêmicas"] a')).some(a => /^\\d+$/.test(a.textContent))`), false);
    await clicar('button[aria-controls="opcoes-unidades"]');
    await aguardar(async () => await links() === 13, "demais unidades disponíveis");
    await aguardar(async () => await avaliar('document.activeElement?.getAttribute("href")?.includes("5008")'), "foco na primeira unidade revelada");
    assert.equal(await avaliar('document.querySelector("button[aria-controls=opcoes-unidades]")'), null);
    await clicar('button[aria-controls="disciplinas-unidade"]');
    await aguardar(async () => await quantidade() === 24, "segundo lote sem duplicação");
    await aguardar(async () => await avaliar('document.activeElement?.closest("li")?.textContent.includes("TEST0012")'), "foco na primeira disciplina revelada");
    await clicar('button[aria-controls="disciplinas-unidade"]');
    await aguardar(async () => await quantidade() === 27, "último lote completo");
    assert.equal(await avaliar('document.querySelector("button[aria-controls=disciplinas-unidade]")'), null);
    assert.equal(await avaliar('new Set(Array.from(document.querySelectorAll("#disciplinas-unidade > li a")).map(a => a.href)).size'), 27);
    await clicar('nav a[href="/departamentos?unidade=5011"]');
    await aguardar(async () => await quantidade() === 2 && await avaliar('location.search === "?unidade=5011"'), "filtro mantém o código na URL");
    assert.equal(await avaliar('document.querySelector("#opcoes-unidades [aria-current=page]").textContent'), "Unidade Acadêmica Teste 11");
    assert.equal(await avaliar('Array.from(document.querySelectorAll("#disciplinas-unidade > li")).every(li => li.textContent.includes("Unidade Acadêmica Teste 11"))'), true);
    await avaliar("history.back()");
    await aguardar(async () => await quantidade() === 12 && await links() === 9, "mudança de filtro reinicia o limite");
    await avaliar("history.forward()");
    await aguardar(async () => await quantidade() === 2 && await avaliar('!!document.querySelector("#opcoes-unidades [aria-current=page]")'), "histórico restaura a seleção");
    await cdp("Page.reload");
    await aguardar(async () => await quantidade() === 2 && await avaliar('document.querySelector("#opcoes-unidades [aria-current=page]")?.textContent === "Unidade Acadêmica Teste 11"'), "seleção visível fora do primeiro lote após recarga");
    assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `overflow: ${width}`);
  }
  console.log("Catálogo: nomes institucionais, códigos preservados, lotes 12/24/27 sem duplicação, expansão das unidades, foco, filtro/histórico/recarga e 320/390/768/1440 px aprovados.");
}
