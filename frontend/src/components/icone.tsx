import type { ReactNode } from "react";

export type NomeIcone = "arrow-left" | "arrow-right" | "book" | "check" | "compare" | "info" | "search" | "shield" | "user";

const caminhos: Record<NomeIcone, ReactNode> = {
  "arrow-left": <path d="m15 18-6-6 6-6" />,
  "arrow-right": <><path d="M5 12h14" /><path d="m13 6 6 6-6 6" /></>,
  book: <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2Z" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  compare: <><path d="M8 3v18" /><path d="m3 8 5-5 5 5" /><path d="M16 21V3" /><path d="m11 16 5 5 5-5" /></>,
  info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v5" /><path d="M12 8h.01" /></>,
  search: <><circle cx="11" cy="11" r="7" /><path d="m20 20-4-4" /></>,
  shield: <><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10Z" /><path d="m9 12 2 2 4-4" /></>,
  user: <><circle cx="12" cy="8" r="4" /><path d="M4 21a8 8 0 0 1 16 0" /></>,
};

/** Ícones de traço do protótipo da #211; sempre decorativos, o texto vizinho dá o nome acessível. */
export default function Icone({ nome, pequeno = false }: { nome: NomeIcone; pequeno?: boolean }) {
  return <svg className={pequeno ? "icon icon-sm" : "icon"} viewBox="0 0 24 24" aria-hidden="true" focusable="false">{caminhos[nome]}</svg>;
}
