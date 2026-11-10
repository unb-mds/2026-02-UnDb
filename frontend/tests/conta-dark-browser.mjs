import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import { contrasteTexto } from './browser-contrast.mjs';

export async function capturarContaDark(cdp, nome) {
  if (!process.env.PREVIEW_DIR) return;
  await mkdir(process.env.PREVIEW_DIR, { recursive: true });
  const { data } = await cdp('Page.captureScreenshot', { format: 'png', captureBeyondViewport: true });
  await writeFile(join(process.env.PREVIEW_DIR, `205-${nome}.png`), Buffer.from(data, 'base64'));
}

// Usa o mesmo navegador e a API controlada do runner de avaliação, sem novas ferramentas.
export async function verificarContaDark({ cdp, avaliar, aguardar }) {
  for (const largura of [320, 390, 768, 1440]) {
    await cdp('Emulation.setDeviceMetricsOverride', { width: largura, height: 900, deviceScaleFactor: 1, mobile: largura < 768 });
    for (const [rota, titulo] of [['login', 'Entrar'], ['cadastro', 'Criar conta'], ['confirmar-email', 'Confirmação de e-mail']]) {
      await cdp('Page.navigate', { url: `http://localhost:3100/${rota}` });
      await aguardar(() => avaliar(`location.pathname === '/${rota}' && document.querySelector('main h1')?.textContent === ${JSON.stringify(titulo)}`), `${rota}: título pronto`);
      if (rota !== 'confirmar-email') {
        await aguardar(() => avaliar('!!document.querySelector("main input[name=senha]")'), `${rota}: formulário pronto`);
        // Não há envio nem credenciais. A condição confirma hidratação antes do teste de teclado.
        await aguardar(async () => {
          if (await avaliar('document.querySelector("main input[name=senha]").type === "text"')) return true;
          await avaliar('document.querySelector("main button[aria-controls]").click()');
          return avaliar('document.querySelector("main input[name=senha]").type === "text"');
        }, `${rota}: mostrar senha`);
        assert.equal(await avaliar('document.querySelector("main button[aria-controls]").getAttribute("aria-pressed")'), 'true');
        await avaliar('document.querySelector("main button[aria-controls]").click()');
        await aguardar(() => avaliar('document.querySelector("main input[name=senha]").type === "password"'), `${rota}: ocultar senha`);
        assert.equal(await avaliar('document.querySelectorAll("main [aria-current=page]").length'), 1);
        assert.ok(await contrasteTexto(avaliar, 'main input[name=email]') >= 4.5);
        assert.ok(await avaliar('document.querySelector("main input[name=email]").getBoundingClientRect().height') >= 44);
        await avaliar('document.querySelector("main input").focus()');
        await cdp('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
        await cdp('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 });
        assert.equal(await avaliar('document.activeElement instanceof HTMLInputElement'), true);
        assert.equal(await avaliar('getComputedStyle(document.activeElement).outlineStyle'), 'solid');
        assert.ok(await avaliar('parseFloat(getComputedStyle(document.activeElement).outlineWidth)') >= 2);
      } else {
        await aguardar(() => avaliar('document.body.innerText.includes("O link de confirmação está incompleto.")'), 'confirmação sem token');
        assert.ok(await contrasteTexto(avaliar, 'main [aria-live]') >= 4.5);
      }
      assert.equal(await avaliar('document.querySelectorAll("main h1").length'), 1);
      assert.equal(await avaliar('document.querySelectorAll("[aria-current=step]").length'), 0);
      assert.equal(await avaliar('document.documentElement.scrollWidth <= innerWidth'), true, `${rota}/${largura}: overflow`);
      await capturarContaDark(cdp, `${rota}-${largura}`);
    }
  }
  console.log('#205: conta em 320/390/768/1440 px, senha, teclado, contraste e confirmação incompleta aprovados; capturas somente com PREVIEW_DIR.');
}
