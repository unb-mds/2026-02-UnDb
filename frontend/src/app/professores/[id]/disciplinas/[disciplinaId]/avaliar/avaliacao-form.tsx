"use client";

import Link from "next/link";
import CriteriosAvaliacao from "@/components/criterios-avaliacao";
import MeusComentarios from "@/components/meus-comentarios";
import { useCallback, useEffect, useRef, useState, type FormEvent } from "react";
import { criarEntradaAvaliacao, mensagemErroAvaliacao } from "@/lib/avaliacao-formulario";
import { consultarSessao, EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { enviarAvaliacaoComComentario } from "@/lib/services/avaliacoes";
import { consultarMeusComentarios, retirarComentario } from "@/lib/services/comentarios";
import { ApiError } from "@/lib/services/http-error";
import type { ComentarioDoAutor } from "@/lib/types/comentario";

type Consulta = { estado: "carregando" | "negado" | "erro" | "pronto"; itens: ComentarioDoAutor[] };

export default function AvaliacaoForm({ professorId, disciplinaId, retornoHref }: {
  professorId: string; disciplinaId: string; retornoHref: string;
}) {
  const enviandoRef = useRef(false);
  const geracaoSessao = useRef(0);
  const consultaRef = useRef<AbortController | null>(null);
  const escritaRef = useRef<AbortController | null>(null);
  const [enviando, setEnviando] = useState(false);
  const [erro, setErro] = useState<string | null>(null);
  const [precisaEntrar, setPrecisaEntrar] = useState(false);
  const [sucesso, setSucesso] = useState(false);
  const [avisoComentario, setAvisoComentario] = useState<string | null>(null);
  const [texto, setTexto] = useState("");
  const [consulta, setConsulta] = useState<Consulta>({ estado: "carregando", itens: [] });
  const [confirmarRetirada, setConfirmarRetirada] = useState<string | null>(null);
  const [resultadoRetirada, setResultadoRetirada] = useState<string | null>(null);

  const carregar = useCallback(async () => {
    consultaRef.current?.abort();
    const controlador = new AbortController();
    consultaRef.current = controlador;
    try {
      const itens = await consultarMeusComentarios(controlador.signal, { professorId, disciplinaId });
      if (!controlador.signal.aborted) setConsulta({ estado: "pronto", itens });
    } catch (falha) {
      if (controlador.signal.aborted) return;
      const negado = falha instanceof ApiError && [401, 403].includes(falha.status);
      setConsulta({ estado: negado ? "negado" : "erro", itens: [] });
    }
  }, [professorId, disciplinaId]);

  useEffect(() => {
    const limpar = () => {
      ++geracaoSessao.current;
      consultaRef.current?.abort();
      escritaRef.current?.abort();
      enviandoRef.current = false;
      setEnviando(false);
      setConsulta({ estado: "carregando", itens: [] });
      setConfirmarRetirada(null);
      setResultadoRetirada(null);
      setSucesso(false);
      setAvisoComentario(null);
      setErro(null);
      setPrecisaEntrar(false);
    };
    const atualizarSessao = () => { limpar(); void carregar(); };
    const visibilidade = () => {
      if (document.visibilityState === "hidden") limpar();
      else atualizarSessao();
    };
    // Adia a consulta inicial até após o commit e cancela a montagem descartada pelo StrictMode.
    const inicio = window.setTimeout(() => void carregar(), 0);
    window.addEventListener(EVENTO_SESSAO_ALTERADA, atualizarSessao);
    window.addEventListener("focus", atualizarSessao);
    document.addEventListener("visibilitychange", visibilidade);
    const invalidar = () => { ++geracaoSessao.current; };
    return () => {
      window.clearTimeout(inicio);
      invalidar();
      consultaRef.current?.abort();
      escritaRef.current?.abort();
      window.removeEventListener(EVENTO_SESSAO_ALTERADA, atualizarSessao);
      window.removeEventListener("focus", atualizarSessao);
      document.removeEventListener("visibilitychange", visibilidade);
    };
  }, [carregar]);

  async function enviar(evento: FormEvent<HTMLFormElement>) {
    evento.preventDefault();
    if (enviandoRef.current) return;
    setErro(null); setSucesso(false); setAvisoComentario(null); setPrecisaEntrar(false);
    let dados;
    try {
      dados = criarEntradaAvaliacao(new FormData(evento.currentTarget), professorId, disciplinaId);
      if (texto !== "") dados.comentario = texto;
    } catch (falha) {
      setErro(falha instanceof Error ? falha.message : "Revise as opções da avaliação.");
      return;
    }
    enviandoRef.current = true; setEnviando(true);
    const geracao = geracaoSessao.current;
    const controlador = new AbortController();
    escritaRef.current = controlador;
    try {
      const sessao = await consultarSessao();
      if (controlador.signal.aborted) return;
      if (!sessao.autenticado) throw new ApiError("É necessário autenticar-se para registrar uma avaliação.", 401);
      const resposta = await enviarAvaliacaoComComentario(dados, controlador.signal);
      if (geracao !== geracaoSessao.current || controlador.signal.aborted) return;
      setSucesso(true);
      setAvisoComentario(resposta.comentario_erro
        ? "Seus critérios foram salvos, mas o comentário não foi enviado: informe de 1 a 500 caracteres, sem contar espaços no início e no fim. O texto anterior foi mantido."
        : dados.comentario ? "Seu novo texto foi enviado para aprovação humana. Ele ainda não está público; a versão anterior mantém seu estado." : null);
      if (!resposta.comentario_erro && dados.comentario) setTexto("");
      setConsulta({ estado: "carregando", itens: [] });
      await carregar();
    } catch (falha) {
      if (geracao !== geracaoSessao.current || controlador.signal.aborted) return;
      setPrecisaEntrar(falha instanceof ApiError && falha.status === 401);
      setErro(mensagemErroAvaliacao(falha));
      if (falha instanceof ApiError && [401, 403].includes(falha.status)) {
        consultaRef.current?.abort(); setConsulta({ estado: "negado", itens: [] });
      }
    } finally {
      if (geracao === geracaoSessao.current) { enviandoRef.current = false; setEnviando(false); }
    }
  }

  async function retirar(id: string) {
    if (enviandoRef.current) return;
    enviandoRef.current = true; setEnviando(true); setResultadoRetirada(null);
    const geracao = geracaoSessao.current;
    const controlador = new AbortController(); escritaRef.current = controlador;
    try {
      await retirarComentario(id, controlador.signal);
      if (geracao !== geracaoSessao.current || controlador.signal.aborted) return;
      setConfirmarRetirada(null);
      setResultadoRetirada("Comentário retirado. Eventual substituto pendente também foi cancelado; seus critérios foram preservados.");
      await carregar();
    } catch {
      if (geracao !== geracaoSessao.current || controlador.signal.aborted) return;
      setResultadoRetirada("Não foi possível confirmar a retirada. Atualize seus comentários antes de tentar novamente.");
      await carregar();
    } finally {
      if (geracao === geracaoSessao.current) { enviandoRef.current = false; setEnviando(false); }
    }
  }

  return (
    <div className="flex min-w-0 flex-col gap-6">
      <form onSubmit={enviar} className="flex min-w-0 flex-col gap-6 rounded-xl border border-foreground/10 p-5" aria-busy={enviando}>
        <div className="flex flex-col items-start gap-3 rounded-lg bg-foreground/[0.03] p-4">
          <p className="text-sm text-foreground/70">Você pode entrar antes de preencher. Para enviar, é necessário ter uma sessão ativa e confirmar seu e-mail institucional.</p>
          <Link href={`/login?returnTo=${encodeURIComponent(retornoHref)}`} className="rounded-lg border border-foreground/20 px-4 py-2.5 text-sm font-medium text-accent">Entrar ou criar conta antes de avaliar</Link>
        </div>
        <CriteriosAvaliacao rotulosExplicitos destacarDidatica disabled={enviando} onChange={() => { setSucesso(false); setErro(null); }} />
        <label className="flex min-w-0 flex-col gap-2">
          <span className="font-semibold">Novo comentário ou substituto (opcional)</span>
          <textarea name="comentario" value={texto} disabled={enviando} rows={5} aria-describedby="orientacao-comentario" onChange={(e) => { setTexto(e.target.value); setSucesso(false); setAvisoComentario(null); }} className="w-full min-w-0 rounded-lg border border-foreground/20 bg-background p-3 text-base" />
          <span id="orientacao-comentario" className="text-sm text-foreground/70">De 1 a 500 caracteres após remover espaços nas extremidades. Críticas acadêmicas são permitidas; não publique ofensas, ameaças, discriminação, dados pessoais ou spam. Todo texto novo depende de aprovação humana. Deixe vazio para manter o comentário existente. Para retirar, use a ação explícita abaixo.</span>
        </label>
        <button type="submit" disabled={enviando} className="rounded-lg bg-accent px-4 py-2.5 font-medium text-on-accent disabled:opacity-60">{enviando ? "Enviando…" : "Enviar avaliação"}</button>
        <div aria-live="polite" aria-atomic="true">
          {sucesso && <p role="status" className="rounded-lg border border-green-600/30 p-4 text-sm">Avaliação registrada com sucesso. Se você já tinha uma avaliação para este professor nesta disciplina, ela foi substituída por este envio.</p>}
          {avisoComentario && <p role="status" className="mt-2 text-sm">{avisoComentario}</p>}
          {erro && <div role="alert" className="rounded-lg border border-red-600/30 p-4 text-sm"><p>{erro}</p>{precisaEntrar && <Link href={`/login?returnTo=${encodeURIComponent(retornoHref)}`} target="_blank" rel="noopener noreferrer" className="mt-2 inline-block text-accent underline">Entrar na conta (nova aba)</Link>}</div>}
        </div>
      </form>
      {consulta.estado === "carregando" && <p role="status">Carregando seus comentários…</p>}
      {consulta.estado === "pronto" && <MeusComentarios comentarios={consulta.itens} aoRetirar={setConfirmarRetirada} disabled={enviando} />}
      {consulta.estado === "erro" && <p role="alert">Não foi possível carregar seus comentários agora. <button type="button" onClick={() => void carregar()} className="text-accent underline">Tentar novamente</button></p>}
      {confirmarRetirada && consulta.estado === "pronto" && <div role="group" aria-label="Confirmar retirada" className="rounded-lg border border-foreground/20 p-4 text-sm">
        <p>A retirada remove o texto público e cancela eventual substituto pendente, preservando os critérios. Deseja continuar?</p>
        <button type="button" disabled={enviando} onClick={() => void retirar(confirmarRetirada)} className="mr-4 mt-3 text-accent underline">Confirmar retirada</button>
        <button type="button" disabled={enviando} onClick={() => setConfirmarRetirada(null)}>Cancelar retirada</button>
      </div>}
      {resultadoRetirada && <p role="status">{resultadoRetirada}</p>}
    </div>
  );
}
