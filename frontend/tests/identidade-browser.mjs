import assert from "node:assert/strict";
import { mkdir, writeFile } from "node:fs/promises";
import { join } from "node:path";
import { contrasteTexto } from "./browser-contrast.mjs";

// Reutiliza o navegador e as respostas controladas do runner de avaliação.
export async function verificarIdentidade({ cdp, avaliar, aguardar }) {
  await cdp("Page.navigate", { url: "http://localhost:3100/" });
  await aguardar(async () => await avaliar("!!document.querySelector('main button.primary') && !!document.querySelector('.brand-logo')?.complete"), "logo e ação principal carregadas");
  assert.equal(await avaliar("document.querySelector('.brand-logo').naturalWidth > 0"), true);
  assert.equal(await avaliar("document.querySelector('.brand').getAttribute('aria-label')"), "UnDb — início");
  assert.equal(await avaliar("document.querySelector('.brand').getAttribute('href')"), "/");
  assert.equal(await avaliar("document.querySelector('.brand-logo').alt"), "");
  const icons = await avaliar(`Promise.all([...document.querySelectorAll('link[rel="icon"]')].map(async link => {
    const response = await fetch(link.href);
    const bytes = new Uint8Array(await response.arrayBuffer());
    return { path: new URL(link.href).pathname, ok: response.ok, signature: [...bytes.slice(0, 4)] };
  }))`);
  assert.ok(icons.some(icon => icon.path === "/favicon.ico" && icon.ok && icon.signature.join() === "0,0,1,0"));
  assert.ok(icons.some(icon => icon.path === "/icon.png" && icon.ok && icon.signature.join() === "137,80,78,71"));
  await cdp("DOM.enable");
  await cdp("CSS.enable");
  const { root } = await cdp("DOM.getDocument");
  const { nodeId } = await cdp("DOM.querySelector", { nodeId: root.nodeId, selector: "main button.primary" });
  const capture = async (name) => {
    if (!process.env.PREVIEW_DIR) return;
    await mkdir(process.env.PREVIEW_DIR, { recursive: true });
    const { data } = await cdp("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
    await writeFile(join(process.env.PREVIEW_DIR, `214-${name}.png`), Buffer.from(data, "base64"));
  };
  try {
    for (const width of [320, 390, 768, 1440]) {
      await cdp("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: false });
      assert.equal(await avaliar("document.documentElement.scrollWidth <= innerWidth"), true, `overflow: ${width}`);
      assert.equal(await avaliar("document.querySelector('.brand').getBoundingClientRect().height >= 44"), true);
      for (const [state, pseudos, expected] of [
        ["normal", [], "rgb(0, 130, 46)"],
        ["hover", ["hover"], "rgb(0, 107, 38)"],
        ["active", ["hover", "active"], "rgb(0, 90, 28)"],
        ["disabled", ["hover", "active"], "rgb(37, 50, 71)"],
      ]) {
        await avaliar(`document.querySelector('main button.primary').disabled = ${state === "disabled"}`);
        await cdp("CSS.forcePseudoState", { nodeId, forcedPseudoClasses: pseudos });
        await aguardar(async () => await avaliar(`getComputedStyle(document.querySelector('main button.primary')).backgroundColor === ${JSON.stringify(expected)}`), `cor ${state}`);
        assert.ok(await contrasteTexto(avaliar, "main button.primary") >= 4.5, `${state}, ${width}`);
        await capture(`${width}-${state}`);
      }
      await avaliar("document.querySelector('main button.primary').disabled = false");
      await cdp("CSS.forcePseudoState", { nodeId, forcedPseudoClasses: [] });
      await avaliar("document.querySelector('main input[name=q]').focus()");
      await cdp("Input.dispatchKeyEvent", { type: "keyDown", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      await cdp("Input.dispatchKeyEvent", { type: "keyUp", key: "Tab", code: "Tab", windowsVirtualKeyCode: 9 });
      assert.equal(await avaliar("document.activeElement === document.querySelector('main button.primary') && document.activeElement.matches(':focus-visible')"), true);
      assert.equal(await avaliar("getComputedStyle(document.activeElement).outlineWidth"), "2px");
      await capture(`${width}-focus`);
      await avaliar("document.activeElement.blur()");
    }
    console.log("Identidade: logo carregada, link acessível ao início, ICO/PNG servidos, ausência de overflow e ações normal/hover/active/disabled/foco em 320/390/768/1440 px; contraste renderizado >= 4,5:1.");
  } finally {
    await avaliar("document.querySelector('main button.primary').disabled = false");
    await cdp("CSS.forcePseudoState", { nodeId, forcedPseudoClasses: [] });
    await cdp("CSS.disable");
  }
}
