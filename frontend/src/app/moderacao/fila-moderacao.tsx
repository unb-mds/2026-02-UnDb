"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";
import { mensagemModeracao, rotulosEstado, statusModeracao } from "@/lib/moderacao";
import { consultarComentario, executarAcao, listarFila } from "@/lib/services/moderacao";
import type { AcaoModeracaoInput, ComentarioModeracao, EstadoFila } from "@/lib/types/moderacao";
import DetalheModeracao from "./detalhe-moderacao";

type Fila = { tipo: "carregando" } | { tipo: "pronta"; itens: ComentarioModeracao[] }
  | { tipo: "erro"; mensagem: string } | { tipo: "acesso"; mensagem: string; login: boolean };
type Detalhe = { tipo: "carregando"; id: string } | { tipo: "pronto"; comentario: ComentarioModeracao }
  | { tipo: "erro"; id: string; mensagem: string } | null;
const filtros: { valor: EstadoFila | ""; rotulo: string }[] = [
  { valor: "", rotulo: "Todos os estados" }, { valor: "PENDENTE", rotulo: "Pendentes de aprovação" },
  { valor: "PUBLICADO", rotulo: "Publicados com denúncias" }, { valor: "SUSPENSO", rotulo: "Suspensos" },
];
const botao = "rounded-lg border border-foreground/20 px-4 py-2.5 text-sm font-medium text-accent hover:bg-accent/5 disabled:opacity-50";

