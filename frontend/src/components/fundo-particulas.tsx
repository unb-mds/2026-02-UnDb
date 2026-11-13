"use client";

import { useEffect, useRef } from "react";

/*
 * Fundo de partículas (vidro e carvão) com vórtice magnético sob o mouse.
 * Decorativo: fica fora da árvore de acessibilidade, não recebe foco nem cliques, usa um canvas
 * do tamanho da janela, pausa com a aba oculta (requestAnimationFrame) e vira um quadro estático
 * com movimento reduzido. A quantidade de partículas acompanha a área e é menor em telas de toque.
 */
const RAIO_MAGNETICO = 280;
const FORCA_VORTICE = 0.07;
const FORCA_ATRACAO = 0.12;

type Particula = { x: number; y: number; vx: number; vy: number; tamanho: number; alfa: number; cor: string; rotacao: number; giro: number; brilho: number };

export default function FundoParticulas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    const reduzido = matchMedia("(prefers-reduced-motion: reduce)").matches;
    const toque = !matchMedia("(hover: hover) and (pointer: fine)").matches;
    const mouse = { x: -1000, y: -1000 };
    let largura = 0, altura = 0, quadro = 0;
    let particulas: Particula[] = [];

    const criar = (): Particula => {
      const vidro = Math.random() > 0.7;
      return {
        x: Math.random() * largura, y: Math.random() * altura,
        tamanho: Math.random() * 1.5 + 0.5,
        vx: (Math.random() - 0.5) * 0.2, vy: (Math.random() - 0.5) * 0.2,
        cor: vidro ? "240, 245, 255" : "110, 112, 120",
        alfa: Math.random() * 0.4 + 0.1,
        rotacao: Math.random() * Math.PI * 2, giro: (Math.random() - 0.5) * 0.05, brilho: 0,
      };
    };

    const iniciar = () => {
      largura = canvas.width = window.innerWidth;
      altura = canvas.height = window.innerHeight;
      ctx.fillStyle = "#000000";
      ctx.fillRect(0, 0, largura, altura);
      const total = Math.max(300, Math.min(1000, Math.round((largura * altura) / 1400))) * (toque ? 0.4 : 1);
      particulas = Array.from({ length: Math.round(total) }, criar);
      if (reduzido) desenhar();
    };

    const atualizar = (p: Particula) => {
      const dx = mouse.x - p.x, dy = mouse.y - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      if (dist < RAIO_MAGNETICO) {
        const forca = (RAIO_MAGNETICO - dist) / RAIO_MAGNETICO;
        p.vx += (dx / dist) * forca * FORCA_ATRACAO + (dy / dist) * forca * FORCA_VORTICE * 10;
        p.vy += (dy / dist) * forca * FORCA_ATRACAO - (dx / dist) * forca * FORCA_VORTICE * 10;
        p.brilho = forca * 0.7;
      } else p.brilho *= 0.92;
      p.x += p.vx; p.y += p.vy;
      p.vx = p.vx * 0.95 + (Math.random() - 0.5) * 0.04;
      p.vy = p.vy * 0.95 + (Math.random() - 0.5) * 0.04;
      p.rotacao += p.giro + (Math.abs(p.vx) + Math.abs(p.vy)) * 0.05;
      if (p.x < -20) p.x = largura + 20;
      if (p.x > largura + 20) p.x = -20;
      if (p.y < -20) p.y = altura + 20;
      if (p.y > altura + 20) p.y = -20;
    };

    const desenhar = () => {
      for (const p of particulas) {
        ctx.save();
        ctx.translate(p.x, p.y);
        ctx.rotate(p.rotacao);
        ctx.fillStyle = `rgba(${p.cor}, ${Math.min(p.alfa + p.brilho, 0.7)})`;
        if (p.brilho > 0.3) { ctx.shadowBlur = 8 * p.brilho; ctx.shadowColor = `rgba(126, 180, 255, ${p.brilho})`; }
        ctx.beginPath();
        ctx.moveTo(0, -p.tamanho * 2.5); ctx.lineTo(p.tamanho, 0); ctx.lineTo(0, p.tamanho * 2.5); ctx.lineTo(-p.tamanho, 0);
        ctx.closePath(); ctx.fill();
        ctx.restore();
      }
    };

    const animar = () => {
      ctx.fillStyle = "rgba(0, 0, 0, 0.18)";
      ctx.fillRect(0, 0, largura, altura);
      particulas.forEach(atualizar);
      desenhar();
      quadro = requestAnimationFrame(animar);
    };

    const mover = (e: MouseEvent) => { mouse.x = e.clientX; mouse.y = e.clientY; };
    const tocar = (e: TouchEvent) => { if (e.touches[0]) { mouse.x = e.touches[0].clientX; mouse.y = e.touches[0].clientY; } };
    // A barra de endereço do celular muda só a altura ao rolar: ignora isso para não recriar as partículas.
    const redimensionar = () => { if (window.innerWidth === largura && Math.abs(window.innerHeight - altura) < 160) return; iniciar(); };
    iniciar();
    window.addEventListener("resize", redimensionar);
    if (!reduzido) {
      window.addEventListener("mousemove", mover, { passive: true });
      window.addEventListener("touchmove", tocar, { passive: true });
      quadro = requestAnimationFrame(animar);
    }
    return () => {
      window.removeEventListener("resize", redimensionar);
      window.removeEventListener("mousemove", mover);
      window.removeEventListener("touchmove", tocar);
      cancelAnimationFrame(quadro);
    };
  }, []);

  return <canvas ref={canvasRef} aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 block h-full w-full" />;
}
