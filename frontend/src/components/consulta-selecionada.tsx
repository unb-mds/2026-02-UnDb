"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";
import type { AvaliacaoAgregada } from "@/lib/types/avaliacao";
import type { ComentarioPublico } from "@/lib/types/comentario";
import { listarComentariosPublicados } from "@/lib/services/comentarios";
import ResultadoBento from "./resultado-bento";
import SecaoComentarios from "./secao-comentarios";
import Icone from "./icone";

export default function ConsultaSelecionada({ avaliacao: a, contexto }: { avaliacao: AvaliacaoAgregada; contexto: ContextoBusca | null }) {
  const [comentarios, setComentarios] = useState<ComentarioPublico[] | null>(null);
  const [erro, setErro] = useState(false);
  useEffect(() => {
    const controller = new AbortController();
    void listarComentariosPublicados(a.professorId, a.disciplinaId, controller.signal).then(v => { if (!controller.signal.aborted) setComentarios(v); }).catch(() => { if (!controller.signal.aborted) setErro(true); });
    return () => controller.abort();
  }, [a.professorId, a.disciplinaId]);
  const rotulos = { FACIL: "Fácil", MEDIO: "Médio", DIFICIL: "Difícil", RUIM: "Ruim", BOM: "Bom" };
  return <section id="consulta-selecionada" aria-labelledby="consulta-nome" className="mt-8 flex scroll-mt-48 flex-col gap-6">
    <div className="flex flex-wrap items-end justify-between gap-4"><div><span className="kicker">Professor nesta disciplina</span><h3 id="consulta-nome" className="section-title mt-2">{a.professor.nome}</h3><p className="lead mt-2">{a.totalAvaliacoes} avaliações. Dificuldade e chamada são informações neutras.</p></div><div className="flex flex-wrap gap-3"><Link className="button primary" href={comContextoBusca(`/professores/${a.professorId}/disciplinas/${a.disciplinaId}/avaliar`, contexto)}>Avaliar este professor <Icone nome="arrow-right" pequeno /></Link><Link className="button border-accent/50! text-accent!" href={comContextoBusca(`/professores/${a.professorId}`, contexto)}><Icone nome="user" pequeno />Ver perfil completo</Link></div></div>
    {a.dadosSuficientes ? <ResultadoBento rotulo="Critérios do professor selecionado" recomenda={a.recomenda} didatica={a.didatica} total={a.totalAvaliacoes} criterios={[
      {rotulo:"Dificuldade",valor:rotulos[a.dificuldade],legenda:"Resposta mais frequente"},
      {rotulo:"Chamada",valor:a.chamada === "CONFLITANTE" ? "Conflitante" : a.chamada ? "Faz chamada" : "Não faz chamada",legenda:"Maioria das respostas"},
      {rotulo:"Material",valor:a.disponibilizaMaterial === "CONFLITANTE" ? "Conflitante" : !a.disponibilizaMaterial ? "Não disponibiliza" : a.qualidadeMaterial ? rotulos[a.qualidadeMaterial] : "Disponibiliza",legenda:"Disponibilidade e qualidade"},
    ]} /> : <p className="state-box">{a.totalAvaliacoes === 0 ? "Ainda não há avaliações. Isso não significa uma avaliação negativa." : "Dados insuficientes: são necessárias pelo menos três avaliações para exibir os critérios."}</p>}
    {erro ? <p role="alert">Não foi possível carregar os comentários. Recarregue a página para tentar novamente.</p> : comentarios ? <SecaoComentarios comentarios={comentarios} /> : <p role="status">Carregando comentários…</p>}
  </section>;
}
