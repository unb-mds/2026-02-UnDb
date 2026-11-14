"use client";

import { useEffect, useRef, useState } from "react";
import { analisarComentario } from "@/lib/services/moderacao";
import { rotulosMotivo } from "@/lib/moderacao";
import { rotulosOpenAI } from "@/lib/types/moderacao";
import type { TriagemComentario } from "@/lib/types/moderacao";

const mensagens = {
  CONCLUIDA: "Análise assistiva concluída. Confira os sinais no contexto do comentário.",
  DESATIVADA: "O apoio de IA está desativado neste ambiente.",
  DADOS_SENSIVEIS: "O texto exige revisão local de privacidade e não foi enviado à IA.",
  LIMITE: "Limite de análises atingido. Continue com a revisão humana.",
  INDISPONIVEL: "O apoio de IA está indisponível. Continue com a revisão humana.",
};
type Estado = { tipo: "inicial" | "carregando" | "erro" } | { tipo: "pronto"; dados: TriagemComentario };

export default function ApoioModeracao({ versaoId, desabilitado }: { versaoId: string; desabilitado: boolean }) {
  const [estado, setEstado] = useState<Estado>({ tipo: "inicial" });
  const controlador = useRef<AbortController | null>(null);
  useEffect(() => () => controlador.current?.abort(), [versaoId]);
  async function analisar() {
    controlador.current?.abort();
    const consulta = new AbortController();
    controlador.current = consulta;
    setEstado({ tipo: "carregando" });
    try {
      const dados = await analisarComentario(versaoId, consulta.signal);
      if (!consulta.signal.aborted) setEstado({ tipo: "pronto", dados });
    } catch {
      if (!consulta.signal.aborted) setEstado({ tipo: "erro" });
    }
  }
  return <section aria-label="Apoio à revisão" className="space-y-3 rounded-lg border border-foreground/15 p-4">
    <h3 className="font-medium">Apoio à revisão</h3>
    <p className="text-sm text-foreground/70">A análise pode errar. Críticas acadêmicas negativas são permitidas e a decisão continua sendo sua.</p>
    <p className="text-sm text-foreground/70">A IA não verifica spam, dados pessoais ou todos os palavrões. Confira esses pontos na revisão humana e no filtro local.</p>
    <p className="text-xs text-foreground/70">Quando habilitada, esta ação envia o texto à OpenAI. Confira se ele contém dados privados antes de solicitar.</p>
    <button type="button" disabled={desabilitado || estado.tipo === "carregando"} onClick={() => void analisar()} className="button secondary min-h-11 disabled:opacity-50">
      {estado.tipo === "carregando" ? "Analisando…" : "Consultar apoio à revisão"}
    </button>
    <div aria-live="polite">
      {estado.tipo === "erro" && <p role="alert" className="text-sm">Não foi possível analisar esta versão. Atualize a fila ou continue com a revisão humana.</p>}
      {estado.tipo === "pronto" && <div className="space-y-2 text-sm">
        <p>{mensagens[estado.dados.status]}</p>
        <p>Filtro de termos: {estado.dados.filtro_ativo ? "habilitado" : "desativado"}.</p>
        {estado.dados.categorias_locais.length > 0 && <p>Sinais locais: {estado.dados.categorias_locais.map((c) => rotulosMotivo[c]).join(", ")}.</p>}
        {estado.dados.status === "CONCLUIDA" && <>
          <p>{estado.dados.categorias_ia.length ? `Sinais da IA: ${estado.dados.categorias_ia.map((c) => rotulosOpenAI[c]).join(", ")}.` : "A IA não identificou sinais nas categorias analisadas. Isso não garante que o texto seja adequado."}</p>
          {estado.dados.sinalizado && <p>A OpenAI sinalizou conteúdo potencialmente nocivo. Isso não é uma decisão de remoção.</p>}
        </>}
        <p className="text-xs text-foreground/60">Lista {estado.dados.versao_lista} · Integração {estado.dados.versao_integracao}{estado.dados.modelo && ` · ${estado.dados.modelo}`}</p>
      </div>}
    </div>
  </section>;
}
