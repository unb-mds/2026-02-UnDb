import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const css = readFileSync(new URL('../src/app/globals.css', import.meta.url), 'utf8');
const tokens = Object.fromEntries(Array.from(css.matchAll(/--([\w-]+):\s*(#[\da-f]{6});/gi), ([, nome, cor]) => [nome, cor]));

// Mesmo cálculo sRGB usado no helper de contraste do navegador, sem nova dependência.
function luminancia(cor) {
  const canais = cor.slice(1).match(/../g).map(v => parseInt(v, 16) / 255)
    .map(v => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  return canais[0] * 0.2126 + canais[1] * 0.7152 + canais[2] * 0.0722;
}

function contraste(texto, fundo) {
  assert.ok(tokens[texto], `Token ausente: ${texto}`);
  assert.ok(tokens[fundo], `Token ausente: ${fundo}`);
  const a = luminancia(tokens[texto]), b = luminancia(tokens[fundo]);
  return (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
}

test('ações primárias mantêm texto AA em normal, hover, active e disabled', t => {
  for (const fundo of ['primary', 'primary-hover', 'primary-active']) {
    const valor = contraste('on-primary', fundo);
    assert.ok(valor >= 4.5, `${fundo}: ${valor}`);
    t.diagnostic(`on-primary / ${fundo}: ${valor.toFixed(2)}:1`);
  }
  const disabled = contraste('on-disabled', 'disabled-surface');
  assert.ok(disabled >= 4.5);
  t.diagnostic(`on-disabled / disabled-surface: ${disabled.toFixed(2)}:1`);
});

test('texto e links azuis preservados são legíveis nas superfícies dark', () => {
  for (const fundo of ['background', 'panel', 'raised']) {
    for (const texto of ['foreground', 'accent']) {
      assert.ok(contraste(texto, fundo) >= 4.5, `${texto} / ${fundo}`);
    }
  }
});

test('foco e limites dos controles atingem 3:1 nas superfícies adjacentes', t => {
  for (const fundo of ['background', 'panel', 'raised']) {
    for (const indicador of ['focus', 'primary-border', 'control-border']) {
      const valor = contraste(indicador, fundo);
      assert.ok(valor >= 3, `${indicador} / ${fundo}: ${valor}`);
      t.diagnostic(`${indicador} / ${fundo}: ${valor.toFixed(2)}:1`);
    }
  }
});

test('destaques #242 preservam contraste do texto, código e foco nas superfícies usadas', t => {
  for (const [texto, fundo] of [
    ['foreground', 'panel'], ['ink-soft', 'panel'], ['muted', 'panel'],
    ['accent', 'panel'], ['accent', 'accent-soft'],
    ['ink-soft', 'background'],
  ]) {
    const valor = contraste(texto, fundo);
    assert.ok(valor >= 4.5, `${texto} / ${fundo}: ${valor}`);
    t.diagnostic(`${texto} / ${fundo}: ${valor.toFixed(2)}:1`);
  }
  const foco = contraste('focus', 'background');
  assert.ok(foco >= 3);
  t.diagnostic(`focus / background (offset do cartão): ${foco.toFixed(2)}:1`);
});
