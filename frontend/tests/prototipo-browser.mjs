import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

// Reutiliza o navegador e o ciclo de vida do runner existente, sem novo framework.
export async function verificarPrototipo({ cdp, avaliar, aguardar, aguardarTexto, socket }) {
  const requisicoesApi = [];
  const observar = ({ data }) => {
    const evento = JSON.parse(data);
    if (evento.method === "Network.requestWillBeSent" && new URL(evento.params.request.url).pathname.startsWith("/api/")) {
      requisicoesApi.push(evento.params.request.url);
    }
  };
  socket.addEventListener("message", observar);
  const navegar = async (query, titulo) => {
    await cdp("Page.navigate", { url: `http://localhost:3100/prototipo${query ? `?${query}` : ""}` });
    await aguardarTexto(titulo);
  };
  const clicar = async (trecho) => {
    await avaliar(`Array.from(document.querySelectorAll('main a')).find(a => a.textContent.includes(${JSON.stringify(trecho)})).click()`);
  };
  const buscar = async (termo) => {
    await avaliar(`document.querySelector('[name=q]').value=${JSON.stringify(termo)}; document.querySelector('form').requestSubmit()`);
    await aguardarTexto("Resultados da busca");
  };
  const capturar = async (nome) => {
    if (!process.env.PREVIEW_DIR) return;
    await mkdir(process.env.PREVIEW_DIR, { recursive: true });
    const { data } = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
    await writeFile(join(process.env.PREVIEW_DIR, `${nome}.png`), Buffer.from(data, "base64"));
  };
  try {
    await cdp("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
    await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: "light" }] });
    await cdp("Page.navigate", { url: "http://localhost:3100" });
    await aguardarTexto("Experimentar o protótipo");
    await clicar("Experimentar o protótipo");
    await aguardarTexto("Escolha sua próxima disciplina");
    await capturar("01-entrada");
    await clicar("Buscar disciplina");
    await aguardarTexto("O que você quer encontrar?");
    await capturar("02-busca");
    await buscar("");
    await aguardarTexto("Informe sua busca");
    await clicar("Alterar busca");
    await aguardarTexto("O que você quer encontrar?");
    await buscar("inexistente");
    await aguardarTexto("Nenhum resultado encontrado");
    await clicar("Alterar busca");
    await aguardarTexto("O que você quer encontrar?");
    await buscar("ALGORÍTMOS");
    await aguardarTexto("1 resultado(s)");
    await capturar("03-resultados");
    await clicar("Algoritmos (exemplo)");
    await aguardarTexto("Comparação de professores");
    assert.deepEqual(await avaliar("Array.from(document.querySelectorAll('main ul > li h3')).map(h => h.textContent)"), ["Bruno (exemplo)", "Ana (exemplo)", "Carla (exemplo)", "Daniel (exemplo)"]);
    await avaliar("history.back()");
    await aguardarTexto("Resultados da busca");
    await avaliar("history.forward()");
    await aguardarTexto("Comparação de professores");
    await cdp("Page.reload");
    await aguardarTexto("Comparação de professores");
    await clicar("Ordenar por recomendação");
    await aguardarTexto("Recomendação decrescente");
    const cartoes = await avaliar("Array.from(document.querySelectorAll('main ul > li')).map(li => li.innerText)");
    assert.equal(cartoes.length, 4);
    assert.match(cartoes[0], /Ana.*4 avaliações/s);
    assert.match(cartoes[0], /75%/);
    assert.match(cartoes[1], /Bruno.*Conflitante/s);
    for (const [indice, quantidade] of [[2, 2], [3, 0]]) {
      assert.match(cartoes[indice], new RegExp(`${quantidade} avaliações`));
      assert.doesNotMatch(cartoes[indice], /Didática|Dificuldade|Chamada|Recomenda a matéria|\d+%/);
    }
    await capturar("04-comparacao");
    await clicar("Avaliar Ana");
    await aguardarTexto("Conferir prévia da avaliação");
    await aguardar(async () => await avaliar('document.querySelectorAll("select").length === 5'), "cinco critérios");
    assert.deepEqual(await avaliar("Array.from(document.querySelectorAll('select')).map(s => Array.from(s.options).slice(1).map(o => o.textContent))"), [
      ["1", "2", "3", "4", "5"], ["Fácil", "Médio", "Difícil"], ["Sim", "Não"], ["Não disponibiliza", "Ruim", "Médio", "Bom"], ["Sim", "Não"],
    ]);
    assert.equal(await avaliar("document.querySelector('form').checkValidity()"), false);
    assert.equal(await avaliar("!!document.querySelector('textarea')"), false);
    await capturar("05-avaliacao");
    await avaliar("document.querySelector('select').focus()");
    await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    assert.equal(await avaliar("document.activeElement.name"), "dificuldade");
    assert.equal(await avaliar("getComputedStyle(document.activeElement).outlineStyle"), "solid");
    await avaliar("Array.from(document.querySelectorAll('select')).forEach(s => { s.value=s.options[1].value; s.dispatchEvent(new Event('change',{bubbles:true})); }); document.querySelector('form').requestSubmit()");
    await aguardarTexto("Prévia conferida.");
    assert.equal(await avaliar("document.querySelector('[name=didatica]').value"), "1");
    await clicar("Voltar à comparação");
    await aguardarTexto("Comparação de professores");
    await clicar("Avaliar Carla");
    await aguardarTexto("Conferir prévia da avaliação");
    assert.match(await avaliar("document.querySelector('main').innerText"), /Carla \(exemplo\)/);
    await navegar("etapa=busca&tipo=professor", "O que você quer encontrar?");
    await buscar("an");
    await aguardarTexto("2 resultado(s)");
    await clicar("Ana (exemplo)");
    await aguardarTexto("Disciplinas de Ana");
    await clicar("Algoritmos (exemplo)");
    await aguardarTexto("Comparação de professores");
    await navegar("etapa=busca", "O que você quer encontrar?");
    await buscar("mat-demo");
    await aguardarTexto("1 resultado(s)");
    await clicar("Cálculo (exemplo)");
    await aguardarTexto("Não há dados suficientes para comparar");
    await clicar("Avaliar Elisa");
    await aguardarTexto("Conferir prévia da avaliação");
    for (const [estado, mensagem] of [["carregando", "Buscando…"], ["erro", "Não foi possível buscar agora"]]) {
      await navegar(`etapa=resultados&tipo=disciplina&q=algoritmos&estado=${estado}`, mensagem);
    }
    await clicar("Tentar novamente");
    await aguardarTexto("1 resultado(s)");
    await navegar("etapa=comparacao&disciplina=invalida", "Escolha uma disciplina nos resultados");
    await navegar("etapa=avaliacao&disciplina=calculo-demo&professor=ana-demo", "Escolha um professor na comparação");
    const telas = [
      ["", "Escolha sua próxima disciplina"],
      ["etapa=busca", "O que você quer encontrar?"],
      ["etapa=resultados&q=algoritmos", "1 resultado(s)"],
      ["etapa=comparacao&disciplina=algoritmos-demo&ordem=recomendacao", "Recomendação decrescente"],
      ["etapa=avaliacao&disciplina=algoritmos-demo&professor=ana-demo", "Conferir prévia da avaliação"],
      ["etapa=resultados", "Informe sua busca"],
      ["etapa=resultados&q=inexistente", "Nenhum resultado encontrado"],
      ["etapa=resultados&estado=erro", "Não foi possível buscar agora"],
      ["etapa=comparacao&disciplina=calculo-demo", "Não há dados suficientes para comparar"],
    ];
    for (const tema of ["light", "dark"]) {
      await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
      for (const largura of [320, 768, 1280]) {
        await cdp("Emulation.setDeviceMetricsOverride", { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura === 320 });
        for (const [query, titulo] of telas) {
          await navegar(query, titulo);
          assert.equal(await avaliar("document.querySelectorAll('h1').length"), 1);
          assert.equal(await avaliar("document.documentElement.scrollWidth <= window.innerWidth"), true, `${tema}/${largura}/${query}`);
          assert.equal(await avaliar("!!document.querySelector('[aria-current=step]')"), true);
          assert.match(await avaliar("document.querySelector('aside').innerText"), /Dados demonstrativos fictícios/);
        }
        if (tema === "dark" && largura === 320) {
          await navegar(telas[3][0], telas[3][1]);
          await capturar("06-comparacao-mobile-escuro");
        }
      }
    }
    assert.deepEqual(requisicoesApi, [], "O protótipo não consulta nem envia dados à API");
    console.log("Protótipo #152: duas jornadas completas, escalas, vazio, conflito, insuficiência, erro/recuperação, teclado, zero chamadas à API e 54 combinações de tela/tema/largura.");
  } finally {
    socket.removeEventListener("message", observar);
  }
}
