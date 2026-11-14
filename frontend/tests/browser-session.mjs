// Infraestrutura já usada no projeto: Node, CDP e Edge/Chromium, sem dependências novas.
import { spawn } from 'node:child_process';
import { mkdtempSync, existsSync } from 'node:fs';
import { rm } from 'node:fs/promises';
import { createServer } from 'node:http';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { contextoEmTransicao } from './browser-navigation.mjs';

export async function comNavegador({ fixture, executar, diretorioFrontend }) {
  const navegador = process.env.BROWSER_PATH ?? 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe';
  assert.ok(existsSync(navegador), 'Informe BROWSER_PATH com Edge/Chromium.');
  for (const porta of fixture ? [8000, 3100, 9228] : [3100, 9228]) {
    const reserva = createServer();
    await new Promise((resolve, reject) => { reserva.once('error', reject); reserva.listen(porta, '127.0.0.1', resolve); });
    await new Promise(resolve => reserva.close(resolve));
  }
  const perfil = mkdtempSync(join(tmpdir(), 'undb-comentarios-'));
  let next, browser, socket, sequence = 0;
  const pendentes = new Map();
  const cdp = (method, params = {}) => new Promise((resolve, reject) => {
    const id = ++sequence;
    const timer = setTimeout(() => { pendentes.delete(id); reject(new Error(`Timeout CDP: ${method}`)); }, 15000);
    pendentes.set(id, { resolve, reject, timer }); socket.send(JSON.stringify({ id, method, params }));
  });
  const avaliar = async expression => {
    const r = await cdp('Runtime.evaluate', { expression: `{${expression}}`, returnByValue: true, awaitPromise: true });
    if (r.exceptionDetails) throw new Error(JSON.stringify(r.exceptionDetails));
    return r.result.value;
  };
  const aguardar = async (condicao, nome) => {
    const inicio = Date.now();
    while (Date.now() - inicio < 25000) {
      try {
        if (await condicao()) return;
      } catch (erro) {
        if (!contextoEmTransicao(erro)) throw erro;
      }
      await new Promise(resolve => setTimeout(resolve, 100));
    }
    throw new Error(`Timeout: ${nome}`);
  };
  const responder = async porta => {
    try { return (await fetch(`http://127.0.0.1:${porta}/${porta === 9228 ? 'json' : ''}`, { signal: AbortSignal.timeout(1500) })).ok; }
    catch { return false; }
  };
  try {
    if (fixture) await new Promise(resolve => fixture.listen(8000, resolve));
    next = spawn(process.execPath, ['node_modules/next/dist/bin/next', 'start', '-p', '3100'], {
      cwd: diretorioFrontend ?? fileURLToPath(new URL('../', import.meta.url)), stdio: 'inherit', windowsHide: true,
    });
    await aguardar(() => responder(3100), 'Next.js');
    browser = spawn(navegador, ['--headless=new', '--edge-skip-compat-layer-relaunch', '--disable-gpu', '--no-first-run', '--remote-debugging-port=9228', `--user-data-dir=${perfil}`, 'about:blank'], { stdio: 'ignore', windowsHide: true });
    await aguardar(() => responder(9228), 'Edge/Chromium');
    const paginas = await (await fetch('http://127.0.0.1:9228/json')).json();
    socket = new WebSocket(paginas.find(p => p.type === 'page').webSocketDebuggerUrl);
    await new Promise(resolve => socket.addEventListener('open', resolve, { once: true }));
    socket.addEventListener('message', ({ data }) => {
      const r = JSON.parse(data), p = pendentes.get(r.id);
      if (!p) return;
      clearTimeout(p.timer); pendentes.delete(r.id);
      if (r.error) p.reject(new Error(JSON.stringify(r.error))); else p.resolve(r.result);
    });
    await cdp('Page.enable');
    await executar({ cdp, avaliar, aguardar });
  } finally {
    if (socket?.readyState === WebSocket.OPEN) await cdp('Browser.close').catch(() => {});
    socket?.close();
    for (const p of pendentes.values()) { clearTimeout(p.timer); p.reject(new Error('Teste encerrado')); }
    browser?.kill(); next?.kill();
    if (fixture?.listening) { fixture.closeAllConnections(); await new Promise(resolve => fixture.close(resolve)); }
    await rm(perfil, { recursive: true, force: true, maxRetries: 10, retryDelay: 200 });
  }
}
