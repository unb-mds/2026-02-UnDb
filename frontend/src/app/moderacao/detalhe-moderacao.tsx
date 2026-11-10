"use client";

import { useEffect, useState } from "react";
import { acoesParaEstado, rotulosAcao, rotulosEstado, rotulosMotivo, statusModeracao } from "@/lib/moderacao";
import { consultarComentario, consultarDecisoes, consultarDenuncias } from "@/lib/services/moderacao";
import type { AcaoModeracao, AcaoModeracaoInput, ComentarioModeracao, DecisaoModeracao, DenunciasDaVersao } from "@/lib/types/moderacao";

type Consulta<T> = { tipo: "carregando" } | { tipo: "pronta"; dados: T } | { tipo: "erro" };
type Props = {
  comentario: ComentarioModeracao;
  executando: boolean;
  impedido: boolean;
  aoDecidir: (id: string, dados: AcaoModeracaoInput) => Promise<void>;
  aoNegarAcesso: (erro: unknown) => void;
};
const campo = "w-full rounded-lg border border-foreground/20 bg-background px-4 py-3 text-base";
const formatarData = (valor: string) => new Date(valor).toLocaleString("pt-BR");

export default function DetalheModeracao({ comentario, executando, impedido, aoDecidir, aoNegarAcesso }: Props) {
  const [denuncias, setDenuncias] = useState<Consulta<DenunciasDaVersao>>({ tipo: "carregando" });
  const [decisoes, setDecisoes] = useState<Consulta<DecisaoModeracao[]>>({ tipo: "carregando" });
  const [anterior, setAnterior] = useState<Consulta<ComentarioModeracao>>({ tipo: "carregando" });
  const [recarga, setRecarga] = useState(0);
  const [acao, setAcao] = useState<AcaoModeracao | "">("");
  const [motivo, setMotivo] = useState("");
  const [erroFormulario, setErroFormulario] = useState("");

  useEffect(() => {
    const controlador = new AbortController();
    function falhou<T>(atualizar: (estado: Consulta<T>) => void) {
      return (erro: unknown) => {
        if (controlador.signal.aborted) return;
        if ([401, 403].includes(statusModeracao(erro) ?? 0)) aoNegarAcesso(erro);
        else atualizar({ tipo: "erro" });
      };
    }
    if (comentario.estado !== "PENDENTE") {
      void consultarDenuncias(comentario.id, controlador.signal).then((dados) => {
        if (!controlador.signal.aborted) setDenuncias({ tipo: "pronta", dados });
      }).catch(falhou(setDenuncias));
    }
    void consultarDecisoes(comentario.id, controlador.signal).then((dados) => {
      if (!controlador.signal.aborted) setDecisoes({ tipo: "pronta", dados });
    }).catch(falhou(setDecisoes));
    if (comentario.substitui_id) {
      void consultarComentario(comentario.substitui_id, controlador.signal).then((dados) => {
        if (!controlador.signal.aborted) setAnterior({ tipo: "pronta", dados });
      }).catch(falhou(setAnterior));
    }
    return () => controlador.abort();
  }, [comentario.id, comentario.estado, comentario.substitui_id, recarga, aoNegarAcesso]);

  const temDenuncias = denuncias.tipo === "pronta" && (denuncias.dados.contas_distintas > 0 || denuncias.dados.total_visitantes > 0);
  const acoes = comentario.estado === "PENDENTE" || denuncias.tipo === "pronta"
    ? acoesParaEstado(comentario.estado, temDenuncias) : [];

  return (
    <div className="space-y-5 [overflow-wrap:anywhere]">
      <div><h2 className="text-lg font-semibold">Analisar comentário</h2>
        <p className="mt-1 text-sm text-accent">{rotulosEstado[comentario.estado]}</p>
        <p className="mt-2 text-xs text-foreground/70">Versão <span className="font-mono">{comentario.id}</span></p>
        <p className="text-xs text-foreground/70">Enviado em {formatarData(comentario.created_at)}</p>
      </div>
      <p className="whitespace-pre-wrap rounded-lg bg-foreground/[0.03] p-4">{comentario.texto ?? "O texto desta versão já foi descartado."}</p>
      <div className="text-sm"><h3 className="font-medium">Autor — informação interna</h3><p>{comentario.autor.nome}</p><p>{comentario.autor.email}</p></div>
      {comentario.substitui_id && <details className="rounded-lg border border-foreground/10 p-3">
        <summary className="cursor-pointer text-sm font-medium text-accent">Versão anterior</summary>
        <p className="mt-2 text-xs text-foreground/70">{comentario.substitui_id}</p>
        {anterior.tipo === "carregando" && <p role="status">Carregando versão anterior…</p>}
        {anterior.tipo === "erro" && <p role="alert">Não foi possível consultar a versão anterior.</p>}
        {anterior.tipo === "pronta" && <><p className="mt-2 text-sm">{rotulosEstado[anterior.dados.estado]}</p><p className="mt-2 whitespace-pre-wrap">{anterior.dados.texto ?? "Texto anterior descartado."}</p></>}
      </details>}
      <section aria-label="Denúncias da versão" className="space-y-3 border-t border-foreground/10 pt-4">
        <h3 className="font-medium">Denúncias abertas desta versão</h3>
        {comentario.estado === "PENDENTE" ? <p className="text-sm text-foreground/70">Este texto aguarda aprovação prévia. Denúncias da versão anterior não são transferidas para ele.</p> : <>
          {denuncias.tipo === "carregando" && <p role="status">Carregando denúncias…</p>}
          {denuncias.tipo === "erro" && <p role="alert" className="text-sm">Não foi possível consultar as denúncias.</p>}
          {denuncias.tipo === "pronta" && <>
            <p className="text-sm">Contas distintas: {denuncias.dados.contas_distintas} · Relatos de visitantes: {denuncias.dados.total_visitantes}</p>
            {!temDenuncias && <p className="text-sm text-foreground/70">Nenhuma denúncia aberta para esta versão.</p>}
            <details><summary className="cursor-pointer text-sm text-accent">Denúncias de contas autenticadas</summary>
              <ul className="mt-2 space-y-3 text-sm">{denuncias.dados.autenticadas.map((item) => <li key={item.id} className="border-l border-foreground/20 pl-3">
                <p className="font-medium">{rotulosMotivo[item.motivo]}</p><p>{item.denunciante?.nome}</p><p>{item.denunciante?.email}</p><p className="text-xs text-foreground/70">{formatarData(item.created_at)}</p>
              </li>)}</ul>
            </details>
            <details><summary className="cursor-pointer text-sm text-accent">Denúncias de visitantes</summary>
              <p className="mt-2 text-xs text-foreground/70">Relatos sem identidade cadastrada; não representam pessoas distintas.</p>
              <ul className="mt-2 space-y-2 text-sm">{denuncias.dados.visitantes.map((item) => <li key={item.id}>{rotulosMotivo[item.motivo]} · {formatarData(item.created_at)}</li>)}</ul>
            </details>
          </>}
        </>}
      </section>
      <section aria-label="Decisões disponíveis" className="border-t border-foreground/10 pt-4">
        <h3 className="font-medium">Decisões disponíveis</h3>
        {decisoes.tipo === "carregando" && <p role="status" className="mt-2 text-sm">Carregando decisões…</p>}
        {decisoes.tipo === "erro" && <p role="alert" className="mt-2 text-sm">Não foi possível consultar as decisões.</p>}
        {decisoes.tipo === "pronta" && (decisoes.dados.length === 0 ? <p className="mt-2 text-sm text-foreground/70">Nenhuma decisão disponível para esta versão.</p> :
          <ul className="mt-2 space-y-3 text-sm">{decisoes.dados.map((item) => <li key={item.id}><p className="font-medium">{rotulosAcao[item.acao]} · {rotulosEstado[item.estado_posterior]}</p><p className="whitespace-pre-wrap">{item.motivo}</p><p className="text-xs text-foreground/70">{formatarData(item.created_at)}</p></li>)}</ul>)}
      </section>
      {(denuncias.tipo === "erro" || decisoes.tipo === "erro" || (comentario.substitui_id && anterior.tipo === "erro")) && <button type="button" disabled={executando} onClick={() => setRecarga((valor) => valor + 1)} className="text-sm text-accent underline underline-offset-4">Tentar carregar informações novamente</button>}
      {impedido ? <p role="alert" className="text-sm">Este caso requer outro moderador. Nenhuma nova ação está disponível nesta análise.</p> : acoes.length > 0 ?
        <form onSubmit={(evento) => {
          evento.preventDefault();
          if (!acao || !acoes.includes(acao) || !motivo.trim()) { setErroFormulario("Selecione uma ação e informe o motivo da decisão."); return; }
          setErroFormulario("");
          void aoDecidir(comentario.id, { acao, motivo });
        }} className="border-t border-foreground/10 pt-4">
          <fieldset disabled={executando} className="space-y-3">
            <legend className="mb-3 font-medium">Registrar decisão</legend>
            <p className="text-sm text-foreground/70">Não julgue seu próprio comentário ou um caso com denúncia sua. Críticas acadêmicas negativas são permitidas.</p>
            <label htmlFor="acao-moderacao" className="block text-sm font-medium">Ação
              <select id="acao-moderacao" required value={acao} onChange={(evento) => setAcao(acoes.find((item) => item === evento.target.value) ?? "")} className={`${campo} mt-1`}>
                <option value="">Selecione a ação</option>{acoes.map((item) => <option key={item} value={item}>{rotulosAcao[item]}</option>)}
              </select>
            </label>
            <label htmlFor="motivo-moderacao" className="block text-sm font-medium">Motivo da decisão
              <textarea id="motivo-moderacao" required rows={4} value={motivo} onChange={(evento) => setMotivo(evento.target.value)} className={`${campo} mt-1`} />
            </label>
            {erroFormulario && <p role="alert" className="text-sm">{erroFormulario}</p>}
            <button type="submit" disabled={executando || !acao || !motivo.trim()} className="button primary min-h-11 disabled:opacity-50">{executando ? "Registrando decisão…" : "Confirmar decisão"}</button>
          </fieldset>
        </form> : <p className="text-sm text-foreground/70">Nenhuma ação disponível com o estado e os relatos consultados. Atualize a fila se o conteúdo mudou.</p>}
    </div>
  );
}
