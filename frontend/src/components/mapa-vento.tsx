"use client";

import { useEffect, useRef } from "react";

/*
 * Fundo decorativo do título da home (protótipo da #211): partículas seguem um
 * campo de fluxo suave. Não carrega dados, fica fora da árvore de acessibilidade,
 * pausa fora da tela e vira um quadro estático com movimento reduzido.
 */
const CORES = ["--background", "--accent-soft", "--accent", "--ink-soft"] as const;
const VERDES = ["--brand-green", "--success", "--ink-soft"] as const;
const DENSIDADE = 11;

const rgb = (hex: string) => {
  const limpo = hex.trim().replace("#", "");
  const completo = limpo.length === 3 ? limpo.split("").map((c) => c + c).join("") : limpo;
  const n = parseInt(completo, 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
};
const misturar = (a: number[], b: number[], t: number) => a.map((v, i) => Math.round(v + (b[i] - v) * t));

function ruido() {
  const p = new Uint8Array(512);
  const base = Array.from({ length: 256 }, (_, i) => i);
  let s = 1013;
  for (let i = 255; i > 0; i--) {
    s = (s * 16807) % 2147483647;
    const j = s % (i + 1);
    [base[i], base[j]] = [base[j], base[i]];
  }
  for (let i = 0; i < 512; i++) p[i] = base[i & 255];
  const g = (h: number) => (h / 255) * 2 - 1;
  const f = (t: number) => t * t * (3 - 2 * t);
  return (x: number, y: number) => {
    const X = Math.floor(x) & 255, Y = Math.floor(y) & 255, xf = x - Math.floor(x), yf = y - Math.floor(y);
    const a = g(p[p[X] + Y]), b = g(p[p[X + 1] + Y]), c = g(p[p[X] + Y + 1]), d = g(p[p[X + 1] + Y + 1]);
    const u = f(xf), v = f(yf);
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v;
  };
}

export default function MapaVento({ className = "" }: { className?: string }) {
  const hostRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const host = hostRef.current;
    if (!host) return;
    const estilos = getComputedStyle(document.documentElement);
    const ler = (nome: string) => estilos.getPropertyValue(nome).trim();
    const cores = CORES.map(ler);
    if (cores.some((cor) => !/^#[\da-f]{3,6}$/i.test(cor))) return;
    const canvas = document.createElement("canvas");
    canvas.setAttribute("aria-hidden", "true");
    canvas.className = "absolute inset-0 block size-full";
    host.prepend(canvas);
    const ctx = canvas.getContext("2d");
    if (!ctx) return () => canvas.remove();

    const reduzido = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const grosso = !matchMedia("(hover: hover) and (pointer: fine)").matches;
    const dpr = Math.min(devicePixelRatio, grosso ? 1.5 : 2);
    const n2 = ruido();
    const fundo = rgb(cores[0]);
    const rampa = (paradas: string[]) => [0, 0.33, 0.66, 1].map((t) => {
      const c = t < 0.5 ? misturar(rgb(paradas[0]), rgb(paradas[1]), t * 2) : misturar(rgb(paradas[1]), rgb(paradas[2]), (t - 0.5) * 2);
      return `rgba(${c[0]},${c[1]},${c[2]},${0.62 + t * 0.38})`;
    });
    const rampas = [rampa(cores.slice(1)), rampa(VERDES.map(ler))];
    const tracos = rampas.flat();
    let W = 0, H = 0, raf = 0, visivel = true, t = 0, ultimo = 0;
    let px = new Float32Array(0), py = new Float32Array(0), vida = new Float32Array(0);
    const ponteiro = { x: 0, y: 0, s: 0, alvo: 0 };

    const semear = (i: number) => { px[i] = Math.random() * W; py[i] = Math.random() * H; vida[i] = 40 + Math.random() * 160; };
    const redimensionar = () => {
      const w = host.clientWidth, h = host.clientHeight;
      if (w === W && h === H) return;
      W = w; H = h;
      canvas.width = Math.round(W * dpr); canvas.height = Math.round(H * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.fillStyle = cores[0]; ctx.fillRect(0, 0, W, H);
      const n = Math.round(((W * H) / 10000) * DENSIDADE * (grosso ? 0.6 : 1));
      px = new Float32Array(n); py = new Float32Array(n); vida = new Float32Array(n);
      for (let i = 0; i < n; i++) semear(i);
    };
    const vento = (x: number, y: number) => {
      const s = 0.0016;
      const a = n2(x * s + t * 0.02, y * s - t * 0.015) * Math.PI * 2.2 + n2(x * s * 2.7 + 40, y * s * 2.7) * 0.8;
      const m = 0.7 + 0.6 * (n2(x * s * 0.6 - 30, y * s * 0.6 + t * 0.01) + 1) * 0.5;
      let vx = Math.cos(a) * m, vy = Math.sin(a) * m;
      if (ponteiro.s > 0.01) {
        const dx = x - ponteiro.x, dy = y - ponteiro.y, d2 = dx * dx + dy * dy;
        const k = ponteiro.s * Math.exp(-d2 / 44100) * 2.2;
        const d = Math.sqrt(d2) + 1;
        vx += (-dy / d - (dx / d) * 0.22) * k;
        vy += (dx / d - (dy / d) * 0.22) * k;
      }
      return [vx, vy];
    };
    const quadro = (passos: number) => {
      ctx.fillStyle = `rgba(${fundo[0]},${fundo[1]},${fundo[2]},${passos > 1 ? 0.02 : 0.06})`;
      ctx.fillRect(0, 0, W, H);
      ctx.lineWidth = 1; ctx.lineCap = "round";
      const caminhos = tracos.map(() => new Path2D());
      for (let i = 0; i < px.length; i++) {
        const x = px[i], y = py[i];
        const [vx, vy] = vento(x, y);
        const nx = x + vx * 1.6, ny = y + vy * 1.6;
        const faixa = Math.max(0, Math.min(3, Math.floor(((Math.hypot(vx, vy) - 0.65) / 0.75) * 4)));
        const caminho = caminhos[(i % 5 < 2 ? 4 : 0) + faixa];
        caminho.moveTo(x, y); caminho.lineTo(nx, ny);
        if (--vida[i] <= 0 || nx < -4 || ny < -4 || nx > W + 4 || ny > H + 4) semear(i);
        else { px[i] = nx; py[i] = ny; }
      }
      caminhos.forEach((caminho, i) => { ctx.strokeStyle = tracos[i]; ctx.stroke(caminho); });
    };
    const laco = (agora: number) => {
      if (!visivel || document.hidden) { raf = 0; return; }
      raf = requestAnimationFrame(laco);
      if (grosso && agora - ultimo < 30) return;
      ultimo = agora;
      redimensionar();
      ponteiro.s += (ponteiro.alvo - ponteiro.s) * 0.04;
      t += 0.016;
      quadro(1);
    };
    const acordar = () => { if (!reduzido && !raf && visivel && !document.hidden) raf = requestAnimationFrame(laco); };
    const mover = (e: PointerEvent) => {
      const r = host.getBoundingClientRect();
      const x = e.clientX - r.left, y = e.clientY - r.top;
      const dentro = x >= 0 && y >= 0 && x <= r.width && y <= r.height;
      if (dentro) { const k = ponteiro.s < 0.05 ? 1 : 0.35; ponteiro.x += (x - ponteiro.x) * k; ponteiro.y += (y - ponteiro.y) * k; }
      ponteiro.alvo = dentro ? 1 : 0;
    };
    const estatico = () => { redimensionar(); for (let k = 0; k < 90; k++) quadro(2); };

    redimensionar();
    if (reduzido) estatico();
    const io = new IntersectionObserver(([entrada]) => { visivel = entrada.isIntersecting; acordar(); });
    io.observe(host);
    const ro = new ResizeObserver(() => { if (reduzido) estatico(); });
    ro.observe(host);
    document.addEventListener("visibilitychange", acordar);
    if (!reduzido) {
      acordar();
      if (!grosso) window.addEventListener("pointermove", mover, { passive: true });
    }
    return () => {
      cancelAnimationFrame(raf);
      io.disconnect(); ro.disconnect();
      document.removeEventListener("visibilitychange", acordar);
      window.removeEventListener("pointermove", mover);
      canvas.remove();
    };
  }, []);

  return <div ref={hostRef} aria-hidden="true" className={`isolate overflow-hidden bg-background ${className}`} />;
}
