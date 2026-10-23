import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

// Reutiliza o navegador e o ciclo de vida do runner existente, sem novo framework.
export async function verificarPrototipo({ cdp, avaliar, aguardar, aguardarTexto, aguardarValidacaoLocal, socket }) {
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
    await aguardarTexto("Encontre professores e disciplinas");
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
      ["1", "2", "3", "4", "5"], ["Fácil", "Médio", "Difícil"], ["Faz chamada", "Não faz chamada"], ["Não disponibiliza", "Ruim", "Médio", "Bom"], ["Recomenda a matéria", "Não recomenda a matéria"],
    ]);
    assert.equal(await avaliar("document.querySelector('form').checkValidity()"), false);
    assert.equal(await avaliar("!!document.querySelector('textarea')"), false);
    await capturar("05-avaliacao");
    await aguardarValidacaoLocal("Selecione uma opção válida para Didática.");
    await avaliar("document.querySelector('select').focus()");
    await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
    assert.equal(await avaliar("document.activeElement.name"), "dificuldade");
    assert.equal(await avaliar("getComputedStyle(document.activeElement).outlineStyle"), "solid");
    assert.match(await avaliar("getComputedStyle(document.activeElement).boxShadow"), /2px/);
    assert.equal(await avaliar("getComputedStyle(document.activeElement).getPropertyValue('--tw-ring-color').trim() === getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), true);
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
    await aguardarTexto("3 resultado(s)");
    await clicar("Ana (exemplo)");
    await aguardarTexto("Disciplinas de Ana");
    await clicar("Comparar professores");
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
    // Relatos #148: contexto, homônimos e acesso direto sem exigir comparação.
    await navegar("etapa=busca&tipo=professor&q=Ana&ordemBusca=departamento", "O que você quer encontrar?");
    assert.equal(await avaliar("document.querySelector('[name=q]').value"), "Ana");
    assert.equal(await avaliar("document.querySelector('[name=ordemBusca]').value"), "departamento");
    await buscar("Ana");
    await aguardarTexto("2 resultado(s)");
    const grupos = await avaliar("Array.from(document.querySelector('[aria-label=\"Lista de resultados\"]').children).map(li => ({texto:li.innerText, destinos:Array.from(li.querySelectorAll('a')).map(a => a.href)}))");
    assert.equal(grupos.length, 2);
    assert.match(grupos[0].texto, /Computação.*Algoritmos.*Estruturas de dados/s);
    assert.match(grupos[1].texto, /Matemática.*Cálculo/s);
    assert.equal(grupos[0].destinos.some(url => new URL(url).searchParams.get("professor") === "ana-matematica-demo"), false);
    assert.equal(grupos[1].destinos.some(url => new URL(url).searchParams.get("professor") === "ana-demo"), false);
    await aguardarTexto("Há professores com o mesmo nome");
    await avaliar("document.querySelector('a[aria-label=\"Avaliar Ana (exemplo) em Estruturas de dados (exemplo) — Computação (exemplo)\"]').click()");
    await aguardarTexto("Conferir prévia da avaliação");
    assert.match(await avaliar("document.querySelector('[aria-label=\"Destino da avaliação\"]').innerText"), /Computação.*Estruturas de dados.*Código da disciplina.*Ana/s);
    assert.equal(await avaliar("new URL(location.href).searchParams.get('q')"), "Ana");
    await cdp("Page.reload");
    await aguardarTexto("Conferir prévia da avaliação");
    await clicar("Entrar ou criar conta para avaliar");
    await aguardarTexto("Minha conta");
    await aguardar(async () => {
      await avaliar("document.querySelector('[aria-controls=senha-demo]').click()");
      return await avaliar("document.querySelector('#senha-demo').type === 'text'");
    }, "mostrar senha após hidratação");
    assert.equal(await avaliar("document.querySelector('[aria-controls=senha-demo]').getAttribute('aria-pressed')"), "true");
    await avaliar("document.querySelector('#senha-demo').value='senha-ficticia'; document.querySelector('[aria-controls=senha-demo]').click()");
    assert.equal(await avaliar("document.querySelector('#senha-demo').type"), "password");
    assert.equal(await avaliar("document.querySelector('#senha-demo').value"), "senha-ficticia");
    assert.equal(await avaliar("document.querySelector('main form')"), null, "Acesso demonstrativo não permite envio nativo, inclusive antes da hidratação");
    await capturar("07-acesso");
    await avaliar("document.querySelector('[name=email-demo]').value='exemplo@aluno.unb.br'; Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Simular entrada').click()");
    await aguardarTexto("Conferir prévia da avaliação");
    assert.equal(await avaliar("document.querySelector('[aria-label=\"Conta do protótipo\"]').textContent"), "Minha conta");
    assert.equal(await avaliar("document.querySelectorAll('header').length"), 1);
    assert.equal(await avaliar("document.querySelector('header a[href=\"/login\"]')"), null);
    await avaliar("document.querySelector('[aria-label=\"Conta do protótipo\"]').click()");
    await aguardarTexto("Seu acesso");
    await capturar("11-conta-confirmada");
    await avaliar("Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Sair da conta demonstrativa').click()");
    await aguardarTexto("Você saiu da conta demonstrativa");
    assert.equal(await avaliar("document.querySelector('[aria-label=\"Conta do protótipo\"]').textContent"), "Entrar / Criar conta");
    await avaliar("Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Criar conta').click()");
    await aguardar(async () => await avaliar("!!document.querySelector('[name=nome-demo]')"), "campos do cadastro demonstrativo");
    await avaliar("document.querySelector('[name=nome-demo]').value='Estudante exemplo'; document.querySelector('[name=email-demo]').value='exemplo@aluno.unb.br'; document.querySelector('#senha-demo').value='senha-ficticia'; Array.from(document.querySelectorAll('button')).find(b => b.textContent === 'Simular criação de conta').click()");
    await aguardarTexto("Ainda não confirmado");
    assert.equal(await avaliar("new URL(location.href).searchParams.get('etapa')"), "acesso");
    await capturar("12-conta-pendente");
    await avaliar("Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Simular confirmação do e-mail')).click()");
    await aguardarTexto("Conferir prévia da avaliação");
    assert.match(await avaliar("document.querySelector('[aria-label=\"Destino da avaliação\"]').innerText"), /Estruturas de dados/);
    await clicar("Voltar às disciplinas do professor");
    await aguardarTexto("Disciplinas de Ana");
    await clicar("Voltar aos resultados da pesquisa");
    await aguardarTexto("2 resultado(s)");
    await clicar("Alterar busca");
    await aguardarTexto("O que você quer encontrar?");
    assert.equal(await avaliar("document.querySelector('[name=q]').value"), "Ana");
    assert.equal(await avaliar("document.querySelector('[name=ordemBusca]').value"), "departamento");
    await buscar("Ana");
    await aguardarTexto("2 resultado(s)");
    assert.equal(await avaliar("document.querySelector('[aria-label=\"Conta do protótipo\"]').textContent"), "Minha conta", "Busca interna preserva o cenário de conta");
    await clicar("Alterar busca");
    await aguardarTexto("O que você quer encontrar?");
    await cdp("Page.reload");
    await aguardarTexto("O que você quer encontrar?");
    assert.equal(await avaliar("document.querySelector('[name=q]').value"), "Ana");
    assert.equal(await avaliar("document.querySelector('[aria-label=\"Conta do protótipo\"]').textContent"), "Entrar / Criar conta", "Recarregar reinicia a simulação");
    const telas = [
      ["", "Encontre professores e disciplinas"],
      ["etapa=busca", "O que você quer encontrar?"],
      ["etapa=resultados&q=algoritmos", "1 resultado(s)"],
      ["etapa=comparacao&disciplina=algoritmos-demo&ordem=recomendacao", "Recomendação decrescente"],
      ["etapa=avaliacao&disciplina=algoritmos-demo&professor=ana-demo", "Conferir prévia da avaliação"],
      ["etapa=resultados&tipo=professor&q=Ana", "2 resultado(s)"],
      ["etapa=acesso&disciplina=estruturas-demo&professor=ana-demo", "Minha conta"],
      ["etapa=acesso", "Entre na sua conta"],
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
          assert.equal(await avaliar("Array.from(document.querySelectorAll('main a')).every(a => !a.pathname.startsWith('/prototipo') || Array.from(new URL(a.href).searchParams.values()).every(v => v !== ''))"), true, `Parâmetros vazios: ${query}`);
          if (query === "etapa=resultados&tipo=professor&q=Ana" && tema === "light") {
            if (largura === 1280) await capturar("08-professores-agrupados");
            if (largura === 320) await capturar("09-professores-mobile");
          }
          if (query.startsWith("etapa=acesso") && tema === "dark" && largura === 320) {
            await capturar("10-acesso-mobile-escuro");
          }
          if (query.startsWith("etapa=avaliacao")) {
            await avaliar("document.querySelector('select').focus()");
            await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
            await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
            assert.equal(await avaliar("document.activeElement.name"), "dificuldade");
            assert.match(await avaliar("getComputedStyle(document.activeElement).boxShadow"), /2px/);
            assert.equal(await avaliar("getComputedStyle(document.activeElement).getPropertyValue('--tw-ring-color').trim() === getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()"), true);
          }
        }
        if (tema === "dark" && largura === 320) {
          await navegar(telas[3][0], telas[3][1]);
          await capturar("06-comparacao-mobile-escuro");
        }
      }
    }
    assert.deepEqual(requisicoesApi, [], "O protótipo não consulta nem envia dados à API");
    console.log("Protótipo #153: jornadas, acesso direto, homônimos, contexto e histórico, senha demonstrativa, escalas, estados, teclado, zero chamadas à API e 72 combinações de tela/tema/largura; conta visitante/pendente/confirmada, saída e retorno à avaliação.");
  } finally {
    socket.removeEventListener("message", observar);
  }
}
