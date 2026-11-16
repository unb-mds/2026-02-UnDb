"use client";

import { useEffect, useState } from "react";
import { apiClient } from "@/lib/services/api-client";
import { categorias, type Recibo, type Solicitacao } from "@/lib/services/solicitacoes";

const campo = "w-full rounded-lg border border-(--border) bg-(--panel) p-3 text-foreground";
const mensagem = (e: unknown) => e instanceof Error ? e.message : "Não foi possível concluir.";

export default function CanalTitulares() {
  const [ativo, setAtivo] = useState(false);
  const [verificado, setVerificado] = useState(false);
  const [ocupado, setOcupado] = useState(false);
  const [erro, setErro] = useState("");
  const [recibo, setRecibo] = useState<Recibo | null>(null);
  const [item, setItem] = useState<Solicitacao | null>(null);
  const [protocolo, setProtocolo] = useState("");
  const [chave, setChave] = useState("");
  useEffect(() => {
    const controller = new AbortController();
    apiClient.request<{ ativo: boolean }>("/api/solicitacoes/disponibilidade", {}, { cache: "no-store", signal: controller.signal })
      .then(r => { setAtivo(r.ativo); setVerificado(true); })
      .catch(() => { if (!controller.signal.aborted) setVerificado(true); });
    return () => controller.abort();
  }, []);
  async function criar(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault(); setOcupado(true); setErro("");
    const form = e.currentTarget;
    const dados = Object.fromEntries(new FormData(form));
    try {
      const r = await apiClient.post<Recibo, typeof dados>("/api/solicitacoes", dados);
      setRecibo(r); setProtocolo(r.protocolo); setChave(r.chave); form.reset();
    } catch (e) { setErro(mensagem(e)); } finally { setOcupado(false); }
  }
  async function consultar(e: React.FormEvent) {
    e.preventDefault(); setOcupado(true); setErro(""); setItem(null);
    try { setItem(await apiClient.post<Solicitacao, object>("/api/solicitacoes/consultar", { protocolo, chave })); }
    catch (e) { setErro(mensagem(e)); } finally { setOcupado(false); }
  }
  async function complementar(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault(); setOcupado(true); setErro("");
    const form = e.currentTarget;
    try {
      setItem(await apiClient.post<Solicitacao, object>("/api/solicitacoes/complementos", { protocolo, chave, texto: new FormData(form).get("texto") })); form.reset();
    } catch (e) { setErro(mensagem(e)); } finally { setOcupado(false); }
  }
  return <div className="grid gap-10 lg:grid-cols-2">
    <section className="space-y-4"><h2 className="section-title">Nova solicitação</h2>
      {!verificado ? <p role="status">Conferindo disponibilidade…</p> : !ativo ? <p role="status">O recebimento ainda não está disponível. O acompanhamento de protocolos existentes continua abaixo.</p> :
      <form onSubmit={criar} className="space-y-4">
        <label className="block">Categoria<select name="categoria" className={campo} required>{Object.entries(categorias).map(([k,v]) => <option key={k} value={k}>{v}</option>)}</select></label>
        <label className="block">Página ou identificador do alvo<input name="alvo" className={campo} required maxLength={1000} /></label>
        <label className="block">Descreva o pedido<textarea name="descricao" className={campo} required minLength={10} maxLength={4000} rows={5} /></label>
        <label className="block">Evidência ou contexto mínimo<textarea name="evidencia" className={campo} required maxLength={4000} rows={4} /></label>
        <p className="text-sm">Não envie senhas, documentos pessoais ou identidade de avaliadores. Não há envio de anexos. Se precisar comprovar identidade, aguarde orientação proporcional da equipe pelo acompanhamento.</p>
        <button className="button primary" disabled={ocupado}>Enviar solicitação</button>
      </form>}
      {recibo && <div role="status" className="space-y-2 rounded-lg border border-(--border) p-4"><h3>Solicitação recebida</h3><p>Recebida em {new Date(recibo.recebido_em).toLocaleString("pt-BR")}</p><p>Protocolo: <code className="break-all">{recibo.protocolo}</code></p><p>Chave secreta: <code className="break-all">{recibo.chave}</code></p><p>Guarde estes dois valores em local privado. Quem possui a chave pode ler o pedido e as respostas. Ela não será mostrada novamente nem enviada por e-mail.</p></div>}
    </section>
    <section className="space-y-4"><h2 className="section-title">Acompanhar ou pedir revisão</h2>
      <form onSubmit={consultar} className="space-y-4">
        <label className="block">Protocolo<input name="protocolo" disabled={ocupado} className={campo} value={protocolo} onChange={e => {setProtocolo(e.target.value); setItem(null);}} required autoComplete="off" /></label>
        <label className="block">Chave secreta<input name="chave" disabled={ocupado} className={campo} type="password" value={chave} onChange={e => {setChave(e.target.value); setItem(null);}} required autoComplete="off" /></label>
        <button className="button" disabled={ocupado}>Consultar</button>
      </form>
      {item && <article className="space-y-4"><h3>Solicitação {item.protocolo}</h3><p>{item.alvo}</p><p className="whitespace-pre-wrap">{item.descricao}</p><p className="whitespace-pre-wrap">{item.evidencia}</p>
        {!item.historico.length && <p>Aguardando análise da equipe.</p>}
        {item.historico.map((e,i) => <div key={i} className="border-l-2 border-(--border) pl-4"><p>{e.tipo === "RESPOSTA" ? "Resposta da equipe" : "Complemento do pedido"} · {new Date(e.data).toLocaleString("pt-BR")}</p><p className="whitespace-pre-wrap">{e.texto}</p></div>)}
        <form onSubmit={complementar} className="space-y-3"><label className="block">Complemento ou pedido de revisão<textarea name="texto" className={campo} maxLength={4000} required rows={4} /></label><button className="button" disabled={ocupado}>Enviar complemento</button></form>
      </article>}
    </section>
    {erro && <p role="alert">{erro}</p>}
  </div>;
}
