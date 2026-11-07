"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { useEffect, useState } from "react";
import { comContextoBusca, ordenarResultados, ordemBusca, urlBusca, type TipoBusca } from "@/lib/contexto-busca";
import { listarProfessores } from "@/lib/services/professores";
import { buscarDisciplinas } from "@/lib/services/disciplinas";
import type { DisciplinaDetalhe, ProfessorDetalhe } from "@/lib/types/institucional";
import ProfessorResultado from "@/app/professores/professor-resultado";

type Resultado = ProfessorDetalhe | DisciplinaDetalhe;
type Consulta = { tipo: TipoBusca; termo: string; tentativa: number } & ({ estado: "sucesso"; resultados: Resultado[] } | { estado: "erro" });

export default function BuscaInstitucional({ tipo }: { tipo: TipoBusca }) {
  const parametros = useSearchParams();
  const termo = parametros.get("q") ?? "";
  const ordem = ordemBusca(parametros.get("ordem"));
  const contexto = { tipo, termo, ordem };
  const busca = termo.trim();
  const [tentativa, setTentativa] = useState(0);
  const [consulta, setConsulta] = useState<Consulta | null>(null);
  const valido = busca.length === 0 || busca.length >= 2;
  const atual = consulta?.tipo === tipo && consulta.termo === busca && consulta.tentativa === tentativa;
  const carregando = valido && !atual;
  const erro = atual && consulta.estado === "erro";
  const resultados = atual && consulta.estado === "sucesso" ? ordenarResultados(consulta.resultados, ordem) : [];

  useEffect(() => {
    if (!valido) return;
    let cancelado = false;
    const pesquisar = tipo === "professores" ? listarProfessores : buscarDisciplinas;
    pesquisar(busca).then(resultados => {
      if (!cancelado) setConsulta({ tipo, termo: busca, tentativa, estado: "sucesso", resultados });
    }).catch(() => { if (!cancelado) setConsulta({ tipo, termo: busca, tentativa, estado: "erro" }); });
    return () => { cancelado = true; };
  }, [busca, tipo, tentativa, valido]);

  return <main className="results-page container page-content">
    <nav className="breadcrumb" aria-label="Caminho da página"><Link href="/">Início</Link><span aria-hidden="true">›</span><span aria-current="page">{busca ? "Resultados da busca" : "Explorar"}</span></nav>
    <div className="results-heading"><div><h1>{busca ? `Resultados para “${termo}”` : "Explore professores e disciplinas"}</h1><p>{busca ? "Encontre a disciplina e consulte ou avalie diretamente." : "Escolha uma disciplina ou um professor para começar."}</p></div><span className="badge outlined">Consulta pública · sem cadastro</span></div>
    <section aria-label="Resultados da busca" className="results-section">
      <div className="results-toolbar"><nav aria-label="Tipo de busca" className="result-tabs">
        <Link href={urlBusca({ ...contexto, tipo: "professores" })} aria-current={tipo === "professores" ? "page" : undefined}>Professores</Link>
        <Link href={urlBusca({ ...contexto, tipo: "disciplinas" })} aria-current={tipo === "disciplinas" ? "page" : undefined}>Disciplinas</Link>
      </nav><label className="results-sort"><span>Ordenar por</span><select aria-label="Ordenar resultados" value={ordem} onChange={e => window.history.pushState(null, "", urlBusca({ ...contexto, ordem: ordemBusca(e.target.value) }))}><option value="nome">Nome (A–Z)</option><option value="unidade">Unidade acadêmica (A–Z)</option></select></label></div>
      <div className="results-status" aria-live="polite" aria-atomic="true" aria-busy={carregando}>
        {!valido && <p>Use ao menos 2 caracteres na busca do cabeçalho.</p>}
        {carregando && <p>Carregando resultados…</p>}
        {atual && !erro && <p>{resultados.length} resultado(s){busca ? ` para “${termo}”` : " disponíveis"}</p>}
      </div>
      {erro && <div className="panel empty-state"><h2>Não foi possível carregar os resultados</h2><p role="alert">Tente novamente em instantes.</p><button className="button" onClick={() => setTentativa(n => n + 1)}>Tentar novamente</button></div>}
      {atual && !erro && !resultados.length && <div className="panel empty-state"><h2>Nenhum resultado encontrado</h2><p>Tente outro nome ou código na busca do cabeçalho.</p></div>}
      {atual && !erro && resultados.length > 0 && <ul className={tipo === "professores" ? "professor-results" : "discipline-results"} aria-label="Lista de resultados">{resultados.map(resultado => "codigo" in resultado ? <li key={resultado.id}><Link className="panel subject-card result-subject" href={comContextoBusca(`/disciplinas/${resultado.id}`, contexto)}><span className="badge blue">{resultado.codigo}</span><h2>{resultado.nome}</h2><p>Unidade acadêmica: {resultado.departamento}</p><span className="text-link">Comparar professores →</span></Link></li> : <ProfessorResultado key={resultado.id} professor={resultado} contexto={contexto} />)}</ul>}
    </section>
  </main>;
}
