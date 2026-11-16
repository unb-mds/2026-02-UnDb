"use client";
import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/lib/services/api-client";
import { EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { categorias, type Solicitacao } from "@/lib/services/solicitacoes";

type Resumo = Pick<Solicitacao, "protocolo" | "categoria" | "recebido_em">;
export default function FilaAtendimento() {
  const [fila,setFila] = useState<Resumo[]>([]);
  const [item,setItem] = useState<Solicitacao | null>(null);
  const [responder,setResponder] = useState(false);
  const [autorizado,setAutorizado] = useState(false);
  const [erro,setErro] = useState("");
  const [offset,setOffset] = useState(0);
  const [ocupado,setOcupado] = useState(false);
  const geracao = useRef(0);
  useEffect(() => {
    let vivo = true;
    const controller = new AbortController();
    async function carregar() {
      setItem(null); setFila([]); setAutorizado(false); setResponder(false);
      try {
        const p = await apiClient.request<{responder:boolean}>("/api/atendimento/permissao", {}, {cache:"no-store", signal:controller.signal});
        const r = await apiClient.request<Resumo[]>("/api/atendimento", {offset:String(offset)}, {cache:"no-store", signal:controller.signal});
        if (vivo) {setResponder(p.responder); setFila(r); setAutorizado(true); setErro("");}
      } catch(e) {if(vivo) setErro(e instanceof Error ? e.message : "Falha ao carregar.");}
    }
    void carregar();
    const limpar = () => {vivo=false; ++geracao.current; controller.abort(); setItem(null); setFila([]); setAutorizado(false); setResponder(false);};
    window.addEventListener(EVENTO_SESSAO_ALTERADA,limpar);
    return () => {limpar(); window.removeEventListener(EVENTO_SESSAO_ALTERADA,limpar);};
  },[offset]);
  async function abrir(protocolo:string) {
    const versao=++geracao.current;
    setOcupado(true); setItem(null);
    try {const r=await apiClient.request<Solicitacao>(`/api/atendimento/${protocolo}`, {}, {cache:"no-store"}); if(versao===geracao.current) setItem(r);}
    catch(e) {setErro(e instanceof Error ? e.message : "Falha ao consultar.");} finally {setOcupado(false);}
  }
  async function atender(e:React.FormEvent<HTMLFormElement>) {
    e.preventDefault(); if(!item) return; setOcupado(true); const form=e.currentTarget;
    const versao=++geracao.current;
    try {const r=await apiClient.post<Solicitacao,object>(`/api/atendimento/${item.protocolo}/eventos`,Object.fromEntries(new FormData(form))); if(versao===geracao.current) {setItem(r); form.reset(); setErro("");}}
    catch(e) {setErro(e instanceof Error ? e.message : "Falha ao responder.");} finally {setOcupado(false);}
  }
  return <div className="space-y-5">
    {erro && <p role="alert">{erro} <Link href="/login">Acessar conta</Link></p>}
    {autorizado && <><p>{responder ? "Permissão de atendimento" : "Somente leitura"}</p><div className="flex flex-wrap gap-2">{fila.map(i => <button disabled={ocupado} className="button" key={i.protocolo} onClick={() => void abrir(i.protocolo)}>{categorias[i.categoria as keyof typeof categorias]} · {new Date(i.recebido_em).toLocaleString("pt-BR")} · {i.protocolo}</button>)}</div>
      {!fila.length && <p>Nenhuma solicitação nesta página.</p>}
      <nav className="flex gap-3" aria-label="Páginas do atendimento"><button className="button" disabled={!offset || ocupado} onClick={() => setOffset(Math.max(0,offset-50))}>Anterior</button><button className="button" disabled={fila.length<50 || ocupado} onClick={() => setOffset(offset+50)}>Próxima</button></nav>
    </>}
    {autorizado && item && <article className="space-y-4"><h2 className="section-title">Pedido {item.protocolo}</h2><p className="break-all">Alvo: {item.alvo}</p><p className="whitespace-pre-wrap">{item.descricao}</p><p className="whitespace-pre-wrap">{item.evidencia}</p>
      <p>Analise cada ocorrência fundamentada independentemente de volume. Confirme a legitimidade proporcionalmente antes de executar direitos. Não identifique avaliadores na resposta. Discordância não provoca remoção automática.</p>
      <p>Encaminhe texto à <Link href="/moderacao">moderação</Link> e catálogo à <Link href="/moderacao/identidades">reconciliação de identidades</Link>. Notas e direitos exigem análise própria. Nenhuma ação aqui altera avaliações.</p>
      {item.historico.map((e,i) => <div key={i} className="rounded-lg border border-(--border) p-3"><p>{e.tipo} · {new Date(e.data).toLocaleString("pt-BR")} · {e.responsavel_id ?? "Solicitante"}</p><p className="whitespace-pre-wrap">{e.texto}</p></div>)}
      {responder && <form onSubmit={atender} className="space-y-3"><label className="block">Registro<select name="tipo" className="button"><option value="TRIAGEM">Triagem interna</option><option value="PROVIDENCIA">Providência interna</option><option value="RESPOSTA">Resposta visível ao solicitante</option></select></label><label className="block">Texto<textarea name="texto" className="w-full rounded-lg border border-(--border) bg-(--panel) p-3" rows={5} required maxLength={4000} /></label><p>Na resposta, explique a decisão e como pedir revisão pelo acompanhamento.</p><button disabled={ocupado} className="button primary">Registrar</button></form>}
    </article>}
  </div>;
}
