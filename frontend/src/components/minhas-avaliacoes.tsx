"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { consultarMinhasAvaliacoes, type MinhasAvaliacoes } from "@/lib/services/minhas-avaliacoes";
import { EVENTO_SESSAO_ALTERADA } from "@/lib/services/auth";
import { ApiError, mensagemErroTemporario } from "@/lib/services/http-error";

const dificuldade = { FACIL: "Fácil", MEDIO: "Média", DIFICIL: "Difícil" };
const material = { RUIM: "Ruim", MEDIO: "Médio", BOM: "Bom" };
type Consulta = { estado: "carregando" } | { estado: "erro"; mensagem: string } | { estado: "sucesso"; dados: MinhasAvaliacoes };

export default function MinhasAvaliacoesPainel() {
  const [consulta, setConsulta] = useState<Consulta>({ estado: "carregando" });
  const [pagina, setPagina] = useState(1);
  const [tentativa, setTentativa] = useState(0);
  useEffect(() => {
    const controlador = new AbortController();
    void consultarMinhasAvaliacoes(pagina, controlador.signal).then(dados => {
      if (!controlador.signal.aborted) setConsulta({ estado: "sucesso", dados });
    }).catch(falha => {
      if (controlador.signal.aborted) return;
      if (falha instanceof ApiError && falha.status === 401) window.dispatchEvent(new Event(EVENTO_SESSAO_ALTERADA));
      setConsulta({ estado: "erro", mensagem: falha instanceof ApiError && falha.status === 401 ? "Sua sessão expirou. Entre novamente para ver suas avaliações." : mensagemErroTemporario(falha) ?? "Não foi possível carregar suas avaliações agora." });
    });
    return () => controlador.abort();
  }, [pagina, tentativa]);

  function mudarPagina(valor: number) { setConsulta({ estado: "carregando" }); setPagina(valor); }

  return <section className="flex min-w-0 flex-col gap-4 border-t border-(--border) pt-5" aria-labelledby="minhas-avaliacoes-titulo">
    <div><h2 id="minhas-avaliacoes-titulo" className="text-xl font-semibold">Minhas avaliações</h2><p className="mt-1 text-sm leading-relaxed text-(--muted)">Confira os critérios que você enviou. Estas respostas individuais são visíveis somente para você.</p></div>
    {consulta.estado === "carregando" && <p role="status" className="text-sm text-(--muted)">Carregando suas avaliações…</p>}
    {consulta.estado === "erro" && <div className="flex flex-col gap-3"><p role="alert" className="status-box error">{consulta.mensagem}</p><button className="button" onClick={() => { setConsulta({ estado: "carregando" }); setTentativa(v => v + 1); }}>Tentar novamente</button></div>}
    {consulta.estado === "sucesso" && <>
      <p role="status" className="text-sm text-(--muted)">{consulta.dados.total} {consulta.dados.total === 1 ? "avaliação enviada" : "avaliações enviadas"}</p>
      {!consulta.dados.itens.length ? <div className="rounded-xl border border-(--border) p-4"><p className="text-sm">{consulta.dados.total ? "Não há avaliações nesta página." : "Você ainda não enviou avaliações."}</p><Link href="/professores" className="link mt-3 inline-block text-sm">Buscar professor para avaliar →</Link></div> : <ul className="grid min-w-0 gap-4 sm:grid-cols-2">
        {consulta.dados.itens.map(a => <li key={a.id} className="min-w-0 rounded-xl border border-(--border) bg-(--panel) p-4 [overflow-wrap:anywhere]">
          <span className="code-chip"><span className="sr-only">Código: </span>{a.disciplina.codigo}</span>
          <h3 className="mt-3 text-base font-semibold">{a.professor.nome}</h3><p className="mt-1 text-sm text-(--ink-soft)">{a.disciplina.nome}</p>
          <dl className="my-4 grid grid-cols-2 gap-x-4 gap-y-3 text-sm">
            <div><dt className="text-xs text-(--muted)">Didática</dt><dd>{a.didatica}/5</dd></div>
            <div><dt className="text-xs text-(--muted)">Dificuldade</dt><dd>{dificuldade[a.dificuldade]}</dd></div>
            <div><dt className="text-xs text-(--muted)">Faz chamada</dt><dd>{a.chamada ? "Sim" : "Não"}</dd></div>
            <div><dt className="text-xs text-(--muted)">Material</dt><dd>{a.disponibiliza_material && a.qualidade_material ? material[a.qualidade_material] : "Não disponibiliza"}</dd></div>
            <div><dt className="text-xs text-(--muted)">Recomenda</dt><dd>{a.recomenda ? "Sim" : "Não"}</dd></div>
          </dl>
          <p className="mb-3 text-xs text-(--muted)">Atualizada em <time dateTime={a.updated_at}>{new Date(a.updated_at).toLocaleDateString("pt-BR", { timeZone: "America/Sao_Paulo" })}</time></p>
          <Link href={`/professores/${a.professor_id}/disciplinas/${a.disciplina_id}`} className="link text-sm">Ver avaliações da disciplina →</Link>
        </li>)}
      </ul>}
      {consulta.dados.total > consulta.dados.tamanho && <nav aria-label="Páginas das minhas avaliações" className="flex flex-wrap items-center justify-between gap-3">
        <button type="button" className="button" disabled={pagina === 1} onClick={() => mudarPagina(pagina - 1)}>Anterior</button>
        <span className="text-sm text-(--muted)">Página {pagina} de {Math.ceil(consulta.dados.total / consulta.dados.tamanho)}</span>
        <button type="button" className="button" disabled={pagina * consulta.dados.tamanho >= consulta.dados.total} onClick={() => mudarPagina(pagina + 1)}>Próxima</button>
      </nav>}
    </>}
  </section>;
}