export default function FilaModeracao() {
  const [filtro, setFiltro] = useState<EstadoFila | "">("");
  const [recarga, setRecarga] = useState(0);
  const [fila, setFila] = useState<Fila>({ tipo: "carregando" });
  const [detalhe, setDetalhe] = useState<Detalhe>(null);
  const [executando, setExecutando] = useState(false);
  const [aviso, setAviso] = useState<{ tipo: "erro" | "sucesso"; mensagem: string } | null>(null);
  const [impedidos, setImpedidos] = useState<Set<string>>(() => new Set());
  const sequencia = useRef(0);
  const consultaFila = useRef<AbortController | null>(null);
  const consultaDetalhe = useRef<AbortController | null>(null);

  const negarAcesso = useCallback((erro: unknown) => {
    sequencia.current += 1;
    consultaFila.current?.abort();
    consultaDetalhe.current?.abort();
    setDetalhe(null);
    setAviso(null);
    setExecutando(false);
    setImpedidos(new Set());
    setFila({ tipo: "acesso", mensagem: mensagemModeracao(erro, "consulta"), login: statusModeracao(erro) === 401 });
  }, []);

  useEffect(() => {
    const controlador = new AbortController();
    consultaFila.current = controlador;
    const atual = sequencia.current;
    void listarFila(filtro || undefined, controlador.signal).then((itens) => {
      if (!controlador.signal.aborted && atual === sequencia.current) setFila({ tipo: "pronta", itens });
    }).catch((erro: unknown) => {
      if (controlador.signal.aborted || atual !== sequencia.current) return;
      if ([401, 403].includes(statusModeracao(erro) ?? 0)) negarAcesso(erro);
      else setFila({ tipo: "erro", mensagem: mensagemModeracao(erro, "consulta") });
    });
    return () => { controlador.abort(); };
  }, [filtro, recarga, negarAcesso]);

  useEffect(() => () => {
    sequencia.current += 1;
    consultaFila.current?.abort();
    consultaDetalhe.current?.abort();
  }, []);

  function atualizar(limparAviso = true) {
    sequencia.current += 1;
    consultaFila.current?.abort();
    consultaDetalhe.current?.abort();
    setDetalhe(null);
    setFila({ tipo: "carregando" });
    if (limparAviso) setAviso(null);
    setRecarga((valor) => valor + 1);
  }

  async function selecionar(id: string) {
    consultaDetalhe.current?.abort();
    const controlador = new AbortController();
    consultaDetalhe.current = controlador;
    const atual = ++sequencia.current;
    setDetalhe({ tipo: "carregando", id });
    try {
      const comentario = await consultarComentario(id, controlador.signal);
      if (!controlador.signal.aborted && atual === sequencia.current) setDetalhe({ tipo: "pronto", comentario });
    } catch (erro) {
      if (controlador.signal.aborted || atual !== sequencia.current) return;
      if ([401, 403].includes(statusModeracao(erro) ?? 0)) negarAcesso(erro);
      else setDetalhe({ tipo: "erro", id, mensagem: mensagemModeracao(erro, "consulta") });
    }
  }

  async function decidir(id: string, dados: AcaoModeracaoInput) {
    const atual = sequencia.current;
    setExecutando(true);
    setAviso(null);
    try {
      const decisao = await executarAcao(id, dados);
      if (atual !== sequencia.current) return;
      setExecutando(false);
      setAviso({ tipo: "sucesso", mensagem: `Decisão registrada. Estado retornado: ${rotulosEstado[decisao.estado_posterior]}.` });
      atualizar(false);
    } catch (erro) {
      if (atual !== sequencia.current) return;
      setExecutando(false);
      if (statusModeracao(erro) === 401) { negarAcesso(erro); return; }
      if (statusModeracao(erro) === 403) setImpedidos((anteriores) => new Set([...anteriores, id]));
      setAviso({ tipo: "erro", mensagem: mensagemModeracao(erro, "acao") });
      // Não reutiliza dados anteriores a uma ação incerta, impedida ou concorrente.
      if (statusModeracao(erro) !== 422) atualizar(false);
    }
  }

  return (
    <>
      <div className="flex flex-wrap items-end gap-3">
        <label className="flex min-w-0 flex-1 flex-col gap-1 text-sm font-medium" htmlFor="estado-fila">Estado dos comentários
          <select id="estado-fila" value={filtro} disabled={executando} onChange={(evento) => {
            const valor = filtros.find((item) => item.valor === evento.target.value)?.valor;
            if (valor !== undefined) { setFiltro(valor); atualizar(); }
          }} className="rounded-lg border border-foreground/20 bg-background px-4 py-2.5 text-base">
            {filtros.map((item) => <option key={item.valor} value={item.valor}>{item.rotulo}</option>)}
          </select>
        </label>
        <button type="button" className={botao} disabled={executando} onClick={() => atualizar()}>Atualizar fila</button>
      </div>
      {aviso && <p role={aviso.tipo === "erro" ? "alert" : "status"} className="rounded-lg border border-foreground/20 bg-accent/5 p-4 text-sm">{aviso.mensagem}</p>}
      {fila.tipo === "carregando" && <p role="status">Carregando fila de moderação…</p>}
      {fila.tipo === "erro" && <div role="alert" className="rounded-lg border border-foreground/20 p-4"><p>{fila.mensagem}</p><button type="button" className={`${botao} mt-3`} onClick={() => atualizar()}>Tentar novamente</button></div>}
      {fila.tipo === "acesso" && <div role="alert" className="rounded-lg border border-foreground/20 p-4">
        <h2 className="font-semibold">{fila.login ? "Entre na sua conta" : "Acesso não permitido"}</h2><p className="mt-2">{fila.mensagem}</p>
        <Link href="/login" className="mt-3 inline-block text-accent underline underline-offset-4">Ir para entrar</Link>
        <p className="mt-2 text-sm text-foreground/70">Depois de entrar, volte à Moderação pelo menu.</p>
      </div>}
      {fila.tipo === "pronta" && (fila.itens.length === 0 ? <p role="status" className="rounded-xl border border-foreground/10 p-5">Nenhum comentário aguardando moderação neste filtro.</p> :
        <div className="grid min-w-0 items-start gap-6 lg:grid-cols-2">
          <section aria-label="Comentários na fila" className="min-w-0">
            <p className="mb-3 text-sm text-foreground/70">Selecione um comentário para analisar.</p>
            <ul className="space-y-3">{fila.itens.map((item) => <li key={item.id}>
              <button type="button" disabled={executando} aria-pressed={detalhe?.tipo === "pronto" && detalhe.comentario.id === item.id} onClick={() => void selecionar(item.id)}
                className="w-full min-w-0 rounded-xl border border-foreground/20 p-4 text-left hover:border-accent aria-pressed:border-accent aria-pressed:bg-accent/5 disabled:opacity-50">
                <span className="text-sm font-semibold text-accent">{item.estado === "PUBLICADO" ? "Publicado com denúncias" : rotulosEstado[item.estado]}</span>
                {item.estado === "PENDENTE" && item.substitui_id && <span className="mt-1 block text-sm text-foreground/70">Substituto em análise</span>}
                <span className="mt-2 block line-clamp-3 whitespace-pre-wrap [overflow-wrap:anywhere]">{item.texto ?? "Texto descartado"}</span>
                <span className="mt-3 block text-xs text-foreground/70 [overflow-wrap:anywhere]">Versão {item.id}</span>
              </button>
            </li>)}</ul>
          </section>
          <section aria-label="Análise do comentário" aria-busy={detalhe?.tipo === "carregando"} className="min-w-0 rounded-xl border border-foreground/20 p-5">
            {!detalhe && <p className="text-sm text-foreground/70">O conteúdo selecionado e suas ações aparecerão aqui.</p>}
            {detalhe?.tipo === "carregando" && <p role="status">Carregando comentário…</p>}
            {detalhe?.tipo === "erro" && <div role="alert"><p>{detalhe.mensagem}</p><button type="button" className={`${botao} mt-3`} onClick={() => void selecionar(detalhe.id)}>Tentar carregar comentário</button></div>}
            {detalhe?.tipo === "pronto" && <DetalheModeracao key={detalhe.comentario.id} comentario={detalhe.comentario} executando={executando} impedido={impedidos.has(detalhe.comentario.id)}
              aoDecidir={decidir} aoNegarAcesso={negarAcesso} />}
          </section>
        </div>)}
    </>
  );
}
