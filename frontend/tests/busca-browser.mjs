import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";

// Cenário isolado do runner já existente. Dados controlados só no processo de teste.
export function criarCenarioBusca(professor, disciplina) {
  let ativo = false;
  let falhar = false;
  let sessao = false;
  let consultas = 0;
  let logins = 0;
  let lentasConcluidas = 0;
  const professores = [
    { ...professor, id: "33333333-3333-4333-8333-333333333333", nome: "Zélia Teste", departamento: "Administração" },
    { ...professor, nome: "Álvaro Teste", departamento: "Matemática" },
    { ...professor, id: "44444444-4444-4444-8444-444444444444", nome: "Ana Teste", departamento: "Computação" },
  ];
  const disciplinas = [
    { ...disciplina, nome: "Zoologia Teste", departamento: "Administração" },
    { ...disciplina, id: "55555555-5555-4555-8555-555555555555", nome: "Álgebra Teste", departamento: "Matemática" },
    { ...disciplina, id: "66666666-6666-4666-8666-666666666666", nome: "Biologia Teste", departamento: "Computação" },
  ];
  const agregado = {
    professor_id: professor.id, disciplina_id: disciplina.id,
    professor, disciplina, total_avaliacoes: 0, dados_suficientes: false,
  };

  async function responder(req, res) {
    if (!ativo) return false;
    const url = new URL(req.url, "http://localhost");
    const enviar = (dados, status = 200) => res.writeHead(status).end(JSON.stringify(dados));
    if (url.pathname === "/api/professores" || url.pathname === "/api/disciplinas") {
      consultas += 1;
      const termo = url.searchParams.get("nome") ?? url.searchParams.get("codigo");
      if (termo === "lenta") {
        await new Promise(resolve => setTimeout(resolve, 900));
        lentasConcluidas += 1;
      }
      if (falhar) enviar({ detail: "Falha controlada" }, 503);
      else if (termo === "vazio") enviar([]);
      else if (url.pathname === "/api/professores") enviar(termo === "nova" || termo === "lenta" ? [{ ...professor, nome: termo }] : professores);
      else enviar(url.searchParams.has("codigo") ? disciplinas.slice(0, 2) : disciplinas.slice(1));
    } else if (url.pathname === `/api/professores/${professor.id}`) enviar(professor);
    else if (url.pathname === `/api/professores/${professor.id}/disciplinas`) enviar([disciplina]);
    else if (/^\/api\/professores\/[^/]+\/disciplinas$/.test(url.pathname)) enviar([]);
    else if (url.pathname === `/api/professores/${professor.id}/disciplinas/${disciplina.id}`) enviar(agregado);
    else if (url.pathname === `/api/disciplinas/${disciplina.id}`) enviar(disciplina);
    else if (url.pathname === `/api/disciplinas/${disciplina.id}/turmas`) enviar([]);
    else if (url.pathname === `/api/disciplinas/${disciplina.id}/professores`) {
      assert.equal(url.searchParams.get("ordenar_por"), "recomendacao");
      enviar({ disciplina, professores: [agregado] });
    } else if (url.pathname === "/api/auth/sessao") enviar({ autenticado: sessao });
    else if (url.pathname === "/api/auth/login") { logins += 1; sessao = true; enviar({ message: "Sessão iniciada." }); }
    else if (url.pathname === "/api/auth/cadastro") enviar({ message: "Confira o link de confirmação." }, 202);
    else return false;
    return true;
  }

  async function verificar({ cdp, avaliar, aguardar, aguardarTexto }) {
    ativo = true;
    const navegar = async (rota, texto) => {
      await cdp("Page.navigate", { url: `http://localhost:3100${rota}` });
      await aguardarTexto(texto);
    };
    const clicar = (trecho) => avaliar(`Array.from(document.querySelectorAll('main a, main button')).find(e => e.textContent.includes(${JSON.stringify(trecho)})).click()`);
    const preencher = (valor) => avaliar(`(() => { const e = document.querySelector('input[type=search]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(e, ${JSON.stringify(valor)}); e.dispatchEvent(new Event('input', {bubbles:true})); })()`);
    const ordenar = async (ordem) => {
      await avaliar(`const s = document.querySelector('select'); s.value=${JSON.stringify(ordem)}; s.dispatchEvent(new Event('change', {bubbles:true}));`);
      await aguardar(async () => await avaliar(`new URL(location.href).searchParams.get('ordem') === ${JSON.stringify(ordem)}`), "ordem na URL");
    };
    const itens = () => avaliar("Array.from(document.querySelectorAll('section[aria-label=\"Resultados da busca\"] > ul > li')).map(e => (e.querySelector('h2 a') ?? e.querySelector('a .font-medium')).textContent)");
    const contexto = async (tipo, termo, ordem, lista = false) => {
      const atual = await avaliar("({caminho:location.pathname, q:new URL(location.href).searchParams.get('q'), ordem:new URL(location.href).searchParams.get('ordem'), busca:new URL(location.href).searchParams.get('busca')})");
      assert.equal(atual.q, termo);
      assert.equal(atual.ordem, ordem);
      if (lista) assert.equal(atual.caminho, `/${tipo}`);
      else assert.equal(atual.busca, tipo);
    };
    const capturar = async (nome) => {
      if (!process.env.PREVIEW_DIR) return;
      await mkdir(process.env.PREVIEW_DIR, { recursive: true });
      const { data } = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
      await writeFile(join(process.env.PREVIEW_DIR, `155-${nome}.png`), Buffer.from(data, "base64"));
    };
    const semTransbordar = async () => assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true);
    try {
      for (const width of [320, 768, 1280]) {
        await cdp("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width === 320 });
        for (const tema of ["light", "dark"]) {
          await cdp("Emulation.setEmulatedMedia", { features: [{ name: "prefers-color-scheme", value: tema }] });
          for (const tipo of ["professores", "disciplinas"]) {
            await navegar(`/${tipo}`, "Digite ao menos 2 letras");
            await semTransbordar();
            const antes = consultas;
            // Evento repetido com valor inválido confirma hidratação, sem disparar HTTP.
            await aguardar(async () => { await preencher("x"); return await avaliar("new URL(location.href).searchParams.get('q') === 'x'"); }, "campo hidratado");
            assert.equal(consultas, antes);
            await preencher("Teste");
            await aguardarTexto("3 resultado(s)");
            assert.equal(await avaliar("document.querySelectorAll('header a[aria-label=\"Conta: entrar ou criar conta\"]').length"), 1);
            await avaliar("document.querySelector('input[type=search]').focus()");
            await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
            await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
            assert.equal(await avaliar("document.activeElement === document.querySelector('select')"), true);
            assert.equal(await avaliar("getComputedStyle(document.activeElement).outlineStyle !== 'none'"), true);
            assert.equal(await avaliar("document.querySelector('select').labels[0].textContent.includes('Ordenar resultados')"), true);
            assert.deepEqual(await itens(), tipo === "professores" ? ["Álvaro Teste", "Ana Teste", "Zélia Teste"] : ["Álgebra Teste", "Biologia Teste", "Zoologia Teste"]);
            const total = consultas;
            await ordenar("unidade");
            assert.equal(consultas, total, "Trocar ordem não refaz a busca");
            assert.deepEqual(await itens(), tipo === "professores" ? ["Zélia Teste", "Ana Teste", "Álvaro Teste"] : ["Zoologia Teste", "Biologia Teste", "Álgebra Teste"]);
            await semTransbordar();
            if (width === 320 || width === 1280) await capturar(`${tipo}-${width}-${tema}`);
            await avaliar("history.back()");
            await aguardar(async () => await avaliar("document.querySelector('select').value === 'nome'"), "histórico da ordenação");
            await avaliar("history.forward()");
            await aguardar(async () => await avaliar("document.querySelector('select').value === 'unidade'"), "avançar ordenação");
            const destino = tipo === "professores" ? professor.id : disciplina.id;
            await avaliar(`document.querySelector('main a[href^="/${tipo}/${destino}?"]').click()`);
            await aguardar(async () => await avaliar(`location.pathname === '/${tipo}/${destino}'`), "detalhe do resultado");
            await aguardarTexto(tipo === "professores" ? "Disciplinas lecionadas" : "Comparação de professores");
            await contexto(tipo, "Teste", "unidade");
            await clicar("Voltar aos resultados");
            await aguardarTexto("3 resultado(s)");
            await contexto(tipo, "Teste", "unidade", true);
            assert.equal(await avaliar("document.querySelector('input[type=search]').value"), "Teste");
            await avaliar("history.back()");
            await aguardar(async () => await avaliar(`location.pathname === '/${tipo}/${destino}'`), "histórico volta ao detalhe");
            await aguardarTexto(tipo === "professores" ? "Disciplinas lecionadas" : "Comparação de professores");
            await avaliar("history.back()");
            await aguardarTexto("3 resultado(s)");
            await contexto(tipo, "Teste", "unidade", true);
            await cdp("Page.reload");
            await aguardarTexto("3 resultado(s)");
            await contexto(tipo, "Teste", "unidade", true);
            await preencher("vazio");
            await aguardarTexto("Nenhum resultado");
            await semTransbordar();
            falhar = true;
            await preencher("falha");
            await aguardarTexto("Não foi possível buscar");
            assert.equal(await avaliar("document.body.innerText.includes('Nenhum resultado')"), false);
            await semTransbordar();
            if (width === 320) await capturar(`${tipo}-erro-${tema}`);
            falhar = false;
            await clicar("Tentar novamente");
            await aguardarTexto("3 resultado(s)");
            await contexto(tipo, "falha", "unidade", true);
            await preencher("");
            await aguardarTexto("Digite ao menos 2 letras");
            assert.deepEqual(await itens(), []);
          }
          for (const rota of ["/login", "/cadastro"]) {
            await navegar(rota, rota === "/login" ? "Use sua conta institucional" : "Use seu e-mail institucional");
            await aguardar(async () => await avaliar("!!document.querySelector('[name=senha]')"), "senha");
            await aguardar(async () => { await clicar("Mostrar senha"); return await avaliar("document.querySelector('[name=senha]').type === 'text'"); }, "controle de senha hidratado");
            await avaliar("document.querySelector('[name=senha]').value='senha-apenas-teste'");
            const enviosAntes = logins;
            await clicar("Ocultar senha");
            assert.equal(await avaliar("document.querySelector('[name=senha]').type"), "password");
            assert.equal(await avaliar("document.querySelector('button[aria-controls]').type"), "button");
            assert.equal(await avaliar("document.querySelector('button[aria-controls]').getAttribute('aria-pressed')"), "false");
            assert.equal(await avaliar("document.querySelector('[name=senha]').value"), "senha-apenas-teste");
            assert.equal(logins, enviosAntes);
            assert.equal(await avaliar("document.querySelector('[aria-label=\"Etapas da jornada\"], input[type=search], main select') === null"), true);
            await avaliar("document.querySelector('button[aria-controls]').focus()");
            assert.equal(await avaliar("document.activeElement === document.querySelector('button[aria-controls]')"), true);
            await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Enter", code: "Enter", text: "\r", windowsVirtualKeyCode: 13 });
            await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Enter", code: "Enter", windowsVirtualKeyCode: 13 });
            await aguardar(async () => await avaliar("document.querySelector('[name=senha]').type === 'text'"), "mostrar senha por teclado");
            assert.equal(await avaliar("getComputedStyle(document.activeElement).outlineStyle !== 'none'"), true);
            assert.equal(await avaliar("!!document.querySelector('label[for=\"'+document.querySelector('[name=senha]').id+'\"]')"), true);
            await semTransbordar();
            if (width === 320 || width === 1280) await capturar(`${rota.slice(1)}-${width}-${tema}`);
          }
        }
      }
      const consultasAntesDaCorrida = consultas;
      await navegar("/professores?q=lenta&ordem=nome", "Buscando…");
      await aguardar(() => Promise.resolve(consultas > consultasAntesDaCorrida), "consulta lenta");
      await preencher("nova");
      await aguardarTexto("1 resultado(s)");
      await aguardar(() => Promise.resolve(lentasConcluidas > 0), "resposta antiga recebida");
      assert.deepEqual(await itens(), ["nova"]);

      await navegar(`/professores/${professor.id}?busca=disciplinas&q=Teste&ordem=unidade`, "Disciplinas lecionadas");
      await clicar("Disciplina de teste");
      await aguardarTexto("Avaliar este professor na disciplina");
      await contexto("disciplinas", "Teste", "unidade");
      await clicar("Avaliar este professor");
      await aguardarTexto("Avaliar professor na disciplina");
      await contexto("disciplinas", "Teste", "unidade");
      await clicar("Voltar para a consulta");
      await aguardarTexto("Avaliar este professor na disciplina");
      await clicar("Voltar para Professor de teste");
      await aguardarTexto("Disciplinas lecionadas");
      await clicar("Comparar professores desta disciplina");
      await aguardarTexto("Comparação de professores");
      await contexto("disciplinas", "Teste", "unidade");
      await clicar("Professor de teste");
      await aguardarTexto("Disciplinas lecionadas");
      await clicar("Voltar aos resultados");
      await aguardarTexto("3 resultado(s)");
      await contexto("disciplinas", "Teste", "unidade", true);

      await navegar("/login", "Use sua conta institucional");
      await aguardar(async () => await avaliar("!!document.querySelector('[name=email]')"), "formulário de entrada");
      await avaliar("document.querySelector('[name=email]').value='teste@aluno.unb.br'; document.querySelector('[name=senha]').value='senha-apenas-teste'; document.querySelector('button[type=submit]').click()");
      await aguardarTexto("Sua sessão está ativa");
      assert.equal(logins, 1);
      console.log("#155: buscas, ordenação sem HTTP, ida/retorno, histórico, recarga, vazio, erro/recuperação em 320/768/1280 e claro/escuro; componentes de #157/#158, corrida de respostas, senha por teclado e login via serviço controlado aprovados. Este runner usa HTTP controlado e viewport emulado.");
    } finally { ativo = false; }
  }
  return { responder, verificar };
}
