"use client";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import { EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { ApiError } from "@/lib/services/http-error";
import { listarIdentidades, consultarPrevia, decidirIdentidade, historicoIdentidade } from "@/lib/services/identidades";
import type { EstadoIdentidade, PendenciaIdentidade, PreviaIdentidade, DecisaoIdentidade } from "@/lib/services/identidades";
const rotulos: Record<EstadoIdentidade, string> = { PENDENTE: "Aguardando revisão", CONFIRMADA: "Aguardando aplicação", SEPARADA: "Mantidas separadas", APLICADA: "Aplicadas" };
const motivos: Record<string, string> = { HOMONIMOS: "Múltiplos perfis institucionais com o mesmo nome", ASSOCIACAO_LOCAL_REVISADA: "Associação local revisada; sem escolher um identificador institucional", ASSOCIACAO_LOCAL: "Associação por nome completo e unidade; sem confirmação institucional", PERFIL_AUSENTE: "Perfil não encontrado na busca pública", CONSULTA_INCONCLUSIVA: "Consulta institucional indisponível", DISCIPLINA_NAO_CONFIRMADA: "Disciplina ou semestre não confirmado no perfil", CONFLITO_INSTITUCIONAL: "Identificador em conflito", COMPATIVEL: "Correspondência institucional compatível", APLICACAO_BLOQUEADA: "Aplicação bloqueada; conferir colisões ou conflito institucional" };
const mensagem = (e: unknown) => e instanceof Error ? e.message : "Não foi possível concluir a operação.";

function Detalhe({ item, concluido, negar }: { item: PendenciaIdentidade; concluido: (mensagem: string) => void; negar: (e: unknown) => void }) {
  const [perfil, setPerfil] = useState("");
  const [justificativa, setJustificativa] = useState("");
  const [previa, setPrevia] = useState<PreviaIdentidade | null>(null);
  const [historico, setHistorico] = useState<DecisaoIdentidade[]>([]);
  const [erro, setErro] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const decisao = useRef<AbortController | null>(null);
  useEffect(() => () => decisao.current?.abort(), []);
  useEffect(() => { const c = new AbortController(); void historicoIdentidade(item.id, c.signal).then(v => { if (!c.signal.aborted) setHistorico(v); }).catch(e => { if (!c.signal.aborted) { if (e instanceof ApiError && [401,403].includes(e.status)) negar(e); else setErro(mensagem(e)); } }); return () => c.abort(); }, [item.id, negar]);
  useEffect(() => { if (!perfil) return; const c = new AbortController(); void consultarPrevia(item.id, perfil, c.signal).then(v => { if (!c.signal.aborted) setPrevia(v); }).catch(e => { if (!c.signal.aborted) { if (e instanceof ApiError && [401,403].includes(e.status)) negar(e); else setErro(mensagem(e)); } }); return () => c.abort(); }, [item.id, perfil, negar]);
  async function decidir(acao: "CONFIRMAR" | "SEPARAR") {
    decisao.current?.abort();
    const c = new AbortController();
    decisao.current = c;
    setOcupado(true); setErro("");
    try { await decidirIdentidade(item, acao, justificativa.trim(), acao === "CONFIRMAR" ? perfil : undefined, c.signal); if (!c.signal.aborted) concluido(acao === "CONFIRMAR" ? "Associação confirmada e aguardando aplicação operacional." : "Registros mantidos separados para esta ocorrência."); }
    catch(e) { if (!c.signal.aborted) { if (e instanceof ApiError && [401,403].includes(e.status)) negar(e); else setErro(mensagem(e)); } }
    finally { if (!c.signal.aborted) setOcupado(false); }
  }
  return <section aria-label={`Análise de ${item.nome}`} className="rounded-xl border border-foreground/20 p-4">
    <h2 className="text-xl font-semibold break-words">{item.nome}</h2>
    <p>{item.disciplina} · turma {item.turma} · {item.periodo} · unidade {item.unidade}</p>
    <p className="mt-2">{motivos[item.motivo] ?? "Pendência de identidade"}</p>
    <p className="mt-2">Estado: {rotulos[item.estado]}</p>
    <Link className="mt-3 inline-block underline" href={`/professores/${item.professor_id}`}>Consultar registro atual</Link>
    <fieldset disabled={ocupado || item.estado !== "PENDENTE"} className="mt-4 space-y-3"><legend>Perfis institucionais candidatos</legend>
      {!item.candidatos.length && <p>Nenhum candidato verificável. Mantenha pendente para nova consulta ou confirme que os registros devem permanecer separados.</p>}
      {item.candidatos.map(c => <div key={c.identificador} className="rounded-lg border border-foreground/15 p-3 break-words"><label className="flex min-h-11 items-center gap-3"><input type="radio" name={`perfil-${item.id}`} value={c.identificador} checked={perfil === c.identificador} onChange={() => { setPerfil(c.identificador); setPrevia(null); setErro(""); }} />{c.nome}</label><a className="underline" href={`https://sigaa.unb.br/sigaa/public/docente/disciplinas.jsf?siape=${c.identificador}`} target="_blank" rel="noreferrer">Ver disciplinas no SIGAA</a><p>{c.compativel ? "Disciplina e semestre conferidos na coleta." : "Disciplina ou semestre não confirmado; confira a evidência antes de decidir."}</p></div>)}
    </fieldset>
    {perfil && !previa && !erro && <p role="status">Conferindo a prévia…</p>}
    {previa && <div className="mt-4 rounded-lg border border-foreground/20 p-3"><h3 className="font-semibold">Prévia da aplicação</h3><p>{previa.uniao_necessaria ? `${previa.turmas ?? 0} turmas e ${previa.avaliacoes ?? 0} avaliações do registro seriam vinculadas ao destino.` : "Não há união com outro registro neste momento."}</p><p>{previa.colisoes} colisões de avaliações.</p><p>A aplicação revalida o grupo inteiro. A prévia não garante ausência de conflitos futuros.</p></div>}
    {item.estado === "PENDENTE" && <div className="mt-4 space-y-3"><label className="block">Justificativa da decisão<textarea className="mt-2 block w-full rounded-lg border border-foreground/30 bg-background p-3" maxLength={500} value={justificativa} onChange={e => setJustificativa(e.target.value)} disabled={ocupado} /></label><div className="flex flex-wrap gap-3"><button className="button min-h-11 disabled:opacity-50" disabled={ocupado || !justificativa.trim() || !perfil || !previa || previa.bloqueada} onClick={() => void decidir("CONFIRMAR")}>Confirmar associação</button><button className="button min-h-11 disabled:opacity-50" disabled={ocupado || !justificativa.trim()} onClick={() => void decidir("SEPARAR")}>Manter separados</button></div><p>Para deixar pendente, basta não decidir. A confirmação não executa união de dados nesta tela.</p></div>}
    {erro && <p role="alert" className="mt-3">{erro}</p>}
    <h3 className="mt-5 font-semibold">Histórico de decisões</h3>{historico.length ? <ul>{historico.map(d => <li key={d.id} className="mt-2 break-words">{d.acao === "CONFIRMAR" ? "Associação confirmada" : "Mantidas separadas"} — {d.justificativa} · responsável {d.usuario_id} · {new Date(d.created_at).toLocaleString("pt-BR")}</li>)}</ul> : <p>Nenhuma decisão humana registrada.</p>}
  </section>;
}

export default function FilaIdentidades() {
  const [estado, setEstado] = useState<EstadoIdentidade>("PENDENTE");
  const [offset, setOffset] = useState(0);
  const [itens, setItens] = useState<PendenciaIdentidade[]>([]);
  const [selecionado, setSelecionado] = useState<PendenciaIdentidade | null>(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState("");
  const [acesso, setAcesso] = useState(false);
  const [recarga, setRecarga] = useState(0);
  const [aviso, setAviso] = useState("");
  // Stable callback clears private content immediately on permission/session loss.
  const [negar] = useState(() => (e: unknown) => { setItens([]); setSelecionado(null); setAcesso(true); setErro(mensagem(e)); });
  useEffect(() => { const c = new AbortController(); void listarIdentidades(estado, offset, c.signal).then(v => { if (!c.signal.aborted) { setItens(v); setCarregando(false); } }).catch(e => { if (!c.signal.aborted) { setCarregando(false); if (e instanceof ApiError && [401,403].includes(e.status)) negar(e); else setErro(mensagem(e)); } }); return () => c.abort(); }, [estado, offset, recarga, negar]);
  useEffect(() => {
    const limpar = () => { setItens([]); setSelecionado(null); setCarregando(true); setErro(""); setAviso(""); setAcesso(false); setRecarga(x => x + 1); };
    window.addEventListener(EVENTO_SESSAO_ALTERADA, limpar);
    return () => window.removeEventListener(EVENTO_SESSAO_ALTERADA, limpar);
  }, []);
  function atualizar() { setItens([]); setSelecionado(null); setCarregando(true); setErro(""); setAcesso(false); setRecarga(x => x+1); }
  return <div className="space-y-5">
    <div className="flex flex-wrap gap-3"><label>Estado<select className="ml-2 rounded border border-foreground/30 bg-background p-2" value={estado} onChange={e => { setEstado(e.target.value as EstadoIdentidade); setOffset(0); atualizar(); }}>{Object.entries(rotulos).map(([v,r]) => <option value={v} key={v}>{r}</option>)}</select></label><button className="button min-h-11" onClick={atualizar}>Atualizar fila</button></div>
    {aviso && <p role="status">{aviso}</p>}{erro && <p role="alert">{erro}</p>}
    {acesso ? <p>A revisão exige uma conta confirmada com permissão específica de identidades. <Link className="underline" href="/login">Acessar conta</Link></p> : carregando ? <p role="status">Carregando identidades…</p> : <>
      {!itens.length && !erro && <p>Nenhuma ocorrência neste estado.</p>}
      <ul className="space-y-2">{itens.map(i => <li key={i.id}><button disabled={selecionado?.id === i.id} className="min-h-11 w-full rounded-lg border border-foreground/20 p-3 text-left break-words focus-visible:outline-2 focus-visible:outline-accent" onClick={() => setSelecionado(i)}>{i.nome} · {i.disciplina} · {i.periodo} · turma {i.turma}</button></li>)}</ul>
      <nav className="flex gap-3" aria-label="Páginas de identidades"><button className="button min-h-11 disabled:opacity-50" disabled={offset === 0} onClick={() => { setOffset(x => Math.max(0,x-50)); atualizar(); }}>Anterior</button><button className="button min-h-11 disabled:opacity-50" disabled={itens.length < 50} onClick={() => { setOffset(x => x+50); atualizar(); }}>Próxima</button></nav>
      {selecionado && <Detalhe key={selecionado.id} item={selecionado} negar={negar} concluido={m => { atualizar(); setAviso(m); }} />}
    </>}
  </div>;
}
