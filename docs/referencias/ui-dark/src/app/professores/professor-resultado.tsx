"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import DisciplinasProfessor from "@/components/disciplinas-professor";
import { listarDisciplinasDoProfessor } from "@/lib/services/professores";
import type { DisciplinaDetalhe, ProfessorDetalhe } from "@/lib/types/institucional";
import { comContextoBusca, type ContextoBusca } from "@/lib/contexto-busca";

type Consulta = { estado: "carregando" } | { estado: "sucesso"; disciplinas: DisciplinaDetalhe[] } | { estado: "erro" };

export default function ProfessorResultado({ professor, contexto = null }: { professor: ProfessorDetalhe; contexto?: ContextoBusca | null }) {
  const [consulta, setConsulta] = useState<Consulta>({ estado: "carregando" });
  useEffect(() => {
    let cancelado = false;
    listarDisciplinasDoProfessor(professor.id).then(disciplinas => {
      if (!cancelado) setConsulta({ estado: "sucesso", disciplinas });
    }).catch(() => { if (!cancelado) setConsulta({ estado: "erro" }); });
    return () => { cancelado = true; };
  }, [professor.id]);
  const iniciais = professor.nome.replace(/^DEMO - /, "").split(" ").filter(Boolean).slice(0,2).map(p => p[0]).join("");
  return <li className="panel professor-result"><div className="professor-result-heading"><div className="small-avatar" aria-hidden="true">{iniciais}</div><div><Link className="person-name" href={comContextoBusca(`/professores/${professor.id}`, contexto)}>{professor.nome}</Link><p>Unidade acadêmica: {professor.departamento}</p></div></div>
    <h2 className="result-section-label">Disciplinas lecionadas</h2>
    {consulta.estado === "carregando" && <p role="status">Carregando disciplinas…</p>}
    {consulta.estado === "erro" && <p role="status">Não foi possível carregar as disciplinas. <Link className="text-link" href={comContextoBusca(`/professores/${professor.id}`, contexto)}>Abrir perfil →</Link></p>}
    {consulta.estado === "sucesso" && <DisciplinasProfessor professorId={professor.id} disciplinas={consulta.disciplinas} contexto={contexto} />}
  </li>;
}
